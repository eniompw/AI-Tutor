import google.generativeai as genai
import os
import sqlite3

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

f = open("/tmp/qp.txt", "r")
qp = f.read()
f.close()
qptext = "output just the first question from this text that ends with square brackets [] and nothing else"
# nextQ = session['question'] + "output the next question from the text and nothing else (use html to present the information nicely)"
q = model.generate_content([qptext, qp])
question = q.text
print ('question generated')

f = open("/tmp/ms.txt", "r")
ms = f.read()
f.close()
mstext = "output the answer from the Mark Scheme that relates to this question stop before the next question starts indicated with brackets () "
mstext += question
q = model.generate_content([mstext, ms])
answer = q.text
print ('answer generated')

con = sqlite3.connect("database.db")
cur = con.cursor()
cur.execute(""" INSERT INTO Questions (Question, Answer)
        VALUES (?, ?) """,
        (question, answer))
con.commit()
con.close()
print ('question saved')

#q = model.generate_content(["remove markdown and format this using html", session['answer']])