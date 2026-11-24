"""
=============================================================================
 styles.py — СТИЛИ ИНТЕРФЕЙСА (CSS для PyQt5)
=============================================================================

PyQt5 позволяет оформлять виджеты через CSS-подобные строки (setStyleSheet).

ВСЕ стили приложения лежат только здесь. В окнах (views/) нет ни одной
строки CSS — там только setStyleSheet(ИМЯ_СТИЛЯ). Чтобы поменять цвет,
не нужно искать его по всему коду.

Как устроен файл:
  LOGIN_STYLES, MAIN_WINDOW_STYLES — большие стили окон
  BTN_*_STYLE                     — кнопки разных типов
  QUIZ_*, CARD_*                  — тесты и карточки
  «Общие стили»                   — то, что повторяется на нескольких вкладках
  Дальше — разделы по вкладкам: CARDS_*, LOGIN_*, MAIN_*, PROGRESS_*,
  QUIZ_*, TRANSLATOR_*, VOCAB_*, WELCOME_*
  rank_*_style(color)             — функции, когда цвет меняется (звания)
"""

# ── Стили окна входа ──────────────────────────────────────────────────────
LOGIN_STYLES = """
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FF, stop:1 #F0F2FA);
        color: #1A2C3E;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    QLabel {
        font-size: 14px;
        color: #5A6E7A;
        font-family: 'Segoe UI', sans-serif;
    }
    QLineEdit {
        padding: 14px 18px;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        font-size: 14px;
        background-color: #FFFFFF;
        color: #1A2C3E;
        selection-background-color: #7DD3B8;
        font-family: 'Segoe UI', sans-serif;
    }
    QLineEdit:focus {
        border: 1.5px solid #7DD3B8;
        background-color: #FFFFFF;
    }
    QPushButton {
        background: #7DD3B8;
        color: #FFFFFF;
        border: none;
        padding: 14px 24px;
        font-size: 14px;
        border-radius: 40px;
        font-weight: 600;
        font-family: 'Segoe UI', sans-serif;
    }
    QPushButton:hover {
        background: #8FE3C8;
    }
    QPushButton:pressed {
        background: #6BC2A7;
    }
    QPushButton[objectName="secondary"] {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
    }
    QPushButton[objectName="secondary"]:hover {
        background: #F8FAFF;
        border-color: #7DD3B8;
        color: #6BC2A7;
    }
"""

