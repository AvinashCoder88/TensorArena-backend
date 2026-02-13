import os
import google.generativeai as genai
from typing import Optional, Dict, Any
import json

class GradingService:
    def __init__(self):
        # Configure Gemini
        # Assuming GOOGLE_API_KEY is in env
        if os.getenv("GOOGLE_API_KEY"):
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            print("Warning: GOOGLE_API_KEY not found")
            self.model = None

    async def grade_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        if not self.model:
            raise ValueError("Gemini API not configured")

        prompt = """
        You are an expert teacher. Analyze this answer sheet image.
        
        1. Identify any spelling mistakes. For each, provide the 'original' text and the 'correction'.
        2. Identify any math equations. Check if they are correct. If incorrect, provide the 'correction' and a brief 'explanation'.
        3. Identify any diagrams. Analyze if they are correct based on the context (infer context from text). Provide 'feedback' on diagrams.
        4. Provide an overall 'grade' (e.g., A, B, C or 8/10) and general 'remarks'.
        
        Return the result as a JSON object with this structure:
        {
            "spelling_mistakes": [{"original": "...", "correction": "...", "context": "..."}],
            "math_corrections": [{"original": "...", "correction": "...", "explanation": "..."}],
            "diagram_analysis": [{"description": "...", "feedback": "...", "is_correct": boolean}],
            "grade": "...",
            "remarks": "..."
        }
        """

        try:
            # Create a content part for the image
            image_part = {
                "mime_type": mime_type,
                "data": image_bytes
            }

            response = self.model.generate_content([prompt, image_part])
            
            # Extract JSON from response (handle markdown code blocks if any)
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text: # fallback if just ```
                text = text.split("```")[1].split("```")[0]
                
            return json.loads(text)
            
        except Exception as e:
            print(f"Error grading image: {e}")
            # Return a fallback or re-raise
            return {
                "error": str(e), 
                "grade": "N/A", 
                "remarks": "Failed to process image."
            }
