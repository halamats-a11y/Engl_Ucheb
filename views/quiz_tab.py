"""
Вкладка с тестами для проверки знаний
"""
import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QComboBox, QSpinBox, QRadioButton,
                             QButtonGroup, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from utils.styles import (BTN_SECONDARY_STYLE, BTN_START_STYLE, BTN_STOP_STYLE, CARD_FRAME_STYLE,
                          COUNTER_STYLE, GREY_TEXT_STYLE, LIGHT_MSG_STYLE, PAGE_TITLE_STYLE,
                          PANEL_FRAME_STYLE, QUIZ_CORRECT_STYLE, QUIZ_NORMAL_STYLE,
                          QUIZ_QUESTION_BOX_STYLE, QUIZ_RESULT_BAD_STYLE, QUIZ_RESULT_OK_STYLE,
                          QUIZ_TIMER_STYLE, QUIZ_TIMER_URGENT_STYLE, QUIZ_WOD_ENGLISH_STYLE,
                          QUIZ_WOD_HINT_STYLE, QUIZ_WOD_RUSSIAN_STYLE, QUIZ_WRONG_STYLE,
                          SECTION_CAPTION_STYLE, TEXT_DARK_STYLE)


class QuizTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.quiz_questions = []
        self.current_question = 0
        self.quiz_score = 0
        self.is_timed_mode = False
        self.quiz_timer = QTimer()
        self.quiz_timer.timeout.connect(self.update_quiz_timer)
        self.time_remaining = 0
        self.quiz_active = False
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        self.setLayout(layout)

        title = QLabel("✍  Тест на знание слов")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PAGE_TITLE_STYLE)
        layout.addWidget(title)

        # Настройки (всегда видны)
        settings_frame = QFrame()
        settings_frame.setStyleSheet(PANEL_FRAME_STYLE)
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(16, 10, 16, 10)

        lbl1 = QLabel("Режим:")
        lbl1.setStyleSheet(GREY_TEXT_STYLE)
        settings_layout.addWidget(lbl1)

        self.quiz_mode = QComboBox()
        self.quiz_mode.addItems(["Обычный режим", "⏱  На время (60 сек)"])
        self.quiz_mode.currentIndexChanged.connect(self.on_quiz_mode_changed)
        settings_layout.addWidget(self.quiz_mode)

        settings_layout.addSpacing(20)

        lbl2 = QLabel("Вопросов:")
        lbl2.setStyleSheet(GREY_TEXT_STYLE)
        settings_layout.addWidget(lbl2)

        self.quiz_count = QSpinBox()
        self.quiz_count.setMinimum(5)
        self.quiz_count.setMaximum(50)
        self.quiz_count.setValue(10)
        settings_layout.addWidget(self.quiz_count)

        settings_layout.addStretch()
        layout.addWidget(settings_frame)

        # Таймер (скрыт до старта)
        self.timer_label = QLabel("")
        self.timer_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(QUIZ_TIMER_STYLE)
        self.timer_label.setVisible(False)
        layout.addWidget(self.timer_label)

        # «Слово дня» — показывается пока тест не начат
        self.word_of_day_frame = QFrame()
        self.word_of_day_frame.setStyleSheet(CARD_FRAME_STYLE)
        wod_layout = QVBoxLayout(self.word_of_day_frame)
        wod_layout.setContentsMargins(32, 28, 32, 28)
        wod_layout.setSpacing(10)
        wod_layout.setAlignment(Qt.AlignCenter)

        wod_title = QLabel("📖  Слово дня")
        wod_title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        wod_title.setAlignment(Qt.AlignCenter)
        wod_title.setStyleSheet(SECTION_CAPTION_STYLE)
        wod_layout.addWidget(wod_title)

        self.wod_english = QLabel("")
        self.wod_english.setFont(QFont('Segoe UI', 30, QFont.Bold))
        self.wod_english.setAlignment(Qt.AlignCenter)
        self.wod_english.setStyleSheet(QUIZ_WOD_ENGLISH_STYLE)
        wod_layout.addWidget(self.wod_english)

        self.wod_russian = QLabel("")
        self.wod_russian.setFont(QFont('Segoe UI', 18))
        self.wod_russian.setAlignment(Qt.AlignCenter)
        self.wod_russian.setStyleSheet(QUIZ_WOD_RUSSIAN_STYLE)
        wod_layout.addWidget(self.wod_russian)

        self.wod_hint = QLabel("Нажмите «Начать тест», чтобы проверить знания")
        self.wod_hint.setFont(QFont('Segoe UI', 11))
        self.wod_hint.setAlignment(Qt.AlignCenter)
        self.wod_hint.setStyleSheet(QUIZ_WOD_HINT_STYLE)
        wod_layout.addWidget(self.wod_hint)

        layout.addWidget(self.word_of_day_frame)
        self._refresh_word_of_day()

        # Вопрос (скрыт до старта)
        self.quiz_question = QLabel("")
        self.quiz_question.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.quiz_question.setAlignment(Qt.AlignCenter)
        self.quiz_question.setMinimumHeight(100)
        self.quiz_question.setWordWrap(True)
        self.quiz_question.setStyleSheet(QUIZ_QUESTION_BOX_STYLE)
        self.quiz_question.setVisible(False)
        layout.addWidget(self.quiz_question)

        # Варианты ответов (скрыты до старта)
        self.answer_group = QButtonGroup()
        self.answer_buttons = []
        for i in range(4):
            btn = QRadioButton()
            btn.setFont(QFont('Segoe UI', 14))
            btn.setStyleSheet(QUIZ_NORMAL_STYLE)
            self.answer_group.addButton(btn, i)
            self.answer_buttons.append(btn)
            btn.setVisible(False)
            layout.addWidget(btn)

        # Результат и прогресс
        self.quiz_result = QLabel("")
        self.quiz_result.setAlignment(Qt.AlignCenter)
        self.quiz_result.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.quiz_result.setStyleSheet(TEXT_DARK_STYLE)
        layout.addWidget(self.quiz_result)

        self.quiz_progress = QLabel("")
        self.quiz_progress.setAlignment(Qt.AlignCenter)
        self.quiz_progress.setStyleSheet(COUNTER_STYLE)
        layout.addWidget(self.quiz_progress)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_quiz_btn = QPushButton("▶  Начать тест")
        self.start_quiz_btn.setStyleSheet(BTN_START_STYLE)
        self.start_quiz_btn.clicked.connect(self.start_quiz)
        button_layout.addWidget(self.start_quiz_btn)

        self.stop_quiz_btn = QPushButton("⏹  Стоп")
        self.stop_quiz_btn.setStyleSheet(BTN_STOP_STYLE)
        self.stop_quiz_btn.clicked.connect(self.stop_quiz)
        self.stop_quiz_btn.setEnabled(False)
        button_layout.addWidget(self.stop_quiz_btn)

        self.check_answer_btn = QPushButton("✓  Проверить")
        self.check_answer_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        self.check_answer_btn.clicked.connect(self.check_quiz_answer)
        self.check_answer_btn.setEnabled(False)
        button_layout.addWidget(self.check_answer_btn)

        self.next_question_btn = QPushButton("➡  Следующий вопрос")
        self.next_question_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        self.next_question_btn.clicked.connect(self.next_quiz_question)
        self.next_question_btn.setEnabled(False)
        button_layout.addWidget(self.next_question_btn)

        layout.addLayout(button_layout)

    def _refresh_word_of_day(self):
        if self.main.vocabulary:
            w = random.choice(self.main.vocabulary)
            self.wod_english.setText(w['english'].upper())
            self.wod_russian.setText(w['russian'])
        else:
            self.wod_english.setText("—")
            self.wod_russian.setText("")

    def _show_quiz_widgets(self, visible):
        self.word_of_day_frame.setVisible(not visible)
        self.quiz_question.setVisible(visible)
        for btn in self.answer_buttons:
            btn.setVisible(visible)

    def on_quiz_mode_changed(self):
        if "На время" in self.quiz_mode.currentText():
            self.quiz_count.setEnabled(False)
            self.quiz_count.setValue(999)
        else:
            self.quiz_count.setEnabled(True)
            self.quiz_count.setValue(10)

    def start_quiz(self):
        self.is_timed_mode = "На время" in self.quiz_mode.currentText()
        num_questions = self.quiz_count.value()

        if len(self.main.vocabulary) < 4:
            msg = QMessageBox(self)
            msg.setWindowTitle("Предупреждение")
            msg.setText("Недостаточно слов в словаре. Минимум: 4")
            msg.setIcon(QMessageBox.NoIcon)
            msg.setStyleSheet(LIGHT_MSG_STYLE)
            msg.exec_()
            return

        self._show_quiz_widgets(True)
        self.quiz_session_id = self.main.start_quiz_session("timed" if self.is_timed_mode else "classic")
        self.quiz_active = True

        if self.is_timed_mode:
            self.time_remaining = 60
            self.quiz_questions = []
            self.quiz_score = 0
            self.current_question = 0
            self.timer_label.setVisible(True)
            self.timer_label.setText(f"⏱  Осталось: {self.time_remaining} сек")
            self.quiz_timer.start(1000)
            self.generate_timed_question()
        else:
            if len(self.main.vocabulary) < num_questions:
                msg = QMessageBox(self)
                msg.setWindowTitle("Предупреждение")
                msg.setText(f"Недостаточно слов. Минимум: {num_questions}")
                msg.setIcon(QMessageBox.NoIcon)
                msg.setStyleSheet(LIGHT_MSG_STYLE)
                msg.exec_()
                self._show_quiz_widgets(False)
                self.quiz_active = False
                return
            self.quiz_questions = random.sample(self.main.vocabulary, num_questions)
            self.current_question = 0
            self.quiz_score = 0
            self.timer_label.setVisible(False)
            self.show_quiz_question()

        self.start_quiz_btn.setEnabled(False)
        self.stop_quiz_btn.setEnabled(True)
        self.check_answer_btn.setEnabled(True)
        self.quiz_count.setEnabled(False)
        self.quiz_mode.setEnabled(False)

    def _build_question(self, question):
        if random.choice([True, False]):
            self.quiz_question.setText(f"Переведите:  {question['english']}")
            correct_answer = question['russian']
            direction = 'en_to_ru'
        else:
            self.quiz_question.setText(f"Переведите:  {question['russian']}")
            correct_answer = question['english']
            direction = 'ru_to_en'

        other_words = [w for w in self.main.vocabulary if w != question]
        wrong_answers = random.sample(other_words, min(3, len(other_words)))

        if direction == 'en_to_ru':
            answers = [correct_answer] + [w['russian'] for w in wrong_answers]
        else:
            answers = [correct_answer] + [w['english'] for w in wrong_answers]

        random.shuffle(answers)
        self.correct_answer_index = answers.index(correct_answer)

        self.answer_group.setExclusive(False)
        for i, btn in enumerate(self.answer_buttons):
            btn.setText(answers[i])
            btn.setEnabled(True)
            btn.setChecked(False)
            btn.setStyleSheet(QUIZ_NORMAL_STYLE)
            btn.setAutoExclusive(False)
        self.answer_group.setExclusive(True)
        for btn in self.answer_buttons:
            btn.setAutoExclusive(True)

        self.quiz_result.setText("")

    def show_quiz_question(self):
        if self.current_question < len(self.quiz_questions):
            question = self.quiz_questions[self.current_question]
            self._build_question(question)
            self.quiz_progress.setText(
                f"Вопрос {self.current_question + 1} из {len(self.quiz_questions)}")
            self.check_answer_btn.setEnabled(True)
            self.next_question_btn.setEnabled(False)
        else:
            self.finish_quiz()

    def generate_timed_question(self):
        if self.time_remaining > 0:
            question = random.choice(self.main.vocabulary)
            self._build_question(question)
            self.quiz_progress.setText(f"Правильных ответов: {self.quiz_score}")
            self.check_answer_btn.setEnabled(True)
            self.next_question_btn.setEnabled(False)
        else:
            self.finish_timed_quiz()

    def check_quiz_answer(self):
        selected_button = self.answer_group.checkedButton()
        if selected_button is None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Внимание")
            msg.setText("Выберите ответ!")
            msg.setIcon(QMessageBox.NoIcon)
            msg.setStyleSheet(LIGHT_MSG_STYLE)
            msg.exec_()
            return

        selected_index = self.answer_group.id(selected_button)
        self.main.user_progress['total_answers'] += 1

        if selected_index == self.correct_answer_index:
            self.quiz_result.setText("✓  Правильно!")
            self.quiz_result.setStyleSheet(QUIZ_RESULT_OK_STYLE)
            self.answer_buttons[selected_index].setStyleSheet(QUIZ_CORRECT_STYLE)
            self.quiz_score += 1
            self.main.user_progress['correct_answers'] += 1
        else:
            self.quiz_result.setText("✗  Неправильно!")
            self.quiz_result.setStyleSheet(QUIZ_RESULT_BAD_STYLE)
            self.answer_buttons[selected_index].setStyleSheet(QUIZ_WRONG_STYLE)
            self.answer_buttons[self.correct_answer_index].setStyleSheet(QUIZ_CORRECT_STYLE)

        for btn in self.answer_buttons:
            btn.setEnabled(False)
        self.check_answer_btn.setEnabled(False)
        self.next_question_btn.setEnabled(True)

    def next_quiz_question(self):
        if self.is_timed_mode:
            self.generate_timed_question()
        else:
            self.current_question += 1
            self.show_quiz_question()

    def finish_quiz(self):
        percentage = int((self.quiz_score / len(self.quiz_questions)) * 100)
        self.quiz_question.setText(
            f"Тест завершён! 🎉\n\nРезультат: {self.quiz_score} из {len(self.quiz_questions)}  ({percentage}%)")

        for btn in self.answer_buttons:
            btn.setText("")
            btn.setEnabled(False)
            btn.setStyleSheet(QUIZ_NORMAL_STYLE)
        self.quiz_result.setText("")
        self.quiz_progress.setText("")
        self.main.user_progress['tests_completed'] += 1
        self.main.finish_quiz_session(getattr(self, 'quiz_session_id', None), self.quiz_score, len(self.quiz_questions))

        self._reset_to_idle()
        self.main.update_progress_stats()
        self.main.save_progress()

    def update_quiz_timer(self):
        self.time_remaining -= 1
        self.timer_label.setText(f"⏱  Осталось: {self.time_remaining} сек")
        if self.time_remaining <= 10:
            self.timer_label.setStyleSheet(QUIZ_TIMER_URGENT_STYLE)
        if self.time_remaining <= 0:
            self.quiz_timer.stop()
            self.finish_timed_quiz()

    def finish_timed_quiz(self):
        self.quiz_timer.stop()
        self.timer_label.setVisible(False)
        wpm = self.quiz_score

        self.quiz_question.setText(f"⏱  Время вышло!\n\n🎉 Результат: {wpm} слов/минуту!")
        for btn in self.answer_buttons:
            btn.setText("")
            btn.setEnabled(False)
            btn.setStyleSheet(QUIZ_NORMAL_STYLE)
        self.quiz_result.setText("")
        self.quiz_progress.setText("")
        self.main.user_progress['tests_completed'] += 1
        self.main.finish_quiz_session(getattr(self, 'quiz_session_id', None), self.quiz_score, self.current_question + 1)

        rating = ""
        if wpm >= 40:
            rating = "🏆 НЕВЕРОЯТНО! Вы мастер!"
        elif wpm >= 30:
            rating = "⭐ ОТЛИЧНО!"
        elif wpm >= 20:
            rating = "✨ ХОРОШО!"
        elif wpm >= 10:
            rating = "👍 НЕПЛОХО!"
        else:
            rating = "💪 Тренируйтесь больше!"

        self._reset_to_idle()

        msg = QMessageBox(self)
        msg.setWindowTitle("Тест завершён!")
        msg.setText(
            f"⏱ Результат теста на время:\n\n"
            f"✅ Правильных: {wpm}\n"
            f"⏰ Время: 60 секунд\n"
            f"📊 Скорость: {wpm} слов/мин\n\n{rating}"
        )
        msg.setIcon(QMessageBox.NoIcon)
        msg.setStyleSheet(LIGHT_MSG_STYLE)
        msg.exec_()

        self.main.update_progress_stats()
        self.main.save_progress()

    def _reset_to_idle(self):
        self._show_quiz_widgets(False)
        self._refresh_word_of_day()
        self.quiz_active = False
        self.start_quiz_btn.setEnabled(True)
        self.stop_quiz_btn.setEnabled(False)
        self.check_answer_btn.setEnabled(False)
        self.next_question_btn.setEnabled(False)
        self.quiz_count.setEnabled(True)
        self.quiz_mode.setEnabled(True)

    def stop_quiz(self):
        self.quiz_timer.stop()
        self.quiz_questions = []
        self.current_question = 0
        self.quiz_score = 0
        self.quiz_active = False
        self.timer_label.setVisible(False)
        self.quiz_result.setText("")
        self.quiz_progress.setText("")
        self._reset_to_idle()
