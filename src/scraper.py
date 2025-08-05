# src/scraper.py
import os
os.system("playwright install")
os.system("playwright install-deps")
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
import sys
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
BASE = os.path.abspath(os.path.join(__file__, "..", ".."))
RAW = os.path.join(BASE, "data", "raw_content")
SS  = os.path.join(BASE, "data", "screenshots")
os.makedirs(RAW, exist_ok=True)
os.makedirs(SS, exist_ok=True)

def run(url: str, name: str, lol="") -> str:
    """Sync scrape + full-page screenshot."""
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        page.screenshot(path=os.path.join(SS, f"{name}.png"), full_page=True)
        browser.close()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style"]): tag.decompose()
    text = "\n\n".join([p.get_text(strip=True) for p in soup.find_all("p")])
    if lol:
        return html
    return text