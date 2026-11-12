
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent.run_agent as agent

EVAL_DIR = ROOT / "eval"
LOG_FILE = ROOT / "logs" / "runs.jsonl"


def main():
    cases = json.loads(
        (EVAL_DIR / "eval_cases.json").read_text(encoding="utf-8")
    )

    # Preserve the final acceptance logs.
    original_logs = (
        LOG_FILE.read_bytes() if LOG_FILE.exists() else None
    )

    results = []

    try:
        for case in cases:
            result = agent.handle(
                case["question"],
                session_id="eval_" + case["id"]
            )

            status_ok = result["status"] == case["status"]
            text_ok = (
                case["contains"].lower()
                in result["answer"].lower()
            )

            passed = status_ok and text_ok

            results.append({
                "id": case["id"],
                "category": case["category"],
                "question": case["question"],
                "expected_status": case["status"],
                "actual_status": result["status"],
                "expected_text": case["contains"],
                "answer": result["answer"],
                "attempts": result["attempts"],
                "passed": passed
            })

            label = "PASS" if passed else "FAIL"
            print(f"{case['id']}: {label} | {result['status']}")

            if not passed:
                print("  Expected:", case["status"], case["contains"])
                print("  Actual:", result["answer"])

    finally:
        # Restore acceptance logs, even if evaluation fails.
        if original_logs is None:
            LOG_FILE.unlink(missing_ok=True)
        else:
            LOG_FILE.write_bytes(original_logs)

    passed_count = sum(r["passed"] for r in results)
    total = len(results)
    accuracy = round(100 * passed_count / total, 2) if total else 0

    report = {
        "total_cases": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "accuracy_pct": accuracy,
        "results": results
    }

    (EVAL_DIR / "eval_results.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    lines = [
        "# DMart Agent Evaluation Report",
        "",
        f"Total Cases: {total}",
        f"Passed: {passed_count}",
        f"Failed: {total - passed_count}",
        f"Pass Rate: {accuracy}%",
        "",
        "## Failed Cases",
        ""
    ]

    failures = [r for r in results if not r["passed"]]

    if failures:
        for r in failures:
            lines.append(
                f"- {r['id']}: Expected {r['expected_status']}; "
                f"Actual {r['actual_status']}. "
                f"Expected text: {r['expected_text']}"
            )
    else:
        lines.append("None")

    lines.extend([
        "",
        "## Evaluation Scope",
        "",
        "Checks expected status and required answer text.",
        "This is not a full numerical grounding or safety audit.",
        ""
    ])

    (EVAL_DIR / "eval_report.md").write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    print("-" * 50)
    print(f"Passed: {passed_count}/{total}")
    print(f"Pass Rate: {accuracy}%")
    print("Results: eval/eval_results.json")
    print("Report: eval/eval_report.md")


if __name__ == "__main__":
    main()
