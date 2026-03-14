import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

def debug_llm():
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="Hi")
    ]
    try:
        response = llm.invoke(messages)
        print("LLM Response Success!")
        print(response.content)
    except Exception as e:
        print(f"LLM Error: {e}")

if __name__ == "__main__":
    debug_llm()
