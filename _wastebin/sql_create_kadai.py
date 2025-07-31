import pymysql

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)


cursor = conn.cursor()

columns = ",\n        ".join([f"kadai_{i} INT" for i in range(1, 31)])

sql = f'''CREATE TABLE IF NOT EXISTS result (
        {columns}
    )'''
conn.commit()
conn.close()
print("DB > result テーブル作成完了")