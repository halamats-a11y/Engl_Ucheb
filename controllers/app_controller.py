from PyQt5.QtWidgets import QApplication
from db.connection import connect, init_db
from db.repository import WordRepository, UserRepository, ProgressRepository, SessionRepository
from views.login_window import LoginWindow
from views.main_window import LanguageLearningApp

class AppController:
 def __init__(self):
  self.conn=connect(); init_db(self.conn)
  self.words=WordRepository(self.conn); self.users=UserRepository(self.conn); self.progress=ProgressRepository(self.conn); self.sessions=SessionRepository(self.conn)
  self.main_window=None; self.login_window=None
  uid=self.sessions.current_user(); user=self.users.get_by_id(uid) if uid else None
  if user: self.on_login(user)
  else: self.show_login()
 def show_login(self):
  self.login_window=LoginWindow(self.on_login,self.users,self.sessions); self.login_window.show()
 def on_login(self,user):
  if self.login_window: self.login_window.close()
  p=self.progress.load(user['id'])
  self.main_window=LanguageLearningApp(user,self.words.all(),p,self.words,self.progress,self.users,self.progress)
  self.main_window._on_logout=self.on_logout; self.main_window.show()
 def on_logout(self):
  uid=self.main_window.user_id if self.main_window else None
  if uid: self.sessions.clear_for_user(uid)
  self.show_login()
 def quit(self): self.conn.close()

def main():
 import sys
 from PyQt5.QtWidgets import QApplication
 from PyQt5.QtGui import QPalette,QColor
 app=QApplication(sys.argv); app.setStyle('Fusion'); palette=QPalette(); palette.setColor(QPalette.Window,QColor(245,245,245)); app.setPalette(palette)
 controller=AppController(); app.aboutToQuit.connect(controller.quit); sys.exit(app.exec_())