# ── Стили главного окна (таблицы, вкладки, поля ввода) ─────────────────────
MAIN_WINDOW_STYLES = """
    QMainWindow, QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F8F9FF, stop:1 #F0F2FA);
        color: #1A2C3E;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    QTabWidget::pane {
        background: transparent;
        border: none;
    }
    QTabBar {
        background: transparent;
    }
    QTabBar::tab {
        background: transparent;
        color: #5A6E7A;
        padding: 12px 24px;
        margin-right: 8px;
        border-radius: 40px;
        font-size: 13px;
        font-weight: 500;
        border: none;
    }
    QTabBar::tab:selected {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1px solid #E2E8F0;
    }
    QTabBar::tab:hover:!selected {
        background: rgba(125, 211, 184, 0.1);
        color: #6BC2A7;
    }
    QPushButton {
        background: #7DD3B8;
        color: #FFFFFF;
        border: none;
        padding: 12px 24px;
        font-size: 13px;
        border-radius: 40px;
        font-weight: 600;
        font-family: 'Segoe UI', sans-serif;
    }
    QPushButton:hover {
        background: #8FE3C8;
    }
    QPushButton:pressed {
        background: #6BC2A7;
    }
    QPushButton:disabled {
        background: #E2E8F0;
        color: #9AAEB9;
        border: none;
    }
    QPushButton[objectName="secondary"] {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
    }
    QPushButton[objectName="secondary"]:hover {
        background: #F8FAFF;
        border-color: #7DD3B8;
        color: #6BC2A7;
    }
    QLineEdit {
        padding: 12px 18px;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        font-size: 13px;
        background-color: #FFFFFF;
        color: #1A2C3E;
        font-family: 'Segoe UI', sans-serif;
    }
    QLineEdit:focus {
        border-color: #7DD3B8;
        background-color: #FFFFFF;
    }
    QTextEdit {
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 12px;
        background-color: #FFFFFF;
        color: #1A2C3E;
        font-size: 13px;
    }
    QTextEdit:focus {
        border-color: #7DD3B8;
    }
    QGroupBox {
        font-weight: 600;
        font-size: 13px;
        color: #1A2C3E;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        margin-top: 16px;
        padding: 20px 16px 16px 16px;
        background-color: #FFFFFF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 20px;
        padding: 0 12px;
        color: #7DD3B8;
        font-size: 12px;
        font-weight: 700;
    }
    QTableWidget {
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        gridline-color: #F1F3F8;
        background-color: #FFFFFF;
        color: #1A2C3E;
        font-size: 13px;
        alternate-background-color: #F8F9FF;
        selection-background-color: rgba(125, 211, 184, 0.2);
        selection-color: #1A2C3E;
    }
    QTableWidget::item {
        padding: 12px 16px;
        border: none;
    }
    QTableWidget::item:selected {
        background-color: rgba(125, 211, 184, 0.2);
        color: #1A2C3E;
    }
    QHeaderView::section {
        background-color: #F8F9FF;
        color: #7DD3B8;
        padding: 12px 16px;
        border: none;
        border-bottom: 1px solid #E2E8F0;
        font-weight: 600;
        font-size: 12px;
    }
    QProgressBar {
        border: none;
        border-radius: 12px;
        background-color: #E2E8F0;
        text-align: center;
        height: 8px;
        color: transparent;
    }
    QProgressBar::chunk {
        background: #7DD3B8;
        border-radius: 12px;
    }
    QScrollBar:vertical {
        background: transparent;
        width: 6px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #C1CFD9;
        border-radius: 3px;
        min-height: 30px;
    }
    QScrollBar::handle:vertical:hover {
        background: #7DD3B8;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background: transparent;
        height: 6px;
        border-radius: 3px;
    }
    QScrollBar::handle:horizontal {
        background: #C1CFD9;
        border-radius: 3px;
        min-width: 30px;
    }
    QScrollBar::handle:horizontal:hover {
        background: #7DD3B8;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }
    QComboBox {
        background-color: #FFFFFF;
        color: #1A2C3E;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 10px 16px;
        font-size: 13px;
        min-height: 20px;
    }
    QComboBox:hover {
        border-color: #7DD3B8;
    }
    QComboBox::drop-down {
        border: none;
        width: 30px;
    }
    QComboBox QAbstractItemView {
        background-color: #FFFFFF;
        color: #1A2C3E;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        selection-background-color: rgba(125, 211, 184, 0.2);
        selection-color: #1A2C3E;
        outline: none;
        padding: 8px;
    }
    QSpinBox {
        background-color: #FFFFFF;
        color: #1A2C3E;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 8px 12px;
        font-size: 13px;
    }
    QSpinBox:focus {
        border-color: #7DD3B8;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        background-color: transparent;
        border: none;
        width: 24px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background-color: rgba(125, 211, 184, 0.1);
    }
    QRadioButton {
        color: #1A2C3E;
        font-size: 14px;
        spacing: 10px;
        padding: 8px 0;
    }
    QRadioButton::indicator {
        width: 20px;
        height: 20px;
        border-radius: 10px;
        border: 2px solid #C1CFD9;
        background-color: #FFFFFF;
    }
    QRadioButton::indicator:checked {
        border: 2px solid #7DD3B8;
        background-color: #7DD3B8;
    }
    QRadioButton::indicator:hover {
        border-color: #7DD3B8;
    }
    QLabel {
        color: #1A2C3E;
        font-family: 'Segoe UI', sans-serif;
    }
    QMessageBox {
        background-color: #FFFFFF;
        color: #1A2C3E;
        border-radius: 24px;
    }
    QMessageBox QPushButton {
        min-width: 80px;
        padding: 10px 24px;
        border-radius: 40px;
    }
"""

# ── Стили флеш-карточек ───────────────────────────────────────────────────
CARD_FRONT_STYLE = """
    background: #FFFFFF;
    border-radius: 32px;
    padding: 40px;
    border: 1px solid #E2E8F0;
"""
CARD_WORD_STYLE = """
    color: #1A2C3E;
    font-size: 36px;
    font-weight: 700;
    letter-spacing: -0.5px;
"""
CARD_TRANSLATION_STYLE = """
    color: #7DD3B8;
    font-size: 24px;
    font-weight: 600;
"""

