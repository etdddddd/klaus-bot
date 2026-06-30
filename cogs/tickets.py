from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot


class TicketView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Selecione o tipo de suporte...",
        custom_id="ticket_select",
        options=[
            discord.SelectOption(label="Bug Report", description="Reportar um bug", value="bug", emoji="\U0001f41b"),
            discord.SelectOption(label="Dúvida", description="Tirar uma dúvida", value="duvida", emoji="\u2753"),
            discord.SelectOption(label="Sugestão", description="Sugerir algo", value="sugestao", emoji="\U0001f4a1"),
            discord.SelectOption(label="Reclamação", description="Fazer uma reclamação", value="reclamacao", emoji="\U0001f621"),
            discord.SelectOption(label="Outro", description="Outro motivo", value="outro", emoji="\U0001f4cc"),
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        guild = interaction.guild
        if not guild:
            return

        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets", overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
            })

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            },
        )

        await db.create_ticket(guild.id, interaction.user.id, channel.id, select.values[0])

        tipo_emojis = {
            "bug": "\U0001f41b Bug Report",
            "duvida": "\u2753 Dúvida",
            "sugestao": "\U0001f4a1 Sugestão",
            "reclamacao": "\U0001f621 Reclamação",
            "outro": "\U0001f4cc Outro",
        }

        embed = (
            make_embed("purple")
            .title(f"\U0001f3ab Ticket de {interaction.user.display_name}")
            .desc(f"Tipo: **{tipo_emojis.get(select.values[0], select.values[0])}**\n\nDescreva seu problema abaixo!")
            .field("Status", "```Aberto```")
            .field("Para Fechar", "Use `/close_ticket`")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await channel.send(content=interaction.user.mention, embed=embed)
        await interaction.response.send_message(
            embed=make_embed("success").title("Ticket Criado!").desc(f"Canal: {channel.mention}").build(),
            ephemeral=True,
        )


class Ticket(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.bot.add_view(TicketView())

    @app_commands.command(name="ticket_panel", description="Envie o painel de tickets.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def ticket_panel(self, interaction: discord.Interaction) -> None:
        embed = (
            make_embed("purple")
            .title("\U0001f3ab Suporte Klaus")
            .desc("Precisa de ajuda? Selecione o tipo de suporte abaixo!")
            .field("\U0001f41b Bug Report", "Reporte bugs do bot")
            .field("\u2753 Dúvida", "Tire suas dúvidas")
            .field("\U0001f4a1 Sugestão", "Sugira melhorias")
            .field("\U0001f621 Reclamação", "Faça uma reclamação")
            .field("\U0001f4cc Outro", "Outros assuntos")
            .footer("Selecione abaixo \u2022 Tickets são anônimos para outros membros")
            .timestamp()
            .build()
        )
        view = TicketView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="close_ticket", description="Feche o ticket atual.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def close_ticket(self, interaction: discord.Interaction) -> None:
        if not isinstance(interaction.channel, discord.TextChannel):
            return

        ticket = await db.close_ticket(interaction.channel.id)
        if not ticket:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Este não é um ticket!"), ephemeral=True
            )
            return

        embed = (
            make_embed("warning")
            .title("\U0001f6ab Ticket Fechado!")
            .desc(f"Ticket fechado por {interaction.user.mention}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

        import asyncio
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete(reason=f"Ticket fechado por {interaction.user}")
        except discord.HTTPException:
            pass


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Ticket(bot))
