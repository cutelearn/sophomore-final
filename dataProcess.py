import os
import pandas as pd
import sqlite3


class CSVToSQLite:
    def __init__(self, db_path, folder_path):
        """
        初始化類別並建立數據庫連接。
        :param db_path: 數據庫文件的路徑。
        :param folder_path: 包含 CSV 文件的資料夾路徑。
        """
        self.db_path = db_path
        self.folder_path = folder_path
        self.conn = sqlite3.connect(db_path)

    def process_files(self):
        """
        處理資料夾中的所有 CSV 文件，並將它們存儲到 SQLite 數據庫中。
        """
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.folder_path, filename)
                df = pd.read_csv(file_path)
                table_name = filename[:-4]
                df.to_sql(table_name, self.conn,
                          if_exists='replace', index=False)

    def close_connection(self):
        """
        關閉數據庫連接。
        """
        self.conn.close()


if __name__ == '__main__':
    # 創建 CSVToSQLite 實例並調用 process_files() 方法。
    csv_to_sqlite = CSVToSQLite('/app/database.db', 'table')
    csv_to_sqlite.process_files()
    csv_to_sqlite.close_connection()
    print('Done.')
