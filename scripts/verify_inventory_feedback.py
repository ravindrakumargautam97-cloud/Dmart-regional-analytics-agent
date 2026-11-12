
import csv
import json
from pathlib import Path
from collections import Counter

def load_csv(filename):
    with open(filename, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

inventory = load_csv("data/inventory.csv")
feedback = load_csv("data/feedback.csv")

data = json.loads(
    Path("eval/eval_results.json").read_text(encoding="utf-8")
)

cases = [
    x for x in data["results"]
    if x["category"] in ("inventory", "feedback")
]

passed = 0

print("INVENTORY AND FEEDBACK VERIFICATION")
print("-" * 45)

for case in cases:
    answer = case["answer"]
    ok = False

    if case["category"] == "inventory":
        for row in inventory:
            store = row["store"]
            product = row["product"]
            stock = row["stock_units"]
            threshold = row["reorder_threshold"]

            if (
                store in answer
                and product in answer
                and f"{stock} units" in answer
                and f"threshold {threshold}" in answer
            ):
                ok = True
                break

    elif case["category"] == "feedback":
        stores = sorted(set(r["store"] for r in feedback))

        for store in stores:
            if store not in answer:
                continue

            records = [r for r in feedback if r["store"] == store]
            ratings = [
                float(r["rating"])
                for r in records
                if r["rating"].strip()
            ]

            avg = sum(ratings) / len(ratings) if ratings else 0
            themes = Counter(
                r["theme"] for r in records if r["theme"].strip()
            )
            top_theme = themes.most_common(1)[0][0] if themes else ""

            ok = (
                f"{avg:.2f}" in answer
                and f"rated records {len(ratings)}" in answer
                and f"total feedback {len(records)}" in answer
                and top_theme in answer
            )
            if ok:
                break

    if ok:
        passed += 1

    print(case["id"], "PASS" if ok else "FAIL")

print("-" * 45)
print("Verified:", passed, "/", len(cases))
