# src/rl_search.py
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")
MODEL_ID = "gemini-2.5-flash"

def rl_based_search(site_url: str, site_title: str, rl_query: str, max_rounds: int = 3):
    """
    Multi-step RL-style search using Gemini API with iterative refinement.
    
    Args:
        site_url (str): Target site URL
        site_title (str): Human-readable site title
        rl_query (str): Initial query string
        max_rounds (int): Max refinement rounds
    
    Returns:
        dict: {
            "site": site_title,
            "url": site_url,
            "query_attempts": [ ... ],
            "final_answer": str
        }
    """
    model = genai.GenerativeModel(MODEL_ID)
    attempts = []
    query = rl_query

    for round_idx in range(1, max_rounds + 1):
        prompt = (
            f"You are an RL-based search agent.\n"
            f"Site: {site_title} ({site_url})\n"
            f"Query attempt {round_idx}: {query}\n\n"
            f"1. Search the site for this phrase or concept.\n"
            f"2. If exact phrase not found, summarize the closest relevant content.\n"
            f"3. Suggest a refined query if needed."
        )

        response = model.generate_content(prompt)
        text = response.text.strip()

        attempts.append({
            "round": round_idx,
            "query": query,
            "result": text
        })

        if "Refined query:" in text:
            query = text.split("Refined query:")[-1].strip()
        else:
            if "does not appear" in text or "found" in text or "appears" in text:
                break

    return {
        "site": site_title,
        "url": site_url,
        "query_attempts": attempts,
        "final_answer": attempts[-1]["result"]
    }
