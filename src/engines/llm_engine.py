import os
from fastapi import (
    status,
    HTTPException,
)
from dotenv import load_dotenv
load_dotenv()
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding

# Accessing variables
api_key = os.getenv('api_key')
azure_endpoint = os.getenv('azure_endpoint')
api_version = os.getenv('api_version')
deployment_name = os.getenv("deployment_name")
model_name = os.getenv("model_name")
openai_key = os.getenv("OPENAI_API_KEY")

deployment_name_2 = os.getenv("deployment_name_2")
model_name_2 = os.getenv("model_name_2")

embeding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
embeding_model_deployment_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
embedding_api_key = os.getenv("AZURE_OPENAI_EMBEDDING_API_KEY")
embedding_endpoint = os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT")
embedding_api_version = os.getenv("AZURE_OPENAI_EMBEDDING_API_VERSION")

class LLMEngine():
    def __init__(self):
        self.llm = AzureOpenAI(
                    model=model_name,
                    engine=deployment_name,
                    api_key=api_key,
                    azure_endpoint=azure_endpoint,
                    api_version=api_version)
        self.llm2 = AzureOpenAI(
                    model=model_name_2,
                    engine=deployment_name_2,
                    api_key=api_key,
                    azure_endpoint=azure_endpoint,
                    api_version=api_version,)
        
        self.embed_model = AzureOpenAIEmbedding(
                model=embeding_model_name,
                deployment_name=embeding_model_deployment_name,
                api_key=embedding_api_key,
                azure_endpoint=embedding_endpoint,
                api_version=api_version,
            )
        # self.embed_model = OpenAIEmbedding(
        #     model=embeding_model_name,
        #     api_key=openai_key,
        # )
        
    async def call_llm(self, prompt):
        try:
            response = await self.llm.acomplete(prompt)
            return response.text
        except Exception as e:
            message = f'📌Error in call_llm function. Detail {e}'
            print(message)
            return None
        
class LLMEngine_2():
    def __init__(self):
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY
        )
        
        self.llm = OpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            #max_tokens = 256000,
        )

        self.llm2 = OpenAI(
            model="gpt-4o-mini",
            api_key=OPENAI_API_KEY,
            temperature=0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            #max_tokens = 256000,
        )
        
    async def call_llm(self, prompt):
        try:
            response = await self.llm.acomplete(prompt)
            return response.text
        except Exception as e:
            message = f'📌Error in call_llm function. Detail {e}'
            print(message)
            return None
    
    # async def get_text_embedding(self, text: str):
    #     try: 
    #         response = None
    #         while not response:
    #             try: 
    #                 response = await self.embed_model.aget_text_embedding(text)
    #             except Exception as e:
    #                 message = f'📌Error in get_text_embedding function. Detail {e}. Re-embedding'
    #                 print(message)
    #         return response
    #     except Exception as e:
    #         message = f'📌Error in get_text_embedding function. Detail {e}'
    #         print(message)
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail=message
    #         )