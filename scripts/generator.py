import json

from prompts import GENERATOR_PROMPT
from utils import call_llm, parse_json_response

from checker import (
    validate_structure,
    rule_based_safety,
    llm_safety,
)

from config import GENERATED_FILE
from utils import save_jsonl, load_jsonl

def generate_chat(topic):
    prompt = GENERATOR_PROMPT + f"\n\nTopic: {topic}"

    response = call_llm(prompt)

    print("RAW RESPONSE:")
    print(repr(response))
    print("----------------")

    return parse_json_response(response)

def validate_generated_chat(chat):
    valid, reason = validate_structure(chat)
    if not valid:
        return False, reason

    safe, violations = rule_based_safety(chat)
    if not safe:
        return False, f"Rule violations: {violations}"

    safe, violations = llm_safety(chat)
    if not safe:
        return False, f"LLM violations: {violations}"

    return True, ""

def save_generated_chat(chat):
    try:
        chats = load_jsonl(GENERATED_FILE)
    except FileNotFoundError:
        chats = []

    chats.append(chat)
    save_jsonl(chats, GENERATED_FILE)

def main():
    topics = [
        "Career delay, Hindi",
        "Marriage compatibility, English",
        "Business loss, English",
        "Education stress, Hindi",
        "Job change, English",
        "Financial uncertainty, Hindi",
        "Love marriage, English",
        "Family conflicts, Hindi",
        "Foreign travel, English",
        "Health anxiety, Hindi",
    ]

    accepted = 0

    for topic in topics:
        try:
            chat = generate_chat(topic)

            valid, reason = validate_generated_chat(chat)

            if valid:
                save_generated_chat(chat)
                accepted += 1
                print(f"✅ {topic}")
            else:
                print(f"❌ {topic} -> {reason}")

        except Exception as e:
            print(f"❌ {topic} -> {e}")

    print(f"\nGenerated {accepted} valid chats.")
    

if __name__ == "__main__":
    main()