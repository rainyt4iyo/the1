import pymysql

conn = pymysql.connect(
    host='localhost',
    user='t4',
    password='t4_password',
    database='myDB',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# テーブル作成
columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

sql_create = f'''
CREATE TABLE IF NOT EXISTS mid_result (
    id INT PRIMARY KEY,
    {columns}
)
'''
cursor.execute(sql_create)
conn.commit()

# データ挿入
for i in range(1, 145):
    # 値の個数はid + kadai_1～kadai_30 = 31個
    # すべて'0'で初期化（文字列ではなくINTなら0でOK）
    values = ", ".join(["0"] * 30)  # kadai_1～30は整数0
    sql_insert = f"INSERT INTO mid_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
    cursor.execute(sql_insert)

conn.commit()
# テーブル作成
columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

sql_create = f'''
CREATE TABLE IF NOT EXISTS fun_result (
    id INT PRIMARY KEY,
    {columns}
)
'''
cursor.execute(sql_create)
conn.commit()

# データ挿入
for i in range(1, 145):
    # 値の個数はid + kadai_1～kadai_30 = 31個
    # すべて'0'で初期化（文字列ではなくINTなら0でOK）
    values = ", ".join(["0"] * 30)  # kadai_1～30は整数0
    sql_insert = f"INSERT INTO fun_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
    cursor.execute(sql_insert)

conn.commit()
# テーブル作成
columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

sql_create = f'''
CREATE TABLE IF NOT EXISTS open_result (
    id INT PRIMARY KEY,
    {columns}
)
'''
cursor.execute(sql_create)
conn.commit()

# データ挿入
for i in range(1, 145):
    # 値の個数はid + kadai_1～kadai_30 = 31個
    # すべて'0'で初期化（文字列ではなくINTなら0でOK）
    values = ", ".join(["0"] * 30)  # kadai_1～30は整数0
    sql_insert = f"INSERT INTO open_result (id, {', '.join([f'kadai_{j}' for j in range(1,31)])}) VALUES ({i}, {values})"
    cursor.execute(sql_insert)

conn.commit()


cursor.close()
conn.close()

print("DB > result テーブル作成・初期化完了")