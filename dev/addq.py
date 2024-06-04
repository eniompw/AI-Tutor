
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
    model="llama3-8b-8192",
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

def addQ():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Questions")
    row = cur.fetchone()
    con.close()

    q = "from the following exam question paper: \n"
    q += readfile("qp")
    q += " \n extract the next question after this one: \n"
    q += row[1]
    res = groqAI(q)
    res = cleanup(res)

    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute(""" INSERT INTO Questions (Question, Answer)
        VALUES (?, ?) """,
        (res, ""))
    con.commit()
    con.close()
    print('question saved')

def addAns():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM Questions")
    row = cur.fetchall()
    con.close()
    print(row[1][1])

    q = "from the following exam mark scheme: \n"
    q += readfile("ms")
    q += " \n extract the text from the mark scheme related to this question: \n"
    q += row[1][1]
    print(groqAI(q))

    # db.execute("UPDATE Questions SET Answer = ? WHERE Question = ?", ans, row[1][1])
addAns()