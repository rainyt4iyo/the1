from flask import render_template, request, redirect, url_for
from testapp import app, conn
import pymysql

@app.route('/')
def mainpage():
    return render_template('testapp/test.html')

@app.route('/judge_lobby')
def judge_lobby():
    return render_template('testapp/judge_lobby.html')

@app.route('/ranking_lobby')
def ranking_lobby():
    return render_template('testapp/ranking_lobby.html')

@app.route('/process_lobby')
def process_lobby():
    return render_template('testapp/process_lobby.html')

@app.route('/process_mid')
def process_mid():
    conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mid_result")
    data = cursor.fetchall()
    return render_template('testapp/process_mid.html', data=data)

@app.route('/mid_ranking')
def mid_ranking():
    conn = pymysql.connect(host='localhost',
                           user='t4',
                           password='t4_password',
                           database='myDB',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM mid_result")
    all_results = {row['id']: row for row in cursor.fetchall()}

    cursor.execute("SELECT id, point FROM mid_kadai")
    kadai_points = {row['id']: row['point'] for row in cursor.fetchall()}

    conn.close()

    team_point_list = []
    final_list = []

    for i in range(1, 49):
        member_ids = [3 * i - 2, 3 * i - 1, 3 * i]
        members = [all_results.get(mid) for mid in member_ids]
        temp_pt = 0

        if None in members:
            continue

        for k in range(1, 31):
            kadai_k = 'kadai_' + str(k)
            try:
                values = [member[kadai_k] for member in members]
            except KeyError:
                continue  

            if all(v == 1 for v in values):
                pt = kadai_points.get(k, 0)
                temp_pt = temp_pt + pt
            elif all(v == 2 for v in values):
                pt = kadai_points.get(k, 0) + 5
                temp_pt = temp_pt + pt
        
        team_point_list.append(temp_pt)

    for i in range(1,49):
        final_list.append((i,team_point_list[i-1]))
    sorted_list = sorted(final_list, key=lambda x: x[1], reverse=True)
    print(sorted_list)
        
    return render_template('testapp/mid_ranking.html', sorted_list=sorted_list)


@app.route('/mid/judge/<area>', methods=['GET'])
def judge_area(area):
    
    area_list = ["A","B","C","D","E","F","G","H","I","J","K","L","BB"]
    if area not in area_list:
        return render_template('testapp/error.html')
    else:
        return render_template('testapp/mid_judge.html', area=area)
    
@app.route('/funopen/judge/<area>', methods=['GET'])
def judge_area_fo(area):
    
    area_list = ["A","B","C","D","E","F","G","H","I","J","K","L","BB"]
    if area not in area_list:
        return render_template('testapp/error.html')
    else:
        return render_template('testapp/fo_judge.html', area=area)
    
    

@app.route('/mid/judge/<area>/team/<int:team_number>', methods=['GET','POST'])
def judge_page(area, team_number):
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                               user='t4',
                               password='t4_password',
                               database='myDB',
                               cursorclass=pymysql.cursors.DictCursor)
        
        cursor = conn.cursor()
        sql = '''SELECT id FROM mid_kadai WHERE area = %s'''
        cursor.execute(sql, (area,))
        res = cursor.fetchall()
        res = tuple(d['id'] for d in res)

        mins = 3 * team_number - 2
        maxs = 3 * team_number + 1

        sql = '''SELECT player FROM mid_player WHERE id >= %s and id < %s'''
        cursor.execute(sql, (mins, maxs))
        name = cursor.fetchall()
        name = tuple(d['player'] for d in name)

        sql = '''SELECT team FROM mid_player WHERE id = %s'''
        cursor.execute(sql, mins)
        tn = cursor.fetchone()
        team_name = tn['team']

        checked_list = []
        for r in res:
            for i in range(mins, maxs):
                sql = '''SELECT kadai_%s FROM mid_result WHERE id = %s'''
                cursor.execute(sql, (r,i))
                row = cursor.fetchone()
                if row and row[f'kadai_{r}'] == 1:
                    checked_list.append((r,i))

        conn.close()
        return render_template('testapp/mid_judge_team.html',
                               area=area,
                               team_number=team_number,
                               min=mins,
                               max=maxs,
                               res=res,
                               name=name,
                               team_name=team_name,
                               checked_list=checked_list)
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
        
        try:
            cursor = conn.cursor()
            sql = "SELECT id FROM mid_kadai WHERE area = %s"
            cursor.execute(sql, (area,))
            res = cursor.fetchall()
            res = tuple(d['id'] for d in res)
            mins = 3*team_number-2
            maxs = 3*team_number+1
            print(res, mins, maxs)
            conn.commit()

            for r in res:
                for i in range(mins, maxs):
                    checked = request.form.get(f"check_{i}_{r}")
                    value = 1 if checked else 0
                    sql = f"UPDATE mid_result SET `kadai_{r}` = {value} WHERE id = {i}"
                    cursor.execute(sql)
                    conn.commit()

        except Exception as e:
            print(e)
        finally:
            conn.close()
        
                
        return redirect(url_for('judge_area', area=area))
    
