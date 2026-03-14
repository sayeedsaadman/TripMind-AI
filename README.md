# TripMind AI

Welcome to the TripMind AI project! This is an AI-powered travel planning chatbot.

## Folder Structure
- `frontend/`: Contains the Streamlit web application.
- `backend/`: Contains the AI Logic, LangChain Agents, tools, and the Vector Database.
- `data/`: Place your PDF travel guides here later!
- `.env`: This file holds your secret API Keys.

## Step 1: Getting Required API Keys (It's Free!)

1. **Google Gemini Key (For the AI Brain)**
   - Go to: https://aistudio.google.com/app/apikey
   - Sign in with your Google Account, click **"Create API Key"**, and copy it.
   - Paste it inside the `.env` file where it says `your_google_api_key_here`.

2. **LangSmith Key (For Tracing / Grading points)**
   - Go to: https://smith.langchain.com/
   - Sign up/Log in, go to Settings (gear icon) -> **API Keys**, create a new Personal Access Token and copy it.
   - Paste it inside the `.env` file where it says `your_langsmith_api_key_here`.

## Step 2: Installation

Open your terminal or command prompt inside `d:\CSE BASED\TripMind-AI` and run:

```bash
# Install everything needed for the backend (Langchain, AI tools, Vector DB)
pip install -r backend/requirements.txt

# Install everything needed for the frontend (Streamlit)
pip install -r frontend/requirements.txt
```

## Step 3: Running the Application

After installing, run this command in your terminal:

```bash
python -m streamlit run frontend/app.py
```
This will automatically open your web browser and show the chatbot interface!
