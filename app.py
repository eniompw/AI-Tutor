from flask import Flask, session
import os 
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.urandom(16)
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/qp')
def question():
    f = open("/tmp/qp.txt", "r")
    qp = f.read()
    f.close()
    qpinstructions = "output just the first question from this text and nothing else (use html to present the information nicely)"
    # nextQ = session['question'] + "output the next question from the text and nothing else (use html to present the information nicely)"
    q = model.generate_content([qpinstructions, qp])
    session['question'] = q.text
    return q.text

@app.route('/ms')
def answer():
    f = open("/tmp/ms.txt", "r")
    ms = f.read()
    f.close()
    msinstructions = "output the text from the following document that relates to this question and nothing else (use html to present the information nicely)" + session['question']
    q = model.generate_content([msinstructions, ms])
    return q.text