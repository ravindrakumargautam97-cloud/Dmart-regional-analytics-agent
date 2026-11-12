
import csv
import json
from pathlib import Path
from collections import defaultdict

with open("data/store_daily_clean.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

data = json.loads(
    Path("eval/eval_results.json").read_text(encoding="utf-8")
)

cases = [
    x for x in data["results"]
    if x["category"] == "comparison"
]

revenue = defaultdict(list)

for row in rows:
    revenue[row["store"]].append(float(row["revenue_inr"]))

ranking = sorted(
    (
        (store, sum(values) / len(values))
        for store, values in revenue.items()
    ),
    key=lambda x: x[1],
    reverse=True
)

expected_lines = [
    f"{i}. {store}: INR {avg:,.2f}"
    for i, (store, avg) in enumerate(ranking, 1)
]

passed = 0

print("COMPARISON SOURCE VERIFICATION")
print("-" * 45)

for case in cases:
    answer = case["answer"]

    ok = all(line in answer for line in expected_lines)

    if ok:
        passed += 1

    print(case["id"], "PASS" if ok else "FAIL")

print("-" * 45)
print("Verified:", passed, "/", len(cases))
print("Expected ranking:")
for line in expected_lines:
    print(line)
