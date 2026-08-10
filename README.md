# DevDocs-AI-RAG-Chat

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/b566e34c-2943-4a8b-ac23-86f801fe95fe"
    width="85%"
    alt="Chat Demo"
  />
</p>

<p align="center">
  <img src="assets/dashboard-demo.gif" width="85%" alt="Monitoring Dashboard Demo">
</p>

A Retrieval-Augmented Generation (RAG) chatbot that answers developer questions about the OpenAI API documentation.

The project combines semantic search, retrieval evaluation, and a Streamlit interface to help developers find answers from technical documentation quickly.

---

# Table of Contents

- [Problem Description](#problem-description)
- [Retrieval Flow](#retrieval-flow)
- [Retrieval Evaluation](#retrieval-evaluation)
- [Interface](#interface)
- [Ingestion Pipeline](#ingestion-pipeline)
- [Monitoring](#monitoring)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Future Improvements](#future-improvements)

---

# Problem Description

## The problem

Developers often need quick answers from large technical documentation. Searching manually through multiple pages interrupts development and makes it difficult to find the right information efficiently.

This project solves that problem by using Retrieval-Augmented Generation (RAG) to retrieve relevant documentation chunks and generate answers grounded in the OpenAI API documentation.

## Target users

- Software developers
- API users
- Students learning the OpenAI API
- Engineers integrating LLMs into applications

## Why RAG?

A language model alone cannot reliably answer questions about large documentation sets.

RAG improves the quality of answers by:

- Retrieving relevant documentation sections
- Injecting them into the prompt
- Generating answers grounded in the source documents

## Documentation corpus

The knowledge base consists of six OpenAI documentation files:

- `authentication.md`
- `responses-api.md`
- `embeddings.md`
- `function-calling.md`
- `models.md`
- `streaming.md`

---

# Retrieval Flow

## Architecture

```text
                    User Question
                           │
                           ▼
               ┌────────────────────┐
               │     Retriever      │
               └─────────┬──────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
      Text Search            Vector Search
      (MinSearch)      (Sentence Transformers)
              │                     │
              └──────────┬──────────┘
                         │
                         ▼
                   Top-k Chunks
                         │
                         ▼
                  Prompt Builder
                         │
                         ▼
                    OpenAI Model
                         │
                         ▼
                 Generated Answer
```

## Retrieval methods

### Text search

- MinSearch
- Keyword matching
- Fast lexical retrieval

### Vector search

- Sentence Transformers
- Semantic similarity search
- Embedding-based retrieval

## RAG pipeline

1. Receive the user question.
2. Retrieve the top-k relevant chunks.
3. Build the prompt context.
4. Send the prompt to the OpenAI model.
5. Generate the final answer.

---

# Retrieval Evaluation

The retriever was evaluated using four metrics:

- Hit@1
- Hit@3
- Hit@5
- Mean Reciprocal Rank (MRR)

## Results

| Method | Hit@1 | Hit@3 | Hit@5 | MRR |
| :--- | ---: | ---: | ---: | ---: |
| Text search | 0.500 | 0.667 | 0.700 | 0.579 |
| Vector search | **0.600** | **0.833** | **0.967** | **0.730** |

## Conclusion

Vector search outperformed text search across all metrics and was selected as the default retriever.

Key observations:

- Vector search returns the correct chunk first 60% of the time.
- The correct chunk appears in the top 5 results 96.7% of the time.
- Retrieval quality is strong, although ranking can still be improved.

---

# Interface

The application provides a Streamlit-based interface for interacting with the RAG system.

## Features

- Chat interface
- Source document panel
- Response metadata
- Monitoring dashboard
- Conversation history

---

# Ingestion Pipeline

The ingestion pipeline automatically transforms the raw documentation into searchable chunks.

```text
Markdown documents
        │
        ▼
Metadata extraction
        │
        ▼
Document chunking
        │
        ▼
Embedding generation
        │
        ▼
Knowledge base
```

## Features

- Automated ingestion with Python scripts
- Markdown chunking
- Metadata extraction
- Embedding generation
- JSON export

---

# Monitoring

The project includes logging and monitoring with Grafana dashboards.

## Tracked metrics

- Total requests
- Average latency
- Token usage
- API cost
- Request volume
- Most retrieved documents

## Dashboard charts

- Most retrieved documents
- Total requests
- Average latency over time
- Cost over time
- Requests over time
- Token usage over time

---

# Project Structure

```text
DevDocs-AI-RAG-Chat
├── app.py
├── main.py
├── rag.py
├── ingest.py
├── embed.py
├── text_search.py
├── vector_search.py
├── evaluate_retrieval.py
├── run_rag_eval.py
├── run_pipeline.py
│
├── data/
├── components/
├── monitoring/
├── grafana/
├── styles/
├── results/
│
├── ground_truth.csv
├── pyproject.toml
├── docker-compose.yml
└── README.md
```

---

# Tech Stack

- Python 3.12
- Streamlit
- OpenAI Python SDK
- Sentence Transformers
- MinSearch
- Markdown
- Grafana
- Docker Compose
- uv

---

# Future Improvements

- Hybrid search
- Document reranking
- Query rewriting
- PostgreSQL or Qdrant backend
- Dockerized deployment
- Cloud deployment
- Conversation memory

---

# Status

🚧 Work in progress.

The following sections will be added in future updates:

- LLM evaluation
- Reproducibility and setup instructions
- Containerization details
- Hybrid retrieval experiments
- Cloud deployment
