# src/main.py
import os
import sys
from dotenv import load_dotenv
from scraper import run as scrape
from versioning import add_version
from rl_search import rl_based_search
from rl_reward import calculate_text_reward
sys.path.append(os.path.abspath(os.path.join(__file__,"..","..")))
from agents.ai_reviewer import ReviewerAgent
from agents.ai_writer import WriterAgent
from agents.voice_api import text_to_speech

load_dotenv()
URL = os.getenv("URL")
NAME = os.getenv("NAME")
RLVar = os.getenv("RLVAR")
api_key = os.getenv("GEMINI_API_KEY")
if not URL:
    URL = str(input("Enter URL to scrape: "))
if not NAME:
    NAME = str(input("Enter content name: "))
if not RLVar:
    RLVar = str(input("Enter RL search query: "))
if not api_key:
    api_key = str(input("Enter your GEMINI API Key: "))

def speak_text(text):
    text_to_speech(text)
    print(f"Audio saved to data/processed_content/{NAME}.txt")

def main():
    os.makedirs("data/processed_content", exist_ok=True)

    print("1) Scraping …")
    raw = scrape(URL,NAME)
    add_version("original", raw)

    print("2) Writing & Reviewing …")
    RA = ReviewerAgent(api_key)
    WA = WriterAgent(api_key)
    processed = WA.spin_chapter(raw, human_feedback="")
    reviewed = RA.review_chapter(processed)
    add_version("processed", processed)
    add_version("reviewed", reviewed)

    print("3) RL Search example …")
    docs = [raw, processed]
    print(rl_based_search(docs, RLVar)[:1500])

    print("4) RL Reward … original->", calculate_text_reward(raw), " and rewritten->", calculate_text_reward(raw, rewritten=processed))

    print("5) Voice Playback …")
    speak_text(processed[:1500])

    with open(f"data/processed_content/{NAME}.txt","w",encoding="utf-8") as f:
        f.write(processed)
    print("Done. Final text saved.")

if __name__=="__main__":
    main()