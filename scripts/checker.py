from utils import load_jsonl
from config import INPUT_FILE


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


def main():
    chats = load_jsonl(INPUT_FILE)

    valid = 0

    for i, chat in enumerate(chats, start=1):
        ok, reason = validate_structure(chat)

        if ok:
            valid += 1
        else:
            print(f"Chat {i}: {reason}")

    print(f"\nValid Chats: {valid}/{len(chats)}")


if __name__ == "__main__":
    main()