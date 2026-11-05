"""
main_window.py — главное окно приложения после входа в аккаунт.

Что делает этот файл:
    Создаёт класс LanguageLearningApp — центральное окно программы (QMainWindow).
    Здесь собираются все вкладки (флеш-карточки, тесты, переводчик, словарь, прогресс),
    боковая навигация, шапка с именем пользователя и кнопка «Выйти».

Как вписывается в приложение:
    1. Пользователь входит через login_window.py.
    2. main.py создаёт LanguageLearningApp и показывает это окно.
    3. Каждая вкладка получает ссылку self (main_window), чтобы читать словарь,
       прогресс и вызывать save_progress() / update_progress_stats().

Ключевые понятия для начинающих:
    • QMainWindow — стандартное «главное» окно PyQt5 с заголовком и кнопками свернуть/закрыть.
    • QStackedWidget — «стопка» виджетов: видна только одна вкладка за раз.
    • self (main_window) — общий объект, который вкладки хранят в self.main.
    • Серия дней (streak) — сколько дней подряд пользователь заходил в приложение.
    • Дневная цель — сколько слов и тестов нужно сделать за сегодня (константы внизу файла).
"""
import os
import json
from datetime import datetime, date
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from views.flashcards_tab import FlashcardsTab
from views.quiz_tab import QuizTab
from views.translator_tab import TranslatorTab
from views.vocabulary_tab import VocabularyTab
from views.progress_tab import ProgressTab
from views.welcome_dialog import WelcomeDialog
from utils.styles import MAIN_WINDOW_STYLES

# Дневная цель: сколько слов и тестов нужно пройти за день (используется в progress_tab и welcome_dialog)
DAILY_WORDS_TARGET = 5
DAILY_TESTS_TARGET = 1


