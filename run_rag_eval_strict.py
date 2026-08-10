import json
import time
from pathlib import Path

import pandas as pd
import rag


GROUND_TRUTH = "ground_truth.csv"
OUTPUT_FILE = "results/rag_evaluation_strict_grounding.json"

PROMPT_NAME = "strict_grounding"

REQUEST_DELAY = 6  # ~10 requests/minute


def main():

    df = pd.read_csv(GROUND_TRUTH)

    rows = []

    # Make sure the results directory exists
    Path("results").mkdir(exist_ok=True)

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        question = row["question"]

        print(f"[{i}/{len(df)}] {question}")

        try:

            result = rag.rag(
                question,
                prompt_name=PROMPT_NAME,
            )

            rows.append(
                {
                    "id": row["id"],
                    "question": question,
                    "reference_path": row["reference_path"],
                    "expected_answer": row["expected_answer"],
                    "generated_answer": result["answer"],

                    # Fill manually after evaluation
                    "correctness": "",
                    "groundedness": "",
                    "hallucination": "",
                    "root_cause": "",
                    "notes": "",
                }
            )

            # Save after every question
            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    rows,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print("  ✓ Saved")

        except Exception as e:

            print(f"  ERROR: {e}")

            # Save whatever has already completed
            with open(
                OUTPUT_FILE,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    rows,
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            print(
                f"  Progress saved: "
                f"{len(rows)}/{len(df)}"
            )

            raise

        # Keep under the 10 RPM limit
        if i < len(df):
            time.sleep(REQUEST_DELAY)

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE")
    print("=" * 60)
    print(f"Prompt: {PROMPT_NAME}")
    print(f"Questions: {len(rows)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()