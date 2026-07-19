from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot


class ReactionRole(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot

    @app_commands.command(name="reaction_role", description="Crie um reaction role.")
    @app_commands.describe(
        message_id="ID da mensagem",
        emoji="Emoji para reação",
        cargo="Cargo para dar",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def reaction_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        cargo: discord.Role,
    ) -> None:
        if not interaction.guild:
            return

        if cargo.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Cargo acima do meu!"), ephemeral=True
            )
            return

        try:
            channel = interaction.channel
            if not isinstance(channel, discord.TextChannel):
                return
            message = await channel.fetch_message(int(message_id))
        except (discord.NotFound, ValueError):
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Mensagem não encontrada!"), ephemeral=True
            )
            return

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Emoji inválido!"), ephemeral=True
            )
            return

        await db.add_reaction_role(message.id, emoji, cargo.id, interaction.guild.id)

        embed = (
            make_embed("success")
            .title("\U0001f44d Reaction Role Criado!")
            .desc(f"Mensagem: [Link]({message.url})")
            .field("Emoji", f"```{emoji}```")
            .field("Cargo", cargo.mention)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        if payload.member and payload.member.bot:
            return

        rr = await db.get_reaction_role(payload.message_id, str(payload.emoji))
        if rr:
            guild = self.bot.get_guild(payload.guild_id)
            if guild:
                role = guild.get_role(rr["role_id"])
                member = guild.get_member(payload.user_id)
                if role and member:
                    try:
                        await member.add_roles(role, reason="Reaction Role")
                    except discord.HTTPException:
                        pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        rr = await db.get_reaction_role(payload.message_id, str(payload.emoji))
        if rr:
            guild = self.bot.get_guild(payload.guild_id)
            if guild:
                role = guild.get_role(rr["role_id"])
                member = guild.get_member(payload.user_id)
                if role and member:
                    try:
                        await member.remove_roles(role, reason="Reaction Role")
                    except discord.HTTPException:
                        pass



async def setup(bot: KlausBot) -> None:
    await bot.add_cog(ReactionRole(bot))
