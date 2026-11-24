"""
welcome_dialog.py — всплывающее окно приветствия при входе в аккаунт.

Что делает этот файл:
    Показывает диалог с приветствием по имени, серией дней (🔥 streak) и прогрессом
    дневной цели (сколько слов и тестов сделано сегодня из запланированных).

Как вписывается в приложение:
    main_window.py вызывает его через QTimer.singleShot(200, ...) сразу после открытия
    главного окна — пользователь видит мотивацию перед работой с вкладками.

Ключевые понятия для начинающих:
    • QDialog — модальное окно поверх главного (блокирует его, пока не закроют).
    • parent=self — диалог «привязан» к главному окну (центрирование, иерархия).
    • accept() — стандартный способ закрыть диалог с результатом «ОК».
    • _day_word() — склонение «1 день / 2 дня / 5 дней» по правилам русского языка.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.styles import (HINT_TEXT_STYLE, TEXT_DARK_STYLE, TRANSPARENT_STYLE,
                          WELCOME_CONGRATS_STYLE, WELCOME_DIALOG_STYLE, WELCOME_GOAL_PCT_STYLE,
                          WELCOME_GOAL_TEXT_STYLE, WELCOME_GOAL_TITLE_STYLE, WELCOME_OK_BTN_STYLE,
                          WELCOME_STREAK_NUM_STYLE)


class WelcomeDialog(QDialog):
    """
    Модальное окно «Добро пожаловать» с серией дней и дневной целью.

    Не изменяет данные — только показывает информацию, переданную из main_window.
    """

    def __init__(self, username: str, streak: int, daily_goal: dict, parent=None):
        """
        Создаёт диалог приветствия.

        username — имя пользователя для надписи «Привет, ...».
        streak — число дней подряд входа в приложение.
        daily_goal — словарь: words_target, tests_target, words_done, tests_done.
        parent — главное окно (LanguageLearningApp), необязательно.
        """
        super().__init__(parent)
        self.username = username
        self.streak = streak
        self.daily_goal = daily_goal  # {'words_target': int, 'tests_target': int,
                                      #  'words_done': int, 'tests_done': int}
        self.setWindowTitle("Добро пожаловать!")
        self.setFixedSize(480, 480)
        # Убираем кнопку «?» в заголовке окна (справка Windows)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._init_ui()
        self._apply_styles()
        # Автозакрытие нет — пользователь закрывает сам кнопкой «Начать учиться»

    def _init_ui(self):
        """Собирает все элементы диалога: заголовок, блок серии, блок цели, кнопку."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(18)

        # ── Заголовок ──────────────────────────────────────────────────
        hi_lbl = QLabel(f"Привет, {self.username}! 👋")
        hi_lbl.setFont(QFont('Segoe UI', 22, QFont.Bold))
        hi_lbl.setAlignment(Qt.AlignCenter)
        hi_lbl.setStyleSheet(TEXT_DARK_STYLE)
        layout.addWidget(hi_lbl)

        # ── Серия дней ─────────────────────────────────────────────────
        streak_frame = QFrame()
        streak_frame.setObjectName("streakFrame")
        s_layout = QHBoxLayout(streak_frame)
        s_layout.setContentsMargins(20, 14, 20, 14)
        s_layout.setSpacing(14)

        fire_lbl = QLabel("🔥")
        fire_lbl.setFont(QFont('Segoe UI', 32))
        fire_lbl.setStyleSheet(TRANSPARENT_STYLE)
        s_layout.addWidget(fire_lbl)

        streak_text = QVBoxLayout()
        streak_text.setSpacing(2)

        day_word = self._day_word(self.streak)
        streak_num = QLabel(f"{self.streak} {day_word} подряд!")
        streak_num.setFont(QFont('Segoe UI', 18, QFont.Bold))
        streak_num.setStyleSheet(WELCOME_STREAK_NUM_STYLE)
        streak_text.addWidget(streak_num)

        streak_sub = QLabel("Продолжай — не прерывай серию!")
        streak_sub.setStyleSheet(HINT_TEXT_STYLE)
        streak_text.addWidget(streak_sub)

        s_layout.addLayout(streak_text)
        s_layout.addStretch()
        layout.addWidget(streak_frame)

        # ── Дневная цель ───────────────────────────────────────────────
        goal_frame = QFrame()
        goal_frame.setObjectName("goalFrame")
        g_layout = QVBoxLayout(goal_frame)
        g_layout.setContentsMargins(20, 14, 20, 14)
        g_layout.setSpacing(12)

        goal_title = QLabel("🎯  Цель на сегодня")
        goal_title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        goal_title.setStyleSheet(WELCOME_GOAL_TITLE_STYLE)
        g_layout.addWidget(goal_title)

        wt = self.daily_goal['words_target']
        wd = min(self.daily_goal['words_done'], wt)  # не показываем больше 100% на полоске
        tt = self.daily_goal['tests_target']
        td = min(self.daily_goal['tests_done'], tt)

        # Слова — подпись, процент и полоска прогресса
        w_row = QHBoxLayout()
        w_icon = QLabel("📖")
        w_icon.setFixedWidth(24)
        w_icon.setStyleSheet(TRANSPARENT_STYLE)
        w_row.addWidget(w_icon)
        w_lbl = QLabel(f"Слов: {wd} / {wt}")
        w_lbl.setStyleSheet(WELCOME_GOAL_TEXT_STYLE)
        w_row.addWidget(w_lbl)
        w_row.addStretch()
        w_pct = QLabel(f"{int(wd/wt*100) if wt else 0}%")
        w_pct.setStyleSheet(WELCOME_GOAL_PCT_STYLE)
        w_row.addWidget(w_pct)
        g_layout.addLayout(w_row)

        self.w_bar = QProgressBar()
        self.w_bar.setMaximum(wt)
        self.w_bar.setValue(wd)
        self.w_bar.setTextVisible(False)
        self.w_bar.setFixedHeight(8)
        g_layout.addWidget(self.w_bar)

        # Тесты — аналогично словам
        t_row = QHBoxLayout()
        t_icon = QLabel("✍")
        t_icon.setFixedWidth(24)
        t_icon.setStyleSheet(TRANSPARENT_STYLE)
        t_row.addWidget(t_icon)
        t_lbl = QLabel(f"Тестов: {td} / {tt}")
        t_lbl.setStyleSheet(WELCOME_GOAL_TEXT_STYLE)
        t_row.addWidget(t_lbl)
        t_row.addStretch()
        t_pct = QLabel(f"{int(td/tt*100) if tt else 0}%")
        t_pct.setStyleSheet(WELCOME_GOAL_PCT_STYLE)
        t_row.addWidget(t_pct)
        g_layout.addLayout(t_row)

        self.t_bar = QProgressBar()
        self.t_bar.setMaximum(tt)
        self.t_bar.setValue(td)
        self.t_bar.setTextVisible(False)
        self.t_bar.setFixedHeight(8)
        g_layout.addWidget(self.t_bar)

        layout.addWidget(goal_frame)

        # ── Поздравление (если цель выполнена) ────────────────────────
        goal_done = (wd >= wt and td >= tt)
        if goal_done:
            congrats_lbl = QLabel("🏆  Ты выполнил дневную цель! Молодец!")
            congrats_lbl.setAlignment(Qt.AlignCenter)
            congrats_lbl.setFont(QFont('Segoe UI', 13, QFont.Bold))
            congrats_lbl.setStyleSheet(WELCOME_CONGRATS_STYLE)
            layout.addWidget(congrats_lbl)
        else:
            layout.addSpacing(4)

        # ── Кнопка закрыть ─────────────────────────────────────────────
        ok_btn = QPushButton("Начать учиться! 🚀")
        ok_btn.setFixedHeight(48)
        ok_btn.setFont(QFont('Segoe UI', 13, QFont.Bold))
        ok_btn.setStyleSheet(WELCOME_OK_BTN_STYLE)
        ok_btn.clicked.connect(self.accept)  # закрывает диалог с кодом «принято»
        layout.addWidget(ok_btn)

    @staticmethod
    def _day_word(n: int) -> str:
        """
        Возвращает правильное слово для числа: «день», «дня» или «дней».

        Учитывает исключения 11–14 (всегда «дней») и последнюю цифру числа.
        """
        if n % 100 in range(11, 20):
            return "дней"
        r = n % 10
        if r == 1:
            return "день"
        if r in (2, 3, 4):
            return "дня"
        return "дней"

    def _apply_styles(self):
        """Задаёт фон диалога, рамки блоков и цвет заполнения QProgressBar."""
        self.setStyleSheet(WELCOME_DIALOG_STYLE)
