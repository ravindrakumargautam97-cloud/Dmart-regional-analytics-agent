
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.understand import understand, MIN_DATE, MAX_DATE
from agent.fetch import (
    get_store_day,
    get_target_vs_actual,
    compare_store_revenue,
    compare_store_metric,
    get_inventory,
    get_feedback,
)
from agent.answer import make_answer
from agent.retry import run_with_retry
from tools.weather import get_weather


SESSIONS = {}
MAX_TOKENS = 150


def handle(question, session_id, user_id="u1"):
    started = time.perf_counter()

    context = SESSIONS.get(session_id, {})
    parsed = understand(question, context)

    intent = parsed["intent"]
    store = parsed.get("store")
    date = parsed.get("date")
    metric = parsed.get("metric")
    start_date = parsed.get("start_date")
    end_date = parsed.get("end_date")
    missing = parsed.get("missing", [])
    confidence = parsed.get("confidence", 0.0)

    tools_called = []
    route = "none"
    executed = False
    attempts = 0

    result = {
        "run_id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "intent": intent,
        "confidence": confidence,
        "route": route,
        "executed": executed,
        "attempts": attempts,
        "tools_called": tools_called,
        "status": "Safe Failure",
        "answer": "",
        "answer_text": "",
        "evidence": [],
        "grounded_values": [],
        "latency_ms": 0,
        "tokens_est": 0,
        "tool_calls": 0,
        "ungrounded_numbers": 0,
        "budget_exceeded": False,
    }

    try:
        if intent == "out_of_scope":
            result["status"] = "Escalated"
            result["answer"] = (
                "This request is outside the agent's "
                "authorized business reporting scope. "
                "Human review is required."
            )

        elif intent == "unsupported_metric":
            result["status"] = "Safe Failure"
            result["answer"] = (
                "This metric is not approved for reporting. "
                "Only whitelisted metrics can be used."
            )

        elif intent == "diagnostic":
            result["status"] = "Escalated"
            result["answer"] = (
                "Root cause cannot be confirmed from "
                "descriptive data alone. Human review "
                "and additional evidence are required."
            )

        # All-store inventory questions do not need
        # a specific store name.
        elif (
            (confidence < 0.70 or missing)
            and not (
                intent == "inventory"
                and not store
                and set(missing).issubset({"store"})
            )
        ):
            result["status"] = "Clarification Needed"
            result["answer"] = (
                "Please clarify: "
                + ", ".join(missing or ["store or metric"])
                + "."
            )

        elif (
            (date and not (
                str(MIN_DATE)
                <= date
                <= str(MAX_DATE)
            ))
            or (
                start_date
                and start_date < str(MIN_DATE)
            )
            or (
                end_date
                and end_date > str(MAX_DATE)
            )
        ):
            result["status"] = "Safe Failure"
            result["answer"] = (
                "The requested date is outside the "
                "available dataset period."
            )

        elif intent == "comparison":
            route = "sql"
            executed = True
            tools_called.append("compare_store_metric")

            ascending = any(
                word in question.lower()
                for word in ["lowest", "worst"]
            )

            if start_date and end_date:
                first, last = start_date, end_date
            else:
                first, last = date, date

            retry = run_with_retry(
                lambda: compare_store_metric(
                    metric=metric or "revenue_inr",
                    start_date=first,
                    end_date=last,
                    ascending=ascending,
                ),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                result.update(
                    make_answer("comparison", retry["data"])
                )
            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Data retrieval failed after "
                    "3 attempts. Human review required."
                )

        elif intent == "inventory":
            route = "sql"
            executed = True
            tools_called.append("get_inventory")

            product = (
                "Amul Milk 1L"
                if "amul milk" in question.lower()
                else None
            )

            retry = run_with_retry(
                lambda: get_inventory(store, product),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                data = retry["data"]

                if "below" in question.lower():
                    data = [
                        row
                        for row in data
                        if row["below_threshold"]
                    ]

                result.update(
                    make_answer("inventory", data)
                )
            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Inventory retrieval failed "
                    "after 3 attempts."
                )

        elif intent == "feedback":
            route = "sql"
            executed = True
            tools_called.append("get_feedback")

            retry = run_with_retry(
                lambda: get_feedback(store),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                result.update(
                    make_answer("feedback", retry["data"])
                )
            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Feedback retrieval failed "
                    "after 3 attempts."
                )

        elif intent == "weather":
            route = "weather"
            executed = True
            tools_called.append("get_weather")

            retry = run_with_retry(
                lambda: get_weather(store, date),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                weather = retry["data"]

                result["status"] = "Answered"
                result["answer"] = (
                    f"{store} weather on {date}: "
                    f"temperature "
                    f"{weather['temperature_c']:.1f} C, "
                    f"humidity "
                    f"{weather['humidity_pct']:.1f}%, "
                    f"wind speed "
                    f"{weather['wind_speed_kmh']:.1f} km/h, "
                    f"rainfall "
                    f"{weather['rainfall_mm']:.1f} mm. "
                    "Simulated offline weather."
                )

                result["evidence"] = [{
                    "source": weather["source"],
                    "fields": [
                        "temperature_c",
                        "humidity_pct",
                        "wind_speed_kmh",
                        "rainfall_mm",
                    ],
                    "city": store,
                    "date": date,
                }]

                result["grounded_values"] = [
                    f"{weather['temperature_c']:.1f}",
                    f"{weather['humidity_pct']:.1f}",
                    f"{weather['wind_speed_kmh']:.1f}",
                    f"{weather['rainfall_mm']:.1f}",
                ]

                # Combined revenue + weather request (W01).
                if any(word in question.lower() for word in
                       ("revenue", "sales", "earned", "earn")):
                    tools_called.append("get_store_day")
                    revenue_retry = run_with_retry(
                        lambda: get_store_day(store, date, "revenue_inr"),
                        max_attempts=3,
                    )
                    attempts += revenue_retry["attempts"]

                    if not revenue_retry["success"]:
                        result["status"] = "Escalated"
                        result["answer"] = (
                            "Revenue retrieval failed after 3 attempts. "
                            "Human review required."
                        )
                        result["evidence"] = []
                        result["grounded_values"] = []
                    elif revenue_retry["data"] is None:
                        result["status"] = "Safe Failure"
                        result["answer"] = (
                            "Revenue data is unavailable for the "
                            "requested store and date."
                        )
                        result["evidence"] = []
                        result["grounded_values"] = []
                    else:
                        revenue_data = revenue_retry["data"]
                        amount = revenue_data["value"]
                        result["answer"] = (
                            f"{store} revenue on {date}: "
                            f"INR {amount:.2f}. "
                            + result["answer"]
                        )
                        result["evidence"].append({
                            "source": revenue_data["source"],
                            "fields": ["revenue_inr"],
                            "store": store,
                            "date": date,
                        })
                        result["grounded_values"].append(
                            f"INR {amount:.2f}"
                        )

            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Weather retrieval failed. "
                    "Human review required."
                )

        elif intent == "target_vs_actual":
            route = "python"
            executed = True
            tools_called.append("get_target_vs_actual")

            retry = run_with_retry(
                lambda: get_target_vs_actual(store, date),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                data = retry["data"]

                if data is None:
                    result.update(
                        make_answer("target_vs_actual", None)
                    )

                elif (
                    metric == "daily_target_inr"
                    and "achieve" not in question.lower()
                    and "achievement" not in question.lower()
                    and "performance" not in question.lower()
                ):
                    target_data = {
                        "store": store,
                        "date": date,
                        "metric": "daily_target_inr",
                        "value": data["daily_target_inr"],
                        "source": data["source"],
                    }

                    result.update(
                        make_answer("lookup", target_data)
                    )

                else:
                    result.update(
                        make_answer("target_vs_actual", data)
                    )

                    if (
                        data is not None
                        and data["performance_band"] == "Poor"
                    ):
                        result["status"] = "Drafted"

            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Target retrieval failed "
                    "after 3 attempts."
                )

        else:
            route = "python"
            executed = True
            tools_called.append("get_store_day")

            selected_metric = metric or "revenue_inr"

            retry = run_with_retry(
                lambda: get_store_day(
                    store,
                    date,
                    selected_metric,
                ),
                max_attempts=3,
            )
            attempts = retry["attempts"]

            if retry["success"]:
                result.update(
                    make_answer("lookup", retry["data"])
                )
            else:
                result["status"] = "Escalated"
                result["answer"] = (
                    "Data retrieval failed after "
                    "3 attempts. Human review required."
                )

        # Preserve metric for follow-up questions.
        if (
            store
            and result["status"] in ("Answered", "Drafted")
        ):
            SESSIONS[session_id] = {
                "store": store,
                "date": date,
                "metric": metric or "revenue_inr",
            }

    except Exception as exc:
        result["status"] = "Safe Failure"
        result["answer"] = (
            "The request could not be completed safely."
        )
        result["error"] = str(exc)

    result["route"] = route
    result["executed"] = executed
    result["attempts"] = attempts
    result["tools_called"] = tools_called
    result["tool_calls"] = len(tools_called)

    result["answer_text"] = result["answer"]

    result["latency_ms"] = round(
        (time.perf_counter() - started) * 1000,
        2,
    )

    # Offline estimate; not actual LLM token usage.
    result["tokens_est"] = (
        len(question.split())
        + len(result["answer"].split())
    )

    result["budget_exceeded"] = (
        result["tokens_est"] > MAX_TOKENS
    )

    log_path = Path(
        os.getenv(
            "AGENT_LOG_PATH",
            str(ROOT / "logs" / "runs.jsonl"),
        )
    )

    log_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with log_path.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(result, ensure_ascii=False)
            + "\n"
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
            "demo_session",
        )

        print("\nAgent:", response["answer"])
        print("Status:", response["status"])
