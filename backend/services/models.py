import google.generativeai as genai
from openrouter import OpenRouter
from langchain_core.prompts import PromptTemplate
import os
from langchain_core.messages import SystemMessage

SYSTEM_MESSAGE = """
        "You are a helpful assistant for software developers. "
        "You answer questions based on the provided documents. "
        "If the answer is not found in the provided documents, say 'I don't know'. "
        "Always provide concise and accurate answers. Provide code snippets if necessary."
"""

class Models:

    _client = None 

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    @staticmethod
    def embedding_model(text: str):
        result = genai.embed_content(
            model='gemini-embedding-2',
            content=text
        )
        return result["embedding"]

    # @staticmethod
    # def get_model():
    #     if Models._client is None:
    #         Models._client = OpenRouter(
    #             api_key=os.getenv("OPENROUTER_API_KEY", "")
    #         )
    #     return Models._client

    @staticmethod
    def get_llm(prompt: str):
        # client = Models.get_model()

        # response = client.chat.send(
        #     model="qwen/qwen3-next-80b-a3b-instruct:free",
        #     messages = [
        #         {"role": "system", "content": SYSTEM_MESSAGE},
        #         {"role": "user", "content": prompt}
        #     ]
        # )

    
        with OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY", "")) as client:
            response = client.chat.send(
                model="nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
                messages = [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ]
            )
        
        return response.choices[0].message.content
