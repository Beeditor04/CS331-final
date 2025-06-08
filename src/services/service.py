import os

from src.services.chatbot_message import ChatbotMessageManagement
from src.engines.llm_engine import LLMEngine
from src.engines.chatbot_agent import Agent


class Service():
    def __init__(self):
        self.llm_engine = LLMEngine()
        self.chatbot = Agent()

        self.chatbot_mess_mgmt = ChatbotMessageManagement()