import random
import string
from datetime import datetime, timezone
from typing import Iterable
from discord import app_commands


def format_koins(value: int) -> str:
    """Format a koins value with thousand separator as dot."""
    return f"{value:,}".replace(",", ".")


def calculate_streak_bonus(streak: int, base: int) -> int:
    """Calculate streak bonus with tiered scaling (no hard cap)."""
    if streak <= 1:
        return 0
    if streak <= 30:
        return int(streak * base)
    if streak <= 100:
        return int(30 * base + (streak - 30) * base * 1.5)
    if streak <= 365:
        return int(30 * base + 70 * base * 1.5 + (streak - 100) * base * 2)
    return int(30 * base + 70 * base * 1.5 + 265 * base * 2 + (streak - 365) * base * 3)


def format_cooldown(retry_after: float) -> str:
    """Return a human-readable cooldown string."""
    total = int(retry_after)
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def random_password(length: int = 12) -> str:
    """Generate a random password with letters and digits."""
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


def build_help_text(commands: Iterable[app_commands.Command]) -> str:
    """Generate help text from a list of app commands."""
    lines = [
        f"`/{cmd.name}` \u2014 {cmd.description or 'Sem descri\u00e7\u00e3o'}"
        for cmd in sorted(commands, key=lambda c: c.name)
    ]
    return "\n".join(lines)


def create_progress_bar(current: int, maximum: int, length: int = 15) -> str:
    """Create a visual progress bar."""
    if maximum <= 0:
        return "\u25a1" * length
    filled = min(int((current / maximum) * length), length)
    return "\u2588" * filled + "\u25a1" * (length - filled)


class CooldownFormatter:
    @staticmethod
    def format(retry_after: float) -> str:
        return format_cooldown(retry_after)

    @staticmethod
    def format_hms(retry_after: float) -> tuple[int, int, int]:
        total = int(retry_after)
        hours = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return hours, minutes, seconds


def format_number(value: int) -> str:
    """Format large numbers with K/M/B/T suffixes."""
    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    if abs_value >= 1_000_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"{sign}{abs_value / 1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"{sign}{abs_value / 1_000:.1f}K"
    return str(value)


def time_ago(dt: datetime) -> str:
    """Convert datetime to 'há X minutos/horas/dias' format (Portuguese)."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return "agora"
    minutes = seconds // 60
    if minutes < 60:
        return f"há {minutes} minuto{'s' if minutes != 1 else ''}"
    hours = minutes // 60
    if hours < 24:
        return f"há {hours} hora{'s' if hours != 1 else ''}"
    days = hours // 24
    if days < 30:
        return f"há {days} dia{'s' if days != 1 else ''}"
    months = days // 30
    if months < 12:
        return f"há {months} mês{'es' if months != 1 else ''}"
    years = days // 365
    return f"há {years} ano{'s' if years != 1 else ''}"


def truncate(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "\u2026"


def risk_color(days: int) -> str:
    """Return risk emoji based on account age in days."""
    if days < 7:
        return "\U0001f534"  # red circle
    if days < 30:
        return "\U0001f7e1"  # yellow circle
    return "\U0001f7e2"  # green circle


def progress_bar_emoji(current: int, maximum: int, length: int = 10) -> str:
    """Create a progress bar using emoji blocks."""
    if maximum <= 0:
        return "\u2b1c" * length
    filled = min(round((current / maximum) * length), length)
    return "\U0001f7e5" * filled + "\U0001f7e8" * (length - filled)


def generate_invite_code() -> str:
    """Generate a random 8-char invite code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


def format_duration(seconds: float) -> str:
    """Format seconds into a human-readable duration string."""
    total = int(seconds)
    days = total // 86400
    hours = (total % 86400) // 3600
    minutes = (total % 3600) // 60
    secs = total % 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def ordinal(n: int) -> str:
    """Return ordinal string for a number (1st, 2nd, 3rd, etc)."""
    if 11 <= (n % 100) <= 13:
        suffix = "\u00aa"
    else:
        suffix = {1: "\u00ba", 2: "\u00aa", 3: "\u00aa"}.get(n % 10, "\u00aa")
    return f"{n}{suffix}"


EMOJI_NUMBERS = {
    0: "\U0001f51f", 1: "\u0031\u20e3", 2: "\u0032\u20e3", 3: "\u0033\u20e3",
    4: "\u0034\u20e3", 5: "\u0035\u20e3", 6: "\u0036\u20e3", 7: "\u0037\u20e3",
    8: "\u0038\u20e3", 9: "\u0039\u20e3", 10: "\U0001f51f",
}


def emoji_number(n: int) -> str:
    """Return keycap emoji for a number (0-10)."""
    return EMOJI_NUMBERS.get(n, f"{n}\u20e3")


def bar(current: int, maximum: int, length: int = 10, filled: str = "\u2588", empty: str = "\u2591") -> str:
    """Create a text progress bar with customizable characters."""
    if maximum <= 0:
        return empty * length
    ratio = max(0.0, min(1.0, current / maximum))
    fill = round(ratio * length)
    return filled * fill + empty * (length - fill)


def bold(text: str) -> str:
    """Wrap text in Discord bold markdown."""
    return f"**{text}**"


def code(text: str) -> str:
    """Wrap text in Discord code block."""
    return f"`{text}`"