from __future__ import annotations

import discord
from datetime import datetime


KLAUS_PRIMARY = 0x8B5CF6
KLAUS_PINK = 0xD946EF
KLAUS_DARK = 0x2C1A4E
KLAUS_GOLD = 0xF59E0B
KLAUS_CYAN = 0x06B6D4
KLAUS_GREEN = 0x22C55E
KLAUS_RED = 0xEF4444
KLAUS_BLUE = 0x3B82F6
KLAUS_ORANGE = 0xF97316
KLAUS_ROSE = 0xF43F5E
KLAUS_VIOLET = 0x7C3AED
KLAUS_MAGENTA = 0xE040FB
KLAUS_LIME = 0x84CC16
KLAUS_CYAN_LIGHT = 0x22D3EE
KLAUS_ORANGE_LIGHT = 0xFB923C
KLAUS_PINK_LIGHT = 0xF472B6


class KlausEmbed:
    _colors = {
        "success": 0x22C55E,
        "error": 0xEF4444,
        "warning": 0xF59E0B,
        "info": 0x8B5CF6,
        "purple": 0x8B5CF6,
        "pink": 0xD946EF,
        "gold": 0xF59E0B,
        "dark": 0x2C1A4E,
        "orange": 0xF97316,
        "teal": 0x14B8A6,
        "red": 0xEF4444,
        "blue": 0x3B82F6,
        "cyan": 0x06B6D4,
        "rose": 0xF43F5E,
        "klaus": 0x8B5CF6,
        "violet": 0x7C3AED,
        "magenta": 0xE040FB,
        "lime": 0x84CC16,
        "cyan_light": 0x22D3EE,
        "orange_light": 0xFB923C,
        "pink_light": 0xF472B6,
    }

    def __init__(self, color: int | str = "info") -> None:
        if isinstance(color, str):
            self._color = self._colors.get(color, self._colors["info"])
        else:
            self._color = color
        self._embed = discord.Embed(color=self._color)

    def title(self, t: str) -> KlausEmbed:
        self._embed.title = t
        return self

    def desc(self, d: str | None) -> KlausEmbed:
        self._embed.description = d
        return self

    def field(self, name: str, value: str, inline: bool = False) -> KlausEmbed:
        self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def fields(self, *items: tuple[str, str, bool]) -> KlausEmbed:
        for item in items:
            name, value = item[0], item[1]
            inline = item[2] if len(item) > 2 else False
            self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def inline_field(self, name: str, value: str) -> KlausEmbed:
        self._embed.add_field(name=name, value=value, inline=True)
        return self

    def block_field(self, name: str, value: str) -> KlausEmbed:
        self._embed.add_field(name=name, value=value, inline=False)
        return self

    def thumb(self, url: str) -> KlausEmbed:
        self._embed.set_thumbnail(url=url)
        return self

    def image(self, url: str) -> KlausEmbed:
        self._embed.set_image(url=url)
        return self

    def footer(self, text: str, icon: str | None = None) -> KlausEmbed:
        self._embed.set_footer(text=text, icon_url=icon)
        return self

    def timestamp(self, dt: datetime | None = None) -> KlausEmbed:
        self._embed.timestamp = dt or discord.utils.utcnow()
        return self

    def author(self, name: str, icon: str | None = None, url: str | None = None) -> KlausEmbed:
        self._embed.set_author(name=name, icon_url=icon, url=url)
        return self

    def color(self, c: int | str) -> KlausEmbed:
        if isinstance(c, str):
            self._color = self._colors.get(c, self._colors["info"])
        else:
            self._color = c
        self._embed.color = self._color
        return self

    def build(self) -> discord.Embed:
        return self._embed

    @staticmethod
    def success(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("success")
            .title(f"\u2705 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Bot"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def error(title: str, desc: str) -> discord.Embed:
        return (
            KlausEmbed("error")
            .title(f"\u274c {title}")
            .desc(desc)
            .timestamp()
            .footer("Klaus Bot")
            .build()
        )

    @staticmethod
    def warn(title: str, desc: str) -> discord.Embed:
        return (
            KlausEmbed("warning")
            .title(f"\u26a0\ufe0f {title}")
            .desc(desc)
            .timestamp()
            .footer("Klaus Bot")
            .build()
        )

    @staticmethod
    def info(title: str, desc: str) -> discord.Embed:
        return (
            KlausEmbed("info")
            .title(f"\U0001f49c {title}")
            .desc(desc)
            .timestamp()
            .footer("Klaus Bot")
            .build()
        )

    @staticmethod
    def profile(user: discord.Member, **fields) -> discord.Embed:
        embed = (
            KlausEmbed(user.color if user.color != discord.Color.default() else "purple")
            .title(f"\U0001f464 {user.display_name}")
            .desc(f"Perfil completo de **{user.display_name}**")
            .thumb(user.display_avatar.url)
            .timestamp()
            .footer(f"Klaus Profile \u2022 ID: {user.id}")
        )
        for name, value in fields.items():
            embed.field(name, str(value))
        return embed.build()

    @staticmethod
    def economy(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("gold")
            .title(f"\U0001f4b0 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Economy"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def casino(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("pink")
            .title(f"\U0001f3b0 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Casino"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def premium(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("gold")
            .title(f"\U0001f451 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Premium"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def mod(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("rose")
            .title(f"\U0001f6e1\ufe0f {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Moderation"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def levelup(user: discord.Member, level: int) -> discord.Embed:
        return (
            KlausEmbed("purple")
            .title("\U0001f3c6 Level Up!")
            .desc(f"{user.mention} subiu para o **Level {level}**!")
            .thumb(user.display_avatar.url)
            .footer("Klaus XP System")
            .timestamp()
            .build()
        )

    @staticmethod
    def progress_bar(label: str, current: int, maximum: int, color: int | str = "info") -> discord.Embed:
        ratio = max(0.0, min(1.0, current / maximum)) if maximum else 0.0
        filled = round(ratio * 20)
        empty = 20 - filled
        bar = "\u2588" * filled + "\u2591" * empty
        pct = ratio * 100
        return (
            KlausEmbed(color)
            .title(f"\U0001f4ca {label}")
            .desc(f"`{bar}` **{pct:.1f}%**\n`{current:,}` / `{'{:,}'.format(maximum)}`")
            .timestamp()
            .footer("Klaus Progress")
            .build()
        )

    @staticmethod
    def countdown(title: str, end_time: datetime, **kwargs) -> discord.Embed:
        remaining = end_time - discord.utils.utcnow()
        seconds = int(max(remaining.total_seconds(), 0))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        time_str = " ".join(parts)
        return (
            KlausEmbed(kwargs.get("color", "violet"))
            .title(f"\u23f3 {title}")
            .desc(f"Termina em **{time_str}**\n<t:{int(end_time.timestamp())}:R>")
            .timestamp(end_time)
            .footer(kwargs.get("footer", "Klaus Countdown"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def leaderboard(title: str, entries: list[dict], color: int | str = "gold") -> discord.Embed:
        medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
        lines = []
        for i, entry in enumerate(entries[:10]):
            prefix = medals[i] if i < 3 else f"`#{i + 1}`"
            name = entry.get("name", f"User #{i + 1}")
            value = entry.get("value", 0)
            lines.append(f"{prefix} **{name}** \u2014 `{value:,}`")
        embed = (
            KlausEmbed(color)
            .title(f"\U0001f3c6 {title}")
            .desc("\n".join(lines) if lines else "Nenhuma entrada.")
            .timestamp()
            .footer(f"Top {min(len(entries), 10)} \u2022 Klaus Leaderboard")
            .build()
        )
        if icon := entries[0].get("icon"):
            embed.set_thumbnail(url=icon)
        return embed

    @staticmethod
    def shop(title: str, items: list[dict], **kwargs) -> discord.Embed:
        lines = []
        for item in items[:15]:
            name = item.get("name", "Item")
            price = item.get("price", 0)
            desc = item.get("desc", "")
            emoji = item.get("emoji", "\U0001f4e6")
            line = f"{emoji} **{name}** \u2014 \U0001f4b0 `{price:,}`"
            if desc:
                line += f"\n    {desc}"
            lines.append(line)
        return (
            KlausEmbed(kwargs.get("color", "purple"))
            .title(f"\U0001f6d2 {title}")
            .desc("\n\n".join(lines) if lines else "Nenhum item dispon\u00edvel.")
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Shop"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def giveaway(title: str, prize: str, end_time: datetime, host: discord.Member, **kwargs) -> discord.Embed:
        remaining = end_time - discord.utils.utcnow()
        seconds = int(max(remaining.total_seconds(), 0))
        days, rem = divmod(seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, secs = divmod(rem, 60)
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        time_str = " ".join(parts)
        return (
            KlausEmbed(kwargs.get("color", "gold"))
            .title(f"\U0001f381 {title}")
            .desc(
                f"**Pr\u00eamio:** {prize}\n"
                f"**Host:** {host.mention}\n"
                f"**Termina em:** {time_str} (<t:{int(end_time.timestamp())}:R>)\n"
                f"\nReaja com \U0001f381 para participar!"
            )
            .thumb(host.display_avatar.url)
            .timestamp(end_time)
            .footer(kwargs.get("footer", "Klaus Giveaways"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def ticket(title: str, user: discord.Member, **kwargs) -> discord.Embed:
        channel_id = kwargs.get("channel_id", "N/A")
        return (
            KlausEmbed(kwargs.get("color", "cyan"))
            .title(f"\U0001f4ab {title}")
            .desc(
                f"**Usu\u00e1rio:** {user.mention}\n"
                f"**Canal:** <#{channel_id}>\n"
                f"**Status:** {kwargs.get('status', '\u23f3 Aberto')}"
            )
            .thumb(user.display_avatar.url)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Tickets"), kwargs.get("icon"))
            .build()
        )

    @staticmethod
    def battle(
        player1: discord.Member,
        player2: discord.Member,
        *,
        p1_hp: int = 100,
        p2_hp: int = 100,
        p1_max_hp: int = 100,
        p2_max_hp: int = 100,
        p1_level: int = 1,
        p2_level: int = 1,
        winner: discord.Member | None = None,
        color: int | str = "rose",
    ) -> discord.Embed:
        def _bar(current: int, maximum: int, length: int = 10) -> str:
            ratio = max(0.0, min(1.0, current / maximum)) if maximum else 0.0
            filled = round(ratio * length)
            return "\u2588" * filled + "\u2591" * (length - filled)

        p1_bar = _bar(p1_hp, p1_max_hp)
        p2_bar = _bar(p2_hp, p2_max_hp)

        p1_status = f"\u274f {p1_hp}/{p1_max_hp}"
        p2_status = f"\u274f {p2_hp}/{p2_max_hp}"

        desc_lines = [
            f"**{player1.display_name}** (Lv.{p1_level})",
            f"`{p1_bar}` {p1_status}",
            "",
            "\u2694\ufe0f  **VS**  \u2694\ufe0f",
            "",
            f"**{player2.display_name}** (Lv.{p2_level})",
            f"`{p2_bar}` {p2_status}",
        ]

        if winner:
            desc_lines.append("")
            desc_lines.append(f"\U0001f3c6 **Vencedor: {winner.display_name}!**")

        embed = (
            KlausEmbed(color)
            .title("\u2694\ufe0f Batalha PvP")
            .desc("\n".join(desc_lines))
            .timestamp()
            .footer("Klaus Battle")
        )
        embed._embed.set_thumbnail(url=player1.display_avatar.url)
        if winner:
            embed._embed.set_image(url=winner.display_avatar.url)
        return embed.build()

    @staticmethod
    def adventure(
        scene: str,
        *,
        description: str = "",
        choices: list[str] | None = None,
        reward: str | None = None,
        loss: str | None = None,
        color: int | str = "teal",
        bg_url: str | None = None,
    ) -> discord.Embed:
        desc_parts = [f"*{scene}*"]
        if description:
            desc_parts.append(f"\n{description}")

        if choices:
            desc_parts.append("\n\u25b6 **Escolhas:**")
            for i, choice in enumerate(choices, 1):
                desc_parts.append(f"  {i}\u20e3 {choice}")

        if reward:
            desc_parts.append(f"\n\U0001f381 **Recompensa:** {reward}")
        if loss:
            desc_parts.append(f"\n\U0001f4a5 **Perda:** {loss}")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f30d {scene}")
            .desc("\n".join(desc_parts))
            .timestamp()
            .footer("Klaus Adventure")
        )
        if bg_url:
            embed.image(bg_url)
        return embed.build()

    @staticmethod
    def quiz(
        question: str,
        *,
        options: list[str] | None = None,
        correct_index: int = 0,
        timer_seconds: int = 30,
        score: int = 0,
        streak: int = 0,
        color: int | str = "cyan",
    ) -> discord.Embed:
        option_emojis = ["1\u20e3", "2\u20e3", "3\u20e3", "4\u20e3"]
        desc_parts = [f"**{question}**\n"]

        if options:
            desc_parts.append("**Op\u00e7\u00f5es:**")
            for i, opt in enumerate(options[:4]):
                emoji = option_emojis[i] if i < len(option_emojis) else f"{i+1}."
                desc_parts.append(f"  {emoji} {opt}")

        minutes, secs = divmod(timer_seconds, 60)
        timer_str = f"{minutes}:{secs:02d}" if minutes else f"{secs}s"
        desc_parts.append(f"\n\u23f1\ufe0f Tempo: **{timer_str}**")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f9e0 Quiz")
            .desc("\n".join(desc_parts))
            .timestamp()
            .footer(f"Score: {score} \u2022 Streak: {streak} \u2022 Klaus Quiz")
        )
        return embed.build()

    @staticmethod
    def poll(
        question: str,
        *,
        options: list[dict] | None = None,
        time_remaining: str | None = None,
        total_votes: int = 0,
        color: int | str = "blue",
    ) -> discord.Embed:
        bar_emojis = ["\U0001f534", "\U0001f7e1", "\U0001f7e2", "\U0001f535", "\U0001f7e3"]
        desc_parts = [f"**{question}**\n"]

        if options:
            max_votes = max((o.get("votes", 0) for o in options), default=1) or 1
            for i, opt in enumerate(options):
                name = opt.get("name", f"Op\u00e7\u00e3o {i+1}")
                votes = opt.get("votes", 0)
                pct = (votes / total_votes * 100) if total_votes else 0
                bar_len = round((votes / max_votes) * 10) if max_votes else 0
                bar = "\u2588" * bar_len + "\u2591" * (10 - bar_len)
                emoji = bar_emojis[i % len(bar_emojis)]
                desc_parts.append(f"{emoji} **{name}**")
                desc_parts.append(f"  `{bar}` **{votes}** votos ({pct:.1f}%)")
                desc_parts.append("")

        desc_parts.append(f"\U0001f4ca **Total:** {total_votes} votos")
        if time_remaining:
            desc_parts.append(f"\u23f3 **Restante:** {time_remaining}")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f4cb {question}")
            .desc("\n".join(desc_parts))
            .timestamp()
            .footer("Klaus Polls \u2022 Reaja com n\u00famero para votar")
        )
        return embed.build()

    @staticmethod
    def inventory(
        user: discord.Member,
        *,
        items: list[dict] | None = None,
        total_value: int = 0,
        color: int | str = "gold",
    ) -> discord.Embed:
        desc_parts = []

        if items:
            for item in items[:20]:
                emoji = item.get("emoji", "\U0001f4e6")
                name = item.get("name", "Item")
                qty = item.get("qty", 1)
                value = item.get("value", 0)
                desc_parts.append(f"{emoji} **{name}** x{qty} \u2014 \U0001f4b0 `{value:,}`")
        else:
            desc_parts.append("*Invent\u00e1rio vazio.*")

        desc_parts.append(f"\n\U0001f4b0 **Valor Total:** `{total_value:,}`")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f392 Invent\u00e1rio \u2022 {user.display_name}")
            .desc("\n".join(desc_parts))
            .thumb(user.display_avatar.url)
            .timestamp()
            .footer(f"{len(items or [])} tipos de item \u2022 Klaus Inventory")
        )
        return embed.build()

    @staticmethod
    def achievement_unlocked(
        user: discord.Member,
        achievement_name: str,
        *,
        emoji: str = "\U0001f3c6",
        description: str = "",
        unlocked_at: datetime | None = None,
        color: int | str = "gold",
    ) -> discord.Embed:
        ts = unlocked_at or discord.utils.utcnow()
        desc_parts = [
            f"{emoji} **{achievement_name}** desbloqueado!",
        ]
        if description:
            desc_parts.append(f"\n{description}")
        desc_parts.append(f"\n\U0001f552 Desbloqueado em: <t:{int(ts.timestamp())}:F>")
        desc_parts.append(f"\n\U0001f389 Parab\u00e9ns, {user.mention}!")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f3c6 Conquista Desbloqueada!")
            .desc("\n".join(desc_parts))
            .thumb(user.display_avatar.url)
            .timestamp(ts)
            .footer("Klaus Achievements")
        )
        return embed.build()

    @staticmethod
    def daily_reward(
        user: discord.Member,
        *,
        day: int = 1,
        streak: int = 1,
        base_reward: int = 100,
        bonus: int = 0,
        streak_multiplier: float = 1.0,
        total_claimed: int = 0,
        next_reward: int | None = None,
        color: int | str = "orange",
    ) -> discord.Embed:
        fire = "\U0001f525" * min(streak // 7, 5) if streak > 0 else ""
        streak_text = f"**Streak:** {streak} dias {fire}" if streak > 0 else "**Streak:** 0 dias"

        calendar_days = []
        for i in range(1, 8):
            if i < day:
                calendar_days.append(f"\u2705 {i}")
            elif i == day:
                calendar_days.append(f"\U0001f525 **{i}** (hoje)")
            else:
                calendar_days.append(f"\u2b1c {i}")
        calendar_lines = " \u2002 ".join(calendar_days)

        desc_parts = [
            streak_text,
            f"\n{calendar_lines}\n",
            f"\U0001f4b0 **Recompensa Base:** `{base_reward:,}` moedas",
        ]
        if streak_multiplier > 1.0:
            desc_parts.append(f"\U0001f4a8 **B\u00f4nus de Streak:** x{streak_multiplier}")
        if bonus:
            desc_parts.append(f"\U0001f381 **B\u00f4nus Extra:** `{bonus:,}` moedas")
        desc_parts.append(f"\n**Total Hoje:** `{total_claimed:,}` moedas")
        if next_reward:
            desc_parts.append(f"\U0001f514 **Pr\u00f3xima recompensa:** `{next_reward:,}` moedas")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f4c5 Recompensa Di\u00e1ria \u2022 Dia {day}")
            .desc("\n".join(desc_parts))
            .thumb(user.display_avatar.url)
            .timestamp()
            .footer("Klaus Daily Rewards")
        )
        return embed.build()

    @staticmethod
    def shop_item(
        name: str,
        *,
        emoji: str = "\U0001f4e6",
        price: int = 0,
        original_price: int | None = None,
        description: str = "",
        stock: int | None = None,
        color: int | str = "purple",
    ) -> discord.Embed:
        if original_price and original_price > price:
            price_display = f"~~`{original_price:,}`~~ \u2192 **`{price:,}`** \U0001f4b0"
            discount = round((1 - price / original_price) * 100)
        else:
            price_display = f"**`{price:,}`** \U0001f4b0"
            discount = 0

        desc_parts = [f"{emoji} **{name}**\n"]
        desc_parts.append(f"\U0001f4b0 **Pre\u00e7o:** {price_display}")
        if discount:
            desc_parts.append(f"\U0001f381 **Desconto:** {discount}% OFF")
        if description:
            desc_parts.append(f"\n{description}")
        if stock is not None:
            desc_parts.append(f"\n\U0001f4e6 **Estoque:** {stock} dispon\u00edveis")
        desc_parts.append("\n\u2705 Clique no bot\u00e3o para comprar!")

        embed = (
            KlausEmbed(color)
            .title(f"\U0001f6d2 {name}")
            .desc("\n".join(desc_parts))
            .timestamp()
            .footer("Klaus Shop \u2022 Compre com o bot\u00e3o abaixo")
        )
        return embed.build()

    @staticmethod
    def loading(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed(kwargs.get("color", "dark"))
            .title(f"\u23f3 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus System \u2022 Aguarde..."))
            .build()
        )

    @staticmethod
    def progress(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed(kwargs.get("color", "purple"))
            .title(f"\u25b6 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus System \u2022 Processando..."))
            .build()
        )

    @staticmethod
    def result(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed(kwargs.get("color", "info"))
            .title(title)
            .desc(desc)
            .thumb(kwargs.get("thumb"))
            .image(kwargs.get("image"))
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Bot"))
            .build()
        )

    @staticmethod
    def game(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed(kwargs.get("color", "purple"))
            .title(f"\U0001f3ae {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Games"))
            .build()
        )

    @staticmethod
    def confirm(title: str, desc: str, **kwargs) -> discord.Embed:
        return (
            KlausEmbed("warning")
            .title(f"\u2753 {title}")
            .desc(desc)
            .timestamp()
            .footer(kwargs.get("footer", "Klaus Confirm"))
            .build()
        )

    @classmethod
    def rich_embed(cls, color: int | str = "info") -> "RichEmbedBuilder":
        return RichEmbedBuilder(color)


class RichEmbedBuilder:
    def __init__(self, color: int | str = "info") -> None:
        if isinstance(color, str):
            c = KlausEmbed._colors.get(color, KlausEmbed._colors["info"])
        else:
            c = color
        self._embed = discord.Embed(color=c)

    def title(self, t: str) -> "RichEmbedBuilder":
        self._embed.title = t
        return self

    def desc(self, d: str | None) -> "RichEmbedBuilder":
        self._embed.description = d
        return self

    def field(self, name: str, value: str, inline: bool = False) -> "RichEmbedBuilder":
        self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def fields(self, *items: tuple[str, str, bool]) -> "RichEmbedBuilder":
        for item in items:
            name, value = item[0], item[1]
            inline = item[2] if len(item) > 2 else False
            self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def inline_field(self, name: str, value: str) -> "RichEmbedBuilder":
        self._embed.add_field(name=name, value=value, inline=True)
        return self

    def block_field(self, name: str, value: str) -> "RichEmbedBuilder":
        self._embed.add_field(name=name, value=value, inline=False)
        return self

    def thumb(self, url: str | None) -> "RichEmbedBuilder":
        if url:
            self._embed.set_thumbnail(url=url)
        return self

    def image(self, url: str | None) -> "RichEmbedBuilder":
        if url:
            self._embed.set_image(url=url)
        return self

    def images(self, thumb: str | None = None, image: str | None = None) -> "RichEmbedBuilder":
        if thumb:
            self._embed.set_thumbnail(url=thumb)
        if image:
            self._embed.set_image(url=image)
        return self

    def footer(self, text: str, icon: str | None = None) -> "RichEmbedBuilder":
        self._embed.set_footer(text=text, icon_url=icon)
        return self

    def timestamp(self, dt: datetime | None = None) -> "RichEmbedBuilder":
        self._embed.timestamp = dt or discord.utils.utcnow()
        return self

    def author(
        self, name: str, icon: str | None = None, url: str | None = None
    ) -> "RichEmbedBuilder":
        self._embed.set_author(name=name, icon_url=icon, url=url)
        return self

    def author_with_url(
        self, name: str, url: str, icon: str | None = None
    ) -> "RichEmbedBuilder":
        self._embed.set_author(name=name, icon_url=icon, url=url)
        return self

    def color(self, c: int | str) -> "RichEmbedBuilder":
        if isinstance(c, str):
            c = KlausEmbed._colors.get(c, KlausEmbed._colors["info"])
        self._embed.color = c
        return self

    def build(self) -> discord.Embed:
        return self._embed


def make_embed(color: int | str = "info") -> KlausEmbed:
    return KlausEmbed(color)
