import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API settings
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def query_claude(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "anthropic/claude-3-sonnet-20240229",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(API_URL, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

def fact_check(statement):
    prompt = f"""
    Please fact-check the following statement and provide a detailed analysis:
    
    Statement: "{statement}"
    
    1. Is this statement true, false, or partially true?
    2. What are the facts that support or refute this statement?
    3. Are there any nuances or context that should be considered?
    4. Provide reliable sources for the information you've used in your analysis.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt)

def main():
    print("Welcome to the Fact Checker powered by Claude Sonnet 3.5!")
    print("Enter a statement to fact-check, or type 'quit' to exit.")
    
    while True:
        statement = input("\nEnter a statement: ").strip()
        
        if statement.lower() == 'quit':
            print("Thank you for using the Fact Checker. Goodbye!")
            break
        
        if statement:
            print("\nAnalyzing... Please wait.\n")
            result = fact_check(statement)
            print(result)
        else:
            print("Please enter a valid statement.")

if __name__ == "__main__":
    main()
