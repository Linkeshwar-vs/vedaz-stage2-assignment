import json
import pandas as pd

from config import TEST_FILE
from config import EVALUATION_REPORT
from prompts import (
    ASSISTANT_PROMPT,
    EVALUATION_PROMPT,
)
from utils import (
    load_jsonl,
    call_llm,
    parse_json_response,
)

def generate_response(question):
    prompt = f"""
{ASSISTANT_PROMPT}

User:
{question}
"""

    return call_llm(prompt)

def judge_response(question, response):
    prompt = f"""
{EVALUATION_PROMPT}

User Question:
{question}

Assistant Response:
{response}
"""

    return parse_json_response(call_llm(prompt))

def main():
    chats = load_jsonl(TEST_FILE)

    results = []

    for chat in chats:
        question = next(
            msg["content"]
            for msg in chat["messages"]
            if msg["role"] == "user"
        )

        response = generate_response(question)

        scores = judge_response(question, response)

        results.append({
            "question": question,
            "response": response,
            **scores
        })

    df = pd.DataFrame(results)

    print(df)

    df.to_csv(EVALUATION_REPORT, index=False)


if __name__ == "__main__":
    main()