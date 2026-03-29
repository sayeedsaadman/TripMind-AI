import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

def test_fallback():
    # Tools (simplified version of gemini_tools from agent.py)
    tools = [{
        "name": "travel_guide_search",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        "description": "Searches travel guides"
    }]

    primary = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", max_retries=0)
    # Use Groq as the fallback model
    fallback = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), max_retries=0)
    
    # Simulate the logic in agent.py
    primary_with_tools = primary.bind_tools(tools)
    fallback_with_tools = fallback.bind_tools(tools)
    
    chain = primary_with_tools.with_fallbacks([fallback_with_tools])
    
    print("Invoking chain...")
    try:
        res = chain.invoke([HumanMessage(content="Hello")])
        print(f"Success! Model used: {res.response_metadata.get('model_name', 'unknown')}")
        print(f"Content: {res.content}")
    except Exception as e:
        print(f"Chain failed with error: {str(e)}")

if __name__ == "__main__":
    test_fallback()
