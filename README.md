# TripMind AI ✈️

TripMind AI is a state-of-the-art, AI-powered travel assistant designed to modernize how you plan your journeys. By leveraging the power of Google Gemini and advanced RAG (Retrieval-Augmented Generation), it transforms static travel documents and vast internet data into personalized, interactive travel experiences.

## 🌟 Project Overview

TripMind AI is not just a chatbot; it's a comprehensive travel companion. It seamlessly integrates real-time web search, document intelligence, and computer vision to provide a premium planning experience. Whether you're looking for hidden gems in a new city, need to identify a landmark from a photo, or want to index your personal collection of travel guides, TripMind AI is equipped to handle it all.

## 🚀 Key Features

- **🧠 Intelligent Itinerary Generation**: Day-by-day structural planning with a conversational touch.
- **📚 Knowledge Base (RAG)**: Upload PDF/TXT travel guides to create a private, searchable knowledge base for high-precision recommendations.
- **🌐 Real-time Web Intelligence**: Integrated with Tavily and Google Search Grounding for current events, ticket prices, and local restrictions.
- **👁️ Vision & Landmark Recognition**: Upload photos of landmarks to get instant identification and historical context.
- **📄 Document Intelligence (OCR)**: Extract details from flight tickets, hotel receipts, or physical itineraries via image uploads.
- **✨ Premium UI**: A modern, glassmorphism-inspired interface with Dark/Light mode support, smooth animations, and a responsive layout.

## 📂 Folder Structure
- `frontend/`: Modern Streamlit web application with custom CSS.
- `backend/`: AI logic, LangChain agents, specialized tools, and the Vector Database (FAISS).
- `data/`: Storage for your uploaded PDFs and knowledge base documents.

## 🔑 Step 1: Getting Required API Keys

1. **Google Gemini Key (Brain)**
   - Get it at: [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Add to `.env` as `GOOGLE_API_KEY`.

2. **LangSmith Key (Optional - Tracing)**
   - Get it at: [LangSmith](https://smith.langchain.com/)
   - Add to `.env` as `LANGCHAIN_API_KEY`.

3. **Tavily Key (Web Search)**
   - Get it at: [Tavily AI](https://tavily.com/)
   - Add to `.env` as `TAVILY_API_KEY`.

## 🛠️ Step 2: Installation

Run these commands in your terminal:

```bash
# Install backend dependencies (LangChain, FAISS, etc.)
pip install -r backend/requirements.txt

# Install frontend dependencies (Streamlit)
pip install -r frontend/requirements.txt
```

## 🚀 Step 3: Running the Application

```bash
python -m streamlit run frontend/app.py
```
This will launch the TripMind AI interface in your default browser!
