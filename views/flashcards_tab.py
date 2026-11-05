"""
Вкладка с флеш-карточками для изучения слов
"""
import os
import random
import sys
import time
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QPixmap
from utils.styles import (BTN_SECONDARY_STYLE, BTN_GOLD_STYLE,
                          BTN_SUCCESS_STYLE, CARD_TRANSLATION_STYLE)

LIGHT_MSG_STYLE = """
    QMessageBox { background-color: #F8F9FF; color: #1A2C3E; }
    QLabel { color: #1A2C3E; font-size: 14px; }
    QPushButton {
        background: #7DD3B8; color: white; border: none;
        padding: 8px 24px; border-radius: 20px; font-weight: 600; min-width: 80px;
    }
    QPushButton:hover { background: #8FE3C8; }
"""


class FlashcardsTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.current_card_index = 0
        self.cards_to_study = []
        self.card_flipped = False
        self.timer_paused = False
        self.elapsed_before_pause = 0
        self.init_ui()
        self.start_time = time.time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Обновление каждую секунду

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.setLayout(layout)


        # Верхняя строка: таймер слева + заголовок + счётчик
        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.setContentsMargins(0, 0, 0, 0)

        # Компактный счётчик времени с кнопками пауза/стоп
        timer_container = QWidget()
        timer_col = QVBoxLayout(timer_container)
        timer_col.setSpacing(6)
        timer_col.setContentsMargins(0, 0, 0, 0)
        timer_col.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel("00:00")
        self.time_label.setFixedSize(150, 50)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                border: 1.5px solid #E2E8F0;
                border-radius: 12px;
                background: #FFFFFF;
                font-family: 'Segoe UI', monospace;
                font-size: 24px;
                font-weight: bold;
                color: #1A2C3E;
            }
        """)
        timer_col.addWidget(self.time_label)

        timer_btn_row = QHBoxLayout()
        timer_btn_row.setSpacing(6)

        self.pause_timer_btn = QPushButton("⏸ Пауза")
        self.pause_timer_btn.setFixedHeight(28)
        self.pause_timer_btn.setStyleSheet(
            "QPushButton { background-color: #E2E8F0; color: #5A6E7A; border: none; padding: 4px 10px; font-size: 11px; border-radius: 14px; font-weight: 600; }"
            "QPushButton:hover { background-color: #CBD5E0; }"
        )
        self.pause_timer_btn.clicked.connect(self.toggle_timer_pause)
        timer_btn_row.addWidget(self.pause_timer_btn)

        self.reset_timer_btn = QPushButton("⟳ Сброс")
        self.reset_timer_btn.setFixedHeight(28)
        self.reset_timer_btn.setStyleSheet(
            "QPushButton { background-color: #E2E8F0; color: #5A6E7A; border: none; padding: 4px 10px; font-size: 11px; border-radius: 14px; font-weight: 600; }"
            "QPushButton:hover { background-color: #CBD5E0; }"
        )
        self.reset_timer_btn.clicked.connect(self.reset_timer)
        timer_btn_row.addWidget(self.reset_timer_btn)

        timer_col.addLayout(timer_btn_row)
        top_row.addWidget(timer_container)

        # Добавляем растяжение, которое будет толкать текст к центру
        top_row.addStretch(1)

        # Контейнер для текста (ВАЖНО: создаём отдельный виджет)
        text_container = QWidget()
        title_col = QVBoxLayout(text_container)  # layout сразу на виджет
        title_col.setSpacing(6)
        title_col.setAlignment(Qt.AlignVCenter)

        info = QLabel("📚  Флеш-карточки")
        info.setFont(QFont('Segoe UI', 25, QFont.Bold))
        info.setAlignment(Qt.AlignCenter)  # Меняем на AlignCenter
        info.setStyleSheet("color: #1A2C3E; margin-bottom: 4px;")
        title_col.addWidget(info)

        self.card_counter = QLabel("Карточка 0 из 0")
        self.card_counter.setAlignment(Qt.AlignCenter)  # Меняем на AlignCenter
        self.card_counter.setStyleSheet("color: #9B9FC4; font-size: 13px;")
        title_col.addWidget(self.card_counter)

        # Добавляем контейнер в top_row
        top_row.addWidget(text_container)

        # Добавляем растяжение справа
        top_row.addStretch(1)

        layout.addLayout(top_row)



        # Карточка
        self.card_frame = QFrame()
        self.card_frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1.5px solid #E2E8F0;
            }
        """)
        self.card_frame.setMinimumHeight(220)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setAlignment(Qt.AlignCenter)

        self.card_word = QLabel("Нажмите  «Начать»  для старта")
        self.card_word.setFont(QFont('Segoe UI', 28, QFont.Bold))
        self.card_word.setAlignment(Qt.AlignCenter)
        self.card_word.setWordWrap(True)
        self.card_word.setStyleSheet("color: #1A2C3E; letter-spacing: 2px; border: none; background: transparent;")
        card_layout.addWidget(self.card_word)

        self.card_translation = QLabel("")
        self.card_translation.setFont(QFont('Segoe UI', 22, QFont.Bold))
        self.card_translation.setAlignment(Qt.AlignCenter)
        self.card_translation.setStyleSheet(CARD_TRANSLATION_STYLE + " border: none; background: transparent;")
        card_layout.addWidget(self.card_translation)

        layout.addWidget(self.card_frame)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_cards_btn = QPushButton("▶  Начать")
        self.start_cards_btn.setStyleSheet(
            "QPushButton { background-color: #7DD3B8; color: white; border: none; padding: 12px 22px; font-size: 14px; border-radius: 40px; font-weight: 700; }"
            "QPushButton:hover { background-color: #8FE3C8; }"
            "QPushButton:pressed { background-color: #6BC2A7; }"
            "QPushButton:disabled { background-color: #E2E8F0; color: #9AAEB9; border: none; }"
        )
        self.start_cards_btn.clicked.connect(self.start_flashcards)
        button_layout.addWidget(self.start_cards_btn)

        self.stop_cards_btn = QPushButton("⏹  Стоп")
        self.stop_cards_btn.setStyleSheet(
            "QPushButton { background-color: #E87A7A; color: white; border: none; padding: 12px 22px; font-size: 14px; border-radius: 40px; font-weight: 700; }"
            "QPushButton:hover { background-color: #F08080; }"
            "QPushButton:pressed { background-color: #D06060; }"
            "QPushButton:disabled { background-color: #E2E8F0; color: #9AAEB9; border: none; }"
        )
        self.stop_cards_btn.clicked.connect(self.stop_flashcards)
        self.stop_cards_btn.setEnabled(False)
        button_layout.addWidget(self.stop_cards_btn)

        self.flip_card_btn = QPushButton("🔄  Перевернуть")
        self.flip_card_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        self.flip_card_btn.clicked.connect(self.flip_card)
        self.flip_card_btn.setEnabled(False)
        button_layout.addWidget(self.flip_card_btn)

        self.next_card_btn = QPushButton("➡  Следующая")
        self.next_card_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        self.next_card_btn.clicked.connect(self.next_card)
        self.next_card_btn.setEnabled(False)
        button_layout.addWidget(self.next_card_btn)

        self.know_btn = QPushButton("✓  Знаю")
        self.know_btn.setStyleSheet(BTN_SUCCESS_STYLE)
        self.know_btn.clicked.connect(self.mark_as_known)
        self.know_btn.setEnabled(False)
        button_layout.addWidget(self.know_btn)

        layout.addLayout(button_layout)

    def _load_icon(self):
        """Загружает иконку из data/ico.png если файл существует"""
        ico_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'ico.png')
        if os.path.exists(ico_path):
            pix = QPixmap(ico_path).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pix)
        else:
            self.icon_label.setText("🖼")
            self.icon_label.setFont(QFont('Segoe UI', 32))

    def start_flashcards(self):
        self.cards_to_study = [w for w in self.main.vocabulary
                               if not self.main.is_word_learned(w['english'])]
        if not self.cards_to_study:
            msg = QMessageBox(self)
            msg.setWindowTitle("Поздравляем!")
            msg.setText("Вы изучили все слова! 🎉")
            msg.setIcon(QMessageBox.NoIcon)
            msg.setStyleSheet(LIGHT_MSG_STYLE)
            msg.exec_()
            return
        random.shuffle(self.cards_to_study)
        self.current_card_index = 0
        self.show_current_card()
        self.start_cards_btn.setEnabled(False)
        self.stop_cards_btn.setEnabled(True)
        self.flip_card_btn.setEnabled(True)
        self.next_card_btn.setEnabled(True)
        self.know_btn.setEnabled(True)

    def show_current_card(self):
        if self.current_card_index < len(self.cards_to_study):
            card = self.cards_to_study[self.current_card_index]
            self.card_word.setText(card['english'].upper())
            self.card_translation.setText("")
            self.card_flipped = False
            self.card_frame.setStyleSheet("""
                QFrame {
                    background: #FFFFFF;
                    border-radius: 20px;
                    border: 1.5px solid #E2E8F0;
                }
            """)
            self.card_counter.setText(
                f"Карточка {self.current_card_index + 1} из {len(self.cards_to_study)}")
        else:
            self.finish_flashcards()

    def flip_card(self):
        if self.current_card_index < len(self.cards_to_study):
            card = self.cards_to_study[self.current_card_index]
            if not self.card_flipped:
                self.card_translation.setText(card['russian'])
                self.card_flipped = True
                self.card_frame.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #F0FBF7, stop:1 #E8F5F0);
                        border-radius: 20px;
                        border: 1.5px solid #7DD3B8;
                    }
                """)
            else:
                self.card_translation.setText("")
                self.card_flipped = False
                self.card_frame.setStyleSheet("""
                    QFrame {
                        background: #FFFFFF;
                        border-radius: 20px;
                        border: 1.5px solid #E2E8F0;
                    }
                """)

    def next_card(self):
        self.current_card_index += 1
        self.show_current_card()

    def mark_as_known(self):
        if self.current_card_index < len(self.cards_to_study):
            card = self.cards_to_study[self.current_card_index]
            self.main.mark_word_learned(card)
            self.next_card()
            self.main.update_progress_stats()
            self.main.save_progress()

    def finish_flashcards(self):
        self.card_word.setText("Все карточки изучены! 🎉")
        self.card_translation.setText("")
        self.card_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E8F5F0, stop:1 #D4EEE5);
                border-radius: 20px;
                border: 1.5px solid #7DD3B8;
            }
        """)
        self.flip_card_btn.setEnabled(False)
        self.next_card_btn.setEnabled(False)
        self.know_btn.setEnabled(False)
        self.start_cards_btn.setEnabled(True)
        self.stop_cards_btn.setEnabled(False)

    def stop_flashcards(self):
        self.cards_to_study = []
        self.current_card_index = 0
        self.card_flipped = False
        self.card_word.setText("Нажмите  «Начать»  для старта")
        self.card_translation.setText("")
        self.card_frame.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border-radius: 20px;
                border: 1.5px solid #E2E8F0;
            }
        """)
        self.card_counter.setText("Карточка 0 из 0")
        self.start_cards_btn.setEnabled(True)
        self.stop_cards_btn.setEnabled(False)
        self.flip_card_btn.setEnabled(False)
        self.next_card_btn.setEnabled(False)
        self.know_btn.setEnabled(False)

    def toggle_timer_pause(self):
        if self.timer_paused:
            # Возобновить: смещаем start_time вперёд на время паузы
            self.start_time = time.time() - self.elapsed_before_pause
            self.timer.start(1000)
            self.timer_paused = False
            self.pause_timer_btn.setText("⏸ Пауза")
        else:
            # Пауза: сохраняем прошедшее время
            self.elapsed_before_pause = int(time.time() - self.start_time)
            self.timer.stop()
            self.timer_paused = True
            self.pause_timer_btn.setText("▶ Продолжить")

    def reset_timer(self):
        self.timer.stop()
        self.timer_paused = False
        self.elapsed_before_pause = 0
        self.start_time = time.time()
        self.time_label.setText("00:00")
        self.pause_timer_btn.setText("⏸ Пауза")
        self.timer.start(1000)

    def update_time(self):
        """Обновление счётчика времени"""
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
