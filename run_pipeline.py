"""
run_pipeline.py

Runs every question in ground_truth.csv through:
    - text_search.search()      (lexical / MinSearch retrieval)
    - vector_search.search()    (semantic retrieval)
    - rag.rag()                 (full retrieval + generation pipeline)

and saves the raw, unscored outputs to results/raw_runs.json.

Scoring (hit rate, MRR, LLM-as-judge, etc.) happens later in
evaluate_retrieval.py / evaluate_generation.py, reading this file.
Kept separate so we don't have to re-run the (slow, costly) actual
RAG calls every time we tweak a metric formula.

IMPORTANT:
    text_search.py and vector_search.py load processed_chunks.json /
    chunks_with_embeddings.json from the CURRENT WORKING DIRECTORY at
    import time. Run this script from the directory containing those
    two files, e.g.:

        cd /path/to/project
        python evaluation/run_pipeline.py

Usage:
    python run_pipeline.py
    python run_pipeline.py --limit 5          # quick smoke test
    python run_pipeline.py --top-k 3
    python run_pipeline.py --delay 5          # slower, for free-tier accounts

Rate limits:
    Free-tier / newly created OpenAI accounts have low requests-per-minute
    limits (check yours at platform.openai.com -> Settings -> Limits).
    This script waits --delay seconds before every LLM call, and on a 429
    rate-limit error retries automatically with exponential backoff
    (up to MAX_RETRIES attempts) instead of crashing the run.
"""

import argparse
import csv
import json
import time
import traceback
from pathlib import Path

import openai

# These imports build the search indexes immediately (they load the
# processed_chunks.json / chunks_with_embeddings.json files and print
# "Loading...", "Building index...", etc. to stdout). That's expected.
import text_search
import vector_search
import rag as rag_module


# ============================================================
# Configuration
# ============================================================

GROUND_TRUTH_FILE = Path(__file__).parent / "ground_truth.csv"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_FILE = RESULTS_DIR / "raw_runs.json"

DEFAULT_TOP_K = 5

# Free-tier / low-tier OpenAI accounts have low requests-per-minute
# limits. A fixed delay between LLM calls plus retry-with-backoff on
# 429s keeps this script from failing a run just because it went too
# fast. Tune --delay to whatever your account's dashboard shows
# (platform.openai.com -> Settings -> Limits).
DEFAULT_DELAY_SECONDS = 3.0
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 5.0


# ============================================================
# Helpers
# ============================================================

def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_rank(retrieved_chunks, reference_document, reference_section):
    """
    Return the 1-indexed rank of the first chunk that matches both
    the reference document and reference section, or None if no
    match is found in the retrieved list.

    A chunk matches if:
        chunk["filename"] == reference_document
        AND reference_section is (case-insensitively) equal to
            chunk["header1"], chunk["header2"], or chunk["header3"]
    """

    target_doc = reference_document.strip().lower()
    target_section = reference_section.strip().lower()

    for rank, chunk in enumerate(retrieved_chunks, start=1):

        if chunk.get("filename", "").strip().lower() != target_doc:
            continue

        headers = [
            chunk.get("header1"),
            chunk.get("header2"),
            chunk.get("header3"),
        ]

        headers = [h.strip().lower() for h in headers if h]

        if target_section in headers:
            return rank

    return None


def strip_embeddings(chunks):
    """
    vector_search results include a raw embedding vector per chunk.
    We don't want that bloating raw_runs.json - drop it, keep the score.
    """

    cleaned = []

    for chunk in chunks:
        chunk = dict(chunk)
        chunk.pop("embedding", None)
        cleaned.append(chunk)

    return cleaned


def call_rag_with_backoff(question):
    """
    Call rag_module.rag(question), retrying with exponential backoff
    if OpenAI returns a rate-limit (429) error. Raises after
    MAX_RETRIES failed attempts.
    """

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return rag_module.rag(question)

        except openai.RateLimitError:
            if attempt == MAX_RETRIES:
                raise

            wait = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
            print(f"    -> Rate limited (attempt {attempt}/{MAX_RETRIES}), "
                  f"waiting {wait:.0f}s...")
            time.sleep(wait)


