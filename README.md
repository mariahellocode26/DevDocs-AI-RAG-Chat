# DevDocs-AI-RAG-Chat

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/b566e34c-2943-4a8b-ac23-86f801fe95fe"
    width="85%"
    alt="Chat Demo"
  />
</p>

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/828e0b42-f26b-467e-82c7-e65b92e2b9c2"
    width="85%"
    alt="Grafana Monitoring Dashboard"
  />
</p>

A Retrieval-Augmented Generation (RAG) chatbot that answers developer questions about the OpenAI API documentation.

The project combines document ingestion, text and vector search, RAG, evaluation, logging, monitoring, and a Streamlit interface.

**Project presentation:** [View the project slides](https://docs.google.com/presentation/d/1cFlQA3p99a2MHw24FWnsd8SgfJfVGxuG/edit?slide=id.p3#slide=id.p3)

---

# Table of Contents

- [Problem Description](#problem-description)
  - [The problem](#the-problem)
  - [Target users](#target-users)
  - [Why RAG?](#why-rag)
  - [Documentation corpus](#documentation-corpus)
- [Retrieval Flow](#retrieval-flow)
  - [Architecture](#architecture)
  - [Retrieval methods](#retrieval-methods)
  - [RAG pipeline](#rag-pipeline)
- [Retrieval Evaluation](#retrieval-evaluation)
  - [Metrics](#metrics)
  - [Results](#results)
  - [Interpretation](#interpretation)
- [LLM Evaluation](#llm-evaluation)
  - [Evaluation approach](#evaluation-approach)
  - [Baseline vs strict grounding](#baseline-vs-strict-grounding)
  - [Evaluation notes](#evaluation-notes)
- [Interface](#interface)
- [Ingestion Pipeline](#ingestion-pipeline)
  - [Pipeline](#pipeline)
  - [Chunk design](#chunk-design)
- [Monitoring](#monitoring)
- [Containerization](#containerization)
- [Reproducibility & Setup](#reproducibility--setup)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [LLM Zoomcamp Evaluation Criteria](#llm-zoomcamp-evaluation-criteria)

---

# Problem Description

## The problem

Developers often need quick answers from large technical documentation. Searching manually through multiple pages interrupts development and makes it difficult to find the right information efficiently.

This project uses Retrieval-Augmented Generation (RAG) to retrieve relevant documentation chunks and generate answers grounded in the OpenAI API documentation.

## Target users

- Software developers
- API users
- Students learning the OpenAI API
- Engineers integrating LLMs into applications

## Why RAG?

A language model alone may not reliably answer questions about a specific documentation corpus.

RAG improves the workflow by:

- Retrieving relevant documentation sections
- Providing the retrieved content to the LLM as context
- Generating answers grounded in the retrieved documents

## Documentation corpus

The knowledge base consists of six Markdown documentation files:

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
- Lexical / keyword-based retrieval
- Used as a baseline for comparison

### Vector search

- Sentence Transformers
- Embedding-based semantic similarity
- Selected as the default retriever after evaluation

## RAG pipeline

1. Receive the user question.
2. Retrieve the top-k relevant chunks.
3. Build the prompt context.
4. Send the prompt and retrieved context to the OpenAI model.
5. Generate the final answer.

The current RAG configuration uses `TOP_K = 5`.

---

# Retrieval Evaluation

The retrieval layer was evaluated against a ground-truth dataset containing 30 developer questions and their expected document sections.

## Metrics

- **Hit@1** — whether the correct chunk is the first result.
- **Hit@3** — whether the correct chunk appears in the top 3.
- **Hit@5** — whether the correct chunk appears in the top 5.
- **MRR** — how highly the correct chunk is ranked on average.

## Results

| Method | Hit@1 | Hit@3 | Hit@5 | MRR |
| :--- | ---: | ---: | ---: | ---: |
| Text search | 0.500 | 0.667 | 0.700 | 0.579 |
| Vector search | **0.600** | **0.833** | **0.967** | **0.730** |

## Interpretation

Vector search outperformed text search across all four metrics and was selected as the default retriever.

- Hit@1 improved from **50.0% → 60.0%**.
- Hit@3 improved from **66.7% → 83.3%**.
- Hit@5 improved from **70.0% → 96.7%**.
- MRR improved from **0.579 → 0.730**.

The gap between Hit@1 and Hit@5 also shows that retrieval is strong, but the ranking of the top results can still be improved.

---

# LLM Evaluation

The final RAG output was evaluated using the same 30-question ground-truth dataset.

Each generated answer was evaluated for:

- Correctness
- Groundedness
- Hallucination
- Root cause
- Notes

The evaluation uses semantic judgment rather than requiring the generated answer to exactly match the expected answer.

## Baseline results

```text
Evaluated questions: 30/30
Average correctness:  4.67/5
Average groundedness: 4.67/5
Hallucination rate:   10.0%
```

## Baseline vs strict grounding

Two prompts were evaluated using the same 30 questions.

| Metric | Baseline | Strict grounding |
| :--- | ---: | ---: |
| Correctness | 4.67/5 | **4.77/5** |
| Groundedness | 4.67/5 | **4.77/5** |
| Hallucinations | 3/30 | **1/30** |
| Hallucination rate | 10.0% | **3.3%** |

The strict grounding prompt was selected because it:

- Improved correctness by **+0.10**
- Improved groundedness by **+0.10**
- Reduced hallucinations by **6.7 percentage points**

Evaluation results are stored in:

```text
results/rag_evaluation_strict_grounding.json
```

## Evaluation notes

Two examples from the evaluation demonstrate why semantic evaluation and root-cause analysis are more informative than exact answer matching.

**Q11 — Retrieval failure**

The expected `Function Calling > Common Use Cases` section was not retrieved in the top 5. The model therefore answered using related retrieved content. This was classified as a **retrieval failure**, rather than simply marking the generated answer as wrong.

**Q18 — Not a hallucination**

The answer correctly combined relevant information from both the Models and Embeddings documentation, even though it went beyond the exact expected answer. This was considered **not a hallucination**.

These cases show why evaluating correctness, groundedness, and root cause provides more useful information than exact answer matching alone.

---

# Interface

The application provides a Streamlit interface for interacting with the RAG system.

## Features

- Chat interface
- Source document panel
- Conversation history
- Response metadata
- Monitoring view
- User feedback

---

# Ingestion Pipeline

The ingestion pipeline automatically transforms the raw Markdown documentation into structured, retrieval-ready chunks.

## Pipeline

```text
Markdown documents
        │
        ▼
YAML front matter
        │
        ▼
Metadata extraction
        │
        ▼
Header-based chunking
        │
        ▼
Metadata-rich chunks
        │
        ▼
processed_chunks.json
        │
        ▼
Embedding generation
        │
        ▼
chunks_with_embeddings.json
```

## Features

- Automated ingestion with `ingest.py`
- YAML front matter parsing with `python-frontmatter`
- Markdown header-based chunking
- Preservation of H1/H2/H3 section hierarchy
- Deterministic chunk IDs
- Metadata preservation
- Enriched `embedding_text`
- JSON output for the next pipeline stage

The ingestion stage produces `processed_chunks.json`, which is then consumed by the embedding stage.

---

# Monitoring

The project includes application logging and a Grafana monitoring dashboard backed by PostgreSQL.

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

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/828e0b42-f26b-467e-82c7-e65b92e2b9c2"
    width="85%"
    alt="Grafana Monitoring Dashboard"
  />
</p>

---

# Containerization

Docker Compose is used for the monitoring dependencies:

- PostgreSQL 17
- Grafana

Start the services with:

```bash
docker compose up -d
```

The application itself can be run locally with `uv`.

Grafana is available at:

```text
http://localhost:3000
```

PostgreSQL is exposed on:

```text
localhost:5432
```

Default local development credentials are defined in `docker-compose.yml`.

---

# Reproducibility & Setup

The project is designed to be reproducible from a fresh clone.

## Requirements

- Python 3.12
- Docker and Docker Compose
- OpenAI API key
- `uv`

Python dependencies are declared in `pyproject.toml` and resolved versions are captured in `uv.lock`.

## Dataset

The evaluation dataset is included in the repository:

```text
ground_truth.csv
```

It contains the evaluation questions, reference documents/sections, and expected answers used for retrieval and RAG evaluation.

The documentation corpus is also included under:

```text
data/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/mariahellocode26/DevDocs-AI-RAG-Chat.git
cd DevDocs-AI-RAG-Chat
```

Install the Python dependencies:

```bash
uv sync
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

## Start PostgreSQL and Grafana

```bash
docker compose up -d
```

Initialize the monitoring database:

```bash
psql -U postgres -d devdocs -f monitoring/schema.sql
```

If PostgreSQL is running inside Docker and `psql` is not installed locally, the schema can also be applied from the container.

## Generate the processed chunks and embeddings

Run the ingestion pipeline:

```bash
uv run python ingest.py
```

Generate embeddings:

```bash
uv run python embed.py
```

This produces:

```text
processed_chunks.json
chunks_with_embeddings.json
```

## Run the Streamlit application

```bash
uv run streamlit run app.py
```

The application can then be opened in the browser at the local Streamlit URL shown in the terminal.

## Run retrieval evaluation

Evaluate text and vector search:

```bash
uv run python evaluate_retrieval.py
```

Results are saved to:

```text
results/retrieval_results.csv
```

## Run RAG evaluation

Generate the 30 RAG answers:

```bash
uv run python run_rag_eval.py
```

The generated answers are saved to:

```text
results/rag_evaluation.csv
```

The answers are then scored for correctness, groundedness, hallucination, and root cause.

## Run strict grounding evaluation

Generate the same evaluation using the strict grounding prompt:

```bash
uv run python run_rag_eval_strict.py
```

The results are saved to:

```text
results/rag_evaluation_strict_grounding.json
```

The repository also contains the evaluation analysis scripts:

```text
compute_rag_metrics.py
analyze_prompt_evaluation.py
analyze_failures.py
```

---

# Project Structure

```text
DevDocs-AI-RAG-Chat
├── README.md
├── app.py
├── main.py
├── rag.py
├── ingest.py
├── embed.py
├── text_search.py
├── vector_search.py
├── evaluate_retrieval.py
├── run_rag_eval.py
├── run_rag_eval_strict.py
├── compute_rag_metrics.py
├── analyze_prompt_evaluation.py
├── analyze_failures.py
├── run_pipeline.py
│
├── data/
│   ├── authentication.md
│   ├── embeddings.md
│   ├── function-calling.md
│   ├── models.md
│   ├── responses-api.md
│   └── streaming.md
│
├── components/
├── monitoring/
├── grafana/
├── styles/
├── utils/
├── results/
│
├── ground_truth.csv
├── processed_chunks.json
├── chunks_with_embeddings.json
├── pyproject.toml
├── uv.lock
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
- LangChain Text Splitters
- PostgreSQL
- Grafana
- Docker Compose
- uv
- Markdown

---

# LLM Zoomcamp Evaluation Criteria

The project is evaluated against the LLM Zoomcamp criteria. The table below shows the score and the evidence implemented in the project.

| Criterion | Score | Evidence in this project |
| :--- | :---: | :--- |
| **Problem description** | **2/2** | The README clearly describes the developer documentation search problem, identifies the target users, and explains why RAG is useful for grounding answers in the documentation. |
| **Retrieval flow** | **2/2** | The project uses a documentation knowledge base, text/vector retrieval, prompt construction, and an OpenAI model. The flow is implemented across `ingest.py`, `embed.py`, `text_search.py`, `vector_search.py`, and `rag.py`. |
| **Retrieval evaluation** | **2/2** | `evaluate_retrieval.py` evaluates both MinSearch text retrieval and Sentence Transformers vector search using Hit@1, Hit@3, Hit@5, and MRR. Vector search performed better and was selected as the default retriever. |
| **LLM evaluation** | **2/2** | `run_rag_eval.py` evaluates the baseline prompt and `run_rag_eval_strict.py` evaluates the strict-grounding prompt. The strict prompt improved correctness and groundedness from 4.67/5 to 4.77/5 and reduced hallucinations from 10.0% to 3.3%. |
| **Interface** | **2/2** | `app.py` provides a Streamlit web UI with chat, source documents, response metadata, conversation history, feedback, and monitoring views. |
| **Ingestion pipeline** | **2/2** | `ingest.py` automatically loads the six Markdown files, parses YAML front matter, chunks documents by Markdown headers, preserves metadata and section hierarchy, generates deterministic IDs, and writes `processed_chunks.json`. |
| **Monitoring** | **2/2** | The `monitoring/` package provides logging, database, and analytics functionality. `grafana/dashboard.json` provides a dashboard with 6 charts covering requests, latency, cost, token usage, request volume, and retrieved documents. User feedback is also collected by the application. |
| **Containerization** | **1/2** | `docker-compose.yml` containerizes PostgreSQL 17 and Grafana. The Streamlit application is currently run locally with `uv`, so the complete application stack is not yet containerized. |
| **Reproducibility** | **2/2** | `ground_truth.csv` and the documentation corpus are included in the repository. `pyproject.toml` defines the dependencies and `uv.lock` records resolved versions. The repository includes scripts for ingestion, embedding generation, retrieval evaluation, and RAG evaluation. |
| **Hybrid search** | **0/1** | Text search and vector search were both implemented and evaluated, but they are evaluated as separate retrieval approaches rather than being combined into a hybrid retriever. |
| **Document re-ranking** | **0/1** | The retrieved chunks are ranked by the underlying text or vector retrieval method. No separate second-stage reranker is currently implemented. |
| **User query rewriting** | **0/1** | User questions are sent directly to the retrieval layer. There is currently no separate query rewriting or query expansion step. |

# Status

The project is complete as an LLM Zoomcamp final project, with the main RAG pipeline, retrieval evaluation, LLM evaluation, Streamlit interface, logging, and monitoring implemented.
