import pymysql

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)


cursor = conn.cursor()
sql = "CREATE TABLE IF NOT EXISTS player (id INT UNIQUE, name VARCHAR(255), category VARCHAR(255))"
cursor.execute(sql)
conn.commit()

sql = "insert into user values (i, '0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0','0', '0',);"
cursor.execute(sql)
conn.commit()

conn.close()
print("DB > player テーブル作成完了")