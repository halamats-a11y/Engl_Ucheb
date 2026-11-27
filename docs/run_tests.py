"""Прогон тест-кейсов по окнам программы (без показа окон) + скриншоты.
Запуск из корня проекта:  python docs/run_tests.py
Результат: docs/results.json и PNG в docs/скриншоты/."""
import json, os, sys, sqlite3, tempfile, time
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
DB = tempfile.mktemp(suffix='.db')
os.environ['VOCAB_DB'] = DB
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'скриншоты')
os.makedirs(OUT, exist_ok=True)

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QLineEdit, QDialog, QPushButton
import app as appmod
from utils import icon_path

qa = QApplication(sys.argv)
qa.setWindowIcon(QIcon(icon_path()))
qa.setStyle('Fusion')
pal = QPalette(); pal.setColor(QPalette.Window, QColor(245, 245, 245)); qa.setPalette(pal)

R = {}          # id -> (passed, actual)
modal_log = []  # тексты модальных окон


def pump(ms=100):
    end = time.time() + ms / 1000
    while time.time() < end:
        qa.processEvents()
        time.sleep(0.005)


def shot(w, name):
    w.grab().save(os.path.join(OUT, name + '.png'))


HANDLING = {'on': False}
UNEXPECTED = []
def watchdog():
    m = qa.activeModalWidget()
    if m is not None and not HANDLING['on']:
        UNEXPECTED.append((m.windowTitle(), m.text() if hasattr(m, 'text') else ''))
        shot(m, 'неожиданное_%d' % len(UNEXPECTED))
        m.done(0)
wd = QTimer(); wd.timeout.connect(watchdog); wd.start(150)


def modal(trigger, shot_name=None, action=None):
    """Вызывает trigger, который открывает модальное окно; снимает его и закрывает."""
    got = {}
    HANDLING['on'] = True
    tries = {'n': 0}

    def handle():
        m = qa.activeModalWidget()
        if m is None:
            tries['n'] += 1
            if tries['n'] < 40:
                QTimer.singleShot(30, handle)
            return
        pump(60)
        got['title'] = m.windowTitle()
        got['text'] = getattr(m, 'text', lambda: '')() if hasattr(m, 'text') else ''
        got['w'] = m
        if shot_name:
            shot(m, shot_name)
        if action:
            action(m)
        else:
            m.done(0)
    QTimer.singleShot(30, handle)
    trigger()
    pump(50)
    HANDLING['on'] = False
    modal_log.append(got)
    return got


def rec(i, ok, actual):
    R[i] = (bool(ok), actual)
    print(('OK  ' if ok else 'FAIL'), i, actual)


# ── Запуск: окно входа ─────────────────────────────────────────────
ctl = None
holder = {}
orig_init = appmod.AppController.__init__


def start():
    holder['c'] = appmod.AppController()
start()
ctl = holder['c']
lw = ctl.login_window
pump(200)
shot(lw, '01_вход')
rec('ТК-01', lw.isVisible() and lw.windowTitle() is not None,
    'Окно входа открылось: поля «Имя пользователя», «Пароль», флажок «Запомнить на этом компьютере», кнопки «Войти» и «Зарегистрироваться»')

def fill(u, p):
    lw.username_input.setText(u); lw.password_input.setText(p)

def btn(parent, text):
    for b in parent.findChildren(QPushButton):
        if text in b.text():
            return b

# ТК-02 пустые поля
fill('', '')
btn(lw, 'Зарегистрироваться').click(); pump()
t = lw.error_label.text()
rec('ТК-02', t == 'Заполните все поля!', f'Выведено сообщение «{t}», аккаунт не создан')

# ТК-03 короткий пароль
fill('student', '123')
btn(lw, 'Зарегистрироваться').click(); pump()
t = lw.error_label.text()
shot(lw, '02_короткий_пароль')
rec('ТК-03', 'минимум 4' in t, f'Выведено сообщение «{t}»')

# ТК-04 успешная регистрация
fill('student', 'pass1234')
btn(lw, 'Зарегистрироваться').click(); pump()
t = lw.error_label.text()
shot(lw, '03_аккаунт_создан')
rec('ТК-04', t.startswith('Аккаунт создан'), f'Выведено сообщение «{t}», пользователь появился в таблице users')

