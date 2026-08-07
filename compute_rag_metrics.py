import json
import pandas as pd


FILE = "results/rag_evaluation.json"


# ---------------------------
# Load JSON
# ---------------------------

with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)


# ---------------------------
# Numeric scores
# ---------------------------

correctness_avg = pd.to_numeric(
    df["correctness"],
    errors="coerce"
).mean()

groundedness_avg = pd.to_numeric(
    df["groundedness"],
    errors="coerce"
).mean()


# ---------------------------
# Hallucination rate
# ---------------------------

hallucination_rate = (
    df["hallucination"]
    .fillna("")
    .str.lower()
    .eq("yes")
    .mean()
    * 100
)


# ---------------------------
# Count evaluated questions
# ---------------------------

evaluated_questions = (
    pd.to_numeric(
        df["correctness"],
        errors="coerce"
    )
    .notna()
    .sum()
)


# ---------------------------
# Print results
# ---------------------------

print("=" * 50)
print("END-TO-END RAG EVALUATION")
print("=" * 50)

print(f"\nEvaluated questions: {evaluated_questions}/{len(df)}")

print(
    f"Average correctness: "
    f"{correctness_avg:.2f}/5"
)

print(
    f"Average groundedness: "
    f"{groundedness_avg:.2f}/5"
)

print(
    f"Hallucination rate: "
    f"{hallucination_rate:.1f}%"
)