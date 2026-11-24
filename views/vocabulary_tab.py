"""
Вкладка со словарем
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.styles import (BTN_SUCCESS_STYLE, BTN_VOCAB_STYLE, PAGE_TITLE_STYLE,
                          VOCAB_ADD_DIALOG_STYLE, VOCAB_ROW_HEADER_STYLE, VOCAB_SAVED_MSG_STYLE,
                          VOCAB_SEARCH_STYLE, VOCAB_TABLE_CORNER_STYLE)


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
        title.setStyleSheet(PAGE_TITLE_STYLE)
        layout.addWidget(title)

        # Поиск
        search_layout = QHBoxLayout()
        search_lbl = QLabel("Поиск:")
        search_lbl.setStyleSheet(VOCAB_SEARCH_STYLE)
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
        self.vocab_table.setStyleSheet(self.vocab_table.styleSheet() + VOCAB_TABLE_CORNER_STYLE)
        self.vocab_table.verticalHeader().setStyleSheet(VOCAB_ROW_HEADER_STYLE)
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
            status = "✓ Изучено" if self.main.is_word_learned(word) else "○ Не изучено"
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
        dialog.setStyleSheet(VOCAB_ADD_DIALOG_STYLE)

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
        # Светлый диалог сохранения
        msg = QMessageBox(self)
        msg.setWindowTitle("Сохранено")
        msg.setText("Словарь и прогресс успешно сохранены!")
        msg.setIcon(QMessageBox.NoIcon)
        msg.setStyleSheet(VOCAB_SAVED_MSG_STYLE)
        msg.exec_()
