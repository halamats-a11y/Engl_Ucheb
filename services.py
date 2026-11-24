"""
services.py — бизнес-логика (без окон и без SQL).

    VocabularyService — словарь: список слов, добавление, удаление
    ProgressService   — прогресс: выученные слова, ответы и тесты,
                        серия дней подряд и дневная цель

Как работает:
    Вкладки НЕ меняют прогресс сами. Они только отправляют сигналы
    («слово выучено», «дан ответ», «тест закончен»). Главное окно подключает
    эти сигналы к методам сервисов. Сервис меняет данные, сохраняет их в базу
    (несколько действий — в одной транзакции) и отправляет сигнал
    progress_changed, чтобы окна обновились.
"""
from datetime import date

from PyQt5.QtCore import QObject, pyqtSignal

from config import DAILY_TESTS_TARGET, DAILY_WORDS_TARGET
from database import transaction


class VocabularyService(QObject):
    vocabulary_changed = pyqtSignal()   # словарь изменился

    def __init__(self, words_repo):
        super().__init__()
        self.repo = words_repo
        self.vocabulary = []
        self._load()

    def _load(self):
        self.vocabulary = self.repo.all()

    def add_word(self, english, russian):
        """Добавляет слово. Если такое уже есть — DuplicateWordError (окно покажет ошибку)."""
        self.repo.add(english, russian)
        self._load()
        self.vocabulary_changed.emit()

    def delete_word(self, word):
        word_id = self.word_id(word)
        if word_id:
            self.repo.delete(word_id)
            self._load()
            self.vocabulary_changed.emit()

    def word_id(self, word):
        """id слова: из словаря-записи или по английскому написанию."""
        if isinstance(word, dict):
            return word.get('id')
        return next((w['id'] for w in self.vocabulary if w['english'] == word), None)


class ProgressService(QObject):
    progress_changed = pyqtSignal()   # прогресс изменился — пора обновить экран

    def __init__(self, conn, progress_repo, user_id, vocabulary_service):
        super().__init__()
        self.conn = conn
        self.repo = progress_repo
        self.user_id = user_id
        self.vocab = vocabulary_service
        self.data = self.repo.load(user_id)     # счётчики из таблицы user_progress
        self.learned_ids = set()
        self.quiz_session_id = None
        self._refresh_learned()
        self.vocab.vocabulary_changed.connect(self._refresh_learned)

    # ── Выученные слова ───────────────────────────────────────────────
    def _refresh_learned(self):
        self.learned_ids = self.repo.learned_ids(self.user_id)
        self.data['words_learned'] = [w['english'] for w in self.vocab.vocabulary
                                      if w['id'] in self.learned_ids]

    def is_learned(self, word):
        return self.vocab.word_id(word) in self.learned_ids

    def mark_learned(self, word):
        """Слот для сигнала FlashcardsTab.word_learned."""
        word_id = self.vocab.word_id(word)
        with transaction(self.conn):            # отметка слова + счётчики — вместе
            if word_id:
                self.repo.mark_learned(self.user_id, word_id)
            self._refresh_learned()
            self.repo.save(self.user_id, self.data)
        self.progress_changed.emit()

    # ── Тесты ─────────────────────────────────────────────────────────
    def start_quiz(self, mode):
        """Слот для сигнала QuizTab.quiz_started."""
        self.quiz_session_id = self.repo.start_quiz(self.user_id, mode)

    def record_answer(self, correct):
        """Слот для сигнала QuizTab.answer_given."""
        self.data['total_answers'] += 1
        if correct:
            self.data['correct_answers'] += 1
        self.save()

    def finish_quiz(self, score, questions):
        """Слот для сигнала QuizTab.quiz_finished."""
        with transaction(self.conn):            # история теста + счётчик тестов — вместе
            self.data['tests_completed'] += 1
            if self.quiz_session_id:
                self.repo.finish_quiz(self.quiz_session_id, score, questions)
            self.repo.save(self.user_id, self.data)
        self.quiz_session_id = None
        self.progress_changed.emit()

    def abandon_quiz(self):
        """Слот для сигнала QuizTab.quiz_stopped: тест брошен, в истории он останется незавершённым."""
        self.quiz_session_id = None

    # ── Серия дней и дневная цель ─────────────────────────────────────
    def update_streak(self, today=None):
        """Вызывается при входе: считает дни подряд и начинает новый день для дневной цели."""
        p = self.data
        today = today or date.today()
        today_str = today.isoformat()
        last = p.get('last_login_date', '') or ''
        try:
            previous = date.fromisoformat(last) if last else None
        except ValueError:
            previous = None
        if last != today_str:
            came_yesterday = previous is not None and (today - previous).days == 1
            p['streak'] = p.get('streak', 0) + 1 if came_yesterday else 1
            p['last_login_date'] = today_str
        if p.get('daily_date') != today_str:
            p['daily_date'] = today_str
            p['daily_words_start'] = len(p['words_learned'])
            p['daily_tests_start'] = p.get('tests_completed', 0)
        self.save()

    def daily_progress(self):
        p = self.data
        return {
            'words_target': DAILY_WORDS_TARGET,
            'tests_target': DAILY_TESTS_TARGET,
            'words_done': max(0, len(p.get('words_learned', [])) - p.get('daily_words_start', 0)),
            'tests_done': max(0, p.get('tests_completed', 0) - p.get('daily_tests_start', 0)),
        }

    def save(self):
        self.repo.save(self.user_id, self.data)
