"""Сборка документации в .docx (ГОСТ). Запуск: python3 сборка_docx.py [страницы.json]"""
import json, sys, os
import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

D = os.path.dirname(os.path.abspath(__file__)) + '/'
S = D + 'скриншоты/'
sys.path.insert(0, D)
from данные import FT, NFT, TP, TK, DEF

RES = json.load(open(D + 'results.json', encoding='utf-8'))
PAGES = json.load(open(sys.argv[1], encoding='utf-8')) if len(sys.argv) > 1 else {}
OUT = D + 'Индивидуальный_проект_Тренажёр_английских_слов.docx'

doc = docx.Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21)
sec.left_margin, sec.right_margin = Cm(3), Cm(1.5)
sec.top_margin = sec.bottom_margin = Cm(2)
sec.different_first_page_header_footer = True

st = doc.styles['Normal']
st.font.name = 'Times New Roman'; st.font.size = Pt(14)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
pf = st.paragraph_format
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
pf.first_line_indent = Cm(1.25); pf.line_spacing = 1.5
pf.space_before = Pt(0); pf.space_after = Pt(0)

# номер страницы внизу по центру (кроме титульного)
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.first_line_indent = Cm(0)
r = fp.add_run()
for tag, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
    if tag:
        e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), tag)
    else:
        e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt
    r._r.append(e)
r.font.size = Pt(12)


def para(text='', align=None, indent=None, after=None, before=None, size=None, bold=None, keep=None, label=None):
    p = doc.add_paragraph()
    if label:
        rr = p.add_run(label); rr.bold = True
        if size: rr.font.size = Pt(size)
    if text:
        rr = p.add_run(text)
        if bold is not None: rr.bold = bold
        if size: rr.font.size = Pt(size)
    f = p.paragraph_format
    if align is not None: p.alignment = align
    if indent is not None: f.first_line_indent = Cm(indent)
    if after is not None: f.space_after = Pt(after)
    if before is not None: f.space_before = Pt(before)
    if keep: f.keep_with_next = True
    return p


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def h1(t, new_page=True):
    if new_page:
        page_break()
    p = para(t, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, bold=True, after=12, keep=True)
    return p


def h2(t):
    return para(t, align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.25, bold=True, before=12, after=6, keep=True)


def bullet(t):
    para('– ' + t)


def num(i, t):
    para(f'{i}) ' + t)


fig_n = [0]
def figure(name, cap, width=15):
    fig_n[0] += 1
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    f = p.paragraph_format
    f.first_line_indent = Cm(0); f.space_before = Pt(6); f.keep_with_next = True; f.line_spacing = 1.0
    p.add_run().add_picture(S + name, width=Cm(width))
    para(f'Рисунок {fig_n[0]} — {cap}', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, size=12, after=6)
    return fig_n[0]


tab_n = [0]
def table(cap, head, rows, widths, size=11, bold_first=False):
    tab_n[0] += 1
    para(f'Таблица {tab_n[0]} — {cap}', align=WD_ALIGN_PARAGRAPH.LEFT, indent=0, size=12, before=6, keep=True)
    t = doc.add_table(rows=1, cols=len(head)); t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(head):
        c = t.rows[0].cells[i]; c.text = ''
        rr = c.paragraphs[0].add_run(h); rr.bold = True; rr.font.size = Pt(size)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    # шапка повторяется на каждой странице
    trPr = t.rows[0]._tr.get_or_add_trPr(); th = OxmlElement('w:tblHeader'); th.set(qn('w:val'), 'true'); trPr.append(th)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ''
            lines = v if isinstance(v, list) else [str(v)]
            for k, line in enumerate(lines):
                pp = cells[i].paragraphs[0] if k == 0 else cells[i].add_paragraph()
                rr = pp.add_run(line); rr.font.size = Pt(size)
                if bold_first and i == 0: rr.bold = True
    t.autofit = False
    for i, col in enumerate(t.columns):
        col.width = Cm(widths[i])
    grid = t._tbl.tblGrid
    for i, gc in enumerate(grid.findall(qn('w:gridCol'))):
        gc.set(qn('w:w'), str(int(widths[i] * 567)))
    tblPr = t._tbl.tblPr
    tw = OxmlElement('w:tblW'); tw.set(qn('w:w'), str(int(sum(widths) * 567))); tw.set(qn('w:type'), 'dxa')
    for old in tblPr.findall(qn('w:tblW')): tblPr.remove(old)
    tblPr.append(tw)
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); cs = OxmlElement('w:cantSplit'); trPr.append(cs)
        for i, c in enumerate(row.cells):
            c.width = Cm(widths[i])
            for p in c.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    sp = doc.add_paragraph(); sp.paragraph_format.line_spacing = 1.0
    return tab_n[0]


