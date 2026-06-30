from __future__ import annotations

import re
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from database import db
from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot


class AutoMod(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.spam_tracker: dict[int, list[float]] = {}
        self.link_pattern = re.compile(r"https?://\S+|www\.\S+")

    # =========================
    # ANTI-SPAM
    # =========================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        cfg = await db.get_guild_config(message.guild.id)

        if cfg.get("automod_links"):
            if self.link_pattern.search(message.content):
                try:
                    await message.delete()
                    embed = make_embed.error(
                        "Link Detectado",
                        f"{message.author.mention}, links não são permitidos!"
                    )
                    msg = await message.channel.send(embed=embed, delete_after=5)
                except discord.HTTPException:
                    pass
                return

        if cfg.get("automod_spam"):
            import time
            now = time.time()
            user_id = message.author.id
            if user_id not in self.spam_tracker:
                self.spam_tracker[user_id] = []
            self.spam_tracker[user_id].append(now)
            self.spam_tracker[user_id] = [t for t in self.spam_tracker[user_id] if now - t < 5]
            if len(self.spam_tracker[user_id]) > 5:
                try:
                    await message.delete()
                    embed = make_embed.error(
                        "Spam Detectado",
                        f"{message.author.mention}, pare de spammar!"
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                except discord.HTTPException:
                    pass
                return

        if cfg.get("automod_bad_words"):
            bad_words = cfg.get("bad_words_list", [])
            content_lower = message.content.lower()
            for word in bad_words:
                if word.lower() in content_lower:
                    try:
                        await message.delete()
                        embed = make_embed.error(
                            "Palavra Proibida",
                            f"{message.author.mention}, essa palavra não é permitida!"
                        )
                        await message.channel.send(embed=embed, delete_after=5)
                    except discord.HTTPException:
                        pass
                    return

        if cfg.get("automod_mass_mentions"):
            if len(message.mentions) > 5:
                try:
                    await message.delete()
                    embed = make_embed.error(
                        "Menções em Massa",
                        f"{message.author.mention}, não mencione tanta gente!"
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                except discord.HTTPException:
                    pass
                return

    # =========================
    # CONFIG COMMANDS
    # =========================

    @app_commands.command(name="automod", description="Configure o auto-mod.")
    @app_commands.describe(config="O que configurar", valor="true ou false")
    @app_commands.choices(config=[
        app_commands.Choice(name="Anti-Spam", value="spam"),
        app_commands.Choice(name="Anti-Links", value="links"),
        app_commands.Choice(name="Palavras Proibidas", value="bad_words"),
        app_commands.Choice(name="Anti-Mentions em Massa", value="mass_mentions"),
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod(self, interaction: discord.Interaction, config: app_commands.Choice[str], valor: str) -> None:
        if not interaction.guild:
            return

        enabled = valor.lower() in ("true", "on", "1", "sim", "yes")
        field_map = {
            "spam": "automod_links",
            "links": "automod_links",
            "bad_words": "automod_bad_words",
            "mass_mentions": "automod_mass_mentions",
        }
        field = field_map.get(config.value, f"automod_{config.value}")
        await db.set_guild_config(interaction.guild.id, **{field: enabled})

        status = "\u2705 Ativado" if enabled else "\u274c Desativado"
        embed = (
            make_embed("success")
            .title(f"\U0001f6e1\ufe0f AutoMod - {config.name}")
            .desc(f"**{config.name}** foi **{'ativado' if enabled else 'desativado'}**!")
            .field("Status", f"```{status}```")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add_badword", description="Adicione uma palavra proibida.")
    @app_commands.describe(palavra="Palavra para proibir")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def add_badword(self, interaction: discord.Interaction, palavra: str) -> None:
        if not interaction.guild:
            return
        cfg = await db.get_guild_config(interaction.guild.id)
        words = cfg.get("bad_words_list", [])
        if palavra.lower() not in [w.lower() for w in words]:
            words.append(palavra)
            await db.set_guild_config(interaction.guild.id, bad_words_list=words, automod_bad_words=True)

        embed = (
            make_embed("success")
            .title("\U0001f6ab Palavra Proibida Adicionada!")
            .desc(f"**{palavra}** foi adicionada à lista de palavras proibidas.")
            .field("Total", f"```{len(words)} palavras```")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(AutoMod(bot))
