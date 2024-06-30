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
    model="llama3-8b-8192",
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
    session['question'] = row[session['number']][0]

    query = "use html and not markdown to present / format this question correctly"
    query += "(dont talk about the html in your answer or add any other content): \n"
    return render_template('index.html', question=session['question'])

@app.route('/llama')
def llama():
    con = sqlite3.connect(session['subject']+".db")
    cur = con.cursor()
    cur.execute("SELECT answer FROM Questions ORDER BY QID")
    row = cur.fetchall()
    con.close()
    session['ms'] = n2br(row[session['number']][0])

    query = "use this question: \n" 
    query += session['question']
    query += "\n the students answer: \n"
    query += request.args.get('answer')
    query += "\n and the mark scheme: \n"
    query += session['ms']
    query += "\n now give the student short and concise feedback on thier answer."
    query += "\n (don't narrate your response)"
    response = groqAI(query)
    return response

def n2br(row):
    processed_row = []
    for field in row:
        if isinstance(field, str):
            field = field.replace("\n", "<br>")
        processed_row.append(field)
    return str(tuple(processed_row))

@app.route('/gemini')
def gemini():
    query = "use this question (marks are in square brackets []): \n" 
    query += session['question']
    query += "\n the students answer: \n"
    query += request.args.get('answer')
    query += "\n and the mark scheme: \n"
    query += session['ms']
    query += "\n now mark the student answer and give clear and detailed feedback on it."
    query += "\n (don't use markdown instead use minimal html to format your response)"
    response = model.generate_content(query)
    return response.text

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

@app.route('/number')
def number():
    return str(session['number'])

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