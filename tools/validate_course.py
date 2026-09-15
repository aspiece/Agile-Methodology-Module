from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "course.json"
ALLOWED_STEPS = {"2", "3", "4", "5", "6", "application", "assessment"}
PROHIBITED_TERMS = ("GCI", "Genesee Career Institute")


def finding(level: str, location: str, message: str) -> dict[str, str]:
    return {"level": level, "location": location, "message": message}


def main() -> int:
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    findings: list[dict[str, str]] = []
    lessons = data.get("lessons", [])
    course = data.get("course", {})

    if len(lessons) != 8:
        findings.append(finding("error", "course", f"Expected exactly 8 lessons; found {len(lessons)}."))
    expected_numbers = list(range(1, 9))
    actual_numbers = [item.get("number") for item in lessons]
    if actual_numbers != expected_numbers:
        findings.append(finding("error", "course", f"Lesson numbers must be {expected_numbers}; found {actual_numbers}."))
    if course.get("target_minutes_per_lesson") != 50:
        findings.append(finding("warning", "course", "The established weekly target is 50 minutes including assessment."))
    mastery = course.get("mastery", {})
    if mastery.get("threshold_percent") != 80 or mastery.get("attempts") != 3:
        findings.append(finding("error", "course.mastery", "Mastery must be 80% with up to 3 attempts."))

    for lesson in lessons:
        number = lesson.get("number")
        location = f"lesson-{number}"
        steps = lesson.get("steps", {})
        missing = []
        if "2" not in steps:
            missing.append("2")
        if "application" not in steps and "5" not in steps:
            missing.append("application")
        if "assessment" not in steps and "6" not in steps:
            missing.append("assessment")
        if missing:
            findings.append(finding("error", location, f"Missing required step definitions: {sorted(missing)}."))
        unknown = set(steps) - ALLOWED_STEPS
        if unknown:
            findings.append(finding("error", location, f"Unsupported step definitions: {sorted(unknown)}."))
        if not lesson.get("objectives"):
            findings.append(finding("error", location, "At least one approved learning objective is required."))
        if lesson.get("estimated_minutes", 0) > 55:
            findings.append(finding("warning", location, "Estimated time exceeds the 50-minute target by more than 5 minutes."))
        for suffix in ("2", "3", "4"):
            step = steps.get(suffix)
            if not step:
                continue
            check = step.get("check")
            if not check and not step.get("check_override_reason"):
                findings.append(finding("error", f"{number}.{suffix}", "Instructional steps require a check or an approved override reason."))
            if len(step.get("resource_ids", [])) > 1:
                findings.append(finding("warning", f"{number}.{suffix}", "Review chunking: an instructional step should have one primary resource."))
        instructional_suffixes = [int(suffix) for suffix in ("2", "3", "4") if steps.get(suffix)]
        application_suffix = max(instructional_suffixes) + 1 if instructional_suffixes else 3
        application = steps.get("application") or steps.get("5", {})
        if course.get("module_type") == "cte" and not application.get("program_scenarios"):
            findings.append(finding("warning", f"{number}.{application_suffix}", "CTE application requires approved program-specific scenarios before release."))

    generated_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [ROOT / "index.html", *sorted((ROOT / "lessons").glob("lesson-*.html"))]
        if path.exists()
    )
    for term in PROHIBITED_TERMS:
        if re.search(rf"\b{re.escape(term)}\b", generated_text, flags=re.IGNORECASE):
            findings.append(finding("error", "generated site", f"Prohibited learner-facing institutional term found: {term}."))

    report = {
        "status": "fail" if any(item["level"] == "error" for item in findings) else "pass",
        "errors": sum(item["level"] == "error" for item in findings),
        "warnings": sum(item["level"] == "warning" for item in findings),
        "findings": findings,
    }
    output = ROOT / "outputs" / "validation-report.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
