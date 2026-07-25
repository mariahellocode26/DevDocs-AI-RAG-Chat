---
title: Embeddings
category: Core API
audience: Developers
topics:
  - embeddings
  - vector search
  - semantic search
  - rag
related:
  - responses-api.md
  - models.md
last_updated: 2026-07
---

# Embeddings

## Overview

Embeddings convert text into numerical vectors that capture semantic meaning. Similar pieces of text produce vectors that are close together in vector space, making embeddings useful for semantic search and Retrieval-Augmented Generation (RAG).

## Common Uses

- Semantic search
- Document retrieval
- Question answering
- Recommendation systems
- Clustering and classification

## Creating an Embedding

```python
from openai import OpenAI

client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Authentication requires an API key."
)

vector = response.data[0].embedding
print(len(vector))
```

## Typical RAG Workflow

1. Load documents.
2. Split documents into chunks.
3. Create an embedding for each chunk.
4. Store vectors in a vector database.
5. Embed the user's question.
6. Retrieve the nearest chunks.
7. Send the retrieved context to the Responses API.

## Chunking

Good chunks are focused on a single topic and include enough context to stand on their own.

Typical settings:

- Chunk size: 400–800 characters
- Overlap: 50–150 characters

## Similarity Search

When a user asks a question, create an embedding for the query and compare it with stored document vectors using a similarity metric such as cosine similarity.

## Best Practices

- Use the same embedding model for documents and queries.
- Re-embed documents if you change embedding models.
- Store metadata (source, title, section) alongside each vector.
- Chunk before embedding.

## Common Mistakes

- Embedding entire books or very large files as one vector.
- Mixing different embedding models in the same index.
- Omitting metadata.

## FAQ

### Are embeddings readable?

No. They are numerical representations, not text.

### Can embeddings generate answers?

No. Embeddings support retrieval. Language models generate the final answer.

## Summary

Embeddings are the foundation of semantic search and RAG systems. They allow applications to retrieve relevant information efficiently before asking a language model to generate a grounded response.
