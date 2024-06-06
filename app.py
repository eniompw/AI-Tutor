from flask import Flask, render_template, session, request, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

import google.generativeai as genai
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

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
    model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content

@app.route('/')
def home():
    if 'number' not in session:
        session['number'] = 0
    if 'subject' not in session:
        session['subject'] = 'computing'
    
    con = sqlite3.connect(session['subject']+".db")
    cur = con.cursor()
    cur.execute("SELECT question FROM Questions ORDER BY QID")
    row = cur.fetchall()
    con.close()
    if 'total' not in session:
        session['total'] = len(row)
    question = row[session['number']][0]

    query = "use html and not markdown to present / format this question correctly"
    query += "(dont talk about the html in your answer or add any other content): \n"
    file_path = "/tmp/api.txt"
    if os.path.exists(file_path):
        f = open(file_path, "r")
        api = f.read()
        f.close()
        session['api'] = api
    else:
        session['api'] = "gemini"
    if session['api'] == "gemini":
        session['question'] = model.generate_content(query + question).text
    elif session['api'] == "llama":
        session['question'] = groqAI(query + question)
    else:
        return "select api" 
    return render_template('index.html', question=session['question'], answer="")

@app.route('/response')
def answer():
    con = sqlite3.connect(session['subject']+".db")
    cur = con.cursor()
    cur.execute("SELECT answer FROM Questions ORDER BY QID")
    row = cur.fetchall()
    con.close()

    query = "use this question (marks are in square brackets []): \n" 
    query += session['question']
    query += "\n the students answer: \n"
    query += request.args.get('ans')
    query += "\n and the mark scheme: \n"
    query += n2br(row[session['number']][0])
    query += "\n now mark the student answer and give feedback on it"

    if session['api'] == "gemini":
        response = model.generate_content(query)
        response = model.generate_content("remove markdown and format this using html: \n" + response.text).text
    elif session['api'] == "llama":
        response = groqAI(query)
        response = groqAI("remove markdown and format this using html. (don't mention the formatting of your response): \n" + response)
    else:
        return "select api"
    
    return render_template('index.html', question=session['question'], answer=response)

def n2br(row):
    processed_row = []
    for field in row:
        if isinstance(field, str):
            field = field.replace("\n", "<br>")
        processed_row.append(field)
    return str(tuple(processed_row))

@app.route('/subject')
def subject():
    return session['subject']

@app.route('/bio')
def bio():
    session['subject'] = 'biology'
    return session['subject']

@app.route('/cs')
def cs():
    session['subject'] = 'computing'
    return session['subject']

@app.route('/api')
def api():
    file_path = "/tmp/api.txt"
    if os.path.exists(file_path):
        f = open(file_path, "r")
        api = f.read()
        f.close()
        return api
    else:
        return "default: gemini"

@app.route('/gemini')
def gemini():
    f = open("/tmp/api.txt", "w")
    f.write("gemini")
    f.close()
    return 'gemini set'

@app.route('/llama')
def llama():
    f = open("/tmp/api.txt", "w")
    f.write("llama")
    f.close()
    return 'llama set'

@app.route('/previous')
def previous():
    if session['number'] > 0:
        session['number'] -= 1
    return redirect('/')

@app.route('/next')
def next():
    if session['number'] < session['total'] - 1:
        session['number'] += 1
    return redirect('/')