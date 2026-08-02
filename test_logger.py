from monitoring.logger import log_request


record = {
    "question": "How does authentication work?",

    "answer": "Use an API key in the Authorization header.",

    "model_name": "gpt-5.4-mini",

    "top_k": 5,

    "latency_seconds": 1.34,

    "input_tokens": 900,

    "output_tokens": 200,

    "total_tokens": 1100,

    "estimated_cost": 0.0032,

    "retrievals": [
        {
            "chunk_id": "abc123",
            "document_name": "authentication.md",
        },
        {
            "chunk_id": "def456",
            "document_name": "responses-api.md",
        },
    ],
}


log_request(record)

print("Request logged successfully!")