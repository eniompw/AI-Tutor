from flask import Flask, render_template, session, request
import google.generativeai as genai
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
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
    
    session['question'] = str(tuple(processed_row))
    return render_template('index.html', question=session['question'], answer="")

@app.route('/response')
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

    query = "use this question: \n" 
    query += session['question']
    query += "the students answer: \n"
    query += request.args.get('ans')
    query += "and the mark scheme: \n"
    query += str(tuple(processed_row))
    query += "now give feedback on the students answer."
    response = model.generate_content(query)
    response = model.generate_content("remove markdown and format this using html: \n" + response.text)
    return render_template('index.html', question=session['question'], answer=response.text)