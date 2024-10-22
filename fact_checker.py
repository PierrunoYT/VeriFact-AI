import requests
import os
import base64
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer, util
import torch
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# OpenRouter API settings
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Google Custom Search API settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def query_claude(prompt, image_path=None, language='english'):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    if language == 'german':
        prompt = f"Please respond in German. {prompt}"
    
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
        "messages": messages,
        "stream": True
    }
    
    response = requests.post(API_URL, json=data, headers=headers, stream=True)
    
    if response.status_code == 200:
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        json_data = json.loads(line[6:])
                        if 'choices' in json_data and json_data['choices']:
                            content = json_data['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        yield line[6:]  # Fallback: return the raw data without the 'data: ' prefix
    else:
        yield f"Error: {response.status_code} - {response.text}"

def search_google(query, num_results=10):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    results = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=num_results).execute()
    return results.get('items', [])

def fetch_webpage_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return ' '.join(p.get_text() for p in soup.find_all('p'))
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return ""

def semantic_search(query, search_results, top_k=5):
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    corpus = []
    for result in search_results:
        snippet = result.get('snippet', '')
        content = fetch_webpage_content(result.get('link', ''))
        corpus.append(f"{snippet} {content}")
    
    corpus_embeddings = model.encode(corpus, convert_to_tensor=True)
    
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
    top_results = torch.topk(cos_scores, k=min(top_k, len(corpus)))
    
    return [
        {
            'score': score.item(),
            'content': corpus[idx],
            'title': search_results[idx].get('title', ''),
            'link': search_results[idx].get('link', '')
        }
        for score, idx in zip(top_results.values, top_results.indices)
    ]

def fact_check(statement, language='english', method='combined'):
    if method == 'ai':
        return ai_fact_check(statement, language)
    elif method == 'search':
        return search_engine_fact_check(statement, language)
    else:  # combined
        return combined_fact_check(statement, language)

def ai_fact_check(statement, language='english'):
    prompt = f"""
    Please fact-check the following statement and provide a detailed analysis, including an assessment of whether it might be fake news:
    
    Statement: "{statement}"
    
    1. Is this statement true, false, or partially true?
    2. What are the facts that support or refute this statement?
    3. Are there any nuances or context that should be considered?
    4. Assess the likelihood that this statement is fake news. Consider factors such as:
       - Emotional language or sensationalism
       - Lack of verifiable sources
       - Inconsistencies with well-established facts
       - Potential motivations for spreading misinformation
    5. Provide at least 5 reliable sources for the information you've used in your analysis. For each source, provide the name of the source, its URL (if available), and a brief description of its relevance. If fewer than 5 sources are available, explain in detail why this is the case and discuss the implications for the reliability of your analysis.
    6. If you suspect this might be fake news, suggest ways for readers to verify the information independently.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, language=language)

def search_engine_fact_check(statement, language='english'):
    search_results = search_google(statement)
    semantic_results = semantic_search(statement, search_results)
    
    prompt = f"""
    Please fact-check the following statement using the provided semantically ranked search results, and assess whether it might be fake news:
    
    Statement: "{statement}"
    
    Semantically Ranked Search Results:
    {json.dumps(semantic_results, indent=2)}
    
    1. Is this statement true, false, or partially true based on the search results?
    2. What facts from the search results support or refute this statement?
    3. Are there any nuances or context from the search results that should be considered?
    4. Provide a summary of the most relevant information from the search results.
    5. Explain how the semantic ranking of the results affects your analysis.
    6. Assess the likelihood that this statement is fake news based on the search results. Consider factors such as:
       - Consistency of information across multiple sources
       - Credibility of the sources
       - Presence of fact-checking articles or debunking information
       - Potential motivations for spreading misinformation
    7. If you suspect this might be fake news, suggest ways for readers to verify the information independently using the search results.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, language=language)

def combined_fact_check(statement, language='english'):
    search_results = search_google(statement)
    semantic_results = semantic_search(statement, search_results)
    
    prompt = f"""
    Please fact-check the following statement using your knowledge and the provided semantically ranked search results, and assess whether it might be fake news:
    
    Statement: "{statement}"
    
    Semantically Ranked Search Results:
    {json.dumps(semantic_results, indent=2)}
    
    1. Is this statement true, false, or partially true?
    2. What facts from your knowledge and the search results support or refute this statement?
    3. Are there any nuances or context that should be considered?
    4. Provide a comprehensive analysis combining your knowledge and the search results.
    5. List at least 5 reliable sources for the information, including those from the search results. For each source, provide the name of the source, its URL (if available), and a brief description of its relevance. If fewer than 5 sources are available, explain in detail why this is the case and discuss the implications for the reliability of the fact-check.
    6. Explain how the semantic ranking of the results affects your analysis and the reliability of the sources.
    7. Assess the likelihood that this statement is fake news. Consider factors such as:
       - Emotional language or sensationalism
       - Lack of verifiable sources
       - Inconsistencies with well-established facts
       - Potential motivations for spreading misinformation
       - Consistency of information across multiple sources
       - Presence of fact-checking articles or debunking information
    8. If you suspect this might be fake news, suggest ways for readers to verify the information independently.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, language=language)

def analyze_image_and_fact(statement, image_path, language='english', method='combined'):
    if method == 'ai':
        return ai_analyze_image_and_fact(statement, image_path, language)
    elif method == 'search':
        return search_engine_analyze_image_and_fact(statement, image_path, language)
    else:  # combined
        return combined_analyze_image_and_fact(statement, image_path, language)

def ai_analyze_image_and_fact(statement, image_path, language='english'):
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
    
    return query_claude(prompt, image_path, language=language)

def search_engine_analyze_image_and_fact(statement, image_path, language='english'):
    search_results = search_google(statement)
    
    prompt = f"""
    Please analyze the provided image and fact-check the following statement using the search results:
    
    Statement: "{statement}"
    
    Search Results:
    {json.dumps(search_results, indent=2)}
    
    1. Describe the contents of the image.
    2. Is the statement true, false, or partially true based on the image and search results?
    3. What elements in the image and search results support or refute the statement?
    4. Are there any nuances or context in the image or search results that should be considered?
    5. Provide a summary of the most relevant information from the image and search results.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, image_path, language=language)

def combined_analyze_image_and_fact(statement, image_path, language='english'):
    search_results = search_google(statement)
    
    prompt = f"""
    Please analyze the provided image and fact-check the following statement using your knowledge and the search results:
    
    Statement: "{statement}"
    
    Search Results:
    {json.dumps(search_results, indent=2)}
    
    1. Describe the contents of the image.
    2. Is the statement true, false, or partially true based on the image, your knowledge, and search results?
    3. What elements in the image, your knowledge, and search results support or refute the statement?
    4. Are there any nuances or context that should be considered?
    5. Provide a comprehensive analysis combining the image analysis, your knowledge, and the search results.
    6. If applicable, provide any additional information or context about the topic shown in the image.
    7. List reliable sources for the information, including those from the search results.
    
    Please structure your response clearly and concisely.
    """
    
    return query_claude(prompt, image_path, language=language)
