# src/rl_reward.py

def calculate_text_reward(original: str, reviewed: str = "") -> float:
    """
    Simple proxy reward: ratio of non‐stopword overlap,
    scaled to [0,1]. You can replace this with any RL‐based metric.
    """
    orig_tokens = original.lower().split()
    if not orig_tokens:
        return 0.0
    elif reviewed == "":
        rev_tokens = set(orig_tokens)
        return len(rev_tokens)/len(orig_tokens)
    else:
        orig_tokens = set(orig_tokens)
        rev_tokens  = set(reviewed.lower().split())
        overlap = orig_tokens.intersection(rev_tokens)
        ratio = len(overlap) / len(orig_tokens)
        ratio = ratio if ratio > 0.65 else ratio*1.5
        return ratio