# ═══════════════ Титульный лист ═══════════════
for t in ('Министерство образования Красноярского края',
          'КГБПОУ «____________________________________»'):
    para(t, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)
for _ in range(5): para('', indent=0)
para('ИНДИВИДУАЛЬНЫЙ ПРОЕКТ', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, bold=True, size=16)
para('по дисциплине «____________________________»', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)
para('', indent=0)
para('Разработка и тестирование информационной системы', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, bold=True)
para('«Тренажёр английских слов»', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, bold=True)
para('Требования, инструкция, тест-сценарий, тест-пакеты, тест-кейсы', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)
for _ in range(4): para('', indent=0)
for t in ('Выполнил: студент группы ________', '______________________________',
          '', 'Проверил: преподаватель', '______________________________'):
    para(t, align=WD_ALIGN_PARAGRAPH.LEFT, indent=9.5)
for _ in range(3): para('', indent=0)
para('Красноярск, 2026', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

# ═══════════════ Содержание ═══════════════
SECTIONS = ['Введение',
            '1 Требования заказчика',
            '2 Инструкция по разработке',
            '3 Руководство пользователя',
            '4 Тест-сценарий',
            '5 Тест-пакеты',
            '6 Тест-кейсы',
            '7 Результаты тестирования',
            'Заключение']
h1('СОДЕРЖАНИЕ')
for s in SECTIONS:
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16.5), alignment=2, leader=1)  # право, точки
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.add_run(f'{s}\t{PAGES.get(s, "")}')

# ═══════════════ Введение ═══════════════
h1('ВВЕДЕНИЕ')
para('Объект разработки — настольное приложение «Тренажёр английских слов». Это информационная система для самостоятельного '
     'изучения английской лексики: флеш-карточки, тесты, переводчик по словарю, личный словарь и статистика прогресса. '
     'У каждого пользователя свой аккаунт и свой прогресс, все данные хранятся в базе SQLite.')
para('Цель проекта — разработать систему по требованиям заказчика и полный комплект документации к ней: требования, '
     'инструкцию по разработке и использованию, тест-сценарий, тест-пакеты и тест-кейсы, а также провести тестирование '
     'и зафиксировать результаты.')
para('Задачи проекта:')
num(1, 'составить функциональные и нефункциональные требования;')
num(2, 'спроектировать архитектуру и базу данных, реализовать приложение;')
num(3, 'написать инструкцию по разработке, сборке и использованию;')
num(4, 'разработать тест-сценарий, тест-пакеты и тест-кейсы;')
num(5, 'выполнить тестирование, описать найденные дефекты.')
para('Исходный код проекта размещён в репозитории GitHub: github.com/halamats-a11y/Engl_Ucheb.')

# ═══════════════ 1 Требования ═══════════════
h1('1 ТРЕБОВАНИЯ ЗАКАЗЧИКА')
h2('1.1 Назначение системы')
para('Система предназначена для студентов и школьников, которые учат английские слова. Она должна помогать '
     'запоминать слова (карточки), проверять знания (тесты), быстро находить перевод (переводчик и словарь) '
     'и поддерживать мотивацию (серия дней, дневная цель, звания). Система работает без интернета на одном компьютере, '
     'но поддерживает несколько пользователей.')
h2('1.2 Пользователи системы')
para('Единственная роль — «Пользователь». Он регистрируется, входит в систему и пользуется всеми разделами. '
     'Данные разных пользователей (выученные слова, тесты, статистика) не смешиваются. Словарь общий для всех.')
h2('1.3 Функциональные требования')
table('Функциональные требования', ['Код', 'Требование', 'Описание'],
      [list(x) for x in FT], [1.9, 3.4, 11.2])
