from __future__ import annotations

import ast
import asyncio
import operator
import random
import string
import time
import sys
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_math_eval(expr: str) -> float | None:
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except (SyntaxError, ValueError):
        return None

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
            return _SAFE_OPS[type(node.op)](_eval(node.operand))
        raise ValueError("Unsafe expression")

    try:
        result = _eval(tree)
        if isinstance(result, float) and result == int(result) and abs(result) < 1e15:
            return int(result)
        return result
    except Exception:
        return None


class Utilidades(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot
        self.start_time = time.monotonic()

    # =========================
    # /PING
    # =========================

    @app_commands.command(name="ping", description="Mostra a latência do bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)

        if latency_ms < 100:
            status, color = "\U0001f7e2 Excelente", "success"
        elif latency_ms < 200:
            status, color = "\U0001f7e1 Boa", "warning"
        elif latency_ms < 300:
            status, color = "\U0001f7e0 Regular", "orange"
        else:
            status, color = "\U0001f534 Ruim", "error"

        embed = (
            make_embed(color)
            .title("Pong!")
            .field("\u23f1\ufe0f Latência", f"```{latency_ms}ms```", True)
            .field("\U0001f4ca Status", f"```{status}```", True)
            .field("\U0001f4e1 WebSocket", f"```{self.bot.latency:.3f}s```", True)
            .thumb(self.bot.user.display_avatar.url)
            .footer("Klaus Ping System")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /UPTIME
    # =========================

    @app_commands.command(name="uptime", description="Mostra ha quanto tempo o bot esta online.")
    async def uptime(self, interaction: discord.Interaction) -> None:
        elapsed = time.monotonic() - self.bot.start_time
        days = int(elapsed // 86400)
        hours = int((elapsed % 86400) // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if minutes: parts.append(f"{minutes}m")
        parts.append(f"{seconds}s")

        embed = (
            make_embed("purple")
            .title("Uptime")
            .desc(f"```\n{' '.join(parts)}\n```")
            .thumb(self.bot.user.display_avatar.url)
            .footer("Klaus Uptime Monitor")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CALCULAR
    # =========================

    @app_commands.command(name="calcular", description="Calcule uma expressão matemática.")
    @app_commands.describe(expressao="Expressão (ex: 2+2, 10*5, 100/4)")
    async def calcular(self, interaction: discord.Interaction, expressao: str) -> None:
        result = _safe_math_eval(expressao)
        if result is None:
            embed = make_embed.error("Inválido", "Use apenas números e operadores (+, -, *, /, **).")
        else:
            embed = (
                make_embed("success")
                .title("\U0001f522 Calculadora")
                .field("Expressão", f"```{expressao}```")
                .field("Resultado", f"```{result}```")
                .build()
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # =========================
    # /USERINFO
    # =========================

    @app_commands.command(name="userinfo", description="Mostre informações de um usuário.")
    @app_commands.describe(member="Usuário para exibir informações")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user

        roles = [r.mention for r in reversed(member.roles[1:])]
        roles_text = ", ".join(roles[:15]) if roles else "Nenhum"
        if len(roles) > 15:
            roles_text += f" +{len(roles) - 15} mais"

        status_map = {
            discord.Status.online: "\U0001f7e2 Online",
            discord.Status.idle: "\U0001f7e0 Idle",
            discord.Status.dnd: "\U0001f534 DND",
            discord.Status.offline: "\u26aa Offline",
        }

        embed = (
            make_embed(member.color if member.color != discord.Color.default() else "info")
            .title(f"\U0001f464 {member.display_name}")
            .thumb(member.display_avatar.url)
            .field("\U0001f464 Conta", f"**ID:** `{member.id}`\n**Criada:** <t:{int(member.created_at.timestamp())}:R>\n**Bot:** {'Sim' if member.bot else 'Não'}")
            .field("\U0001f3ef Servidor", f"**Entrou:** <t:{int(member.joined_at.timestamp())}:R>\n**Cargos:** {len(member.roles) - 1}" if member.joined_at else "N/A")
            .field("\U0001f310 Status", status_map.get(member.status, "Desconhecido"))
            .field(f"\U0001f3ad Cargos ({len(member.roles) - 1})", roles_text[:1024] if roles else "Nenhum")
            .footer(f"Klaus User Info \u2022 {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /SERVERINFO
    # =========================

    @app_commands.command(name="serverinfo", description="Mostra informações do servidor.")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                embed=make_embed.error("Servidor Necessário", "Este comando só pode ser usado em servidores."),
                ephemeral=True,
            )
            return

        online = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)
        boosts = guild.premium_subscription_count or 0

        embed = (
            make_embed("purple")
            .title(f"{guild.name}")
            .field("\U0001f451 Geral", f"**Dono:** {guild.owner}\n**ID:** `{guild.id}`\n**Criado:** <t:{int(guild.created_at.timestamp())}:R>")
            .field("\U0001f465 Membros", f"**Total:** {guild.member_count}\n**Online:** {online}\n**Bots:** {sum(1 for m in guild.members if m.bot)}")
            .field("\U0001f4e1 Canais", f"**Texto:** {len(guild.text_channels)}\n**Voz:** {len(guild.voice_channels)}")
            .field("\U0001f496 Boosts", f"**Nível {guild.premium_tier}** ({boosts})")
            .field("\U0001f3ad Outros", f"**Emojis:** {len(guild.emojis)}/{guild.emoji_limit}\n**Roles:** {len(guild.roles)}")
            .thumb(guild.icon.url if guild.icon else self.bot.user.display_avatar.url)
            .footer(f"Klaus Server Info \u2022 {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /POLL
    # =========================

    # =========================
    # /EMBED
    # =========================

    @app_commands.command(name="embed", description="Crie um embed personalizado.")
    @app_commands.describe(titulo="Título", descricao="Descrição", cor="Hex (ex: 0xFF0000)")
    async def embed_cmd(self, interaction: discord.Interaction, titulo: str, descricao: str, cor: str = "0x3498DB") -> None:
        try:
            color = int(cor, 16)
        except ValueError:
            await interaction.response.send_message(
                embed=make_embed.error("Cor Inválida", "Use: `0xFF0000`"),
                ephemeral=True,
            )
            return

        embed = (
            make_embed(color)
            .title(titulo)
            .desc(descricao)
            .footer(f"Criado por {interaction.user.display_name}", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /DASHBOARD
    # =========================

    @app_commands.command(name="dashboard", description="Abra o painel de configuração do bot.")
    async def dashboard(self, interaction: discord.Interaction) -> None:
        class DashboardButton(discord.ui.Button):
            def __init__(self) -> None:
                super().__init__(
                    style=discord.ButtonStyle.link,
                    label="Abrir Dashboard",
                    emoji="\U0001f5a5\ufe0f",
                    url="https://klaus-dashboard-delta.vercel.app",
                )

        class DashboardView(discord.ui.View):
            def __init__(self) -> None:
                super().__init__(timeout=60)
                self.add_item(DashboardButton())

        embed = (
            make_embed("purple")
            .title("Klaus Dashboard")
            .desc(
                "Configure seu servidor facilmente pelo site!\n\n"
                "\u2714\ufe0f **Boas-vindas** personalizadas\n"
                "\u2714\ufe0f **Auto Cargo** automático\n"
                "\u2714\ufe0f **Logs** de mensagens e moderação\n"
                "\u2714\ufe0f **Mensagem de adeus** customizável"
            )
            .field(
                "\U0001f517 Como acessar",
                "1. Clique no botão abaixo\n"
                "2. Faça login com Discord\n"
                "3. Selecione seu servidor\n"
                "4. Configure como quiser!"
            )
            .field(
                "\u26a0\ufe0f Requisitos",
                "Você precisa ter permissão de **Gerenciar Servidor** para configurar."
            )
            .thumb(self.bot.user.display_avatar.url)
            .footer("Klaus Dashboard")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=DashboardView())

    # =========================
    # /HELP
    # =========================

    @app_commands.command(name="help", description="Mostra todos os comandos.")
    async def help(self, interaction: discord.Interaction) -> None:
        economy_cmds = (
            "/daily \u2014 Recompensa diária\n"
            "/weekly \u2014 Recompensa semanal\n"
            "/streak \u2014 Sua sequência\n"
            "/recompensa \u2014 Ver recompensas\n"
            "/perfil \u2014 Seu perfil completo\n"
            "/conquistas \u2014 Todas as conquistas\n"
            "/pagar \u2014 Transferir koins\n"
            "/moeda_social \u2014 Enviar koins + msg\n"
            "/trabalhar \u2014 Ganhar koins\n"
            "/apostar \u2014 Roleta com botões\n"
            "/coinflip \u2014 Cara ou coroa\n"
            "/aposta_dados \u2014 Aposta nos dados\n"
            "/blackjack \u2014 Blackjack 21\n"
            "/slot \u2014 Caça-niquel\n"
            "/duel \u2014 Duelo PvP\n"
            "/batalhar \u2014 Batalha koins\n"
            "/crime \u2014 Cometer crime\n"
            "/heist \u2014 Assalto bancário\n"
            "/bounty \u2014 Colocar bounty\n"
            "/invest \u2014 Investir koins\n"
            "/challenges \u2014 Desafios diários\n"
            "/lucky_wheel \u2014 Roda da sorte\n"
            "/caixa_fortuna \u2014 Caixa da sorte\n"
            "/sorteio \u2014 Roda da sorte\n"
            "/cofre \u2014 Poupança com juros\n"
            "/lottery \u2014 Loteria\n"
            "/pet \u2014 Adote um pet\n"
            "/case \u2014 Abrir case gacha\n"
            "/roubar \u2014 Roubar koins\n"
            "/doar \u2014 Doar koins\n"
            "/vender \u2014 Vender itens\n"
            "/sobrevivencia \u2014 Aventura\n"
            "/saldo \u2014 Ver saldo\n"
            "/carteira \u2014 Carteira completa\n"
            "/ranking \u2014 Top 10 mais ricos\n"
            "/loja \u2014 Itens disponíveis\n"
            "/minerar \u2014 Minerar koins\n"
            "/forjar \u2014 Forjar itens"
        )
        fun_cmds = (
            "/hug \u2014 Abraçar\n"
            "/kiss \u2014 Beijo\n"
            "/slap \u2014 Tapa\n"
            "/pat \u2014 Carinho\n"
            "/ship \u2014 Compatibilidade\n"
            "/batalha \u2014 Batalha PvP\n"
            "/rps \u2014 Pedra, papel, tesoura\n"
            "/jokenpo \u2014 Jokenpô PvP\n"
            "/coin \u2014 Moeda\n"
            "/dado \u2014 Dado\n"
            "/dados \u2014 Multi-dados\n"
            "/adivinha \u2014 Adivinhe o número\n"
            "/amigo \u2014 Amigo aleatório\n"
            "/eightball \u2014 Bola 8\n"
            "/piada \u2014 Piada\n"
            "/meme \u2014 Meme\n"
            "/horoscopo \u2014 Horóscopo\n"
            "/randomnumber \u2014 Nº aleatório\n"
            "/rather \u2014 Would you rather\n"
            "/tod \u2014 Truth or Dare\n"
            "/ttt \u2014 Tic Tac Toe\n"
            "/magic \u2014 Bola Mágica\n"
            "/random \u2014 Nº aleatório\n"
            "/russian \u2014 Roulette Russo"
        )
        util_cmds = (
            "/ping \u2014 Latência\n"
            "/uptime \u2014 Tempo online\n"
            "/soma \u2014 Somar\n"
            "/calcular \u2014 Calculadora\n"
            "/avatar \u2014 Avatar\n"
            "/av \u2014 Avatar HD\n"
            "/userinfo \u2014 Info usuário\n"
            "/whois \u2014 Info detalhada\n"
            "/botinfo \u2014 Info bot\n"
            "/serverinfo \u2014 Info servidor\n"
            "/server_stats \u2014 Stats do server\n"
            "/rank \u2014 Seu rank XP\n"
            "/xpleaderboard \u2014 Ranking XP\n"
            "/poll \u2014 Enquete\n"
            "/poll2 \u2014 Enquete com botões\n"
            "/password \u2014 Gerar senha\n"
            "/embed \u2014 Embed customizado\n"
            "/snipe \u2014 Msg deletada\n"
            "/afk \u2014 Ficar AFK\n"
            "/reminder \u2014 Lembrete\n"
            "/clone \u2014 Clonar canal\n"
            "/slowmode \u2014 Slowmode\n"
            "/dashboard \u2014 Painel de config\n"
            "/help \u2014 Esta mensagem"
        )
        mod_cmds = (
            "/ban \u2014 Banir\n"
            "/kick \u2014 Expulsar\n"
            "/mute \u2014 Silenciar\n"
            "/unmute \u2014 Desmutar\n"
            "/warn \u2014 Advertir\n"
            "/warnings \u2014 Ver warns\n"
            "/clearwarnings \u2014 Limpar warns\n"
            "/slowmode_all \u2014 Slowmode\n"
            "/lock \u2014 Trancar canal\n"
            "/unlock \u2014 Destravar canal\n"
            "/add_badword \u2014 Proibir palavra\n"
            "/ticket_panel \u2014 Painel tickets\n"
            "/close_ticket \u2014 Fechar ticket\n"
            "/giveaway \u2014 Criar giveaway\n"
            "/reaction_role \u2014 Reaction role\n"
            "/correio \u2014 Enviar mensagem"
        )

        embed = (
            make_embed("purple")
            .title("Central de Comandos Klaus")
            .desc("Use `/comando` para executar.\nTodos os comandos são slash commands.")
            .field("\U0001f4b0 Economia", economy_cmds, True)
            .field("\U0001f3ae Diversão", fun_cmds, True)
            .field("\u2699\ufe0f Utilidades", util_cmds, True)
            .field("\U0001f6e1\ufe0f Moderação", mod_cmds, True)
            .thumb(self.bot.user.display_avatar.url)
            .footer(f"Klaus Bot \u2022 {len(self.bot.tree.get_commands())} comandos")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    # =========================
    # /RANK
    # =========================

    @app_commands.command(name="rank", description="Veja seu rank de XP no servidor.")
    @app_commands.describe(member="Ver rank de outro membro")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user
        if not interaction.guild:
            return

        from database import db
        xp_data = await db.get_xp(member.id, interaction.guild.id)
        xp_rank = await db.get_xp_rank(member.id, interaction.guild.id)
        needed = db._xp_for_level(xp_data["level"])
        bar = db._xp_bar(xp_data["xp"], xp_data["level"])

        embed = (
            make_embed("purple")
            .title(f"Rank de {member.display_name}")
            .thumb(member.display_avatar.url)
            .field("Level", f"```{xp_data['level']}```", True)
            .field("XP Total", f"```{xp_data['xp']}```", True)
            .field("Posição", f"```#{xp_rank}```", True)
            .field("Progresso", f"```\n{bar}\n```\n{xp_data['xp']}/{needed} XP para o próximo level", False)
            .field("Mensagens", f"```{xp_data['messages']}```", True)
            .footer(f"Klaus XP System \u2022 {interaction.guild.name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /XPLEADERBOARD
    # =========================

    @app_commands.command(name="xpleaderboard", description="Veja o ranking de XP do servidor.")
    async def xpleaderboard(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return

        from database import db
        entries = await db.get_xp_leaderboard(interaction.guild.id, 10)
        user_rank = await db.get_xp_rank(interaction.user.id, interaction.guild.id)

        medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
        lines = []
        for entry in entries:
            try:
                user = await self.bot.fetch_user(entry["discord_id"])
                name = user.display_name
            except discord.NotFound:
                name = f"ID: {entry['discord_id']}"
            medal = medals[entry["rank"] - 1] if entry["rank"] <= 3 else f"`#{entry['rank']}`"
            lines.append(f"{medal} **{name}** \u2014 Level **{entry['level']}** ({entry['xp']} XP)")

        embed = (
            make_embed("purple")
            .title("XP Leaderboard \u2014 Top 10")
            .desc("\n".join(lines) if lines else "Nenhum dado ainda.")
            .field("Sua Posicao", f"```#{user_rank}```")
            .thumb(interaction.guild.icon.url if interaction.guild.icon else self.bot.user.display_avatar.url)
            .footer(f"Klaus XP \u2022 {interaction.guild.name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /AVATAR
    # =========================

    @app_commands.command(name="avatar", description="Veja o avatar de um membro.")
    @app_commands.describe(member="Membro para ver o avatar")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user
        avatar_url = member.display_avatar.url

        embed = (
            make_embed(member.color if member.color != discord.Color.default() else "info")
            .title(f"Avatar de {member.display_name}")
            .image(avatar_url)
            .field("Formatos", f"[PNG]({avatar_url}?size=1024) | [JPG]({avatar_url}&size=1024) | [WebP]({avatar_url}&size=1024)")
            .footer(f"Klaus Avatar \u2022 {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /WHOIS
    # =========================

    @app_commands.command(name="whois", description="Informacoes detalhadas de um usuario.")
    @app_commands.describe(member="Usuario para analisar")
    async def whois(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user

        from database import db
        user_data = await db.get_user(member.id)
        koins = user_data.get("koins", 0)
        rank = await db.get_user_rank(member.id)
        achievements = len(user_data.get("achievements", []))

        roles = [r.mention for r in reversed(member.roles[1:])]
        roles_text = ", ".join(roles[:10]) if roles else "Nenhum"
        if len(roles) > 10:
            roles_text += f" +{len(roles) - 10} mais"

        status_map = {
            discord.Status.online: "\U0001f7e2 Online",
            discord.Status.idle: "\U0001f7e0 Idle",
            discord.Status.dnd: "\U0001f534 DND",
            discord.Status.offline: "\u26aa Offline",
        }

        embed = (
            make_embed(member.color if member.color != discord.Color.default() else "info")
            .title(f"\U0001f50d {member.display_name}")
            .thumb(member.display_avatar.url)
            .field(
                "\U0001f464 Conta",
                f"**ID:** `{member.id}`\n"
                f"**Criada:** <t:{int(member.created_at.timestamp())}:R>\n"
                f"**Bot:** {'Sim' if member.bot else 'Nao'}\n"
                f"**Avatar:** [Link]({member.display_avatar.url})",
            )
            .field(
                "\U0001f3ef Servidor",
                f"**Entrou:** <t:{int(member.joined_at.timestamp())}:R>\n" if member.joined_at else "**Entrou:** N/A\n"
                f"**Cargos:** {len(member.roles) - 1}\n"
                f"**Top Role:** {member.top_role.mention}"
            )
            .field("\U0001f310 Status", status_map.get(member.status, "Desconhecido"))
            .field("\U0001f4b0 Klaus Economy", f"**Koins:** `{koins:,}`\n**Rank:** `#{rank}`\n**Conquistas:** `{achievements}`")
            .field(f"\U0001f3ad Cargos ({len(member.roles) - 1})", roles_text[:1024] if roles else "Nenhum")
            .footer(f"Klaus WhoIs \u2022 {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /BOTINFO
    # =========================

    @app_commands.command(name="botinfo", description="Informacoes sobre o Klaus Bot.")
    async def botinfo(self, interaction: discord.Interaction) -> None:
        import platform
        from database import db

        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count or 0 for g in self.bot.guilds)
        total_commands = len(self.bot.tree.get_commands())
        loaded_cogs = len(self.bot.extensions)
        latency = round(self.bot.latency * 1000)

        elapsed = time.monotonic() - self.bot.start_time
        days = int(elapsed // 86400)
        hours = int((elapsed % 86400) // 3600)
        minutes = int((elapsed % 3600) // 60)
        uptime_str = f"{days}d {hours}h {minutes}m"

        total_users = await db.get_total_users()

        embed = (
            make_embed("purple")
            .title("\U0001f916 Klaus Bot")
            .desc("Bot multifuncional com economia, diversao, moderacao e muito mais!")
            .field(
                "\U0001f4ca Estatisticas",
                f"**Servidores:** `{guild_count}`\n"
                f"**Usuarios:** `{user_count}`\n"
                f"**Usuarios no DB:** `{total_users}`\n"
                f"**Comandos:** `{total_commands}`\n"
                f"**Cogs:** `{loaded_cogs}`",
            )
            .field(
                "\U0001f310 Sistema",
                f"**Uptime:** `{uptime_str}`\n"
                f"**Latencia:** `{latency}ms`\n"
                f"**Python:** `{platform.python_version()}`\n"
                f"**Discord.py:** `{discord.__version__}`\n"
                f"**Plataforma:** `{platform.system()}`",
            )
            .field(
                "\U0001f517 Links",
                "[Dashboard](https://klaus-dashboard-delta.vercel.app) | "
                "[Suporte](https://discord.gg/klaus)"
            )
            .thumb(self.bot.user.display_avatar.url)
            .footer(f"Klaus Bot v3.0.0 \u2022 {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /SNIPE
    # =========================

    @app_commands.command(name="snipe", description="Veja a ultima mensagem deletada no canal.")
    async def snipe(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            return

        if not hasattr(self.bot, "_snipe_cache"):
            self.bot._snipe_cache: dict[int, dict] = {}

        cache = self.bot._snipe_cache.get(interaction.channel.id)
        if not cache:
            await interaction.response.send_message(
                embed=make_embed.warn("Aviso", "Nenhuma mensagem deletada encontrada."), ephemeral=True
            )
            return

        embed = (
            make_embed("info")
            .title("\U0001f4a4 Mensagem Deletada")
            .field("Autor", f"{cache.get('author', 'Desconhecido')}")
            .field("Conteudo", f"```{cache.get('content', 'Sem conteudo')[:1000]}```")
            .field("Deletada em", f"<t:{int(cache.get('timestamp', 0))}:R>")
            .footer("Klaus Snipe")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Utilidades(bot))