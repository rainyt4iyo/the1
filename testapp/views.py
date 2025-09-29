from flask import render_template, request, redirect, url_for
from testapp import app
import pymysql
import time
import logging
from contextlib import contextmanager

def categorytranslate(category):
    if category == "asp_men":
        return "Aspirant 男子"
    elif category == "asp_wmn":
        return "Aspirant 女子"  
    elif category == "fin_men":
        return "Finals 男子"   
    elif category == "fin_wmn":
        return "Finals 女子"

@app.route('/')
def mainpage():
    return render_template('testapp/mainpage.html')

@app.route('/rules')
def rules():
    return render_template('testapp/rules.html')

@app.route('/admin')
def admin():
    return render_template('testapp/admin.html')

@app.route('/competitors')
def competitors():
    return render_template('testapp/competitors.html')

@app.route('/competitors/<category>')
def competitorslist(category):

    allowed_categories = ['asp_men', 'asp_wmn', 'fin_men', 'fin_wmn']
    if category not in allowed_categories:
        return render_template('testapp/error.html')
    else:
        pass

    conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    try:
        with conn.cursor() as cursor:
            sql = f"SELECT `id`, `player` from {category} ORDER BY id"
            cursor.execute(sql)
            listed = cursor.fetchall()
            listed = sorted(listed, key=lambda x: (x['id'] is None, x['id']))

    finally:
        conn.close()

    category = categorytranslate(category)

    return render_template('testapp/competitors_list.html', 
                               listed=listed,
                               category=category)

@app.route('/judge/<category>/<problem>')
def judgeselect(category, problem):
    cat_name = categorytranslate(category)
    return render_template('testapp/judgeselect.html', category=category, problem=problem, cat_name=cat_name)

@app.route('/judge/<category>/<problem>/<player_number>', methods=['GET', 'POST'])
def judgefeed(category, problem, player_number):
    if request.method == 'GET':
        cat_name = categorytranslate(category)

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                if problem == "p1":
                    sql = f"SELECT player, z1, t1 from {category} WHERE id = %s"   
                elif problem == "p2":
                    sql = f"SELECT player, z2, t2 from {category} WHERE id = %s"
                elif problem == "p3":
                    sql = f"SELECT player, z3, t3 from {category} WHERE id = %s"
                elif problem == "p4":
                    sql = f"SELECT player, z4, t4 from {category} WHERE id = %s"
                else:
                    return render_template('testapp/error.html')
                temp = (player_number,)
                cursor.execute(sql, temp) 
                playerdata = cursor.fetchone()
        finally:
            conn.close()

        print(playerdata)

        player_name = playerdata['player']

        if problem == "p1":
            zonegot = playerdata['z1']
            topgot = playerdata['t1']
        elif problem == "p2":
            zonegot = playerdata['z2']
            topgot = playerdata['t2']    
        elif problem == "p3":
            zonegot = playerdata['z3']
            topgot = playerdata['t3']
        elif problem == "p4":
            zonegot = playerdata['z4']
            topgot = playerdata['t4']

        if zonegot == None:
            zonegot = 0
        if topgot == None:
            topgot = 0

        return render_template('testapp/judgefeed.html',category=category, 
                                                        problem=problem, 
                                                        player_name=player_name, 
                                                        player_number=player_number, 
                                                        cat_name=cat_name,
                                                        zonegot=zonegot,
                                                        topgot=topgot)
    
    if request.method == 'POST':
        zone = request.form.get('zone')
        top = request.form.get('top')
        zone_attempt = request.form.get('zone_attempt')
        top_attempt = request.form.get('top_attempt')

        #print(zone, top, zone_attempt, top_attempt)

        if zone == 'on':
            zone_value = zone_attempt
        else:
            zone_value = 0

        if top == 'on':
            top_value = top_attempt
        else:
            top_value = 0

        #print(zone_value, top_value)

        conn = pymysql.connect(host='localhost',
                       user='t4',
                       password='t4_password',
                       database='the1',
                       cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()

        try:
            with conn.cursor() as cursor:
                if problem == "p1":
                    sql = f"UPDATE {category} SET z1 = %s, t1 = %s WHERE id = %s"
                elif problem == "p2":
                    sql = f"UPDATE {category} SET z2 = %s, t2 = %s WHERE id = %s"
                elif problem == "p3":
                    sql = f"UPDATE {category} SET z3 = %s, t3 = %s WHERE id = %s"
                elif problem == "p4":
                    sql = f"UPDATE {category} SET z4 = %s, t4 = %s WHERE id = %s"
                else:
                    return render_template('testapp/error.html')

                temp = (zone_value, top_value, player_number)
                cursor.execute(sql, temp)
                conn.commit()

        finally:
            conn.close()

        return redirect(url_for('judgeselect', category=category, problem=problem))

@app.route('/ranking/<category>')
def ranking(category):
    return render_template('testapp/ranking.html', category=category)