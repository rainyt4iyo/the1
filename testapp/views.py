from flask import render_template, request, redirect, url_for
from testapp import app, conn
import pymysql

import time
import logging
from contextlib import contextmanager

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# デッドロック対策のためのリトライ設定
MAX_RETRIES = 3
RETRY_DELAY = 0.1  # 100ms

@contextmanager
def get_db_connection():
    """データベース接続のコンテキストマネージャー"""
    conn = None
    try:
        conn = pymysql.connect(
            host='localhost',
            user='t4',
            password='t4_password',
            database='myDB',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,  # 明示的にautocommitを無効化
            charset='utf8mb4'
        )
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute_with_retry(func, max_retries=MAX_RETRIES):
    """デッドロック発生時のリトライ機能"""
    for attempt in range(max_retries):
        try:
            return func()
        except pymysql.MySQLError as e:
            if e.args[0] == 1213:  # デッドロックエラーコード
                if attempt < max_retries - 1:
                    logger.warning(f"DEADLOCK HAS OCCURRED リトライします (試行 {attempt + 1}/{max_retries})")
                    time.sleep(RETRY_DELAY * (2 ** attempt))  # 指数バックオフ
                    continue
                else:
                    logger.error("最大リトライ回数に達しました")
                    raise
            else:
                raise
    return None

@app.route('/')
def mainpage():
    return render_template('testapp/test.html')

@app.route('/admin')
def admin():
    return render_template('testapp/admin.html')

@app.route('/rules')
def rules():
    return render_template('testapp/rules.html')

@app.route('/judge_lobby')
def judge_lobby():
    return render_template('testapp/judge_lobby.html')

@app.route('/ranking_lobby')
def ranking_lobby():
    return render_template('testapp/ranking_lobby.html')

@app.route('/process_lobby')
def process_lobby():
    return render_template('testapp/process_lobby.html')

def fetch_process_data(category):
    def fetch_data():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {category}_result ORDER BY id")
                return cursor.fetchall()
    
    return execute_with_retry(fetch_data)

def fetch_player_data(category):
    def fetch_data():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {category}_player ORDER BY id")
                return cursor.fetchall()
    
    return execute_with_retry(fetch_data)

@app.route('/process_fun')
def process_fun():
    data = fetch_process_data('fun')
    player = fetch_player_data('fun')
    for i in data:
        ids = i['id']
        for j in player:
            if ids == j['id']:
                i['player'] = j['player']
    return render_template('testapp/process_fun.html', data=data)

@app.route('/process_mid')
def process_mid():
    data = fetch_process_data('mid')
    player = fetch_player_data('mid')
    for i in data:
        ids = i['id']
        for j in player:
            if ids == j['id']:
                i['player'] = j['player']
    return render_template('testapp/process_mid.html', data=data)

@app.route('/process_open')
def process_open():
    data = fetch_process_data('open')
    player = fetch_player_data('open')
    for i in data:
        ids = i['id']
        for j in player:
            if ids == j['id']:
                i['player'] = j['player']
    return render_template('testapp/process_open.html', data=data)

