"""
connection.py — подключение к базе SQLite и создание таблиц.
"""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from utils.paths import db_path, seed_vocabulary_path

SCHEMA_VERSION = 1
# Схема базы: 6 таблиц. Слова общие для всех, прогресс и тесты — у каждого пользователя свои.
DDL_V1 = '''
CREATE TABLE IF NOT EXISTS words(
    id           INTEGER PRIMARY KEY,
    english      TEXT NOT NULL,
    russian      TEXT NOT NULL,
    english_norm TEXT NOT NULL,
    russian_norm TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(english, russian)
);
CREATE INDEX IF NOT EXISTS idx_words_english_norm ON words(english_norm);
CREATE INDEX IF NOT EXISTS idx_words_russian_norm ON words(russian_norm);

CREATE TABLE IF NOT EXISTS users(
    id            INTEGER PRIMARY KEY,
    username      TEXT NOT NULL,
    username_norm TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_progress(
    user_id           INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    tests_completed   INTEGER NOT NULL DEFAULT 0,
    correct_answers   INTEGER NOT NULL DEFAULT 0,
    total_answers     INTEGER NOT NULL DEFAULT 0,
    streak            INTEGER NOT NULL DEFAULT 0,
    last_login_date   TEXT NOT NULL DEFAULT '',
    daily_date        TEXT NOT NULL DEFAULT '',
    daily_words_start INTEGER NOT NULL DEFAULT 0,
    daily_tests_start INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS learned_words(
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_id    INTEGER NOT NULL REFERENCES words(id) ON DELETE CASCADE,
    learned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(user_id, word_id)
);

CREATE TABLE IF NOT EXISTS sessions(
    user_id    INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quiz_sessions(
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mode        TEXT NOT NULL,
    score       INTEGER NOT NULL DEFAULT 0,
    questions   INTEGER NOT NULL DEFAULT 0,
    started_at  TEXT NOT NULL,
    finished_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_sessions(user_id, started_at);
'''


def connect(path=None):
    """Открывает базу SQLite (создаёт папку, если её нет) и включает нужные настройки."""
    path = path or db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    c.execute('PRAGMA journal_mode=WAL')
    c.execute('PRAGMA synchronous=NORMAL')
    return c


# id подключений, у которых сейчас открыта транзакция
_open_transactions = set()


@contextmanager
def transaction(conn):
    """
    Транзакция: несколько изменений в базе как одно целое.

        with transaction(conn):
            repo.finish_quiz(...)
            repo.save(...)

    Если всё прошло хорошо — сохраняется всё сразу (commit).
    Если где-то ошибка — не сохраняется ничего (rollback), база не «ломается» наполовину.
    """
    key = id(conn)
    if key in _open_transactions:       # уже внутри другой транзакции — она и сохранит
        yield conn
        return
    _open_transactions.add(key)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _open_transactions.discard(key)


def commit(conn):
    """Сохраняет изменения. Внутри transaction() ничего не делает — сохранит сама транзакция."""
    if id(conn) not in _open_transactions:
        conn.commit()


def init_db(conn, seed=True):
    """Создаёт таблицы (если их ещё нет) и заполняет словарь из data/vocabulary.json."""
    conn.executescript(DDL_V1)
    conn.execute(f'PRAGMA user_version={SCHEMA_VERSION}')
    if seed:
        seed_words(conn)


def seed_words(conn, path=None):
    """Добавляет стартовые слова. Повторы пропускаются (INSERT OR IGNORE)."""
    p = Path(path or seed_vocabulary_path())
    if not p.exists():
        return
    for w in json.loads(p.read_text(encoding='utf-8')):
        en = str(w.get('english', '')).strip()
        ru = str(w.get('russian', '')).strip()
        if en and ru:
            conn.execute(
                'INSERT OR IGNORE INTO words(english, russian, english_norm, russian_norm) '
                'VALUES(?, ?, ?, ?)',
                (en, ru, en.lower(), ru.lower())
            )
    commit(conn)
