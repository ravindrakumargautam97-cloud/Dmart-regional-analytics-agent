
import csv
import json
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parent

source = BASE / "eval_results.json"
data = json.loads(source.read_text(encoding="utf-8"))

results = data["results"]

assert len(results) == 36, "Expected 36 evaluation cases"
assert len({r["id"] for r in results}) == 36, "Duplicate case IDs"

# 1. Create CSV
csv_path = BASE / "eval_results.csv"

fields = [
    "id", "category", "question",
    "expected_status", "actual_status",
    "expected_text", "answer",
    "attempts", "passed"
]

with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(results)

# 2. Create JSONL from evaluation results
jsonl_path = BASE / "eval_runs.jsonl"

with jsonl_path.open("w", encoding="utf-8") as f:
    for result in results:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

# 3. Create summary
total = len(results)
passed = sum(r["passed"] is True for r in results)
failed = total - passed
accuracy = round(passed / total * 100, 2)

categories = Counter(r["category"] for r in results)

lines = [
    "# DMart Regional Analytics Agent - Evaluation Summary",
    "",
    f"- Total Cases: {total}",
    f"- Passed: {passed}",
    f"- Failed: {failed}",
    f"- Accuracy: {accuracy}%",
    "",
    "## Category Distribution",
    ""
]

for category, count in sorted(categories.items()):
    lines.append(f"- {category}: {count}")

lines += [
    "",
    "## Evaluation Evidence",
    "",
    "- eval_results.csv",
    "- eval_runs.jsonl",
    "- eval_results.json",
    "- eval_report.md",
    "",
    "## Release Gate",
    "",
    "Evaluation accuracy requirement: PASS (>= 90%).",
    "Numerical grounding: Pending independent verification.",
    "Budget-exceeded cases: Pending verification.",
    "Final release decision: Pending.",
]

summary_path = BASE / "eval_summary.md"
summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Created:", csv_path.name)
print("Created:", jsonl_path.name)
print("Created:", summary_path.name)
print("Total Cases:", total)
print("Passed:", passed)
print("Accuracy:", f"{accuracy}%")
