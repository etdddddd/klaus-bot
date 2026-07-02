from __future__ import annotations

import asyncio
import datetime
import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import settings
from database import db
from embed_builder import KlausEmbed as make_embed
from helpers import format_cooldown

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from klaus import KlausBot


# =========================
# VIEWS & MODALS
# =========================

class NukeModal(discord.ui.Modal, title="Confirmar Nuke"):
    reason = discord.ui.TextInput(
        label="Motivo do nuke",
        placeholder="Digite o motivo...",
        required=False,
        max_length=200,
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.nuke_channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        reason_text = self.reason.value or f"Nuke por {interaction.user}"

        confirm = (
            make_embed("warning")
            .title("Nuke do Canal")
            .desc(f"O canal {self.nuke_channel.mention} sera deletado e recriado em **3 segundos**.")
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason_text)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=confirm)

        await asyncio.sleep(3)

        channel = self.nuke_channel
        guild = interaction.guild
        category = channel.category
        overwrites = channel.overwrites
        name = channel.name

        try:
            await channel.delete(reason=reason_text)
        except discord.HTTPException as e:
            await interaction.followup.send(
                embed=make_embed.error("Falha ao Nuke", f"Não foi possível deletar o canal: {e}"),
                ephemeral=True,
            )
            return

        new_channel = await guild.create_text_channel(
            name=name,
            category=category,
            overwrites=overwrites,
            reason=reason_text,
        )

        embed = (
            make_embed("success")
            .title("Canal Nukado")
            .desc(f"O canal {new_channel.mention} foi recriado com sucesso.")
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason_text)
            .timestamp()
            .build()
        )
        await new_channel.send(embed=embed)


