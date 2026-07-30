# evaluation/run_pipeline.py
import time
import sys
import argparse
import csv
import json
import time
import traceback
from collections import deque
from pathlib import Path

import text_search
import vector_search
import rag as rag_module


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================
# Configuration
# ============================================================

GROUND_TRUTH_FILE = Path(__file__).parent / "ground_truth.csv"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_FILE = RESULTS_DIR / "raw_runs.json"

DEFAULT_TOP_K = 5

# OpenAI limit for your free account
TPM_LIMIT = 100_000
WINDOW_SECONDS = 60


# ============================================================
# TPM Limiter
# ============================================================

token_window = deque()


def throttle_tpm(estimated_tokens: int):
    """
    Ensure we do not exceed the TPM limit.
    Uses a rolling 60-second window.
    """

    now = time.time()

    # Remove expired entries
    while token_window and now - token_window[0][0] > WINDOW_SECONDS:
        token_window.popleft()

    used_last_minute = sum(tokens for _, tokens in token_window)

    if used_last_minute + estimated_tokens <= TPM_LIMIT:
        return

    # Wait until enough tokens expire
    while token_window:
        oldest_time, _ = token_window[0]

        sleep_time = WINDOW_SECONDS - (now - oldest_time)

        if sleep_time > 0:
            print(f"TPM limit reached. Sleeping {sleep_time:.1f}s...")
            time.sleep(sleep_time)

        now = time.time()

        while token_window and now - token_window[0][0] > WINDOW_SECONDS:
            token_window.popleft()

        used_last_minute = sum(tokens for _, tokens in token_window)

        if used_last_minute + estimated_tokens <= TPM_LIMIT:
            return


# ============================================================
# Helpers
# ============================================================

def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_rank(retrieved_chunks, reference_document, reference_section):
    """
    Return the 1-indexed rank of the first chunk matching
    both document and section.
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
    Remove raw embedding vectors from results to keep
    raw_runs.json small.
    """

    cleaned = []

    for chunk in chunks:
        chunk = dict(chunk)
        chunk.pop("embedding", None)
        cleaned.append(chunk)

    return cleaned


# ============================================================
# Per-question run
# ============================================================

def run_one(row, top_k):
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

    # -----------------------------
    # Text search
    # -----------------------------
    try:
        text_results = text_search.search(query=question, top_k=top_k)

        result["text_search"] = {
            "results": text_results,
            "correct_rank": find_rank(
                text_results,
                reference_document,
                reference_section,
            ),
        }

    except Exception as e:
        result["text_search"] = {
            "results": [],
            "correct_rank": None,
        }

        result["error"] = (
            f"text_search failed: {e}\\n{traceback.format_exc()}"
        )

    # -----------------------------
    # Vector search
    # -----------------------------
    try:
        vector_results = vector_search.search(
            query=question,
            top_k=top_k,
        )

        vector_results = strip_embeddings(vector_results)

        result["vector_search"] = {
            "results": vector_results,
            "correct_rank": find_rank(
                vector_results,
                reference_document,
                reference_section,
            ),
        }

    except Exception as e:
        result["vector_search"] = {
            "results": [],
            "correct_rank": None,
        }

        result["error"] = (
            f"vector_search failed: {e}\\n{traceback.format_exc()}"
        )

    # -----------------------------
    # Full RAG pipeline
    # -----------------------------
    try:
        # Conservative estimate before the request
        throttle_tpm(3000)

        start = time.perf_counter()

        rag_output = rag_module.rag(question)
        time.sleep(6.5)

        latency = time.perf_counter() - start

        usage = rag_output.get("usage", {})

        actual_tokens = usage.get("total_tokens", 0)

        # Record real token usage
        token_window.append((time.time(), actual_tokens))

        sources = strip_embeddings(
            rag_output.get("sources", [])
        )

        result["rag"] = {
            "answer": rag_output.get("answer"),
            "model": rag_output.get("model"),
            "top_k": rag_output.get("top_k"),
            "sources": sources,
            "correct_rank": find_rank(
                sources,
                reference_document,
                reference_section,
            ),
            "latency_seconds": round(latency, 3),
            "usage": usage,
            "cost_usd": rag_output.get("cost_usd", 0.0),
        }

    except Exception as e:
        result["rag"] = {
            "answer": None,
            "sources": [],
            "correct_rank": None,
            "latency_seconds": None,
            "usage": {},
            "cost_usd": 0.0,
        }

        result["error"] = (
            f"rag failed: {e}\\n{traceback.format_exc()}"
        )

    return result


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Run ground_truth.csv through the RAG pipeline."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only run the first N questions.",
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Number of chunks to retrieve (default: {DEFAULT_TOP_K}).",
    )

    args = parser.parse_args()

    ground_truth = load_ground_truth(GROUND_TRUTH_FILE)

    if args.limit:
        ground_truth = ground_truth[: args.limit]

    print(f"Running {len(ground_truth)} questions (top_k={args.top_k})...\\n")

    results = []

    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0

    for i, row in enumerate(ground_truth, start=1):

        print(f"[{i}/{len(ground_truth)}] {row['question'][:70]}...")

        result = run_one(row, top_k=args.top_k)

        results.append(result)

        rag_result = result.get("rag", {})

        usage = rag_result.get("usage", {})

        total_input_tokens += usage.get("input_tokens", 0)
        total_output_tokens += usage.get("output_tokens", 0)
        total_cost += rag_result.get("cost_usd", 0.0)

        if result["error"]:
            print(f"    ERROR: {result['error'].splitlines()[0]}")

        else:
            print(
                f"    {usage.get('total_tokens', 0)} tokens | "
                f"${rag_result.get('cost_usd', 0.0):.4f} | "
                f"{rag_result.get('latency_seconds')}s"
            )

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    n_errors = sum(1 for r in results if r["error"])

    print("\\n" + "=" * 60)
    print("Evaluation Summary")
    print("=" * 60)

    print(f"Questions:      {len(results)}")
    print(f"Input tokens:   {total_input_tokens:,}")
    print(f"Output tokens:  {total_output_tokens:,}")
    print(f"Total tokens:   {total_input_tokens + total_output_tokens:,}")
    print(f"Total cost:     ${total_cost:.4f}")
    print(f"Results file:   {RESULTS_FILE}")

    if n_errors:
        print(f"Errors:         {n_errors}")


if __name__ == "__main__":
    main()