from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

INPUT_FILE = DATA_DIR / "vedaz_astrologer_finetune.jsonl"
TRAIN_FILE = DATA_DIR / "train.jsonl"
TEST_FILE = DATA_DIR / "test.jsonl"
GENERATED_FILE = DATA_DIR / "generated.jsonl"

CHECKER_REPORT = REPORTS_DIR / "checker_report.json"
EVALUATION_REPORT = REPORTS_DIR / "evaluation.csv"

MODEL_NAME = "gpt-4.1-mini"

SIMILARITY_THRESHOLD = 90

TRAIN_SIZE = 0.8
TEST_SIZE = 0.2