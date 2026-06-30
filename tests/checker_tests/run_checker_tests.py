import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT, "scripts"))

from checker import main


TEST_FILES = {
    "1": ("Safe Chats", "tests/checker_tests/test_data/safe_chats.jsonl"),
    "2": ("Unsafe Chats", "tests/checker_tests/test_data/unsafe_chats.jsonl"),
    "3": ("Duplicate Chats", "tests/checker_tests/test_data/duplicate_chats.jsonl"),
}


def run():
    while True:
        print("\n========== Checker Test Runner ==========\n")

        for key, (name, _) in TEST_FILES.items():
            print(f"{key}. {name}")

        print("0. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("\nExiting Checker Test Runner.")
            break

        if choice not in TEST_FILES:
            print("\nInvalid option. Please try again.")
            continue

        name, path = TEST_FILES[choice]

        print(f"\nRunning: {name}\n")

        main(path)

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    run()