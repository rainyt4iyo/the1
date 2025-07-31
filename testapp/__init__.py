from flask import Flask
import pymysql

app = Flask(__name__)
app.config.from_object('testapp.config')

conn = pymysql.connect(host='localhost',
                       user='root',
                       password='t4_password',
                       database='myDB',
                       cursorclass=pymysql.cursors.DictCursor)

import testapp.views