h2('1.4 Нефункциональные требования')
table('Нефункциональные требования', ['Код', 'Требование', 'Описание'],
      [list(x) for x in NFT], [2.1, 3.4, 11.0])

# ═══════════════ 2 Инструкция по разработке ═══════════════
h1('2 ИНСТРУКЦИЯ ПО РАЗРАБОТКЕ')
h2('2.1 Инструменты')
table('Инструменты разработки', ['Инструмент', 'Для чего'], [
    ['Python 3.9+', 'язык программирования'],
    ['PyQt5 5.15', 'графический интерфейс: окна, кнопки, таблицы, сигналы'],
    ['SQLite (модуль sqlite3)', 'база данных в одном файле, отдельный сервер не нужен'],
    ['unittest', 'автотесты базы и сервисов'],
    ['PyInstaller', 'сборка готового файла VocabularyTrainer.exe для Windows'],
    ['Git и GitHub', 'хранение кода и истории изменений'],
    ['Visual Studio Code / PyCharm', 'редактор кода'],
], [5.5, 11.0])
h2('2.2 Архитектура')
para('Приложение разделено на слои. Каждый слой знает только о слое ниже:')
para('окна (windows/) → сервисы (services.py) → база (database.py) → SQLite', align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, bold=True)
bullet('окна только показывают данные и сообщают о действиях пользователя сигналами (word_learned, answer_given, quiz_finished и другие), сами ничего не сохраняют;')
bullet('главное окно подключает сигналы вкладок к методам сервисов;')
bullet('сервисы (VocabularyService, ProgressService) содержат бизнес-логику: отметка слов, учёт тестов, серия дней, дневная цель;')
bullet('database.py — единственное место с SQL-запросами (классы-репозитории WordRepository, UserRepository, ProgressRepository, SessionRepository);')
bullet('app.py собирает всё вместе и управляет переходами «вход → главное окно → выход».')
table('Структура проекта', ['Файл / папка', 'Содержимое'], [
    ['main.py', 'точка входа: python main.py'],
    ['app.py', 'контроллер приложения: база → сервисы → окна'],
    ['config.py', 'настройки: дневная цель, длительность теста «На время», число вопросов'],
    ['database.py', 'подключение, создание таблиц, транзакции, все SQL-запросы'],
    ['services.py', 'бизнес-логика: словарь и прогресс'],
    ['styles.py', 'всё оформление (CSS для Qt)'],
    ['utils.py', 'пути к файлам, хеширование паролей'],
    ['windows/', 'окна: вход, главное окно, 5 вкладок, приветствие'],
    ['data/vocabulary.json', 'стартовый словарь (2094 записи, 2073 уникальных пары)'],
    ['tests/', 'автотесты базы данных и сервисов (11 тестов)'],
], [4.5, 12.0])
h2('2.3 База данных')
para('База SQLite создаётся автоматически при первом запуске (CREATE TABLE IF NOT EXISTS), стартовые слова переносятся '
     'из vocabulary.json, повторы отбрасываются. Включены внешние ключи и журнал WAL. При удалении пользователя '
     'все его данные удаляются каскадно (ON DELETE CASCADE).')
