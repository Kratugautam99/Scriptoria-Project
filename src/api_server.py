# src/api_server.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Scriptoria Agentic API")

class ChapterRequest(BaseModel):
    content: str

@app.post("/spin")
def spin_chapter_api(req: ChapterRequest):
    return {"spun_content": f"[SPUN] {req.content[:100]}..."}

@app.post("/review")
def review_chapter_api(req: ChapterRequest):
    return {"reviewed_content": f"[REVIEWED] {req.content[:100]}..."}