@app.route('/fun/judge/<area>/team/<int:team_number>', methods=['GET','POST'])
def judge_page_fun(area, team_number):
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                               user='t4',
                               password='t4_password',
                               database='myDB',
                               cursorclass=pymysql.cursors.DictCursor)
        
        cursor = conn.cursor()
        sql = '''SELECT id FROM fun_kadai WHERE area = %s'''
        cursor.execute(sql, (area,))
        res = cursor.fetchall()
        res = tuple(d['id'] for d in res)

        mins = 3 * team_number - 2
        maxs = 3 * team_number + 1

        sql = '''SELECT player FROM fun_player WHERE id >= %s and id < %s'''
        cursor.execute(sql, (mins, maxs))
        name = cursor.fetchall()
        name = tuple(d['player'] for d in name)

        sql = '''SELECT team FROM fun_player WHERE id = %s'''
        cursor.execute(sql, mins)
        tn = cursor.fetchone()
        team_name = tn['team']

        checked_list = []
        for r in res:
            for i in range(mins, maxs):
                sql = '''SELECT kadai_%s FROM fun_result WHERE id = %s'''
                cursor.execute(sql, (r,i))
                row = cursor.fetchone()
                if row and row[f'kadai_{r}'] == 1:
                    checked_list.append((r,i))

        conn.close()
        return render_template('testapp/fun_judge_team.html',
                               area=area,
                               team_number=team_number,
                               min=mins,
                               max=maxs,
                               res=res,
                               name=name,
                               team_name=team_name,
                               checked_list=checked_list)
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
        
        try:
            cursor = conn.cursor()
            sql = "SELECT id FROM fun_kadai WHERE area = %s"
            cursor.execute(sql, (area,))
            res = cursor.fetchall()
            res = tuple(d['id'] for d in res)
            mins = 3*team_number-2
            maxs = 3*team_number+1
            print(res, mins, maxs)
            conn.commit()

            for r in res:
                for i in range(mins, maxs):
                    checked = request.form.get(f"check_{i}_{r}")
                    value = 1 if checked else 0
                    sql = f"UPDATE fun_result SET `kadai_{r}` = {value} WHERE id = {i}"
                    cursor.execute(sql)
                    conn.commit()

        except Exception as e:
            print(e)
        finally:
            conn.close()
        
                
        return redirect(url_for('judge_area_fo', area=area))
    


@app.route('/mid/judge/<area>/team/<int:team_number>/<handorfoot>', methods=['GET','POST'])
def judge_page_special(area, team_number, handorfoot):
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                               user='t4',
                               password='t4_password',
                               database='myDB',
                               cursorclass=pymysql.cursors.DictCursor)
        
        cursor = conn.cursor()
        sql = '''SELECT id FROM mid_kadai WHERE area = %s'''
        cursor.execute(sql, (area,))
        res = cursor.fetchall()
        res = tuple(d['id'] for d in res)

        mins = 3 * team_number - 2
        maxs = 3 * team_number + 1

        sql = '''SELECT player FROM mid_player WHERE id >= %s and id < %s'''
        cursor.execute(sql, (mins, maxs))
        name = cursor.fetchall()
        name = tuple(d['player'] for d in name)

        sql = '''SELECT team FROM mid_player WHERE id = %s'''
        cursor.execute(sql, mins)
        tn = cursor.fetchone()
        team_name = tn['team']

        checked_list = []
        for r in res:
            for i in range(mins, maxs):
                sql = f'''SELECT kadai_{r} FROM mid_result WHERE id = %s'''
                cursor.execute(sql, (i,))
                row = cursor.fetchone()
                if row and row[f'kadai_{r}'] == 2:
                    checked_list.append((r,i))

        conn.close()
        return render_template('testapp/mid_judge_team_special.html',
                               area=area,
                               team_number=team_number,
                               min=mins,
                               max=maxs,
                               res=res,
                               name=name,
                               team_name=team_name,
                               checked_list=checked_list,
                               handorfoot=handorfoot)
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
        
        try:
            cursor = conn.cursor()
            sql = "SELECT id FROM mid_kadai WHERE area = %s"
            cursor.execute(sql, (area,))
            res = cursor.fetchall()
            res = tuple(d['id'] for d in res)
            mins = 3*team_number-2
            maxs = 3*team_number+1
            conn.commit()

            for r in res:
                for i in range(mins, maxs):
                    checked = request.form.get(f"check_{i}_{r}")
                    value = 2 if checked else 0
                    sql = f"UPDATE mid_result SET `kadai_{r}` = {value} WHERE id = {i}"
                    cursor.execute(sql)
                    conn.commit()

        except Exception as e:
            print(e)
        finally:
            conn.close()        
                
        return redirect(url_for('judge_area', area=area))


