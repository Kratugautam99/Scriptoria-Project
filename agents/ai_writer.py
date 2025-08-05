# agents/ai_writer.py
import google.generativeai as genai

class WriterAgent:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def spin_chapter(self, content: str, human_feedback: str) -> str:
        if human_feedback:
            prompt = f"Rewrite and Change this chapter based on the following feedback:{human_feedback}.\n Original content:\n{content}"
        else:
            prompt = f"Rewrite this in a modern, engaging style, removing any inaccuracies and maintain structure.\n Original content:\n{content}"
        resp = self.model.generate_content(prompt)
        return resp.text