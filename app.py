from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', output="")

@app.route('/q')
def question():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT question FROM Questions")
    row = cur.fetchone()
    con.close()

    processed_row = []
    for field in row:
        if isinstance(field, str):
            field = field.replace("\n", "<br>")
        processed_row.append(field)

    return str(tuple(processed_row))

@app.route('/a')
def answer():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT answer FROM Questions")
    row = cur.fetchone()
    con.close()

    processed_row = []
    for field in row:
        if isinstance(field, str):
            field = field.replace("\n", "<br>")
        processed_row.append(field)

    return str(tuple(processed_row))