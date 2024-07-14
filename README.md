# AI Fact Checker

This project is an AI-powered fact-checking web application that can analyze statements and images using Claude Sonnet 3.5 via OpenRouter.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-fact-checker.git
   cd ai-fact-checker
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the project root directory and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Running the Application

1. Make sure your virtual environment is activated.

2. Start the Flask development server:
   ```
   python app.py
   ```

3. Open a web browser and navigate to `http://127.0.0.1:5000` to use the AI Fact Checker.

## Usage

1. Enter a statement in the text area.
2. Optionally, upload an image related to the statement.
3. Click the "Check Facts" button to submit your request.
4. The AI will analyze the statement (and image, if provided) and display the results.

## Note

This application uses the Claude Sonnet 3.5 model via OpenRouter. Make sure you have a valid API key and sufficient credits to use the service.