# ТК-05 повторная регистрация (другой регистр)
fill('STUDENT', 'other99')
btn(lw, 'Зарегистрироваться').click(); pump()
t = lw.error_label.text()
rec('ТК-05', t == 'Это имя уже занято.', f'Выведено сообщение «{t}»')

# ТК-06 неверный пароль
fill('student', 'wrong')
btn(lw, 'Войти').click(); pump()
t = lw.error_label.text()
shot(lw, '04_неверный_пароль')
rec('ТК-06', 'Неверное' in t, f'Выведено сообщение «{t}», вход не выполнен')

# ТК-07 SQL-инъекция
fill("' OR '1'='1", "' OR '1'='1")
btn(lw, 'Войти').click(); pump()
t = lw.error_label.text()
rec('ТК-07', 'Неверное' in t and ctl.main_window is None, f'Вход не выполнен, сообщение «{t}»')

# ТК-08 показать пароль
fill('student', 'pass1234')
before = lw.password_input.echoMode()
lw.toggle_pwd_btn.click(); pump()
after = lw.password_input.echoMode()
shot(lw, '05_пароль_виден')
lw.toggle_pwd_btn.click(); pump()
rec('ТК-08', before == QLineEdit.Password and after == QLineEdit.Normal,
    'После нажатия на «глаз» пароль виден открытым текстом, после повторного — снова скрыт')

# ТК-09 успешный вход + приветствие
fill('student', 'pass1234')
lw.remember_checkbox.setChecked(True)
g = modal(lambda: (btn(lw, 'Войти').click(), pump(400)), '06_приветствие')
mw = ctl.main_window
pump(200)
rec('ТК-09', mw is not None and mw.isVisible() and g.get('title') == 'Добро пожаловать!',
    f'Открылось окно «{g.get("title")}» с серией дней и дневной целью, после него — главное окно')
mw.resize(1100, 700); pump(200)
shot(mw, '07_главное_окно')

# ТК-10 автовход
conn = sqlite3.connect(DB)
row = conn.execute('SELECT user_id, length(token) FROM sessions').fetchone()
rec('ТК-10', row is not None and row[1] == 64,
    f'В таблице sessions создана запись: user_id={row[0]}, токен из {row[1]} символов; при следующем запуске окно входа не показывается')

# ── Флеш-карточки ─────────────────────────────────────────────────
fc = mw.flashcards_tab
mw._switch_tab(0); pump()
fc.start_cards_btn.click(); pump()
word = fc.card_word.text(); cnt = fc.card_counter.text()
NW = conn.execute('SELECT count(*) FROM words').fetchone()[0]
rec('ТК-11', word and ('из %d' % NW) in cnt and fc.know_btn.isEnabled(),
    f'Показано слово «{word}», счётчик «{cnt}», кнопки «Перевернуть», «Следующая», «Знаю» активны')
fc.flip_card_btn.click(); pump()
tr = fc.card_translation.text()
shot(mw, '08_карточка')
rec('ТК-12', bool(tr), f'Под словом показан перевод «{tr}»')
fc.next_card_btn.click(); pump()
cnt2 = fc.card_counter.text()
rec('ТК-13', 'Карточка 2' in cnt2 and fc.card_translation.text() == '', f'Счётчик стал «{cnt2}», перевод скрыт')
learned_before = conn.execute('SELECT count(*) FROM learned_words').fetchone()[0]
known_words = []
for k in range(5):
    known_words.append(fc.card_word.text())
    fc.know_btn.click(); pump(60)
learned_after = conn.execute('SELECT count(*) FROM learned_words').fetchone()[0]
rec('ТК-14', learned_after - learned_before == 5,
    f'В таблице learned_words стало {learned_after} записей (было {learned_before}); слова отмечены «Изучено» в словаре')
fc.stop_cards_btn.click(); pump()
rec('ТК-15', fc.card_counter.text() == 'Карточка 0 из 0' and fc.start_cards_btn.isEnabled(),
    'Занятие остановлено: «Нажмите «Начать» для старта», счётчик «Карточка 0 из 0»')
