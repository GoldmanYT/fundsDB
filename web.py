import streamlit as st
import sqlite3
from queries import *

db_name = 'Фонды денежного рынка.db'


@st.dialog('Добавление записи')
def dialog_insert(tab_name):
    data = tab_data[tab_name]
    values = [st.text_input(label, key=label) for label in data['labels'] if label != 'Код']
    fields = [field for field in data['fields'] if field != 'Код']
    if st.button('OK'):
        with sqlite3.connect(db_name) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(INSERT_INTO.format(
                table=data['table'],
                fields=','.join(fields),
                values=','.join('?' * len(values)),
            ), values)
        st.rerun()


@st.dialog('Изменение записи')
def dialog_update(tab_name):
    data = tab_data[tab_name]
    values = [st.text_input(label, key=label) for label in data['labels'] if label != 'Код']
    fields = [field for field in data['fields'] if field != 'Код']
    if st.button('OK'):
        with sqlite3.connect(db_name) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(INSERT_INTO.format(
                table=data['table'],
                fields=','.join(fields),
                values=','.join('?' * len(values)),
            ), values)
        st.rerun()


@st.dialog('Удаление записи')
def dialog_delete(tab_name):
    data = tab_data[tab_name]
    values = [st.text_input(label, key=label) for label in data['labels'] if label != 'Код']
    fields = [field for field in data['fields'] if field != 'Код']
    if st.button('OK'):
        with sqlite3.connect(db_name) as con:
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(INSERT_INTO.format(
                table=data['table'],
                fields=','.join(fields),
                values=','.join('?' * len(values)),
            ), values)
        st.rerun()


st.title('Фонды денежного рынка')

with sqlite3.connect(db_name) as con:
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    data_labels = st.session_state['data_labels'] = {}
    for row in con.execute(GET_DATA_LABELS).fetchall():
        table_name = row['ИмяТаблицы']
        row_name = row['ИмяПоля']
        label = row['Подпись']
        if row_name is None:
            data_labels[table_name] = label
        else:
            data_labels[table_name, row_name] = label

    tabs_data = {}
    tables_data = cur.execute(GET_TABLES).fetchall()
    tab_data = {}
    for index, table_data in enumerate(tables_data):
        table_name = table_data['name']
        tab_name = data_labels.get(table_name, table_name)
        rows = cur.execute(GET_TABLE_DATA.format(table=table_name)).fetchall()
        labels = [data_labels.get((table_name, row_name), row_name) for row_name in rows[0].keys()]
        fields = list(rows[0].keys())
        table_content = [{
            label: str(column)
            for label, column in zip(labels, row)}
            for row in rows]
        tabs_data[tab_name] = table_content
        tab_data[tab_name] = {'table': table_name, 'labels': labels, 'fields': fields}

tabs = st.tabs(tabs_data.keys())
for tab, tab_name in zip(tabs, tabs_data):
    with tab:
        insert, update, delete = st.columns(3)
        with insert:
            if st.button('Добавить', f'{tab_name}_insert'):
                dialog_insert(tab_name)
        with update:
            if st.button('Изменить', f'{tab_name}_update'):
                dialog_update(tab_name)
        with delete:
            if st.button('Удалить', f'{tab_name}_delete'):
                dialog_delete(tab_name)
        st.table(tabs_data[tab_name])
