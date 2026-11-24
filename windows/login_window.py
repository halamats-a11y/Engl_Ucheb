"""
login_window.py — окно входа и регистрации нового пользователя.

Что делает этот файл:
    Показывает форму: имя пользователя, пароль, «Запомнить меня», кнопки «Войти» и «Зарегистрироваться».
    Проверка пароля и регистрация идут через базу SQLite (UserRepository в database.py),
    «Запомнить меня» записывает сессию в таблицу sessions (SessionRepository).

Как вписывается в приложение:
    AppController (app.py) создаёт LoginWindow и передаёт колбэк on_login(user).
    После успешного входа вызывается этот колбэк — открывается главное окно (main_window.py).

Ключевые понятия для начинающих:
    • QWidget — обычное окно/панель PyQt5 (не главное окно, а отдельный виджет).
    • Пароль в базе не хранится открытым текстом, только хеш PBKDF2-SHA256 с солью (utils.py).
    • Сессия в таблице sessions — если «Запомнить» включено, при следующем запуске вход без формы.
"""
import sys
import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from styles import (LOGIN_ERROR_STYLE, LOGIN_SUBTITLE_STYLE, LOGIN_SUCCESS_STYLE,
                    LOGIN_WINDOW_STYLE, TRANSPARENT_STYLE)
from utils import icon_path


def resource_path(relative_path):
    """
    Возвращает абсолютный путь к файлу в папке проекта или внутри .exe.

    При сборке в exe PyInstaller кладёт ресурсы во временную папку sys._MEIPASS.
    relative_path — например 'data/ico.png'.
    """
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        # Поднимаемся из папки windows/ в корень проекта
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(base, relative_path))


class LoginWindow(QWidget):
    """
    Окно авторизации: вход существующего пользователя или регистрация нового.

    После успешного входа вызывает self.on_login_success(username), переданный из main.py.
    """

    def __init__(self, on_login_success, users, sessions):
        super().__init__()
        self.on_login_success, self.users, self.sessions = on_login_success, users, sessions
        self.init_ui()
        self.apply_styles()

    # ── UI ───────────────────────────────────────────────────────────

    def init_ui(self):
        """Создаёт все поля ввода, кнопки и подписи на окне входа."""
        self.setWindowTitle("Вход")
        self.setFixedSize(420, 650)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(14)
        self.setLayout(layout)

        # Иконка и заголовок
        logo = QLabel()
        logo.setPixmap(QPixmap(icon_path()).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedHeight(80)
        logo.setStyleSheet(TRANSPARENT_STYLE)
        layout.addWidget(logo)

        title = QLabel("Изучение английского")
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Войдите или создайте аккаунт")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(LOGIN_SUBTITLE_STYLE)
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Имя пользователя
        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя...")
        layout.addWidget(self.username_input)

        # Пароль + кнопка-глазик (показать/скрыть)
        layout.addWidget(QLabel("Пароль:"))

        pwd_container = QWidget()
        pwd_container.setFixedHeight(48)
        # QHBoxLayout: поле пароля растягивается, кнопка «глаз» фиксированной ширины справа
        pwd_row = QHBoxLayout(pwd_container)
        pwd_row.setContentsMargins(0, 0, 0, 0)
        pwd_row.setSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль...")
        self.password_input.setEchoMode(QLineEdit.Password)  # символы скрыты точками
        self.password_input.setMinimumHeight(44)
        pwd_row.addWidget(self.password_input)

        self.toggle_pwd_btn = QPushButton("👁")
        self.toggle_pwd_btn.setFixedSize(44, 44)
        self.toggle_pwd_btn.setObjectName("eyeBtn")
        self.toggle_pwd_btn.setToolTip("Показать / скрыть пароль")
        self.toggle_pwd_btn.clicked.connect(self._toggle_password_visibility)
        pwd_row.addWidget(self.toggle_pwd_btn)

        layout.addWidget(pwd_container)

        # Галочка «Запомнить на этом компьютере»
        self.remember_checkbox = QCheckBox("Запомнить на этом компьютере")
        self.remember_checkbox.setObjectName("rememberCheck")
        layout.addWidget(self.remember_checkbox)

        # Метка ошибки / успеха (красный или зелёный текст)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(LOGIN_ERROR_STYLE)
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        # Кнопки
        login_btn = QPushButton("▶ Войти")
        login_btn.clicked.connect(self.do_login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("➕ Зарегистрироваться")
        register_btn.setObjectName("secondary")
        register_btn.clicked.connect(self.do_register)
        layout.addWidget(register_btn)

        layout.addStretch()

        # Enter в поле пароля = то же, что кнопка «Войти»
        self.password_input.returnPressed.connect(self.do_login)

    def _toggle_password_visibility(self):
        """Переключает режим поля пароля: скрытый ↔ видимый текст, меняет иконку кнопки."""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pwd_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pwd_btn.setText("👁")

    # ── Логика входа / регистрации ────────────────────────────────────

    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Заполните все поля!")
            return
        try:
            user = self.users.authenticate(username, password)
        except Exception:
            self.error_label.setText("Неверное имя пользователя или пароль.")
            return
        self.users.rehash_if_needed(user, password)
        if self.remember_checkbox.isChecked():
            self.sessions.start(user['id'])
        else:
            self.sessions.clear()
        self.error_label.setText("")
        self.on_login_success(user)

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Заполните все поля!")
            return
        if len(password) < 4:
            self.error_label.setText("Пароль должен быть минимум 4 символа.")
            return
        try:
            self.users.create(username, password)
        except Exception:
            self.error_label.setText("Это имя уже занято.")
            return
        self.error_label.setStyleSheet(LOGIN_SUCCESS_STYLE)
        self.error_label.setText("Аккаунт создан! Теперь войдите.")

    def apply_styles(self):
        """Подключает CSS из LOGIN_STYLES и дополнительные стили для глаза и чекбокса."""
        self.setStyleSheet(LOGIN_WINDOW_STYLE)
