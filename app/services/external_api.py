import requests
from dotenv import load_dotenv
import os

load_dotenv()  

API_KEY = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
headers = {"x-api-key": API_KEY}

SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def fetch_similar_papers(title: str, limit: int = 5):
    params = {
        "query": title,
        "limit": limit,
        "fields": "title,abstract,year,authors,url"
    }
    response = requests.get(SEMANTIC_SCHOLAR_URL, params=params, headers = headers)
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch papers: {response.text}"}
    
    data = response.json()
    papers = []
    for paper in data.get("data", []):
        papers.append({
            "title": paper.get("title"),
            "abstract": paper.get("abstract"),
            "year": paper.get("year"),
            "authors": [a.get("name") for a in paper.get("authors", [])],
            "url": paper.get("url")
        })
    
    return papers
