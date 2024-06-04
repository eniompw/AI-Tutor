import google.generativeai as genai
import os
import sqlite3

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

def readfile(file):
    f = open("/tmp/"+file+".txt", "r")
    text = f.read()
    f.close()
    return text


con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute("SELECT * FROM Questions ORDER BY QID DESC")
row = cur.fetchall()
con.close()
print(row[0][1])

q = "from the following exam mark scheme: \n"
q += readfile("ms")
q += " \n extract the answer from the mark scheme related to this question: (dont add anything else) \n"
q += row[0][1]

response = model.generate_content(q)
print(response.text)

con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute("UPDATE Questions SET Answer = ? WHERE Question = ?", (response.text, row[0][1]))
con.commit()
con.close()