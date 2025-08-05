# agents/ai_reviewer.py
import os
import google.generativeai as genai

class ReviewerAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def review_chapter(self, content: str) -> str:
        prompt = f"Think you are a well known author and writer. Evaluate the content below and critically analyze/review it on how well it is written in 10 bullet points of 1 sentence:-\n\n{content}"
        resp = self.model.generate_content(prompt)
        return resp.text