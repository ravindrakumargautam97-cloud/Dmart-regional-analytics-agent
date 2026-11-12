
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import agent.run_agent as agent

CASES = [
    ("A01", "What was Pune revenue on 15 May 2026?", "Answered", "623,845.00"),
    ("A02", "What was Hyderabad revenue on 15 May 2026?", "Answered", "786,399.27"),
    ("A03", "Did Pune achieve its target on 16 May 2026?", "Drafted", "74.59%"),
    ("A04", "Did Mumbai achieve its target on 21 May 2026?", "Answered", "107.99%"),
    ("A05", "Compare revenue across all stores", "Answered", "Mumbai"),
    ("A06", "Is Amul Milk below reorder threshold in Hyderabad?", "Answered", "40 units"),
    ("A07", "Is Amul Milk below reorder threshold in Pune?", "Answered", "85 units"),
    ("A08", "What is the customer feedback rating for Hyderabad?", "Answered", "2.63"),
    ("A09", "What was Pune's profit margin on 15 May 2026?", "Safe Failure", "not approved"),
    ("A10", "Can you approve a salary increase for the Pune store manager?", "Escalated", "human manager"),
    ("A11", "What was Pune revenue on 15 July 2026?", "Safe Failure", "outside"),
    ("A12", "Why did Pune revenue decrease?", "Escalated", "Root cause"),
    ("A13", "What was Kolkata revenue on 15 May 2026?", "Clarification Needed", "specify"),
    ("A14", "What was Mumbai weather on 15 May 2026?", "Answered", "simulated"),
    ("A15", "What was Pune weather on 16 May 2026?", "Answered", "6.5 mm"),
    ("A16", "What was Pune revenue yesterday?", "Answered", "revenue"),
    ("A17", "What was Bangalore revenue on 15 May 2026?", "Answered", "Bengaluru"),
    ("A18", "What was Pune revenue?", "Clarification Needed", "date"),
]

def run_case(case):
    case_id, question, expected_status, expected_text = case
    result = agent.handle(question, case_id)
    passed = (
        result["status"] == expected_status
        and expected_text.lower() in result["answer"].lower()
    )
    return {
        "id": case_id,
        "question": question,
        "expected_status": expected_status,
        "actual_status": result["status"],
        "answer": result["answer"],
        "attempts": result["attempts"],
        "passed": passed,
    }

def run_retry(case_id, fail_count):
    original = agent.get_store_day
    state = {"count": 0}

    def simulated_fetch(store, date):
        state["count"] += 1
        if state["count"] <= fail_count:
            raise ConnectionError("Simulated database failure")
        return original(store, date)

    agent.get_store_day = simulated_fetch
    try:
        result = agent.handle(
            "What was Pune revenue on 15 May 2026?",
            case_id,
        )
    finally:
        agent.get_store_day = original

    expected_status = "Answered" if fail_count == 2 else "Escalated"
    passed = (
        result["status"] == expected_status
        and result["attempts"] == 3
    )

    return {
        "id": case_id,
        "question": f"Simulated database failure {fail_count} times",
        "expected_status": expected_status,
        "actual_status": result["status"],
        "answer": result["answer"],
        "attempts": result["attempts"],
        "passed": passed,
    }

def main():
    results = [run_case(case) for case in CASES]
    results.append(run_retry("A19", 2))
    results.append(run_retry("A20", 3))

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)

    lines = [
        "# DMart Agent Acceptance Transcript",
        "",
        "20 automated acceptance cases",
        "",
    ]

    for item in results:
        label = "PASS" if item["passed"] else "FAIL"
        print(f"{item['id']}: {label} | {item['actual_status']}")

        lines.extend([
            f"## {item['id']} - {label}",
            "",
            f"Question: {item['question']}",
            "",
            f"Expected status: {item['expected_status']}",
            "",
            f"Actual status: {item['actual_status']}",
            "",
            f"Attempts: {item['attempts']}",
            "",
            f"Answer: {item['answer']}",
            "",
        ])

    passed = sum(item["passed"] for item in results)
    lines.insert(3, f"Passed: {passed}/{len(results)}")
    lines.insert(4, "")

    transcript = output_dir / "acceptance_transcript.md"
    transcript.write_text("\n".join(lines), encoding="utf-8")

    print("-" * 50)
    print(f"Passed: {passed}/{len(results)}")
    print(f"Transcript: {transcript}")

if __name__ == "__main__":
    main()
