
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import agent.run_agent as agent


CASES = [
    ("A01", "session_1", "What was Pune revenue on 15 May 2026?",
     "Answered", ["623845.00"], 0),

    ("A02", "session_1", "And the target?",
     "Answered", ["900000.00"], 0),

    ("A03", "session_1", "What about Mumbai?",
     "Answered", ["1050000.00"], 0),

    ("A04", "session_4", "What is the value?",
     "Clarification Needed", [], 0),

    ("A05", "session_5", "What was Hyderabad revenue on 15 May 2026?",
     "Answered", ["786399.27"], 0),

    ("A06", "session_6", "What was Hydrabad revenue yesterday?",
     "Answered", ["784954.90"], 0),

    ("A07", "session_7", "Did Pune achieve its target on 16 May 2026?",
     "Drafted", ["74.59", "Poor"], 0),

    ("A08", "session_8", "Did Pune achieve its target on 20 May 2026?",
     "Answered", ["75.30", "Good"], 0),

    ("A09", "session_9", "Did Mumbai achieve its target on 21 May 2026?",
     "Answered", ["107.99", "Excellent"], 0),

    ("A10", "session_10",
     "Compare store revenue from 1 May 2026 to 31 May 2026",
     "Answered",
     ["1071614.03", "916766.02", "900317.89",
      "798849.31", "643251.34"], 0),

    ("A11", "session_11",
     "Rank stores by lowest revenue on 10 June 2026",
     "Answered",
     ["602942.85", "807522.21", "819290.32",
      "848248.05", "903822.34"], 0),

    ("A12", "session_12",
     "Which stores have Amul Milk 1L below reorder threshold?",
     "Answered", ["Hyderabad", "40", "Pune", "85"], 0),

    ("A13", "session_13",
     "What is Hyderabad customer feedback average rating and top theme?",
     "Answered", ["2.63", "38", "40", "Stock availability"], 0),

    ("A14", "session_14",
     "What is Pune profit margin on 15 May 2026?",
     "Safe Failure", [], 0),

    ("A15", "session_15",
     "What is the capital of India?",
     "Escalated", [], 0),

    ("A16", "session_16",
     "What was Mumbai revenue on 15 July 2026?",
     "Safe Failure", [], 0),

    ("A17", "session_17",
     "Why is Pune revenue low?",
     "Escalated", [], 0),

    ("A18", "session_18",
     "What was Kolkata revenue on 15 May 2026?",
     "Clarification Needed", [], 0),

    ("A19", "session_19",
     "What was Pune revenue on 15 May 2026?",
     "Answered", ["623845.00"], 2),

    ("A20", "session_20",
     "What was Pune revenue on 15 May 2026?",
     "Escalated", [], 3),
]


def run_case(case):
    case_id, session_id, question, expected_status, expected_values, failures = case

    if failures:
        original = agent.get_store_day
        counter = {"count": 0}

        def simulated_fetch(*args, **kwargs):
            counter["count"] += 1
            if counter["count"] <= failures:
                raise ConnectionError("Simulated database failure")
            return original(*args, **kwargs)

        with patch.object(agent, "get_store_day", simulated_fetch):
            result = agent.handle(question, session_id)
    else:
        result = agent.handle(question, session_id)

    actual_status = result["status"]
    answer = result.get("answer_text", result.get("answer", ""))

    status_ok = actual_status == expected_status
    values_ok = all(str(value) in answer for value in expected_values)

    attempts_ok = (
        result.get("attempts") == 3
        if case_id in ("A19", "A20")
        else True
    )

    passed = status_ok and values_ok and attempts_ok

    return {
        "case_id": case_id,
        "question": question,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "expected_values": expected_values,
        "actual_answer": answer,
        "attempts": result.get("attempts", 0),
        "passed": passed,
    }


def main():
    output_dir = ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    log_path = output_dir / "acceptance_runs.jsonl"

    # Keep acceptance logs separate from normal agent runs.
    old_log_path = os.environ.get("AGENT_LOG_PATH")
    os.environ["AGENT_LOG_PATH"] = str(log_path)

    agent.SESSIONS.clear()
    if log_path.exists():
        log_path.unlink()

    try:
        results = [run_case(case) for case in CASES]
    finally:
        if old_log_path is None:
            os.environ.pop("AGENT_LOG_PATH", None)
        else:
            os.environ["AGENT_LOG_PATH"] = old_log_path

    passed_count = sum(item["passed"] for item in results)

    lines = [
        "# DMart Agent Acceptance Transcript",
        "",
        f"**Passed:** {passed_count}/{len(results)}",
        "",
        "| Case | Expected | Actual | Attempts | Result |",
        "|---|---|---|---:|---|",
    ]

    for item in results:
        label = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"| {item['case_id']} | "
            f"{item['expected_status']} | "
            f"{item['actual_status']} | "
            f"{item['attempts']} | {label} |"
        )

    lines.extend(["", "## Detailed Results", ""])

    for item in results:
        lines.extend([
            f"### {item['case_id']}",
            "",
            f"**Question:** {item['question']}",
            "",
            f"**Expected status:** {item['expected_status']}",
            "",
            f"**Actual status:** {item['actual_status']}",
            "",
            f"**Expected values:** {item['expected_values']}",
            "",
            f"**Answer:** {item['actual_answer']}",
            "",
            f"**Result:** {'PASS' if item['passed'] else 'FAIL'}",
            "",
        ])

    report_path = output_dir / "acceptance_transcript.md"
    report_path.write_text(
        "\n".join(lines), encoding="utf-8"
    )

    print("\nDMart Acceptance Results")
    print("=" * 35)

    for item in results:
        label = "PASS" if item["passed"] else "FAIL"
        print(
            f"{item['case_id']}: {label} "
            f"({item['actual_status']})"
        )

    print("=" * 35)
    print(f"TOTAL: {passed_count}/{len(results)}")
    print(f"REPORT: {report_path}")
    print(f"LOG: {log_path}")

    if log_path.exists():
        count = len(log_path.read_text(encoding="utf-8").splitlines())
        print(f"LOG RECORDS: {count}")

    if passed_count != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
