import json
import pandas as pd

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT, "scripts"))

from evaluator import judge_response


def load_tests(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    TEST_FILE = os.path.join(
        ROOT,
        "tests",
        "evaluator_tests",
        "test_data",
        "evaluation_test.json",
    )

    tests = load_tests(TEST_FILE)

    results = []

    for test in tests:

        good_scores = judge_response(
            test["question"],
            test["good_response"]
        )

        bad_scores = judge_response(
            test["question"],
            test["bad_response"]
        )

        results.append({
            "type": "GOOD",
            "question": test["question"],
            **good_scores
        })

        results.append({
            "type": "BAD",
            "question": test["question"],
            **bad_scores
        })

    df = pd.DataFrame(results)

    print("\nEvaluation Results\n")
    print(df.to_string(index=False))

    OUTPUT_FILE = os.path.join(
        ROOT,
        "tests",
        "evaluator_tests",
        "outputs",
        "evaluation_results.csv",
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nResults saved to tests/evaluator_tests/outputs/evaluation_results.csv")


if __name__ == "__main__":
    main()