class LanguageLearningApp(QMainWindow):
    """
    Главное окно приложения для изучения английского.

    Наследуется от QMainWindow — это базовый класс PyQt5 для окон с меню/панелями.
    Хранит словарь, прогресс текущего пользователя и переключает вкладки в QStackedWidget.
    """

    def __init__(self, user, words, progress, words_repo, progress_repo, user_repo, quiz_repo):
        super().__init__()
        self.user = user
        self.user_id = user['id']
        self.username = user['username']
        self.words_repo, self.progress_repo = words_repo, progress_repo
        self.user_repo, self.quiz_repo = user_repo, quiz_repo
        self.vocabulary = words
        self.progress_obj = progress
        self.user_progress = dict(progress)
        self.user_progress['words_learned'] = [w['english'] for w in words if w['id'] in progress_repo.learned_ids(self.user_id)]
        self.setWindowTitle(f"Помощник для изучения языков 🌍 — {self.username}")
        self.setGeometry(100, 100, 1100, 700)
        self._update_streak()
        self.init_ui()
        self.apply_styles()
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(200, self._show_welcome_dialog)

    def _update_streak(self):
        from datetime import date
        p = self.user_progress
        today = date.today().isoformat()
        last = p.get('last_login_date', '') or ''
        try:
            previous = date.fromisoformat(last) if last else None
        except ValueError:
            previous = None
        if last != today:
            p['streak'] = (p.get('streak', 0) + 1) if previous and (date.today()-previous).days == 1 else 1
            p['last_login_date'] = today
        if p.get('daily_date') != today:
            p['daily_date'] = today
            p['daily_words_start'] = len(p['words_learned'])
            p['daily_tests_start'] = p.get('tests_completed', 0)
        self.save_progress()

    def _get_daily_progress(self):
        p=self.user_progress
        return {'words_target': DAILY_WORDS_TARGET, 'tests_target': DAILY_TESTS_TARGET,
                'words_done': max(0,len(p.get('words_learned',[]))-p.get('daily_words_start',0)),
                'tests_done': max(0,p.get('tests_completed',0)-p.get('daily_tests_start',0))}

    def _show_welcome_dialog(self):
        dlg=WelcomeDialog(self.username,self.user_progress.get('streak',1),self._get_daily_progress(),parent=self); dlg.exec_()

    def reload_vocabulary(self):
        self.vocabulary=self.words_repo.all()
        if hasattr(self,'vocabulary_tab'): self.vocabulary_tab.refresh_table()
        if hasattr(self,'word_count_label'): self.word_count_label.setText(f"📚 Словарь: {len(self.vocabulary)} слов")

    def add_word(self, english, russian):
        self.words_repo.add(english,russian); self.reload_vocabulary()

    def delete_word(self, word):
        wid=word.get('id') if isinstance(word,dict) else self._word_id(word)
        if wid: self.words_repo.delete(wid); self.reload_vocabulary()

    def _word_id(self, word):
        return word.get('id') if isinstance(word,dict) else next((w['id'] for w in self.vocabulary if w['english']==word),None)

    def is_word_learned(self, word):
        if isinstance(word,dict): wid=word.get('id')
        else: wid=self._word_id(word)
        return bool(wid and wid in self.progress_repo.learned_ids(self.user_id))

    def mark_word_learned(self, word):
        wid=self._word_id(word)
        if wid: self.progress_repo.mark_learned(self.user_id,wid)
        self.user_progress['words_learned']=[w['english'] for w in self.vocabulary if w['id'] in self.progress_repo.learned_ids(self.user_id)]
        self.save_progress()

    def unmark_word_learned(self, word):
        wid=self._word_id(word)
        if wid: self.progress_repo.unmark_learned(self.user_id,wid)
        self.user_progress['words_learned']=[w['english'] for w in self.vocabulary if w['id'] in self.progress_repo.learned_ids(self.user_id)]
        self.save_progress()

    def save_progress(self):
        self.progress_repo.save(self.user_id,self.user_progress)

    def start_quiz_session(self, mode): return self.quiz_repo.start_quiz(self.user_id,mode)
    def finish_quiz_session(self, session_id, score, questions):
        self.quiz_repo.finish_quiz(session_id,score,questions)
    def abandon_quiz_session(self, session_id): pass

    def init_ui(self):
        """
        Собирает весь интерфейс: шапка, боковое меню, стек вкладок.

        QStackedWidget (self.stack) переключается по индексу 0..4 при клике на кнопки сайдбара.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        central_widget.setLayout(root_layout)

        # ── Верхняя панель ──────────────────────────────────────────
        header_widget = QWidget()
        header_widget.setObjectName("headerBar")
        header_widget.setStyleSheet("""
            QWidget#headerBar {
                background: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 12, 24, 12)

        title = QLabel("🎓 Помощник для изучения английского языка")
        title.setFont(QFont('Segoe UI', 15, QFont.Bold))
        title.setStyleSheet("color: #1A2C3E;")
        header_layout.addWidget(title)

        header_layout.addStretch()  # пустое пространство, толкает элементы справа к краю

        word_count = QLabel(f"📚 Словарь: {len(self.vocabulary)} слов")
        word_count.setStyleSheet("color: #7DD3B8; font-size: 13px; font-weight: 600; margin-right: 16px;")
        header_layout.addWidget(word_count)

        user_label = QLabel(f"👤 {self.username}")
        user_label.setStyleSheet("color: #5A6E7A; font-size: 13px; font-weight: 600; margin-right: 12px;")
        header_layout.addWidget(user_label)

        logout_btn = QPushButton("Выйти")
        logout_btn.setFixedWidth(80)
        logout_btn.setStyleSheet("""
            QPushButton { background-color: #5A6E7A; color: white; border-radius: 16px;
                          padding: 6px 12px; font-size: 12px; font-weight: 600; }
            QPushButton:hover { background-color: #4A5E6A; }
        """)
        logout_btn.clicked.connect(self.logout)
        header_layout.addWidget(logout_btn)

        root_layout.addWidget(header_widget)

        # ── Основная область: сайдбар + контент ─────────────────────
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # ── Боковая панель навигации ─────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QWidget#sidebar {
                background: #FFFFFF;
                border-right: 1px solid #E2E8F0;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 20, 12, 20)
        sidebar_layout.setSpacing(6)

        nav_items = [
            ("📚", "Флеш-карточки"),
            ("✏️", "Тесты"),
            ("🔄", "Переводчик"),
            ("📖", "Словарь"),
            ("📊", "Прогресс"),
        ]

        self.nav_buttons = []
        for i, (icon, label) in enumerate(nav_items):
            btn = QPushButton(f"  {icon}  {label}")
            btn.setFixedHeight(44)
            btn.setCheckable(True)  # кнопка может быть «нажата» как переключатель
            btn.setStyleSheet(self._nav_btn_style(False))
            # ВАЖНО: lambda с idx=i — без «=i» все кнопки переключали бы последнюю вкладку
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        body_layout.addWidget(sidebar)

        # ── Стек страниц (одна видимая вкладка) ─────────────────────
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")

        # Каждая вкладка получает self — ссылку на главное окно
        self.flashcards_tab = FlashcardsTab(self)
        self.quiz_tab = QuizTab(self)
        self.translator_tab = TranslatorTab(self)
        self.vocabulary_tab = VocabularyTab(self)
        self.progress_tab = ProgressTab(self)

        self.stack.addWidget(self.flashcards_tab)
        self.stack.addWidget(self.quiz_tab)
        self.stack.addWidget(self.translator_tab)
        self.stack.addWidget(self.vocabulary_tab)
        self.stack.addWidget(self.progress_tab)

        body_layout.addWidget(self.stack)
        root_layout.addLayout(body_layout)

        # Активировать первую вкладку (флеш-карточки)
        self._switch_tab(0)

    def _nav_btn_style(self, active: bool) -> str:
        """
        Возвращает CSS-строку для кнопки навигации.

        active=True — подсветка текущей вкладки, False — обычное состояние.
        """
        if active:
            return """
                QPushButton {
                    background: rgba(125, 211, 184, 0.15);
                    color: #2A8C6E;
                    border: none;
                    border-radius: 12px;
                    font-size: 13px;
                    font-weight: 700;
                    text-align: left;
                    padding-left: 12px;
                }
            """
        return """
            QPushButton {
                background: transparent;
                color: #5A6E7A;
                border: none;
                border-radius: 12px;
                font-size: 13px;
                font-weight: 500;
                text-align: left;
                padding-left: 12px;
            }
            QPushButton:hover {
                background: rgba(125, 211, 184, 0.08);
                color: #2A8C6E;
            }
        """

    def _switch_tab(self, index: int):
        """
        Переключает видимую вкладку в QStackedWidget и подсвечивает кнопку в сайдбаре.

        index: 0 — флеш-карточки, 1 — тесты, 2 — переводчик, 3 — словарь, 4 — прогресс.
        """
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
            btn.setStyleSheet(self._nav_btn_style(i == index))

    def logout(self):
        """
        Сохраняет данные, закрывает окно и вызывает колбэк _on_logout (если задан в main.py).

        После этого приложение обычно снова показывает окно входа.
        """
        self.save_progress()
        self.close()
        if hasattr(self, '_on_logout'):
            self._on_logout()

    def update_progress_stats(self):
        """
        Обновляет отображение прогресса на всех связанных вкладках.

        Вызывается из flashcards_tab и quiz_tab после изучения слова или теста.
        """
        self.progress_tab.update_stats()
        self.vocabulary_tab.refresh_table()
        self._check_daily_goal_completion()

    def _check_daily_goal_completion(self):
        """
        Показывает поздравление, если дневная цель только что выполнена.

        Флаг _daily_goal_congratulated не даёт показать окно дважды за одну сессию.
        """
        daily = self._get_daily_progress()
        goal_done = (daily['words_done'] >= daily['words_target'] and
                     daily['tests_done'] >= daily['tests_target'])

        # Показываем только один раз за сессию (атрибут появляется при первом выполнении)
        if goal_done and not getattr(self, '_daily_goal_congratulated', False):
            self._daily_goal_congratulated = True
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setWindowTitle("🏆 Дневная цель выполнена!")
            msg.setText(
                f"<b>Отличная работа, {self.username}!</b><br><br>"
                f"Ты выучил {daily['words_target']} слов и прошёл {daily['tests_target']} тест(а) сегодня.<br>"
                "Так держать — ты на верном пути! 🚀"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox { background: #F7FAFA; }
                QLabel { color: #1A2C3E; font-size: 14px; }
                QPushButton { background: #7DD3B8; color: white; border-radius: 10px;
                              padding: 6px 20px; font-weight: 700; border: none; }
                QPushButton:hover { background: #3ABFA0; }
            """)
            msg.exec_()

    def apply_styles(self):
        """Применяет общие стили главного окна из utils/styles.py."""
        self.setStyleSheet(MAIN_WINDOW_STYLES)
