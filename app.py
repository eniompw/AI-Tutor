from flask import Flask, render_template, session, request
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(16)

# import google.generativeai as genai
# genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# model = genai.GenerativeModel('gemini-1.5-flash')

from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"),)

@app.route('/')
def home():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT question FROM Questions")
    row = cur.fetchone()
    con.close()

    query = "clean this up and replace it with well presented html (don't mention the formatting of your response): "
    session['question'] = groqAI(query + n2br(row))
    return render_template('index.html', question=session['question'], answer="")

@app.route('/response')
def answer():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT answer FROM Questions")
    row = cur.fetchone()
    con.close()

    query = "use this question: \n" 
    query += session['question']
    query += "\n the students answer: \n"
    query += request.args.get('ans')
    query += "\n and the mark scheme: \n"
    query += n2br(row)
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