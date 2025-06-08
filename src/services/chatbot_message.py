from typing import List, Optional
from datetime import datetime

from llama_index.core.llms import ChatMessage
from src.storage.chatbot_message import CRUDChatMessage
from src.schemas.chatbot import ChatbotMessage

class ChatbotMessageManagement():
    def __init__(self):
        """
        Initialize the JobDescriptionManagement instance.
        """
        self.collection = CRUDChatMessage()     


    def insert_chat_record(self, message: ChatbotMessage):
        item = message.model_dump()
        self.collection.insert_one_doc(item)

    def find_chat_record_by_session_id(self, session_id: str):
        query = {"session_id": session_id}
        results = self.collection.read_documents(query)
        return [ChatbotMessage(**record) for record in results]

    def get_conversation_history(
        self, session_id, intent: Optional[str] = None, sort_order=1
    ) -> ChatMessage:
        conversations = self.aggregate_conversation_by_session_id(
            session_id=session_id, sort_order=sort_order
        )

        chat_history = []
        if len(conversations) > 0:
            for record in conversations:
                user_message = {"role": "user", "content":record.chat_message}
                assistant_message = {"role": "assistant", "content":record.answer}
                if not intent or intent == record.intent:
                    chat_history.append(user_message)
                    chat_history.append(assistant_message)

        chat_messages = [
            ChatMessage(role=message["role"], content=message["content"])
            for message in chat_history
        ]
        return chat_messages
    
    def aggregate_conversation_by_session_id(
        self, session_id: str, sort_order: int = 1
    ):
        pipeline = [
            {"$match": {"session_id": session_id}},
            {"$sort": {"datetime": sort_order}},
        ]
        results = list(self.collection.collection.aggregate(pipeline))
        return [ChatbotMessage(**record) for record in results]