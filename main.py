from kivy.uix.anchorlayout import AnchorLayout
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
import psycopg2
from datetime import datetime
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

connection_string = (
    'postgres://msojsqyh:xBl-Ab3tNu_hVXBc4ylHJbSamWhhib4j@ella.db.elephantsql.com/msojsqyh') 

box = BoxLayout(orientation='vertical')
box.add_widget(Label(text='здесь должен быть такой звук "ту-дум"', font_size=45))
box.add_widget(Label(text='Введите номер детали', font_size=75))
btn_close: Button = Button(text='закрыть', size_hint=(1, None), height=200, font_size=75)
box.add_widget(btn_close)


class MainMenu(Screen):
    pass


class AddScreen(Screen):
    # for adding data in inclusion table"""
    def btn_add_press(self):  # this func work with text from textinput and spinner
        if self.ids.parent_number.text != '' or self.ids.child_number.text !='':
            self.detail = self.ids.parent_number.text, self.ids.parent_name.text, self.ids.child_number.text, \
                          self.ids.child_name.text
            con = psycopg2.connect(connection_string)  # connection string for work with psql
            cur = con.cursor()
            tag = 'отправка'
            rows = (
                self.ids.parent_number.text, self.ids.parent_name.text, self.ids.child_number.text, self.ids.child_name.text,
                '1')
            insert_in_sent_table = '''INSERT INTO inclusion(parent_number, parent_name, child_number, child_name, quantity) 
                                      VALUES(%s, %s, %s, %s, %s) '''
            cur.execute(insert_in_sent_table, rows, )
            con.commit()
            self.update_lbl_add.text = str('Последняя деталь: ' + str(self.ids.parent_number.text) + ' ' +
                                            str(self.ids.parent_name.text) + ' ' + str(self.ids.child_number.text) +
                                            ' ' + str(self.ids.child_name.text))

            self.ids.parent_number.text = ''
            self.ids.child_number.text = ''

        else:
            message_done = Popup(title='!Введите номер/наименование детали!', content=box, auto_dismiss=False, size_hint=(1, None), height=600)

            btn_close.bind(on_press=message_done.dismiss)

            message_done.open()


class TableAllWindow(Screen):
    """ main screen with common table consists of 1 textview string and some buttons for see info  """
    def __init__(self, **kw):
        super().__init__(**kw)
        self.con = None
        self.data_tables = None
        self.cur = None
        self.rows = None

    def add_all_table(self):
        self.con = psycopg2.connect(connection_string)
        self.cur = self.con.cursor()
        self.cur.execute("SELECT parent_number, parent_name, child_number, child_name FROM inclusion ORDER BY parent_name")
        self.rows = self.cur.fetchall()

        layout = AnchorLayout()
        self.data_tables = MDDataTable(
            use_pagination=True,
            rows_num=10,
            pagination_menu_pos='auto',
            # elevation=8,
            # pagination_menu_height = '480dp',
            size_hint=(1, 0.1),
            column_data=[
                ("№ детали/узла", dp(20)),
                ("Наименование", dp(30)),
                ("№ входящего", dp(20)),
                ("Наименование вх", dp(30)),
            ],
            row_data=[self.row for self.row in self.rows],

        )
        self.ids.all_table_layout.add_widget(self.data_tables)
        return layout

    def on_enter(self):
        self.add_all_table()

    def remove_table(self):
        self.ids.all_table_layout.remove_widget(self.data_tables)


class TableComWindow(Screen):
    """ for work with common table of parts """
    def __init__(self, **kw):
        super().__init__(**kw)
        self.data_table_arrive = None
        self.data_tables = None
        self.cur = None
        self.rows = None

    def add_com_table(self):
        self.con = psycopg2.connect(connection_string)
        self.cur = self.con.cursor()
        browse = self.manager.get_screen('table_all')
        self.det = '%'+browse.ids.input_det.text+'%'
        self.name = browse.ids.det_name.text
        self.cur.execute("SELECT  parent_number, parent_name, child_number, child_name FROM inclusion WHERE "
                         "parent_number LIKE %s AND parent_name=%s ORDER BY parent_number DESC", (self.det, self.name,))
        self.rows = self.cur.fetchall()

        layout = AnchorLayout()
        self.data_tables_sent = MDDataTable(
            use_pagination=True,
            rows_num=5,
            column_data=[
                ("№ детали", dp(20)),
                ("Наименование", dp(30)),
                ("№ детали", dp(15)),
                ("Наименование", dp(20)),
            ],
            row_data=[self.row for self.row in self.rows],
        )
        self.ids.com_layout.add_widget(self.data_tables_sent)

        return layout

    def on_enter(self):
        self.add_com_table()
        
    def remove_tables(self):
        self.ids.com_layout.remove_widget(self.data_tables_sent)


