
import re
from datetime import datetime, timedelta
from difflib import get_close_matches

AS_OF_DATE = datetime(2026, 6, 30)
MIN_DATE = datetime(2026, 4, 1)
MAX_DATE = datetime(2026, 6, 29)

STORES = [
    "Mumbai",
    "Pune",
    "Hyderabad",
    "Bengaluru",
    "Ahmedabad",
]

ALIASES = {"bangalore": "Bengaluru"}


def parse_date(question):
    q = question.lower()

    if "yesterday" in q:
        return (AS_OF_DATE - timedelta(days=1)).date().isoformat()

    iso = re.search(r"\b\d{4}-\d{2}-\d{2}\b", q)
    if iso:
        try:
            return datetime.strptime(
                iso.group(), "%Y-%m-%d"
            ).date().isoformat()
        except ValueError:
            return None

    match = re.search(
        r"\b(\d{1,2})\s+"
        r"(january|february|march|april|may|june|"
        r"july|august|september|october|november|december)"
        r"\s+(\d{4})\b",
        q,
    )

    if match:
        try:
            return datetime.strptime(
                match.group(), "%d %B %Y"
            ).date().isoformat()
        except ValueError:
            return None

    return None


def detect_store(question, context=None):
    q = question.lower()

    for alias, store in ALIASES.items():
        if re.search(r"\b" + alias + r"\b", q):
            return store

    for store in STORES:
        if re.search(r"\b" + store.lower() + r"\b", q):
            return store

    words = re.findall(r"[a-z]+", q)

    for word in words:
        match = get_close_matches(
            word, [s.lower() for s in STORES],
            n=1, cutoff=0.85
        )
        if match:
            return next(
                s for s in STORES
                if s.lower() == match[0]
            )

    if context and any(
        phrase in q
        for phrase in ["what about", "next day", "and then", "same store"]
    ):
        return context.get("store")

    return None


def understand(question, context=None):
    context = context or {}
    q = question.lower().strip()

    store = detect_store(question, context)
    date = parse_date(question)

    if "next day" in q and context.get("date"):
        try:
            previous = datetime.strptime(
                context["date"], "%Y-%m-%d"
            )
            date = (
                previous + timedelta(days=1)
            ).date().isoformat()
        except ValueError:
            pass

    intent = "lookup"
    if any(
        phrase in q
        for phrase in [
            "approve a salary",
            "salary increase",
            "approve salary",
            "change salary",
            "increase salary",
            "approve payment",
            "transfer money",
            "fire employee",
            "hire employee",
        ]
    ):
        return {
            "question": question,
            "intent": "out_of_scope",
            "store": store,
            "date": date,
            "confidence": 0.99,
        }
    if any(x in q for x in ["profit margin", "gross margin", "net profit"]):
        intent = "unsupported_metric"
    elif any(x in q for x in ["why", "diagnose", "root cause"]):
        intent = "diagnostic"
    elif any(x in q for x in ["weather", "rainfall", "temperature"]):
        intent = "weather"
    elif any(x in q for x in ["feedback", "rating", "complaint", "theme"]):
        intent = "feedback"
    elif any(x in q for x in ["inventory", "stock units", "reorder", "amul milk"]):
        intent = "inventory"
    elif any(x in q for x in ["compare", "highest", "lowest", "ranking", "rank"]):
        intent = "comparison"
    elif any(x in q for x in ["target", "achieve", "achievement"]):
        intent = "target_vs_actual"

    confidence = 0.95 if store or intent in (
        "comparison", "unsupported_metric", "diagnostic"
    ) else 0.60

    return {
        "question": question,
        "intent": intent,
        "store": store,
        "date": date,
        "confidence": confidence,
    }
