import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-preview-02-05",
]

print("Systematic Model Testing:")
for model_name in models_to_test:
    print(f"Testing {model_name}...", end=" ", flush=True)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'OK'")
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            print("FAILED: Quota Exceeded (429)")
        elif "404" in error_msg:
            print("FAILED: Model Not Found (404)")
        else:
            print(f"FAILED: {error_msg[:100]}...")

print("\nTesting with SECONDARY_GOOGLE_API_KEY if available:")
sec_key = os.getenv("SECONDARY_GOOGLE_API_KEY")
if sec_key and sec_key != "your_secondary_api_key_here":
    genai.configure(api_key=sec_key)
    for model_name in models_to_test:
        print(f"Testing {model_name}...", end=" ", flush=True)
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'OK'")
            print(f"SUCCESS: {response.text.strip()}")
        except Exception as e:
            print(f"FAILED: {str(e)[:50]}")
else:
    print("No secondary key found or it's the placeholder.")