def calculate_ranking(category):
    """ランキング計算の共通関数"""
    def fetch_and_calculate():
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # 一貫した順序でデータを取得
                cursor.execute(f"SELECT * FROM {category}_result ORDER BY id")
                all_results = {row['id']: row for row in cursor.fetchall()}

                cursor.execute(f"SELECT id, point FROM {category}_kadai ORDER BY id")
                kadai_points = {row['id']: row['point'] for row in cursor.fetchall()}

                cursor.execute(f"SELECT id, team FROM {category}_player ORDER BY id")
                teams = {row['id']: row['team'] for row in cursor.fetchall()}

        team_name = [v for i, v in teams.items() if i is not None and (i - 1) % 3 == 0]
        team_point_list = []
        final_list = []

        for i in range(1, 49):
            member_ids = [3 * i - 2, 3 * i - 1, 3 * i]
            members = [all_results.get(mid) for mid in member_ids]
            temp_pt = 0
            send_list = []
            send_sum = 0

            if None in members:
                continue

            for k in range(1, 31):
                kadai_k = 'kadai_' + str(k)
                try:
                    values = [member[kadai_k] for member in members]
                    send_sum = send_sum + values.count(1) + values.count(2)
                except KeyError:
                    continue  

                if all(v == 2 for v in values):
                    pt = kadai_points.get(k, 0) + 5
                    temp_pt = temp_pt + pt
                    send_list.append(2)
                elif all(v != 0 for v in values):
                    pt = kadai_points.get(k, 0)
                    temp_pt = temp_pt + pt
                    send_list.append(1)
                else:
                    send_list.append(0)
            
            if i <= len(team_name) and '*' in team_name[i-1]:
                temp_pt = temp_pt + 50

            team_point_list.append((temp_pt, send_list, send_sum))

        for i in range(1, min(49, len(team_name) + 1)):
            final_list.append((team_name[i-1], team_point_list[i-1]))
        
        return sorted(final_list, key=lambda x: (x[1][0], x[1][2]), reverse=True)
    
    return execute_with_retry(fetch_and_calculate)

@app.route('/fun_ranking')
def fun_ranking():
    sorted_list = calculate_ranking('fun')
    return render_template('testapp/fun_ranking.html', sorted_list=sorted_list)

@app.route('/mid_ranking')
def mid_ranking():
    sorted_list = calculate_ranking('mid')
    return render_template('testapp/mid_ranking.html', sorted_list=sorted_list)

@app.route('/open_ranking')
def open_ranking():
    sorted_list = calculate_ranking('open')
    return render_template('testapp/open_ranking.html', sorted_list=sorted_list)

@app.route('/fun_output')
def fun_output():
    sorted_list = calculate_ranking('fun')
    return render_template('testapp/fun_output.html', sorted_list=sorted_list)

@app.route('/mid_output')
def mid_output():
    sorted_list = calculate_ranking('mid')
    return render_template('testapp/mid_output.html', sorted_list=sorted_list)

@app.route('/open_output')
def open_output():
    sorted_list = calculate_ranking('open')
    return render_template('testapp/open_output.html', sorted_list=sorted_list)


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
    
    

