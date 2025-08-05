# src/versioning.py
import chromadb

client = chromadb.PersistentClient(path="chromadb")

col = client.get_or_create_collection("chapters")

def add_version(name: str, content: str):
    col.add(
        documents=[content],
        metadatas=[{"name": name}],
        ids=[f"{name}-{len(col.get()['ids'])}"]
    )

def retrieve_similar(name: str, query: str, k: int = 3):
    res = col.query(query_texts=[query], n_results=k)
    return [doc for doc in res["documents"][0]]