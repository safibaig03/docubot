import os
import google.generativeai as genai
from groq import Groq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class LLMResponseAgent:
    def __init__(self):
        self.gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        self.groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

        self.hf_client = InferenceClient(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            token=os.environ.get("HUGGINGFACE_API_KEY")
        )

    def generate_response(self, model_name: str, context_chunks: List[Dict], history: List[Dict], query: str) -> str:
        
        context_for_llm = ""
        for source in context_chunks:
            context_for_llm += source['content'] + "\n\n"

        if model_name == 'gemini':
            prompt = f"""
            You are a helpful AI assistant. Your task is to synthesize a clear and concise answer to the user's question based exclusively on the provided `CONTEXT` below.
            If the answer cannot be found within the context, you must state 'I could not find an answer to that in the provided documents.'
            --- CONTEXT BEGIN ---
            {context_for_llm}
            --- CONTEXT END ---
            Question: {query}
            """
            response = self.gemini_client.generate_content(prompt)
            return response.text

        elif model_name == 'groq':
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. Your task is to synthesize a clear and concise answer to the user's question based exclusively on the provided context. If the answer is not in the context, say 'I could not find an answer to that in the provided documents.'"
                    },
                    {
                        "role": "user",
                        "content": f"CONTEXT: {context_for_llm} \n\n QUESTION: {query}"
                    }
                ],
                model="llama-3.1-8b-instant", 
            )
            return chat_completion.choices[0].message.content
        
        elif model_name == 'huggingface':
            system_prompt = "You are a helpful AI assistant. Your task is to synthesize a clear and concise answer to the user's question based exclusively on the provided context. If the answer is not in the context, say 'I could not find an answer to that in the provided documents.'"
            user_prompt = f"CONTEXT: {context_for_llm} \n\n QUESTION: {query}"
            
            response = self.hf_client.chat_completion(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                max_tokens=500
            )
            return response.choices[0].message.content

        else:
            return "Error: Invalid model selected."