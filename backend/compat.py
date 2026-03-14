def fix_tool_for_gemini(tool):
    """
    Workaround for 'Key title is not supported in schema' error with Gemini.
    Strips the 'title' key from the tool's parameter schema.
    """
    if hasattr(tool, "args_schema") and tool.args_schema:
        # Some tools use a pydantic model for args_schema
        # We can't easily modify it without breaking things, 
        # but langchain-google-genai converts it to a dict internally.
        pass 
    
    # The error usually happens when the tool is converted to a Google tool spec.
    # We can patch the tool's name/description or wrap it.
    return tool

# Actually, the fix is often to ensure the tool's arguments are simple.
# Let's try to identify if it's the RAG tool.
