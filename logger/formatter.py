
import logging
from copy import copy
from pathlib import Path
from typing import Literal
from multiprocessing import current_process

from .exceptions import FormatError
from .safe_logger import SafeLogger


LEVELS_COLORS = {
    'DEBUG': '\033[1m' + '\033[36m' + 'DEBUG' + '\033[0m',
    'INFO': '\033[1m' + '\033[32m' + 'INFO' + '\033[0m',
    'WARNING': '\033[1m' + '\033[33m' + 'WARNING' + '\033[0m',
    'ERROR': '\033[1m' + '\033[31m' + 'ERROR' + '\033[0m',
    'CRITICAL': '\033[1m' + '\033[31m' + 'CRITICAL' + '\033[0m'
}


class DefaultFormatter(logging.Formatter):
    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal['%', '{', '$'] = '{',
        use_colors: bool = True,
        base_path: Path | None = None,
        project_name: str = '',
    ):
        self.use_colors = use_colors
        self.base_path = base_path
        self.project_name = project_name
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def _safe_relative(self, pathname: str | None) -> str:
        """Безопасно получает относительный путь"""
        if not pathname:
            return "<unknown>"
        if not self.base_path:
            return str(pathname)
        try:
            return str(Path(pathname).relative_to(self.base_path))
        except Exception:
            return str(pathname)

    def formatMessage(self, record: logging.LogRecord) -> str:
        recordcopy = copy(record)

        pid = current_process().pid
        name = recordcopy.name
        levelname = recordcopy.levelname
        message = recordcopy.message
        separator = ' ' * (8 - len(levelname))

        """---------- относительный путь ----------"""
        relative_path = ''

        if self.base_path:
            path_str = self._safe_relative(recordcopy.pathname)
            relative_path = path_str.replace('\\', '/') + ':'
            if recordcopy.funcName != '<module>':
                relative_path += recordcopy.funcName
            relative_path += f'[{recordcopy.lineno}]'
        elif 'relativePath' in self._fmt:
            raise FormatError('В формате указан ключ {relativePath}, но base_path не задан')

        """---------- название проекта ----------"""
        project_name = ''

        if self.project_name:
            project_name = self.project_name
        elif 'projectName' in self._fmt:
            raise FormatError('В формате указан ключ {projectName}, но project_name не задан')

        """---------- оформление ----------"""
        if self.use_colors:
            pid = f'\033[36m{pid}\033[0m'
            name = f'\033[37m{name}\033[0m'
            levelname = LEVELS_COLORS[levelname]
            relative_path = f'\033[2m\033[37m{relative_path}\033[0m'

        recordcopy.__dict__.update({
            'levelprefix': levelname + separator,
            'relativePath': relative_path,
            'projectName': project_name,
            'message': SafeLogger(message).protect(),
            'name': name,
            'pid': pid,
        })

        return super().formatMessage(recordcopy)