# ── Стили тестов: правильный / неправильный / обычный ответ ───────────────
QUIZ_CORRECT_STYLE = """
    background-color: #E8F5F0;
    border: 1px solid #7DD3B8;
    border-radius: 20px;
    color: #2A8C6E;
    font-size: 14px;
    padding: 12px 18px;
"""
QUIZ_WRONG_STYLE = """
    background-color: #FFF0F0;
    border: 1px solid #FFB8B8;
    border-radius: 20px;
    color: #E87A7A;
    font-size: 14px;
    padding: 12px 18px;
"""
QUIZ_NORMAL_STYLE = """
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    color: #1A2C3E;
    font-size: 14px;
    padding: 12px 18px;
"""
QUIZ_QUESTION_STYLE = """
    background: #FFFFFF;
    border-radius: 28px;
    padding: 28px;
    border: 1px solid #E2E8F0;
    font-size: 22px;
    font-weight: 700;
    color: #1A2C3E;
"""

# ── Стили кнопок: зелёная (успех), золотая, вторичная ─────────────────────
BTN_SUCCESS_STYLE = """
    QPushButton {
        background: #7DD3B8;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 13px;
        border-radius: 40px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #8FE3C8;
    }
    QPushButton:disabled {
        background: #E2E8F0;
        color: #9AAEB9;
    }
"""
BTN_GOLD_STYLE = """
    QPushButton {
        background: #F5B841;
        color: #FFFFFF;
        border: none;
        padding: 12px 24px;
        font-size: 13px;
        border-radius: 40px;
        font-weight: 700;
    }
    QPushButton:hover {
        background: #F7C35C;
    }
    QPushButton:disabled {
        background: #E2E8F0;
        color: #9AAEB9;
    }
"""
BTN_SECONDARY_STYLE = """
    QPushButton {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
        padding: 12px 24px;
        font-size: 13px;
        border-radius: 40px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #F8FAFF;
        color: #6BC2A7;
        border-color: #7DD3B8;
    }
    QPushButton:disabled {
        color: #C1CFD9;
        border-color: #E2E8F0;
    }
"""
# ── Карточки статистики на вкладке «Прогресс» ─────────────────────────────
STAT_CARD_STYLE = """
    background: #FFFFFF;
    border-radius: 28px;
    border: 1px solid #E2E8F0;
    padding: 24px;
"""


# ── Общие стили (используются на нескольких вкладках) ─────────────────────
# зелёная кнопка «Начать»
BTN_START_STYLE = """
    QPushButton {
        background-color: #7DD3B8;
        color: white;
        border: none;
        padding: 12px 22px;
        font-size: 14px;
        border-radius: 40px;
        font-weight: 700;
        }QPushButton:hover { background-color: #8FE3C8;
        }QPushButton:pressed { background-color: #6BC2A7;
        }QPushButton:disabled { background-color: #E2E8F0;
        color: #9AAEB9;
        border: none;
    }
"""

# красная кнопка «Стоп»
BTN_STOP_STYLE = """
    QPushButton {
        background-color: #E87A7A;
        color: white;
        border: none;
        padding: 12px 22px;
        font-size: 14px;
        border-radius: 40px;
        font-weight: 700;
        }QPushButton:hover { background-color: #F08080;
        }QPushButton:pressed { background-color: #D06060;
        }QPushButton:disabled { background-color: #E2E8F0;
        color: #9AAEB9;
        border: none;
    }
"""

# белая карточка (радиус 20)
CARD_FRAME_STYLE = """
    QFrame {
        background: #FFFFFF;
        border-radius: 20px;
        border: 1.5px solid #E2E8F0;
    }
"""

# счётчик «Карточка 1 из 10», «Вопрос 1 из 10»
COUNTER_STYLE = "color: #9B9FC4; font-size: 13px;"

# карточка с зелёным градиентом
GRADIENT_FRAME_STYLE = """
    QFrame {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #F0FBF7, stop:1 #E8F5F0);
        border-radius: 20px;
        border: 1.5px solid #7DD3B8;
    }
"""

