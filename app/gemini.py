import os
from google import genai
from drive_loader import load_drive_docs 
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
SERVICE_ACCOUNT_PATH = os.getenv("GDRIVE_JSON_PATH", "service_account.json")

KNOWLEDGE_TEXT = load_drive_docs(
    os.getenv("KNOWLEDGE_BASE_FOLDER_ID"), 
    SERVICE_ACCOUNT_PATH
)

def ask_gemini_fast(question):

    prompt = f"""
        You are an HR assistant.
        Use the knowledge base given below to answer the 
        query in a clear and consice way for the employee to understand.
        If answer is not found, say "NOT_FOUND"
        Make sure its nice and formal.

    CONTEXT:
    {KNOWLEDGE_TEXT}

    USER QUESTION: {question}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        cached_count = response.usage_metadata.cached_content_token_count or 0

        if cached_count > 0:
            print(f"⚡ Cache Hit! Reused {cached_count} tokens.")
        
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"