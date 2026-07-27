"""
embed.py

Reads processed_chunks.json
Creates embeddings for each chunk
Saves chunks_with_embeddings.json

Run:
    python embed.py
"""

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


# ============================================================
# Configuration
# ============================================================

INPUT_FILE = Path("processed_chunks.json")
OUTPUT_FILE = Path("chunks_with_embeddings.json")

MODEL_NAME = "all-MiniLM-L6-v2"


# ============================================================
# Load embedding model
# ============================================================

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)

print("Embedding dimension:", model.get_sentence_embedding_dimension())


# ============================================================
# Load chunks
# ============================================================

print(f"Loading {INPUT_FILE}...")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")


# ============================================================
# Build embedding text
# ============================================================

def build_embedding_text(chunk):
    """
    Build the text sent to the embedding model.

    We include document title and section headers so the
    embedding contains additional context.
    """

    parts = [
        chunk.get("title"),
        chunk.get("header1"),
        chunk.get("header2"),
        chunk.get("header3"),
        chunk.get("text"),
    ]

    return "\n".join(
        part.strip()
        for part in parts
        if part
    )


texts = [build_embedding_text(chunk) for chunk in chunks]


# ============================================================
# Generate embeddings
# ============================================================

print("Generating embeddings...")

embeddings = model.encode(
    texts,
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
)

print("Embeddings generated.")


# ============================================================
# Attach embeddings to chunks
# ============================================================

for chunk, embedding in zip(chunks, embeddings):
    chunk["embedding"] = embedding.tolist()


# ============================================================
# Save output
# ============================================================

print(f"Saving {OUTPUT_FILE}...")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        chunks,
        f,
        indent=2,
        ensure_ascii=False,
    )

print("Done!")