@app.route('/<category>/judge/<area>/team/<int:team_number>', methods=['GET','POST'])
def judge_page(category, area, team_number):
    if request.method == 'GET':
        def fetch_data():
            with get_db_connection() as conn:
                with conn.cursor() as cursor:

                    sql = f'''SELECT id FROM {category}_kadai WHERE area = %s ORDER BY id'''
                    cursor.execute(sql, (area,))
                    res = cursor.fetchall()
                    res = tuple(d['id'] for d in res)

                    mins = 3 * team_number - 2
                    maxs = 3 * team_number + 1

                    sql = f'''SELECT player FROM {category}_player WHERE id >= %s and id < %s ORDER BY id'''
                    cursor.execute(sql, ( mins, maxs))
                    name = cursor.fetchall()
                    name = tuple(d['player'] for d in name)

                    sql = f'''SELECT team FROM {category}_player WHERE id = %s'''
                    cursor.execute(sql, (mins,))
                    tn = cursor.fetchone()
                    team_name = tn['team'] if tn else ""

                    checked_list = []
                    locked_list = []
                    for r in res:
                        for i in range(mins, maxs):
                            sql = f'''SELECT kadai_%s FROM {category}_result WHERE id = %s'''
                            cursor.execute(sql, (r, i))
                            row = cursor.fetchone()
                            if row and row[f'kadai_{r}'] == 1:
                                checked_list.append((r, i))
                            elif row and row[f'kadai_{r}'] == 2:
                                locked_list.append((r, i))

                    return {
                        'res': res,
                        'mins': mins,
                        'maxs': maxs,
                        'name': name,
                        'team_name': team_name,
                        'checked_list': checked_list,
                        'locked_list': locked_list
                    }
        
        try:
            data = execute_with_retry(fetch_data)
            return render_template(f'testapp/{category}_judge_team.html',
                                   area=area,
                                   team_number=team_number,
                                   min=data['mins'],
                                   max=data['maxs'],
                                   res=data['res'],
                                   name=data['name'],
                                   team_name=data['team_name'],
                                   checked_list=data['checked_list'],
                                   locked_list=data['locked_list'])
        except Exception as e:
            logger.error(f"Judge page data fetch failed: {e}")
            return render_template('testapp/error.html')
    
    if request.method == 'POST':
        def update_data():
            with get_db_connection() as conn:
                try:
                    with conn.cursor() as cursor:
                        sql = f"SELECT id FROM {category}_kadai WHERE area = %s ORDER BY id"
                        cursor.execute(sql, (area,))
                        res = cursor.fetchall()
                        res = tuple(d['id'] for d in res)
                        mins = 3 * team_number - 2
                        maxs = 3 * team_number + 1

                        # 更新順序を一定にするため、更新をまとめて処理
                        updates = []
                        for r in res:
                            for i in range(mins, maxs):
                                # 現在の値を取得（プレースホルダーを使用）
                                sql = f"SELECT kadai_%s FROM {category}_result WHERE id = %s"
                                cursor.execute(sql, (r, i))
                                data = cursor.fetchone()
                                current_value = data[f'kadai_{r}'] if data else 0
                                
                                checked = request.form.get(f"check_{i}_{r}")
                                
                                if current_value != 2:
                                    new_value = 1 if checked else 0
                                else:
                                    new_value = 1 if checked else 2
                                
                                updates.append((r, i, new_value))
                        
                        # 更新処理をソートして一定の順序で実行
                        updates.sort(key=lambda x: (x[1], x[0]))  # id, kadai_idの順でソート
                        
                        for r, i, value in updates:
                            sql = f"UPDATE {category}_result SET kadai_%s = %s WHERE id = %s"
                            cursor.execute(sql, (r, value, i))
                        
                        conn.commit()
                        print(f"[UPDATED] {category}-{area}-{team_number}: {updates}")
                        
                except Exception as e:
                    conn.rollback()
                    raise e
        
        try:
            execute_with_retry(update_data)
        except Exception as e:
            logger.error(f"Judge page update failed: {e}")
        
        if category == 'mid':
            return redirect(url_for('judge_area', area=area))
        else:
            return redirect(url_for('judge_area_fo', area=area))
        


