# AI Fact Checker

This project is an AI-powered fact-checking web application that can analyze statements and images using Claude Sonnet 3.5 via OpenRouter, combined with web search results.

## Features

- Fact-check statements using AI, web search, or a combination of both
- Detect potential fake news and provide guidance on verification
- Analyze images in conjunction with statements
- Support for multiple languages (currently English and German)
- User preferences for language and fact-checking method
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

5. Create a `.env` file in the project root directory and add your API keys:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   GOOGLE_CSE_ID=your_google_cse_id_here
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
3. Select the desired language and fact-checking method.
4. Click the "Check Facts" button to submit your request.
5. The application will analyze the statement (and image, if provided) and display the results.

## Fact-Checking Methods

- AI Only: Uses Claude Sonnet 3.5 to analyze the statement based on its knowledge.
- Web Search Only: Uses Google Custom Search to find relevant information and analyzes it.
- AI + Web Search: Combines AI analysis with web search results for a comprehensive fact-check.

## User Preferences

You can set your preferred language and fact-checking method, which will be saved for the current session.

## Note

This application uses the Claude Sonnet 3.5 model via OpenRouter and Google Custom Search API. Make sure you have valid API keys and sufficient credits to use these services.
