import json


BASELINE_FILE = "results/rag_evaluation.json"
STRICT_FILE = "results/rag_evaluation_strict_grounding.json"


def load_results(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_metrics(results):
    # Only include questions that have been manually evaluated
    evaluated = [
        row
        for row in results
        if row.get("correctness") not in ("", None)
        and row.get("groundedness") not in ("", None)
        and row.get("hallucination") not in ("", None)
    ]

    if not evaluated:
        return None

    correctness = [
        float(row["correctness"])
        for row in evaluated
    ]

    groundedness = [
        float(row["groundedness"])
        for row in evaluated
    ]

    hallucinations = [
        row
        for row in evaluated
        if str(row["hallucination"]).strip().lower() == "yes"
    ]

    return {
        "total_questions": len(results),
        "evaluated_questions": len(evaluated),
        "avg_correctness": sum(correctness) / len(correctness),
        "avg_groundedness": sum(groundedness) / len(groundedness),
        "hallucinations": len(hallucinations),
        "hallucination_rate": (
            len(hallucinations) / len(evaluated) * 100
        ),
    }


def print_metrics(name, metrics):

    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    if metrics is None:
        print("No evaluated results found.")
        return

    print(
        f"Evaluated questions: "
        f"{metrics['evaluated_questions']}/"
        f"{metrics['total_questions']}"
    )

    print(
        f"Average correctness:  "
        f"{metrics['avg_correctness']:.2f}/5"
    )

    print(
        f"Average groundedness: "
        f"{metrics['avg_groundedness']:.2f}/5"
    )

    print(
        f"Hallucinations:       "
        f"{metrics['hallucinations']}/"
        f"{metrics['evaluated_questions']}"
    )

    print(
        f"Hallucination rate:   "
        f"{metrics['hallucination_rate']:.1f}%"
    )


def main():

    baseline_results = load_results(BASELINE_FILE)
    strict_results = load_results(STRICT_FILE)

    baseline = calculate_metrics(baseline_results)
    strict = calculate_metrics(strict_results)

    print_metrics(
        "BASELINE PROMPT",
        baseline,
    )

    print_metrics(
        "STRICT GROUNDING PROMPT",
        strict,
    )

    # --------------------------------------------------------
    # Comparison
    # --------------------------------------------------------

    if baseline and strict:

        print("\n" + "=" * 60)
        print("PROMPT COMPARISON")
        print("=" * 60)

        correctness_diff = (
            strict["avg_correctness"]
            - baseline["avg_correctness"]
        )

        groundedness_diff = (
            strict["avg_groundedness"]
            - baseline["avg_groundedness"]
        )

        hallucination_diff = (
            strict["hallucination_rate"]
            - baseline["hallucination_rate"]
        )

        print(
            f"Correctness change:   "
            f"{correctness_diff:+.2f}"
        )

        print(
            f"Groundedness change:  "
            f"{groundedness_diff:+.2f}"
        )

        print(
            f"Hallucination change: "
            f"{hallucination_diff:+.1f}%"
        )

        print("\nSummary:")

        if correctness_diff > 0:
            print("✓ Strict grounding improved correctness.")
        elif correctness_diff < 0:
            print("✗ Strict grounding reduced correctness.")
        else:
            print("= Correctness was unchanged.")

        if groundedness_diff > 0:
            print("✓ Strict grounding improved groundedness.")
        elif groundedness_diff < 0:
            print("✗ Strict grounding reduced groundedness.")
        else:
            print("= Groundedness was unchanged.")

        if hallucination_diff < 0:
            print("✓ Strict grounding reduced hallucinations.")
        elif hallucination_diff > 0:
            print("✗ Strict grounding increased hallucinations.")
        else:
            print("= Hallucination rate was unchanged.")


if __name__ == "__main__":
    main()