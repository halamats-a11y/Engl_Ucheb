"""
utils.py — вспомогательные функции.

    Пути к файлам: база, словарь, иконка (работает и в .exe)
    Пароли: хранятся не открытым текстом, а «отпечатком» PBKDF2-SHA256 с солью
"""
import hashlib
import hmac
import os
import sys
from pathlib import Path


def project_root():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


def resource_path(relative_path):
    return str(project_root() / relative_path)


def data_dir():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32':
            base = os.environ.get('APPDATA', str(Path.home()))
        elif sys.platform == 'darwin':
            base = str(Path.home() / 'Library/Application Support')
        else:
            base = os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))
        path = Path(base) / 'VocabularyTrainer'
    else:
        path = project_root() / 'data'
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path():
    return os.environ.get('VOCAB_DB', str(data_dir() / 'app.db'))


def icon_path():
    """Иконка программы: окно, панель задач, шапка, окно входа."""
    return resource_path('data/ico.png')


def seed_vocabulary_path():
    return resource_path('data/vocabulary.json')


ITERATIONS = 260_000


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return f'pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest.hex()}'


def verify_password(password, encoded):
    if encoded.startswith('pbkdf2_sha256$'):
        try:
            _, rounds, salt, expected = encoded.split('$')
            actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(rounds)).hex()
            return hmac.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False
    # старый формат (простой sha256) — поддерживаем, чтобы старые аккаунты могли войти
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), encoded)


def needs_rehash(encoded):
    return not encoded.startswith('pbkdf2_sha256$')
