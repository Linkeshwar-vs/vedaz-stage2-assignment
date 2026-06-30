import json

from prompts import GENERATOR_PROMPT
from utils import call_llm, parse_json_response

from checker import (
    validate_structure,
    rule_based_safety,
    llm_safety,
)

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

def main():
    chat = generate_chat("Career delay, Hindi")

    valid, reason = validate_generated_chat(chat)

    if valid:
        print("✅ Chat passed validation.\n")
        print(json.dumps(chat, indent=4, ensure_ascii=False))
    else:
        print(f"❌ Chat rejected: {reason}")
        

if __name__ == "__main__":
    main()