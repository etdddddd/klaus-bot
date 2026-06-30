from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from klaus import KlausBot

logger = logging.getLogger(__name__)

XP_COOLDOWN: dict[int, float] = {}

LEVEL_MILESTONES = {10, 25, 50, 100}

LEVEL_UP_CONGRATS_GIFS = [
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o7buirYcmV5nSwIRW/giphy.gif",
    "https://media.giphy.com/media/26ufdipQqU2hNA4Gc/giphy.gif",
    "https://media.giphy.com/media/l0HlBO7eyXzSZkJri/giphy.gif",
    "https://media.giphy.com/media/26BRv0ThflsHCqDrG/giphy.gif",
]


def _format_time_delta(delta) -> str:
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m {seconds % 60}s"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h {minutes % 60}m"
    days = hours // 24
    if days < 30:
        return f"{days}d {hours % 24}h"
    months = days // 30
    if months < 12:
        return f"{months}m {days % 30}d"
    years = days // 365
    return f"{years}a {days % 365}d"


class Eventos(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot

    async def _get_guild_cfg(self, guild_id: int) -> dict:
        return await self.bot.db.get_guild_config(guild_id)

    def _parse_color(self, color_str: str, default: int = 0x8B5CF6) -> int:
        try:
            return int(color_str.lstrip("#"), 16)
        except (ValueError, TypeError):
            return default

    def _get_account_risk(self, member: discord.Member) -> tuple[str, int]:
        account_age = discord.utils.utcnow() - member.created_at
        days = account_age.days
        if days < 7:
            return "\U0001f534 Suspeita (< 7 dias)", 0xEF4444
        elif days < 30:
            return "\U0001f7e1 Nova (< 30 dias)", 0xFBBF24
        else:
            return "\U0001f7e2 Segura (30+ dias)", 0x22C55E

    def _get_top_role_color(self, member: discord.Member) -> int:
        if member.roles:
            for role in reversed(member.roles[1:]):
                if role.color.value != 0:
                    return role.color.value
        return 0x8B5CF6

    # ── MEMBER JOIN: welcome + log ───────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        cfg = await self._get_guild_cfg(member.guild.id)

        if cfg.get("welcome_enabled"):
            ch_id = cfg.get("welcome_channel")
            if ch_id:
                channel = member.guild.get_channel(int(ch_id))
                if isinstance(channel, discord.TextChannel):
                    title = cfg.get("welcome_title", "Bem-vindo!")
                    msg = cfg.get("welcome_message", "Bem-vindo(a) ao servidor, {user}!")
                    msg = msg.replace("{user}", member.mention)
                    msg = msg.replace("{server}", member.guild.name)
                    msg = msg.replace("{count}", str(member.guild.member_count))
                    msg = msg.replace("{mention}", member.mention)

                    risk_text, risk_color = self._get_account_risk(member)

                    embed = discord.Embed(
                        title=title,
                        description=msg,
                        color=risk_color,
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_image(url="https://cdn.discordapp.com/banners/1502096967055184024/a_1b5e3b7c9e4f8d2a6c0b3e5f7d9a1c4e.png?size=600")
                    embed.add_field(
                        name="📅 Membro #",
                        value=str(member.guild.member_count),
                        inline=True,
                    )
                    embed.add_field(
                        name="⏱️ Conta criada",
                        value=f"<t:{int(member.created_at.timestamp())}:R>",
                        inline=True,
                    )
                    embed.add_field(
                        name="🛡️ Risco",
                        value=risk_text,
                        inline=True,
                    )
                    embed.add_field(name="ID", value=str(member.id), inline=True)
                    embed.set_footer(text=f"{member.guild.name} • {member.guild.member_count} membros")
                    try:
                        await channel.send(content=member.mention, embed=embed)
                    except discord.HTTPException as e:
                        logger.debug("Welcome send failed: %s", e)

        autorole_enabled = cfg.get("autorole_enabled")
        autorole_id = cfg.get("autorole_role")
        if autorole_enabled and autorole_id:
            role = member.guild.get_role(int(autorole_id))
            if role:
                try:
                    await member.add_roles(role, reason="Auto Cargo via dashboard")
                except discord.HTTPException as e:
                    logger.debug("Event action failed: %s", e)

        if cfg.get("logs_enabled") and cfg.get("logging_members"):
            log_ch_id = cfg.get("logs_channel")
            if log_ch_id:
                log_ch = member.guild.get_channel(int(log_ch_id))
                if isinstance(log_ch, discord.TextChannel):
                    account_age = discord.utils.utcnow() - member.created_at
                    days = account_age.days
                    risk = "\U0001f534 Suspeita" if days < 7 else "\U0001f7e1 Nova" if days < 30 else "\U0001f7e2 Segura"

                    embed = discord.Embed(
                        title="\U0001f465 Membro Entrou",
                        description=f"{member.mention} ({member})",
                        color=0x22C55E,
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.add_field(name="ID", value=str(member.id), inline=True)
                    embed.add_field(name="Membros", value=str(member.guild.member_count), inline=True)
                    embed.add_field(name="Conta", value=f"{days} dias", inline=True)
                    embed.add_field(name="Risco", value=risk, inline=True)
                    embed.add_field(name="Criado em", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
                    try:
                        await log_ch.send(embed=embed)
                    except discord.HTTPException as e:
                        logger.debug("Event action failed: %s", e)

    # ── MEMBER REMOVE: farewell + log ────────────────────────

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        cfg = await self._get_guild_cfg(member.guild.id)

        if cfg.get("farewell_enabled"):
            ch_id = cfg.get("farewell_channel")
            if ch_id:
                channel = member.guild.get_channel(int(ch_id))
                if isinstance(channel, discord.TextChannel):
                    title = cfg.get("farewell_title", "Adeus!")
                    msg = cfg.get("farewell_message", "Tchau, {user}!")
                    msg = msg.replace("{user}", member.display_name)
                    msg = msg.replace("{server}", member.guild.name)
                    msg = msg.replace("{count}", str(member.guild.member_count))

                    farewell_color = self._get_top_role_color(member)

                    embed = discord.Embed(
                        title=title,
                        description=msg,
                        color=farewell_color,
                        timestamp=discord.utils.utcnow(),
                    )
                    if member.display_avatar:
                        embed.set_thumbnail(url=member.display_avatar.url)

                    if member.joined_at:
                        join_timestamp = f"<t:{int(member.joined_at.timestamp())}:R>"
                        time_in_server = _format_time_delta(discord.utils.utcnow() - member.joined_at)
                    else:
                        join_timestamp = "Desconhecido"
                        time_in_server = "Desconhecido"

                    embed.add_field(
                        name="📅 Membro desde",
                        value=join_timestamp,
                        inline=True,
                    )
                    embed.add_field(
                        name="⏱️ Tempo no servidor",
                        value=time_in_server,
                        inline=True,
                    )

                    roles = [r.mention for r in member.roles[1:10]]
                    roles_text = ", ".join(roles) if roles else "Nenhum"
                    if len(member.roles) > 11:
                        roles_text += f" (+{len(member.roles) - 11} mais)"
                    embed.add_field(
                        name=f"🏷️ Cargos ({len(member.roles) - 1})",
                        value=roles_text,
                        inline=False,
                    )

                    embed.add_field(
                        name="👥 Membros restantes",
                        value=str(member.guild.member_count - 1),
                        inline=True,
                    )

                    embed.add_field(name="ID", value=str(member.id), inline=True)
                    embed.set_footer(text=f"{member.guild.name} • {member.guild.member_count - 1} membros restantes")
                    try:
                        await channel.send(embed=embed)
                    except discord.HTTPException as e:
                        logger.debug("Farewell send failed: %s", e)

        if cfg.get("logs_enabled") and cfg.get("logging_members"):
            log_ch_id = cfg.get("logs_channel")
            if log_ch_id:
                log_ch = member.guild.get_channel(int(log_ch_id))
                if isinstance(log_ch, discord.TextChannel):
                    roles = [r.mention for r in member.roles[1:5]]
                    roles_text = ", ".join(roles) if roles else "Nenhum"
                    join_time = discord.utils.utcnow() - member.joined_at if member.joined_at else None
                    days_in_server = join_time.days if join_time else "Desconhecido"

                    embed = discord.Embed(
                        title="\U0001f465 Membro Saiu",
                        description=f"**{member}** ({member.id})",
                        color=0xEF4444,
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.add_field(name="Membros", value=str(member.guild.member_count), inline=True)
                    embed.add_field(name="Tempo no Server", value=f"{days_in_server} dias", inline=True)
                    embed.add_field(name="Cargos", value=roles_text, inline=False)
                    if member.display_avatar:
                        embed.set_thumbnail(url=member.display_avatar.url)
                    try:
                        await log_ch.send(embed=embed)
                    except discord.HTTPException as e:
                        logger.debug("Event action failed: %s", e)

    # ── LOGS: MESSAGE EDIT ───────────────────────────────────

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot or not before.guild:
            return
        if before.content == after.content:
            return

        cfg = await self._get_guild_cfg(before.guild.id)

        if not cfg.get("logs_enabled") or not cfg.get("logging_messages"):
            return

        ch_id = cfg.get("logs_channel")
        if not ch_id:
            return
        log_ch = before.guild.get_channel(int(ch_id))
        if not isinstance(log_ch, discord.TextChannel):
            return

        before_text = before.content[:1000] or "(vazio)"
        after_text = after.content[:1000] or "(vazio)"

        embed = discord.Embed(
            title="\u270f\ufe0f Mensagem Editada",
            color=0xEAB308,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=before.author.display_avatar.url)
        embed.add_field(name="Autor", value=before.author.mention, inline=True)
        embed.add_field(name="Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(name="Antes", value=f"```{before_text}```", inline=False)
        embed.add_field(name="Depois", value=f"```{after_text}```", inline=False)
        embed.add_field(name="🔗 Link", value=f"[Ir para mensagem]({before.jump_url})", inline=True)

        len_before = len(before.content)
        len_after = len(after.content)
        diff = len_after - len_before
        diff_str = f"+{diff}" if diff > 0 else str(diff)
        embed.add_field(
            name="📊 Tamanho",
            value=f"{len_before} → {len_after} ({diff_str})",
            inline=True,
        )

        if before.edited_at and before.created_at:
            edit_delta = before.edited_at - before.created_at
            embed.add_field(
                name="⏱️ Editado após",
                value=_format_time_delta(edit_delta),
                inline=True,
            )

        embed.set_footer(text=f"ID: {before.author.id}")

        try:
            await log_ch.send(embed=embed)
        except discord.HTTPException as e:
            logger.debug("Event action failed: %s", e)

    # ── LOGS: MESSAGE DELETE ─────────────────────────────────

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        cfg = await self._get_guild_cfg(message.guild.id)
        if not cfg.get("logs_enabled") or not cfg.get("logging_messages"):
            return

        ch_id = cfg.get("logs_channel")
        if not ch_id:
            return
        log_ch = message.guild.get_channel(int(ch_id))
        if not isinstance(log_ch, discord.TextChannel):
            return

        content = message.content[:1000] if message.content else "(vazio)"

        embed = discord.Embed(
            title="\U0001f5d1\ufe0f Mensagem Deletada",
            color=0xEF4444,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        embed.add_field(name="Autor", value=message.author.mention, inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        embed.add_field(name="📝 Conteúdo Anterior", value=f"```{content}```", inline=False)

        if message.attachments:
            attachments_list = []
            for i, att in enumerate(message.attachments[:10], 1):
                attachments_list.append(f"[{att.filename}]({att.url})")
            files = "\n".join(attachments_list)
            embed.add_field(name=f"📎 Anexos ({len(message.attachments)})", value=files, inline=False)
        else:
            embed.add_field(name="📎 Anexos", value="Nenhum", inline=True)

        embed.add_field(name="🔗 Link", value=f"[Ir para mensagem]({message.jump_url})", inline=False)
        embed.set_footer(text=f"ID: {message.author.id}")

        try:
            await log_ch.send(embed=embed)
        except discord.HTTPException as e:
            logger.debug("Event action failed: %s", e)

    # ── XP SYSTEM ────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return

        cfg = await self._get_guild_cfg(message.guild.id)
        if not cfg.get("xp_enabled"):
            return

        user_id = message.author.id
        guild_id = message.guild.id
        now = time.time()
        cooldown = cfg.get("xp_cooldown", 60)
        is_premium = await self.bot.db.is_premium(user_id)
        if is_premium:
            cooldown //= 2

        last = XP_COOLDOWN.get(user_id, 0)
        if now - last < cooldown:
            return
        XP_COOLDOWN[user_id] = now
        if len(XP_COOLDOWN) > 5000:
            stale = [k for k, v in XP_COOLDOWN.items() if now - v > 300]
            for k in stale:
                del XP_COOLDOWN[k]

        xp_min = cfg.get("xp_min", 15)
        xp_max = cfg.get("xp_max", 25)
        xp_amount = random.randint(xp_min, xp_max)

        bonus_event = random.random() < 0.10
        if bonus_event:
            xp_amount *= 2

        if is_premium:
            xp_amount *= 2

        result = await self.bot.db.add_xp(user_id, guild_id, xp_amount)

        if result["leveled_up"]:
            announce = cfg.get("xp_announce_channel", "")
            if announce:
                ch = message.guild.get_channel(int(announce))
                if isinstance(ch, discord.TextChannel):
                    old_level = result["old_level"]
                    new_level = result["level"]
                    total_xp = result["xp"]

                    xp_for_next = (new_level * 100) ** 2
                    xp_needed = max(0, xp_for_next - total_xp)

                    embed = discord.Embed(
                        title="🎉 Level Up!",
                        description=f"Parabéns {message.author.mention}! Você subiu para o **Level {new_level}**!",
                        color=0xFFD700,
                        timestamp=discord.utils.utcnow(),
                    )
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.set_image(url=random.choice(LEVEL_UP_CONGRATS_GIFS))

                    embed.add_field(name="📊 XP Total", value=f"`{total_xp}`", inline=True)
                    embed.add_field(name="🎯 Próximo Level", value=f"`{xp_needed} XP`", inline=True)

                    try:
                        leaderboard = await self.bot.db.get_leaderboard(guild_id)
                        position = "N/A"
                        for i, entry in enumerate(leaderboard[:100], 1):
                            if entry["user_id"] == user_id:
                                position = f"#{i}"
                                break
                        embed.add_field(name="🏆 Ranking", value=f"`{position}`", inline=True)
                    except Exception:
                        embed.add_field(name="🏆 Ranking", value="`N/A`", inline=True)

                    embed.add_field(name="Level Anterior", value=str(old_level), inline=True)
                    embed.add_field(name="Level Atual", value=str(new_level), inline=True)

                    if bonus_event:
                        embed.add_field(name="⭐ Bônus", value="Evento aleatório! 2x XP!", inline=True)

                    if new_level in LEVEL_MILESTONES:
                        milestone_messages = {
                            10: "🌟 Você alcançou o **Level 10**! Continue assim!",
                            25: "🔥 **Level 25**! Você é um membro dedicado!",
                            50: "💎 **Level 50**! Lenda do servidor!",
                            100: "👑 **Level 100**! Mestre absoluto! Você é lendário!",
                        }
                        embed.add_field(
                            name="🎯 Marco Alcançado!",
                            value=milestone_messages.get(new_level, f"Parabéns pelo Level {new_level}!"),
                            inline=False,
                        )

                    embed.set_footer(text="Klaus XP System")
                    try:
                        await ch.send(embed=embed)
                    except discord.HTTPException as e:
                        logger.debug("Event action failed: %s", e)

            role_rewards = cfg.get("xp_role_rewards", {})
            role_id = role_rewards.get(str(result["level"]))
            if role_id:
                role = message.guild.get_role(int(role_id))
                if role:
                    try:
                        await message.author.add_roles(role, reason=f"Level {result['level']} reward")
                    except discord.HTTPException as e:
                        logger.debug("Event action failed: %s", e)

    # ── MEMBER UPDATE: role change logs ──────────────────────

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.roles == after.roles:
            return

        cfg = await self._get_guild_cfg(before.guild.id)
        if not cfg.get("logs_enabled") or not cfg.get("logging_members"):
            return

        ch_id = cfg.get("logs_channel")
        if not ch_id:
            return
        log_ch = before.guild.get_channel(int(ch_id))
        if not isinstance(log_ch, discord.TextChannel):
            return

        before_role_ids = set(r.id for r in before.roles)
        after_role_ids = set(r.id for r in after.roles)

        added_role_ids = after_role_ids - before_role_ids
        removed_role_ids = before_role_ids - after_role_ids

        added_roles = [before.guild.get_role(rid) for rid in added_role_ids if before.guild.get_role(rid)]
        removed_roles = [before.guild.get_role(rid) for rid in removed_role_ids if before.guild.get_role(rid)]

        if not added_roles and not removed_roles:
            return

        if before.top_role.color.value != 0:
            embed_color = before.top_role.color.value
        elif after.top_role.color.value != 0:
            embed_color = after.top_role.color.value
        else:
            embed_color = 0x5865F2

        embed = discord.Embed(
            title="🏷️ Cargos Atualizados",
            description=f"**{before}** ({before.id})",
            color=embed_color,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=before.display_avatar.url)

        if added_roles:
            added_text = " ".join(r.mention for r in added_roles[:20])
            embed.add_field(name=f"➕ Adicionados ({len(added_roles)})", value=added_text, inline=False)

        if removed_roles:
            removed_text = " ".join(r.mention for r in removed_roles[:20])
            embed.add_field(name=f"➖ Removidos ({len(removed_roles)})", value=removed_text, inline=False)

        all_before = ", ".join(r.name for r in before.roles[1:10])
        all_after = ", ".join(r.name for r in after.roles[1:10])

        embed.add_field(
            name="📋 Antes",
            value=all_before if all_before else "Nenhum cargo",
            inline=True,
        )
        embed.add_field(
            name="📋 Depois",
            value=all_after if all_after else "Nenhum cargo",
            inline=True,
        )

        embed.set_footer(text=f"ID: {before.id}")
        try:
            await log_ch.send(embed=embed)
        except discord.HTTPException as e:
            logger.debug("Event action failed: %s", e)

    # ── VOICE STATE UPDATE: voice event logs ─────────────────

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot:
            return

        cfg = await self._get_guild_cfg(member.guild.id)
        if not cfg.get("logs_enabled") or not cfg.get("voice_events"):
            return

        ch_id = cfg.get("logs_channel")
        if not ch_id:
            return
        log_ch = member.guild.get_channel(int(ch_id))
        if not isinstance(log_ch, discord.TextChannel):
            return

        joined = before.channel is None and after.channel is not None
        left = before.channel is not None and after.channel is None
        moved = before.channel is not None and after.channel is not None and before.channel.id != after.channel.id

        if not (joined or left or moved):
            return

        if member.top_role.color.value != 0:
            embed_color = member.top_role.color.value
        else:
            embed_color = 0x00AFF4

        if joined:
            embed = discord.Embed(
                title="🔊 Entrou no Canal de Voz",
                description=f"{member.mention} entrou em **{after.channel.name}**",
                color=0x22C55E,
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(
                name="👥 Membros no Canal",
                value=str(len(after.channel.members)),
                inline=True,
            )
        elif left:
            embed = discord.Embed(
                title="🔇 Saiu do Canal de Voz",
                description=f"{member.mention} saiu de **{before.channel.name}**",
                color=0xEF4444,
                timestamp=discord.utils.utcnow(),
            )
            embed.add_field(
                name="👥 Membros no Canal",
                value=str(len(before.channel.members)),
                inline=True,
            )
        elif moved:
            embed = discord.Embed(
                title="🔀 Moveu entre Canais",
                description=f"{member.mention} moveu de **{before.channel.name}** para **{after.channel.name}**",
                color=0xEAB308,
                timestamp=discord.utils.utcnow(),
            )

        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")

        try:
            await log_ch.send(embed=embed)
        except discord.HTTPException as e:
            logger.debug("Event action failed: %s", e)

    # ── PRESENCE UPDATE: status change logs ──────────────────

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.bot:
            return

        cfg = await self._get_guild_cfg(before.guild.id)
        if not cfg.get("logs_enabled") or not cfg.get("presence_events"):
            return

        ch_id = cfg.get("logs_channel")
        if not ch_id:
            return
        log_ch = before.guild.get_channel(int(ch_id))
        if not isinstance(log_ch, discord.TextChannel):
            return

        before_status = str(before.status)
        after_status = str(after.status)

        if before_status == after_status:
            return

        status_emojis = {
            "online": ("🟢", "Online"),
            "idle": ("🌙", "Idle"),
            "dnd": ("🔴", "Não Perturbe"),
            "offline": ("⚫", "Offline"),
            "invisible": ("⚫", "Invisível"),
        }

        before_emoji, before_name = status_emojis.get(before_status, ("❓", before_status))
        after_emoji, after_name = status_emojis.get(after_status, ("❓", after_status))

        if before_status in ("online", "idle", "dnd") and after_status == "offline":
            embed_color = 0xEF4444
        elif before_status == "offline" and after_status in ("online", "idle", "dnd"):
            embed_color = 0x22C55E
        else:
            embed_color = 0xEAB308

        embed = discord.Embed(
            title="📡 Status Atualizado",
            description=f"**{before}** ({before.id})",
            color=embed_color,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=before.display_avatar.url)
        embed.add_field(
            name="Antes",
            value=f"{before_emoji} {before_name}",
            inline=True,
        )
        embed.add_field(
            name="Depois",
            value=f"{after_emoji} {after_name}",
            inline=True,
        )
        embed.set_footer(text=f"ID: {before.id}")

        try:
            await log_ch.send(embed=embed)
        except discord.HTTPException as e:
            logger.debug("Event action failed: %s", e)

    # ── GUILD ────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info("Joined guild: %s (%d)", guild, guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.info("Left guild: %s (%d)", guild, guild.id)


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Eventos(bot))
