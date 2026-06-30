from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands, tasks

from database import db
from embed_builder import KlausEmbed as make_embed
from helpers import format_koins

if TYPE_CHECKING:
    from klaus import KlausBot

logger = logging.getLogger(__name__)


class GiveawayView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label="Participar! \U0001f389", style=discord.ButtonStyle.green, custom_id="giveaway_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(
            embed=make_embed("success").title("Participando!").desc("Você está participando do giveaway!").build(),
            ephemeral=True,
        )


class Giveaway(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.bot.add_view(GiveawayView())
        self.check_giveaways.start()

    def cog_unload(self) -> None:
        self.check_giveaways.cancel()

    @tasks.loop(seconds=30)
    async def check_giveaways(self) -> None:
        try:
            giveaways = await db.get_active_giveaways()
            for gw in giveaways:
                try:
                    channel = self.bot.get_channel(gw["channel_id"])
                    if not channel:
                        continue

                    message = await channel.fetch_message(gw["message_id"])
                    reactions = message.reactions
                    participants = []
                    for reaction in reactions:
                        if str(reaction.emoji) == "\U0001f389":
                            users = [u async for u in reaction.users() if not u.bot]
                            participants.extend(users)

                    if participants:
                        winner = participants[0]
                        embed = (
                            make_embed("gold")
                            .title("\U0001f3c6 Giveaway Encerrado!")
                            .desc(f"**{gw['prize']}**\n\nGanhador: {winner.mention}")
                            .field("Participantes", f"```{len(participants)}```")
                            .timestamp()
                            .build()
                        )
                        await channel.send(content=winner.mention, embed=embed)

                        for item in message.components:
                            for child in item.children:
                                child.disabled = True
                        try:
                            await message.edit(view=None)
                        except discord.HTTPException:
                            pass

                    await db.end_giveaway(gw["_id"])
                except Exception as e:
                    logger.warning("Giveaway processing failed for %s: %s", gw.get("_id"), e)
        except Exception as e:
            logger.warning("Giveaway check loop error: %s", e)

    @check_giveaways.before_loop
    async def before_check(self) -> None:
        await self.bot.wait_until_ready()

    @app_commands.command(name="giveaway", description="Crie um giveaway!")
    @app_commands.describe(prize="O prêmio", tempo="Duração (ex: 1h, 30m, 1d)", canal="Canal do giveaway")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        tempo: str = "1h",
        canal: discord.TextChannel | None = None,
    ) -> None:
        channel = canal or interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return

        seconds = self._parse_time(tempo)
        if seconds <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Use formato: `30m`, `1h`, `2d`"), ephemeral=True
            )
            return

        from datetime import datetime, timezone, timedelta
        end_time = datetime.now(timezone.utc) + timedelta(seconds=seconds)

        embed = (
            make_embed("gold")
            .title(f"\U0001f389 {prize}!")
            .desc(f"Clique no botão abaixo para participar!\n\nEncerra: <t:{int(end_time.timestamp())}:R>")
            .field("Host", interaction.user.mention)
            .footer(f"Giveaway Klaus \u2022 {tempo}")
            .timestamp()
            .build()
        )
        view = GiveawayView()
        msg = await channel.send(embed=embed, view=view)

        await db.create_giveaway(channel.id, msg.id, prize, interaction.user.id, seconds)

        await interaction.response.send_message(
            embed=make_embed("success").title("Giveaway Criado!").desc(f"Canal: {channel.mention}").build(),
            ephemeral=True,
        )

    @staticmethod
    def _parse_time(time_str: str) -> int:
        time_str = time_str.strip().lower()
        multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        unit = time_str[-1]
        if unit not in multipliers:
            return -1
        try:
            value = int(time_str[:-1])
            return value * multipliers[unit]
        except ValueError:
            return -1


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Giveaway(bot))
