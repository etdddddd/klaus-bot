from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands, tasks

from database import db
from embed_builder import KlausEmbed as make_embed
from helpers import format_koins, parse_time

if TYPE_CHECKING:
    from klaus import KlausBot

logger = logging.getLogger(__name__)


class GiveawayJoinView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Participar! \U0001f389", style=discord.ButtonStyle.green, custom_id="giveaway_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(
            embed=make_embed("success").title("Participando!").desc("Voce esta participando do giveaway!").build(),
            ephemeral=True,
        )


class Giveaway(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.bot.add_view(GiveawayJoinView())
        self._participants: dict[int, set[int]] = {}
        self.check_giveaways.start()

    def cog_unload(self) -> None:
        self.check_giveaways.cancel()

    @tasks.loop(seconds=30)
    async def check_giveaways(self) -> None:
        try:
            giveaways = await db.get_active_giveaways()
            for gw in giveaways:
                try:
                    giveaway_id = gw.get("_id")
                    channel_id = gw.get("channel_id")
                    message_id = gw.get("message_id")
                    prize = gw.get("prize", "Premio")
                    host_id = gw.get("host_id")

                    if not giveaway_id:
                        continue

                    channel = self.bot.get_channel(channel_id) if channel_id else None
                    if not isinstance(channel, discord.TextChannel):
                        await db.end_giveaway(str(giveaway_id))
                        continue

                    message = None
                    if message_id:
                        try:
                            message = await channel.fetch_message(message_id)
                        except discord.HTTPException:
                            message = None

                    participants = set()
                    if message:
                        for reaction in message.reactions:
                            if str(reaction.emoji) == "\U0001f389":
                                users = [u async for u in reaction.users() if not u.bot]
                                participants.update(u.id for u in users)

                    stored_participants = self._participants.get(message_id, set())
                    participants.update(stored_participants)

                    await db.end_giveaway(str(giveaway_id))

                    if participants:
                        winner_id = random.choice(list(participants))
                        try:
                            winner = await self.bot.fetch_user(winner_id)
                        except discord.NotFound:
                            winner = None

                        if winner:
                            embed = (
                                make_embed("gold")
                                .title("\U0001f3c6 Giveaway Encerrado!")
                                .desc(f"**{prize}**\n\nGanhador: {winner.mention}")
                                .field("Participantes", f"```{len(participants)}```")
                                .timestamp()
                                .footer("Klaus Giveaways")
                                .build()
                            )
                            try:
                                await channel.send(content=winner.mention, embed=embed)
                            except discord.HTTPException:
                                pass

                            try:
                                dm_embed = discord.Embed(
                                    title="\U0001f3c6 Parabens! Voce ganhou um giveaway!",
                                    description=f"**Servidor:** {channel.guild.name}\n**Premio:** {prize}\n**Canal:** {channel.mention}",
                                    color=0xF59E0B,
                                )
                                dm_embed.set_footer(text="Klaus Giveaways")
                                await winner.send(embed=dm_embed)
                            except discord.HTTPException:
                                pass

                            if message:
                                for item in message.components:
                                    for child in item.children:
                                        child.disabled = True
                                try:
                                    await message.edit(view=None)
                                except discord.HTTPException:
                                    pass
                        else:
                            embed = (
                                make_embed("error")
                                .title("\U0001f389 Giveaway Encerrado!")
                                .desc(f"**{prize}**\n\nNenhum participante valido.")
                                .timestamp()
                                .footer("Klaus Giveaways")
                                .build()
                            )
                            try:
                                await channel.send(embed=embed)
                            except discord.HTTPException:
                                pass
                    else:
                        embed = (
                            make_embed("error")
                            .title("\U0001f389 Giveaway Encerrado!")
                            .desc(f"**{prize}**\n\nNenhum participante valido.")
                            .timestamp()
                            .footer("Klaus Giveaways")
                            .build()
                        )
                        try:
                            await channel.send(embed=embed)
                        except discord.HTTPException:
                            pass

                    self._participants.pop(message_id, None)
                    logger.info("Giveaway %s ended in channel %s", giveaway_id, channel.name)

                except Exception as e:
                    logger.warning("Giveaway processing failed for %s: %s", gw.get("_id"), e)
        except Exception as e:
            logger.warning("Giveaway check loop error: %s", e)

    @check_giveaways.before_loop
    async def before_check(self) -> None:
        await self.bot.wait_until_ready()

    @app_commands.command(name="giveaway", description="Crie um giveaway!")
    @app_commands.describe(
        prize="O premio",
        tempo="Duracao (ex: 1h, 30m, 1d)",
        canal="Canal do giveaway",
        participantes="Numero de vencedores",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_cmd(
        self,
        interaction: discord.Interaction,
        prize: str,
        tempo: str = "1h",
        canal: discord.TextChannel | None = None,
        participantes: int = 1,
    ) -> None:
        channel = canal or interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return

        seconds = parse_time(tempo)
        if seconds <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Use formato: `30m`, `1h`, `2d`"), ephemeral=True
            )
            return

        if seconds > 86400 * 30:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Duracao maxima: 30 dias"), ephemeral=True
            )
            return

        end_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        embed = (
            make_embed("gold")
            .title(f"\U0001f389 {prize}!")
            .desc(
                f"Clique no botao abaixo para participar!\n\n"
                f"**Host:** {interaction.user.mention}\n"
                f"**Encerra:** <t:{int(end_time.timestamp())}:R>\n"
                f"**Vencedores:** {participantes}"
            )
            .footer(f"Giveaway Klaus \u2022 {tempo}")
            .timestamp()
            .build()
        )
        view = GiveawayJoinView()
        msg = await channel.send(embed=embed, view=view)

        await db.create_giveaway(channel.id, msg.id, prize, interaction.user.id, seconds)

        await interaction.response.send_message(
            embed=make_embed("success").title("Giveaway Criado!").desc(f"Canal: {channel.mention}").build(),
            ephemeral=True,
        )

    @app_commands.command(name="giveaway_reroll", description="Refaca o sorteio de um giveaway!")
    @app_commands.describe(message_id="ID da mensagem do giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_reroll(self, interaction: discord.Interaction, message_id: str) -> None:
        try:
            mid = int(message_id)
        except ValueError:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "ID invalido."), ephemeral=True
            )
            return

        try:
            message = await interaction.channel.fetch_message(mid)  # type: ignore
        except (discord.HTTPException, AttributeError):
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Mensagem nao encontrada."), ephemeral=True
            )
            return

        participants = set()
        for reaction in message.reactions:
            if str(reaction.emoji) == "\U0001f389":
                users = [u async for u in reaction.users() if not u.bot]
                participants.update(u.id for u in users)

        if not participants:
            await interaction.response.send_message(
                embed=make_embed.warn("Aviso", "Nenhum participante encontrado."), ephemeral=True
            )
            return

        winner_id = random.choice(list(participants))
        try:
            winner = await self.bot.fetch_user(winner_id)
        except discord.NotFound:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Usuario nao encontrado."), ephemeral=True
            )
            return

        embed = (
            make_embed("gold")
            .title("\U0001f3c6 Giveaway Reroll!")
            .desc(f"Ganhador: {winner.mention}")
            .timestamp()
            .footer("Klaus Giveaways")
            .build()
        )
        await interaction.response.send_message(content=winner.mention, embed=embed)


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Giveaway(bot))
