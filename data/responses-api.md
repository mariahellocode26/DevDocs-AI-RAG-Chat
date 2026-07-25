---
title: Responses API
category: Core API
audience: Developers
topics:
  - responses api
  - text generation
  - multimodal
  - sdk
  - python
related:
  - authentication.md
  - streaming.md
  - function-calling.md
  - models.md
last_updated: 2026-07
---

# Responses API

**Last Updated:** July 2026

## Overview

The Responses API is the primary interface for interacting with OpenAI language models. It provides a consistent way to send inputs to a model and receive generated outputs. It supports text generation, structured outputs, multimodal inputs, streaming, and tool calling.

## Basic Request

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Explain what an API is in one paragraph."
)

print(response.output_text)
```

## Request Components

| Field | Description |
|--------|-------------|
| model | Model to use |
| input | Prompt or conversation |
| tools | Optional tool definitions |
| stream | Enable streaming |
| temperature | Controls randomness (if supported) |
| max_output_tokens | Limits output length |

## Understanding Input

Simple prompt:

```python
input="What is machine learning?"
```

Long-form prompts may include detailed instructions and retrieved context for RAG applications.

## Understanding Output

The easiest way to access generated text is:

```python
print(response.output_text)
```

Depending on the request, responses may also contain usage information, tool calls, or structured outputs.

## Example: Question Answering

```python
response = client.responses.create(
    model="gpt-5",
    input="What are embeddings?"
)

print(response.output_text)
```

## Example: Summarization

```python
article = "Very long article..."

response = client.responses.create(
    model="gpt-5",
    input=f"Summarize the following:\n\n{article}"
)

print(response.output_text)
```

## Example: Translation

```python
response = client.responses.create(
    model="gpt-5",
    input="Translate 'Good morning' into French."
)

print(response.output_text)
```

## Error Handling

Common issues include:

- Missing or invalid API key
- Missing required fields
- Invalid parameter values
- Rate limiting

## Best Practices

- Keep prompts focused.
- Reuse the client object.
- Log latency and token usage.
- Handle API errors gracefully.
- Send only relevant context in RAG systems.

## Responses API in RAG

```
User Question
      │
      ▼
Retriever
      │
Relevant Chunks
      │
      ▼
Prompt Builder
      │
      ▼
Responses API
      │
      ▼
Generated Answer
```

## Summary

The Responses API is the recommended interface for modern OpenAI applications and is well suited for chatbots, document assistants, and Retrieval-Augmented Generation systems.
