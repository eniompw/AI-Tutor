# AI-Powered Exam Tutor

This application is an interactive exam tutor that leverages AI to provide personalized feedback on student answers across multiple subjects.

## Key Features

* **Multi-Subject Support**: Covers Biology, Computing, and Physics.
* **AI-Powered Feedback**: Utilizes two AI models for comprehensive feedback:
  - Groq: Provides a concise summary of the answer.
  - Gemini: Offers detailed feedback and marking.
* **Interactive UI**: 
  - Easy subject switching
  - Navigation between questions
  - Real-time AI feedback
  - Progress tracking

## How It Works

1. **Subject Selection**: Users can choose between Biology, Computing, and Physics.
2. **Question Presentation**: Questions are fetched from a subject-specific SQLite database.
3. **Answer Submission**: Students enter their answers in a text area.
4. **AI Feedback**: 
   - Groq AI provides a quick summary.
   - Gemini AI offers detailed feedback and marking.
5. **Navigation**: Users can move between questions and try again as needed.

## Technical Stack

* **Backend**: Flask (Python)
* **Frontend**: HTML, CSS, JavaScript
* **AI Models**: 
  - Google's Gemini 1.5 Pro
  - Groq's Gemma 2 9B
* **Database**: SQLite

## Development Tools

* **PDF to TXT**: Convert PDF questions to text format
* **Add Question**: Tool to add new questions to the database
* **Add Answer**: Tool to add or update answer schemes

## Setup and Running

[Add instructions for setting up and running the application]

## Contributing

[Add information about how to contribute to the project]

## License

[Add license information]
