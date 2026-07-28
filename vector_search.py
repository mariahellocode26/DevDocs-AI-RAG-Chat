"""
vector_search.py

Performs semantic vector search using Sentence Transformers
and cosine similarity.

Run:
    python vector_search.py
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("chunks_with_embeddings.json")

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# Load embedding model
# ============================================================

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)


# ============================================================
# Load chunks
# ============================================================

print(f"Loading {INPUT_FILE}...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")


# ============================================================
# Prepare embedding matrix
# ============================================================

chunk_embeddings = np.array(
    [chunk["embedding"] for chunk in chunks]
)

print("Embedding matrix shape:", chunk_embeddings.shape)


# ============================================================
# Search
# ============================================================

def search(query, top_k=5):
    """
    Perform semantic vector search.
    """

    # Embed the query
    query_embedding = model.encode(query)

    # Compute cosine similarity
    scores = cosine_similarity(
        [query_embedding],
        chunk_embeddings
    )[0]

    # Get indices of top scores
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for idx in top_indices:

        chunk = chunks[idx].copy()

        chunk["score"] = float(scores[idx])

        results.append(chunk)

    return results


# ============================================================
# Example
# ============================================================

if __name__ == "__main__":

    while True:

        query = input("\nQuery (or 'exit'): ")

        if query.lower() == "exit":
            break

        results = search(query)

        print()

        for i, result in enumerate(results, start=1):

            print("=" * 80)
            print(f"Result {i}")
            print("=" * 80)

            print(f"Score : {result['score']:.4f}")
            print(f"Title : {result['title']}")

            headers = " > ".join(
                h for h in [
                    result.get("header1"),
                    result.get("header2"),
                    result.get("header3"),
                ]
                if h
            )

            print(f"Section : {headers}")

            print()
            print(result["text"][:500])
            print()