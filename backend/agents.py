import openai
import google.generativeai as genai
from groq import Groq
from typing import List, Dict

class Agent:
    def __init__(self, name: str, role: str, model: str):
        self.name = name
        self.role = role
        self.model = model

    def call(self, prompt: str, context: List[Dict]) -> str:
        raise NotImplementedError


class ChatGPTAgent(Agent):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        super().__init__("ChatGPT", "Product Manager", model)
        self.client = openai.OpenAI(api_key=api_key)

    def call(self, prompt: str, context: List[Dict]) -> str:
        messages = [
            {"role": "system", "content": f"You are a {self.role}. You are collaborating with other AI agents to build a project. IMPORTANT: When sharing code, ALWAYS wrap it in markdown code blocks using triple backticks (```) with the language specified, like ```python or ```javascript or ```html. This ensures proper formatting."}
        ]

        recent_context = context[-5:] if len(context) > 5 else context

        for msg in recent_context:
            messages.append({
                "role": "assistant" if msg["agent"] != "User" else "user",
                "content": f"[{msg['agent']}]: {msg['message'][:500]}"
            })

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=600
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling ChatGPT: {str(e)}"


class GeminiAgent(Agent):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        super().__init__("Gemini", "Full-Stack Developer", model)
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(model)

    def call(self, prompt: str, context: List[Dict]) -> str:
        recent_context = context[-5:] if len(context) > 5 else context

        context_str = "\n".join([
            f"[{msg['agent']}]: {msg['message'][:500]}"
            for msg in recent_context
        ])

        full_prompt = f"""You are a {self.role}. You are collaborating with other AI agents to build a project.

Previous conversation:
{context_str}

Your task: {prompt}

IMPORTANT: When sharing code, ALWAYS wrap it in markdown code blocks using triple backticks (```) with the language specified, like ```python or ```javascript or ```html.
Provide your response with code examples where applicable. Keep responses concise."""

        try:
            response = self.gemini_model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error calling Gemini: {str(e)}"


class GroqAgent(Agent):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__("Groq", "QA Engineer", model)
        self.client = Groq(api_key=api_key)

    def call(self, prompt: str, context: List[Dict]) -> str:
        messages = [
            {"role": "system", "content": f"You are a {self.role}. You are collaborating with other AI agents. Be concise. IMPORTANT: When sharing code, ALWAYS wrap it in markdown code blocks using triple backticks (```) with the language specified, like ```python or ```javascript or ```html."}
        ]

        recent_context = context[-3:] if len(context) > 3 else context

        for msg in recent_context:
            messages.append({
                "role": "assistant" if msg["agent"] != "User" else "user",
                "content": f"[{msg['agent']}]: {msg['message'][:400]}"
            })

        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq: {str(e)}"
