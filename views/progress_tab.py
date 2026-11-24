"""
Вкладка с прогрессом изучения + система званий
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QPushButton, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.styles import (BTN_SECONDARY_STYLE, GRADIENT_FRAME_STYLE, GREY_TEXT_STYLE,
                          HINT_TEXT_STYLE, PAGE_TITLE_STYLE, PANEL_FRAME_STYLE,
                          PROGRESS_BIG_TEXT_STYLE, PROGRESS_CARD_STYLE, PROGRESS_CHECK_DONE_STYLE,
                          PROGRESS_DAILY_CONGRATS_STYLE, PROGRESS_GOAL_BAR_STYLE,
                          PROGRESS_GOAL_TEXT_STYLE, PROGRESS_PROG_TITLE_STYLE,
                          PROGRESS_RANKS_TITLE_STYLE, PROGRESS_RANK_HEADER_STYLE,
                          PROGRESS_RANK_LOCKED_STYLE, PROGRESS_REQ_DONE_STYLE,
                          PROGRESS_REQ_LOCKED_STYLE, PROGRESS_REQ_STYLE, PROGRESS_STREAK_CARD_STYLE,
                          PROGRESS_STREAK_SUB_STYLE, PROGRESS_STREAK_TITLE_STYLE,
                          PROGRESS_VALUE_STYLE, PROGRESS_VAL_ACCURACY_STYLE, SECTION_CAPTION_STYLE,
                          TRANSPARENT_STYLE, rank_done_style, rank_name_style, rank_title_style)

# ── Таблица званий ────────────────────────────────────────────────────────────
# (мин_слов, мин_тестов, эмодзи, название, цвет)
RANKS = [
    (0,   0,  "🌱", "Новичок",          "#9AAEB9"),
    (10,  1,  "📝", "Студент",          "#5A6E7A"),
    (30,  3,  "📖", "Читатель",         "#7DD3B8"),
    (75,  5,  "🎓", "Ученик",           "#3ABFA0"),
    (150, 10, "⭐", "Знаток",           "#F5B841"),
    (300, 20, "🔥", "Эрудит",           "#F5824A"),
    (500, 35, "💎", "Мастер слов",      "#7B74FF"),
    (750, 50, "🏆", "Лингвист",         "#E8A020"),
    (1000,75, "👑", "Полиглот",         "#E8504A"),
    (2094,100,"🌟", "Легенда словаря",  "#7DD3B8"),
]

def get_rank(words_learned: int, tests_completed: int) -> tuple:
    """Возвращает (эмодзи, название, цвет, след_порог_слов, след_порог_тестов)."""
    current = RANKS[0]
    for rank in RANKS:
        if words_learned >= rank[0] and tests_completed >= rank[1]:
            current = rank
        else:
            break
    idx = RANKS.index(current)
    if idx + 1 < len(RANKS):
        nxt = RANKS[idx + 1]
        return current[2], current[3], current[4], nxt[0], nxt[1]
    return current[2], current[3], current[4], None, None


class ProgressTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main = main_window
        self.init_ui()
        self.update_stats()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.setLayout(layout)

        title = QLabel("📊  Мой прогресс")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PAGE_TITLE_STYLE)
        layout.addWidget(title)

        # ── Карточка звания ───────────────────────────────────────────
        self.rank_frame = QFrame()
        self.rank_frame.setStyleSheet(GRADIENT_FRAME_STYLE)
        rank_layout = QHBoxLayout(self.rank_frame)
        rank_layout.setContentsMargins(24, 18, 24, 18)
        rank_layout.setSpacing(16)

        self.rank_icon_lbl = QLabel("🌱")
        self.rank_icon_lbl.setFont(QFont('Segoe UI', 36))
        self.rank_icon_lbl.setStyleSheet(TRANSPARENT_STYLE)
        rank_layout.addWidget(self.rank_icon_lbl)

        rank_text_col = QVBoxLayout()
        rank_text_col.setSpacing(4)

        rank_header = QLabel("Ваше звание")
        rank_header.setStyleSheet(PROGRESS_RANK_HEADER_STYLE)
        rank_text_col.addWidget(rank_header)

        self.rank_name_lbl = QLabel("Новичок")
        self.rank_name_lbl.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.rank_name_lbl.setStyleSheet(PROGRESS_BIG_TEXT_STYLE)
        rank_text_col.addWidget(self.rank_name_lbl)

        self.rank_next_lbl = QLabel("")
        self.rank_next_lbl.setStyleSheet(HINT_TEXT_STYLE)
        rank_text_col.addWidget(self.rank_next_lbl)

        rank_layout.addLayout(rank_text_col)
        rank_layout.addStretch()
        layout.addWidget(self.rank_frame)

        # ── Серия дней + дневная цель ─────────────────────────────────
        streak_goal_row = QHBoxLayout()
        streak_goal_row.setSpacing(12)

        # Карточка серии дней
        streak_card = QFrame()
        streak_card.setStyleSheet(PROGRESS_STREAK_CARD_STYLE)
        sc_layout = QVBoxLayout(streak_card)
        sc_layout.setContentsMargins(18, 14, 18, 14)
        sc_layout.setSpacing(4)

        streak_title = QLabel("🔥  Серия дней")
        streak_title.setFont(QFont('Segoe UI', 11, QFont.Bold))
        streak_title.setStyleSheet(PROGRESS_STREAK_TITLE_STYLE)
        sc_layout.addWidget(streak_title)

        self.streak_val_lbl = QLabel("0 дней подряд")
        self.streak_val_lbl.setFont(QFont('Segoe UI', 20, QFont.Bold))
        self.streak_val_lbl.setStyleSheet(PROGRESS_BIG_TEXT_STYLE)
        sc_layout.addWidget(self.streak_val_lbl)

        self.streak_sub_lbl = QLabel("Войди завтра, чтобы не прерывать!")
        self.streak_sub_lbl.setStyleSheet(PROGRESS_STREAK_SUB_STYLE)
        sc_layout.addWidget(self.streak_sub_lbl)

        streak_goal_row.addWidget(streak_card)

        # Карточка дневной цели
        from PyQt5.QtWidgets import QProgressBar as _QProgressBar
        goal_card = QFrame()
        goal_card.setStyleSheet(PROGRESS_CARD_STYLE)
        gc_layout = QVBoxLayout(goal_card)
        gc_layout.setContentsMargins(18, 14, 18, 14)
        gc_layout.setSpacing(6)

        goal_title_lbl = QLabel("🎯  Цель на сегодня")
        goal_title_lbl.setFont(QFont('Segoe UI', 11, QFont.Bold))
        goal_title_lbl.setStyleSheet(SECTION_CAPTION_STYLE)
        gc_layout.addWidget(goal_title_lbl)

        self.daily_words_lbl = QLabel("Слов: 0 / 5")
        self.daily_words_lbl.setStyleSheet(PROGRESS_GOAL_TEXT_STYLE)
        gc_layout.addWidget(self.daily_words_lbl)

        self.daily_words_bar = _QProgressBar()
        self.daily_words_bar.setMaximum(5)
        self.daily_words_bar.setValue(0)
        self.daily_words_bar.setTextVisible(False)
        self.daily_words_bar.setFixedHeight(7)
        self.daily_words_bar.setStyleSheet(PROGRESS_GOAL_BAR_STYLE)
        gc_layout.addWidget(self.daily_words_bar)

        self.daily_tests_lbl = QLabel("Тестов: 0 / 1")
        self.daily_tests_lbl.setStyleSheet(PROGRESS_GOAL_TEXT_STYLE)
        gc_layout.addWidget(self.daily_tests_lbl)

        self.daily_tests_bar = _QProgressBar()
        self.daily_tests_bar.setMaximum(1)
        self.daily_tests_bar.setValue(0)
        self.daily_tests_bar.setTextVisible(False)
        self.daily_tests_bar.setFixedHeight(7)
        self.daily_tests_bar.setStyleSheet(PROGRESS_GOAL_BAR_STYLE)
        gc_layout.addWidget(self.daily_tests_bar)

        self.daily_congrats_lbl = QLabel("")
        self.daily_congrats_lbl.setAlignment(Qt.AlignCenter)
        self.daily_congrats_lbl.setFont(QFont('Segoe UI', 11, QFont.Bold))
        self.daily_congrats_lbl.setStyleSheet(PROGRESS_DAILY_CONGRATS_STYLE)
        self.daily_congrats_lbl.setVisible(False)
        gc_layout.addWidget(self.daily_congrats_lbl)

        streak_goal_row.addWidget(goal_card)
        layout.addLayout(streak_goal_row)

        # ── Три карточки статистики ───────────────────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        def make_stat_card(icon, label_text):
            frame = QFrame()
            frame.setStyleSheet(PROGRESS_CARD_STYLE)
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(20, 18, 20, 18)
            fl.setSpacing(6)

            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont('Segoe UI', 26))
            icon_lbl.setAlignment(Qt.AlignCenter)
            icon_lbl.setStyleSheet(TRANSPARENT_STYLE)
            fl.addWidget(icon_lbl)

            val_lbl = QLabel("—")
            val_lbl.setFont(QFont('Segoe UI', 22, QFont.Bold))
            val_lbl.setAlignment(Qt.AlignCenter)
            val_lbl.setStyleSheet(PROGRESS_VALUE_STYLE)
            fl.addWidget(val_lbl)

            desc_lbl = QLabel(label_text)
            desc_lbl.setAlignment(Qt.AlignCenter)
            desc_lbl.setStyleSheet(HINT_TEXT_STYLE)
            fl.addWidget(desc_lbl)

            return frame, val_lbl

        card_words, self.val_words = make_stat_card("📖", "Слов изучено")
        card_tests, self.val_tests = make_stat_card("✍", "Тестов пройдено")
        card_acc, self.val_accuracy = make_stat_card("🎯", "Точность ответов")
        self.val_accuracy.setStyleSheet(PROGRESS_VAL_ACCURACY_STYLE)

        cards_layout.addWidget(card_words)
        cards_layout.addWidget(card_tests)
        cards_layout.addWidget(card_acc)
        layout.addLayout(cards_layout)

        # ── Прогресс-бар изучения ─────────────────────────────────────
        prog_frame = QFrame()
        prog_frame.setStyleSheet(PANEL_FRAME_STYLE)
        prog_layout = QVBoxLayout(prog_frame)
        prog_layout.setContentsMargins(22, 18, 22, 18)
        prog_layout.setSpacing(10)

        prog_title = QLabel("Прогресс изучения словаря")
        prog_title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        prog_title.setStyleSheet(PROGRESS_PROG_TITLE_STYLE)
        prog_layout.addWidget(prog_title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        prog_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("0 из 0 слов изучено")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet(GREY_TEXT_STYLE)
        prog_layout.addWidget(self.progress_label)

        layout.addWidget(prog_frame)

        # ── Таблица всех званий ───────────────────────────────────────
        ranks_frame = QFrame()
        ranks_frame.setStyleSheet(PANEL_FRAME_STYLE)
        ranks_layout = QVBoxLayout(ranks_frame)
        ranks_layout.setContentsMargins(22, 14, 22, 14)
        ranks_layout.setSpacing(6)

        ranks_title = QLabel("Все звания")
        ranks_title.setFont(QFont('Segoe UI', 11, QFont.Bold))
        ranks_title.setStyleSheet(PROGRESS_RANKS_TITLE_STYLE)
        ranks_layout.addWidget(ranks_title)

        self.rank_rows = []
        for rank in RANKS:
            row = QHBoxLayout()
            row.setSpacing(10)

            icon_l = QLabel(rank[2])
            icon_l.setFixedWidth(28)
            icon_l.setFont(QFont('Segoe UI', 16))
            icon_l.setStyleSheet(TRANSPARENT_STYLE)
            row.addWidget(icon_l)

            name_l = QLabel(rank[3])
            name_l.setFont(QFont('Segoe UI', 12, QFont.Bold))
            name_l.setStyleSheet(rank_name_style(rank[4]))
            row.addWidget(name_l)

            req_l = QLabel(f"— {rank[0]}+ слов  •  {rank[1]}+ тестов")
            req_l.setStyleSheet(PROGRESS_REQ_STYLE)
            row.addWidget(req_l)
            row.addStretch()

            check_l = QLabel("")
            check_l.setFixedWidth(20)
            check_l.setStyleSheet(TRANSPARENT_STYLE)
            row.addWidget(check_l)

            ranks_layout.addLayout(row)
            self.rank_rows.append((name_l, req_l, check_l))

        layout.addWidget(ranks_frame)

        update_btn = QPushButton("🔄  Обновить статистику")
        update_btn.setStyleSheet(BTN_SECONDARY_STYLE)
        update_btn.clicked.connect(self.update_stats)
        update_btn.setFixedWidth(220)
        layout.addWidget(update_btn, alignment=Qt.AlignCenter)

        layout.addStretch()

    def update_stats(self):
        learned_count = len(self.main.user_progress.get('words_learned', []))
        total_words = len(self.main.vocabulary)
        tests_done = self.main.user_progress['tests_completed']

        self.val_words.setText(f"{learned_count}")
        self.val_tests.setText(str(tests_done))

        if self.main.user_progress['total_answers'] > 0:
            accuracy = int(
                (self.main.user_progress['correct_answers'] /
                 self.main.user_progress['total_answers']) * 100)
            self.val_accuracy.setText(f"{accuracy}%")
        else:
            self.val_accuracy.setText("0%")

        if total_words > 0:
            pct = int((learned_count / total_words) * 100)
            self.progress_bar.setValue(pct)
            self.progress_label.setText(
                f"{learned_count} из {total_words} слов изучено ({pct}%)")
        else:
            self.progress_bar.setValue(0)
            self.progress_label.setText("0 из 0 слов изучено")

        # Обновляем звание
        icon, name, color, next_words, next_tests = get_rank(learned_count, tests_done)
        self.rank_icon_lbl.setText(icon)
        self.rank_name_lbl.setText(name)
        self.rank_name_lbl.setStyleSheet(rank_title_style(color))

        if next_words is not None:
            need_w = max(0, next_words - learned_count)
            need_t = max(0, next_tests - tests_done)
            parts = []
            if need_w > 0:
                parts.append(f"{need_w} слов")
            if need_t > 0:
                parts.append(f"{need_t} тестов")
            if parts:
                self.rank_next_lbl.setText(f"До следующего звания: ещё {' и '.join(parts)}")
            else:
                self.rank_next_lbl.setText("Следующее звание совсем близко!")
        else:
            self.rank_next_lbl.setText("🌟 Вы достигли максимального звания!")

        # Подсвечиваем достигнутые ранги в таблице
        for i, (rank, row_widgets) in enumerate(zip(RANKS, self.rank_rows)):
            name_l, req_l, check_l = row_widgets
            achieved = learned_count >= rank[0] and tests_done >= rank[1]
            if achieved:
                name_l.setStyleSheet(rank_done_style(rank[4]))
                req_l.setStyleSheet(PROGRESS_REQ_DONE_STYLE)
                check_l.setText("✓")
                check_l.setStyleSheet(PROGRESS_CHECK_DONE_STYLE)
            else:
                name_l.setStyleSheet(PROGRESS_RANK_LOCKED_STYLE)
                req_l.setStyleSheet(PROGRESS_REQ_LOCKED_STYLE)
                check_l.setText("")

        # ── Серия дней ────────────────────────────────────────────────
        streak = self.main.user_progress.get('streak', 0)
        day_word = self._day_word(streak)
        self.streak_val_lbl.setText(f"{streak} {day_word} подряд")
        if streak >= 7:
            self.streak_sub_lbl.setText("🔥 Отличная серия! Не останавливайся!")
        elif streak >= 3:
            self.streak_sub_lbl.setText("💪 Так держать! Войди завтра снова!")
        else:
            self.streak_sub_lbl.setText("Войди завтра, чтобы не прерывать серию!")

        # ── Дневная цель ──────────────────────────────────────────────
        p = self.main.user_progress
        from views.main_window import DAILY_WORDS_TARGET, DAILY_TESTS_TARGET
        wt = DAILY_WORDS_TARGET
        tt = DAILY_TESTS_TARGET
        words_done = max(0, len(p.get('words_learned', [])) - p.get('daily_words_start', 0))
        t_done = max(0, p.get('tests_completed', 0) - p.get('daily_tests_start', 0))

        self.daily_words_lbl.setText(f"📖 Слов: {min(words_done, wt)} / {wt}")
        self.daily_words_bar.setMaximum(wt)
        self.daily_words_bar.setValue(min(words_done, wt))

        self.daily_tests_lbl.setText(f"✍ Тестов: {min(t_done, tt)} / {tt}")
        self.daily_tests_bar.setMaximum(tt)
        self.daily_tests_bar.setValue(min(t_done, tt))

        goal_done = (words_done >= wt and t_done >= tt)
        self.daily_congrats_lbl.setVisible(goal_done)
        if goal_done:
            self.daily_congrats_lbl.setText("🏆 Дневная цель выполнена! Молодец!")

    @staticmethod
    def _day_word(n: int) -> str:
        if n % 100 in range(11, 20):
            return "дней"
        r = n % 10
        if r == 1:
            return "день"
        if r in (2, 3, 4):
            return "дня"
        return "дней"
