from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "content" / "course.json").read_text(encoding="utf-8"))
OUTPUT = ROOT / "outputs" / "assessment-exports"


FIELDS = [
    "lesson_number", "question_id", "standard_ids", "objective_ids", "question_type",
    "prompt", "option_a", "option_b", "option_c", "option_d", "option_e", "option_f",
    "correct_answers", "points", "feedback_correct", "feedback_incorrect", "source_ids",
    "cognitive_level", "randomization_group", "required", "approval_status",
    "google_forms_override", "canvas_override", "conversion_notes"
]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    approved = [item for item in DATA.get("assessment_bank", []) if item.get("approval_status") == "Approved"]
    (OUTPUT / "assessment-bank.json").write_text(json.dumps(approved, indent=2), encoding="utf-8")
    with (OUTPUT / "assessment-bank.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(approved)
    print(f"Exported {len(approved)} approved assessment items to {OUTPUT}")


if __name__ == "__main__":
    main()
