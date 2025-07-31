from flask import Flask
import pymysql
import openpyxl

app = Flask(__name__)
app.config.from_object('testapp.config')

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

sql = "DROP TABLE if exists fun_player"
cursor.execute(sql)
sql = "DROP TABLE if exists mid_player"
cursor.execute(sql)
sql = "DROP TABLE if exists open_player"
cursor.execute(sql)
sql = "DROP TABLE if exists fun_team"
cursor.execute(sql)
sql = "DROP TABLE if exists mid_team"
cursor.execute(sql)
sql = "DROP TABLE if exists open_team"
cursor.execute(sql)

sql = "CREATE TABLE IF NOT EXISTS fun_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))"
cursor.execute(sql)
conn.commit()
sql = "CREATE TABLE IF NOT EXISTS mid_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))"
cursor.execute(sql)
conn.commit()
sql = "CREATE TABLE IF NOT EXISTS open_player (id INT UNIQUE, player VARCHAR(255), team VARCHAR(255))"
cursor.execute(sql)
conn.commit()

print("--------------------------------------")
print("[DB] > fun_player fun_team 初期化完了")
print("[DB] > mid_player mid_team 初期化完了")
print("[DB] > open_player open_team 初期化完了")
print("--------------------------------------")


sql = "CREATE TABLE IF NOT EXISTS mid_kadai (id INT UNIQUE, area VARCHAR(255), point INT)"
cursor.execute(sql)
conn.commit()
conn.close()

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)


cursor = conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS fun_kadai (id INT UNIQUE, area VARCHAR(255), point INT)"
cursor.execute(sql)
conn.commit()
conn.close()

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)


cursor = conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS open_kadai (id INT UNIQUE, area VARCHAR(255), point INT)"
cursor.execute(sql)
conn.commit()

print("[DB] > kadai 初期化完了")
print("--------------------------------------")

conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()

wb = openpyxl.load_workbook("static.xlsx")

ws = wb["FUN"]
for i in range(1,145):
    if ws.cell(i,1).value != "None" and ws.cell(i,2).value != "None" and ws.cell(i,3).value != "None":
        temp = (ws.cell(i,1).value, ws.cell(i,2).value, ws.cell(i,3).value)
        sql = "INSERT INTO fun_player (id, player, team ) VALUES (%s, %s, %s)"
        cursor.execute(sql, temp)
        conn.commit()

ws = wb["MIDDLE"]
for i in range(1,145):
    if ws.cell(i,1).value != "None" and ws.cell(i,2).value != "None" and ws.cell(i,3).value != "None":
        temp = (ws.cell(i,1).value, ws.cell(i,2).value, ws.cell(i,3).value)
        sql = "INSERT INTO mid_player (id, player, team ) VALUES (%s, %s, %s)"
        cursor.execute(sql, temp)
        conn.commit()

ws = wb["OPEN"]
for i in range(1,145):
    if ws.cell(i,1).value != "None" and ws.cell(i,2).value != "None" and ws.cell(i,3).value != "None":
        temp = (ws.cell(i,1).value, ws.cell(i,2).value, ws.cell(i,3).value)
        sql = "INSERT INTO open_player (id, player, team ) VALUES (%s, %s, %s)"
        cursor.execute(sql, temp)
        conn.commit()



cursor.execute("SHOW TABLES LIKE 'fun_result'")
result = cursor.fetchone()
if not result:

    columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

    sql_create = f'''
    CREATE TABLE fun_result (
        id INT PRIMARY KEY,
        {columns}
    )
    '''
    cursor.execute(sql_create)
    conn.commit()

    # データ挿入
    for i in range(1, 145):
        values = ", ".join(["0"] * 30)  
        sql_insert = f"INSERT INTO fun_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
        cursor.execute(sql_insert)

    conn.commit()
    print("[DB] > fun_result を初期化しました")
else:
    print("[DB] > fun_result は存在しています")

cursor.execute("SHOW TABLES LIKE 'mid_result'")
result = cursor.fetchone()
if not result:

    columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

    sql_create = f'''
    CREATE TABLE mid_result (
        id INT PRIMARY KEY,
        {columns}
    )
    '''
    cursor.execute(sql_create)
    conn.commit()

    # データ挿入
    for i in range(1, 145):
        values = ", ".join(["0"] * 30)  
        sql_insert = f"INSERT INTO mid_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
        cursor.execute(sql_insert)

    conn.commit()
    print("[DB] > mid_result を初期化しました")
else:
    print("[DB] > mid_result は存在しています")


cursor.execute("SHOW TABLES LIKE 'open_result'")
result = cursor.fetchone()
if not result:

    columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

    sql_create = f'''
    CREATE TABLE open_result (
        id INT PRIMARY KEY,
        {columns}
    )
    '''
    cursor.execute(sql_create)
    conn.commit()

    # データ挿入
    for i in range(1, 145):
        values = ", ".join(["0"] * 30)  
        sql_insert = f"INSERT INTO open_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
        cursor.execute(sql_insert)

    conn.commit()
    print("[DB] > open_result を初期化しました")
else:
    print("[DB] > open_result は存在しています")


cursor.close()
conn.close()

print("[DB] >>> result テーブル作成・初期化完了")
print("--------------------------------------")

import testapp.views
