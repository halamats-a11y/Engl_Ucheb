import tempfile, unittest
from db.connection import connect, init_db
from db.repository import WordRepository, UserRepository, ProgressRepository, SessionRepository, UserExistsError
class DatabaseTests(unittest.TestCase):
 def setUp(self): self.c=connect(tempfile.mktemp(suffix='.db')); init_db(self.c); self.w=WordRepository(self.c); self.u=UserRepository(self.c); self.p=ProgressRepository(self.c)
 def tearDown(self): self.c.close()
 def test_seed_unique(self): self.assertGreater(self.w.count(),2000); self.assertEqual(self.w.count(),self.c.execute('select count(*) from (select english,russian from words group by english,russian)').fetchone()[0])
 def test_user_password_and_unicode_casefold(self):
  u=self.u.create('Тест','abcd'); self.assertEqual(self.u.authenticate('тест','abcd')['id'],u['id']); self.assertNotEqual(u['password_hash'],'abcd')
  with self.assertRaises(UserExistsError): self.u.create('тест','abcd')
 def test_progress_and_word_relationship(self):
  u=self.u.create('a','abcd'); wid=self.w.add('unusual','особенный'); self.p.mark_learned(u['id'],wid); self.p.mark_learned(u['id'],wid); self.assertEqual(self.p.learned_count(u['id']),1)
 def test_search_cyrillic(self): self.w.add('veil','Защитный покров'); self.assertEqual(self.w.find_by_russian('ЗАЩИТНЫЙ ПОКРОВ')['english'],'veil'); self.assertTrue(self.w.search('ЗАЩИТНЫЙ'))
 def test_session(self):
  u=self.u.create('a','abcd'); s=SessionRepository(self.c); s.start(u['id']); self.assertEqual(s.current_user(),u['id']); s.clear(); self.assertIsNone(s.current_user())
if __name__=='__main__': unittest.main()
