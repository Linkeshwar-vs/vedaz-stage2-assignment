from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

INPUT_FILE = DATA_DIR / "input.jsonl"
TRAIN_FILE = DATA_DIR / "train.jsonl"
TEST_FILE = DATA_DIR / "test.jsonl"
GENERATED_FILE = DATA_DIR / "generated.jsonl"

CHECKER_REPORT = REPORTS_DIR / "checker_report.json"
EVALUATION_REPORT = REPORTS_DIR / "evaluation.csv"

MODEL_NAME = "gpt-4.1-mini"

SIMILARITY_THRESHOLD = 90

TRAIN_SIZE = 0.8
TEST_SIZE = 0.2