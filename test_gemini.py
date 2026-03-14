import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("API Key not found!")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("AVAILABLE MODELS FOR YOUR KEY:")
        for m in models:
            # We want models that support generateContent
            methods = m.get('supportedGenerationMethods', [])
            if 'generateContent' in methods:
                print(f" - {m['name']}")
    else:
        print(f"ERROR Fetching models: {response.text}")
