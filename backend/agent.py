import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
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
    """
    if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_google_api_key_here":
        return "I cannot respond yet! Please add your Google Gemini API key to the .env file."
        
    # 1. Initialize the AI Model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.7 
    )
    
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
    
    # "Bind" the tools to the LLM so it knows they exist
    llm_with_tools = llm.bind_tools(active_tools)
    
    # 3. Prepare the memory/history messages
    messages = [
        SystemMessage(content="""You are TripMind AI, an expert travel planner. 
        Your goal is to help the user plan trips, including suggesting destinations, itineraries, and providing practical travel advice.
        
        TOOLS AT YOUR DISPOSAL:
        1. tavily_search_results_json: Use this for general internet search (e.g., top attractions, weather, restrictions).
        2. google_search_grounding: Use this specifically when you need deeper, grounded recent events, or if the user explicitly asks you to 'Google' something.
        3. travel_guide_search: If available, use this FIRST when the user asks about specific recommendations, secret spots, or hotel ideas from the provided travel guides.
        4. ocr_tool: Use this when the user uploads a document image (ticket, receipt, itinerary) and asks to extract information.
        5. landmark_recognition_tool: Use this when the user uploads a photo of a place or landmark and asks you to identify it.
        
        You have VISION CAPABILITIES. When a user uploads an image, you can see it. Use the appropriate tool to 'analyze' it for the user.
        When generating an itinerary, make sure it is structural, day-by-day, and conversational.""")
    ]
    
    for msg in chat_history:
        if msg["role"] == "user":
            # Check if there's an image attached to this message
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
            
    # 4. Agent Loop: Let the AI think and use tools if it wants to!
    try:
        # Step A: The LLM reads everything and decides if it needs a tool or can answer directly
        # Note: Handling vision natively during the first invoke
        response = llm_with_tools.invoke(messages)
        
        # Step B: If the LLM wants to use tools, we run them in a loop
        if response.tool_calls:
            # We add a specialized "Vision/OCR" logic if the user specifically asked for it via tools
            # (Though gemini sees it naturally, we can reinforce it)
            messages.append(response) 
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                
                # Check for standard tools
                if tool_name in tools_list and tools_list[tool_name] is not None:
                    tool_output = tools_list[tool_name].invoke(tool_call["args"])
                    
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"]))
            
            # Step C: The AI reads the findings and gives the FINAL answer
            final_response = llm.invoke(messages)
            return final_response.content
        else:
            return response.content
            
    except Exception as e:
        return f"Oops! I encountered an error: {str(e)}"