@app.route('/<category>/judge/<area>/team/<int:team_number>/<handorfoot>', methods=['GET','POST'])
def judge_page_special(category, area, team_number, handorfoot):
    if request.method == 'GET':
        def fetch_data():
            with get_db_connection() as conn:
                with conn.cursor() as cursor:

                    sql = f'''SELECT id FROM {category}_kadai WHERE area = %s ORDER BY id'''
                    cursor.execute(sql, (area,))
                    res = cursor.fetchall()
                    res = tuple(d['id'] for d in res)

                    mins = 3 * team_number - 2
                    maxs = 3 * team_number + 1

                    sql = f'''SELECT player FROM {category}_player WHERE id >= %s and id < %s ORDER BY id'''
                    cursor.execute(sql, (mins, maxs))
                    name = cursor.fetchall()
                    name = tuple(d['player'] for d in name)

                    sql = f'''SELECT team FROM {category}_player WHERE id = %s'''
                    cursor.execute(sql, (mins,))
                    tn = cursor.fetchone()
                    team_name = tn['team'] if tn else ""

                    checked_list = []
                    locked_list = []
                    for r in res:
                        for i in range(mins, maxs):
                            sql = f'''SELECT kadai_%s FROM {category}_result WHERE id = %s'''
                            cursor.execute(sql, (r, i))
                            row = cursor.fetchone()
                            if row and row[f'kadai_{r}'] == 2:
                                checked_list.append((r, i))

                    return {
                        'res': res,
                        'mins': mins,
                        'maxs': maxs,
                        'name': name,
                        'team_name': team_name,
                        'checked_list': checked_list,
                        'locked_list': locked_list,
                        'handorfoot': handorfoot
                    }
        
        try:
            data = execute_with_retry(fetch_data)
            return render_template(f'testapp/{category}_judge_team_special.html',
                                   area=area,
                                   team_number=team_number,
                                   min=data['mins'],
                                   max=data['maxs'],
                                   res=data['res'],
                                   name=data['name'],
                                   team_name=data['team_name'],
                                   checked_list=data['checked_list'],
                                   locked_list=data['locked_list'],
                                   handorfoot=data['handorfoot'])
        except Exception as e:
            logger.error(f"Judge page data fetch failed: {e}")
            return render_template('testapp/error.html')
    
    if request.method == 'POST':
        def update_data():
            with get_db_connection() as conn:
                try:
                    with conn.cursor() as cursor:
                        sql = f"SELECT id FROM {category}_kadai WHERE area = %s ORDER BY id"
                        cursor.execute(sql, (area,))
                        res = cursor.fetchall()
                        res = tuple(d['id'] for d in res)
                        mins = 3 * team_number - 2
                        maxs = 3 * team_number + 1

                        # 更新順序を一定にするため、更新をまとめて処理
                        updates = []
                        for r in res:
                            for i in range(mins, maxs):
                                # 現在の値を取得（プレースホルダーを使用）
                                sql = f"SELECT kadai_%s FROM {category}_result WHERE id = %s"
                                cursor.execute(sql, (r, i))
                                data = cursor.fetchone()
                                current_value = data[f'kadai_{r}'] if data else 0
                                
                                checked = request.form.get(f"check_{i}_{r}")
                                
                                if current_value != 1:
                                    new_value = 2 if checked else 0
                                else:
                                    new_value = 2 if checked else 1
                                
                                updates.append((r, i, new_value))
                        
                        # 更新処理をソートして一定の順序で実行
                        updates.sort(key=lambda x: (x[1], x[0]))  # id, kadai_idの順でソート
                        
                        for r, i, value in updates:
                            sql = f"UPDATE {category}_result SET kadai_%s = %s WHERE id = %s"
                            cursor.execute(sql, (r, value, i))
                        
                        conn.commit()
                        print(f"[UPDATED] ONEHAND / ONEFOOT * {category}-{area}-{team_number}: {updates}")
                        
                except Exception as e:
                    conn.rollback()
                    raise e
        
        try:
            execute_with_retry(update_data)
        except Exception as e:
            logger.error(f"Judge page update failed: {e}")
        
        if category == 'mid':
            return redirect(url_for('judge_area', area=area))
        else:
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
                sql = "SELECT `id`, `area`, `point` from fun_kadai ORDER BY id"
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
                sql = "SELECT `id`, `area`, `point` from mid_kadai ORDER BY id"
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
                sql = "SELECT `id`, `area`, `point` from open_kadai ORDER BY id"
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
                sql = "SELECT `id`, `player`, `team` from fun_player ORDER BY id"
                cursor.execute(sql)
                result_fun = cursor.fetchall()
                result_fun = sorted(result_fun, key=lambda x: (x['id'] is None, x['id']))
                
                sql = "SELECT `id`, `player`, `team` from mid_player ORDER BY id"
                cursor.execute(sql)
                result_mid = cursor.fetchall()
                result_mid = sorted(result_mid, key=lambda x: (x['id'] is None, x['id']))

                sql = "SELECT `id`, `player`, `team` from open_player ORDER BY id"
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