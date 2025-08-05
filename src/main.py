# src/main.py
import os
from dotenv import load_dotenv
from scraper import run as scrape
from content_spinner import process
from versioning import add_version
from rl_search import rl_based_search
from rl_reward import calculate_text_reward
from agents.voice_api import text_to_speech

load_dotenv()
URL = os.getenv("URL")
NAME = os.getenv("NAME")
if not URL:
    URL = str(input("Enter URL to scrape: "))
if not NAME:
    NAME = str(input("Enter content name: "))

def speak_text(text):
    mp3 = f"data/processed_content/{NAME}.mp3"
    text_to_speech(text)
    print("Audio saved to", mp3)

def main():
    os.makedirs("data/processed_content", exist_ok=True)

    print("1) Scraping …")
    raw = scrape(URL,NAME,"kk")
    add_version("original", raw)

    print("2) Spinning & Reviewing …")
    try:
        processed = scrape(URL, NAME)
    except Exception as e:
        processed = raw
    add_version("spun_reviewed", processed)

    print("3) RL Search example …")
    docs = [raw, processed]
    print(rl_based_search(docs, "canoe lagoon"))

    print("4) RL Reward …", calculate_text_reward(processed))

    print("5) Voice Playback …")
    speak_text(processed[:200])

    with open(f"data/processed_content/{NAME}_final.txt","w",encoding="utf-8") as f:
        f.write(processed)
    print("Done. Final text saved.")

if __name__=="__main__":
    main()