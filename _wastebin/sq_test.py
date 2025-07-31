import pymysql

import pymysql.cursors
 
# データベースに接続
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Thermal_1119',
                             database='myDB',
                             cursorclass=pymysql.cursors.DictCursor)
 
values = [['webmaster1@python.org', 'very-secret1'],
          ['webmaster2@python.org', 'very-secret2'],
          ['webmaster3@python.org', 'very-secret3'],
          ['webmaster4@python.org', 'very-secret4'],
          ['webmaster5@python.org', 'very-secret5']]
 
with connection:
    with connection.cursor() as cursor:
        # レコードを挿入
        sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
        cursor.executemany(sql, values)
 
    # コミットしてトランザクション実行
    connection.commit()