---
title: Function Calling
category: Advanced Features
audience: Developers
topics:
  - function calling
  - tools
  - structured outputs
  - agents
related:
  - responses-api.md
  - streaming.md
  - models.md
last_updated: 2026-07
---

# Function Calling

## Overview

Function calling allows a language model to request that your application execute a predefined function (tool). Instead of directly answering a question that requires external data or actions, the model returns a tool call that your application executes.

## Common Use Cases

- Weather lookups
- Database queries
- Calendar events
- Order status
- Internal business APIs

## Tool Definition

```python
tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    }
]
```

## Basic Flow

1. Send the user's question and tool definitions.
2. The model decides whether a tool is needed.
3. Your application executes the requested function.
4. Return the tool result to the model.
5. The model generates the final answer.

## Example Workflow

```text
User
  │
  ▼
Responses API
  │
Tool Call
  ▼
Your Function
  │
Tool Result
  ▼
Responses API
  │
Final Answer
```

## Best Practices

- Keep tool descriptions clear.
- Validate all function arguments.
- Handle failures gracefully.
- Return structured data.
- Only expose trusted functions.

## Common Mistakes

- Letting the model execute arbitrary code.
- Skipping argument validation.
- Returning inconsistent data formats.

## FAQ

### Does the model execute my code?

No. Your application executes the function after receiving the tool call.

### Can I define multiple tools?

Yes. The model can choose the appropriate tool based on the user's request.

## Summary

Function calling connects language models with external systems. It enables applications to retrieve live information, perform actions, and combine LLM reasoning with business logic in a controlled and secure way.
