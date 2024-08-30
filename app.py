# Import necessary libraries
from flask import Flask, render_template, session, request, redirect, url_for, jsonify
import sqlite3
import os
from google.generativeai import configure, GenerativeModel
from groq import Groq
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(16)  # Set a random secret key for session management

# Set session lifetime to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Configure AI models
configure(api_key=os.getenv('GOOGLE_API_KEY'))  # Configure Google AI with API key
gemini_model = GenerativeModel('gemini-1.5-pro-exp-0827')  # Initialize Gemini model
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))  # Initialize Groq client

# Function to get AI response based on the selected model
def get_ai_response(model, query):
    if model == 'groq':
        # Use Groq model for response
        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": query}],
            model="gemma2-9b-it",
        )
        return chat_completion.choices[0].message.content
    elif model == 'gemini':
        # Use Gemini model for response
        response = gemini_model.generate_content(query)
        return response.text.replace("\n", "<br>")  # Replace newlines with HTML line breaks

# Function to fetch question data from the database
def get_question_data(subject):
    with sqlite3.connect(f"{subject}.db") as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT question, answer FROM Questions ORDER BY QID")
        return cur.fetchall()

# Route for the home page
@app.route('/')
def home():
    # Get the current subject from the session, or default to 'computing'
    current_subject = session.get('subject', 'computing')
    
    # Fetch question data for the current subject
    rows = get_question_data(current_subject)
    
    # Update session variables
    session['subject'] = current_subject
    session['total'] = len(rows)
    
    # Ensure number is within bounds or set to 0 if not present
    session['number'] = min(session.get('number', 0), max(0, len(rows) - 1))
    
    # Get the current question
    if rows:
        current_question = rows[session['number']]
        session['question'] = current_question['question'].replace('\n', '<br>')
        session['ms'] = current_question['answer']
    else:
        session['question'] = "No questions available for this subject."
        session['ms'] = ""

    return render_template('index.html', question=session['question'], subject=session['subject'])

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
@app.route('/<subject>', methods=['GET', 'POST'])
def set_subject(subject):
    if subject in ['biology', 'computing', 'physics']:
        session.clear()  # Clear the entire session
        session['subject'] = subject
        session['number'] = 0  # Reset question number when changing subject
        session.permanent = True  # Make the session permanent with the 30-minute lifetime
        if request.method == 'POST':
            return jsonify({"success": True, "subject": subject})
        return redirect(url_for('home'))
    if request.method == 'POST':
        return jsonify({"success": False, "subject": session.get('subject', 'computing')})
    return redirect(url_for('home'))  # Redirect to home even if subject is invalid

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

# Route to get next question
@app.route('/next')
def next_question():
    current_subject = session.get('subject', 'computing')
    rows = get_question_data(current_subject)
    session['number'] = min(session.get('number', 0) + 1, len(rows) - 1)
    
    if session['number'] < len(rows):
        current_question = rows[session['number']]
        session['question'] = current_question['question'].replace('\n', '<br>')
        session['ms'] = current_question['answer']
        return jsonify({
            'success': True,
            'question': session['question']
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No more questions available'
        })

# Route to get previous question
@app.route('/previous')
def previous_question():
    current_subject = session.get('subject', 'computing')
    rows = get_question_data(current_subject)
    session['number'] = max(0, session.get('number', 0) - 1)
    
    if session['number'] >= 0:
        current_question = rows[session['number']]
        session['question'] = current_question['question'].replace('\n', '<br>')
        session['ms'] = current_question['answer']
        return jsonify({
            'success': True,
            'question': session['question']
        })
    else:
        return jsonify({
            'success': False,
            'message': 'This is the first question'
        })

# Run the Flask app in debug mode if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)