'''
Since vector Hit@5 is 0.967, there should be exactly one failed question (30 × 0.033 ≈ 1). 
That question is the one worth investigating.
'''

import pandas as pd

results = pd.read_csv(
    "results/retrieval_results.csv"
)

failed = results[
    (results["method"] == "vector")
    & (results["hit@5"] == 0)
]

print(
    failed[
        [
            "question",
            "expected_path",
            "top_1",
            "top_2",
            "top_3",
            "top_4",
            "top_5",
        ]
    ].to_string(index=False)
)



'''
This is the output of the above code:

python analyze_failures.py
                                               question                       expected_path                       top_1                      top_2                             top_3                               top_4                         top_5
What kinds of tasks can function calling help automate? Function Calling > Common Use Cases Function Calling > Overview Function Calling > Summary Function Calling > Best Practices Function Calling > Example Workflow Function Calling > Basic Flow
'''