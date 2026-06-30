import json
import re
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

import config

load_dotenv()

client = OpenAI()


def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_jsonl(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def word_count(chat):
    text = " ".join(
        msg["content"]
        for msg in chat["messages"]
        if msg["role"] != "system"
    )
    return len(text.split())


def call_llm(prompt):
    response = client.responses.create(
        model=config.MODEL_NAME,
        input=prompt,
        
    )
    return response.output_text.strip()


def save_report(report, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)


def parse_json_response(response):
    response = response.strip()

    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()

    return json.loads(response)