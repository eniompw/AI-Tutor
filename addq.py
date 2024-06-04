import sqlite3
import os
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

def readfile(file):
    f = open("/tmp/"+file+".txt", "r")
    text = f.read()
    f.close()
    return text

def cleanup(text):
    # Split the string into lines
    lines = text.split('\n')
    # Remove the first line
    lines = lines[1:]
    # Join the remaining lines back into a single string
    return '\n'.join(lines)


con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute("SELECT * FROM Questions ORDER BY QID DESC")
row = cur.fetchall()
con.close()

q = "from the following exam question paper: \n"
q += readfile("qp")
q += " \n extract the next question after this one: \n"
q += row[0][1]
print(row[0][1])
res = groqAI(q)
res = cleanup(res)
print(res)

con = sqlite3.connect('database.db')
cur = con.cursor()
cur.execute(""" INSERT INTO Questions (Question, Answer)
    VALUES (?, ?) """,
    (res, ""))
con.commit()
con.close()
print('question saved')