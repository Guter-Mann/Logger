
import re
import os
import gzip
import shutil

from pathlib import Path


def namer(name: str):
    file_path = Path(name)
    names = file_path.name.split('.')
    dest = file_path.parent / names[0]
    dest.mkdir(parents=True, exist_ok=True)
    return str(dest / f'{names[2]}.log.gz')


def rotator(source: str, dest: str):
    with open(source, 'rb') as f_in:
        with gzip.open(dest, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(source)


def escape_markdown_v2(text: str) -> str:
    text = text.replace('\\', '/')
    escape_chars = r'[_*\[\]()~`>#+\-=|{}.!]'
    return re.sub(escape_chars, lambda match: f'\\{match.group(0)}', text)