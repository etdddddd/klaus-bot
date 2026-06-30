from __future__ import annotations

import asyncio
import datetime
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


class UtilidadesExtra(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.reminder_loop.start()

    def cog_unload(self) -> None:
        self.reminder_loop.cancel()

    @app_commands.command(name="reminder", description="Defina um lembrete!")
    @app_commands.describe(tempo="Tempo (ex: 10m, 2h, 1d)", texto="O que lembrar")
    async def reminder(self, interaction: discord.Interaction, tempo: str, texto: str) -> None:
        seconds = self._parse_time(tempo)
        if seconds <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Use formato: `10m`, `2h`, `1d`"), ephemeral=True
            )
            return
        if seconds > 86400 * 7:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Máximo de 7 dias!"), ephemeral=True
            )
            return

        remind_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
        await db.add_reminder(interaction.user.id, interaction.channel.id, texto, remind_at)

        embed = (
            make_embed("success")
            .title("\U0001f514 Lembrete Definido!")
            .desc(f"Você será lembrado em **{tempo}**.")
            .field("Texto", f"```{texto}```")
            .field("Em", f"<t:{int(remind_at.timestamp())}:R>")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @tasks.loop(seconds=30)
    async def reminder_loop(self) -> None:
        try:
            reminders = await db.get_pending_reminders()
            for r in reminders:
                try:
                    channel = self.bot.get_channel(r["channel_id"])
                    if channel:
                        user = self.bot.get_user(r["user_id"])
                        embed = (
                            make_embed("purple")
                            .title("\U0001f514 Lembrete!")
                            .desc(f"{user.mention if user else 'Usuário'}, aqui está seu lembrete:")
                            .field("Texto", f"```{r['text']}```")
                            .timestamp()
                            .build()
                        )
                        await channel.send(embed=embed)
                        await db.mark_reminder_delivered(r["_id"])
                except Exception as e:
                    logger.debug("Reminder delivery failed: %s", e)
        except Exception as e:
            logger.warning("Reminder loop error: %s", e)

    @reminder_loop.before_loop
    async def before_reminder(self) -> None:
        await self.bot.wait_until_ready()

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
    await bot.add_cog(UtilidadesExtra(bot))
