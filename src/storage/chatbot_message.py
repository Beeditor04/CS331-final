from src.storage.mongodb import CRUDDocuments

class CRUDChatMessage(CRUDDocuments):
    def __init__(self):
        CRUDDocuments.__init__(self)
        self.collection = CRUDDocuments.connection.db.chatbot_message