@app.route('/fun/judge/<area>/team/<int:team_number>/<handorfoot>', methods=['GET','POST'])
def judge_page_special_fun(area, team_number, handorfoot):
    if request.method == 'GET':
        conn = pymysql.connect(host='localhost',
                               user='t4',
                               password='t4_password',
                               database='myDB',
                               cursorclass=pymysql.cursors.DictCursor)
        
        cursor = conn.cursor()
        sql = '''SELECT id FROM fun_kadai WHERE area = %s'''
        cursor.execute(sql, (area,))
        res = cursor.fetchall()
        res = tuple(d['id'] for d in res)

        mins = 3 * team_number - 2
        maxs = 3 * team_number + 1

        sql = '''SELECT player FROM fun_player WHERE id >= %s and id < %s'''
        cursor.execute(sql, (mins, maxs))
        name = cursor.fetchall()
        name = tuple(d['player'] for d in name)

        sql = '''SELECT team FROM fun_player WHERE id = %s'''
        cursor.execute(sql, mins)
        tn = cursor.fetchone()
        team_name = tn['team']

        checked_list = []
        for r in res:
            for i in range(mins, maxs):
                sql = f'''SELECT kadai_{r} FROM fun_result WHERE id = %s'''
                cursor.execute(sql, (i,))
                row = cursor.fetchone()
                if row and row[f'kadai_{r}'] == 2:
                    checked_list.append((r,i))

        conn.close()
        return render_template('testapp/fun_judge_team_special.html',
                               area=area,
                               team_number=team_number,
                               min=mins,
                               max=maxs,
                               res=res,
                               name=name,
                               team_name=team_name,
                               checked_list=checked_list,
                               handorfoot=handorfoot)
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)
        
        try:
            cursor = conn.cursor()
            sql = "SELECT id FROM fun_kadai WHERE area = %s"
            cursor.execute(sql, (area,))
            res = cursor.fetchall()
            res = tuple(d['id'] for d in res)
            mins = 3*team_number-2
            maxs = 3*team_number+1
            conn.commit()

            for r in res:
                for i in range(mins, maxs):
                    checked = request.form.get(f"check_{i}_{r}")
                    value = 2 if checked else 0
                    sql = f"UPDATE fun_result SET `kadai_{r}` = {value} WHERE id = {i}"
                    cursor.execute(sql)
                    conn.commit()

        except Exception as e:
            print(e)
        finally:
            conn.close()        
                
        return redirect(url_for('judge_area_fo', area=area))


@app.route('/register_kadai', methods=['GET','POST'])
def registerpage_kadai():

    if request.method == 'GET':
        return render_template('testapp/register_kadai.html')
    
    if request.method == 'POST':

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)

        try:
            cursor = conn.cursor()

            id = request.form['id']
            category = request.form['category']
            area = request.form['area']
            point = request.form['point']

            if category == "FUN": 

                insert_sql = '''
                INSERT INTO fun_kadai (id, area, point)
                VALUES (%s, %s, %s)
                '''
                data = (id, area, point)
                cursor.execute(insert_sql, data)
                
                url = "registered_kadai_fun"

                conn.commit()

            if category == "MIDDLE": 

                insert_sql = '''
                INSERT INTO mid_kadai (id, area, point)
                VALUES (%s, %s, %s)
                '''
                data = (id, area, point)
                cursor.execute(insert_sql, data)
                
                url = "registered_kadai_mid"

                conn.commit()

            if category == "OPEN": 

                insert_sql = '''
                INSERT INTO open_kadai (id, area, point)
                VALUES (%s, %s, %s)
                '''
                data = (id, area, point)
                cursor.execute(insert_sql, data)
                
                url = "registered_kadai_open"

                conn.commit()

        except Exception as e:
            print(e)

        conn.close()
                
        return redirect(url_for(url))
    


    

