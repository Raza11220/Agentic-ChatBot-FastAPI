# if you dont use pipenv uncomment the following:
from dotenv import load_dotenv
load_dotenv()  # API Keys load karne ke liye isko active rakhein

# Step1: Setup Pydantic Model (Schema Validation)
from pydantic import BaseModel
from typing import List

class RequestState(BaseModel):
    model_name: str
    model_provider: str
    system_prompt: str
    messages: List[str]
    allow_search: bool

# Step2: Setup AI Agent from FrontEnd Request
from fastapi import FastAPI
from ai_agent import get_response_from_ai_agent

ALLOWED_MODEL_NAMES = ["llama3-70b-8192", "mixtral-8x7b-32768", "llama-3.3-70b-versatile", "gpt-4o-mini"]

app = FastAPI(title="LangGraph AI Agent")

@app.post("/chat")
def chat_endpoint(request: RequestState): 
    """
    API Endpoint to interact with the Chatbot using LangGraph and search tools.
    It dynamically selects the model specified in the request
    """
    # 1. Model Name check validation
    if request.model_name not in ALLOWED_MODEL_NAMES:
        return {"error": "Invalid model name. Kindly select a valid AI model"}
    
    # 2. System prompt handling (Agar khali ho to fallback default set karein)
    safe_system_prompt = request.system_prompt.strip() if request.system_prompt.strip() else "You are a helpful and smart AI assistant."
    
    # 3. Create AI Agent and get string response from it! 
    agent_response_text = get_response_from_ai_agent(
        llm_id=request.model_name,
        query=request.messages[-1],  # FIX: Poori list ke bajaye sirf aakhri string message bhejein
        allow_search=request.allow_search,
        system_prompt=safe_system_prompt,  # FIX: Empty string validation guard
        provider=request.model_provider
    )
    
    # FIX: Raw string ke bajaye hamesha format dictionary JSON return karein
    return {"response": agent_response_text}

# Step3: Run app & Explore Swagger UI Docs
if __name__ == "__main__":
    import uvicorn
    # Enforce safe reloading
    uvicorn.run("backend:app", host="127.0.0.1", port=9999, reload=True)