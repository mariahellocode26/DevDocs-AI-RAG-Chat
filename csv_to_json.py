import pandas as pd
import json


INPUT_FILE = "results/rag_evaluation.csv"
OUTPUT_FILE = "results/rag_evaluation.json"


df = pd.read_csv(INPUT_FILE)

records = df.to_dict(orient="records")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        records,
        f,
        indent=4,
        ensure_ascii=False,
    )

print(f"Saved {len(records)} rows to {OUTPUT_FILE}")