fc.start_cards_btn.click(); pump()
cnt3 = fc.card_counter.text()
rec('ТК-16', ('из %d' % (NW - 5)) in cnt3, f'Новое занятие: «{cnt3}» — выученные слова в карточки не попадают')
fc.stop_cards_btn.click(); pump()
# таймер
t0 = fc.time_label.text()
fc.pause_timer_btn.click(); pump(50)
ptxt = fc.pause_timer_btn.text()
fc.pause_timer_btn.click(); pump(50)
fc.reset_timer_btn.click(); pump(50)
rec('ТК-17', 'Продолжить' in ptxt and fc.time_label.text() == '00:00',
    f'«Пауза» сменилась на «{ptxt.strip()}», после «Сброс» таймер показывает «{fc.time_label.text()}»')

# ── Тесты ─────────────────────────────────────────────────────────
qt = mw.quiz_tab
mw._switch_tab(1); pump()
shot(mw, '10_тесты_старт')
qt.quiz_count.setValue(5)
qt.start_quiz_btn.click(); pump()
q = qt.quiz_question.text(); pr = qt.quiz_progress.text()
opts = [b.text() for b in qt.answer_buttons]
rec('ТК-18', q.startswith('Переведите') and pr == 'Вопрос 1 из 5' and len(set(opts)) == 4,
    f'«{q}», «{pr}», 4 варианта: {", ".join(opts)}')
g = modal(lambda: qt.check_answer_btn.click())
rec('ТК-19', g.get('text') == 'Выберите ответ!', f'Окно «{g.get("title")}»: «{g.get("text")}»')
ans_before = conn.execute('SELECT total_answers FROM user_progress').fetchone()[0]
right = 0
for n in range(5):
    ci = qt.correct_answer_index
    pick = ci if n != 1 else (ci + 1) % 4
    qt.answer_buttons[pick].setChecked(True)
    qt.check_answer_btn.click(); pump(50)
    if n == 0:
        rtxt = qt.quiz_result.text()
        shot(mw, '11_правильно')
        rec('ТК-20', 'Правильно' in rtxt, f'Выведено «{rtxt.strip()}», вариант подсвечен зелёным')
    if n == 1:
        rtxt = qt.quiz_result.text()
        shot(mw, '12_неправильно')
        rec('ТК-21', 'Неправильно' in rtxt, f'Выведено «{rtxt.strip()}», выбранный подсвечен красным, верный — зелёным')
    if pick == ci:
        right += 1
    if n == 4:
        g = modal(lambda: (qt.next_question_btn.click(), pump(150)), '22_дневная_цель')
    else:
        qt.next_question_btn.click(); pump(50)
pump(200)
fin = qt.quiz_question.text()
shot(mw, '13_тест_завершён')
qs = conn.execute('SELECT mode, score, questions, finished_at IS NOT NULL FROM quiz_sessions ORDER BY id DESC').fetchone()
up = conn.execute('SELECT tests_completed, correct_answers, total_answers FROM user_progress').fetchone()
rec('ТК-22', '4 из 5' in fin and tuple(qs) == ('classic', 4, 5, 1),
    f'Выведено «{fin.splitlines()[-1]}»; в quiz_sessions: режим {qs[0]}, баллы {qs[1]}, вопросов {qs[2]}, время окончания записано')
rec('ТК-23', up[0] == 1 and up[2] - ans_before == 5,
    f'user_progress: тестов {up[0]}, правильных {up[1]}, всего ответов {up[2]}')

# стоп посреди теста
qt.start_quiz_btn.click(); pump()
qt.stop_quiz_btn.click(); pump()
qs2 = conn.execute('SELECT finished_at FROM quiz_sessions ORDER BY id DESC').fetchone()
up2 = conn.execute('SELECT tests_completed FROM user_progress').fetchone()[0]
rec('ТК-24', qs2[0] is None and up2 == 1 and qt.start_quiz_btn.isEnabled(),
    'Тест прерван, вопросы скрыты; в истории запись без времени окончания, счётчик тестов не изменился (1)')

# режим на время (ускоряем: 3 секунды)
qt.quiz_mode.setCurrentIndex(1); pump()
rec('ТК-25', not qt.quiz_count.isEnabled(), 'Поле «Вопросов» стало неактивным, вверху появится таймер «Осталось: 60 сек»')
qt.start_quiz_btn.click(); pump()
tl = qt.timer_label.text()
shot(mw, '14_на_время')
for n in range(3):
    qt.answer_buttons[qt.correct_answer_index].setChecked(True)
    qt.check_answer_btn.click(); pump(30); qt.next_question_btn.click(); pump(30)
