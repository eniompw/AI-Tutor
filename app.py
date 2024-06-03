from flask import Flask, session
import os 
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.urandom(16)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    return 'use /qp and /ms'

@app.route('/qp')
def question():
    f = open("/tmp/qp.txt", "r")
    qp = f.read()
    f.close()
    qptext = "output just the first question from this text that ends with square brackets [] and nothing else"
    # nextQ = session['question'] + "output the next question from the text and nothing else (use html to present the information nicely)"
    q = model.generate_content([qptext, qp])
    session['question'] = q.text
    return q.text

@app.route('/ms')
def answer():
    f = open("/tmp/ms.txt", "r")
    ms = f.read()
    f.close()
    mstext = "output the text from the text that begins Mark Scheme that relates to this question stop when the next question starts with brackets () "
    mstext += session['question']
    q = model.generate_content([mstext, ms])
    session['answer'] = q.text
    print(session['answer'])
    q = model.generate_content(["remove markdown and format this using html", session['answer']])
    return q.text