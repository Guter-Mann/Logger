
import logging

from pathlib import Path
from logging import StreamHandler
from logging.handlers import TimedRotatingFileHandler

from .utils import namer, rotator
from .formatter import DefaultFormatter
from .handlers import TelegramLogHandler
from .enums import LoggerLevel, ParseMode
from .exceptions import FormatError


class CreateLogger:
    """
    Класс предназначен для конфигурирования заготовленных
    настроек логгеров.

    ## Параметры:
    - **name**: `str` - Название логгера и файла f'{name}.log'
    если включен to_file;

    - **level**: `LoggerLevel` - Уровень логов. Принимает
    числа от 10 до 50. Можно использовать такой формат записи
    logging.INFO;

    - **fmt**: `str` - Формат логов для консоли;

    - **base_path**: `Path | None` - Введя полный путь к
    вашему проекту вы сможете выводить в лог относительный
    путь к модулю используя `relativePath`. Пример вывода:
    src/test.py:main[19] или если без функции src/test.py:[19]

    - **project_name**: `str | None` - Имя проекта которое
    будет доступно в логах по ключу `projectName`.По сути этот
    параметр нужен только для метода `telegram_handle()` если
    у вас один бот и на него идут логи с нескольких проектов.

    ## Методы:
    - **console_handle** - Регистрирует обработчик для вывода
    логов в консоль;

    - **file_handle** - Регистрирует обработчик для записи
    логов в файл с ротацией в архив .gz;

    - **telegram_handle** - Регистрирует обработчик для
    отправки логов в телеграм.
    """

    def __init__(
            self,
            name: str,
            fmt: str,
            level: LoggerLevel,
            base_path: Path | None = None,
            project_name: str | None = None
        ):

        self.name = name
        self.level = level
        self.fmt = fmt

        self.base_path = base_path
        self.project_name = project_name

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        if self.fmt.find('relativePath') > -1 and not base_path:
            raise FormatError('В формате указан ключ {relativePath} в то время как не указан base_path')
        if self.fmt.find('projectName') > -1 and not project_name:
            raise FormatError('В формате указан ключ {projectName} в то время как не указан project_name')

    def console_handle(
            self,
            fmt: str | None = None,
            level: LoggerLevel | None = None,
        ):
        """
        Метод предназначен для создания обработчика который
        выводит логи в консоль.

        #### Параметры:
        - **fmt**: `str | None` - Формат логов. Если не
        указать тогда по умолчанию будет установлен  общий
        формат объекта логгера;

        - **level**: `LoggerLevel | None` - Уровень логов.
        Если не указать тогда по умолчанию будет установлен
        общий уровень объекта логгера.
        """

        fmt = fmt or self.fmt
        level = level or self.level

        console_handler = StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(DefaultFormatter(
            fmt=fmt,
            datefmt='%H:%M:%S',
            base_path=self.base_path,
            project_name=self.project_name
        ))
        self.logger.addHandler(console_handler)

    def file_handle(
            self,
            log_path: Path,
            fmt: str | None = None,
            level: LoggerLevel | None = None,
        ):
        """
        Метод предназначен для создания обработчика который записывает логи в файл. Данный 
        обработчик имеет ротацию по дням которые архивируются в формат `.gz`.

        #### Параметры:
        - **fmt**: `str | None` - Формат логов. Если не
        указать тогда по умолчанию будет установлен общий
        формат объекта логгера;

        - **level**: `LoggerLevel | None` - Уровень логов.
        Если не указать тогда по умолчанию будет установлен
        общий уровень объекта логгера;

        - **log_path**: `Path` - Путь к созданию файлов для
        записи в лог.
        """

        fmt = fmt or self.fmt
        level = level or self.level

        log_path.mkdir(parents=True, exist_ok=True)

        filename = f'{self.name}.log'
        file_handler = TimedRotatingFileHandler(
            Path(log_path / filename),
            when='midnight',
            backupCount=7,
            encoding='utf-8'
        )

        file_handler.namer = namer
        file_handler.rotator = rotator
        file_handler.setLevel(level)
        file_handler.setFormatter(DefaultFormatter(
            fmt=fmt,
            datefmt='%Y-%m-%d %H:%M:%S',
            use_colors=False,
            base_path=self.base_path,
            project_name=self.project_name
        ))

        self.logger.addHandler(file_handler)

    def telegram_handle(
            self,
            bot_token: str,
            user_id: str | int,
            fmt: str | None = None,
            level: LoggerLevel | None = None,
            parse_mode: ParseMode = ParseMode.MarkdownV2
        ):
        """
        Метод предназначен для создания обработчика который отправляет логи в вашего
        телеграм бота. Сообщения можно форматировать используя HTML, Markdown и
        MarkdownV2 которые описанны в logger.enums.ParseMode. Если вы используете
        одного бота для нескольких проектов то в `fmt` вы можете указать `projectName`
        перед этим указав `project_name` в инициализации объекта логгера.

        #### Параметры:
        - **bot_token**: `str` - Токен вашего телеграм бота;

        - **user_id**: `str | int` - Идентификатор пользователя которому вы хотите
        отправлять логи. Обратите внимание что перед использованием пользователь
        должен запустить бота чтобы тот смог отправлять ему сообщения;

        - **fmt**: `str | None` - Формат логов. Если не указать тогда по умолчанию
        будет установлен  общий формат объекта логгера;

        - **level**: `LoggerLevel | None` - Уровень логов. Если не указать тогда по
        умолчанию будет установлен общий уровень объекта логгера;

        - **parse_mode**: `ParseMode = ParseMode.MarkdownV2` - Метод форматирования
        сообщений отправленные в телеграм. По умолчанию стоит MarkdownV2.
        """
        
        fmt = fmt or self.fmt
        level = level or self.level

        telegram_handler = TelegramLogHandler(
            user_id=user_id,
            bot_token=bot_token,
            parse_mode=parse_mode
        )
        telegram_handler.setLevel(level)
        telegram_handler.setFormatter(DefaultFormatter(
            fmt=fmt,
            use_colors=False,
            base_path=self.base_path,
            project_name=self.project_name
        ))
        self.logger.addHandler(telegram_handler)
