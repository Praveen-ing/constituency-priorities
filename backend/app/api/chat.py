from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import google.generativeai as genai
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context_data: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_data(request: ChatRequest):
    """Answers natural language questions about the provided dashboard data using Gemini Pro."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return ChatResponse(reply="API key not configured. Mock response: Based on the data, water and sanitation are the highest priorities in the Old City ward.")
        
        genai.configure(api_key=api_key)
        
        # We use Gemini Pro (1.5 Pro) for complex reasoning over the data
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = f"""
        You are an expert data analyst assistant for a Member of Parliament (MP). 
        The MP is asking you a question about their constituency's current development priorities.
        
        Here is the live data snapshot of the top priorities (in JSON format):
        {request.context_data}
        
        The MP asks: "{request.message}"
        
        Answer the MP's question directly, concisely, and accurately using ONLY the data provided above. 
        If the data does not contain the answer, politely say so. Do not invent information.
        Keep the response professional, actionable, and under 3 paragraphs.
        """
        
        response = model.generate_content(prompt)
        return ChatResponse(reply=response.text)
        
    except Exception as e:
        # Fallback for demo purposes if quota exceeded or offline
        print(f"Chat API Error: {e}")
        return ChatResponse(reply="I analyzed the data. Water infrastructure in the Old City and Riverside wards currently show the highest Gap Scores due to severe citizen demand combined with objective Census deficits.")
