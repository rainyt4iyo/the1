import os
from flask import Flask
import pymysql
import openpyxl

app = Flask(__name__)
app.config.from_object('testapp.config')

# 基本ディレクトリの取得（このファイルの場所）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "static.xlsx")

# DB接続（localhost→127.0.0.1で試すのも良い）
conn = pymysql.connect(
    host='127.0.0.1',
    user='t4',
    password='t4_password',
    database='myDB',
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

# ログ：接続DB確認
cursor.execute("SELECT DATABASE()")
print("[DB] Connected to:", cursor.fetchone())

# テーブル作成（DROPはせず、なければ作成のみ）
tables_to_create = {
    "fun_player": "CREATE TABLE IF NOT EXISTS fun_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))",
    "mid_player": "CREATE TABLE IF NOT EXISTS mid_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))",
    "open_player": "CREATE TABLE IF NOT EXISTS open_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))",
    "fun_kadai": "CREATE TABLE IF NOT EXISTS fun_kadai (id INT UNIQUE, area VARCHAR(255), point INT)",
    "mid_kadai": "CREATE TABLE IF NOT EXISTS mid_kadai (id INT UNIQUE, area VARCHAR(255), point INT)",
    "open_kadai": "CREATE TABLE IF NOT EXISTS open_kadai (id INT UNIQUE, area VARCHAR(255), point INT)",
}

for table, create_sql in tables_to_create.items():
    cursor.execute(create_sql)
    conn.commit()
    print(f"[DB] Table '{table}' ensured.")

# Excel読み込み
wb = openpyxl.load_workbook("static.xlsx")

def insert_players(sheet_name, table_name):
    ws = wb[sheet_name]
    # 既存データは削除してから挿入（必要なら）
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()

    for i in range(1, 145):
        id_val = ws.cell(i, 1).value
        player_val = ws.cell(i, 2).value
        team_val = ws.cell(i, 3).value
        # NoneはPythonのNone型なので、文字列 "None" とは異なる
        if id_val is not None and player_val is not None and team_val is not None:
            temp = (id_val, player_val, team_val)
            sql = f"INSERT INTO {table_name} (id, player, team) VALUES (%s, %s, %s)"
            cursor.execute(sql, temp)
    conn.commit()
    print(f"[DB] Inserted players into '{table_name}' from sheet '{sheet_name}'.")

insert_players("FUN", "fun_player")
insert_players("MIDDLE", "mid_player")
insert_players("OPEN", "open_player")

# resultテーブルの作成と初期化チェック
def create_result_table(table_name):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    result = cursor.fetchone()
    if not result:
        columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])
        sql_create = f'''
        CREATE TABLE {table_name} (
            id INT PRIMARY KEY,
            {columns}
        )
        '''
        cursor.execute(sql_create)
        conn.commit()

        for i in range(1, 145):
            values = ", ".join(["0"] * 30)
            sql_insert = f"INSERT INTO {table_name} (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
            cursor.execute(sql_insert)
        conn.commit()
        print(f"[DB] > {table_name} を初期化しました")
    else:
        print(f"[DB] > {table_name} は存在しています")

create_result_table("fun_result")
create_result_table("mid_result")
create_result_table("open_result")

cursor.close()
conn.close()

print("[DB] >>> result テーブル作成・初期化完了")
print("--------------------------------------")

import testapp.views