import pymysql

conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)


cursor = conn.cursor()
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
conn.close()


print("DB > kadai テーブル作成完了")