# серый текст
GREY_TEXT_STYLE = "color: #5A6E7A; font-size: 13px; border: none; background: transparent;"

# серая мелкая подсказка
HINT_TEXT_STYLE = "color: #5A6E7A; font-size: 12px; border: none; background: transparent;"

# заголовок вкладки
PAGE_TITLE_STYLE = "color: #1A2C3E; margin-bottom: 4px;"

# белая панель (радиус 16)
PANEL_FRAME_STYLE = """
    QFrame {
        background-color: #FFFFFF;
        border-radius: 16px;
        border: 1.5px solid #E2E8F0;
    }
"""

# зелёная подпись раздела
SECTION_CAPTION_STYLE = "color: #7DD3B8; border: none; background: transparent; letter-spacing: 1px;"

# тёмный текст
TEXT_DARK_STYLE = "color: #1A2C3E;"

# без рамки и фона (иконки, подписи на карточках)
TRANSPARENT_STYLE = "border: none; background: transparent;"

# светлое окно-сообщение (QMessageBox) на вкладках
LIGHT_MSG_STYLE = """
    QMessageBox { background-color: #F8F9FF; color: #1A2C3E; }
    QLabel { color: #1A2C3E; font-size: 14px; }
    QPushButton {
        background: #7DD3B8; color: white; border: none;
        padding: 8px 24px; border-radius: 20px; font-weight: 600; min-width: 80px;
    }
    QPushButton:hover { background: #8FE3C8; }
"""


# ── Вкладка/окно: Флеш-карточки ───────────────────────────────────────────
CARDS_DONE_FRAME_STYLE = """
    QFrame {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #E8F5F0, stop:1 #D4EEE5);
        border-radius: 20px;
        border: 1.5px solid #7DD3B8;
    }
"""

CARDS_TIMER_BTN_STYLE = """
    QPushButton {
        background-color: #E2E8F0;
        color: #5A6E7A;
        border: none;
        padding: 4px 10px;
        font-size: 11px;
        border-radius: 14px;
        font-weight: 600;
        }QPushButton:hover { background-color: #CBD5E0;
    }
"""

CARDS_TIME_STYLE = """
    QLabel {
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        background: #FFFFFF;
        font-family: 'Segoe UI', monospace;
        font-size: 24px;
        font-weight: bold;
        color: #1A2C3E;
    }
"""

CARDS_BIG_WORD_STYLE = "color: #1A2C3E; letter-spacing: 2px; border: none; background: transparent;"

CARD_TRANSLATION_FLAT_STYLE = CARD_TRANSLATION_STYLE + " border: none; background: transparent;"


# ── Вкладка/окно: Окно входа ──────────────────────────────────────────────
LOGIN_ERROR_STYLE = "color: #F44336; font-size: 12px;"

LOGIN_SUBTITLE_STYLE = "color: #757575; font-size: 13px;"

LOGIN_SUCCESS_STYLE = "color: #4CAF50; font-size: 12px;"

# общий стиль входа + кнопка-глаз и галочка «Запомнить меня»
LOGIN_WINDOW_STYLE = LOGIN_STYLES + """
    QPushButton#eyeBtn {
          background: #EEF6F3;
          border: 1.5px solid #E2E8F0;
          border-radius: 10px;
          font-size: 18px;
          padding: 0px;
          color: #5A6E7A;
      }
      QPushButton#eyeBtn:hover {
          background: #D4F0E8;
          color: #2A8C6E;
      }
      QCheckBox#rememberCheck {
          font-size: 13px;
          color: #5A6E7A;
          spacing: 8px;
      }
      QCheckBox#rememberCheck::indicator {
          width: 18px;
          height: 18px;
          border: 1.5px solid #E2E8F0;
          border-radius: 5px;
          background: #FFFFFF;
      }
      QCheckBox#rememberCheck::indicator:checked {
          background: #7DD3B8;
          border-color: #7DD3B8;
          image: none;
      }
      QCheckBox#rememberCheck::indicator:hover {
          border-color: #7DD3B8;
      }
"""


