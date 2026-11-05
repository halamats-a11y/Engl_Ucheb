from datetime import datetime
from utils.password_utils import hash_password, verify_password, needs_rehash
class DuplicateWordError(ValueError): pass
class UserExistsError(ValueError): pass
class AuthError(ValueError): pass
class WordRepository:
 def __init__(self,c): self.c=c
 def all(self): return [dict(r) for r in self.c.execute('SELECT id,english,russian FROM words ORDER BY id')]
 def count(self): return self.c.execute('SELECT count(*) FROM words').fetchone()[0]
 def by_id(self,i):
  r=self.c.execute('SELECT id,english,russian FROM words WHERE id=?',(i,)).fetchone(); return dict(r) if r else None
 def find_by_english(self,s):
  r=self.c.execute('SELECT id,english,russian FROM words WHERE english_norm=?',(s.strip().lower(),)).fetchone(); return dict(r) if r else None
 def find_by_russian(self,s):
  r=self.c.execute('SELECT id,english,russian FROM words WHERE russian_norm=?',(s.strip().lower(),)).fetchone(); return dict(r) if r else None
 def search(self,s):
  q='%'+s.lower().replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%'
  return [dict(r) for r in self.c.execute("SELECT id,english,russian FROM words WHERE english_norm LIKE ? ESCAPE '\\' OR russian_norm LIKE ? ESCAPE '\\' ORDER BY id",(q,q))]
 def add(self,en,ru):
  try:
   cur=self.c.execute('INSERT INTO words(english,russian,english_norm,russian_norm) VALUES(?,?,?,?)',(en.strip(),ru.strip(),en.strip().lower(),ru.strip().lower())); self.c.commit(); return cur.lastrowid
  except Exception as e:
   if 'UNIQUE' in str(e): raise DuplicateWordError from e
   raise
 def delete(self,i): self.c.execute('DELETE FROM words WHERE id=?',(i,)); self.c.commit()
class UserRepository:
 def __init__(self,c): self.c=c
 def get_by_username(self,u):
  r=self.c.execute('SELECT * FROM users WHERE username_norm=?',(u.strip().lower(),)).fetchone(); return dict(r) if r else None
 def get_by_id(self,i):
  r=self.c.execute('SELECT * FROM users WHERE id=?',(i,)).fetchone(); return dict(r) if r else None
 def exists(self,u): return self.get_by_username(u) is not None
 def create(self,u,p):
  if self.exists(u): raise UserExistsError(u)
  now=datetime.now().isoformat(); cur=self.c.execute('INSERT INTO users(username,username_norm,password_hash,created_at) VALUES(?,?,?,?)',(u,u.strip().lower(),hash_password(p),now)); self.c.execute('INSERT INTO user_progress(user_id) VALUES(?)',(cur.lastrowid,)); self.c.commit(); return self.get_by_id(cur.lastrowid)
 def authenticate(self,u,p):
  user=self.get_by_username(u)
  if not user or not verify_password(p,user['password_hash']): raise AuthError('Неверное имя пользователя или пароль')
  return user
 def rehash_if_needed(self,user,p):
  if needs_rehash(user['password_hash']): self.c.execute('UPDATE users SET password_hash=? WHERE id=?',(hash_password(p),user['id'])); self.c.commit()
 def change_password(self,user_id,p): self.c.execute('UPDATE users SET password_hash=? WHERE id=?',(hash_password(p),user_id)); self.c.commit()
class ProgressRepository:
 def __init__(self,c): self.c=c
 def ensure(self,uid): self.c.execute('INSERT OR IGNORE INTO user_progress(user_id) VALUES(?)',(uid,)); self.c.commit()
 def load(self,uid):
  self.ensure(uid); return dict(self.c.execute('SELECT * FROM user_progress WHERE user_id=?',(uid,)).fetchone())
 def save(self,uid,p):
  cols=('tests_completed','correct_answers','total_answers','streak','last_login_date','daily_date','daily_words_start','daily_tests_start')
  self.c.execute('UPDATE user_progress SET '+','.join(x+'=?' for x in cols)+' WHERE user_id=?',tuple(p.get(x,0 if x not in ('last_login_date','daily_date') else '') for x in cols)+(uid,)); self.c.commit()
 def learned_ids(self,uid): return {r[0] for r in self.c.execute('SELECT word_id FROM learned_words WHERE user_id=?',(uid,))}
 def learned_count(self,uid): return self.c.execute('SELECT count(*) FROM learned_words WHERE user_id=?',(uid,)).fetchone()[0]
 def mark_learned(self,uid,wid): self.c.execute('INSERT OR IGNORE INTO learned_words(user_id,word_id) VALUES(?,?)',(uid,wid)); self.c.commit()
 def unmark_learned(self,uid,wid): self.c.execute('DELETE FROM learned_words WHERE user_id=? AND word_id=?',(uid,wid)); self.c.commit()
 def start_quiz(self,uid,mode):
  cur=self.c.execute('INSERT INTO quiz_sessions(user_id,mode,started_at) VALUES(?,?,?)',(uid,mode,datetime.now().isoformat())); self.c.commit(); return cur.lastrowid
 def finish_quiz(self,i,score,questions):
  r=self.c.execute('SELECT user_id FROM quiz_sessions WHERE id=?',(i,)).fetchone()
  self.c.execute('UPDATE quiz_sessions SET score=?,questions=?,finished_at=? WHERE id=?',(score,questions,datetime.now().isoformat(),i))
  self.c.commit()
 def recent_quizzes(self,uid,limit=20): return [dict(r) for r in self.c.execute('SELECT * FROM quiz_sessions WHERE user_id=? ORDER BY id DESC LIMIT ?',(uid,limit))]
class SessionRepository:
 def __init__(self,c): self.c=c
 def start(self,uid):
  import secrets
  self.c.execute('INSERT OR REPLACE INTO sessions VALUES(?,?,?)',(uid,secrets.token_hex(32),datetime.now().isoformat())); self.c.commit()
 def current_user(self):
  r=self.c.execute('SELECT user_id FROM sessions ORDER BY created_at DESC LIMIT 1').fetchone(); return r[0] if r else None
 def clear(self): self.c.execute('DELETE FROM sessions'); self.c.commit()
 def clear_for_user(self,uid): self.c.execute('DELETE FROM sessions WHERE user_id=?',(uid,)); self.c.commit()
