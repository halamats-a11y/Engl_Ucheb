"""
=============================================================================
 styles.py — СТИЛИ ИНТЕРФЕЙСА (CSS для PyQt5)
=============================================================================

PyQt5 позволяет оформлять виджеты через CSS-подобные строки (setStyleSheet).

В этом файле собраны все стили приложения в одном месте — так проще
менять цвета и не искать их по всему коду.

Основные переменные:
  LOGIN_STYLES         — окно входа
  MAIN_WINDOW_STYLES   — главное окно, таблицы, поля
  BTN_*_STYLE          — кнопки разных типов
  QUIZ_*_STYLE         — подсветка ответов в тестах
  CARD_*_STYLE         — карточки флеш-карточек
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