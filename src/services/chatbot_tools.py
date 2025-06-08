import os
from llama_index.core import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexAutoRetriever, VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import PromptTemplate
from llama_index.core.tools import FunctionTool
from typing import Annotated
from typing import List, Optional
import chromadb
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.vector_stores.types import MetadataInfo, VectorStoreInfo
from pydantic import BaseModel, Field
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator, FilterCondition
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from src.engines.llm_engine import LLMEngine
from src.prompts.chatbot_prompt import *
import re
import logging
from dotenv import load_dotenv
load_dotenv()

TOP_K=int(os.getenv("TOP_K"))

vectorstore_path = os.getenv("VECTORSTORE_PATH")
vectorstore_path = os.path.abspath(vectorstore_path)
# vectorstore_path = "../../chroma_db_eachfileisanode"

class Disability(BaseModel):
    type: str = Field(description="Tên loại bệnh tật nằm trong danh sách sau: ['sâu1', 'sâu2']")
    level: str = Field(description="Mức độ 'nhẹ' hoặc 'nặng'")

class ChatbotTools:
    def __init__(self):

        """
        Tools for chatbot agent.
        """

        # Initialize LLM and embedding model
        self.engine = LLMEngine()
        self.llm = self.engine.llm
        self.embed_model = self.engine.embed_model
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
    
    def get_tools(self):
        return   
    