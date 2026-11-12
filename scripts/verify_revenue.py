
import csv
import json
import re
from pathlib import Path

rows = list(csv.DictReader(
    Path("data/store_daily_clean.csv").open(
        encoding="utf-8-sig"
    )
))

data = json.loads(
    Path("eval/eval_results.json").read_text(
        encoding="utf-8"
    )
)

cases = [
    x for x in data["results"]
    if x["category"] in ("revenue", "target")
]

passed = 0

print("SOURCE DATA VERIFICATION")
print("-" * 45)

for case in cases:
    answer = case["answer"]

    match = re.search(
        r"(Mumbai|Pune|Hyderabad|Bengaluru|Ahmedabad)"
        r".*?(2026-\d{2}-\d{2})",
        answer,
        re.DOTALL
    )

    row = next(
        (
            r for r in rows
            if match
            and r["store"] == match.group(1)
            and r["date"] == match.group(2)
        ),
        None
    )

    revenue_ok = False
    target_ok = False

    if row:
        revenue = float(row["revenue_inr"])
        revenue_ok = f"{revenue:,.2f}" in answer

        if case["category"] == "target":
            target = float(row["daily_target_inr"])
            achievement = float(row["achievement_pct"])

            target_ok = (
                f"{target:,.2f}" in answer
                and f"{achievement:.2f}%" in answer
            )
        else:
            target_ok = True

    ok = revenue_ok and target_ok

    if ok:
        passed += 1

    print(
        case["id"],
        "PASS" if ok else "FAIL"
    )

print("-" * 45)
print("Verified:", passed, "/", len(cases))
