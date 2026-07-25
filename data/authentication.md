---
title: Authentication
category: Getting Started
audience: Developers
topics:
  - authentication
  - api keys
  - security
  - environment variables
related:
  - responses-api.md
  - models.md
last_updated: 2026-07
---

# Authentication

**Last Updated:** July 2026

## Overview

Before your application can interact with the OpenAI API, it must authenticate every request using an API key. Authentication allows OpenAI to identify your project, apply usage limits, attribute billing correctly, and authorize access to models and services.

API keys should always be treated as sensitive credentials. Never embed them directly into source code, client-side applications, or public repositories.

## How Authentication Works

Every request includes an Authorization header:

```text
Authorization: Bearer YOUR_API_KEY
```

The server validates the key before processing the request.

## Creating an API Key

1. Create or sign in to your OpenAI account.
2. Create a project.
3. Generate a new API key.
4. Copy the key immediately.
5. Store it securely.

## Storing API Keys Securely

Avoid hardcoding keys:

```python
client = OpenAI(api_key="sk-...")
```

Instead:

```bash
export OPENAI_API_KEY="your_api_key"
```

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
```

## Using a .env File

```text
OPENAI_API_KEY=your_api_key_here
```

```python
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
```

## Initializing the Client

```python
from openai import OpenAI

client = OpenAI()
```

## First Request

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input="Say hello."
)

print(response.output_text)
```

## Common Errors

### Missing API Key
- Environment variable not set
- Incorrect variable name

### Invalid API Key
- Typo
- Deleted or inactive key

## Security Best Practices

**Do**
- Store keys in environment variables
- Rotate keys periodically
- Use separate keys for development and production

**Don't**
- Commit keys to Git
- Expose keys in frontend applications
- Share keys publicly

## FAQ

### Can I expose my API key in browser JavaScript?

No. Always send requests through a trusted backend.

### Should I use different keys for dev and production?

Yes.

## Summary

Authentication is required for every OpenAI API request. Store credentials securely, use environment variables, and follow good secret-management practices.
