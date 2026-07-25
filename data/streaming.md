---
title: Streaming
category: Advanced Features
audience: Developers
topics:
  - streaming
  - real-time responses
  - latency
  - user experience
related:
  - responses-api.md
  - function-calling.md
  - models.md
last_updated: 2026-07
---

# Streaming

## Overview

Streaming allows an application to receive a model's output incrementally instead of waiting for the complete response. This improves perceived responsiveness and provides a better user experience for longer generations.

## Why Use Streaming?

Streaming is useful when:

- Responses are long.
- Low perceived latency is important.
- Building chat applications.
- Displaying generated text as it arrives.

## Basic Example

```python
from openai import OpenAI

client = OpenAI()

stream = client.responses.create(
    model="gpt-5",
    input="Write a short story about space.",
    stream=True
)

for event in stream:
    print(event)
```

## Typical Streaming Flow

```text
User Request
     │
     ▼
Responses API
     │
     ▼
Token 1
Token 2
Token 3
...
Final Response
```

## Handling Events

Applications typically:

1. Open a streaming connection.
2. Process incoming events.
3. Append new text to the UI.
4. Detect completion.
5. Close the stream.

## Best Practices

- Update the UI incrementally.
- Handle interruptions gracefully.
- Show a loading indicator before the first token.
- Close streams when complete.

## Common Mistakes

- Assuming the full response arrives in one event.
- Ignoring connection errors.
- Blocking the UI while waiting for tokens.

## FAQ

### Is streaming faster?

The total generation time is often similar, but users see results sooner.

### Can streaming be used with RAG?

Yes. Retrieve relevant context first, then stream the generated answer.

## Summary

Streaming improves responsiveness by delivering model output incrementally. It is especially valuable for chat interfaces, document assistants, and other applications where users benefit from seeing results immediately.
