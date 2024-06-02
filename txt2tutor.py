import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

f = open("qp.txt", "r")
qp = f.read()
f.close()

f = open("ms.txt", "r")
ms = f.read()
f.close()

qpinstructions = "output just the first question from this text and nothing else"
q = model.generate_content([qpinstructions, qp])
print(q.text)
qpinstructions = q.text + "output the next question from the text and nothing else: "
q = model.generate_content([qpinstructions, qp])
# msinstructions = "output the text from the following document that relates to this question and nothing else " + q.text
# q = model.generate_content([msinstructions, ms])
print(q.text)