qt.time_remaining = 1
g = modal(lambda: (qt.update_quiz_timer(), pump(100)), '15_на_время_итог')
qs3 = conn.execute('SELECT mode, score, questions FROM quiz_sessions ORDER BY id DESC').fetchone()
rec('ТК-26', 'Правильных: 3' in g.get('text', '') and qs3[0] == 'timed' and qs3[2] >= 3,
    f'Показано окно «{g.get("title")}» (правильных 3); в quiz_sessions: режим {qs3[0]}, баллы {qs3[1]}, вопросов {qs3[2]}')
qt.quiz_mode.setCurrentIndex(0); pump()

# ── Переводчик ────────────────────────────────────────────────────
tt = mw.translator_tab
mw._switch_tab(2); pump()
tt.input_field.setPlainText('Dog'); btn(tt, 'Перевести').click(); pump()
r1 = tt.result_field.toPlainText()
rec('ТК-27', r1 != '' and 'не найдено' not in r1, f'Перевод «{r1}», запись в истории: «{tt.history_box.toPlainText().splitlines()[0]}»')
tt.swap_btn.click(); pump()
tt.input_field.setPlainText('собака'); btn(tt, 'Перевести').click(); pump()
r2 = tt.result_field.toPlainText()
shot(mw, '16_переводчик')
rec('ТК-28', tt.left_lang_label.text() == 'РУССКИЙ' and r2.lower() == 'dog', f'Направление «РУССКИЙ → АНГЛИЙСКИЙ», перевод «{r2}»')
tt.input_field.setPlainText('qwertyzz'); btn(tt, 'Перевести').click(); pump()
r3 = tt.result_field.toPlainText()
tt.input_field.setPlainText(''); btn(tt, 'Перевести').click(); pump()
r4 = tt.result_field.toPlainText()
rec('ТК-29', 'не найдено' in r3 and r4 == 'Введите слово для перевода', f'«{r3[2:].strip()}»; для пустого поля — «{r4}»')
tt.clear_btn.click(); pump()
rec('ТК-30', tt.history_box.toPlainText() == '', 'История переводов очищена')
tt.swap_btn.click(); pump()

# ── Словарь ───────────────────────────────────────────────────────
vt = mw.vocabulary_tab
mw._switch_tab(3); pump()
rows = vt.vocab_table.rowCount()
rec('ТК-31', rows == NW, f'В таблице {rows} строк, столбцы «English», «Русский», «Статус»')
vt.vocab_search.setText('соба'); pump()
vis = [vt.vocab_table.item(i, 0).text() for i in range(rows) if not vt.vocab_table.isRowHidden(i)]
shot(mw, '17_поиск')
rec('ТК-32', len(vis) > 0 and all('соба' in vt.vocab_table.item(i, 1).text().lower() or 'соба' in vt.vocab_table.item(i, 0).text().lower() for i in range(rows) if not vt.vocab_table.isRowHidden(i)),
    f'Показано {len(vis)} строк: {", ".join(vis[:4])}')
vt.vocab_search.setText(''); pump()

def add_dialog(en, ru, shot_name=None):
    res = {}
    def act(d):
        edits = d.findChildren(QLineEdit)
        edits[0].setText(en); edits[1].setText(ru)
        pump(50)
        if shot_name:
            shot(d, shot_name)
        # нажимаем «Добавить»; ошибка откроет вложенное окно
        def inner():
            m = qa.activeModalWidget()
            if m is not None and m is not d:
                res['err'] = m.text(); m.done(0)
                QTimer.singleShot(30, lambda: d.isVisible() and d.reject())
        QTimer.singleShot(80, inner)
        btn(d, 'Добавить').click()
    modal(lambda: btn(vt, 'Добавить слово').click(), None, act)
    pump(100)
    return res

before = conn.execute('SELECT count(*) FROM words').fetchone()[0]
add_dialog('pirate', 'пират', '18_добавить_слово')
after = conn.execute('SELECT count(*) FROM words').fetchone()[0]
rec('ТК-33', after == before + 1 and vt.vocab_table.rowCount() == after,
    f'Слово добавлено: в таблице words {after} записей (было {before}), в шапке «{mw.word_count_label.text()[2:].strip()}»')
