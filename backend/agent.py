import os
from typing import TypedDict, Annotated, List, Union
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage, BaseMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from backend.tools import (
    get_internet_search_tool, 
    get_google_search_grounding_tool,
    get_ocr_tool,
    get_vision_tool
)
from backend.rag import get_rag_tool

def get_chatbot_response(chat_history):
    """
    Sends the chat history to the Google Gemini model and allows it to use tools.
    Uses LangGraph for structured workflow tracing.
    """
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_google_api_key_here":
        return "I cannot respond yet! Please add your Google Gemini API key to the .env file."
        
    # 1. Initialize the Primary AI Model
    primary_llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        temperature=0.3,
        max_retries=1, # Don't wait! If it fails, go to fallback immediately.
    )
    
    # 1.1 Setup Fallback Models (Optional)
    # We add fallbacks in order of preference.
    fallbacks = []
    
    # Option A: Secondary Gemini Key
    second_gemini_key = os.getenv("SECONDARY_GOOGLE_API_KEY")
    if second_gemini_key and second_gemini_key != "your_secondary_api_key_here":
        fallbacks.append(ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=second_gemini_key,
            temperature=0.3,
            max_retries=1, # Quick failure for secondary Gemini too
        ))
        
    # Option B: Groq (Llama 3.1 70B is a great free/cheap alternative)
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from langchain_groq import ChatGroq
            fallbacks.append(ChatGroq(
                model="llama-3.1-70b-versatile", 
                api_key=groq_key,
                temperature=0.3
            ))
        except ImportError:
            print("Warning: langchain-groq not installed. Skipping Groq fallback.")

    # Option C: OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            fallbacks.append(ChatOpenAI(
                model="gpt-4o-mini", 
                api_key=openai_key,
                temperature=0.3
            ))
        except ImportError:
            print("Warning: langchain-openai not installed. Skipping OpenAI fallback.")

    # 1.2 Debug: Check what fallbacks are loaded
    print(f"--- DEBUG: LLM Configuration ---")
    print(f"Primary Gemini Key: {'Found' if os.getenv('GOOGLE_API_KEY') else 'NOT FOUND'}")
    print(f"Secondary Gemini: {'Found' if second_gemini_key else 'NOT FOUND'}")
    print(f"Groq: {'Found' if groq_key else 'NOT FOUND'}")
    print(f"OpenAI: {'Found' if openai_key else 'NOT FOUND'}")
    print(f"Total fallbacks configured: {len(fallbacks)}")
    print(f"---------------------------------")
    
    # 2. Setup the Tools!
    tools_list = {
        "tavily_search_results_json": get_internet_search_tool(),
        "google_search_grounding": get_google_search_grounding_tool(),
        "travel_guide_search": get_rag_tool(),
        "ocr_tool": get_ocr_tool(),
        "landmark_recognition_tool": get_vision_tool()
    }
    
    # Filter out None tools (like if RAG isn't built yet)
    active_tools = [t for t in tools_list.values() if t is not None]

    # 3. Define the Workflow using LangGraph!
    # HACK: Fix for Gemini "Key 'title' is not supported in schema" error.
    # We use a helper to format tools without 'title' in the schema.
    def format_tool_for_gemini(tool):
        # This is a bit advanced: we use the tool's own conversion but strip 'title'
        from langchain_core.utils.function_calling import convert_to_openai_tool
        tool_json = convert_to_openai_tool(tool)
        
        def strip_title(obj):
            if isinstance(obj, dict):
                return {k: strip_title(v) for k, v in obj.items() if k != 'title'}
            elif isinstance(obj, list):
                return [strip_title(i) for i in obj]
            return obj
        
        return strip_title(tool_json["function"])

    gemini_tools = [format_tool_for_gemini(t) for t in active_tools]
    
    # 2.2 Bind tools to each model individually for reliability
    # This ensures that with_fallbacks works correctly with tool calling
    primary_llm_with_tools = primary_llm.bind_tools(gemini_tools)
    
    if fallbacks:
        fallbacks_with_tools = [f.bind_tools(gemini_tools) for f in fallbacks]
        llm_with_tools = primary_llm_with_tools.with_fallbacks(fallbacks_with_tools)
    else:
        llm_with_tools = primary_llm_with_tools
    
    # 3. Define the Workflow using LangGraph!
    
    def agent_node(state: MessagesState):
        """The AI makes a decision: answer or use a tool."""
        print("--- DEBUG: Invoking LLM Chain ---")
        try:
            response = llm_with_tools.invoke(state["messages"])
            print(f"--- DEBUG: LLM Success with model: {response.response_metadata.get('model_name', 'unknown')} ---")
            return {"messages": [response]}
        except Exception as e:
            print(f"--- DEBUG: LLM Chain Error: {str(e)} ---")
            # If everything fails, return a friendly error message instead of crashing
            error_msg = AIMessage(content=f"I'm sorry, all my AI brains are currently exhausted (Quota Limit). Please try again in a few minutes.\n\nDetails: {str(e)}")
            return {"messages": [error_msg]}

    def should_continue(state: MessagesState):
        """Decision branch: if tool calls exist, go to 'tools', else 'END'."""
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Build the graph
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(active_tools))
    
    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    
    # Compile the graph
    app = workflow.compile()
    
    # 4. Prepare the initial state
    system_prompt = """You are TripMind AI, an expert travel planner. 
    Your goal is to help the user plan trips, including suggesting destinations, itineraries, and providing practical travel advice.
    
    KNOWLEDGE BASE (Knowledge Base):
    - You have access to a 'Knowledge Base' containing PDF and TXT documents.
    - You MUST use the 'travel_guide_search' tool to search these documents FIRST whenever the user asks about their submitted PDF or uploaded travel files.
    
    TOOLS AT YOUR DISPOSAL:
    1. travel_guide_search: Use this to search the Knowledge Base (the user's submitted PDF or TXT files).
    2. tavily_search_results_json: Use this for general internet search.
    3. google_search_grounding: Use this for deeper, grounded search.
    4. ocr_tool: Use this when the user uploads an image of a document directly in chat.
    5. landmark_recognition_tool: Use this when the user uploads a photo of a place.
    
    You have VISION CAPABILITIES. If the user mentions an image, you can see it in chat history.
    When generating an itinerary, make sure it is structural, day-by-day, and conversational."""

    messages = [SystemMessage(content=system_prompt)]
    
    for msg in chat_history:
        if msg["role"] == "user":
            if "image" in msg:
                content = [
                    {"type": "text", "text": msg["content"]},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{msg['image_type']};base64,{msg['image']}"},
                    },
                ]
                messages.append(HumanMessage(content=content))
            else:
                messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    # 5. Run the Workflow!
    try:
        final_state = app.invoke({"messages": messages})
        return final_state["messages"][-1].content
    except Exception as e:
        return f"Oops! I encountered an error during the workflow: {str(e)}"
