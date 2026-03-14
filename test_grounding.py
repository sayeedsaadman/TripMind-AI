import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

try:
    # Native Google Search Grounding is enabled by passing a specific tool object
    # In langchain-google-genai, we can try passing the string directly
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    grounded_llm = llm.bind_tools(["google_search_retrieval"])
    
    res = grounded_llm.invoke("What is the latest score of Real Madrid today?")
    print("SUCCESS Grounding:", res.content)
except Exception as e:
    print("ERROR:", str(e))
