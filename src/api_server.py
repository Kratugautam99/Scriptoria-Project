from fastapi import FastAPI
import os
from agents.ai_reviewer import ReviewerAgent  
from agents.ai_writer import WriterAgent
from src.scraper import run as scrape

app = FastAPI(title="Scriptoria Agentic API")

api_key = os.getenv("GEMINI_API_KEY")
reviewer = ReviewerAgent(api_key)  
writer = WriterAgent(api_key)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Scriptoria Agentic API"}

@app.get("/write")
def rewrite_chapter_api(url: str):
    content = scrape(url, "chapter_content")
    rewritten = writer.spin_chapter(content, human_feedback="")
    return {"rewritten_content": rewritten}

@app.get("/review")
def review_chapter_api(url: str):
    content = scrape(url, "chapter_content")
    reviewed = reviewer.review_chapter(content)
    return {"reviewed_content": reviewed}
