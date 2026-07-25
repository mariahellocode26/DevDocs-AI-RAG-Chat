---
title: Models
category: Core Concepts
audience: Developers
topics:
  - models
  - model selection
  - reasoning
  - embeddings
related:
  - responses-api.md
  - embeddings.md
  - function-calling.md
last_updated: 2026-07
---

# Models

## Overview

A model is the AI system that processes your input and generates an output. Different models are designed for different tasks, such as reasoning, text generation, multimodal understanding, or creating embeddings.

Selecting the right model involves balancing quality, speed, latency, and cost.

## Model Categories

### Language Models

Used for:

- Chatbots
- Question answering
- Summarization
- Content generation
- Code assistance

These models are commonly accessed through the Responses API.

### Embedding Models

Embedding models convert text into numerical vectors for:

- Semantic search
- Retrieval-Augmented Generation (RAG)
- Recommendation systems
- Clustering

Unlike language models, embedding models do not generate text.

## Choosing a Model

Consider:

- Task complexity
- Response quality
- Latency requirements
- Cost
- Context window
- Multimodal support

## Example

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Explain vector databases."
)

print(response.output_text)
```

Embedding example:

```python
embedding = client.embeddings.create(
    model="text-embedding-3-small",
    input="Vector databases"
)
```

## Best Practices

- Use language models for generation.
- Use embedding models for retrieval.
- Test different models for your workload.
- Monitor latency and cost in production.

## Common Mistakes

- Using a language model to generate embeddings.
- Mixing embedding models within the same vector index.
- Choosing the largest model for every task.

## FAQ

### Can I change models later?

Yes. Most applications can switch models with minimal code changes.

### Which model should I use for RAG?

A common architecture combines an embedding model for retrieval with a language model for answer generation.

## Summary

Models are the core of every OpenAI application. Understanding the differences between language and embedding models helps you design efficient, scalable, and cost-effective AI systems.
