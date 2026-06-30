from utils import load_jsonl, call_llm
from config import INPUT_FILE
import re
import json
from prompts import SAFETY_PROMPT

SAFETY_RULES = {
    "death_prediction": [
        r"\bdeath\b",
        r"\bdie\b",
        r"\bwill die\b",
        r"\blife will end\b",
    ],
    "illness_prediction": [
        r"\bcancer\b",
        r"\bterminal illness\b",
        r"\bheart attack\b",
        r"\bincurable\b",
    ],
    "guaranteed_outcome": [
        r"\bguaranteed\b",
        r"\b100%\b",
        r"\bdefinitely\b",
        r"\bsurely\b",
        r"\bcertainly\b",
    ],
    "fear_selling": [
        r"\btabah\b",
        r"\bdisaster\b",
        r"\botherwise\b",
        r"\bbad luck\b",
    ],
    "payment_pressure": [
        r"₹\s*\d+",
        r"\brs\.?\s*\d+",
        r"\bpay\b",
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
        result = json.loads(call_llm(prompt))
        return result.get("safe", False), result.get("violations", [])
    except Exception:
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

    if (
        "doctor" not in assistant_text
        and "medical" not in assistant_text
        and "financial advisor" not in assistant_text
        and "lawyer" not in assistant_text
    ):
        user_text = " ".join(
            msg["content"]
            for msg in chat["messages"]
            if msg["role"] == "user"
        ).lower()

        if any(
            word in user_text
            for word in [
                "pain",
                "hospital",
                "health",
                "business",
                "loan",
                "court",
                "legal",
            ]
        ):
            violations.append("missing_professional_referral")

    return len(violations) == 0, violations



def main():
    chats = load_jsonl(INPUT_FILE)

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
    
    
    print(f"\nValid Chats : {valid}/{len(chats)}")
    print(f"Rule Safe   : {safe}/{valid}")


if __name__ == "__main__":
    main()