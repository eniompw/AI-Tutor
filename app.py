from flask import Flask, render_template, session, request, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

# import google.generativeai as genai
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# model = genai.GenerativeModel('gemini-1.5-flash')

from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

def groqAI(q):
    chat_completion = client.chat.completions.create(
    messages=[
        {   
            "role": "user",
            "content": str(q),
        }
    ],
    model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

@app.route('/previous')
def previous():
    if session['number'] > 0:
        session['number'] -= 1
    return redirect('/')

@app.route('/next')
def next():
    if session['number'] < session['total']:
        session['number'] += 1
    return redirect('/')

@app.route('/')
def home():
    if 'number' not in session:
        session['number'] = 0
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT question FROM Questions ORDER BY QID DESC")
    row = cur.fetchall()
    con.close()
    session['total'] = len(row)
    query = "clean this up and replace it with well presented html "
    query += "only show the question in your response dont add anything else: "
    session['question'] = groqAI(query + n2br(row[session['number']][0]))
    # session['question'] = model.generate_content(query + n2br(row[session['number']][0]))
    return render_template('index.html', question=session['question'], answer="")

@app.route('/response')
def answer():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT answer FROM Questions ORDER BY QID DESC")
    row = cur.fetchall()
    con.close()

    query = "use this question (marks are in square brackets []): \n" 
    query += session['question']
    query += "\n the students answer: \n"
    query += request.args.get('ans')
    query += "\n and the mark scheme: \n"
    query += n2br(row[session['number']][0])
    query += "\n now give feedback on the students answer."

    # response = model.generate_content(query)
    # response = model.generate_content("remove markdown and format this using html: \n" + response.text)
    # return render_template('index.html', question=session['question'], answer=response.text)

    response = groqAI(query)
    response = groqAI("remove markdown and format this using html. (don't mention the formatting of your response): \n" + response)
    return render_template('index.html', question=session['question'], answer=response)

def n2br(row):
    processed_row = []
    for field in row:
        if isinstance(field, str):
            field = field.replace("\n", "<br>")
        processed_row.append(field)
    return str(tuple(processed_row))