from pydantic import BaseModel
from datetime import datetime


class InputChatbotMessage(BaseModel):
    session_id: str
    message: str

class ChatbotMessage(BaseModel):
    session_id: str
    chat_message: str
    answer: str
    datetime: datetime