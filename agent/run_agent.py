
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.understand import understand, MIN_DATE, MAX_DATE
from agent.fetch import (
    get_store_day,
    get_target_vs_actual,
    compare_store_revenue,
    get_inventory,
    get_feedback,
)
from agent.answer import make_answer
from tools.weather import get_weather
from agent.retry import run_with_retry


LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

SESSIONS = {}


def handle(question, session_id, user_id="u1"):
    started = time.perf_counter()

    context = SESSIONS.get(session_id, {})
    parsed = understand(question, context)

    intent = parsed["intent"]
    store = parsed["store"]
    date = parsed["date"]

    result = {
        "question": question,
        "intent": intent,
        "status": "Safe Failure",
        "answer": "",
        "evidence": [],
        "confidence": parsed["confidence"],
        "attempts": 0,
    }

    try:
        # 1. Out-of-scope safety
        if intent == "out_of_scope":
            result["status"] = "Escalated"
            result["answer"] = (
                "I cannot approve salary increases or "
                "make HR decisions. This request requires "
                "review by an authorized human manager."
            )

        # 2. Unsupported metrics
        elif intent == "unsupported_metric":
            result["status"] = "Safe Failure"
            result["answer"] = (
                "This metric is not approved for reporting. "
                "Only whitelisted metrics can be used."
            )

        # 3. Diagnostic questions
        elif intent == "diagnostic":
            result["status"] = "Escalated"
            result["answer"] = (
                "Root cause cannot be confirmed from "
                "descriptive data alone. Human review "
                "and additional evidence are required."
            )

        # 4. Date validation
        elif date and not (
            MIN_DATE.date().isoformat()
            <= date
            <= MAX_DATE.date().isoformat()
        ):
            result["status"] = "Safe Failure"
            result["answer"] = (
                "The requested date is outside the "
                "available dataset period."
            )

        # 5. Store comparison
        elif intent == "comparison":
            data = compare_store_revenue()
            result.update(make_answer(intent, data))
            result["attempts"] = 1

        # 6. Missing store
        elif not store:
            result["status"] = "Clarification Needed"
            result["answer"] = (
                "Please specify one of these stores: "
                "Mumbai, Pune, Hyderabad, Bengaluru, "
                "or Ahmedabad."
            )

        # 7. Inventory lookup
        elif intent == "inventory":
            product = (
                "Amul Milk 1L"
                if "amul milk" in question.lower()
                else None
            )

            data = get_inventory(store, product)
            result.update(make_answer(intent, data))
            result["attempts"] = 1

        # 8. Feedback lookup
        elif intent == "feedback":
            data = get_feedback(store)
            result.update(make_answer(intent, data))
            result["attempts"] = 1

        # 9. Weather lookup
        elif intent == "weather":
            if not date:
                result["status"] = "Clarification Needed"
                result["answer"] = (
                    "Please provide a date for the "
                    "weather request."
                )
            else:
                weather = get_weather(
                    store,
                    date,
                    mode="stub"
                )

                result["status"] = "Answered"
                result["answer"] = (
                    f"{store} weather on {date}: "
                    f"temperature {weather['temperature_c']} C, "
                    f"humidity {weather['humidity_pct']}%, "
                    f"wind speed {weather['wind_speed_kmh']} km/h, "
                    f"rainfall {weather['rainfall_mm']} mm. "
                    f"Source: {weather['source']} "
                    f"(simulated weather, not observed)."
                )
                result["evidence"] = [weather]
                result["attempts"] = 1

        # 10. Missing date
        elif not date:
            result["status"] = "Clarification Needed"
            result["answer"] = (
                "Please provide a date, such as "
                "15 May 2026."
            )
        elif intent == "target_vs_actual":
            data = get_target_vs_actual(store, date)
            result.update(make_answer(intent, data))

            if data and data["performance_band"] == "Poor":
                result["status"] = "Drafted"

            result["attempts"] = 1

      
        # 12. Default revenue lookup
        
        else:
            retry_result = run_with_retry(
                lambda: get_store_day(store, date),
                max_attempts=3
            )

            result["attempts"] = retry_result["attempts"]

            if retry_result["success"]:
                data = retry_result["data"]
                result.update(make_answer("lookup", data))
  
            else:
                result["status"] = "Escalated"
                result["error"] = retry_result["error"]
                result["answer"] = (
                    "Data retrieval failed after 3 attempts. "
                    "Human review is required."
                )


        # Save conversation context
        if store:
            SESSIONS[session_id] = {
                "store": store,
                "date": date,
            }

    except Exception as exc:
        result["status"] = "Safe Failure"
        result["answer"] = (
            "The request could not be completed safely."
        )
        result["error"] = str(exc)

    # Processing latency
    result["latency_ms"] = round(
        (time.perf_counter() - started) * 1000, 2
    )

    # Audit log
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "user_id": user_id,
        **result,
    }

    with (LOG_DIR / "runs.jsonl").open(
        "a", encoding="utf-8"
    ) as file:
        file.write(
            json.dumps(log_entry) + "\n"
        )

    return result


if __name__ == "__main__":
    print("DMart Regional Analytics Agent")
    print("Type exit to quit.")

    while True:
        question = input("\nYou: ").strip()

        if question.lower() in ("exit", "quit"):
            break

        if not question:
            continue

        response = handle(
            question,
            "demo_session"
        )

        print("\nAgent:", response["answer"])
        print("Status:", response["status"])
