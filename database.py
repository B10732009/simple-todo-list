import sqlite3
import os


#Database物件, 使用sqlite
class Database:
    def __init__(self, dbName):
        self.dbName = dbName
        self.data = []

        self.__openConnection()
        self.__closeConnection()

    # 打開/創建資料庫連線
    def __openConnection(self):
        currentPath = os.path.dirname(os.path.abspath(__file__))
        self.connection = sqlite3.connect(
            '{}/{}.sqlite3'.format(currentPath, self.dbName))
        self.cursor = self.connection.cursor()

    # 關閉資料庫連線
    def __closeConnection(self):
        self.connection.close()

    # 執行SQL命令
    def execute(self, sqlCommand):
        # 打開資料庫連線
        self.__openConnection()
        try:
            # 執行SQL命令
            self.cursor.execute(sqlCommand)

            # 將變更儲存至資料庫中
            self.connection.commit()

            #若為SELECT命令, 則將選取的資料存入self.data中
            self.data = self.cursor.fetchall()

            # 關閉資料庫連線
            self.__closeConnection()

            # 回傳SQL命令執行結果
            return True
        except sqlite3.Error as e:
            # 印出SQL錯誤訊息
            print('[sqlite3 ERROR] {}'.format(e))

            # 關閉資料庫連線
            self.__closeConnection()

            # 回傳SQL命令執行結果
            return False

    # 取得self.data
    def fetch(self):
        return self.data
