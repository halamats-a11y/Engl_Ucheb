"""
vocabulary_service.py — словарь: список слов, добавление и удаление.

Окна не обращаются к базе напрямую: они вызывают методы сервиса.
После любого изменения сервис отправляет сигнал vocabulary_changed,
и главное окно само обновляет таблицу и счётчик слов.
"""
from PyQt5.QtCore import QObject, pyqtSignal


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