# ── Вкладка/окно: Главное окно ────────────────────────────────────────────
MAIN_GOAL_MSG_STYLE = """
    QMessageBox { background: #F7FAFA; }
    QLabel { color: #1A2C3E; font-size: 14px; }
    QPushButton { background: #7DD3B8; color: white; border-radius: 10px;
                  padding: 6px 20px; font-weight: 700; border: none; }
    QPushButton:hover { background: #3ABFA0; }
"""

MAIN_HEADER_STYLE = """
    QWidget#headerBar {
        background: #FFFFFF;
        border-bottom: 1px solid #E2E8F0;
    }
"""

MAIN_LOGOUT_BTN_STYLE = """
    QPushButton { background-color: #5A6E7A; color: white; border-radius: 16px;
                  padding: 6px 12px; font-size: 12px; font-weight: 600; }
    QPushButton:hover { background-color: #4A5E6A; }
"""

MAIN_SIDEBAR_STYLE = """
    QWidget#sidebar {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
"""

MAIN_STACK_STYLE = "background: transparent;"

MAIN_USER_STYLE = "color: #5A6E7A; font-size: 13px; font-weight: 600; margin-right: 12px;"

MAIN_WORD_COUNT_STYLE = "color: #7DD3B8; font-size: 13px; font-weight: 600; margin-right: 16px;"

# кнопка бокового меню: текущая вкладка
NAV_BTN_ACTIVE_STYLE = """
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

# кнопка бокового меню: обычная
NAV_BTN_STYLE = """
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


# ── Вкладка/окно: Прогресс ────────────────────────────────────────────────
PROGRESS_BIG_TEXT_STYLE = "color: #1A2C3E; border: none; background: transparent;"

PROGRESS_CARD_STYLE = """
    QFrame {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1.5px solid #E2E8F0;
    }
"""

PROGRESS_CHECK_DONE_STYLE = "color: #7DD3B8; font-weight: bold; border: none; background: transparent;"

PROGRESS_DAILY_CONGRATS_STYLE = "color: #FFFFFF; background: #3ABFA0; border-radius: 8px; padding: 4px; border: none;"

PROGRESS_GOAL_BAR_STYLE = """
    QProgressBar { background: #E2E8F0; border-radius: 3px; border: none; }
    QProgressBar::chunk { background: #7DD3B8; border-radius: 3px; }
"""

PROGRESS_GOAL_TEXT_STYLE = "color: #1A2C3E; font-size: 12px; font-weight: 600; border: none; background: transparent;"

PROGRESS_PROG_TITLE_STYLE = """
    color: #7DD3B8; border: none; background: transparent;
    font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
"""

PROGRESS_RANKS_TITLE_STYLE = """
    color: #7DD3B8; border: none; background: transparent; font-size: 11px; letter-spacing: 1px;
"""

PROGRESS_RANK_HEADER_STYLE = """
    color: #7DD3B8; font-size: 11px; font-weight: 700; letter-spacing: 1px; border: none; background: transparent;
"""

PROGRESS_REQ_DONE_STYLE = "color: #7DD3B8; font-size: 11px; border: none; background: transparent;"

PROGRESS_REQ_LOCKED_STYLE = "color: #C1CFD9; font-size: 11px; border: none; background: transparent;"

PROGRESS_REQ_STYLE = "color: #9AAEB9; font-size: 11px; border: none; background: transparent;"

PROGRESS_STREAK_CARD_STYLE = """
    QFrame {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #FFF5EF, stop:1 #FFE8DA);
        border-radius: 16px;
        border: 1.5px solid #F5B89A;
    }
"""

PROGRESS_STREAK_SUB_STYLE = "color: #5A6E7A; font-size: 11px; border: none; background: transparent;"

PROGRESS_STREAK_TITLE_STYLE = "color: #F5824A; border: none; background: transparent; letter-spacing: 1px;"

PROGRESS_VALUE_STYLE = "color: #7DD3B8; border: none; background: transparent;"

PROGRESS_VAL_ACCURACY_STYLE = ("color: #F5B841; font-size: 22px; font-weight: 700; "
                               "border: none; background: transparent;")

# звание, которое ещё не получено
PROGRESS_RANK_LOCKED_STYLE = "color: #C1CFD9; font-size: 12px; font-weight: 600; border: none; background: transparent;"


# Цвет звания разный, поэтому здесь функции: передаём цвет — получаем стиль.
def rank_name_style(color):
    """Название звания в таблице званий."""
    return f"color: {color}; border: none; background: transparent;"


