import os
import json
import google.generativeai as genai
from datetime import datetime

GEMINI_API_KEY = "AIzaSyD6dzEw3vdxB6apeprHH1d0nKwVNWTj02Q"

class AIEvaluator:
    def __init__(self):
        """
        Initialize Gemini client
        """
        api_key = os.environ.get(GEMINI_API_KEY)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def evaluate(self, question, student_answer):
        """
        Evaluates a student answer using Gemini.

        Returns:
        {
            feedback: str,
            score: float,
            raw_prompt: str,
            raw_response: str
        }
        """

        prompt = f"""
You are an examiner.

Evaluate the student's answer strictly and fairly.

Instructions:
- Provide detailed, constructive feedback.
- Assign a numeric score out of 10.
- Return ONLY valid JSON.
- Do NOT include markdown or extra text.

Required JSON format:
{{
  "feedback": "<detailed feedback>",
  "score": <number>
}}

Question:
{question}

Student Answer:
{student_answer}
"""

        try:
            response = self.model.generate_content(prompt)
            raw_response = response.text.strip()

            parsed = json.loads(raw_response)

            return {
                "feedback": parsed.get("feedback", ""),
                "score": float(parsed.get("score", 0)),
                "raw_prompt": prompt,
                "raw_response": raw_response,
                "evaluated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            # Fail gracefully but log everything
            return {
                "feedback": f"AI evaluation failed: {str(e)}",
                "score": 0,
                "raw_prompt": prompt,
                "raw_response": "",
                "evaluated_at": datetime.utcnow().isoformat()
            }