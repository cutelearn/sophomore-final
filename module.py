import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class SQLGenerator:
    def query_order_amount_and_price_by_date_range(self, startDate, endDate):
        return f"""
        SELECT od.Pno, SUM(od.Amount) AS TotalAmount, p.Price
        FROM `order` o
        JOIN order_details od ON o.Ono = od.Ono
        JOIN product p ON od.Pno = p.Pno
        WHERE o.Odate BETWEEN '{startDate}' AND '{endDate}'
        GROUP BY od.Pno, p.Price;
        """

    def query_purchased_products_by_customer_id(self, customerId):
        return f"""
        SELECT c.Cno, c.CName, p.PName
        FROM customer c
        JOIN `order` o ON c.Cno = o.Cno
        JOIN order_details od ON o.Ono = od.Ono
        JOIN product p ON od.Pno = p.Pno
        WHERE c.Cno = '{customerId}';
        """

    def query_inventory_by_order_and_delivery_dates(self, orderDate, deliveryDate):
        return f"""
        SELECT o.Ono, p.PName, p.Inventory
        FROM `order` o
        JOIN order_details od ON o.Ono = od.Ono
        JOIN product p ON od.Pno = p.Pno
        WHERE o.Odate = '{orderDate}' AND o.Ddate = '{deliveryDate}';
        """

    def get_customer_order_summary(self, customerId):
        return f"""
        SELECT p.Pno, SUM(od.Amount * p.Price) AS TotalPrice, p.Inventory
        FROM customer c
        JOIN `order` o ON c.Cno = o.Cno
        JOIN order_details od ON o.Ono = od.Ono
        JOIN product p ON od.Pno = p.Pno
        WHERE c.Cno = '{customerId}'
        GROUP BY p.Pno, p.Inventory;
        """


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)

    def execute_query(self, query):
        if self.conn is None:
            raise Exception(
                "資料庫未連線。首先呼叫 connect() 方法。")
        return pd.read_sql_query(query, self.conn)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


class BarChartPlotter:
    def __init__(self, dataframe):
        self.df = dataframe

    def plot_bar_chart(self, title, x_label, y_label, filename, bar_width=0.35, colors=('b', 'g')):
        index = np.arange(len(self.df))

        fig, ax = plt.subplots()
        for i, column in enumerate(self.df.columns[1:]):
            ax.bar(index + i * bar_width,
                   self.df[column], bar_width, label=column, color=colors[i])

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(self.df[self.df.columns[0]])
        ax.legend()
        plt.savefig(filename)


if __name__ == '__main__':
    db_manager = DatabaseManager('/app/database.db')
    sql_generator = SQLGenerator()

    db_manager.connect()

    while True:
        print("請選擇查詢選項：")
        print("1. 由訂貨日期範圍查詢訂購數量及單價")
        print("2. 由客戶代號查詢客戶曾經購買的商品名稱")
        print("3. 由訂貨日期及送貨日期查詢庫存量")
        print("4. 統計客戶名稱（代號）的訂購金額比較圖（附註庫存量）")
        print("5. 退出")

        choice = input("輸入選項 (1-5): ")

        if choice == '1':
            startDate = input("輸入起始日期 (yyyy-mm-dd): ")
            endDate = input("輸入結束日期 (yyyy-mm-dd): ")
            query = sql_generator.query_order_amount_and_price_by_date_range(
                startDate, endDate)
        elif choice == '2':
            customerId = input("輸入客戶代號: ")
            query = sql_generator.query_purchased_products_by_customer_id(
                customerId)
        elif choice == '3':
            orderDate = input("輸入訂貨日期 (yyyy-mm-dd): ")
            deliveryDate = input("輸入送貨日期 (yyyy-mm-dd): ")
            query = sql_generator.query_inventory_by_order_and_delivery_dates(
                orderDate, deliveryDate)
        elif choice == '4':
            customerId = input("輸入客戶代號: ")
            query = sql_generator.get_customer_order_summary(customerId)
            df = db_manager.execute_query(query)
            print("Query Result:")
            print(df.head())
            plotter = BarChartPlotter(df)
            plotter.plot_bar_chart(title='Total Order Amount and Inventory by Customer',
                                   x_label='Product Name', y_label='Value', filename='bar_chart.png')
            continue
        elif choice == '5':
            break
        else:
            print("無效的選項，請重新輸入。")
            continue

        df = db_manager.execute_query(query)
        print("Query Result:")
        print(df.head())

    db_manager.close()