def rank_title_style(color):
    """Большое название текущего звания."""
    return f"color: {color}; font-size: 20px; font-weight: 700; border: none; background: transparent;"


def rank_done_style(color):
    """Полученное звание в таблице."""
    return f"color: {color}; font-size: 12px; font-weight: 700; border: none; background: transparent;"


# ── Вкладка/окно: Тесты ───────────────────────────────────────────────────
QUIZ_QUESTION_BOX_STYLE = """
    background: #FFFFFF;border-radius: 16px; padding: 22px; border: 1.5px solid #E2E8F0; color: #1A2C3E;
"""

QUIZ_RESULT_BAD_STYLE = "color: #E87A7A; font-weight: bold; font-size: 15px;"

QUIZ_RESULT_OK_STYLE = "color: #2A8C6E; font-weight: bold; font-size: 15px;"

QUIZ_TIMER_STYLE = """
    color: #E87A7A; background-color: #FFF0F0; padding: 10px; border-radius: 16px; border: 1.5px solid #FFB8B8;
"""

QUIZ_TIMER_URGENT_STYLE = """
    color: white; background: #E87A7A; padding: 10px;
    border-radius: 16px; font-weight: bold; border: 1.5px solid #E87A7A;
"""

QUIZ_WOD_ENGLISH_STYLE = "color: #1A2C3E; border: none; background: transparent; letter-spacing: 2px;"

QUIZ_WOD_HINT_STYLE = "color: #9AAEB9; border: none; background: transparent; margin-top: 6px;"

QUIZ_WOD_RUSSIAN_STYLE = "color: #7DD3B8; border: none; background: transparent; font-weight: 600;"


# ── Вкладка/окно: Переводчик ──────────────────────────────────────────────
TRANSLATOR_STYLE = """
    QWidget {
        background: transparent;
        color: #1A2C3E;
        font-family: 'Segoe UI', sans-serif;
    }
    QTextEdit {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
        padding: 14px;
        font-size: 15px;
        color: #1A2C3E;
        font-family: 'Segoe UI', sans-serif;
        selection-background-color: #7DD3B8;
    }
    QTextEdit:focus {
        border: 1.5px solid #7DD3B8;
    }
    QTextEdit[readOnly="true"] {
        background-color: #F8F9FF;
        color: #1A2C3E;
    }
    QPushButton#translateBtn {
        background: #7DD3B8;
        color: #FFFFFF;
        border: none;
        padding: 12px 36px;
        font-size: 14px;
        border-radius: 40px;
        font-weight: 600;
    }
    QPushButton#translateBtn:hover {
        background: #8FE3C8;
    }
    QPushButton#translateBtn:pressed {
        background: #6BC2A7;
    }
    QPushButton#swapBtn {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
        padding: 8px 16px;
        font-size: 18px;
        border-radius: 20px;
        font-weight: 600;
        min-width: 48px;
        max-width: 48px;
        min-height: 48px;
        max-height: 48px;
    }
    QPushButton#swapBtn:hover {
        background: #F0FBF7;
        border-color: #7DD3B8;
    }
    QPushButton#clearHistoryBtn {
        background: transparent;
        color: #B0BEC5;
        border: 1px solid #E2E8F0;
        padding: 4px 14px;
        font-size: 12px;
        border-radius: 12px;
    }
    QPushButton#clearHistoryBtn:hover {
        color: #EF5350;
        border-color: #EF5350;
    }
    QLabel#langLabel {
        font-size: 12px;
        font-weight: 600;
        color: #7DD3B8;
        letter-spacing: 1px;
    }
    QLabel#titleLabel {
        font-size: 18px;
        font-weight: 700;
        color: #1A2C3E;
    }
    QLabel#historyTitle {
        font-size: 13px;
        font-weight: 600;
        color: #5A6E7A;
        letter-spacing: 0.5px;
    }
    QFrame#card {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
    }
    QFrame#historyCard {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 16px;
    }
    QTextEdit#historyBox {
        background-color: transparent;
        border: none;
        font-size: 13px;
        color: #5A6E7A;
        font-family: 'Segoe UI', sans-serif;
    }
    QTextEdit#historyBox:focus {
        border: none;
    }
"""


