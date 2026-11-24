"""
Вкладка переводчика — новый дизайн
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTextEdit, QFrame)
from PyQt5.QtCore import Qt
from datetime import datetime
from styles import TRANSLATOR_STYLE


class TranslatorTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.direction = "en_ru"   # en_ru или ru_en
        self.history = []          # список переводов за сессию
        self.init_ui()
        self.setStyleSheet(TRANSLATOR_STYLE)

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)

        # ── Заголовок ──────────────────────────────────────────────
        title = QLabel("🔄 Переводчик")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # ── Два поля + кнопка смены ─────────────────────────────────
        fields_layout = QHBoxLayout()
        fields_layout.setSpacing(12)

        # Левое поле (ввод)
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        self.left_lang_label = QLabel("АНГЛИЙСКИЙ")
        self.left_lang_label.setObjectName("langLabel")
        self.left_lang_label.setAlignment(Qt.AlignCenter)
        left_col.addWidget(self.left_lang_label)
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Введите слово или фразу...")
        self.input_field.setMinimumHeight(120)
        self.input_field.setMaximumHeight(160)
        left_col.addWidget(self.input_field)
        fields_layout.addLayout(left_col)

        # Кнопка смены направления
        swap_col = QVBoxLayout()
        swap_col.setAlignment(Qt.AlignCenter)
        swap_col.addSpacing(28)
        self.swap_btn = QPushButton("⇌")
        self.swap_btn.setObjectName("swapBtn")
        self.swap_btn.setToolTip("Сменить направление")
        self.swap_btn.clicked.connect(self.swap_direction)
        swap_col.addWidget(self.swap_btn)
        fields_layout.addLayout(swap_col)

        # Правое поле (результат)
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        self.right_lang_label = QLabel("РУССКИЙ")
        self.right_lang_label.setObjectName("langLabel")
        self.right_lang_label.setAlignment(Qt.AlignCenter)
        right_col.addWidget(self.right_lang_label)
        self.result_field = QTextEdit()
        self.result_field.setReadOnly(True)
        self.result_field.setPlaceholderText("Перевод появится здесь...")
        self.result_field.setMinimumHeight(120)
        self.result_field.setMaximumHeight(160)
        right_col.addWidget(self.result_field)
        fields_layout.addLayout(right_col)

        root.addLayout(fields_layout)

        # ── Кнопка Перевести ────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        translate_btn = QPushButton("🔍 Перевести")
        translate_btn.setObjectName("translateBtn")
        translate_btn.clicked.connect(self.translate_word)
        self.input_field.installEventFilter(self)
        btn_row.addWidget(translate_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # ── История ─────────────────────────────────────────────────
        history_header = QHBoxLayout()
        history_title = QLabel("📋 ИСТОРИЯ ПЕРЕВОДОВ")
        history_title.setObjectName("historyTitle")
        history_header.addWidget(history_title)
        history_header.addStretch()
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("clearHistoryBtn")
        self.clear_btn.clicked.connect(self.clear_history)
        history_header.addWidget(self.clear_btn)
        root.addLayout(history_header)

        history_frame = QFrame()
        history_frame.setObjectName("historyCard")
        history_frame_layout = QVBoxLayout(history_frame)
        history_frame_layout.setContentsMargins(8, 8, 8, 8)
        self.history_box = QTextEdit()
        self.history_box.setObjectName("historyBox")
        self.history_box.setReadOnly(True)
        self.history_box.setPlaceholderText("История переводов пуста...")
        self.history_box.setMinimumHeight(140)
        history_frame_layout.addWidget(self.history_box)
        root.addWidget(history_frame)

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent
        from PyQt5.QtCore import Qt
        if obj == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self.translate_word()
                return True
        return super().eventFilter(obj, event)

    def swap_direction(self):
        if self.direction == "en_ru":
            self.direction = "ru_en"
            self.left_lang_label.setText("РУССКИЙ")
            self.right_lang_label.setText("АНГЛИЙСКИЙ")
        else:
            self.direction = "en_ru"
            self.left_lang_label.setText("АНГЛИЙСКИЙ")
            self.right_lang_label.setText("РУССКИЙ")
        self.input_field.clear()
        self.result_field.clear()

    def translate_word(self):
        word = self.input_field.toPlainText().strip().lower()
        if not word:
            self.result_field.setPlainText("Введите слово для перевода")
            return

        found = False
        result_text = ""

        if self.direction == "en_ru":
            matches = [v for v in self.main.vocabulary if v['english'].lower() == word]
            if matches:
                result_text = matches[0]['russian']
                history_entry = f"{matches[0]['english']} → {matches[0]['russian']}"
                found = True
        else:
            matches = [v for v in self.main.vocabulary if v['russian'].lower() == word]
            if matches:
                result_text = matches[0]['english']
                history_entry = f"{matches[0]['russian']} → {matches[0]['english']}"
                found = True

        if found:
            self.result_field.setPlainText(result_text)
            # Добавляем в историю
            time_str = datetime.now().strftime("%H:%M")
            self.history.append(f"[{time_str}]  {history_entry}")
            self._refresh_history()
        else:
            self.result_field.setPlainText(f"❌ Слово «{word}» не найдено в словаре")

    def _refresh_history(self):
        if not self.history:
            self.history_box.setPlainText("")
            return
        # Показываем последние записи сверху
        self.history_box.setPlainText("\n".join(reversed(self.history)))

    def clear_history(self):
        self.history.clear()
        self.history_box.setPlainText("")
