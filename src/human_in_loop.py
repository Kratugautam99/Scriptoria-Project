# src/human_in_loop.py

def get_human_feedback(text: str) -> str:
    """
    Print AI output, accept user edits or keep as-is.
    """
    print("=== AI OUTPUT PREVIEW ===\n")
    print(text[:500] + ("\n..." if len(text)>500 else ""))
    fb = input("\nEnter your edits (or Enter to accept):\n")
    return fb.strip() or text