"""
Вкладка со словарем
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.styles import BTN_SUCCESS_STYLE, BTN_SECONDARY_STYLE

DIALOG_STYLE = """
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


class VocabularyTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.init_ui()
        self.refresh_table()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(12)
        self.setLayout(layout)

        title = QLabel("📖 Мой словарь")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1A2C3E; margin-bottom: 4px;")
        layout.addWidget(title)

        # Поиск
        search_layout = QHBoxLayout()
        search_lbl = QLabel("Поиск:")
        search_lbl.setStyleSheet("color: #5A6E7A; font-size: 13px; font-weight: 600;")
        search_layout.addWidget(search_lbl)
        self.vocab_search = QLineEdit()
        self.vocab_search.setPlaceholderText("Введите слово для поиска...")
        self.vocab_search.textChanged.connect(self.filter_vocabulary)
        search_layout.addWidget(self.vocab_search)
        layout.addLayout(search_layout)

        # Таблица — убираем чёрный квадрат corner widget
        self.vocab_table = QTableWidget()
        self.vocab_table.setColumnCount(3)
        self.vocab_table.setHorizontalHeaderLabels(["English", "Русский", "Статус"])
        self.vocab_table.horizontalHeader().setStretchLastSection(True)
        # Corner (верхний левый квадрат между заголовками)
        self.vocab_table.setCornerButtonEnabled(False)
        self.vocab_table.setStyleSheet(self.vocab_table.styleSheet() + """
            QAbstractScrollArea::corner {
                background-color: #F8F9FF;
                border: none;
                border-right: 1px solid #E2E8F0;
                border-bottom: 1px solid #E2E8F0;
            }
        """)
        self.vocab_table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #F8F9FF;
                color: #5A6E7A;
                padding: 6px 10px;
                border: none;
                border-right: 1px solid #E2E8F0;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        layout.addWidget(self.vocab_table)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        add_word_btn = QPushButton("➕  Добавить слово")
        add_word_btn.setStyleSheet(BTN_VOCAB_STYLE)
        add_word_btn.clicked.connect(self.show_add_word_dialog)
        button_layout.addWidget(add_word_btn)

        refresh_btn = QPushButton("🔄  Обновить")
        refresh_btn.setStyleSheet(BTN_VOCAB_STYLE)
        refresh_btn.clicked.connect(self.refresh_table)
        button_layout.addWidget(refresh_btn)

        save_btn = QPushButton("💾  Сохранить")
        save_btn.setStyleSheet(BTN_SUCCESS_STYLE)
        save_btn.clicked.connect(self.manual_save)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def refresh_table(self):
        self.vocab_table.setRowCount(len(self.main.vocabulary))
        for i, word in enumerate(self.main.vocabulary):
            self.vocab_table.setItem(i, 0, QTableWidgetItem(word['english']))
            self.vocab_table.setItem(i, 1, QTableWidgetItem(word['russian']))
            status = "✓ Изучено" if self.main.is_word_learned(word['english']) else "○ Не изучено"
            self.vocab_table.setItem(i, 2, QTableWidgetItem(status))

    def filter_vocabulary(self):
        search_text = self.vocab_search.text().lower()
        for i in range(self.vocab_table.rowCount()):
            english = self.vocab_table.item(i, 0).text().lower()
            russian = self.vocab_table.item(i, 1).text().lower()
            self.vocab_table.setRowHidden(i, search_text not in english and search_text not in russian)

    def show_add_word_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новое слово")
        dialog.setModal(True)
        dialog.setMinimumWidth(320)
        dialog.setStyleSheet(DIALOG_STYLE)

        layout = QFormLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        english_input = QLineEdit()
        russian_input = QLineEdit()
        layout.addRow("English:", english_input)
        layout.addRow("Русский:", russian_input)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        add_btn = QPushButton("Добавить")
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("cancel")
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        dialog.setLayout(layout)

        def add_word():
            eng = english_input.text().strip()
            rus = russian_input.text().strip()
            if eng and rus:
                try:
                    self.main.add_word(eng, rus)
                    dialog.accept()
                except Exception:
                    QMessageBox.warning(dialog, "Ошибка", "Такое слово уже есть в словаре.")
            else:
                QMessageBox.warning(dialog, "Ошибка", "Заполните оба поля!")

        add_btn.clicked.connect(add_word)
        cancel_btn.clicked.connect(dialog.reject)
        dialog.exec_()

    def manual_save(self):
        self.main.save_progress()
        self.main.save_progress()
        # Светлый диалог сохранения
        msg = QMessageBox(self)
        msg.setWindowTitle("Сохранено")
        msg.setText("Словарь и прогресс успешно сохранены!")
        msg.setIcon(QMessageBox.NoIcon)
        msg.setStyleSheet("""
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
        """)
        msg.exec_()