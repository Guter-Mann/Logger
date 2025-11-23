
import logging
import requests

from copy import copy
from logging import LogRecord, Handler

from .enums import ParseMode
from .utils import escape_markdown_v2
from .exceptions import HTTPException


class TelegramLogHandler(Handler):
    def __init__(
        self,
        user_id: str | int,
        bot_token: str,
        parse_mode: ParseMode,
        level=logging.NOTSET
    ):
        self.user_id = user_id
        self.bot_token = bot_token
        self.parse_mode = parse_mode
        super().__init__(level)

    def emit(self, record: LogRecord):
        recordcopy = copy(record)
        if recordcopy.exc_info:
            exc_info = self.formatter.formatException(recordcopy.exc_info)
        else:
            exc_info = ''
        exc_message = recordcopy.message
        recordcopy.msg = escape_markdown_v2(exc_message + '\n' + exc_info)
        recordcopy.args = ()
        recordcopy.exc_info = None
        recordcopy.exc_text = None
        message = self.formatter.format(recordcopy)

        res = requests.post(
            url=f'https://api.telegram.org/bot{self.bot_token}/sendMessage',
            json={
                'chat_id': self.user_id,
                'text': message,
                'parse_mode': self.parse_mode.value
            }
        )

        if res.status_code != 200:
            error = res.json()
            raise HTTPException(status_code=error['error_code'], detail=error['description'])
        
        # TODO: Сюда могу прилетать очень большие ошибки. Их нужно как то сокращать!
