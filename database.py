"""
database.py — всё, что связано с базой SQLite.

Первая часть — подключение:
    connect()       открыть базу
    init_db()       создать таблицы и заполнить словарь
    transaction()   несколько изменений как одно целое (всё или ничего)

Вторая часть — репозитории (единственное место с SQL):
    WordRepository     — слова словаря
    UserRepository     — пользователи и пароли
    ProgressRepository — прогресс, выученные слова, история тестов
    SessionRepository  — «запомнить меня» (кто вошёл последним)
"""
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from utils import db_path, hash_password, needs_rehash, seed_vocabulary_path, verify_password


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


class DuplicateWordError(ValueError):
    pass


class UserExistsError(ValueError):
    pass


class AuthError(ValueError):
    pass


class WordRepository:
    def __init__(self, c):
        self.c = c

    def all(self):
        return [dict(r) for r in self.c.execute('SELECT id, english, russian FROM words ORDER BY id')]

    def count(self):
        return self.c.execute('SELECT count(*) FROM words').fetchone()[0]

    def by_id(self, i):
        r = self.c.execute('SELECT id, english, russian FROM words WHERE id=?', (i,)).fetchone()
        return dict(r) if r else None

    def find_by_english(self, s):
        r = self.c.execute('SELECT id, english, russian FROM words WHERE english_norm=?',
                           (s.strip().lower(),)).fetchone()
        return dict(r) if r else None

    def find_by_russian(self, s):
        r = self.c.execute('SELECT id, english, russian FROM words WHERE russian_norm=?',
                           (s.strip().lower(),)).fetchone()
        return dict(r) if r else None

    def search(self, s):
        # экранируем спецсимволы LIKE (\ % _), чтобы искать их как обычный текст
        q = '%' + s.lower().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%'
        rows = self.c.execute(
            "SELECT id, english, russian FROM words "
            "WHERE english_norm LIKE ? ESCAPE '\\' OR russian_norm LIKE ? ESCAPE '\\' ORDER BY id",
            (q, q)
        )
        return [dict(r) for r in rows]

    def add(self, en, ru):
        try:
            cur = self.c.execute(
                'INSERT INTO words(english, russian, english_norm, russian_norm) VALUES(?, ?, ?, ?)',
                (en.strip(), ru.strip(), en.strip().lower(), ru.strip().lower())
            )
            commit(self.c)
            return cur.lastrowid
        except Exception as e:
            if 'UNIQUE' in str(e):
                raise DuplicateWordError from e
            raise

    def delete(self, i):
        self.c.execute('DELETE FROM words WHERE id=?', (i,))
        commit(self.c)


class UserRepository:
    def __init__(self, c):
        self.c = c

    def get_by_username(self, u):
        r = self.c.execute('SELECT * FROM users WHERE username_norm=?', (u.strip().lower(),)).fetchone()
        return dict(r) if r else None

    def get_by_id(self, i):
        r = self.c.execute('SELECT * FROM users WHERE id=?', (i,)).fetchone()
        return dict(r) if r else None

    def exists(self, u):
        return self.get_by_username(u) is not None

    def create(self, u, p):
        if self.exists(u):
            raise UserExistsError(u)
        now = datetime.now().isoformat()
        with transaction(self.c):       # пользователь и его прогресс создаются вместе
            cur = self.c.execute(
                'INSERT INTO users(username, username_norm, password_hash, created_at) VALUES(?, ?, ?, ?)',
                (u, u.strip().lower(), hash_password(p), now)
            )
            self.c.execute('INSERT INTO user_progress(user_id) VALUES(?)', (cur.lastrowid,))
        return self.get_by_id(cur.lastrowid)

    def authenticate(self, u, p):
        user = self.get_by_username(u)
        if not user or not verify_password(p, user['password_hash']):
            raise AuthError('Неверное имя пользователя или пароль')
        return user

    def rehash_if_needed(self, user, p):
        if needs_rehash(user['password_hash']):
            self.c.execute('UPDATE users SET password_hash=? WHERE id=?', (hash_password(p), user['id']))
            commit(self.c)

    def change_password(self, user_id, p):
        self.c.execute('UPDATE users SET password_hash=? WHERE id=?', (hash_password(p), user_id))
        commit(self.c)


class ProgressRepository:
    COLUMNS = ('tests_completed', 'correct_answers', 'total_answers', 'streak',
               'last_login_date', 'daily_date', 'daily_words_start', 'daily_tests_start')
    TEXT_COLUMNS = ('last_login_date', 'daily_date')

    def __init__(self, c):
        self.c = c

    def ensure(self, uid):
        self.c.execute('INSERT OR IGNORE INTO user_progress(user_id) VALUES(?)', (uid,))
        commit(self.c)

    def load(self, uid):
        self.ensure(uid)
        return dict(self.c.execute('SELECT * FROM user_progress WHERE user_id=?', (uid,)).fetchone())

    def save(self, uid, p):
        sets = ', '.join(col + '=?' for col in self.COLUMNS)
        values = tuple(p.get(col, '' if col in self.TEXT_COLUMNS else 0) for col in self.COLUMNS)
        self.c.execute('UPDATE user_progress SET ' + sets + ' WHERE user_id=?', values + (uid,))
        commit(self.c)

    def learned_ids(self, uid):
        return {r[0] for r in self.c.execute('SELECT word_id FROM learned_words WHERE user_id=?', (uid,))}

    def learned_count(self, uid):
        return self.c.execute('SELECT count(*) FROM learned_words WHERE user_id=?', (uid,)).fetchone()[0]

    def mark_learned(self, uid, wid):
        self.c.execute('INSERT OR IGNORE INTO learned_words(user_id, word_id) VALUES(?, ?)', (uid, wid))
        commit(self.c)

    def unmark_learned(self, uid, wid):
        self.c.execute('DELETE FROM learned_words WHERE user_id=? AND word_id=?', (uid, wid))
        commit(self.c)

    def start_quiz(self, uid, mode):
        cur = self.c.execute('INSERT INTO quiz_sessions(user_id, mode, started_at) VALUES(?, ?, ?)',
                             (uid, mode, datetime.now().isoformat()))
        commit(self.c)
        return cur.lastrowid

    def finish_quiz(self, i, score, questions):
        self.c.execute('UPDATE quiz_sessions SET score=?, questions=?, finished_at=? WHERE id=?',
                       (score, questions, datetime.now().isoformat(), i))
        commit(self.c)

    def recent_quizzes(self, uid, limit=20):
        rows = self.c.execute('SELECT * FROM quiz_sessions WHERE user_id=? ORDER BY id DESC LIMIT ?',
                              (uid, limit))
        return [dict(r) for r in rows]


class SessionRepository:
    def __init__(self, c):
        self.c = c

    def start(self, uid):
        self.c.execute('INSERT OR REPLACE INTO sessions VALUES(?, ?, ?)',
                       (uid, secrets.token_hex(32), datetime.now().isoformat()))
        commit(self.c)

    def current_user(self):
        r = self.c.execute('SELECT user_id FROM sessions ORDER BY created_at DESC LIMIT 1').fetchone()
        return r[0] if r else None

    def clear(self):
        self.c.execute('DELETE FROM sessions')
        commit(self.c)

    def clear_for_user(self, uid):
        self.c.execute('DELETE FROM sessions WHERE user_id=?', (uid,))
        commit(self.c)
