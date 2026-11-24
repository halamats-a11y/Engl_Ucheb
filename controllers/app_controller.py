"""
app_controller.py — запуск приложения: база, вход, главное окно.

Контроллер собирает приложение из слоёв:
    db/        — подключение и репозитории (SQL)
    services/  — бизнес-логика (словарь, прогресс)
    views/     — окна PyQt5
Показывает окно входа или сразу главное окно (если пользователь уже входил).
"""
import sys

from PyQt5.QtGui import QColor, QIcon, QPalette
from PyQt5.QtWidgets import QApplication

from db.connection import connect, init_db
from db.repository import (ProgressRepository, SessionRepository,
                           UserRepository, WordRepository)
from services.progress_service import ProgressService
from services.vocabulary_service import VocabularyService
from utils.paths import icon_path
from views.login_window import LoginWindow
from views.main_window import LanguageLearningApp


class AppController:
    def __init__(self):
        self.conn = connect()
        init_db(self.conn)
        self.words = WordRepository(self.conn)
        self.users = UserRepository(self.conn)
        self.progress = ProgressRepository(self.conn)
        self.sessions = SessionRepository(self.conn)
        self.vocabulary = VocabularyService(self.words)
        self.main_window = None
        self.login_window = None

        uid = self.sessions.current_user()
        user = self.users.get_by_id(uid) if uid else None
        if user:
            self.on_login(user)
        else:
            self.show_login()

    def show_login(self):
        self.login_window = LoginWindow(self.on_login, self.users, self.sessions)
        self.login_window.show()

    def on_login(self, user):
        if self.login_window:
            self.login_window.close()
        progress = ProgressService(self.conn, self.progress, user['id'], self.vocabulary)
        progress.update_streak()
        self.main_window = LanguageLearningApp(user, self.vocabulary, progress)
        self.main_window.logged_out.connect(self.on_logout)
        self.main_window.show()

    def on_logout(self):
        uid = self.main_window.user_id if self.main_window else None
        if uid:
            self.sessions.clear_for_user(uid)
        self.show_login()

    def quit(self):
        self.conn.close()


def main():
    if sys.platform == 'win32':
        # чтобы на панели задач Windows была наша иконка, а не значок Python
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('EnglUcheb.VocabularyTrainer')

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(icon_path()))   # иконка у всех окон программы
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    app.setPalette(palette)

    controller = AppController()
    app.aboutToQuit.connect(controller.quit)
    sys.exit(app.exec_())
