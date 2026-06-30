from config import INPUT_FILE
import re
import json
from prompts import SAFETY_PROMPT

from rapidfuzz import fuzz
from utils import (
    call_llm,
    load_jsonl, 
    parse_json_response,
    normalize_text,
    word_count
)
from config import SIMILARITY_THRESHOLD

from sklearn.model_selection import train_test_split

from config import (
    TRAIN_FILE,
    TEST_FILE,
    CHECKER_REPORT,
    TRAIN_SIZE,
)

from utils import save_jsonl, save_report

SAFETY_RULES = {
    "death_prediction": [
        r"\bwill die\b",
        r"\byou will die\b",
        r"\bdeath is certain\b",
        r"\byour life will end\b",
    ],
    "illness_prediction": [
        r"\byou have cancer\b",
        r"\byou have a terminal illness\b",
        r"\byou will get cancer\b",
        r"\byou will suffer a heart attack\b",
    ],
    "fear_selling": [
        r"\bbad luck forever\b",
        r"\byour family will suffer\b",
        r"\bdisaster will happen\b",
        r"\bcurse\b",
    ],
    "payment_pressure": [
        r"pay\s*₹?\s*\d+",
        r"pay\s+rs\.?\s*\d+",
        r"mandatory\s+puja",
        r"buy\s+this\s+gemstone",
    ],
}

def validate_structure(chat):
    messages = chat.get("messages", [])

    if not messages:
        return False, "Conversation is empty."

    if messages[0].get("role") != "system":
        return False, "First message must be 'system'."

    expected = "user"
    for message in messages[1:]:
        role = message.get("role")

        if role != expected:
            return False, f"Expected '{expected}', found '{role}'."

        expected = "assistant" if expected == "user" else "user"

    return True, ""

def llm_safety(chat):
    prompt = SAFETY_PROMPT.format(
        conversation=json.dumps(chat, ensure_ascii=False, indent=2)
    )

    try:
        response = call_llm(prompt)
        result = parse_json_response(response)
        return result.get("safe", False), result.get("violations", [])
    
    except Exception as e:
        print(f"LLM Parsing Error: {e}")
        print(response)
        return False, ["llm_validation_failed"]


def rule_based_safety(chat):
    assistant_text = " ".join(
        msg["content"]
        for msg in chat["messages"]
        if msg["role"] == "assistant"
    ).lower()

    violations = []

    for rule, patterns in SAFETY_RULES.items():
        if any(re.search(pattern, assistant_text) for pattern in patterns):
            violations.append(rule)

    return len(violations) == 0, violations

def find_duplicates(chats):
    processed = []

    for i, chat in enumerate(chats):
        text = normalize_text(
            " ".join(
                msg["content"]
                for msg in chat["messages"]
                if msg["role"] in ("user", "assistant")
            )
        )

        processed.append((i, text))

    duplicates = []

    for i in range(len(processed)):
        idx1, text1 = processed[i]

        for j in range(i + 1, len(processed)):
            idx2, text2 = processed[j]

            score = fuzz.token_set_ratio(text1, text2)

            

            if score >= SIMILARITY_THRESHOLD:
                duplicates.append({
                    "chat_1": idx1 + 1,
                    "chat_2": idx2 + 1,
                    "similarity": round(score, 2)
                })

    

    return duplicates

def split_dataset(chats):
    train, test = train_test_split(
        chats,
        train_size=TRAIN_SIZE,
        random_state=42,
        shuffle=True,
    )

    save_jsonl(train, TRAIN_FILE)
    save_jsonl(test, TEST_FILE)

    return train, test


def generate_report(total, valid, safe, duplicates):
    report = {
        "total_chats": total,
        "structure_valid": valid,
        "safety_passed": safe,
        "duplicate_chats": len(duplicates),
        "duplicates": duplicates,
    }

    save_report(report, CHECKER_REPORT)


def main(input_file=INPUT_FILE):
    chats = load_jsonl(input_file)

    word_counts = {
        i + 1: word_count(chat)
        for i, chat in enumerate(chats)
    }

    print("\nWord Counts:")
    print(word_counts)
    valid = 0   
    safe = 0

    for i, chat in enumerate(chats, start=1):
        ok, reason = validate_structure(chat)

        if not ok:
            print(f"Chat {i}: {reason}")
            continue

        valid += 1

        safe_chat, violations = rule_based_safety(chat)

        if not safe_chat:
            print(f"Chat {i} Rule Violations: {violations}")
            continue

        llm_safe, llm_violations = llm_safety(chat)

        if llm_safe:
            safe += 1
        else:
            print(f"Chat {i} LLM Violations: {llm_violations}")
    
    duplicates = find_duplicates(chats)

    if duplicates:
        print("\nDuplicate Chats:")
        for dup in duplicates:
            print(
                f"Chat {dup['chat_1']} <-> Chat {dup['chat_2']} "
                f"({dup['similarity']:.1f}%)"
            )


    train, test = split_dataset(chats)

    generate_report(
        total=len(chats),
        valid=valid,
        safe=safe,
        duplicates=duplicates,
    )

    print(f"\nValid Chats : {valid}/{len(chats)}")
    print(f"Safety Passed : {safe}/{valid}")
    print(f"Duplicates  : {len(duplicates)}")
    print(f"Train Chats : {len(train)}")
    print(f"Test Chats  : {len(test)}")
    print("\nChecker report saved.")


if __name__ == "__main__":
    main()