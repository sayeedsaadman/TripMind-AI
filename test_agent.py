import os
import sys
from dotenv import load_dotenv

# Add parent directory to paths
sys.path.append(os.getcwd())

from backend.agent import get_chatbot_response

def test_agent():
    load_dotenv()
    print("Testing LangGraph Agent with different tool sets...")
    
    chat_history = [{"role": "user", "content": "Hi"}]
    
    try:
        response = get_chatbot_response(chat_history)
        print("\nAgent Response:")
        print(response)
    except Exception as e:
        print(f"\nError with full toolset: {e}")

if __name__ == "__main__":
    test_agent()
