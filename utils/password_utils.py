"""
password_utils.py — хранение паролей.

Пароль не хранится в базе в открытом виде: сохраняется «отпечаток»
PBKDF2-SHA256 с солью (случайные байты), его нельзя превратить обратно в пароль.
"""
import hashlib
import hmac
import os

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
