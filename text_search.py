"""
text_search.py

Builds a MinSearch index from processed_chunks.json
and performs keyword search.

Run:
    python text_search.py
"""

import json
from pathlib import Path
from minsearch import Index


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("processed_chunks.json")


# ============================================================
# Load chunks
# ============================================================

print(f"Loading {INPUT_FILE}...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")


# ============================================================
# Create index
# ============================================================

print("Building MinSearch index...")

index = Index(
    text_fields=[
        "title",
        "header1",
        "header2",
        "header3",
        "text",
    ],
    keyword_fields=[
        "category",
        "audience",
        "topics",
    ],
)

index.fit(chunks)

print("Index ready.")


# ============================================================
# Search function
# ============================================================

def search(query, top_k=5):
    """
    Perform lexical search.
    """

    results = index.search(
        query=query,
        num_results=top_k,
    )

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

            print("Title:")
            print(result["title"])

            print()

            headers = " > ".join(
                h for h in [
                    result.get("header1"),
                    result.get("header2"),
                    result.get("header3"),
                ]
                if h
            )

            print("Section:")
            print(headers)

            print()

            print(result["text"][:500])

            print()