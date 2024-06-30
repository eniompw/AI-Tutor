from flask import Flask, render_template, session, request, redirect
import sqlite3
import os
import google.generativeai as genai
from groq import Groq

app = Flask(__name__)
app.secret_key = os.urandom(16)

# Configure AI models
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def groq_ai(query):
    chat_completion = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": query}],
        model="llama3-8b-8192",
    )
    return chat_completion.choices[0].message.content

@app.route('/')
def home():
    session.setdefault('number', 0)
    session.setdefault('subject', 'computing')
    
    with sqlite3.connect(f"{session['subject']}.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT question, answer FROM Questions ORDER BY QID")
        rows = cur.fetchall()
    
    session['total'] = len(rows)
    session['question'] = rows[session['number']]['question']
    session['ms'] = rows[session['number']]['answer'].replace("\n", "<br>")

    return render_template('index.html', question=session['question'])

@app.route('/llama')
def llama():
    query = f"""
    Use this question:
    {session['question']}
    
    The student's answer:
    {request.args.get('answer')}
    
    And the mark scheme:
    {session['ms']}
    
    Now give the student short and concise feedback on their answer.
    (Don't narrate your response)
    """
    return groq_ai(query)

@app.route('/gemini')
def gemini():
    query = f"""
    Use this question (marks are in square brackets []):
    {session['question']}
    
    The student's answer:
    {request.args.get('answer')}
    
    And the mark scheme:
    {session['ms']}
    
    Now mark the student answer and give clear and detailed feedback on it.
    (Don't use markdown; instead, use minimal HTML to format your response)
    """
    response = gemini_model.generate_content(query)
    return response.text

@app.route('/subject')
def subject():
    return session['subject']

@app.route('/bio')
def bio():
    session['subject'] = 'biology'
    return redirect('/')

@app.route('/cs')
def cs():
    session['subject'] = 'computing'
    return redirect('/')

@app.route('/number')
def number():
    return str(session['number'])

@app.route('/previous')
def previous():
    session['number'] = max(0, session['number'] - 1)
    return redirect('/')

@app.route('/next')
def next():
    session['number'] = min(session['total'] - 1, session['number'] + 1)
    return redirect('/')
