import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem, QDialog, QLineEdit, QFormLayout
from main_window import Ui_main_window as UiMainWindow
from table_widget import Ui_Form as UiTableWidget
from insert_form import Ui_Form as UiInsertDialog
import sqlite3
from queries import *
from dataclasses import dataclass


@dataclass
class TableData:
    name: str
    labels: list[str]
    fields: list[str]

    def filter(self):
        self.labels = [label for label in self.labels if label != 'Код']
        self.fields = [field for field in self.fields if field != 'Код']


class MainWindow(QMainWindow, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.con = sqlite3.connect('Фонды денежного рынка.db')
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

        self.data_labels = {}
        for row in self.con.execute(GET_DATA_LABELS).fetchall():
            table_name = row['ИмяТаблицы']
            row_name = row['ИмяПоля']
            label = row['Подпись']
            if row_name is None:
                self.data_labels[table_name] = label
            else:
                self.data_labels[table_name, row_name] = label
        self.load_tables()

    def load_tables(self):
        tables_data = self.cur.execute(GET_TABLES).fetchall()
        self.tab_widget_tables.clear()
        for index, table_data in enumerate(tables_data):
            table_name = table_data['name']
            tab_name = self.data_labels.get(table_name, table_name)
            rows = self.cur.execute(GET_TABLE_DATA.format(table=table_name)).fetchall()
            labels = [self.data_labels.get((table_name, row_name), row_name) for row_name in rows[0].keys()]
            fields = list(rows[0].keys())
            table_data = TableData(table_name, labels, fields)
            self.tab_widget_tables.addTab(TableWidget(self, self.cur, table_data), tab_name)

            table_widget = self.tab_widget_tables.widget(index).table_widget
            table_widget.setColumnCount(len(rows[0]))
            table_widget.setHorizontalHeaderLabels(labels)
            table_widget.setRowCount(len(rows))
            for row_index, row in enumerate(rows):
                for column_index, column in enumerate(row):
                    table_widget.setItem(row_index, column_index, QTableWidgetItem(str(column)))
            table_widget.resizeColumnsToContents()
        self.con.commit()


class TableWidget(QWidget, UiTableWidget):
    def __init__(self, parent, cursor, table_data):
        super().__init__(parent)
        self.setupUi(self)
        self.main_window = parent
        self.cur = cursor
        self.table_data = table_data
        self.push_button_insert.clicked.connect(lambda: FormDialog(
            self, parent, cursor, table_data))
        self.push_button_delete.clicked.connect(self.delete)
        self.push_button_update.clicked.connect(lambda: FormDialog(
            self, parent, cursor, table_data,
            id=self.table_widget.item(self.table_widget.currentRow(), 0).text(),
            defaults=[
                self.table_widget.item(self.table_widget.currentRow(), column).text()
                for column in range(1, self.table_widget.columnCount())
            ]
        ))

    def delete(self):
        try:
            self.cur.execute(DELETE_FROM.format(
                table=self.table_data.name,
                id=self.table_widget.item(self.table_widget.currentRow(), 0).text()
            ))
        except sqlite3.Error:
            pass
        self.main_window.load_tables()


class FormDialog(QDialog, UiInsertDialog):
    def __init__(self, parent, main_window, cursor, table_data, id=None, defaults=()):
        super().__init__(parent)
        self.setupUi(self)
        table_data.filter()
        self.main_window = main_window
        self.cur = cursor
        self.table_data = table_data
        self.id = id
        for i, label in enumerate(table_data.labels):
            self.form_layout.addRow(label, QLineEdit(defaults[i] if i < len(defaults) else '', self))
        if id is None:
            self.button_box.accepted.connect(self.insert)
        else:
            self.button_box.accepted.connect(self.update_)
            self.setWindowTitle('Изменение записи')
        self.button_box.rejected.connect(lambda: self.close())
        self.exec()

    def insert(self):
        self.close()
        try:
            self.cur.execute(INSERT_INTO.format(
                table=self.table_data.name,
                fields=','.join(self.table_data.fields),
                values=','.join('?' * len(self.table_data.fields))
            ), [
                self.form_layout
                .itemAt(row, QFormLayout.FieldRole)
                .widget()
                .text()
                for row in range(len(self.table_data.fields))
            ])
        except sqlite3.Error:
            pass
        self.main_window.load_tables()

    def update_(self):
        self.close()
        try:
            for row in range(len(self.table_data.fields)):
                self.cur.execute(UPDATE_SET.format(
                    table=self.table_data.name,
                    field=self.table_data.fields[row],
                    id=self.id
                ), [
                    self.form_layout
                    .itemAt(row, QFormLayout.FieldRole)
                    .widget()
                    .text()
                ])
        except sqlite3.Error as err:
            print(err)
        self.main_window.load_tables()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
