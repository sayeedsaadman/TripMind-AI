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
    # Since Gemini is currently out of quota for the user, we promote Groq to primary!
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and groq_key != "your_groq_api_key_here":
        from langchain_groq import ChatGroq
        primary_llm = ChatGroq(
            model="llama-3.3-70b-versatile", 
            api_key=groq_key,
            temperature=0.3
        )
        print("--- DEBUG: Using Groq as Primary Model ---")
    else:
        primary_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite", 
            temperature=0.3,
            max_retries=0, 
        )
        print("--- DEBUG: Using Gemini as Primary Model ---")
    
    # 1.1 Setup Fallback Models (Optional)
    # We add fallbacks in order of preference.
    fallbacks = []
    
    # Option A: Secondary Gemini Key
    second_gemini_key = os.getenv("SECONDARY_GOOGLE_API_KEY")
    if second_gemini_key and second_gemini_key != "your_secondary_api_key_here":
        fallbacks.append(ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite", 
            google_api_key=second_gemini_key,
            temperature=0.3,
            max_retries=0, 
        ))
        
    # Option B: Gemini (Moved to fallback since quota is tight)
    if os.getenv("GOOGLE_API_KEY"):
        fallbacks.append(ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite", 
            temperature=0.3,
            max_retries=0,
        ))

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
    def bind_appropriately(model):
        if hasattr(model, "google_api_key") or "ChatGoogleGenerativeAI" in str(type(model)):
            return model.bind_tools(gemini_tools)
        else:
            # Groq, OpenAI etc.
            return model.bind_tools(active_tools)

    primary_llm_with_tools = bind_appropriately(primary_llm)
    
    if fallbacks:
        processed_fallbacks = [bind_appropriately(f) for f in fallbacks]
        llm_with_tools = primary_llm_with_tools.with_fallbacks(processed_fallbacks)
    else:
        llm_with_tools = primary_llm_with_tools
    
    # 3. Define the Workflow using LangGraph!
    
    def agent_node(state: MessagesState):
        """The AI makes a decision: answer or use a tool."""
        print("--- DEBUG: Invoking LLM Chain ---")
        
        # Determine if the CURRENT model being invoked supports vision.
        # This is tricky with fallbacks, so we sanitize for the MOST RESTRICTIVE model 
        # unless we are sure it's a vision model.
        
        # Helper to sanitize messages for non-vision models
        def sanitize_messages(msgs):
            sanitized = []
            for m in msgs:
                if isinstance(m.content, list):
                    # Extract only text parts
                    text_content = ""
                    for part in m.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_content += part.get("text", "")
                        elif isinstance(part, str):
                            text_content += part
                    # Create a new message of the same type but with string content
                    sanitized.append(type(m)(content=text_content))
                else:
                    sanitized.append(m)
            return sanitized

        try:
            # We check the primary model first. If it's NOT Gemini, we sanitize.
            # (In your current setup, Groq is primary if keys exist, and it doesn't support the vision format used here).
            current_messages = state["messages"]
            
            # Simple heuristic: if we are using Groq (llama), we MUST sanitize.
            if "ChatGroq" in str(type(primary_llm)):
                 print("--- DEBUG: Sanitizing messages for non-vision primary (Groq) ---")
                 current_messages = sanitize_messages(current_messages)

            response = llm_with_tools.invoke(current_messages)
            
            # Extract which model actually answered
            actual_model = response.response_metadata.get('model_name', 'Unknown Model')
            print(f"--- DEBUG: LLM Success with model: {actual_model} ---")
            
            return {"messages": [response]}
        except Exception as e:
            error_str = str(e).lower()
            print(f"--- DEBUG: LLM Chain Error: {str(e)} ---")
            
            # Distinguish between Quota and other errors
            if "quota" in error_str or "429" in error_str or "rate limit" in error_str:
                msg_content = f"I'm sorry, all my AI brains (Gemini/Groq) are currently exhausted (Quota Limit). Please try again in a few minutes or check your API billing.\n\nDetails: {str(e)}"
            elif "400" in error_str:
                msg_content = f"I encountered a formatting error (400). This usually happens when I try to send an image to a model that only understands text. I'll try to recover by ignoring the image.\n\nDetails: {str(e)}"
            else:
                msg_content = f"Oops! I hit a snag: {str(e)}"
                
            error_msg = AIMessage(content=msg_content)
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
