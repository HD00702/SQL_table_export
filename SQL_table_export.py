import mysql.connector
import pandas as pd
import time
import wx
import wx.grid as grid
import pandas.io.sql as pdsql
import os


class ConnectSqlDb(object):  # opening the config file, look for config data, connecting to SQL and looking for tables
    host = ''
    filename = ''
    database = ''
    user = ''
    password = ''
    sql_op = []
    tables_list = []

    def __init__(self, filename):  # name of the config file
        self.filename = filename

    def openfile(self):  # separate the data in the opened file
        with open(self.filename) as f:  # open the file
            data = f.readlines()  # read the lines
        self.host, self.database, self.user, self.password = [d.split('=')[1].split('\n')[0] for d in data]
        # separate lines into different variables
        return self.host, self.database, self.user, self.password

    def connectDatabase(self):  # connect to Database
        self.sql_op = mysql.connector.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            database=self.database
        )
        return self.sql_op

    def lookDatabases(self):  # check all the databases, currently not used since we tell the db name in the config file
        myCurs = self.sql_op.cursor()
        myCurs.execute("show databases")
        result = myCurs.fetchall()
        for databases in result:
            print(databases)

    def lookTables(self):  # show all the tables in the given database
        myCurs = self.sql_op.cursor()
        myCurs.execute("show tables")
        result = myCurs.fetchall()

        for tables in result:
            self.tables_list.append(tables)
        return self.tables_list


# noinspection PyPropertyAccess
class TableGrid(grid.Grid):
    my_var = ConnectSqlDb('config.txt')  # connect to SQL server class
    my_var.openfile()  # open config.txt file
    conn = my_var.connectDatabase()
    tables = my_var.lookTables()  # read all the tables
    tables_list = [item for tupl in tables for item in tupl]  # list of tuples into list

    def __init__(self, parent):
        grid.Grid.__init__(self, parent, -1, pos=(10, 40), size=(360, 450))

        self.CreateGrid(len(self.tables), 2)  # create grid based on table list length
        self.RowLabelSize = 20
        self.ColLabelSize = 20

        attr = grid.GridCellAttr()  # create checkboxes
        attr.SetEditor(grid.GridCellBoolEditor())
        attr.SetRenderer(grid.GridCellBoolRenderer())  # checkbox in grid cells
        self.SetColAttr(0, attr)  # which column
        self.SetColSize(0, 20)  # set column 0 size
        self.SetColSize(1, 300)  # set column 1 size

        for index, value in enumerate(self.tables_list):  # put all the tables in the grid
            self.SetCellValue(index, 1, value)


class TableFrame(wx.Frame):
    connect = TableGrid.conn
    tables_list = TableGrid.tables_list

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Save selected SQL", size=(400, 580))  # init frame
        panel = wx.Panel(self, style=0)
        self.grid1 = TableGrid(panel)
        self.grid1.SetFocus()
        self.CentreOnScreen()
        save_Btn = wx.Button(panel, 0, "Save selected", pos=(150, 500))
        save_Btn.Bind(wx.EVT_BUTTON, self.SaveClick)

    # def SaveClick(self, event):
    #    query = pdsql.read_sql('select* from KEYWORDS', self.connect)
    #    query.to_csv(r'E:\python\pythonProject\KEYWORDS.csv', index=False,sep=',')
    #    print('Saved')

    def SaveClick(self, event):

        for index, value in enumerate(self.tables_list):  # loop through the talbes checkbox column
            if self.grid1.GetCellValue(index, 0) == '1':  # check which one is selected
                query = pdsql.read_sql('select* from {}'.format(value), self.connect)  # read the files from sql
                query_df = pd.DataFrame(query)
                query_df.to_csv('{filename}.csv'.format(filename=value), index=False, sep=',')  # save it as a csv file


class SQLApp(wx.App): # show 
    def OnInit(self):
        frame = TableFrame(None)
        frame.Show(True)
        self.SetTopWindow(frame)
        return True


app = SQLApp()
app.MainLoop()

