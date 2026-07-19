"""Professional logging configuration for Klaus Bot.

Provides:
- Colored console output with colorama
- File rotation (5 MB, keeps 5 backups)
- Structured format with level, module, and timestamp
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys

_DIR = os.path.dirname(os.path.abspath(__file__))
_LOG_DIR = os.path.join(_DIR, "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_LEVEL_COLORS = {
    logging.DEBUG: "\033[36m",       # cyan
    logging.INFO: "\033[32m",        # green
    logging.WARNING: "\033[33m",     # yellow
    logging.ERROR: "\033[31m",       # red
    logging.CRITICAL: "\033[1;31m",  # bold red
}
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_MAGENTA = "\033[35m"


class _ColoredFormatter(logging.Formatter):
    """Console formatter with ANSI colors and compact layout."""

    def format(self, record: logging.LogRecord) -> str:
        level_color = _LEVEL_COLORS.get(record.levelno, "")
        level_name = record.levelname.ljust(8)
        ts = self.formatTime(record, "%H:%M:%S")
        module = record.name.replace("klaus.", "").replace("cogs.", "")

        msg = record.getMessage()
        if record.exc_info and record.exc_info[0] is not None:
            exc = self.formatException(record.exc_info)
            msg = f"{msg}\n{exc}"

        return (
            f"{_DIM}{ts}{_RESET} "
            f"{_MAGENTA}{_BOLD}|{_RESET} "
            f"{level_color}{_BOLD}{level_name}{_RESET} "
            f"{_DIM}{module:<16}{_RESET} "
            f"{msg}"
        )


class _FileFormatter(logging.Formatter):
    """File formatter with full details (no ANSI)."""

    def format(self, record: logging.LogRecord) -> str:
        ts = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        module = record.name
        msg = record.getMessage()
        if record.exc_info and record.exc_info[0] is not None:
            exc = self.formatException(record.exc_info)
            msg = f"{msg}\n{exc}"
        return f"{ts} | {record.levelname:<8} | {module:<24} | {msg}"


def setup_logging() -> None:
    """Configure root logger with colored console + rotating file handler."""
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Remove existing handlers
    for h in root.handlers[:]:
        root.removeHandler(h)

    # Console handler (INFO level, colored)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(_ColoredFormatter())
    root.addHandler(console)

    # File handler (DEBUG level, rotating, 5MB x 5 files)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(_LOG_DIR, "klaus.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_FileFormatter())
    root.addHandler(file_handler)

    # Suppress noisy libraries
    for noisy in ("discord", "discord.http", "discord.gateway", "urllib3", "motor"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
