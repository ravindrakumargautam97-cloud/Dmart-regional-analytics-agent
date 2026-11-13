
from decimal import Decimal, ROUND_HALF_UP


def format_number(value, places=2):
    """Format numbers using ROUND_HALF_UP."""
    quantum = Decimal("1").scaleb(-places)
    number = Decimal(str(value)).quantize(
        quantum,
        rounding=ROUND_HALF_UP
    )
    return f"{number:.{places}f}"


def format_inr(value):
    """Format money without commas."""
    return f"INR {format_number(value)}"


def make_evidence(data, fields):
    """Create structured evidence from fetched data."""
    evidence = {
        "source": data.get("source", "data/store_daily_clean.csv"),
        "fields": fields,
    }

    if data.get("store"):
        evidence["store"] = data["store"]

    if data.get("date"):
        evidence["date"] = data["date"]

    return evidence


def make_answer(intent, data):
    """Convert verified data into a grounded answer."""

    if data is None:
        return {
            "status": "Safe Failure",
            "answer": "No matching record was found.",
            "evidence": [],
            "grounded_values": [],
        }

    if intent == "lookup":
        store = data["store"]
        date = data["date"]
        metric = data["metric"]
        value = data["value"]

        labels = {
            "revenue_inr": "revenue",
            "daily_target_inr": "daily target",
            "footfall": "footfall",
            "stockout_hours": "stockout hours",
            "discount_pct": "discount percentage",
            "achievement_pct": "target achievement",
            "performance_band": "performance band",
        }

        label = labels.get(metric, metric)

        if metric in ("revenue_inr", "daily_target_inr"):
            display_value = format_inr(value)
        elif metric in ("discount_pct", "achievement_pct"):
            display_value = f"{format_number(value)}%"
        elif metric == "performance_band":
            display_value = str(value)
        else:
            display_value = str(value)

        answer = (
            f"{store}'s {label} on {date} was "
            f"{display_value}. "
            f"Source: {data['source']}."
        )

        return {
            "status": "Answered",
            "answer": answer,
            "evidence": [make_evidence(data, [metric])],
            "grounded_values": [display_value],
        }

    if intent == "target_vs_actual":
        revenue = data["revenue_inr"]
        target = data["daily_target_inr"]
        achievement = data["achievement_pct"]
        band = data["performance_band"]

        met_target = revenue >= target

        answer = (
            f"{data['store']} on {data['date']}: "
            f"revenue {format_inr(revenue)}, "
            f"target {format_inr(target)}, "
            f"achievement {format_number(achievement)}%, "
            f"performance band {band}. "
            f"Target {'achieved' if met_target else 'not achieved'}. "
            f"Source: {data['source']}."
        )

        return {
            "status": "Answered",
            "answer": answer,
            "evidence": [
                make_evidence(
                    data,
                    [
                        "revenue_inr",
                        "daily_target_inr",
                        "achievement_pct",
                        "performance_band",
                    ],
                )
            ],
            "grounded_values": [
                format_inr(revenue),
                format_inr(target),
                f"{format_number(achievement)}%",
            ],
        }

    if intent == "comparison":
        if not data:
            return {
                "status": "Safe Failure",
                "answer": "No comparison data available.",
                "evidence": [],
                "grounded_values": [],
            }

        lines = [
            f"{i}. {row['store']}: "
            f"{format_inr(row['avg_revenue'])}"
            for i, row in enumerate(data, 1)
        ]

        return {
            "status": "Answered",
            "answer": (
                "Average daily revenue ranking:\n"
                + "\n".join(lines)
                + "\nSource: data/store_daily_clean.csv."
            ),
            "evidence": [
                {
                    "source": "data/store_daily_clean.csv",
                    "fields": ["revenue_inr"],
                    "aggregation": "average_by_store",
                }
            ],
            "grounded_values": [
                format_inr(row["avg_revenue"])
                for row in data
            ],
        }

    if intent == "inventory":
        if not data:
            return {
                "status": "Safe Failure",
                "answer": "No matching inventory records.",
                "evidence": [],
                "grounded_values": [],
            }

        lines = []
        grounded = []

        for row in data:
            condition = (
                "below reorder threshold"
                if row["below_threshold"]
                else "at or above reorder threshold"
            )

            lines.append(
                f"{row['store']} - {row['product']}: "
                f"{row['stock_units']} units, "
                f"threshold {row['reorder_threshold']} "
                f"({condition})."
            )

            grounded.extend([
                str(row["stock_units"]),
                str(row["reorder_threshold"]),
            ])

        return {
            "status": "Answered",
            "answer": (
                "\n".join(lines)
                + "\nSource: data/inventory.csv."
            ),
            "evidence": [
                {
                    "source": "data/inventory.csv",
                    "fields": [
                        "stock_units",
                        "reorder_threshold",
                    ],
                }
            ],
            "grounded_values": grounded,
        }

    if intent == "feedback":
        themes = data.get("themes", [])
        top_theme = (
            themes[0]["theme"] if themes else "Unavailable"
        )

        avg_rating = data.get("average_rating")
        rating_text = (
            format_number(avg_rating)
            if avg_rating is not None
            else "Unavailable"
        )

        answer = (
            f"{data['store']} feedback: "
            f"average rating {rating_text}, "
            f"rated records {data['rated_count']}, "
            f"total feedback {data['total_feedback']}, "
            f"most frequent theme {top_theme}. "
            f"Source: {data['source']}."
        )

        grounded = [
            str(data["rated_count"]),
            str(data["total_feedback"]),
        ]

        if avg_rating is not None:
            grounded.insert(0, rating_text)

        return {
            "status": "Answered",
            "answer": answer,
            "evidence": [
                make_evidence(
                    data,
                    ["rating", "theme"]
                )
            ],
            "grounded_values": grounded,
        }

    return {
        "status": "Safe Failure",
        "answer": "This request is not supported.",
        "evidence": [],
        "grounded_values": [],
    }
