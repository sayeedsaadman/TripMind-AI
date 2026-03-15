# ✈️ TripMind AI: The Ultimate Agentic Travel Companion

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/Powered%20by-LangChain-brightgreen.svg)](https://langchain.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**TripMind AI** is a state-of-the-art, AI-powered travel ecosystem designed to revolutionize journey planning. By merging the reasoning power of **Google Gemini (2.0 Flash)** with a robust **LangGraph-driven agentic workflow** and **Advanced RAG (Retrieval-Augmented Generation)**, TripMind AI transforms static travel data into dynamic, interactive experiences.

---

## 🌟 Premium Features

### 🧠 Agentic Intelligence
*   **Dynamic Itinerary Generation**: Structural, day-by-day travel planning with a conversational touch, grounded in real-time data.
*   **Multi-Model Resilience**: Intelligent fallback logic that shifts between Google Gemini, Groq (Llama 3.3), and OpenAI to ensure service continuity.

### 📚 Document Intelligence (RAG)
*   **Knowledge Base Integration**: Upload PDF or TXT guides to create a private, searchable database.
*   **High-Precision Retrieval**: Uses HuggingFace embeddings and FAISS vector storage for zero-hallucination recommendations.

### 🌐 Real-time Web Grounding
*   **Live Web Intelligence**: Integrated with Tavily for current ticket prices, local events, and travel restrictions.
*   **Google Search Grounding**: Advanced verification of facts to provide the most reliable travel advice.

### 👁️ Computer Vision & OCR
*   **Landmark Recognition**: Identify famous places and buildings from uploaded photos instantly.
*   **Document Parsing (OCR)**: Extract critical info from flight tickets, hotel receipts, or physical brochures with a single image upload.

### ✨ State-of-the-Art UI
*   **Glassmorphism Design**: A premium, modern interface with fluid animations, custom SVG icons, and a Plus Jakarta Sans typography.
*   **Theme Versatility**: Seamless transition between sophisticated Light and Dark modes.

---

## 🛠️ Technical Architecture

TripMind AI is built on a decoupled, modular architecture:

-   **Frontend**: Streamlit-based SPA (Single Page Application) with a custom CSS-in-Python theme engine.
-   **Agent Layer**: LangGraph State Machine managing stateful conversation and tool orchestration.
-   **Toolkit**: A collection of specialized tools for Search, Vision, OCR, and Retrieval.
-   **Memory Layer**: FAISS vector database for persistent knowledge retrieval.

---

## 📂 Project Structure

```text
TripMind-AI/
├── frontend/             # Premium Streamlit UI & Custom CSS
│   └── app.py            # Main Application Entry Point
├── backend/              # Core Logic & AI Agents
│   ├── agent.py          # LangGraph Agent Implementation
│   ├── rag.py            # RAG Ingestion & Search Logic
│   └── tools.py          # Specialized Agentic Tools
├── data/                 # Knowledge Base Document Storage
├── .env.example          # Template for Configuration
└── requirements.txt      # Global Dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or higher.
- A Google Gemini API Key (Required).
- A Tavily API Key (Required for web search).
- A LangSmith API Key (Optional for tracing).

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Clone the repo
git clone https://github.com/yourusername/TripMind-AI.git
cd TripMind-AI

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory (refer to `.env.example`):

```env
GOOGLE_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_key_here  # Optional
```

### 4. Running the Application

Launch the TripMind AI ecosystem:

```bash
python -m streamlit run frontend/app.py
```

---

## 📊 Monitoring & Tracing

TripMind AI is fully instrumented with **LangSmith**. Every agent decision, tool call, and RAG retrieval is traced, providing deep visibility into the "Chain of Thought" and performance metrics.

---

## 🤝 Contributing

We welcome contributions! If you have ideas for new agents (e.g., Budget Agent, Booking Specialist), feel free to fork the repo and submit a PR.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Plan Smarter. Explore Further. Discover Much More with TripMind AI.** 🌍✈️