# ============================================================
# Per-question run
# ============================================================

def run_one(row, top_k, delay_seconds):
    """
    Run a single ground truth question through both retrievers and
    the full RAG pipeline. Returns a result dict. Never raises -
    errors are captured in the result so one bad question doesn't
    kill the whole batch.

    delay_seconds is applied before the LLM call (not before the
    local text/vector search calls, which don't hit any external
    rate limit).
    """

    question = row["question"]
    reference_document = row["reference_document"]
    reference_section = row["reference_section"]

    result = {
        "id": row["id"],
        "question": question,
        "reference_document": reference_document,
        "reference_section": reference_section,
        "expected_answer": row["expected_answer"],
        "error": None,
    }

    # --- Text search ---
    try:
        text_results = text_search.search(query=question, top_k=top_k)
        result["text_search"] = {
            "results": text_results,
            "correct_rank": find_rank(
                text_results, reference_document, reference_section
            ),
        }
    except Exception as e:
        result["text_search"] = {"results": [], "correct_rank": None}
        result["error"] = f"text_search failed: {e}\n{traceback.format_exc()}"

    # --- Vector search ---
    try:
        vector_results = vector_search.search(query=question, top_k=top_k)
        vector_results = strip_embeddings(vector_results)
        result["vector_search"] = {
            "results": vector_results,
            "correct_rank": find_rank(
                vector_results, reference_document, reference_section
            ),
        }
    except Exception as e:
        result["vector_search"] = {"results": [], "correct_rank": None}
        result["error"] = f"vector_search failed: {e}\n{traceback.format_exc()}"

    # --- Full RAG pipeline (retrieval + generation) ---
    try:
        time.sleep(delay_seconds)

        start = time.perf_counter()
        rag_output = call_rag_with_backoff(question)
        latency = time.perf_counter() - start

        sources = strip_embeddings(rag_output.get("sources", []))

        result["rag"] = {
            "answer": rag_output.get("answer"),
            "model": rag_output.get("model"),
            "top_k": rag_output.get("top_k"),
            "sources": sources,
            "correct_rank": find_rank(
                sources, reference_document, reference_section
            ),
            "latency_seconds": latency,
        }
    except Exception as e:
        result["rag"] = {
            "answer": None,
            "sources": [],
            "correct_rank": None,
            "latency_seconds": None,
        }
        result["error"] = f"rag failed: {e}\n{traceback.format_exc()}"

    return result


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Run ground_truth.csv questions through the RAG pipeline."
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only run the first N questions (useful for a quick smoke test)."
    )
    parser.add_argument(
        "--top-k", type=int, default=DEFAULT_TOP_K,
        help=f"Number of chunks to retrieve per question (default: {DEFAULT_TOP_K})."
    )
    parser.add_argument(
        "--delay", type=float, default=DEFAULT_DELAY_SECONDS,
        help=f"Seconds to wait before each LLM call, to stay under free-tier "
             f"rate limits (default: {DEFAULT_DELAY_SECONDS})."
    )
    args = parser.parse_args()

    ground_truth = load_ground_truth(GROUND_TRUTH_FILE)

    if args.limit:
        ground_truth = ground_truth[: args.limit]

    print(f"Running {len(ground_truth)} questions "
          f"(top_k={args.top_k}, delay={args.delay}s between LLM calls)...\n")

    results = []

    for i, row in enumerate(ground_truth, start=1):
        print(f"[{i}/{len(ground_truth)}] {row['question'][:70]}...")

        result = run_one(row, top_k=args.top_k, delay_seconds=args.delay)
        results.append(result)

        if result["error"]:
            print(f"    -> ERROR: {result['error'].splitlines()[0]}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    n_errors = sum(1 for r in results if r["error"])
    print(f"\nDone. Saved {len(results)} results to {RESULTS_FILE}")
    if n_errors:
        print(f"({n_errors} question(s) had errors - check the 'error' field)")


if __name__ == "__main__":
    main()
