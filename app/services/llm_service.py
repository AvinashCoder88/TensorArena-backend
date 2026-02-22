import os
import json
import google.generativeai as genai


class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-pro")
        else:
            self.model = None

    def _extract_json(self, text: str):
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        try:
            return json.loads(text)
        except Exception:
            return None

    async def generate_structured(self, prompt: str):
        if not self.model:
            raise ValueError("Gemini API not configured")
        response = self.model.generate_content(prompt)
        parsed = self._extract_json(response.text)
        return parsed or {"raw": response.text}
