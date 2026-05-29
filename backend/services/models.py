import google.generativeai as genai
import os


class Models:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    @staticmethod
    def embedding_model(text: str):
        result = genai.embed_content(
            model='gemini-embedding-2',
            content=text
        )
        return result["embedding"]

    @staticmethod
    def get_llm():
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")
        return model 