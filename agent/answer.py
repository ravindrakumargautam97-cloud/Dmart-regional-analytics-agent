
def format_inr(value):
    return f"INR {float(value):,.2f}"


def make_answer(intent, data):
    """
    Convert verified data into a grounded answer.
    """

    if data is None:
        return {
            "status": "Safe Failure",
            "answer": "No matching record was found.",
            "evidence": [],
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
            "evidence": [data],
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
            f"achievement {achievement:.2f}%, "
            f"performance band {band}. "
            f"Target {'achieved' if met_target else 'not achieved'}. "
            f"Source: {data['source']}."
        )

        return {
            "status": "Answered",
            "answer": answer,
            "evidence": [data],
        }

    if intent == "comparison":
        if not data:
            return {
                "status": "Safe Failure",
                "answer": "No comparison data available.",
                "evidence": [],
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
            "evidence": data,
        }

    if intent == "inventory":
        if not data:
            return {
                "status": "Safe Failure",
                "answer": "No matching inventory records.",
                "evidence": [],
            }

        lines = []
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

        return {
            "status": "Answered",
            "answer": (
                "\n".join(lines)
                + "\nSource: data/inventory.csv."
            ),
            "evidence": data,
        }

    if intent == "feedback":
        themes = data.get("themes", [])

        top_theme = (
            themes[0]["theme"] if themes else "Unavailable"
        )

        answer = (
            f"{data['store']} feedback: "
            f"average rating {data['average_rating']}, "
            f"rated records {data['rated_count']}, "
            f"total feedback {data['total_feedback']}, "
            f"most frequent theme {top_theme}. "
            f"Source: {data['source']}."
        )

        return {
            "status": "Answered",
            "answer": answer,
            "evidence": [data],
        }

    return {
        "status": "Safe Failure",
        "answer": "This request is not supported.",
        "evidence": [],
    }