class TableUnitWindow(Screen):
    """ for looking child units that make up parent details """
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cur = None
        self.con = None

    def add_unit_table(self):
        self.con = psycopg2.connect(connection_string)
        self.cur = self.con.cursor()
        browse = self.manager.get_screen('table_all')
        self.unit = '%'+browse.ids.input_det.text+'%'
        self.unit_name = browse.ids.det_name.text
        self.cur.execute(
            "SELECT parent_number, parent_name, child_number, child_name FROM inclusion WHERE child_number LIKE %s AND child_name=%s",
            (self.unit, self.unit_name,))
        self.rows = self.cur.fetchall()

        layout = AnchorLayout()
        self.data_tables = MDDataTable(
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("№ детали/узла", dp(40)),
                ("Наименование", dp(40)),
                ("№ входящего", dp(25)),
                ("Наименование вх", dp(40)),
                ],
            row_data=[self.row for self.row in self.rows],
        )

        self.ids.unit_layout.add_widget(self.data_tables)
        return layout

    def on_enter(self):
        self.add_unit_table()

    def remove_tables(self):
        self.ids.unit_layout.remove_widget(self.data_tables)


class DeleteString(Screen):
    """ for removing data per strings from inclusion table """
    def __init__(self, **kw):
        super().__init__(**kw)
        self.con = None
        self.data_tables = None
        self.cur = None
        self.rows = None
        self.q = None

    def delete_string_table(self):
        self.con = psycopg2.connect(connection_string)
        self.cur = self.con.cursor()
        self.cur.execute("SELECT id, parent_number, parent_name, child_number, child_name FROM inclusion ORDER BY parent_number")
        self.rows = self.cur.fetchall()

        layout = AnchorLayout()
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos='auto',
            check=True,
            size_hint=(1, 0.1),
            column_data=[
                ("id", dp(20)),
                ("№ детали", dp(40)),
                ("Наименование", dp(30)),
                ("№ вх", dp(15)),
                ("Наименование вх", dp(20)),
            ],
            row_data=[self.row for self.row in self.rows],

        )
        self.data_tables.bind(on_check_press=self.on_check_press)
        self.ids.del_string_layout.add_widget(self.data_tables)

        return layout

    def on_check_press(self, instance_table, current_row):
        """Called when the checkbox in the table row is checked."""
        print(current_row[0])
        return self.q

    def on_enter(self):
        self.delete_string_table()

    def remove_table(self):
        self.ids.del_string_layout.remove_widget(self.data_tables)

    def on_del_press_arrive(self):
        req = list(self.data_tables.get_row_checks())

        con = psycopg2.connect(connection_string)  
        cur = con.cursor()

        ident = req[0][0]
        delete_query = '''DELETE FROM inclusion WHERE id = %s '''
        cur.execute(delete_query, (ident,))
        con.commit()

        btn_close: Button = Button(text='закрыть')
        messege_done = Popup(title='Кто-то накосячил, кто-то убрал. кто-то - молодец!', content=(btn_close), size_hint=(1, None), height=400, 
                             auto_dismiss=False)

        btn_close.bind(on_press=messege_done.dismiss)

        messege_done.open()


class CommonApp(MDApp):

    def build(self):
        sm = ScreenManager()  # transition=WipeTransition())
        sm.add_widget(MainMenu(name='main_menu'))
        sm.add_widget(AddScreen(name='add_screen'))
        sm.add_widget(TableAllWindow(name='table_all'))
        sm.add_widget(TableComWindow(name='com_layout'))
        sm.add_widget(TableUnitWindow(name='table_unit'))
        sm.add_widget(DeleteString(name='delete_string'))
        return sm


if __name__ == '__main__':
    CommonApp().run()
