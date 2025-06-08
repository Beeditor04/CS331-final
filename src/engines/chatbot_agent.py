from llama_index.core.agent.workflow import FunctionAgent
from src.services.chatbot_tools import ChatbotTools
from src.prompts.chatbot_prompt import *
from llama_index.core.memory.chat_memory_buffer import ChatMemoryBuffer
from src.engines.llm_engine import LLMEngine

from llama_index.core.agent.workflow import (
    AgentInput,
    AgentOutput,
    ToolCall,
    ToolCallResult,
    AgentStream,
)



class Agent:
    """
    QAAgent class that initializes a FunctionAgent, takes queries, and returns responses.
    """

    def __init__(self):
        tools = ChatbotTools()
        config = LLMEngine()
        self.llm = config.llm
        self.tools = tools.get_tools()
        self.system_prompt = system_prompt

        self.agent = FunctionAgent(
            name="qa_agent",
            tools=self.tools,
            system_prompt=self.system_prompt,
            llm=self.llm,
        )

    async def handle_query(self, query: str, memory: ChatMemoryBuffer) -> str:
        """
        Handles a query by running it through the agent.
        
        Args:
            query (str): The user query.
            memory: memory to pass into the agent.
        
        Returns:
            str: The response from the agent.
        """

        response = await self.agent.run(query, memory=memory)
        return str(response)
    
    async def stream_query(self, query: str, memory: ChatMemoryBuffer):
        """
        Streaming response from the agent.
        Can add tool call and tool call result to the stream.
        
        """
        handler = self.agent.run(query, memory=memory)
        async for event in handler.stream_events():
            if isinstance(event, AgentStream):
                yield event.delta