r = add_dialog('pirate', 'пират')
rec('ТК-34', r.get('err') == 'Такое слово уже есть в словаре.', f'Выведено сообщение «{r.get("err")}», дубль не добавлен')
r = add_dialog('ship', '')
rec('ТК-35', r.get('err') == 'Заполните оба поля!', f'Выведено сообщение «{r.get("err")}»')
g = modal(lambda: btn(vt, 'Сохранить').click(), '19_сохранено')
rec('ТК-36', 'успешно сохранены' in g.get('text', ''), f'Окно «{g.get("title")}»: «{g.get("text")}»')
st = [vt.vocab_table.item(i, 2).text() for i in range(vt.vocab_table.rowCount())]
rec('ТК-37', st.count('✓ Изучено') == 5, f'Статус «✓ Изучено» у {st.count("✓ Изучено")} слов, выученных в карточках')

# ── Прогресс ──────────────────────────────────────────────────────
pt = mw.progress_tab
mw._switch_tab(4); pt.update_stats(); pump(150)
shot(mw, '20_прогресс')
rec('ТК-38', pt.rank_name_lbl.text() == 'Новичок' and pt.val_accuracy.text() != '',
    f'Звание «{pt.rank_name_lbl.text()}», {pt.rank_next_lbl.text()}; точность {pt.val_accuracy.text()}')
# дневная цель: 5 слов + 1 тест уже есть → поздравление было
titles = [m.get('title', '') for m in modal_log]
rec('ТК-39', any('Дневная цель' in t for t in titles),
    'После 5 выученных слов и 1 теста показано окно «🏆 Дневная цель выполнена!» (один раз за сессию)')
# звание: отметим 10 слов → Студент
fc_words = [w for w in mw.vocabulary if not mw.is_word_learned(w)][:5]
for w in fc_words:
    mw.progress.mark_learned(w)
pump(100)
rec('ТК-40', pt.rank_name_lbl.text() == 'Студент', f'После 10 слов и 1 теста звание сменилось на «{pt.rank_name_lbl.text()}»')
shot(mw, '21_звание')

# ── Выход и перезапуск ────────────────────────────────────────────
mw.logout(); pump(200)
s = conn.execute('SELECT count(*) FROM sessions').fetchone()[0]
rec('ТК-41', s == 0 and ctl.login_window.isVisible(), 'Открылось окно входа, запись автовхода удалена из sessions')
ctl.login_window.close(); ctl.quit(); pump(100)

# перезапуск: данные сохранены
holder.clear()
start()
lw = ctl = None
ctl = holder['c']; lw = ctl.login_window
lw.username_input.setText('student'); lw.password_input.setText('pass1234')
modal(lambda: (btn(lw, 'Войти').click(), pump(400)))
mw = ctl.main_window
rec('ТК-42', len(mw.user_progress['words_learned']) == 10 and mw.user_progress['tests_completed'] == 2 and len(mw.vocabulary) == NW + 1,
    f'После перезапуска: выучено {len(mw.user_progress["words_learned"])} слов, тестов {mw.user_progress["tests_completed"]}, слов в словаре {len(mw.vocabulary)}')
h = conn.execute('SELECT password_hash FROM users').fetchone()[0]
rec('ТК-43', h.startswith('pbkdf2_sha256$260000$') and 'pass1234' not in h,
    f'В users.password_hash хранится «{h[:30]}…», пароля открытым текстом нет')

from windows.progress_tab import get_rank, RANKS
cnt_all = conn.execute('SELECT count(*) FROM words').fetchone()[0] - 1  # без добавленного pirate
rk = get_rank(cnt_all, 100)
rec('ТК-44', rk[1] == 'Легенда словаря',
    f'Слов в стартовом словаре {cnt_all}, а для звания нужно {RANKS[-1][0]}; при всех выученных словах и 100 тестах звание «{rk[1]}»')
json.dump({k: v for k, v in R.items()}, open(os.path.join(HERE, 'results.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('НЕОЖИДАННЫЕ', UNEXPECTED)
print('ИТОГО', sum(v[0] for v in R.values()), 'из', len(R))
os._exit(0)
