GET_DATA_LABELS = '''
SELECT * FROM ПодписиДанных
'''

GET_TABLES = '''
SELECT * FROM sqlite_master
WHERE type = 'table' AND name <> 'ПодписиДанных'
'''

GET_TABLE_DATA = '''
SELECT * FROM {table}
'''

INSERT_INTO = '''
INSERT INTO {table} ({fields})
VALUES ({values})
'''

DELETE_FROM = '''
DELETE FROM {table}
WHERE Код = {id}
'''

UPDATE_SET = '''
UPDATE {table}
SET {field} = ?
WHERE Код = {id}
'''