# ── Вкладка/окно: Словарь ─────────────────────────────────────────────────
VOCAB_ROW_HEADER_STYLE = """
    QHeaderView::section {
        background-color: #F8F9FF;
        color: #5A6E7A;
        padding: 6px 10px;
        border: none;
        border-right: 1px solid #E2E8F0;
        font-size: 12px;
        font-weight: 500;
    }
"""

VOCAB_SAVED_MSG_STYLE = """
    QMessageBox {
        background-color: #F8F9FF;
        color: #1A2C3E;
    }
    QLabel { color: #1A2C3E; font-size: 14px; }
    QPushButton {
        background: #7DD3B8; color: white; border: none;
        padding: 8px 24px; border-radius: 20px; font-weight: 600;
        min-width: 80px;
    }
    QPushButton:hover { background: #8FE3C8; }
"""

VOCAB_SEARCH_STYLE = "color: #5A6E7A; font-size: 13px; font-weight: 600;"

VOCAB_ADD_DIALOG_STYLE = """
    QDialog {
        background-color: #F8F9FF;
        color: #1A2C3E;
    }
    QLabel {
        color: #1A2C3E;
        font-size: 13px;
    }
    QLineEdit {
        padding: 10px 14px;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        font-size: 13px;
        background-color: #FFFFFF;
        color: #1A2C3E;
    }
    QLineEdit:focus {
        border-color: #7DD3B8;
    }
    QPushButton {
        background: #7DD3B8;
        color: #FFFFFF;
        border: none;
        padding: 10px 22px;
        font-size: 13px;
        border-radius: 20px;
        font-weight: 600;
    }
    QPushButton:hover { background: #8FE3C8; }
    QPushButton:pressed { background: #6BC2A7; }
    QPushButton[objectName="cancel"] {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
    }
    QPushButton[objectName="cancel"]:hover {
        background: #F8FAFF;
        border-color: #7DD3B8;
    }
"""

BTN_VOCAB_STYLE = """
    QPushButton {
        background: #FFFFFF;
        color: #7DD3B8;
        border: 1.5px solid #E2E8F0;
        padding: 10px 20px;
        font-size: 13px;
        border-radius: 20px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: #F0FBF7;
        border-color: #7DD3B8;
        color: #6BC2A7;
    }
    QPushButton:pressed { background: #E8F5F0; }
"""

# левый верхний угол таблицы (без чёрного квадрата)
VOCAB_TABLE_CORNER_STYLE = """
    QAbstractScrollArea::corner {
        background-color: #F8F9FF;
        border: none;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }
"""


# ── Вкладка/окно: Окно приветствия ────────────────────────────────────────
WELCOME_CONGRATS_STYLE = "color: #FFFFFF; background: #3ABFA0; border-radius: 12px; padding: 10px;"

WELCOME_DIALOG_STYLE = """
    QDialog {
        background: #F7FAFA;
    }
    QFrame#streakFrame {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
            stop:0 #FFF5EF, stop:1 #FFE8DA);
        border-radius: 16px;
        border: 1.5px solid #F5B89A;
    }
    QFrame#goalFrame {
        background: #FFFFFF;
        border-radius: 16px;
        border: 1.5px solid #E2E8F0;
    }
    QProgressBar {
        background: #E2E8F0;
        border-radius: 4px;
        border: none;
    }
    QProgressBar::chunk {
        background: #7DD3B8;
        border-radius: 4px;
    }
"""

WELCOME_GOAL_PCT_STYLE = "color: #7DD3B8; font-weight: 700; border: none; background: transparent;"

WELCOME_GOAL_TEXT_STYLE = "color: #1A2C3E; font-size: 13px; font-weight: 600; border: none; background: transparent;"

WELCOME_GOAL_TITLE_STYLE = "color: #7DD3B8; letter-spacing: 1px; border: none; background: transparent;"

WELCOME_OK_BTN_STYLE = """
    QPushButton {
        background: #7DD3B8;
        color: white;
        border: none;
        border-radius: 14px;
    }
    QPushButton:hover { background: #3ABFA0; }
"""

WELCOME_STREAK_NUM_STYLE = "color: #F5824A; border: none; background: transparent;"
