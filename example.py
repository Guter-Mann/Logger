
import os
import logging

from dotenv import load_dotenv
from pathlib import Path
from logger import CreateLogger


# ======================= BASE FORMATS ====================== #
DEFULT_FORMAT = '[{asctime}] {levelprefix}: {name}[{pid}] - {message}'

FILE_FORMAT = '[{asctime}] {levelprefix}: {relativePath} {message}'

TELEGRAM_FROMAT = """
*Project:* `{projectName}`

*Logger:* `{name}`
*Level:* `{levelname}`
*Time:* `{asctime}`
*Path:* `{relativePath}`

```python
{message}
```
"""

# ====================== BASE SETTINGS ====================== #
BASE_PATH = Path(__file__).parent.resolve()
LOG_PATH = BASE_PATH / 'logs'
ENV_PATH = BASE_PATH / '.env'
NAME_PROJECT = 'Example'

if ENV_PATH.exists():
    load_dotenv()

TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# ===================== BASE CONFIGURATE ==================== #
logger = CreateLogger(
    name='Logger1',
    fmt=DEFULT_FORMAT,
    level=logging.DEBUG,
    base_path=BASE_PATH,
    project_name=NAME_PROJECT
)
logger.console_handle()
logger.file_handle(log_path=LOG_PATH, fmt=FILE_FORMAT)
logger.telegram_handle(
    bot_token=TELEGRAM_BOT_TOKEN,
    user_id=TELEGRAM_USER_ID,
    fmt=TELEGRAM_FROMAT,
    level=logging.WARNING,
)


# ========================== EXAMPLE ======================== #
log = logging.getLogger('Logger1')

log.debug('Log debug')
log.info('Log info')
log.warning('Log warning')
log.error('Log error')
log.critical('Log critical')