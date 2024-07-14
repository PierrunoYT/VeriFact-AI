import requests
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API settings
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

def query_claude(prompt, image_path=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "user", "content": prompt}]
    
    if image_path:
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        messages[0]["content"] = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"}
        ]
    
    data = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": messages
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

def analyze_image_and_fact(statement, image_path):
    prompt = f"""
    Please analyze the provided image and fact-check the following statement:
    
    Statement: "{statement}"
    
    1. Describe the contents of the image.
    2. Is the statement true, false, or partially true based on the image?
    3. What elements in the image support or refute the statement?
    4. Are there any nuances or context in the image that should be considered?
    5. If applicable, provide any additional information or context about the topic shown in the image.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, image_path)

# Remove the main() function as it's no longer needed for the web interface
