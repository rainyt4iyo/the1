from flask import render_template, request, redirect, url_for
from testapp import app, conn
import pymysql

@app.route('/')
def mainpage():
    return render_template('testapp/test.html')
    

@app.route('/register_player', methods=['GET','POST'])
def registerpage_player():

    if request.method == 'GET':
        return render_template('testapp/register_player.html')
    
    if request.method == 'POST':
        conn = pymysql.connect(host='localhost',
                       user='root',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
        
        try:
            id = request.form['id']
            name = request.form['name']
            cat = request.form['category']

            cursor = conn.cursor()
            
            insert_sql = '''
            INSERT INTO player (id, name, category)
            VALUES (%s, %s, %s)
            '''
            data = (id, name, cat)
            cursor.execute(insert_sql, data)
            print("レコードを追加しました。")

            conn.commit()

        except Exception as e:
            print(e)

        finally:
            conn.close()

        return redirect(url_for('registered_player'))
    

@app.route('/register_kadai', methods=['GET','POST'])
def registerpage_kadai():

    if request.method == 'GET':
        return render_template('testapp/register_kadai.html')
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='root',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)

        try:
            cursor = conn.cursor()

            id = request.form['id']
            kadai_category = request.form['category']
            kadai_number = int(request.form['number'])
            kadai_area = request.form['area']
            kadai_point = request.form['point']
            kadai_id = kadai_category + '-' + str(kadai_number)
            
            insert_sql = '''
            INSERT INTO kadai (id, kadai_id, kadai_category, kadai_number, kadai_area, kadai_point)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            data = (id, kadai_id, kadai_category, kadai_number, kadai_area, kadai_point)
            cursor.execute(insert_sql, data)
            print("レコードを追加しました。")

            conn.commit()

        except Exception as e:
            print(e)

        conn.close()
                
        return redirect(url_for('registered_kadai'))


@app.route('/registered_player_list',  methods=['GET','POST'])
def registered_player():

    if request.method == 'GET':

        conn = pymysql.connect(host='localhost',
                        user='root',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)

        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `name`, `category` FROM `player`"
                cursor.execute(sql)
                player = cursor.fetchall()
                print(player)

        return render_template('testapp/registered_player_list.html' , player = player)


    if request.method == 'POST':

        action = request.form.get("action")
        print(action)
        conn = pymysql.connect(host='localhost',
                        user='root',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
        
        if action == "nuke":
            with conn:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM player"
                    cursor.execute(sql)
                    sql = "alter table player auto_increment = 1"
                    cursor.execute(sql)
                    conn.commit()
        else:
            action = int(action)
            with conn:
                with conn.cursor() as cursor:

                    sql = f"DELETE FROM player where id = {action}"
                    cursor.execute(sql)
                    conn.commit()

        return render_template('testapp/temp_registered_player_list.html')



@app.route('/registered_kadai_list', methods=['GET', 'POST'])
def registered_kadai():

    if request.method == 'GET':

        conn = pymysql.connect(host='localhost',
                            user='root',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)

        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `kadai_id`, `kadai_category`, `kadai_number`,  `kadai_area`, `kadai_point` FROM `kadai`"
                cursor.execute(sql)
                result = cursor.fetchall()
                print(result)

        return render_template('testapp/registered_kadai_list.html' , result = result)

    if request.method == 'POST':

        action = request.form.get("action")
        print(action)
        conn = pymysql.connect(host='localhost',
                        user='root',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
        
        if action == "nuke":
            with conn:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM kadai"
                    cursor.execute(sql)
                    sql = "alter table kadai auto_increment = 1"
                    cursor.execute(sql)
                    conn.commit()
        else:
            action = int(action)
            with conn:
                with conn.cursor() as cursor:

                    sql = f"DELETE FROM kadai where id = {action}"
                    cursor.execute(sql)
                    conn.commit()

        return render_template('testapp/temp_registered_kadai_list.html')



@app.route('/temp_registered_player_list')
def temp_registered_player_list():

    return render_template('testapp/temp_registered_player_list.html')


@app.route('/temp_registered_kadai_list')
def temp_registered_kadai_list():

    return render_template('testapp/temp_registered_kadai_list.html')


@app.route('/judge/<area>')
def judge_area(area):

    conn = pymysql.connect(host='localhost',
                            user='root',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)
    
    with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `kadai_area` FROM `kadai`"
                cursor.execute(sql)
                area_list = cursor.fetchall()

    boo = False
    for i in area_list:
        if area in i.values():
            boo = True
            break
        else:
            pass

    if boo == True:

        conn = pymysql.connect(host='localhost',
                                user='root',
                                password='t4_password',
                                database='myDB',
                                cursorclass=pymysql.cursors.DictCursor)
        
        with conn:
                with conn.cursor() as cursor:
                    sql = f"SELECT `kadai_category` FROM kadai WHERE kadai_area='{area}'"
                    cursor.execute(sql)
                    category_list = cursor.fetchall()                
        
        print(category_list)
        result = list(dict.fromkeys(item['kadai_category'] for item in category_list))

        print(result)

        return render_template('testapp/judge_area.html', area = area, result = result)
    
    else:
        return f'ジャッジエリアが存在しません'
    

@app.route('/judge/<area>/<category>')
def judge_area_category(area, category):
    # データベース接続
    conn = pymysql.connect(host='localhost',
                                user='root',
                                password='t4_password',
                                database='myDB',
                                cursorclass=pymysql.cursors.DictCursor)

    with conn:
        with conn.cursor() as cursor:
            # カテゴリーに一致する選手一覧を取得
            sql = "SELECT id, name, category FROM player WHERE category = %s ORDER BY id ASC"
            cursor.execute(sql, (category,))
            players = cursor.fetchall()

    return render_template("testapp/judge_area_category.html", area=area, category=category, players=players)



    

