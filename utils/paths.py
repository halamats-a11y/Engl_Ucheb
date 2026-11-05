import os, sys
from pathlib import Path

def project_root():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
def resource_path(relative_path): return str(project_root() / relative_path)
def data_dir():
    if getattr(sys, 'frozen', False):
        if sys.platform == 'win32': base = os.environ.get('APPDATA', str(Path.home()))
        elif sys.platform == 'darwin': base = str(Path.home() / 'Library/Application Support')
        else: base = os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))
        path = Path(base) / 'VocabularyTrainer'
    else: path = project_root() / 'data'
    path.mkdir(parents=True, exist_ok=True)
    return path
def db_path(): return os.environ.get('VOCAB_DB', str(data_dir() / 'app.db'))
def seed_vocabulary_path(): return resource_path('data/vocabulary.json')
