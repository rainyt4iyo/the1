from flask import render_template, request, redirect, url_for
from testapp import app, conn
import pymysql

import time
import logging
from contextlib import contextmanager

@app.route('/')
def admin():
    return render_template('testapp/test.html')
