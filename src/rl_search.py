# src/rl_search.py
from typing import List

def rl_based_search(documents: List[str], query: str) -> str:
    scores = [sum(1 for w in query.lower().split() if w in doc.lower())
              for doc in documents]
    idx = scores.index(max(scores)) if scores else 0
    return documents[idx] if documents else ""