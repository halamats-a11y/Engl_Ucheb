import tempfile
import unittest
from datetime import date

from PyQt5.QtCore import QCoreApplication

from db.connection import connect, init_db, transaction
from db.repository import ProgressRepository, UserRepository, WordRepository
from services.progress_service import ProgressService
from services.vocabulary_service import VocabularyService

app = QCoreApplication.instance() or QCoreApplication([])


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.c = connect(tempfile.mktemp(suffix='.db'))
        init_db(self.c, seed=False)
        self.w = WordRepository(self.c)

    def tearDown(self):
        self.c.close()

    def test_rollback_on_error(self):
        with self.assertRaises(RuntimeError):
            with transaction(self.c):
                self.w.add('one', 'один')
                raise RuntimeError('сбой посередине')
        self.assertEqual(self.w.count(), 0)     # ничего не сохранилось

    def test_commit_once(self):
        with transaction(self.c):
            self.w.add('one', 'один')
            self.w.add('two', 'два')
        self.assertEqual(self.w.count(), 2)


class ProgressServiceTests(unittest.TestCase):
    def setUp(self):
        self.c = connect(tempfile.mktemp(suffix='.db'))
        init_db(self.c, seed=False)
        words = WordRepository(self.c)
        for en, ru in [('cat', 'кошка'), ('dog', 'собака'), ('sun', 'солнце'), ('sea', 'море')]:
            words.add(en, ru)
        self.user = UserRepository(self.c).create('a', 'abcd')
        self.repo = ProgressRepository(self.c)
        self.vocab = VocabularyService(words)
        self.s = ProgressService(self.c, self.repo, self.user['id'], self.vocab)
        self.changed = 0
        self.s.progress_changed.connect(self._on_changed)

    def _on_changed(self):
        self.changed += 1

    def tearDown(self):
        self.c.close()

    def test_mark_learned_saves_and_signals(self):
        self.s.mark_learned(self.vocab.vocabulary[0])
        self.assertTrue(self.s.is_learned('cat'))
        self.assertEqual(self.repo.learned_count(self.user['id']), 1)
        self.assertEqual(self.changed, 1)

    def test_quiz_flow(self):
        self.s.start_quiz('classic')
        self.s.record_answer(True)
        self.s.record_answer(False)
        self.s.finish_quiz(1, 2)
        p = self.repo.load(self.user['id'])
        self.assertEqual((p['correct_answers'], p['total_answers'], p['tests_completed']), (1, 2, 1))
        q = self.repo.recent_quizzes(self.user['id'])[0]
        self.assertEqual((q['score'], q['questions']), (1, 2))
        self.assertIsNotNone(q['finished_at'])

    def test_streak(self):
        self.s.update_streak(date(2026, 1, 1))
        self.s.update_streak(date(2026, 1, 2))
        self.assertEqual(self.s.data['streak'], 2)
        self.s.update_streak(date(2026, 1, 5))  # пропустил дни — серия заново
        self.assertEqual(self.s.data['streak'], 1)

    def test_daily_progress(self):
        self.s.update_streak(date(2026, 1, 1))
        self.s.mark_learned('cat')
        self.s.mark_learned('dog')
        self.assertEqual(self.s.daily_progress()['words_done'], 2)


if __name__ == '__main__':
    unittest.main()