@app.route('/registered_kadai_list_fun', methods=['GET', 'POST'])
def registered_kadai_fun():

    if request.method == 'GET':

        conn = pymysql.connect(host='localhost',
                            user='t4',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)

        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `area`, `point` from fun_kadai"
                cursor.execute(sql)
                result = cursor.fetchall()
                result = sorted(result, key=lambda x: x['id'])

        return render_template('testapp/registered_kadai_list_fun.html' , result = result)

    if request.method == 'POST':

        action = request.form.get("action")
        print(action)
        conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
        
        if action == "nuke":
            with conn:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM fun_kadai"
                    cursor.execute(sql)
                    sql = "alter table fun_kadai auto_increment = 1"
                    cursor.execute(sql)
                    conn.commit()
        else:
            action = int(action)
            with conn:
                with conn.cursor() as cursor:

                    sql = f"DELETE FROM fun_kadai where id = {action}"
                    cursor.execute(sql)
                    conn.commit()

        return render_template('testapp/temp_registered_kadai_list.html')

    
@app.route('/registered_kadai_list_mid', methods=['GET', 'POST'])
def registered_kadai_mid():

    if request.method == 'GET':

        conn = pymysql.connect(host='localhost',
                            user='t4',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)

        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `area`, `point` from mid_kadai"
                cursor.execute(sql)
                result = cursor.fetchall()
                result = sorted(result, key=lambda x: x['id'])

        return render_template('testapp/registered_kadai_list_mid.html' , result = result)

    if request.method == 'POST':

        action = request.form.get("action")
        print(action)
        conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
        
        if action == "nuke":
            with conn:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM mid_kadai"
                    cursor.execute(sql)
                    sql = "alter table mid_kadai auto_increment = 1"
                    cursor.execute(sql)
                    conn.commit()
        else:
            action = int(action)
            with conn:
                with conn.cursor() as cursor:

                    sql = f"DELETE FROM mid_kadai where id = {action}"
                    cursor.execute(sql)
                    conn.commit()

        return render_template('testapp/temp_registered_kadai_list.html')
    

@app.route('/registered_kadai_list_open', methods=['GET', 'POST'])
def registered_kadai_open():

    if request.method == 'GET':

        conn = pymysql.connect(host='localhost',
                            user='t4',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)

        with conn:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `area`, `point` from open_kadai"
                cursor.execute(sql)
                result = cursor.fetchall()
                result = sorted(result, key=lambda x: x['id'])

        return render_template('testapp/registered_kadai_list_open.html' , result = result)

    if request.method == 'POST':

        action = request.form.get("action")
        print(action)
        conn = pymysql.connect(host='localhost',
                        user='t4',
                        password='t4_password',
                        database='myDB',
                        cursorclass=pymysql.cursors.DictCursor)
        
        if action == "nuke":
            with conn:
                with conn.cursor() as cursor:

                    sql = "DELETE FROM open_kadai"
                    cursor.execute(sql)
                    sql = "alter table open_kadai auto_increment = 1"
                    cursor.execute(sql)
                    conn.commit()
        else:
            action = int(action)
            with conn:
                with conn.cursor() as cursor:

                    sql = f"DELETE FROM open_kadai where id = {action}"
                    cursor.execute(sql)
                    conn.commit()

        return render_template('testapp/temp_registered_kadai_list.html')
    

@app.route('/temp_registered_kadai_list')
def temp_registered_kadai_list():

    return render_template('testapp/temp_registered_kadai_list.html')


@app.route('/registered_player_list')
def registered_player_list():

        conn = pymysql.connect(host='localhost',
                            user='t4',
                            password='t4_password',
                            database='myDB',
                            cursorclass=pymysql.cursors.DictCursor)

        try:
            with conn.cursor() as cursor:
                sql = "SELECT `id`, `player`, `team` from fun_player"
                cursor.execute(sql)
                result_fun = cursor.fetchall()
                result_fun = sorted(result_fun, key=lambda x: (x['id'] is None, x['id']))
                
                sql = "SELECT `id`, `player`, `team` from mid_player"
                cursor.execute(sql)
                result_mid = cursor.fetchall()
                result_mid = sorted(result_mid, key=lambda x: (x['id'] is None, x['id']))

                sql = "SELECT `id`, `player`, `team` from open_player"
                cursor.execute(sql)
                result_open = cursor.fetchall()
                result_open = sorted(result_open, key=lambda x: (x['id'] is None, x['id']))

        finally:
            conn.close()


        return render_template('testapp/registered_player_list.html' , 
                               result_mid = result_mid, 
                               result_fun = result_fun, 
                               result_open = result_open,
                               )