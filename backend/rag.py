import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool

DATA_DIR = "data"
FAISS_INDEX_PATH = "backend/faiss_index"

def get_huggingface_embeddings():
    """Returns free HuggingFace embeddings."""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def ingest_documents():
    """
    Reads all text and PDF files from the data/ folder, splits them into chunks, 
    embeds them using HuggingFace, and saves the FAISS index locally.
    """
    print("Loading documents from data/ ...")
    
    # Check if data directory exists and has files
    if not os.path.exists(DATA_DIR) or len(os.listdir(DATA_DIR)) == 0:
        print(f"No documents found in '{DATA_DIR}'. Please add some .txt or .pdf files!")
        return False
        
    documents = []
    
    # Load Text Files
    txt_loader = DirectoryLoader(DATA_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    
    # Load PDF Files
    try:
        pdf_loader = DirectoryLoader(DATA_DIR, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents.extend(pdf_loader.load())
    except Exception as e:
        print(f"Skipping PDFs (pypdf might not be installed): {e}")

    if not documents:
        print("No readable text/pdf documents found.")
        return False

    print(f"Loaded {len(documents)} document pages. Chunking...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    
    print(f"Split into {len(docs)} chunks. Generating embeddings and building FAISS index...")
    embeddings = get_huggingface_embeddings()
    
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    
    print(f"SUCCESS! Web database saved to {FAISS_INDEX_PATH}")
    return True

def get_rag_tool():
    """
    Loads the local FAISS index and returns a LangChain tool that the agent can use 
    to search through the provided travel guides.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        print("FAISS index not found. Run ingest_documents() first.")
        # Return a dummy tool if DB isn't built yet
        return None
        
    embeddings = get_huggingface_embeddings()
    vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    rag_tool = create_retriever_tool(
        retriever,
        "travel_guide_search",
        "Searches and returns excerpts from the user's personal travel guides and documents. Use this when asked about specific local recommendations from the guides."
    )
    return rag_tool

# If you run this file directly, it will build the database
if __name__ == "__main__":
    ingest_documents()
