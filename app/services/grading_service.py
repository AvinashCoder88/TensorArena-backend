import os
import google.generativeai as genai
from typing import Dict, Any, Optional
import json

class GradingService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        else:
            print("Warning: GEMINI_API_KEY or GOOGLE_API_KEY not found")
            self.model = None

    async def extract_question_paper(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
        """Extract questions, marks per question, and total marks from a question paper image/PDF."""
        if not self.model:
            raise ValueError("Gemini API not configured")

        prompt = """
        You are an expert teacher analyzing a question paper / exam paper.

        Carefully read this question paper image and extract ALL questions with their mark allocations.

        For each question:
        1. Identify the question number (q_num)
        2. Extract the full question text (question_text)
        3. Identify how many marks it carries (max_marks) — look for patterns like "[5 marks]", "(3)", "Marks: 10", etc.
        4. If marks are not explicitly stated for a question, estimate based on context.

        Also determine the total marks for the entire paper.

        Return the result as a JSON object with this exact structure:
        {
            "title": "Name/title of the exam if visible, otherwise describe it",
            "total_marks": <total marks for the paper>,
            "questions": [
                {
                    "q_num": 1,
                    "question_text": "Full text of question 1...",
                    "max_marks": 5
                },
                {
                    "q_num": 2,
                    "question_text": "Full text of question 2...",
                    "max_marks": 10
                }
            ],
            "full_text": "Complete text content of the entire question paper"
        }

        Be thorough — capture every question and sub-question. If a question has parts (a, b, c), list them as separate entries like 1a, 1b, 1c.
        """

        try:
            image_part = {"mime_type": mime_type, "data": image_bytes}
            response = self.model.generate_content([prompt, image_part])

            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text)

        except Exception as e:
            print(f"Error extracting question paper: {e}")
            return {"error": str(e), "title": "Unknown", "total_marks": 0, "questions": [], "full_text": ""}

    async def grade_with_context(
        self,
        answer_image_bytes: bytes,
        mime_type: str,
        question_paper_text: str,
        mark_scheme: str,
        total_marks: int
    ) -> Dict[str, Any]:
        """
        Grade an answer sheet using the question paper as context.
        Uses logical reasoning to evaluate each answer — not just keyword matching.
        """
        if not self.model:
            raise ValueError("Gemini API not configured")

        prompt = f"""
        You are an expert, experienced teacher grading a student's answer sheet.

        ## QUESTION PAPER (Reference)
        {question_paper_text}

        ## MARK SCHEME
        {mark_scheme}

        ## TOTAL MARKS: {total_marks}

        ## YOUR TASK
        Carefully examine the student's answer sheet image provided below. For EACH question in the mark scheme:

        1. **Find the student's answer** in the answer sheet image
        2. **Evaluate it logically** — think like a human teacher:
           - Check if the core concept is correct
           - Check if the working/steps are shown (for math/science)
           - Check for partial credit — give marks proportionally for partially correct answers
           - Check spelling, grammar, and presentation for essay-type answers
           - For diagrams, check accuracy and labeling
        3. **Assign marks** out of the maximum for that question
        4. **Write specific remarks** explaining what was right, what was wrong, and how to improve

        ## IMPORTANT GRADING PRINCIPLES
        - Be fair and consistent
        - Award partial marks for partially correct answers
        - If a student writes the right answer but with wrong working, give partial credit
        - If an answer is missing or blank, give 0 marks
        - Look for logical reasoning, not just memorized text
        - Consider alternative correct approaches

        Return the result as a JSON object with this EXACT structure:
        {{
            "questions": [
                {{
                    "q_num": "1",
                    "max_marks": 5,
                    "scored": 3,
                    "remarks": "Correct approach but made an arithmetic error in step 3. Lost 2 marks for the calculation mistake."
                }},
                {{
                    "q_num": "2",
                    "max_marks": 10,
                    "scored": 8,
                    "remarks": "Well-explained with good examples. Minor spelling errors but content is strong."
                }}
            ],
            "total_scored": <sum of all scored>,
            "total_max": {total_marks},
            "percentage": <percentage>,
            "overall_remarks": "Overall assessment of the student's performance with specific areas to improve."
        }}
        """

        try:
            image_part = {"mime_type": mime_type, "data": answer_image_bytes}
            response = self.model.generate_content([prompt, image_part])

            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            result = json.loads(text)

            # Ensure consistency
            if "total_scored" not in result and "questions" in result:
                result["total_scored"] = sum(q.get("scored", 0) for q in result["questions"])
            if "total_max" not in result:
                result["total_max"] = total_marks
            if "percentage" not in result:
                result["percentage"] = round((result["total_scored"] / max(result["total_max"], 1)) * 100, 1)

            return result

        except Exception as e:
            print(f"Error grading answer sheet: {e}")
            return {
                "error": str(e),
                "questions": [],
                "total_scored": 0,
                "total_max": total_marks,
                "percentage": 0,
                "overall_remarks": "Failed to grade — please try again."
            }

    # Keep original method for backward compatibility
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
            image_part = {"mime_type": mime_type, "data": image_bytes}
            response = self.model.generate_content([prompt, image_part])

            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            return json.loads(text)

        except Exception as e:
            print(f"Error grading image: {e}")
            return {"error": str(e), "grade": "N/A", "remarks": "Failed to process image."}
