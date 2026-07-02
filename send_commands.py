import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import discord
from config import settings

logger = logging.getLogger(__name__)

CHANNEL_ID = 1521169991788138707

COMMANDS = [
    "/daily", "/weekly", "/streak", "/recompensa", "/trabalhar", "/minerar", "/forjar",
    "/loja", "/vender", "/saldo", "/carteira", "/perfil", "/ranking", "/conquistas",
    "/pagar", "/correio", "/doar", "/sobrevivencia",
    "/apostar", "/coinflip", "/aposta_dados", "/blackjack", "/slot", "/duel",
    "/batalhar", "/lottery", "/case",
    "/crime", "/roubar", "/heist", "/bounty", "/cofre", "/invest",
    "/challenges", "/caixa_fortuna",
    "/hug", "/kiss", "/slap", "/pat", "/ship", "/casal", "/coin", "/rps",
    "/batalha", "/piada", "/meme", "/8ball", "/roll", "/quiz", "/poll",
    "/reacao", "/adivinha", "/corrida", "/aventura", "/ranking_social",
    "/ban", "/kick", "/mute", "/unmute", "/warn", "/warnings", "/clearwarnings",
    "/slowmode_all", "/lock", "/unlock", "/clearchannel", "/nuke", "/modlog",
    "/ping", "/uptime", "/calcular", "/userinfo", "/serverinfo", "/embed",
    "/dashboard", "/help", "/rank", "/xpleaderboard",
    "/marry", "/divorce", "/comprar", "/afk", "/afk_off", "/pet_name", "/inventario",
    "/add_badword", "/ticket_panel", "/close_ticket", "/giveaway", "/reaction_role",
    "/reminder", "/pet", "/pet_feed", "/pet_play",
]


async def main():
    intents = discord.Intents.default()
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        logger.info("Logged in as %s", bot.user)

        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            logger.error("Channel %d not found!", CHANNEL_ID)
            await bot.close()
            return

        for cmd in COMMANDS:
            try:
                await channel.send(cmd)
                logger.info("Sent: %s", cmd)
            except discord.HTTPException as e:
                logger.error("Failed to send %s: %s", cmd, e)
            await asyncio.sleep(1)

        await channel.send(f"**Total: {len(COMMANDS)} comandos!**")
        logger.info("All commands sent!")
        await bot.close()

    await bot.start(settings.discord_token)


if __name__ == "__main__":
    asyncio.run(main())
