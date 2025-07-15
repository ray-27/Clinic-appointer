from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

def load_llm():
    load_dotenv()

    service = os.getenv("LLM_SERVICE")
    model = os.getenv("LLM_MODEL")

    if service == "ollama":
        return ChatOllama(model=model)
    elif service == "openai":
        print("openai service is not made yet")
        return None
    elif service == "gemini":
        return ChatGoogleGenerativeAI(
            model=model,  # Use "gemini-2.0-flash"
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    else:
        print("no service is showing up...... chat llm_config and .env")


