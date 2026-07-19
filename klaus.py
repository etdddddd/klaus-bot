import asyncio
import datetime
import logging
import os
import random
import signal
import sys
import time
import traceback

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    C = Fore  # shorthand
    R = Style.RESET_ALL
    BOLD = Style.BRIGHT
    DIM = Style.DIM
except ImportError:
    C = type("Fore", (), {k: "" for k in ("GREEN","YELLOW","RED","CYAN","MAGENTA","WHITE","BLUE","LIGHTGREEN_EX","LIGHTYELLOW_EX","LIGHTRED_EX","LIGHTCYAN_EX","LIGHTMAGENTA_EX","RESET")})()
    R = ""
    BOLD = ""
    DIM = ""

import discord
from discord import app_commands
from discord.ext import commands, tasks

from config import settings
from database import db
from embed_builder import KlausEmbed as make_embed
from logger_config import setup_logging


def _t(color: str, text: str) -> str:
    return f"{color}{text}{R}"


def _box_line(content: str, width: int = 60) -> str:
    padding = width - len(content.replace("\033[", "").replace("[0m", "")) - 4
    return f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {content}{' ' * max(padding, 1)}{C.LIGHTMAGENTA_EX}{BOLD}║{R}"


def print_startup_banner(bot: "KlausBot") -> None:
    guild_count = len(bot.guilds)
    user_count = sum(g.member_count or 0 for g in bot.guilds)
    elapsed = time.monotonic() - bot.start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    loaded_exts = len(bot.extensions)
    total_cmds = len(bot.tree.get_commands())
    latency = round(bot.latency * 1000)
    bot_name = bot.user.name if bot.user else "N/A"
    bot_id = bot.user.id if bot.user else 0
    now = datetime.datetime.now()

    lat_color = C.LIGHTGREEN_EX if latency < 150 else C.LIGHTYELLOW_EX if latency < 400 else C.LIGHTRED_EX
    lat_icon = "\u25cf" if latency < 150 else "\u25ac" if latency < 400 else "\u25cf"

    print()
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}╔══════════════════════════════════════════════════════════════╗{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}                                                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  ██╗  ██╗██╗      █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  ██║ ██╔╝██║     ██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  █████╔╝ ██║     ███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  ██╔═██╗ ██║     ██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  ██║  ██╗███████╗██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTMAGENTA_EX}{BOLD}  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {DIM}                      S Y S T E M   v 3 . 0 . 0{R}                       {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}                                                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}╠══════════════════════════════════════════════════════════════╣{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Bot     {DIM}:{R}  {_t(C.LIGHTGREEN_EX, bot_name)} {DIM}({bot_id}){R}                                {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Version {DIM}:{R}  {_t(C.LIGHTMAGENTA_EX, '1.3.0')} {_t(DIM, '|')} {_t(C.WHITE, 'discord.py')} {_t(DIM, discord.__version__)}                     {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Date    {DIM}:{R}  {_t(C.WHITE, now.strftime('%d/%m/%Y %H:%M:%S'))}                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}                                                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {DIM}─── Runtime ────────────────────────────────────────────────{R}  {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Guilds  {DIM}:{R}  {_t(C.LIGHTGREEN_EX, str(guild_count))}  {DIM}│{R}  {C.WHITE}Users   {DIM}:{R}  {_t(C.LIGHTCYAN_EX, str(user_count))}                          {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Cogs    {DIM}:{R}  {_t(C.LIGHTYELLOW_EX, str(loaded_exts))}  {DIM}│{R}  {C.WHITE}Cmds    {DIM}:{R}  {_t(C.LIGHTMAGENTA_EX, str(total_cmds))}                          {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Uptime  {DIM}:{R}  {_t(C.WHITE, f'{hours}h {minutes}m {seconds}s')}                                   {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.WHITE}Latency {DIM}:{R}  {_t(lat_color, f'{lat_icon} {latency}ms')}                                          {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}                                                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}  {C.LIGHTGREEN_EX}{BOLD}  \u25cf ONLINE{R}  {DIM}All systems operational{R}                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}║{R}                                                              {C.LIGHTMAGENTA_EX}{BOLD}║{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}╚══════════════════════════════════════════════════════════════╝{R}")
    print()


intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class KlausBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(settings.command_prefix),
            intents=intents,
            help_command=None,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(settings.rank_thresholds)} ranks | /help",
            ),
            status=discord.Status.online,
        )
        self.db = db
        self.start_time = time.monotonic()
        self._total_commands_today: int = 0
        self._total_koins_earned_today: int = 0
        self._total_messages_processed: int = 0
        self._total_commands_executed: int = 0
        self._daily_commands: int = 0
        self._daily_koins: int = 0
        self._last_stats_reset: datetime.datetime | None = None
        self._auto_response_guilds: set[int] = set()

    async def setup_hook(self) -> None:
        extensions = [
            "cogs.economia",
            "cogs.diversao",
            "cogs.utilidades",
            "cogs.eventos",
            "cogs.moderacao",
            "cogs.utilidades_extra",
            "cogs.diversao_extra",
            "cogs.automod",
            "cogs.tickets",
            "cogs.giveaway",
            "cogs.social",
        ]
        for ext in extensions:
            try:
                await self.load_extension(ext)
                logging.info("Loaded extension: %s", ext)
            except Exception:
                logging.exception("Failed to load extension: %s", ext)

        synced = await self.tree.sync()
        logging.info("Synced %d slash commands", len(synced))

    async def on_ready(self) -> None:
        assert self.user is not None
        logging.info(
            "Logged in as %s (ID: %d) | %d guilds | %d users",
            self.user,
            self.user.id,
            len(self.guilds),
            sum(g.member_count or 0 for g in self.guilds),
        )

        try:
            await db.connect()
            healthy = await db.health_check()
            if healthy:
                logging.info("Database connection verified OK")
            else:
                logging.warning("Database ping failed")
        except Exception as e:
            logging.exception("Database connection check failed during on_ready: %s", e)

        loaded_exts = len(self.extensions)
        total_cmds = len(self.tree.get_commands())
        logging.info("Loaded %d cogs | %d registered slash commands", loaded_exts, total_cmds)

        print_startup_banner(self)

        asyncio.create_task(terminal_console(self))

        await self._load_auto_response_guilds()

        if not self.broadcast_loop.is_running():
            self.broadcast_loop.start()
        if not self.leave_queue_loop.is_running():
            self.leave_queue_loop.start()
        if not self.presence_loop.is_running():
            self.presence_loop.start()
        if not self.reminder_loop.is_running():
            self.reminder_loop.start()
        if not self.giveaway_loop.is_running():
            self.giveaway_loop.start()
        if not self.stats_loop.is_running():
            self.stats_loop.start()

    async def _load_auto_response_guilds(self) -> None:
        try:
            cursor = db.guilds.find({"auto_response": True})
            async for doc in cursor:
                self._auto_response_guilds.add(doc.get("guild_id", 0))
            logging.info("Loaded auto-response for %d guilds", len(self._auto_response_guilds))
        except Exception as e:
            logging.exception("Failed to load auto-response guilds: %s", e)

    # =========================
    # ON MEMBER JOIN
    # =========================

    async def on_member_join(self, member: discord.Member) -> None:
        guild = member.guild
        logging.info("Member %s (ID: %d) joined guild %s (ID: %d)", member, member.id, guild, guild.id)

        try:
            config = await db.get_guild_config(guild.id)
            if not config.get("welcome_enabled", True):
                return

            welcome_channel_id = config.get("welcome_channel")
            if welcome_channel_id:
                channel = self.get_channel(welcome_channel_id)
            else:
                channel = guild.system_channel

            if not isinstance(channel, discord.TextChannel):
                return

            embed = discord.Embed(
                title=f"\U0001f44b Bem-vindo(a) ao {guild.name}!",
                description=(
                    f"Olá {member.mention}, que bom te ver por aqui!\n\n"
                    f"**Meu nome e Klaus**, seu bot multifuncional.\n"
                    f"Aqui voce pode economizar, se divertir, subir de nivel e muito mais.\n\n"
                    f"\U0001f4a1 **Como comecar:**\n"
                    f"> Use `/daily` para receber koins diarios\n"
                    f"> Use `/perfil` para ver seu perfil completo\n"
                    f"> Use `/help` para ver todos os comandos\n"
                    f"> Use `/minerar` para minerar koins\n"
                    f"> Use `/trabalhar` para trabalhar e ganhar koins\n\n"
                    f"\U0001f310 **Dashboard:** <https://klaus-bot.com/dashboard>\n\n"
                    f"**Comandos populares:**\n"
                    f"`/daily` `/minerar` `/trabalhar` `/apostar` `/crime`\n"
                    f"`/perfil` `/rank` `/loja` `/pet` `/giveaway`\n\n"
                    f"Se precisar de ajuda, crie um **ticket** com `/ticket`."
                ),
                color=0x8B5CF6,
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"Membro #{guild.member_count} \u2022 Klaus Bot")
            embed.timestamp = discord.utils.utcnow()

            await channel.send(embed=embed)
            logging.info("Welcome message sent to %s in guild %s", channel.name, guild.name)

        except discord.HTTPException:
            logging.exception("Failed to send welcome message in guild %s", guild.name)
        except Exception as e:
            logging.exception("Error in on_member_join for guild %s: %s", guild.name, e)

    # =========================
    # ON GUILD REMOVE
    # =========================

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logging.info("Bot removed from guild: %s (ID: %d)", guild.name, guild.id)

        try:
            await db.guilds.delete_one({"guild_id": guild.id})
            logging.info("Cleaned up guild config for %s (ID: %d)", guild.name, guild.id)
        except Exception as e:
            logging.exception("Failed to clean up guild config for %s: %s", guild.id, e)

        self._auto_response_guilds.discard(guild.id)

    # =========================
    # ON MESSAGE - AUTO RESPONSES
    # =========================

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if message.guild:
            self._total_messages_processed += 1

            if message.guild.id in self._auto_response_guilds:
                content_lower = message.content.lower()
                if any(word in content_lower for word in ["klaus", "bot"]):
                    try:
                        await message.add_reaction("\U0001f49c")
                    except discord.HTTPException:
                        pass

                if content_lower.strip() in ["obrigado klaus", "obrigado bot", "valeu klaus", "valeu bot"]:
                    try:
                        await message.reply("De nada! \U0001f49c", mention_author=False)
                    except discord.HTTPException:
                        pass

        await self.process_commands(message)

    # =========================
    # ON APP COMMAND - TRACK USAGE
    # =========================

    async def on_app_command(
        self, interaction: discord.Interaction, command: app_commands.Command
    ) -> None:
        if interaction.user and not interaction.user.bot:
            self._total_commands_today += 1
            self._total_commands_executed += 1
            try:
                await db.add_command_use(interaction.user.id)

                cmd_name = command.qualified_name
                today_str = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
                await db._db["command_stats"].update_one(
                    {"date": today_str, "command": cmd_name},
                    {"$inc": {"count": 1}},
                    upsert=True,
                )

                await db._db["command_stats"].update_one(
                    {"date": today_str, "command": "_total"},
                    {"$inc": {"count": 1}},
                    upsert=True,
                )

                user_id = interaction.user.id
                await db._db["daily_user_commands"].update_one(
                    {"date": today_str, "user_id": user_id},
                    {"$inc": {"count": 1}, "$set": {"username": interaction.user.name}},
                    upsert=True,
                )

            except Exception as e:
                logging.exception("Failed to track command usage for %s: %s", command.qualified_name, e)

    # =========================
    # ON INTERACTION - EXISTING
    # =========================

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        if interaction.type == discord.InteractionType.application_command:
            if interaction.user and not interaction.user.bot:
                try:
                    avatar_key = interaction.user.avatar.key if interaction.user.avatar else ""
                    global_name = interaction.user.global_name or interaction.user.name
                    await db.update_username(interaction.user.id, interaction.user.name, avatar_key, global_name)
                except Exception as e:
                    logging.debug("Failed to update username: %s", e)

    # =========================
    # PRESENCE LOOP - ENHANCED
    # =========================

    @tasks.loop(seconds=30)
    async def presence_loop(self) -> None:
        try:
            guild_count = len(self.guilds)
            user_count = sum(g.member_count or 0 for g in self.guilds)
            elapsed = time.monotonic() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)

            giveaway_count = 0
            try:
                giveaway_count = await db.giveaways.count_documents({"ended": False})
            except Exception as e:
                logging.debug("Failed to count giveaways: %s", e)

            presences = [
                discord.Activity(type=discord.ActivityType.watching, name=f"{guild_count} servidores \u2022 /help"),
                discord.Activity(type=discord.ActivityType.listening, name=f"/daily para koins di\u00e1rios"),
                discord.Activity(type=discord.ActivityType.watching, name=f"{user_count} usu\u00e1rios ativos"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/apostar na roleta"),
                discord.Activity(type=discord.ActivityType.watching, name=f"{hours}h {minutes}m online"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/minerar ouro"),
                discord.Activity(type=discord.ActivityType.listening, name=f"/help para comandos"),
                discord.Activity(type=discord.ActivityType.watching, name=f"{guild_count} guilds \u2022 {user_count} users"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/perfil para ver progresso"),
                discord.Activity(type=discord.ActivityType.watching, name=f"/daily para koins"),
                discord.Activity(type=discord.ActivityType.listening, name=f"/help"),
                discord.Activity(type=discord.ActivityType.playing, name=f"{self._daily_commands} comandos hoje"),
                discord.Activity(type=discord.ActivityType.watching, name=f"{self._daily_koins:,} koins ganhos"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/giveaway para ganhar pr\u00eamios"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/trabalhar para ganhar koins"),
                discord.Activity(type=discord.ActivityType.listening, name=f"/crime para arriscar"),
                discord.Activity(type=discord.ActivityType.watching, name=f"/loja para comprar itens"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/pet para cuidar do seu"),
                discord.Activity(type=discord.ActivityType.watching, name=f"/rank para ver ranking"),
                discord.Activity(type=discord.ActivityType.listening, name=f"{giveaway_count} giveaways ativos"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/cofre para guardar koins"),
                discord.Activity(type=discord.ActivityType.watching, name=f"/investir para multiplicar"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/batalhar PvP"),
                discord.Activity(type=discord.ActivityType.playing, name=f"/caixa_fortuna"),
            ]

            weather_phrases = [
                "Hoje est\u00e1 ensolarado para minerar \u2600\ufe0f",
                "Tempo de apostar! \U0001f3b2",
                "Chovendo koins hoje! \U0001f327\ufe0f",
                "Neblina... cuidado ao trabalhar \U0001f32b\ufe0f",
                "Ventania de recompensas! \U0001f32a\ufe0f",
                "Tempestade de apostas! \u26c8\ufe0f",
                "Frio? Cozinhe no /crime \U0001f525",
                "Lua cheia = sorte no /apostar \U0001f315",
                "Quente! Aproveite /caixa_fortuna \U0001f321\ufe0f",
                "Noite estrelada para /aventura \u2b50",
            ]
            presences.append(discord.Activity(
                type=discord.ActivityType.playing,
                name=random.choice(weather_phrases),
            ))

            activity = random.choice(presences)
            await self.change_presence(activity=activity, status=discord.Status.online)
        except Exception as e:
            logging.exception("Error in presence_loop: %s", e)

    # =========================
    # STATS LOOP - EVERY 5 MINUTES
    # =========================

    @tasks.loop(minutes=5)
    async def stats_loop(self) -> None:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            today_str = now.date().isoformat()

            if self._last_stats_reset is None or self._last_stats_reset.date() < now.date():
                self._daily_commands = 0
                self._daily_koins = 0
                self._last_stats_reset = now

            await db._db["bot_stats"].update_one(
                {"date": today_str},
                {
                    "$set": {
                        "guild_count": len(self.guilds),
                        "user_count": sum(g.member_count or 0 for g in self.guilds),
                        "total_messages": self._total_messages_processed,
                        "total_commands": self._total_commands_executed,
                        "daily_commands": self._daily_commands,
                        "daily_koins": self._daily_koins,
                        "last_updated": now,
                    },
                    "$inc": {"updates": 1},
                },
                upsert=True,
            )

            try:
                pipeline = [
                    {"$group": {"_id": None, "total": {"$sum": "$koins"}}},
                ]
                result = await db.users.aggregate(pipeline).to_list(1)
                total_koins_in_economy = result[0]["total"] if result else 0
                await db._db["bot_stats"].update_one(
                    {"date": today_str},
                    {"$set": {"total_koins_in_economy": total_koins_in_economy}},
                    upsert=True,
                )
            except Exception as e:
                logging.debug("Failed to aggregate koins: %s", e)

            logging.debug("Stats loop updated for %s", today_str)

        except Exception as e:
            logging.exception("Error in stats_loop: %s", e)

    @stats_loop.before_loop
    async def before_stats_loop(self) -> None:
        await self.wait_until_ready()

    # =========================
    # GIVEAWAY LOOP - EVERY 30 SECONDS
    # =========================

    @tasks.loop(seconds=30)
    async def giveaway_loop(self) -> None:
        try:
            ended_giveaways = await db.get_active_giveaways()

            for giveaway in ended_giveaways:
                giveaway_id = giveaway.get("_id")
                channel_id = giveaway.get("channel_id")
                message_id = giveaway.get("message_id")
                prize = giveaway.get("prize", "Premio")
                host_id = giveaway.get("host_id")

                if not giveaway_id:
                    continue

                channel = self.get_channel(channel_id) if channel_id else None
                if not isinstance(channel, discord.TextChannel):
                    await db.end_giveaway(str(giveaway_id))
                    continue

                message = None
                if message_id:
                    try:
                        message = await channel.fetch_message(message_id)
                    except discord.HTTPException:
                        message = None

                winners = []
                if message:
                    reaction = discord.utils.get(message.reactions, emoji="\U0001f381")
                    if reaction:
                        users = [u async for u in reaction.users() if not u.bot]
                        if users:
                            winner = random.choice(users)
                            winners.append(winner)

                await db.end_giveaway(str(giveaway_id))

                if winners:
                    winner_mentions = ", ".join(w.mention for w in winners)
                    embed = discord.Embed(
                        title="\U0001f389 Giveaway Encerrado!",
                        description=(
                            f"**Premio:** {prize}\n"
                            f"**Vencedor(es):** {winner_mentions}\n\n"
                            f"Parabens! Voces ganharam o premio!"
                        ),
                        color=0xF59E0B,
                    )
                    embed.set_footer(text="Klaus Giveaways")
                    embed.timestamp = discord.utils.utcnow()

                    try:
                        await channel.send(content=winner_mentions, embed=embed)
                    except discord.HTTPException as e:
                        logging.error("Failed to announce giveaway winner in channel %s: %s", channel.name, e)

                    for winner in winners:
                        try:
                            dm_embed = discord.Embed(
                                title="\U0001f389 Parabens! Voce ganhou um giveaway!",
                                description=(
                                    f"**Servidor:** {channel.guild.name}\n"
                                    f"**Premio:** {prize}\n"
                                    f"**Canal:** {channel.mention}"
                                ),
                                color=0xF59E0B,
                            )
                            dm_embed.set_footer(text="Klaus Giveaways")
                            await winner.send(embed=dm_embed)
                        except discord.HTTPException:
                            logging.info("Could not DM giveaway winner %s", winner)
                else:
                    embed = discord.Embed(
                        title="\U0001f389 Giveaway Encerrado!",
                        description=f"**Premio:** {prize}\n\nNenhum participante valido. O premio nao foi distribuido.",
                        color=0xEF4444,
                    )
                    embed.set_footer(text="Klaus Giveaways")
                    embed.timestamp = discord.utils.utcnow()

                    try:
                        await channel.send(embed=embed)
                    except discord.HTTPException:
                        pass

                logging.info("Giveaway %s ended in channel %s", giveaway_id, channel.name if channel else "unknown")

        except Exception as e:
            logging.exception("Error in giveaway_loop: %s", e)

    @giveaway_loop.before_loop
    async def before_giveaway_loop(self) -> None:
        await self.wait_until_ready()

    # =========================
    # BROADCAST LOOP
    # =========================

    @tasks.loop(seconds=30)
    async def broadcast_loop(self) -> None:
        try:
            broadcasts = await db.get_pending_broadcasts()
            for bc in broadcasts:
                bc_id = bc.get("_id")
                message = bc.get("message", "")
                sent_by = bc.get("sent_by", 0)
                bc_channel = bc.get("broadcast_channel")

                if not message or not bc_id:
                    continue

                embed = discord.Embed(
                    title="\U0001f4e2 An\u00facio do Staff",
                    description=message,
                    color=0xF43F5E,
                )
                embed.set_footer(text=f"Enviado por ID: {sent_by}")

                sent_count = 0

                if bc_channel:
                    channel = self.get_channel(bc_channel)
                    if isinstance(channel, discord.TextChannel):
                        try:
                            await channel.send(embed=embed)
                            sent_count += 1
                        except discord.HTTPException:
                            logging.error("Failed to send broadcast %s to channel %s in guild %s", bc_id, channel.name, channel.guild.name)
                else:
                    for guild in self.guilds:
                        for ch in guild.text_channels:
                            if ch.permissions_for(guild.me).send_messages:
                                try:
                                    await ch.send(embed=embed)
                                    sent_count += 1
                                except discord.HTTPException:
                                    logging.error("Failed to send broadcast %s to channel %s in guild %s", bc_id, ch.name, guild.name)

                logging.info("Broadcast %s sent to %d channels", bc_id, sent_count)
                await db.mark_broadcast_sent(str(bc_id))
        except Exception as e:
            logging.exception("Error in broadcast loop: %s", e)

    # =========================
    # REMINDER LOOP
    # =========================

    @tasks.loop(seconds=30)
    async def reminder_loop(self) -> None:
        try:
            reminders = await db.get_pending_reminders()
            for reminder in reminders:
                reminder_id = reminder.get("_id")
                user_id = reminder.get("user_id")
                message = reminder.get("message", "")
                channel_id = reminder.get("channel_id")

                if not reminder_id or not user_id or not channel_id:
                    continue

                channel = self.get_channel(channel_id)
                if not isinstance(channel, discord.TextChannel):
                    continue

                try:
                    user = self.get_user(user_id)
                    if user:
                        await channel.send(f"{user.mention} {message}")
                    else:
                        await channel.send(message)
                    await db.mark_reminder_delivered(str(reminder_id))
                    logging.info("Reminder %s delivered to channel %s", reminder_id, channel.name)
                except discord.HTTPException:
                    logging.error("Failed to send reminder %s to channel %s in guild %s", reminder_id, channel.name, channel.guild.name)
        except Exception as e:
            logging.exception("Error in reminder loop: %s", e)

    # =========================
    # LEAVE QUEUE LOOP
    # =========================

    @tasks.loop(seconds=15)
    async def leave_queue_loop(self) -> None:
        try:
            col = db._db["leave_queue"]
            pending = await col.find({"status": "pending"}).to_list(50)
            for item in pending:
                guild_id = item.get("guild_id")
                item_id = item.get("_id")
                if not guild_id or not item_id:
                    continue
                guild = self.get_guild(guild_id)
                if guild:
                    try:
                        await guild.leave()
                        logging.info("Left guild: %s (%d)", guild.name, guild_id)
                    except Exception:
                        logging.exception("Failed to leave guild %d", guild_id)
                await col.update_one({"_id": item_id}, {"$set": {"status": "done"}})
        except Exception as e:
            logging.exception("Error in leave queue loop: %s", e)

    # =========================
    # ERROR HANDLERS
    # =========================

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        logging.exception("Unhandled command error in %s: %s", ctx.command, error, exc_info=error)

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            embed = make_embed.error("Sem Permiss\u00f5es", f"Voc\u00ea precisa de: **{', '.join(error.missing_permissions)}**")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            logging.exception("Unhandled app command error: %s", error, exc_info=error)
            try:
                embed = make_embed.error("Erro", "Ocorreu um erro inesperado!")
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                logging.debug("Failed to send error response: %s", e)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.bot:
            return True
        try:
            banned = await db.is_bot_banned(interaction.user.id)
            if banned:
                embed = make_embed.error("Banido", "Voce foi banido de usar o Klaus.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return False
        except Exception:
            pass
        return True

    # =========================
    # TASK LOOP ERROR RECOVERY
    # =========================

    def _setup_loop_recovery(self) -> None:
        for loop_attr_name in [
            "presence_loop",
            "broadcast_loop",
            "reminder_loop",
            "leave_queue_loop",
            "giveaway_loop",
            "stats_loop",
        ]:
            loop = getattr(self, loop_attr_name, None)
            if loop is None:
                continue

            original_loop_error = loop.error

            async def wrapped_error(task_loop, exc, _name=loop_attr_name, _original=original_loop_error):
                logging.error("Task loop '%s' failed with error: %s", _name, exc)
                if _original is not None:
                    await _original(task_loop, exc)
                logging.info("Waiting 30 seconds before restarting loop '%s'...", _name)
                await asyncio.sleep(30)
                if not task_loop.is_running():
                    task_loop.restart()
                    logging.info("Loop '%s' restarted successfully", _name)

            loop.error = wrapped_error


# =========================
# TERMINAL CONSOLE
# =========================

import subprocess

PROMPT = f"{C.LIGHTMAGENTA_EX}{BOLD}klaus{R} {DIM}\u2502{R} "


def _log(color: str, tag: str, msg: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    tag_str = f"{color}{BOLD}[{tag}]{R}"
    logging.info(f"{DIM}{ts}{R} {tag_str} {color}{msg}{R}")


def _log_ok(msg: str) -> None:
    _log(C.LIGHTGREEN_EX, " OK ", msg)


def _log_err(msg: str) -> None:
    _log(C.LIGHTRED_EX, "ERR ", msg)


def _log_info(msg: str) -> None:
    _log(C.LIGHTCYAN_EX, "INFO", msg)


def _log_warn(msg: str) -> None:
    _log(C.LIGHTYELLOW_EX, "WARN", msg)


def _print_table(rows: list[tuple[str, str]], title: str = "") -> None:
    w = 58
    if title:
        print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u250c\u2500 {title} {'\u2500' * (w - len(title) - 3)}\u2510{R}")
    for i, (label, value) in enumerate(rows):
        sep = "\u2502" if i < len(rows) - 1 else "\u2514"
        print(f"  {C.LIGHTMAGENTA_EX}\u2502{R}  {C.WHITE}{label:<12}{R} {DIM}\u2524{R} {value}  {C.LIGHTMAGENTA_EX}{sep}{R}")
    if not title:
        print(f"  {C.LIGHTMAGENTA_EX}\u2514{'\u2500' * (w + 1)}\u2518{R}")
    print()


def _print_box(title: str, lines: list[str], width: int = 58) -> None:
    print()
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u250c{'\u2500' * (width + 2)}\u2510{R}")
    pad = width - len(title)
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u2502{R}  {C.LIGHTMAGENTA_EX}{BOLD}{title}{R}{' ' * max(pad - 2, 1)}{C.LIGHTMAGENTA_EX}{BOLD}\u2502{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u251c{'\u2500' * (width + 2)}\u2524{R}")
    for line in lines:
        print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u2502{R}  {line}  {C.LIGHTMAGENTA_EX}{BOLD}\u2502{R}")
    print(f"  {C.LIGHTMAGENTA_EX}{BOLD}\u2514{'\u2500' * (width + 2)}\u2518{R}")
    print()


async def terminal_console(bot: "KlausBot") -> None:
    loop = asyncio.get_event_loop()
    _log_ok("Console pronto. Digite 'help' para ver os comandos.")
    print(f"  {DIM}Dica: Use Tab para completar, Ctrl+C para interromper{R}")
    print()

    while True:
        try:
            sys.stdout.write(PROMPT)
            sys.stdout.flush()
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            cmd_input = line.strip()
            if not cmd_input:
                continue

            parts = cmd_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "help":
                _print_box("KLAUS SYSTEM \u2014 COMANDOS", [
                    f"{C.LIGHTGREEN_EX}{BOLD}status{R}          {DIM}\u2502{R}  Status completo do bot",
                    f"{C.LIGHTGREEN_EX}{BOLD}guilds{R}          {DIM}\u2502{R}  Listar todos os servidores",
                    f"{C.LIGHTGREEN_EX}{BOLD}leave <id>{R}      {DIM}\u2502{R}  Sair de um servidor",
                    f"{C.LIGHTGREEN_EX}{BOLD}ban <id>{R}        {DIM}\u2502{R}  Banir usuario do bot",
                    f"{C.LIGHTGREEN_EX}{BOLD}unban <id>{R}      {DIM}\u2502{R}  Desbanir usuario do bot",
                    f"{C.LIGHTGREEN_EX}{BOLD}broadcast <msg>{R} {DIM}\u2502{R}  Enviar msg para todos servers",
                    f"{C.LIGHTGREEN_EX}{BOLD}reload <cog>{R}    {DIM}\u2502{R}  Recarregar um cog",
                    f"{C.LIGHTGREEN_EX}{BOLD}sync{R}            {DIM}\u2502{R}  Sincronizar slash commands",
                    f"{C.LIGHTGREEN_EX}{BOLD}eval <code>{R}     {DIM}\u2502{R}  Executar codigo Python",
                    f"{C.LIGHTGREEN_EX}{BOLD}cogs{R}            {DIM}\u2502{R}  Listar cogs carregados",
                    f"{C.LIGHTGREEN_EX}{BOLD}players{R}         {DIM}\u2502{R}  Jogadores ativos",
                    f"{C.LIGHTRED_EX}{BOLD}shutdown{R}        {DIM}\u2502{R}  Desligar o bot",
                    f"{C.LIGHTYELLOW_EX}{BOLD}restart{R}         {DIM}\u2502{R}  Reiniciar o bot",
                ])

            elif cmd == "status":
                elapsed = time.monotonic() - bot.start_time
                h = int(elapsed // 3600)
                m = int((elapsed % 3600) // 60)
                s = int(elapsed % 60)
                guild_count = len(bot.guilds)
                user_count = sum(g.member_count or 0 for g in bot.guilds)
                latency = round(bot.latency * 1000)
                lat_color = C.LIGHTGREEN_EX if latency < 150 else C.LIGHTYELLOW_EX if latency < 400 else C.LIGHTRED_EX
                lat_icon = "\u25cf" if latency < 150 else "\u25ac" if latency < 400 else "\u25cf"
                print()
                _print_box("STATUS DO BOT", [
                    f"{C.WHITE}Bot      {DIM}\u2524{R}  {C.LIGHTGREEN_EX}{bot.user}{R} {DIM}({bot.user.id}){R}",
                    f"{C.WHITE}Version  {DIM}\u2524{R}  {C.LIGHTMAGENTA_EX}3.0.0{R}",
                    f"{C.WHITE}Guilds   {DIM}\u2524{R}  {C.LIGHTGREEN_EX}{guild_count}{R}",
                    f"{C.WHITE}Users    {DIM}\u2524{R}  {C.LIGHTCYAN_EX}{user_count}{R}",
                    f"{C.WHITE}Cogs     {DIM}\u2524{R}  {C.LIGHTYELLOW_EX}{len(bot.extensions)}{R}",
                    f"{C.WHITE}Cmds     {DIM}\u2524{R}  {C.LIGHTMAGENTA_EX}{len(bot.tree.get_commands())}{R}",
                    f"{C.WHITE}Uptime   {DIM}\u2524{R}  {C.WHITE}{h}h {m}m {s}s{R}",
                    f"{C.WHITE}Latency  {DIM}\u2524{R}  {lat_color}{lat_icon} {latency}ms{R}",
                    f"{C.WHITE}MongoDB  {DIM}\u2524{R}  {C.LIGHTGREEN_EX}\u25cf Connected{R}",
                    f"{C.WHITE}Status   {DIM}\u2524{R}  {C.LIGHTGREEN_EX}{BOLD}\u25cf ONLINE{R}",
                ])

            elif cmd == "guilds":
                guilds = bot.guilds
                lines = []
                for i, g in enumerate(guilds, 1):
                    mc = g.member_count or 0
                    lines.append(f"{C.LIGHTGREEN_EX}{i:>2}.{R} {C.WHITE}{g.name}{R} {DIM}({g.id}){R} {C.LIGHTCYAN_EX}{mc} membros{R}")
                _print_box(f"SERVIDORES ({len(guilds)})", lines)

            elif cmd == "leave":
                if not arg:
                    _log_warn("Uso: leave <guild_id>")
                    continue
                try:
                    gid = int(arg)
                except ValueError:
                    _log_err("ID invalido.")
                    continue
                guild = bot.get_guild(gid)
                if not guild:
                    _log_err("Servidor nao encontrado.")
                    continue
                _log_info(f"Saindo de {C.WHITE}{guild.name}{R}...")
                await guild.leave()
                _log_ok(f"Saiu de {C.WHITE}{guild.name}{R} com sucesso!")

            elif cmd == "ban":
                if not arg:
                    _log_warn("Uso: ban <user_id>")
                    continue
                try:
                    uid = int(arg)
                except ValueError:
                    _log_err("ID invalido.")
                    continue
                await db.set_bot_banned(uid, True)
                _log_ok(f"Usuario {C.WHITE}{uid}{R} banido do bot.")

            elif cmd == "unban":
                if not arg:
                    _log_warn("Uso: unban <user_id>")
                    continue
                try:
                    uid = int(arg)
                except ValueError:
                    _log_err("ID invalido.")
                    continue
                await db.set_bot_banned(uid, False)
                _log_ok(f"Usuario {C.WHITE}{uid}{R} desbanido do bot.")

            elif cmd == "broadcast":
                if not arg:
                    _log_warn("Uso: broadcast <mensagem>")
                    continue
                await db.create_broadcast(arg, bot.user.id if bot.user else 0)
                _log_ok(f"Broadcast criado para {C.LIGHTGREEN_EX}{len(bot.guilds)}{R} servidores!")

            elif cmd == "reload":
                if not arg:
                    _log_warn("Uso: reload <cog_name>  (ex: cogs.economia)")
                    continue
                try:
                    await bot.reload_extension(arg)
                    _log_ok(f"Cog '{C.LIGHTGREEN_EX}{arg}{R}' recarregado!")
                except Exception as e:
                    _log_err(f"Falha ao recarregar: {e}")

            elif cmd == "sync":
                count = await bot.tree.sync()
                _log_ok(f"{C.LIGHTGREEN_EX}{len(count)}{R} comandos sincronizados.")

            elif cmd == "eval":
                if not arg:
                    _log_warn("Uso: eval <python_code>")
                    continue
                try:
                    result = eval(arg, {"bot": bot, "db": db})
                    if hasattr(result, "__await__"):
                        result = await result
                    _log_ok(f"Resultado: {C.WHITE}{result}{R}")
                except Exception as e:
                    _log_err(f"Erro: {C.LIGHTRED_EX}{e}{R}")

            elif cmd == "cogs":
                lines = []
                for name in sorted(bot.extensions.keys()):
                    lines.append(f"{C.LIGHTGREEN_EX}\u25cf{R} {C.WHITE}{name}{R}")
                _print_box(f"COGS CARREGADOS ({len(bot.extensions)})", lines)

            elif cmd == "players":
                lines = []
                for g in bot.guilds:
                    mc = g.member_count or 0
                    if mc > 0:
                        lines.append(f"{C.WHITE}{g.name}{R} {DIM}\u2502{R} {C.LIGHTCYAN_EX}{mc} membros{R}")
                if not lines:
                    lines.append(f"{DIM}Nenhum jogador encontrado.{R}")
                _print_box("JOGADORES ATIVOS", lines)

            elif cmd == "shutdown":
                _log_warn("Desligando o bot...")
                await bot.close()
                break

            elif cmd == "restart":
                _log_warn("Reiniciando o bot...")
                await bot.close()
                subprocess.Popen([sys.executable, "klaus.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
                break

            else:
                _log_err(f"Comando desconhecido: '{C.WHITE}{cmd}{R}'. Digite 'help'.")

        except (EOFError, KeyboardInterrupt):
            break
        except Exception as e:
            _log_err(f"Erro no console: {e}")


async def main() -> None:
    setup_logging()
    log = logging.getLogger("klaus.main")

    log.info("Connecting to MongoDB...")
    await db.connect()
    log.info("MongoDB connected")

    bot = KlausBot()
    bot._setup_loop_recovery()

    loop = asyncio.get_running_loop()

    def _handle_signal(sig: int) -> None:
        log.info("Received signal %s, shutting down...", signal.Signals(sig).name)
        asyncio.ensure_future(bot.close())

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_signal, sig)
        except NotImplementedError:
            pass

    try:
        await bot.start(settings.discord_token)
    except KeyboardInterrupt:
        log.info("Shutdown requested via keyboard")
    finally:
        log.info("Cleaning up...")
        await bot.close()
        await db.close()
        log.info("Bot shut down gracefully")


if __name__ == "__main__":
    asyncio.run(main())
