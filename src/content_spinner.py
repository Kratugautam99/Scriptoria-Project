# src/content_spinner.py
import os, sys
from bs4 import BeautifulSoup
sys.path.append(os.path.abspath(os.path.join(__file__,"..","..")))

from agents.ai_writer import WriterAgent
from agents.ai_reviewer import ReviewerAgent
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def process(raw_html_path: str) -> str:
    with open(raw_html_path, encoding="utf-8") as f:
        raw_html = f.read()
    soup = BeautifulSoup(raw_html, "html.parser")
    for tag in soup(["script","style"]): tag.decompose()
    clean = "\n\n".join(p.get_text(strip=True) for p in soup.find_all("p"))
    writer = WriterAgent(API_KEY)
    spun = writer.spin_chapter(clean)
    reviewer = ReviewerAgent(API_KEY)
    return reviewer.review_chapter(spun)