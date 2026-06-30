from __future__ import annotations

from typing import Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
import certifi
from config import settings


class Database:
    def __init__(self) -> None:
        self._client: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None
        self._users: AsyncIOMotorCollection | None = None
        self._warnings: AsyncIOMotorCollection | None = None
        self._guilds: AsyncIOMotorCollection | None = None
        self._users_xp: AsyncIOMotorCollection | None = None
        self.bounties: AsyncIOMotorCollection | None = None
        self.reminders: AsyncIOMotorCollection | None = None
        self.tickets: AsyncIOMotorCollection | None = None
        self.giveaways: AsyncIOMotorCollection | None = None
        self.reaction_roles: AsyncIOMotorCollection | None = None
        self._broadcasts: AsyncIOMotorCollection | None = None
        self._social_stats: AsyncIOMotorCollection | None = None
        self._command_stats: AsyncIOMotorCollection | None = None
        self._guild_stats: AsyncIOMotorCollection | None = None
        self._daily_stats: AsyncIOMotorCollection | None = None
        self._inventory: AsyncIOMotorCollection | None = None
        self._auctions: AsyncIOMotorCollection | None = None
        self._mod_logs: AsyncIOMotorCollection | None = None

    async def connect(self) -> None:
        if self._client is not None:
            return

        import asyncio, logging
        _log = logging.getLogger("klaus.db")

        self._client = AsyncIOMotorClient(
            settings.mongodb_url,
            tls=True,
            tlsCAFile=certifi.where(),
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=15000,
            connectTimeoutMS=20000,
            socketTimeoutMS=20000,
            retryWrites=True,
            retryReads=True,
        )
        self._db = self._client["economia"]
        self._users = self._db["usuarios"]
        self._warnings = self._db["warnings"]
        self._guilds = self._db["guilds"]
        self._users_xp = self._db["users_xp"]
        self.bounties = self._db["bounties"]
        self.reminders = self._db["reminders"]
        self.tickets = self._db["tickets"]
        self.giveaways = self._db["giveaways"]
        self.reaction_roles = self._db["reaction_roles"]
        self._broadcasts = self._db["broadcasts"]
        self._social_stats = self._db["social_stats"]
        self._command_stats = self._db["command_stats"]
        self._guild_stats = self._db["guild_stats"]
        self._daily_stats = self._db["daily_stats"]
        self._inventory = self._db["inventory"]
        self._auctions = self._db["auctions"]
        self._mod_logs = self._db["mod_logs"]

        await self._create_indexes()

        for attempt in range(1, 4):
            try:
                await self._client.admin.command("ping")
                _log.info("MongoDB connected (attempt %d)", attempt)
                return
            except Exception as exc:
                _log.warning("MongoDB connect attempt %d failed: %s", attempt, exc)
                if attempt < 3:
                    await asyncio.sleep(3 * attempt)
                else:
                    raise

    async def _create_indexes(self) -> None:
        if self._users is not None:
            await self._users.create_index([("discord_id", ASCENDING)], unique=True)
            await self._users.create_index([("koins", DESCENDING)])
        if self._warnings is not None:
            await self._warnings.create_index([("guild_id", ASCENDING), ("user_id", ASCENDING)])
        if self._users_xp is not None:
            await self._users_xp.create_index([("discord_id", ASCENDING), ("guild_id", ASCENDING)], unique=True)
            await self._users_xp.create_index([("guild_id", ASCENDING), ("xp", DESCENDING)])
        if self._social_stats is not None:
            await self._social_stats.create_index([("user_id", ASCENDING), ("guild_id", ASCENDING)], unique=True)
            await self._social_stats.create_index([("guild_id", ASCENDING), ("action", ASCENDING), ("count", DESCENDING)])
        if self._command_stats is not None:
            await self._command_stats.create_index([("command_name", ASCENDING)], unique=True)
            await self._command_stats.create_index([("count", DESCENDING)])
        if self._guild_stats is not None:
            await self._guild_stats.create_index([("guild_id", ASCENDING), ("stat_type", ASCENDING)], unique=True)
            await self._guild_stats.create_index([("guild_id", ASCENDING)])
        if self._daily_stats is not None:
            await self._daily_stats.create_index([("date", ASCENDING), ("stat_type", ASCENDING)], unique=True)
        if self._inventory is not None:
            await self._inventory.create_index([("user_id", ASCENDING), ("item_id", ASCENDING)], unique=True)
            await self._inventory.create_index([("user_id", ASCENDING)])
        if self._auctions is not None:
            await self._auctions.create_index([("auction_id", ASCENDING)])
            await self._auctions.create_index([("seller_id", ASCENDING)])
            await self._auctions.create_index([("active", ASCENDING)])
        if self._mod_logs is not None:
            await self._mod_logs.create_index([("guild_id", ASCENDING), ("created_at", DESCENDING)])

    async def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    async def health_check(self) -> bool:
        try:
            if self._client is None:
                return False
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    @property
    def users(self) -> AsyncIOMotorCollection:
        if self._users is None:
            raise RuntimeError("Database not connected.")
        return self._users

    @property
    def warnings_col(self) -> AsyncIOMotorCollection:
        if self._warnings is None:
            raise RuntimeError("Database not connected.")
        return self._warnings

    @property
    def guilds(self) -> AsyncIOMotorCollection:
        if self._guilds is None:
            raise RuntimeError("Database not connected.")
        return self._guilds

    @property
    def broadcasts(self) -> AsyncIOMotorCollection:
        if self._broadcasts is None:
            raise RuntimeError("Database not connected.")
        return self._broadcasts

    @property
    def social_stats(self) -> AsyncIOMotorCollection:
        if self._social_stats is None:
            raise RuntimeError("Database not connected.")
        return self._social_stats

    @property
    def command_stats_col(self) -> AsyncIOMotorCollection:
        if self._command_stats is None:
            raise RuntimeError("Database not connected.")
        return self._command_stats

    @property
    def guild_stats_col(self) -> AsyncIOMotorCollection:
        if self._guild_stats is None:
            raise RuntimeError("Database not connected.")
        return self._guild_stats

    @property
    def daily_stats_col(self) -> AsyncIOMotorCollection:
        if self._daily_stats is None:
            raise RuntimeError("Database not connected.")
        return self._daily_stats

    @property
    def inventory_col(self) -> AsyncIOMotorCollection:
        if self._inventory is None:
            raise RuntimeError("Database not connected.")
        return self._inventory

    @property
    def auctions_col(self) -> AsyncIOMotorCollection:
        if self._auctions is None:
            raise RuntimeError("Database not connected.")
        return self._auctions

    @property
    def mod_logs_col(self) -> AsyncIOMotorCollection:
        if self._mod_logs is None:
            raise RuntimeError("Database not connected.")
        return self._mod_logs

    # =========================
    # USER
    # =========================

    async def create_user(self, user_id: int, username: str = "") -> dict[str, Any]:
        doc = await self.users.find_one({"discord_id": user_id})
        if doc is not None:
            if username and doc.get("username") != username:
                await self.users.update_one({"discord_id": user_id}, {"$set": {"username": username}})
                doc["username"] = username
            return doc

        new_user = {
            "discord_id": user_id,
            "username": username,
            "koins": settings.starting_koins,
            "wins": 0,
            "losses": 0,
            "profit": 0,
            "easy_wins": 0,
            "big_losses": 0,
            "daily_streak": 0,
            "last_daily": None,
            "total_earned": 0,
            "total_lost": 0,
            "commands_used": 0,
            "mines": 0,
            "bets": 0,
            "robs": 0,
            "achievements": [],
        }
        await self.users.insert_one(new_user)
        return new_user

    async def get_user(self, user_id: int, username: str = "") -> dict[str, Any]:
        doc = await self.users.find_one({"discord_id": user_id})
        if doc is None:
            return await self.create_user(user_id, username)
        if username and doc.get("username") != username:
            await self.users.update_one({"discord_id": user_id}, {"$set": {"username": username}})
            doc["username"] = username
        return doc

    async def update_username(self, user_id: int, username: str, avatar: str = "", global_name: str = "") -> None:
        update: dict = {"username": username}
        if avatar:
            update["avatar"] = avatar
        if global_name:
            update["global_name"] = global_name
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": update},
            upsert=True,
        )

    # =========================
    # PROFILE SYSTEM
    # =========================

    async def get_profile(self, user_id: int) -> dict:
        user = await self.get_user(user_id)
        return {
            "background": user.get("profile_background", "padrao"),
            "border": user.get("profile_border", "default"),
            "purchased_bg": user.get("purchased_backgrounds", ["padrao"]),
            "purchased_border": user.get("purchased_borders", ["default"]),
            "custom_bg_url": user.get("custom_bg_url", ""),
            "has_custom_bg": user.get("has_custom_bg", False),
        }

    async def set_profile_background(self, user_id: int, bg: str) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"profile_background": bg}},
            upsert=True,
        )

    async def set_profile_border(self, user_id: int, border: str) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"profile_border": border}},
            upsert=True,
        )

    async def buy_profile_item(self, user_id: int, item_type: str, item_id: str, price: int) -> bool:
        user = await self.get_user(user_id)
        koins = user.get("koins", 0)
        if koins < price:
            return False

        field = f"purchased_{item_type}"
        purchased = user.get(field, [])
        if item_id in purchased:
            return False

        await self.users.update_one(
            {"discord_id": user_id},
            {
                "$inc": {"koins": -price},
                "$push": {field: item_id},
            },
            upsert=True,
        )
        return True

    async def save_profile_image(self, user_id: int, image_b64: str) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"profile_image_b64": image_b64}},
            upsert=True,
        )

    async def get_profile_image(self, user_id: int) -> str | None:
        user = await self.get_user(user_id)
        return user.get("profile_image_b64")

    async def get_balance(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return user.get("koins", 0)

    async def add_koins(self, user_id: int, amount: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"koins": amount, "total_earned": max(0, amount)}},
            upsert=True,
        )

    async def remove_koins(self, user_id: int, amount: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"koins": -amount, "total_lost": max(0, amount)}},
            upsert=True,
        )

    async def set_balance(self, user_id: int, amount: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"koins": amount}},
            upsert=True,
        )

    async def add_command_use(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"commands_used": 1}},
            upsert=True,
        )

    # =========================
    # STATS
    # =========================

    async def get_stats(self, user_id: int) -> dict[str, int]:
        user = await self.get_user(user_id)
        return {
            "wins": user.get("wins", 0),
            "losses": user.get("losses", 0),
            "profit": user.get("profit", 0),
            "easy_wins": user.get("easy_wins", 0),
            "big_losses": user.get("big_losses", 0),
            "daily_streak": user.get("daily_streak", 0),
            "total_earned": user.get("total_earned", 0),
            "total_lost": user.get("total_lost", 0),
            "commands_used": user.get("commands_used", 0),
            "mines": user.get("mines", 0),
            "bets": user.get("bets", 0),
            "robs": user.get("robs", 0),
        }

    async def add_win(self, user_id: int, profit: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"wins": 1, "profit": profit, "easy_wins": 1, "bets": 1}},
            upsert=True,
        )

    async def add_loss(self, user_id: int, loss: int) -> None:
        user = await self.get_user(user_id)
        update: dict[str, Any] = {
            "$inc": {"losses": 1, "profit": -loss, "bets": 1}
        }
        if loss >= 15000:
            update["$inc"]["big_losses"] = 1
            update["$set"] = {"easy_wins": 0}
        await self.users.update_one({"discord_id": user_id}, update, upsert=True)

    async def add_mine(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id}, {"$inc": {"mines": 1}}, upsert=True
        )

    async def add_rob(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id}, {"$inc": {"robs": 1}}, upsert=True
        )

    async def reset_greed(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id}, {"$set": {"easy_wins": 0}}, upsert=True
        )

    # =========================
    # STREAK
    # =========================

    async def update_streak(self, user_id: int, premium: bool = False) -> dict[str, Any]:
        import datetime
        user = await self.get_user(user_id)
        now = datetime.datetime.now(datetime.timezone.utc)
        last = user.get("last_daily")

        streak = user.get("daily_streak", 0)
        window = 86400 * 3 if premium else 86400 * 2
        if last:
            last_dt = last if isinstance(last, datetime.datetime) else datetime.datetime.fromisoformat(str(last))
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=datetime.timezone.utc)
            diff = now - last_dt
            if diff.total_seconds() < window:
                streak += 1
            else:
                streak = 1
        else:
            streak = 1

        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"daily_streak": streak, "last_daily": now}},
            upsert=True,
        )
        return {"streak": streak, "is_new": streak == 1}

    async def get_streak(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return user.get("daily_streak", 0)

    # =========================
    # ACHIEVEMENTS
    # =========================

    async def add_achievement(self, user_id: int, achievement: str) -> bool:
        user = await self.get_user(user_id)
        if achievement in user.get("achievements", []):
            return False
        await self.users.update_one(
            {"discord_id": user_id},
            {"$addToSet": {"achievements": achievement}},
            upsert=True,
        )
        return True

    async def get_achievements(self, user_id: int) -> list[str]:
        user = await self.get_user(user_id)
        return user.get("achievements", [])

    # =========================
    # WARNINGS
    # =========================

    async def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        doc = {
            "guild_id": guild_id,
            "user_id": user_id,
            "moderator_id": moderator_id,
            "reason": reason,
        }
        await self.warnings_col.insert_one(doc)
        count = await self.warnings_col.count_documents({"guild_id": guild_id, "user_id": user_id})
        return count

    async def get_warnings(self, guild_id: int, user_id: int) -> list[dict]:
        cursor = self.warnings_col.find({"guild_id": guild_id, "user_id": user_id})
        return [doc async for doc in cursor]

    async def clear_warnings(self, guild_id: int, user_id: int) -> int:
        result = await self.warnings_col.delete_many({"guild_id": guild_id, "user_id": user_id})
        return result.deleted_count

    # =========================
    # GUILD CONFIG
    # =========================

    async def get_guild_config(self, guild_id: int) -> dict[str, Any]:
        doc = await self.guilds.find_one({"guild_id": guild_id})
        if doc is None:
            return {}
        return doc

    async def set_guild_config(self, guild_id: int, **kwargs) -> None:
        await self.guilds.update_one(
            {"guild_id": guild_id},
            {"$set": kwargs},
            upsert=True,
        )

    # =========================
    # LEADERBOARD
    # =========================

    async def get_top_rich(self, limit: int = 10) -> list[dict[str, Any]]:
        cursor = self.users.find().sort("koins", DESCENDING).limit(limit)
        return [
            {"discord_id": doc["discord_id"], "koins": doc.get("koins", 0)}
            async for doc in cursor
        ]

    async def get_leaderboard_page(self, page: int = 1, per_page: int = 10) -> dict[str, Any]:
        total = await self.users.count_documents({})
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        skip = (page - 1) * per_page

        cursor = self.users.find().sort("koins", DESCENDING).skip(skip).limit(per_page)
        entries = [
            {"rank": skip + i + 1, "discord_id": doc["discord_id"], "koins": doc.get("koins", 0)}
            for i, doc in enumerate(await cursor.to_list(length=per_page))
        ]
        return {"entries": entries, "page": page, "total_pages": total_pages, "total": total}

    async def get_user_rank(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        koins = user.get("koins", 0)
        count = await self.users.count_documents({"koins": {"$gt": koins}})
        return count + 1

    # =========================
    # XP SYSTEM
    # =========================

    async def add_xp(self, user_id: int, guild_id: int, amount: int) -> dict[str, Any]:
        key = {"discord_id": user_id, "guild_id": guild_id}
        doc = await self._users_xp.find_one(key)
        if doc is None:
            doc = {"discord_id": user_id, "guild_id": guild_id, "xp": 0, "level": 0, "messages": 0}
            await self._users_xp.insert_one(doc)

        new_xp = doc.get("xp", 0) + amount
        old_level = doc.get("level", 0)
        new_level = self._calc_level(new_xp)
        leveled_up = new_level > old_level

        await self._users_xp.update_one(
            key,
            {"$set": {"xp": new_xp, "level": new_level}, "$inc": {"messages": 1}},
            upsert=True,
        )
        return {"xp": new_xp, "level": new_level, "leveled_up": leveled_up, "old_level": old_level}

    async def get_xp(self, user_id: int, guild_id: int) -> dict[str, Any]:
        key = {"discord_id": user_id, "guild_id": guild_id}
        doc = await self._users_xp.find_one(key)
        if doc is None:
            return {"xp": 0, "level": 0, "messages": 0}
        return {"xp": doc.get("xp", 0), "level": doc.get("level", 0), "messages": doc.get("messages", 0)}

    async def get_xp_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict[str, Any]]:
        cursor = self._users_xp.find({"guild_id": guild_id}).sort("xp", DESCENDING).limit(limit)
        return [
            {"rank": i + 1, "discord_id": doc["discord_id"], "xp": doc.get("xp", 0), "level": doc.get("level", 0)}
            for i, doc in enumerate(await cursor.to_list(length=limit))
        ]

    async def get_xp_rank(self, user_id: int, guild_id: int) -> int:
        doc = await self._users_xp.find_one({"discord_id": user_id, "guild_id": guild_id})
        if doc is None:
            total = await self._users_xp.count_documents({"guild_id": guild_id})
            return total + 1
        xp = doc.get("xp", 0)
        count = await self._users_xp.count_documents({"guild_id": guild_id, "xp": {"$gt": xp}})
        return count + 1

    @staticmethod
    def _calc_level(xp: int) -> int:
        level = 0
        while True:
            needed = 5 * (level ** 2) + 50 * level + 100
            if xp < needed:
                break
            xp -= needed
            level += 1
        return level

    @staticmethod
    def _xp_for_level(level: int) -> int:
        return 5 * (level ** 2) + 50 * level + 100

    @staticmethod
    def _xp_bar(current_xp: int, level: int, length: int = 20) -> str:
        needed = Database._xp_for_level(level)
        progress = min(current_xp, needed)
        filled = int((progress / needed) * length) if needed > 0 else 0
        return "\u2588" * filled + "\u25a1" * (length - filled)

    # =========================
    # COFRE (SAVINGS)
    # =========================

    async def get_cofre(self, user_id: int) -> dict[str, Any]:
        user = await self.get_user(user_id)
        return {
            "balance": user.get("cofre_balance", 0),
            "last_deposit": user.get("cofre_last_deposit"),
            "total_deposited": user.get("cofre_total_deposited", 0),
            "interest_earned": user.get("cofre_interest_earned", 0),
        }

    async def deposit_cofre(self, user_id: int, amount: int) -> dict[str, Any]:
        import datetime
        balance = await self.get_balance(user_id)
        if balance < amount:
            return {"ok": False, "error": "Saldo insuficiente"}

        await self.remove_koins(user_id, amount)
        await self.users.update_one(
            {"discord_id": user_id},
            {
                "$inc": {"cofre_balance": amount, "cofre_total_deposited": amount},
                "$set": {"cofre_last_deposit": datetime.datetime.now(datetime.timezone.utc)},
            },
            upsert=True,
        )
        new_cofre = await self.get_cofre(user_id)
        return {"ok": True, "cofre": new_cofre}

    async def withdraw_cofre(self, user_id: int, amount: int) -> dict[str, Any]:
        cofre = await self.get_cofre(user_id)
        if cofre["balance"] < amount:
            return {"ok": False, "error": "Saldo insuficiente no cofre"}

        await self.add_koins(user_id, amount)
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"cofre_balance": -amount}},
            upsert=True,
        )
        new_cofre = await self.get_cofre(user_id)
        return {"ok": True, "cofre": new_cofre}

    async def collect_interest(self, user_id: int, rate: float = 0.02) -> int:
        cofre = await self.get_cofre(user_id)
        interest = int(cofre["balance"] * rate)
        if interest <= 0:
            return 0
        await self.users.update_one(
            {"discord_id": user_id},
            {"$inc": {"cofre_balance": interest, "cofre_interest_earned": interest}},
            upsert=True,
        )
        return interest

    # =========================
    # CRIME
    # =========================

    async def add_crime(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id}, {"$inc": {"crimes": 1}}, upsert=True
        )

    async def get_crimes(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return user.get("crimes", 0)

    async def add_jail(self, user_id: int, minutes: int) -> None:
        import datetime
        release = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"jail_until": release, "in_jail": True}},
            upsert=True,
        )

    async def is_in_jail(self, user_id: int) -> dict[str, Any]:
        import datetime
        user = await self.get_user(user_id)
        jail_until = user.get("jail_until")
        if not jail_until:
            return {"jailed": False}
        if isinstance(jail_until, str):
            jail_until = datetime.datetime.fromisoformat(jail_until)
        if datetime.datetime.now(datetime.timezone.utc) > jail_until:
            await self.users.update_one(
                {"discord_id": user_id},
                {"$set": {"in_jail": False}, "$unset": {"jail_until": ""}},
                upsert=True,
            )
            return {"jailed": False}
        remaining = (jail_until - datetime.datetime.now(datetime.timezone.utc)).seconds
        return {"jailed": True, "remaining_seconds": remaining}

    # =========================
    # LOTTERY
    # =========================

    async def buy_lottery_ticket(self, user_id: int, price: int) -> dict[str, Any]:
        import datetime, random
        balance = await self.get_balance(user_id)
        if balance < price:
            return {"ok": False, "error": "Saldo insuficiente"}

        await self.remove_koins(user_id, price)
        number = random.randint(1, 100)
        await self.users.update_one(
            {"discord_id": user_id},
            {
                "$inc": {"lottery_tickets": 1},
                "$push": {"lottery_numbers": {"number": number, "date": datetime.datetime.now(datetime.timezone.utc), "won": False}},
            },
            upsert=True,
        )
        return {"ok": True, "number": number}

    async def draw_lottery(self, pool: int) -> dict[str, Any]:
        import random
        winning = random.randint(1, 100)
        cursor = self.users.find({"lottery_numbers": {"$elemMatch": {"number": winning, "won": False}}})
        winners = []
        async for doc in cursor:
            winners.append(doc["discord_id"])
            await self.users.update_one(
                {"discord_id": doc["discord_id"]},
                {"$set": {"lottery_numbers.$[elem].won": True}},
                array_filters=[{"elem.number": winning, "elem.won": False}],
            )
        return {"winning_number": winning, "winners": winners, "pool": pool}

    async def get_lottery_pool(self) -> int:
        total = 0
        async for doc in self.users.find({"lottery_numbers": {"$exists": True}}):
            total += len(doc.get("lottery_numbers", []))
        return total * 500

    # =========================
    # PET SYSTEM
    # =========================

    async def get_pet(self, user_id: int) -> dict[str, Any] | None:
        user = await self.get_user(user_id)
        return user.get("pet")

    async def create_pet(self, user_id: int, name: str, pet_type: str) -> dict[str, Any]:
        import datetime
        pet = {
            "name": name,
            "type": pet_type,
            "level": 1,
            "xp": 0,
            "hunger": 100,
            "happiness": 100,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "last_fed": datetime.datetime.now(datetime.timezone.utc),
            "total_fed": 0,
            "total_played": 0,
        }
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"pet": pet}},
            upsert=True,
        )
        return pet

    async def update_pet(self, user_id: int, **kwargs) -> None:
        update = {}
        for k, v in kwargs.items():
            update[f"pet.{k}"] = v
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": update},
            upsert=True,
        )

    async def feed_pet(self, user_id: int) -> dict[str, Any]:
        import datetime
        pet = await self.get_pet(user_id)
        if not pet:
            return {"ok": False, "error": "Você não tem um pet!"}

        new_hunger = min(100, pet["hunger"] + 30)
        new_happiness = min(100, pet["happiness"] + 10)
        new_xp = pet["xp"] + 5
        new_level = pet["level"]
        if new_xp >= new_level * 50:
            new_xp = 0
            new_level += 1

        await self.update_pet(
            user_id,
            hunger=new_hunger,
            happiness=new_happiness,
            xp=new_xp,
            level=new_level,
            last_fed=datetime.datetime.now(datetime.timezone.utc),
            total_fed=pet.get("total_fed", 0) + 1,
        )
        return {"ok": True, "hunger": new_hunger, "happiness": new_happiness, "leveled_up": new_level > pet["level"]}

    async def play_pet(self, user_id: int) -> dict[str, Any]:
        pet = await self.get_pet(user_id)
        if not pet:
            return {"ok": False, "error": "Você não tem um pet!"}

        new_happiness = min(100, pet["happiness"] + 25)
        new_hunger = max(0, pet["hunger"] - 10)
        new_xp = pet["xp"] + 3
        new_level = pet["level"]
        if new_xp >= new_level * 50:
            new_xp = 0
            new_level += 1

        await self.update_pet(
            user_id,
            happiness=new_happiness,
            hunger=new_hunger,
            xp=new_xp,
            level=new_level,
            total_played=pet.get("total_played", 0) + 1,
        )
        return {"ok": True, "happiness": new_happiness, "hunger": new_hunger, "leveled_up": new_level > pet["level"]}

    # =========================
    # GACHA / CASE
    # =========================

    async def open_case(self, user_id: int, price: int) -> dict[str, Any]:
        import random
        balance = await self.get_balance(user_id)
        if balance < price:
            return {"ok": False, "error": "Saldo insuficiente"}

        await self.remove_koins(user_id, price)

        drops = [
            ("common", "\U0001f4a1 Comum", 50, 1.0),
            ("uncommon", "\U0001f7e2 Incomum", 30, 1.5),
            ("rare", "\U0001f535 Raro", 15, 2.0),
            ("epic", "\U0001f7e3 Epico", 4, 3.0),
            ("legendary", "\U0001f48e Lendario", 1, 5.0),
        ]

        roll = random.random() * 100
        cumulative = 0
        chosen = drops[0]
        for rarity, name, chance, mult in drops:
            cumulative += chance
            if roll <= cumulative:
                chosen = (rarity, name, chance, mult)
                break

        prize = int(price * chosen[3])
        await db.add_koins(user_id, prize)

        return {
            "ok": True,
            "rarity": chosen[0],
            "name": chosen[1],
            "prize": prize,
            "multiplier": chosen[3],
        }

    # =========================
    # HEIST SYSTEM
    # =========================

    async def add_heist(self, user_id: int) -> None:
        await self.users.update_one(
            {"discord_id": user_id}, {"$inc": {"heists": 1}}, upsert=True
        )

    async def get_heists(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return user.get("heists", 0)

    # =========================
    # BOUNTY SYSTEM
    # =========================

    async def place_bounty(self, target_id: int, placer_id: int, amount: int) -> dict[str, Any]:
        import datetime
        balance = await self.get_balance(placer_id)
        if balance < amount:
            return {"ok": False, "error": "Saldo insuficiente"}

        await self.remove_koins(placer_id, amount)
        await self.bounties.insert_one({
            "target_id": target_id,
            "placer_id": placer_id,
            "amount": amount,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "claimed": False,
        })
        return {"ok": True}

    async def get_bounties(self, target_id: int) -> list[dict]:
        cursor = self.bounties.find({"target_id": target_id, "claimed": False})
        return [doc async for doc in cursor]

    async def claim_bounty(self, target_id: int, claimer_id: int) -> dict[str, Any]:
        bounty = await self.bounties.find_one({"target_id": target_id, "claimed": False})
        if not bounty:
            return {"ok": False, "error": "Sem bounty disponível"}
        if bounty["placer_id"] == claimer_id:
            return {"ok": False, "error": "Não pode claim seu próprio bounty"}

        await self.add_koins(claimer_id, bounty["amount"])
        await self.bounties.update_one({"_id": bounty["_id"]}, {"$set": {"claimed": True, "claimer_id": claimer_id}})
        return {"ok": True, "amount": bounty["amount"]}

    # =========================
    # INVESTMENT SYSTEM
    # =========================

    async def invest(self, user_id: int, inv_type: str, amount: int) -> dict[str, Any]:
        import datetime
        balance = await self.get_balance(user_id)
        if balance < amount:
            return {"ok": False, "error": "Saldo insuficiente"}

        await self.remove_koins(user_id, amount)
        investment = {
            "type": inv_type,
            "amount": amount,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "status": "active",
        }
        await self.users.update_one(
            {"discord_id": user_id},
            {"$push": {"investments": investment}},
            upsert=True,
        )
        return {"ok": True}

    async def get_investments(self, user_id: int) -> list[dict]:
        user = await self.get_user(user_id)
        return user.get("investments", [])

    async def collect_investment(self, user_id: int, index: int) -> dict[str, Any]:
        import random
        user = await self.get_user(user_id)
        investments = user.get("investments", [])
        if index >= len(investments):
            return {"ok": False, "error": "Investimento não encontrado"}

        inv = investments[index]
        if inv["status"] != "active":
            return {"ok": False, "error": "Investimento já coletado"}

        from config import settings as cfg
        inv_data = cfg.investment_types.get(inv["type"], {})
        risk = inv_data.get("risk", 0.3)
        max_return = inv_data.get("max_return", 0.2)

        if random.random() < risk:
            loss = int(inv["amount"] * random.uniform(0.1, 0.5))
            await self.add_koins(user_id, inv["amount"] - loss)
            await self.users.update_one(
                {"discord_id": user_id},
                {"$set": {f"investments.{index}.status": "lost"}},
            )
            return {"ok": True, "won": False, "loss": loss, "returned": inv["amount"] - loss}
        else:
            gain = int(inv["amount"] * random.uniform(0.05, max_return))
            await self.add_koins(user_id, inv["amount"] + gain)
            await self.users.update_one(
                {"discord_id": user_id},
                {"$set": {f"investments.{index}.status": "won"}},
            )
            return {"ok": True, "won": True, "gain": gain, "returned": inv["amount"] + gain}

    # =========================
    # DAILY CHALLENGES
    # =========================

    async def get_daily_challenges(self, user_id: int) -> dict[str, Any]:
        import datetime
        user = await self.get_user(user_id)
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        last = user.get("challenges_date")

        if last == today:
            return {
                "challenges": user.get("daily_challenges", []),
                "progress": user.get("challenge_progress", {}),
                "completed": user.get("challenges_completed", []),
                "date": today,
            }

        from config import settings as cfg
        import random
        available = cfg.daily_challenges.copy()
        random.shuffle(available)
        selected = available[:3]

        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {
                "daily_challenges": selected,
                "challenge_progress": {},
                "challenges_completed": [],
                "challenges_date": today,
            }},
            upsert=True,
        )
        return {"challenges": selected, "progress": {}, "completed": [], "date": today}

    async def update_challenge_progress(self, user_id: int, challenge_type: str, amount: int = 1) -> list[str]:
        import datetime
        challenges = await self.get_daily_challenges(user_id)
        progress = challenges["progress"]
        completed = challenges["completed"]
        newly_completed = []

        for i, ch in enumerate(challenges["challenges"]):
            if ch["type"] == challenge_type and str(i) not in completed:
                current = progress.get(str(i), 0) + amount
                progress[str(i)] = current
                if current >= ch["target"]:
                    completed.append(str(i))
                    newly_completed.append(ch)

        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"challenge_progress": progress, "challenges_completed": completed}},
            upsert=True,
        )
        return newly_completed

    # =========================
    # LUCKY WHEEL
    # =========================

    async def spin_lucky_wheel(self, user_id: int) -> dict[str, Any]:
        import random
        from config import settings as cfg
        reward = random.choice(cfg.lucky_wheel_rewards)
        await self.add_koins(user_id, reward)
        return {"ok": True, "reward": reward}

    # =========================
    # AFK SYSTEM
    # =========================

    async def set_afk(self, user_id: int, reason: str = "") -> None:
        import datetime
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {
                "afk": True,
                "afk_reason": reason,
                "afk_since": datetime.datetime.now(datetime.timezone.utc),
            }},
            upsert=True,
        )

    async def remove_afk(self, user_id: int) -> dict[str, Any]:
        user = await self.get_user(user_id)
        was_afk = user.get("afk", False)
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"afk": False}, "$unset": {"afk_reason": "", "afk_since": ""}},
            upsert=True,
        )
        return {"was_afk": was_afk, "reason": user.get("afk_reason", "")}

    async def is_afk(self, user_id: int) -> dict[str, Any]:
        user = await self.get_user(user_id)
        return {
            "afk": user.get("afk", False),
            "reason": user.get("afk_reason", ""),
            "since": user.get("afk_since"),
        }

    # =========================
    # REMINDER SYSTEM
    # =========================

    async def add_reminder(self, user_id: int, channel_id: int, text: str, remind_at) -> None:
        import datetime
        await self.reminders.insert_one({
            "user_id": user_id,
            "channel_id": channel_id,
            "text": text,
            "remind_at": remind_at,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "delivered": False,
        })

    async def get_pending_reminders(self) -> list[dict]:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        cursor = self.reminders.find({"delivered": False, "remind_at": {"$lte": now}})
        return [doc async for doc in cursor]

    async def mark_reminder_delivered(self, reminder_id) -> None:
        from bson import ObjectId
        await self.reminders.update_one({"_id": ObjectId(reminder_id)}, {"$set": {"delivered": True}})

    # =========================
    # TICKET SYSTEM
    # =========================

    async def create_ticket(self, guild_id: int, user_id: int, channel_id: int, category: str) -> dict:
        import datetime
        ticket = {
            "guild_id": guild_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "category": category,
            "status": "open",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "messages": [],
        }
        result = await self.tickets.insert_one(ticket)
        ticket["_id"] = result.inserted_id
        return ticket

    async def close_ticket(self, channel_id: int) -> dict | None:
        ticket = await self.tickets.find_one({"channel_id": channel_id, "status": "open"})
        if ticket:
            await self.tickets.update_one({"_id": ticket["_id"]}, {"$set": {"status": "closed"}})
            return ticket
        return None

    async def get_user_tickets(self, user_id: int, guild_id: int) -> list[dict]:
        cursor = self.tickets.find({"user_id": user_id, "guild_id": guild_id, "status": "open"})
        return [doc async for doc in cursor]

    # =========================
    # GIVEAWAY SYSTEM
    # =========================

    async def create_giveaway(self, channel_id: int, message_id: int, prize: str, host_id: int, duration: int) -> None:
        import datetime, discord
        end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=duration)
        await self.giveaways.insert_one({
            "channel_id": channel_id,
            "message_id": message_id,
            "prize": prize,
            "host_id": host_id,
            "end_time": end_time,
            "ended": False,
            "winner_id": None,
        })

    async def get_active_giveaways(self) -> list[dict]:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        cursor = self.giveaways.find({"ended": False, "end_time": {"$lte": now}})
        return [doc async for doc in cursor]

    async def end_giveaway(self, giveaway_id) -> dict | None:
        from bson import ObjectId
        doc = await self.giveaways.find_one({"_id": ObjectId(giveaway_id)})
        if doc:
            await self.giveaways.update_one({"_id": ObjectId(giveaway_id)}, {"$set": {"ended": True}})
            return doc
        return None

    # =========================
    # REACTION ROLES
    # =========================

    async def add_reaction_role(self, message_id: int, emoji: str, role_id: int, guild_id: int) -> None:
        await self.reaction_roles.update_one(
            {"message_id": message_id, "emoji": emoji},
            {"$set": {"role_id": role_id, "guild_id": guild_id}},
            upsert=True,
        )

    async def get_reaction_role(self, message_id: int, emoji: str) -> dict | None:
        return await self.reaction_roles.find_one({"message_id": message_id, "emoji": emoji})

    async def remove_reaction_role(self, message_id: int, emoji: str) -> None:
        await self.reaction_roles.delete_one({"message_id": message_id, "emoji": emoji})

    # =========================
    # PREMIUM
    # =========================

    async def is_premium(self, user_id: int) -> bool:
        doc = await self.users.find_one({"discord_id": user_id})
        return bool(doc and doc.get("premium", False))

    # =========================
    # BROADCAST
    # =========================

    async def create_broadcast(self, message: str, sent_by: int, broadcast_channel: int | None = None) -> str:
        import datetime
        doc = {
            "message": message,
            "sent_by": sent_by,
            "broadcast_channel": broadcast_channel,
            "pending": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        result = await self.broadcasts.insert_one(doc)
        return str(result.inserted_id)

    async def get_pending_broadcasts(self) -> list[dict[str, Any]]:
        cursor = self.broadcasts.find({"pending": True})
        return await cursor.to_list(length=50)

    async def mark_broadcast_sent(self, broadcast_id: str) -> None:
        from bson import ObjectId
        await self.broadcasts.update_one(
            {"_id": ObjectId(broadcast_id)},
            {"$set": {"pending": False}},
        )

    async def get_broadcast_history(self, limit: int = 20) -> list[dict[str, Any]]:
        cursor = self.broadcasts.find().sort("created_at", DESCENDING).limit(limit)
        results = []
        async for doc in cursor:
            results.append({
                "id": str(doc.get("_id", "")),
                "message": doc.get("message", ""),
                "sent_by": doc.get("sent_by", 0),
                "broadcast_channel": doc.get("broadcast_channel"),
                "pending": doc.get("pending", False),
                "created_at": str(doc.get("created_at", "")),
            })
        return results

    # =========================
    # ADMIN / UTILITIES
    # =========================

    async def get_guild_count(self) -> int:
        if self._users_xp is None:
            return 0
        guilds = await self._users_xp.distinct("guild_id")
        return len(guilds)

    async def get_total_users(self) -> int:
        return await self.users.count_documents({})

    async def get_richest_user(self) -> dict[str, Any]:
        doc = await self.users.find_one(sort=[("koins", DESCENDING)])
        if not doc:
            return {}
        return {"discord_id": doc.get("discord_id", 0), "koins": doc.get("koins", 0), "username": doc.get("username", "")}

    async def get_achievements_count(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        return len(user.get("achievements", []))

    async def get_investment_total(self, user_id: int) -> int:
        user = await self.get_user(user_id)
        investments = user.get("investments", [])
        return sum(inv.get("amount", 0) for inv in investments if inv.get("status") == "active")

    async def update_premium(self, user_id: int, premium: bool) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"premium": premium}},
            upsert=True,
        )

    async def set_bot_banned(self, user_id: int, banned: bool) -> None:
        await self.users.update_one(
            {"discord_id": user_id},
            {"$set": {"bot_banned": banned}},
            upsert=True,
        )

    async def is_bot_banned(self, user_id: int) -> bool:
        doc = await self.users.find_one({"discord_id": user_id})
        return bool(doc and doc.get("bot_banned", False))

    # =========================
    # SOCIAL TRACKING
    # =========================

    async def add_social_action(self, user_id: int, action: str) -> None:
        await self.social_stats.update_one(
            {"user_id": user_id, "action": action},
            {"$inc": {"count": 1}, "$set": {"user_id": user_id, "action": action}},
            upsert=True,
        )

    async def get_social_stats(self, user_id: int) -> dict:
        cursor = self.social_stats.find({"user_id": user_id})
        stats = {}
        async for doc in cursor:
            stats[doc["action"]] = doc.get("count", 0)
        return stats

    async def get_social_leaderboard(self, guild_id: int, action: str, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$match": {"action": action}},
            {"$group": {"_id": "$user_id", "count": {"$sum": "$count"}}},
            {"$sort": {"count": DESCENDING}},
            {"$limit": limit},
        ]
        cursor = self.social_stats.aggregate(pipeline)
        results = []
        rank = 0
        async for doc in cursor:
            rank += 1
            results.append({"rank": rank, "user_id": doc["_id"], "count": doc["count"]})
        return results

    # =========================
    # COMMAND STATISTICS
    # =========================

    async def add_command_stat(self, command_name: str) -> None:
        await self.command_stats_col.update_one(
            {"command_name": command_name},
            {"$inc": {"count": 1}, "$set": {"command_name": command_name}},
            upsert=True,
        )

    async def get_command_stats(self) -> dict:
        cursor = self.command_stats_col.find()
        stats = {}
        async for doc in cursor:
            stats[doc["command_name"]] = doc.get("count", 0)
        return stats

    async def get_most_used_commands(self, limit: int = 10) -> list[dict]:
        cursor = self.command_stats_col.find().sort("count", DESCENDING).limit(limit)
        results = []
        rank = 0
        async for doc in cursor:
            rank += 1
            results.append({"rank": rank, "command": doc["command_name"], "count": doc.get("count", 0)})
        return results

    # =========================
    # GUILD STATISTICS
    # =========================

    async def add_guild_stat(self, guild_id: int, stat_type: str, value: int = 1) -> None:
        await self.guild_stats_col.update_one(
            {"guild_id": guild_id, "stat_type": stat_type},
            {"$inc": {"value": value}, "$set": {"guild_id": guild_id, "stat_type": stat_type}},
            upsert=True,
        )

    async def get_guild_stats(self, guild_id: int) -> dict:
        cursor = self.guild_stats_col.find({"guild_id": guild_id})
        stats = {}
        async for doc in cursor:
            stats[doc["stat_type"]] = doc.get("value", 0)
        return stats

    async def get_guild_leaderboard(self, guild_id: int, limit: int = 10) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$guild_id", "total": {"$sum": "$value"}}},
            {"$sort": {"total": DESCENDING}},
            {"$limit": limit},
        ]
        cursor = self.guild_stats_col.aggregate(pipeline)
        results = []
        rank = 0
        async for doc in cursor:
            rank += 1
            results.append({"rank": rank, "guild_id": doc["_id"], "total": doc["total"]})
        return results

    # =========================
    # DAILY STATISTICS
    # =========================

    async def add_daily_stat(self, stat_type: str, value: int = 1) -> None:
        import datetime
        today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        await self.daily_stats_col.update_one(
            {"date": today, "stat_type": stat_type},
            {"$inc": {"value": value}, "$set": {"date": today, "stat_type": stat_type}},
            upsert=True,
        )

    async def get_daily_stats(self, date: str = None) -> dict:
        import datetime
        if date is None:
            date = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
        cursor = self.daily_stats_col.find({"date": date})
        stats = {}
        async for doc in cursor:
            stats[doc["stat_type"]] = doc.get("value", 0)
        return stats

    async def get_weekly_stats(self) -> dict:
        import datetime
        today = datetime.datetime.now(datetime.timezone.utc).date()
        week_ago = (today - datetime.timedelta(days=7)).isoformat()
        cursor = self.daily_stats_col.find({"date": {"$gte": week_ago}})
        stats = {}
        async for doc in cursor:
            stat_type = doc["stat_type"]
            if stat_type not in stats:
                stats[stat_type] = {}
            stats[stat_type][doc["date"]] = doc.get("value", 0)
        return stats

    # =========================
    # INVENTORY
    # =========================

    async def add_inventory_item(self, user_id: int, item_id: str, quantity: int = 1) -> None:
        await self.inventory_col.update_one(
            {"user_id": user_id, "item_id": item_id},
            {"$inc": {"quantity": quantity}, "$set": {"user_id": user_id, "item_id": item_id}},
            upsert=True,
        )

    async def remove_inventory_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        doc = await self.inventory_col.find_one({"user_id": user_id, "item_id": item_id})
        if not doc or doc.get("quantity", 0) < quantity:
            return False
        new_qty = doc["quantity"] - quantity
        if new_qty <= 0:
            await self.inventory_col.delete_one({"user_id": user_id, "item_id": item_id})
        else:
            await self.inventory_col.update_one(
                {"user_id": user_id, "item_id": item_id},
                {"$set": {"quantity": new_qty}},
            )
        return True

    async def get_inventory(self, user_id: int) -> dict:
        cursor = self.inventory_col.find({"user_id": user_id})
        items = {}
        async for doc in cursor:
            items[doc["item_id"]] = doc.get("quantity", 0)
        return items

    async def has_item(self, user_id: int, item_id: str) -> bool:
        doc = await self.inventory_col.find_one({"user_id": user_id, "item_id": item_id})
        return bool(doc and doc.get("quantity", 0) > 0)

    # =========================
    # AUCTION SYSTEM
    # =========================

    async def create_auction(self, seller_id: int, item: str, price: int) -> str:
        import datetime, uuid
        auction_id = str(uuid.uuid4())[:8]
        await self.auctions_col.insert_one({
            "auction_id": auction_id,
            "seller_id": seller_id,
            "item": item,
            "price": price,
            "active": True,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        })
        return auction_id

    async def get_auctions(self) -> list[dict]:
        cursor = self.auctions_col.find({"active": True}).sort("created_at", DESCENDING)
        results = []
        async for doc in cursor:
            results.append({
                "auction_id": doc["auction_id"],
                "seller_id": doc["seller_id"],
                "item": doc["item"],
                "price": doc.get("price", 0),
                "created_at": str(doc.get("created_at", "")),
            })
        return results

    async def buy_auction(self, auction_id: str, buyer_id: int) -> bool:
        import datetime
        doc = await self.auctions_col.find_one({"auction_id": auction_id, "active": True})
        if not doc:
            return False
        if doc["seller_id"] == buyer_id:
            return False
        balance = await self.get_balance(buyer_id)
        if balance < doc.get("price", 0):
            return False
        await self.remove_koins(buyer_id, doc["price"])
        await self.add_koins(doc["seller_id"], doc["price"])
        await self.auctions_col.update_one(
            {"auction_id": auction_id},
            {"$set": {"active": False, "buyer_id": buyer_id, "sold_at": datetime.datetime.now(datetime.timezone.utc)}},
        )
        return True

    # =========================
    # MOD LOGGING
    # =========================

    async def add_mod_log(self, guild_id: int, moderator_id: int, target_id: int, action: str, reason: str) -> None:
        import datetime
        await self.mod_logs_col.insert_one({
            "guild_id": guild_id,
            "moderator_id": moderator_id,
            "target_id": target_id,
            "action": action,
            "reason": reason,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        })

    async def get_mod_logs(self, guild_id: int, limit: int = 20) -> list[dict]:
        cursor = self.mod_logs_col.find({"guild_id": guild_id}).sort("created_at", DESCENDING).limit(limit)
        results = []
        async for doc in cursor:
            results.append({
                "moderator_id": doc.get("moderator_id", 0),
                "target_id": doc.get("target_id", 0),
                "action": doc.get("action", ""),
                "reason": doc.get("reason", ""),
                "created_at": str(doc.get("created_at", "")),
            })
        return results


db = Database()