table('Таблицы базы данных', ['Таблица', 'Назначение', 'Основные поля'], [
    ['users', 'пользователи', 'id, username, username_norm (уникально), password_hash, created_at'],
    ['words', 'словарь', 'id, english, russian, UNIQUE(english, russian)'],
    ['learned_words', 'выученные слова (многие ко многим)', 'user_id, word_id — составной ключ'],
    ['user_progress', 'статистика (один к одному)', 'tests_completed, correct_answers, total_answers, streak, daily_*'],
    ['sessions', 'автовход «Запомнить меня»', 'user_id, token (64 символа), created_at'],
    ['quiz_sessions', 'история тестов', 'mode, score, questions, started_at, finished_at'],
], [3.2, 4.8, 8.5])
h2('2.4 Порядок разработки')
num(1, 'Создать репозиторий на GitHub, папку проекта, файл requirements.txt (PyQt5>=5.15).')
num(2, 'Описать схему базы в database.py: 6 таблиц, индексы, функцию init_db() и загрузку стартового словаря.')
num(3, 'Написать репозитории — классы, в которых собраны все SQL-запросы; запросы только параметризованные (?).')
num(4, 'Реализовать хеширование паролей в utils.py (PBKDF2-SHA256, 260 000 итераций, соль).')
num(5, 'Написать сервисы в services.py: словарь, прогресс, серия дней, дневная цель; связанные изменения обернуть в transaction().')
num(6, 'Сделать окно входа и регистрации (login_window.py).')
num(7, 'Сделать главное окно с боковым меню и пятью вкладками: карточки, тесты, переводчик, словарь, прогресс.')
num(8, 'Подключить сигналы вкладок к сервисам в главном окне; после изменений сервис посылает progress_changed, экран обновляется.')
num(9, 'Вынести оформление в styles.py, настройки — в config.py.')
num(10, 'Написать автотесты (tests/) и выполнить ручное тестирование по тест-кейсам (раздел 6).')
num(11, 'Собрать .exe через PyInstaller и выложить в раздел Releases на GitHub.')
h2('2.5 Установка, запуск и сборка')
para('Запуск из исходников (нужен Python 3.9 или новее):')
for line in ('pip install -r requirements.txt', 'python main.py'):
    p = para(line, align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.25)
    for rr in p.runs: rr.font.name = 'Courier New'; rr.font.size = Pt(12)
para('Запуск автотестов:')
p = para('python -m unittest -v', align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.25)
for rr in p.runs: rr.font.name = 'Courier New'; rr.font.size = Pt(12)
para('Сборка готового файла для Windows:')
for line in ('pip install pyinstaller',
             'pyinstaller --onefile --windowed --name VocabularyTrainer --icon=data/icon.ico --add-data "data;data" main.py'):
    p = para(line, align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.25)
    for rr in p.runs: rr.font.name = 'Courier New'; rr.font.size = Pt(11)
para('Готовый файл появляется в папке dist/. База собранной программы хранится в %APPDATA%\\VocabularyTrainer\\app.db, '
     'при запуске из исходников — в data/app.db.')

# ═══════════════ 3 Руководство пользователя ═══════════════
h1('3 РУКОВОДСТВО ПОЛЬЗОВАТЕЛЯ')
h2('3.1 Регистрация и вход')
para('При первом запуске открывается окно входа (рисунок 1). Чтобы создать аккаунт, введите имя и пароль '
     '(не короче 4 символов) и нажмите «Зарегистрироваться». После сообщения «Аккаунт создан! Теперь войдите.» '
     'нажмите «Войти». Кнопка с глазом показывает введённый пароль. Флажок «Запомнить на этом компьютере» '
     'включает автовход: при следующем запуске окно входа не появится.')
figure('01_вход.png', 'Окно входа', width=7)
para('После входа появляется приветствие (рисунок 2): серия дней подряд и цель на сегодня — 5 слов и 1 тест. '
     'Кнопка «Начать учиться!» открывает главное окно.')
figure('06_приветствие.png', 'Окно приветствия', width=8)
h2('3.2 Главное окно')
para('Слева — меню разделов: «Флеш-карточки», «Тесты», «Переводчик», «Словарь», «Прогресс». Вверху — число слов '
     'в словаре, имя пользователя и кнопка «Выйти».')
h2('3.3 Флеш-карточки')
para('Нажмите «Начать» — появится английское слово (рисунок 3). «Перевернуть» показывает перевод, «Следующая» — '
     'следующее слово, «Знаю» отмечает слово выученным, и больше оно в карточках не появится. «Стоп» заканчивает занятие. '
     'Слева вверху — таймер занятия с кнопками «Пауза» и «Сброс».')
figure('08_карточка.png', 'Флеш-карточка с переводом', width=8.5)
h2('3.4 Тесты')
para('Выберите режим и число вопросов (от 5 до 50) и нажмите «Начать тест». Выберите вариант ответа и нажмите '
     '«Проверить»: верный ответ подсветится зелёным, ошибка — красным (рисунок 4). Затем нажмите «Следующий вопрос». '
     'В режиме «На время» за 60 секунд нужно ответить правильно на как можно больше вопросов.')