class ModlogView(discord.ui.View):
    def __init__(self, logs: list[dict], guild: discord.Guild):
        super().__init__(timeout=120)
        self.logs = logs
        self.guild = guild
        self.page = 0
        self.per_page = 5
        self.max_pages = max(1, (len(logs) + self.per_page - 1) // self.per_page)
        self._update_buttons()

    def _update_buttons(self):
        self.prev_button.disabled = self.page <= 0
        self.next_button.disabled = self.page >= self.max_pages - 1

    def get_page_embed(self) -> discord.Embed:
        start = self.page * self.per_page
        end = start + self.per_page
        page_logs = self.logs[start:end]

        if not page_logs:
            return (
                make_embed("info")
                .title("Historico de Moderacao")
                .desc("Nenhuma acao de moderacao registrada.")
                .timestamp()
                .build()
            )

        lines = []
        for log in page_logs:
            mod_id = log.get("moderator_id", 0)
            target_id = log.get("target_id", 0)
            action = log.get("action", "unknown")
            reason = log.get("reason", "Sem motivo")
            ts = log.get("created_at", "")

            action_emoji = {"ban": "BAN", "kick": "KICK", "mute": "MUTE", "warn": "WARN", "automute": "AUTOMUTE"}.get(action.upper(), "LOG")
            lines.append(
                f"**[{action_emoji}]** <@{target_id}>\n"
                f"> Motivo: {reason}\n"
                f"> Mod: <@{mod_id}> - {ts}"
            )

        embed = (
            make_embed("rose")
            .title("Historico de Moderacao")
            .desc("\n\n".join(lines))
            .footer(text=f"Pagina {self.page + 1}/{self.max_pages} - {len(self.logs)} acoes registradas")
            .timestamp()
            .build()
        )
        return embed

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)

    @discord.ui.button(label="Proximo", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_pages - 1:
            self.page += 1
            self._update_buttons()
            await interaction.response.edit_message(embed=self.get_page_embed(), view=self)


class Moderacao(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot

    async def _log_mod_action(self, guild_id: int, moderator_id: int, target_id: int, action: str, reason: str) -> None:
        try:
            await db.add_mod_log(guild_id, moderator_id, target_id, action, reason)
        except Exception as e:
            logger.warning("Failed to log mod action: %s", e)

    async def _count_mod_actions(self, guild_id: int, action: str) -> int:
        try:
            logs = await db.get_mod_logs(guild_id, limit=1000)
            return sum(1 for l in logs if l.get("action", "").lower() == action.lower())
        except Exception:
            return 0

    # =========================
    # /BAN
    # =========================

    @app_commands.command(name="ban", description="Bane um membro do servidor.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para banir", reason="Motivo do ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Sem motivo especificado",
    ) -> None:
        if member.top_role >= interaction.user.top_role:
            embed = make_embed.error("Erro", "Nao pode banir alguem com cargo igual ou superior.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not member.bannable:
            embed = make_embed.error("Erro", "Nao consigo banir este membro.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.send(
                embed=make_embed.warn(
                    f"Voce foi banido de {interaction.guild.name}",
                    f"**Motivo:** {reason}\n**Moderador:** {interaction.user.mention}",
                )
            )
        except discord.HTTPException:
            pass

        previous_bans = await self._count_mod_actions(interaction.guild.id, "ban")

        severity_keywords_high = ["raid", "spam", "scam", "hack", "exploit", "nsfw", "gore", "racismo"]
        severity_keywords_medium = ["toxic", "ofensa", "assédio", "harassment", "ameaca"]
        reason_lower = reason.lower()

        color = 0xEF4444
        severity_label = "Alta"
        for kw in severity_keywords_medium:
            if kw in reason_lower:
                color = 0xF97316
                severity_label = "Media"
                break
        for kw in severity_keywords_high:
            if kw in reason_lower:
                color = 0xEF4444
                severity_label = "Alta"
                break

        await member.ban(reason=reason)
        await self._log_mod_action(interaction.guild.id, interaction.user.id, member.id, "ban", reason)

        created_ts = f"<t:{int(member.created_at.timestamp())}:R>" if member.created_at else "Desconhecido"

        embed = (
            make_embed(color)
            .title("Membro Banido")
            .field("Membro", f"{member.mention} (`{member.id}`)")
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason)
            .field("Gravidade", severity_label, inline=True)
            .field("Historico", f"**{previous_bans}** ban(s) anteriores no servidor", inline=True)
            .field("Conta criada", created_ts, inline=True)
            .thumb(member.display_avatar.url)
            .footer(text=f"Moderador ID: {interaction.user.id}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /KICK
    # =========================

    @app_commands.command(name="kick", description="Expulsa um membro do servidor.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para expulsar", reason="Motivo da expulsao")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Sem motivo especificado",
    ) -> None:
        if member.top_role >= interaction.user.top_role:
            embed = make_embed.error("Erro", "Nao pode expulsar alguem com cargo igual ou superior.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not member.kickable:
            embed = make_embed.error("Erro", "Nao consigo expulsar este membro.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            await member.send(
                embed=make_embed.warn(
                    f"Voce foi expulso de {interaction.guild.name}",
                    f"**Motivo:** {reason}\n**Moderador:** {interaction.user.mention}",
                )
            )
        except discord.HTTPException:
            pass

        await member.kick(reason=reason)
        await self._log_mod_action(interaction.guild.id, interaction.user.id, member.id, "kick", reason)

        embed = (
            make_embed("warning")
            .title("Membro Expulso")
            .field("Membro", f"{member.mention} (`{member.id}`)")
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /MUTE
    # =========================

    @app_commands.command(name="mute", description="Silencia um membro do servidor.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para silenciar", minutos="Duracao em minutos (padrao: 10)", reason="Motivo")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutos: int = 10,
        reason: str = "Sem motivo especificado",
    ) -> None:
        if member.top_role >= interaction.user.top_role:
            embed = make_embed.error("Erro", "Nao pode silenciar alguem com cargo igual ou superior.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if member.is_timed_out():
            embed = make_embed.error("Erro", "Este membro ja esta silenciado.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        minutos = max(1, min(40320, minutos))
        duration = discord.utils.utcnow() + datetime.timedelta(minutes=minutos)

        await member.timeout(duration, reason=reason)
        await self._log_mod_action(interaction.guild.id, interaction.user.id, member.id, "mute", reason)

        embed = (
            make_embed("warning")
            .title("Membro Silenciado")
            .field("Membro", f"{member.mention} (`{member.id}`)")
            .field("Duracao", f"**{minutos}** minutos")
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /UNMUTE
    # =========================

    @app_commands.command(name="unmute", description="Remove o silencio de um membro.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para desmutar")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if not member.is_timed_out():
            embed = make_embed.error("Erro", "Este membro nao esta silenciado.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await member.timeout(None, reason=f"Desmutado por {interaction.user}")

        embed = (
            make_embed("success")
            .title("Membro Desmutado")
            .field("Membro", f"{member.mention}")
            .field("Moderador", interaction.user.mention)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /WARN
    # =========================

    @app_commands.command(name="warn", description="Advertencia para um membro.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para advertir", reason="Motivo da advertencia")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "Sem motivo especificado",
    ) -> None:
        if member.bot:
            embed = make_embed.error("Erro", "Nao pode advertir bots.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        count = await db.add_warning(interaction.guild.id, member.id, interaction.user.id, reason)
        await self._log_mod_action(interaction.guild.id, interaction.user.id, member.id, "warn", reason)

        guild_premium = await db.is_premium(interaction.guild.owner_id)
        max_warns = 10 if guild_premium else settings.max_warnings

        ratio = min(count / max_warns, 1.0)
        filled = round(ratio * 15)
        empty = 15 - filled
        bar = "\u2588" * filled + "\u2591" * empty

        if count < 3:
            next_penalty = "Mute (3 warnings)"
        elif count < 4:
            next_penalty = "Kick (4 warnings)"
        elif count < 5:
            next_penalty = "Ban (5 warnings)"
        else:
            next_penalty = "Ban automatico"

        if ratio < 0.3:
            color = 0xF59E0B
        elif ratio < 0.6:
            color = 0xF97316
        else:
            color = 0xEF4444

        embed = (
            make_embed(color)
            .title("Advertencia Aplicada")
            .field("Membro", f"{member.mention} (`{member.id}`)")
            .field("Progresso", f"`{bar}` **{count}**/{max_warns}")
            .field("Proxima penalidade", next_penalty)
            .field("Moderador", interaction.user.mention)
            .field("Motivo", reason)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

        if count >= max_warns:
            try:
                await member.ban(reason=f"Max warnings atingido ({count})")
            except discord.HTTPException:
                pass

    # =========================
    # /WARNINGS
    # =========================

    @app_commands.command(name="warnings", description="Veja as advertencias de um membro.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para verificar")
    async def warnings(self, interaction: discord.Interaction, member: discord.Member) -> None:
        warns = await db.get_warnings(interaction.guild.id, member.id)

        if not warns:
            embed = make_embed.info("Warnings", f"{member.mention} nao possui advertencias.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        lines = []
        for i, w in enumerate(warns, 1):
            mod_id = w.get("moderator_id", 0)
            reason = w.get("reason", "Sem motivo")
            lines.append(f"`{i}.` **{reason}** - <@{mod_id}>")

        embed = (
            make_embed("warning")
            .title(f"Warnings de {member.display_name}")
            .desc("\n".join(lines))
            .field("Total", f"**{len(warns)}** advertencias")
            .thumb(member.display_avatar.url)
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CLEARWARNINGS
    # =========================

    @app_commands.command(name="clearwarnings", description="Remove todas as advertencias de um membro.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="Membro para limpar warnings")
    @app_commands.checks.has_permissions(ban_members=True)
    async def clearwarnings(self, interaction: discord.Interaction, member: discord.Member) -> None:
        count = await db.clear_warnings(interaction.guild.id, member.id)

        embed = (
            make_embed("success")
            .title("Warnings Limpos")
            .desc(f"**{count}** advertencia(s) removida(s) de {member.mention}.")
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================
    # /SLOWMODE_ALL
    # =========================

    @app_commands.command(name="slowmode_all", description="Defina o slowmode para todos os canais de texto.")
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
    @app_commands.describe(segundos="Slowmode em segundos (0 para desativar)")
    @app_commands.checks.has_permissions(administrator=True)
    async def slowmode_all(self, interaction: discord.Interaction, segundos: int = 0) -> None:
        segundos = max(0, min(21600, segundos))

        embed = (
            make_embed("purple")
            .title("Slowmode Global")
            .desc(f"Definindo slowmode de **{segundos}** segundos em todos os canais...")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

        text_channels = [ch for ch in interaction.guild.text_channels]
        total = len(text_channels)
        done = 0
        errors = 0

        for ch in text_channels:
            try:
                await ch.edit(slowmode_delay=segundos)
                done += 1
            except discord.HTTPException:
                errors += 1

            if done % 5 == 0 or done == total:
                progress_ratio = done / total if total > 0 else 1
                filled = round(progress_ratio * 20)
                bar = "\u2588" * filled + "\u2591" * (20 - filled)
                progress_embed = (
                    make_embed("purple")
                    .title("Slowmode Global - Progresso")
                    .desc(f"`{bar}` **{done}/{total}** canais atualizados")
                    .field("Erros", str(errors), inline=True)
                    .timestamp()
                    .build()
                )
                try:
                    await interaction.edit_original_response(embed=progress_embed)
                except discord.HTTPException:
                    pass

        final_embed = (
            make_embed("success")
            .title("Slowmode Global Concluido")
            .desc(f"Slowmode de **{segundos}** segundos aplicado em **{done}** canais.")
            .field("Erros", str(errors), inline=True)
            .timestamp()
            .build()
        )
        await interaction.edit_original_response(embed=final_embed)

    # =========================
    # /LOCK
    # =========================

    @app_commands.command(name="lock", description="Trave o canal atual.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction) -> None:
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

        embed = (
            make_embed("warning")
            .title("Canal Trancado")
            .desc(f"O canal {interaction.channel.mention} foi trancado.")
            .field("Moderador", interaction.user.mention)
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /UNLOCK
    # =========================

    @app_commands.command(name="unlock", description="Destrave o canal atual.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction) -> None:
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = None
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

        embed = (
            make_embed("success")
            .title("Canal Destrancado")
            .desc(f"O canal {interaction.channel.mention} foi destrancado.")
            .field("Moderador", interaction.user.mention)
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CLEARCHANNEL
    # =========================

    @app_commands.command(name="clearchannel", description="Limpe um numero especifico de mensagens.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(quantidade="Numero de mensagens (1-200)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearchannel(self, interaction: discord.Interaction, quantidade: int = 50) -> None:
        quantidade = max(1, min(200, quantidade))
        deleted = await interaction.channel.purge(limit=quantidade + 1)

        embed = (
            make_embed("success")
            .title("Canal Limpo")
            .desc(f"**{len(deleted) - 1}** mensagens removidas.")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================
    # /NUKE
    # =========================

    @app_commands.command(name="nuke", description="Nuke um canal (deleta e recria com as mesmas permissoes).")
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    @app_commands.checks.has_permissions(manage_channels=True)
    async def nuke(self, interaction: discord.Interaction) -> None:
        modal = NukeModal(channel=interaction.channel)
        await interaction.response.send_modal(modal)

    # =========================
    # /ROLE
    # =========================

    @app_commands.command(name="role", description="Adiciona ou remove um cargo de um membro.")
    @app_commands.describe(member="Membro", role="Cargo", action="Adicionar ou remover")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Adicionar", value="add"),
            app_commands.Choice(name="Remover", value="remove"),
        ]
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        action: str,
    ) -> None:
        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            embed = make_embed.error("Erro", "Nao pode gerenciar cargos iguais ou superiores ao seu.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if role >= interaction.guild.me.top_role:
            embed = make_embed.error("Erro", "O cargo e superior ou igual ao meu cargo.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if action == "add":
            if role in member.roles:
                embed = make_embed.error("Erro", f"{member.mention} ja possui o cargo {role.mention}.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            await member.add_roles(role, reason=f"Adicionado por {interaction.user}")
            desc = f"Cargo {role.mention} adicionado a {member.mention}."
        else:
            if role not in member.roles:
                embed = make_embed.error("Erro", f"{member.mention} nao possui o cargo {role.mention}.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            await member.remove_roles(role, reason=f"Removido por {interaction.user}")
            desc = f"Cargo {role.mention} removido de {member.mention}."

        embed = (
            make_embed("success")
            .title("Cargo Atualizado")
            .desc(desc)
            .field("Moderador", interaction.user.mention)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /NICK
    # =========================

    @app_commands.command(name="nick", description="Altera o apelido de um membro.")
    @app_commands.describe(member="Membro para alterar o apelido", nickname="Novo apelido (deixe vazio para remover)")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        nickname: str = "",
    ) -> None:
        old_nick = member.display_name
        await member.edit(nick=nickname or None, reason=f"Alterado por {interaction.user}")

        new_nick = member.display_name
        if nickname:
            desc = f"Apelido de {member.mention} alterado de **{old_nick}** para **{new_nick}**."
        else:
            desc = f"Apelido de {member.mention} foi removido (era **{old_nick}**)."

        embed = (
            make_embed("success")
            .title("Apelido Alterado")
            .desc(desc)
            .field("Moderador", interaction.user.mention)
            .thumb(member.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /AUTOMOD_CONFIG
    # =========================

    # =========================
    # /RAID_PROTECTION
    # =========================

    # =========================
    # /LOGS_CONFIG
    # =========================

    # =========================
    # /MODLOG
    # =========================

    @app_commands.command(name="modlog", description="Veja o historico de moderacao do servidor.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def modlog(self, interaction: discord.Interaction) -> None:
        logs = await db.get_mod_logs(interaction.guild.id, limit=50)

        view = ModlogView(logs, interaction.guild)
        await interaction.response.send_message(embed=view.get_page_embed(), view=view)

    # =========================
    # /AUTOMUTE
    # =========================



async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Moderacao(bot))
