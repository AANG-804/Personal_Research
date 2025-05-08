from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    prompt: str
    model: str
    messages: List[Dict] = []


class ChatResponse(BaseModel):
    response: str


class AgentRequest(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    response: str
