# Import necessary libraries
from flask import Flask, render_template, session, request, redirect
import sqlite3
import os
from google.generativeai import configure, GenerativeModel
from groq import Groq

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(16)  # Set a random secret key for session management

# Configure AI models
configure(api_key=os.getenv('GOOGLE_API_KEY'))  # Configure Google AI with API key
gemini_model = GenerativeModel('gemini-1.5-flash')  # Initialize Gemini model
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))  # Initialize Groq client

# Function to get AI response based on the selected model
def get_ai_response(model, query):
    if model == 'groq':
        # Use Groq model for response
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    elif model == 'gemini':
        # Use Gemini model for response
        response = gemini_model.generate_content(query)
        return response.text.replace("\n", "<br>")  # Replace newlines with HTML line breaks

# Function to fetch question data from the database
def get_question_data():
    with sqlite3.connect(f"{session['subject']}.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT question, answer FROM Questions ORDER BY QID")
        return cur.fetchall()

# Route for the home page
@app.route('/')
def home():
    # Initialize session variables if not set
    session.setdefault('number', 0)
    session.setdefault('subject', 'computing')
    
    # Fetch question data
    rows = get_question_data()
    session['total'] = len(rows)
    session['question'] = rows[session['number']]['question']
    session['ms'] = rows[session['number']]['answer']

    return render_template('index.html', question=session['question'])

# Route to get AI response
@app.route('/ai_response/<model>')
def ai_response(model):
    # Define query templates for different models
    query_templates = {
        'groq': """
        Question: {question}
        Mark scheme: {ms}
        Write a short and concise summary (Don't narrate your response).
        """,
        'gemini': """
        Question: {question}
        Student's answer: {answer}
        Mark scheme: {ms}
        I am the student now mark my answer and give clear and detailed feedback on it.
        """
    }
    
    # Format the query based on the selected model
    query = query_templates[model].format(
        question=session['question'],
        answer=request.args.get('answer'),
        ms=session['ms'] if model == 'gemini' else ''
    )
    
    # Get and return the AI response
    return get_ai_response(model, query)

# Route to get current subject
@app.route('/subject')
def get_subject():
    return session['subject']

# Route to set subject
@app.route('/<subject>')
def set_subject(subject):
    if subject in ['biology', 'computing']:
        session['subject'] = subject
    return redirect('/')

# Route to get current question number
@app.route('/number')
def get_number():
    return str(session['number'])

# Route to navigate between questions
@app.route('/<direction>')
def navigate(direction):
    if direction == 'previous':
        session['number'] = max(0, session['number'] - 1)
    elif direction == 'next':
        session['number'] = min(session['total'] - 1, session['number'] + 1)
    return redirect('/')

# Run the Flask app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)