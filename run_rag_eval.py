import pandas as pd
import rag
import time


GROUND_TRUTH = "ground_truth.csv"


def main():

    df = pd.read_csv(GROUND_TRUTH)

    rows = []

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        question = row["question"]

        print(f"[{i}/{len(df)}] {question}")

        result = rag.rag(question)
        time.sleep(6) # To keep it under 10 requests per minute limit

        rows.append(

            {
                "id": row["id"],
                "question": question,
                "reference_path": row["reference_path"],
                "expected_answer": row["expected_answer"],
                "generated_answer": result["answer"],

                # fill manually after running the script
                "correctness": "",
                "groundedness": "",
                "hallucination": "",
                "root_cause": "",
                "notes": "",
            }

        )
        pd.DataFrame(rows).to_csv(
            "results/rag_evaluation.csv",
            index=False,
        )

    output = pd.DataFrame(rows)

    output.to_csv(

        "results/rag_evaluation.csv",

        index=False,
    )

    print("\nSaved to results/rag_evaluation.csv")


if __name__ == "__main__":

    main()