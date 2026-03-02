from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    top_k: Optional[int] = Field(5, ge=1, le=20)
    conversation_title: Optional[str] = Field(None, description="Optional session title")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")


class MessageResponse(BaseModel):
    question: str
    answer: str
    sources: List[dict]
    confidence: float
    created_at: datetime
        
class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    messages: List[MessageResponse]

class SimpleResponse(BaseModel):
    message: str
    
    
    
class CreateConversationRequest(BaseModel):
    title: Optional[str] = Field("New Conversation", max_length=200)
    
    
class ConversationSummaryResponse(BaseModel):
    conversation_id: str
    title: str
    created_at: datetime
    class Config:
        from_attributes = True



class TextBookCreate(BaseModel):
    class_name: int
    subject: str
    part: str

class TextBookResponse(BaseModel):
    id: str
    class_name: int
    subject: str
    part: str
    file_url: str