figure('12_неправильно.png', 'Тест: ответ проверен', width=8.5)
h2('3.5 Переводчик')
para('Введите слово и нажмите «Перевести» или Enter (рисунок 5). Кнопка «⇌» меняет направление перевода. '
     'Все переводы попадают в историю, кнопка «Очистить» её стирает. Перевод ищется по словарю программы.')
figure('16_переводчик.png', 'Переводчик', width=8.5)
h2('3.6 Словарь')
para('В таблице все слова и их статус (рисунок 6). Поле поиска фильтрует слова по-английски и по-русски. '
     '«Добавить слово» открывает окно, где вводится английское слово и перевод (рисунок 7). «Сохранить» сохраняет данные.')
figure('17_поиск.png', 'Словарь: поиск', width=8.5)
figure('18_добавить_слово.png', 'Окно добавления слова', width=8)
h2('3.7 Прогресс')
para('На вкладке «Прогресс» (рисунок 8) показаны звание, серия дней, цель на сегодня, число выученных слов и пройденных '
     'тестов, точность ответов и список всех 10 званий с условиями их получения.')
figure('21_звание.png', 'Прогресс пользователя', width=8.5)

# ═══════════════ 4 Тест-сценарий ═══════════════
h1('4 ТЕСТ-СЦЕНАРИЙ')
h2('4.1 Объект и цель тестирования')
para('Объект — приложение «Тренажёр английских слов», версия из ветки main репозитория Engl_Ucheb (коммит 40acf73). '
     'Цель — проверить, что система выполняет все требования раздела 1, и найти дефекты.')
h2('4.2 Тестовое окружение')
table('Тестовое окружение', ['Параметр', 'Значение'], [
    ['Операционная система', 'Debian 13 (Linux); итоговая сборка — Windows 10/11'],
    ['Python', '3.13'],
    ['PyQt5', '5.15'],
    ['База данных', 'SQLite, новая пустая база для каждого прогона'],
    ['Тестовые данные', 'пользователь student / pass1234; стартовый словарь 2073 слова'],
], [5.5, 11.0])
h2('4.3 Виды тестирования')
bullet('функциональное тестирование интерфейса — по тест-кейсам раздела 6 (44 тест-кейса);')
bullet('проверка данных в базе — после действий в окнах проверяется содержимое таблиц;')
bullet('тестирование безопасности — SQL-инъекция в форме входа, хранение паролей;')
bullet('модульное тестирование — автотесты tests/ (11 тестов).')
para('Действия в окнах выполнялись скриптом run_tests.py (лежит в папке проекта): он нажимает кнопки и вводит данные '
     'так же, как пользователь, проверяет результат и делает снимки экрана. Это позволяет повторить всё тестирование '
     'одной командой после каждого изменения.')
h2('4.4 Порядок выполнения')
para('Тест-пакеты выполняются строго по порядку, так как следующие пакеты используют данные предыдущих:')
num(1, 'ТП-01 «Регистрация и вход» — создаётся пользователь student;')
num(2, 'ТП-02 «Флеш-карточки» — выучивается 5 слов;')
num(3, 'ТП-03 «Тесты» — проходится обычный тест и тест «На время»;')
num(4, 'ТП-04 «Переводчик»;')
num(5, 'ТП-05 «Словарь» — добавляется слово pirate;')
num(6, 'ТП-06 «Прогресс и дневная цель»;')
num(7, 'ТП-07 «Сохранение данных и безопасность» — выход, перезапуск, проверка базы.')
h2('4.5 Критерии начала и окончания')
para('Начало: программа запускается без ошибок, база пустая, автотесты проходят.')
para('Окончание: выполнены все тест-кейсы, каждому присвоен статус «Пройден» или «Не пройден», на каждый непройденный '
     'тест-кейс заведён дефект. Система считается принятой, если нет дефектов высокой важности.')

# ═══════════════ 5 Тест-пакеты ═══════════════
h1('5 ТЕСТ-ПАКЕТЫ')
para('Тест-кейсы сгруппированы в тест-пакеты по разделам системы (таблица ' + str(tab_n[0] + 1) + ').')
rows = []
for tp in TP:
    ids = [t[0] for t in TK if t[1] == tp[0]]
    rows.append([tp[0], tp[1], tp[2], f'{ids[0]}…{ids[-1]}' if len(ids) > 1 else ids[0], tp[3]])
