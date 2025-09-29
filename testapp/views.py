from flask import render_template, request, redirect, url_for
from testapp import app
import time
import logging
from contextlib import contextmanager

@app.route('/')
def mainpage():
    return render_template('testapp/mainpage.html')

@app.route('/rules')
def rules():
    return render_template('testapp/rules.html')

@app.route('/ranking/<category>')
def ranking(category):
    return render_template('testapp/ranking.html', category=category)