from sqlite3 import connect
import csv

reader = csv.reader('Фонд.csv')

db = connect('Фонды денежного рынка.db')
cursor = db.cursor()
cursor.execute('''
DROP TABLE IF EXISTS ПодписиДанных 
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS ПодписиДанных (
    Код INTEGER PRIMARY KEY,
    ИмяТаблицы TEXT,
    ИмяПоля TEXT,
    Подпись TEXT
)''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS ВидФонда (
    Код INTEGER PRIMARY KEY,
    КодТипа TEXT,
    Описание TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS Фонд (
    Код INTEGER PRIMARY KEY,
    Название TEXT,
    ISIN TEXT,
    ДатаСоздания INTEGER,
    Статус TEXT,
    Валюта TEXT,
    КодВидаФонда INTEGER,
    FOREIGN KEY(КодВидаФонда) REFERENCES ВидФонда(Код)
)''')

data = [('ВидФонда.csv', 'ВидФонда'), ('Фонд.csv', 'Фонд'), ('ПодписиДанных.csv', 'ПодписиДанных')]

for filename, table_name in data:
    with open(filename, encoding='utf-8-sig') as file:
        rows = [row for row in csv.reader(file, delimiter=';')]
        if not cursor.execute(f'''
        SELECT 1 FROM {table_name}
        ''').fetchone():
            cursor.executemany(f'''
            INSERT INTO {table_name}
            VALUES ({','.join('?' * len(rows[0]))})
            ''', rows)
cursor.execute('''
UPDATE ПодписиДанных
SET ИмяПоля = NULL
WHERE ИмяПоля = 'NULL'
''')

db.commit()
db.close()
