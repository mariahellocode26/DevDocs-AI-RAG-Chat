"""
evaluation_retrieval.py

Evaluate:

1. Text Search
2. Vector Search

Metrics:

- Hit@1
- Hit@3
- Hit@5
- MRR

It also saves all results to results/retrieval_results.csv
"""

import pandas as pd

from text_search import search as text_search
from vector_search import search as vector_search


GROUND_TRUTH = "ground_truth.csv"
TOP_K = 5


# ============================================================
# Matching
# ============================================================


def chunk_match(chunk, row):

    if chunk["filename"] != row["reference_document"]:
        return False

    checks = [
        ("reference_h1", "header1"),
        ("reference_h2", "header2"),
        ("reference_h3", "header3"),
    ]

    for ref_col, header_col in checks:

        expected = row[ref_col]

        actual = chunk.get(header_col)

        if pd.isna(expected) or expected == "":
            continue

        if expected != actual:
            return False

    return True


# ============================================================
# Metrics
# ============================================================


def hit_at_k(results, row, k):

    for chunk in results[:k]:

        if chunk_match(chunk, row):
            return 1

    return 0


def mrr(results, row):

    for rank, chunk in enumerate(results, start=1):

        if chunk_match(chunk, row):
            return 1 / rank

    return 0


def build_path(chunk):

    headers = [
        chunk.get("header1"),
        chunk.get("header2"),
        chunk.get("header3"),
    ]

    headers = [h for h in headers if h]

    return " > ".join(headers)


# ============================================================
# Evaluation
# ============================================================


def evaluate(search_fn, name, df):

    rows = []

    h1 = 0
    h3 = 0
    h5 = 0
    total_mrr = 0

    print(f"\n{'=' * 60}")
    print(name.upper())
    print(f"{'=' * 60}")

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        question = row["question"]

        print(f"[{i}/{len(df)}] {question}")

        results = search_fn(
            query=question,
            top_k=TOP_K,
        )

        hit1 = hit_at_k(results, row, 1)
        hit3_value = hit_at_k(results, row, 3)
        hit5_value = hit_at_k(results, row, 5)

        rr = mrr(results, row)

        h1 += hit1
        h3 += hit3_value
        h5 += hit5_value
        total_mrr += rr

        rows.append(
            {
                "question": question,
                "expected_path": row["reference_path"],
                "top_1": build_path(results[0]) if len(results) > 0 else "",
                "top_2": build_path(results[1]) if len(results) > 1 else "",
                "top_3": build_path(results[2]) if len(results) > 2 else "",
                "top_4": build_path(results[3]) if len(results) > 3 else "",
                "top_5": build_path(results[4]) if len(results) > 4 else "",
                "hit@1": hit1,
                "hit@3": hit3_value,
                "hit@5": hit5_value,
                "mrr": rr,
                "method": name,
            }
        )

    n = len(df)

    metrics = {
        "method": name,
        "hit@1": h1 / n,
        "hit@3": h3 / n,
        "hit@5": h5 / n,
        "mrr": total_mrr / n,
    }

    return metrics, rows


# ============================================================
# Main
# ============================================================


def main():

    df = pd.read_csv(GROUND_TRUTH)

    text_metrics, text_rows = evaluate(
        text_search,
        "text",
        df,
    )

    vector_metrics, vector_rows = evaluate(
        vector_search,
        "vector",
        df,
    )

    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    for metrics in [text_metrics, vector_metrics]:

        print(f"\n{metrics['method'].upper()}")

        print(f"Hit@1: {metrics['hit@1']:.3f}")
        print(f"Hit@3: {metrics['hit@3']:.3f}")
        print(f"Hit@5: {metrics['hit@5']:.3f}")
        print(f"MRR:   {metrics['mrr']:.3f}")

    results = pd.DataFrame(text_rows + vector_rows)

    results.to_csv(
        "results/retrieval_results.csv",
        index=False,
    )

    print(
        "\nSaved results to "
        "results/retrieval_results.csv"
    )


if __name__ == "__main__":
    main()