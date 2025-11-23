
from enum import Enum


class LoggerLevel(Enum):
    DEBUG: int = 10
    INFO: int = 20
    WARNING: int = 30
    ERROR: int = 40
    CRITICAL: int = 50


class ParseMode(Enum):
    MarkdownV2: str = 'MarkdownV2'
    Markdown: str = 'Markdown'
    HTML: str = 'HTML'