# ТК-44 в ТП-06 стоит в конце — поправим диапазон вручную
for r_ in rows:
    if r_[0] == 'ТП-06': r_[3] = 'ТК-38…ТК-40, ТК-44'
    if r_[0] == 'ТП-07': r_[3] = 'ТК-41…ТК-43'
table('Тест-пакеты', ['Код', 'Название', 'Предусловие', 'Тест-кейсы', 'Требования'], rows,
      [1.7, 2.8, 6.0, 2.7, 3.3])

# ═══════════════ 6 Тест-кейсы ═══════════════
h1('6 ТЕСТ-КЕЙСЫ')
para('Для каждого тест-кейса указаны шаги, ожидаемый и фактический результат. Фактический результат получен при '
     'прогоне 26.11.2026. Статус «Пройден» — фактический результат совпал с ожидаемым.')
for tp in TP:
    h2(f'6.{TP.index(tp) + 1} {tp[0]} «{tp[1]}»')
    para(tp[2], label='Предусловие: ')
    rows = []
    for t in TK:
        if t[1] != tp[0]: continue
        ok, actual = RES[t[0]]
        rows.append([t[0], t[2], [f'{i}. {s}' for i, s in enumerate(t[3], 1)], t[4], actual,
                     'Пройден' if ok else 'Не пройден'])
    table(f'Тест-кейсы пакета {tp[0]}', ['Код', 'Название', 'Шаги', 'Ожидаемый результат', 'Фактический результат', 'Статус'],
          rows, [1.5, 2.2, 3.3, 3.6, 3.8, 2.1], size=10)

# ═══════════════ 7 Результаты ═══════════════
h1('7 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ')
h2('7.1 Сводка')
rows = []; tot = [0, 0]
for tp in TP:
    ids = [t[0] for t in TK if t[1] == tp[0]]
    ok = sum(1 for i in ids if RES[i][0])
    tot[0] += len(ids); tot[1] += ok
    rows.append([tp[0], tp[1], str(len(ids)), str(ok), str(len(ids) - ok)])
rows.append(['', 'Итого', str(tot[0]), str(tot[1]), str(tot[0] - tot[1])])
table('Итоги по тест-пакетам', ['Код', 'Тест-пакет', 'Всего', 'Пройдено', 'Не пройдено'], rows, [2.0, 7.5, 2.0, 2.5, 2.5])
para(f'Из {tot[0]} тест-кейсов пройдено {tot[1]} ({round(tot[1] * 100 / tot[0])} %). Автотесты: 11 из 11 пройдены '
     '(команда python -m unittest -v).')
h2('7.2 Найденные дефекты')
para('По непройденным тест-кейсам и при разборе кода и данных найдены дефекты (таблица ' + str(tab_n[0] + 1) + '). '
     'Дефектов высокой важности нет: все основные функции работают.')
table('Дефекты', ['Код', 'Тест-кейс', 'Важность', 'Описание', 'Причина', 'Как исправить'],
      [list(d) for d in DEF], [1.4, 1.5, 2.1, 4.3, 3.9, 3.3], size=10)

# ═══════════════ Заключение ═══════════════
h1('ЗАКЛЮЧЕНИЕ')
para('В ходе проекта разработана информационная система «Тренажёр английских слов» — настольное приложение на Python '
     'с интерфейсом PyQt5 и базой SQLite. Система поддерживает несколько пользователей и включает флеш-карточки, '
     'тесты двух видов, переводчик, словарь с поиском и добавлением слов, статистику прогресса, серию дней, '
     'дневную цель и звания.')
para(f'Составлены требования заказчика (15 функциональных и 7 нефункциональных), инструкция по разработке, сборке '
     f'и использованию, тест-сценарий, 7 тест-пакетов и {tot[0]} тест-кейса. Тестирование показало, что система '
     f'выполняет требования: пройдено {tot[1]} тест-кейса из {tot[0]}, все 11 автотестов. Найдено 4 дефекта средней '
     'и низкой важности, для каждого указана причина и способ исправления.')

doc.save(OUT)
print(OUT, 'рисунков', fig_n[0], 'таблиц', tab_n[0])
