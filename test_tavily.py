import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

try:
    search = TavilySearchResults(max_results=3)
    response = search.invoke("What is the capital of France?")
    print("SUCCESS! Tavily Search works. Capital:", response)
except Exception as e:
    print("ERROR:", str(e))
