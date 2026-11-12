
from pathlib import Path
import sqlite3
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

APPROVED_METRICS = {
    "revenue_inr",
    "daily_target_inr",
    "footfall",
    "stockout_hours",
    "discount_pct",
    "achievement_pct",
    "performance_band",
    "stock_units",
    "reorder_threshold",
    "rating",
    "theme",
}

DAILY_METRICS = APPROVED_METRICS & {
    "revenue_inr",
    "daily_target_inr",
    "footfall",
    "stockout_hours",
    "discount_pct",
    "achievement_pct",
    "performance_band",
}


def load_data():
    daily = pd.read_csv(DATA_DIR / "store_daily_clean.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    feedback = pd.read_csv(DATA_DIR / "feedback.csv")

    return daily, inventory, feedback


def get_store_day(store, date, metric="revenue_inr"):
    if metric not in DAILY_METRICS:
        raise ValueError("Unsupported metric")

    daily, _, _ = load_data()

    rows = daily[
        (daily["store"].str.lower() == store.lower())
        & (daily["date"] == date)
    ]

    if rows.empty:
        return None

    row = rows.iloc[0]

    return {
        "store": str(row["store"]),
        "date": str(row["date"]),
        "metric": metric,
        "value": row[metric].item()
        if hasattr(row[metric], "item")
        else row[metric],
        "source": "data/store_daily_clean.csv",
    }


def get_target_vs_actual(store, date):
    daily, _, _ = load_data()

    rows = daily[
        (daily["store"].str.lower() == store.lower())
        & (daily["date"] == date)
    ]

    if rows.empty:
        return None

    row = rows.iloc[0]

    return {
        "store": str(row["store"]),
        "date": str(row["date"]),
        "revenue_inr": float(row["revenue_inr"]),
        "daily_target_inr": float(row["daily_target_inr"]),
        "achievement_pct": float(row["achievement_pct"]),
        "performance_band": str(row["performance_band"]),
        "source": "data/store_daily_clean.csv",
    }


def compare_store_revenue(start_date=None, end_date=None):
    daily, _, _ = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        daily.to_sql("store_daily", conn, index=False)

        query = """
            SELECT
                store,
                ROUND(AVG(revenue_inr), 2) AS avg_revenue
            FROM store_daily
            WHERE (? IS NULL OR date >= ?)
              AND (? IS NULL OR date <= ?)
            GROUP BY store
            ORDER BY avg_revenue DESC
        """

        rows = conn.execute(
            query,
            (
                start_date, start_date,
                end_date, end_date,
            ),
        ).fetchall()

        return [
            {"store": store, "avg_revenue": value}
            for store, value in rows
        ]
    finally:
        conn.close()


def get_inventory(store, product=None):
    _, inventory, _ = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        inventory.to_sql("inventory", conn, index=False)

        query = """
            SELECT
                store,
                product,
                stock_units,
                reorder_threshold
            FROM inventory
            WHERE LOWER(store) = LOWER(?)
              AND (
                  ? IS NULL
                  OR LOWER(product) = LOWER(?)
              )
            ORDER BY product
        """

        rows = conn.execute(
            query, (store, product, product)
        ).fetchall()

        return [
            {
                "store": s,
                "product": p,
                "stock_units": int(stock),
                "reorder_threshold": int(threshold),
                "below_threshold": stock < threshold,
            }
            for s, p, stock, threshold in rows
        ]
    finally:
        conn.close()


def get_feedback(store):
    _, _, feedback = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        feedback.to_sql("feedback", conn, index=False)

        summary = conn.execute(
            """
            SELECT
                ROUND(AVG(rating), 2),
                COUNT(rating),
                COUNT(*)
            FROM feedback
            WHERE LOWER(store) = LOWER(?)
            """,
            (store,),
        ).fetchone()

        themes = conn.execute(
            """
            SELECT theme, COUNT(*) AS total
            FROM feedback
            WHERE LOWER(store) = LOWER(?)
            GROUP BY theme
            ORDER BY total DESC, theme ASC
            """,
            (store,),
        ).fetchall()

        return {
            "store": store,
            "average_rating": summary[0],
            "rated_count": summary[1],
            "total_feedback": summary[2],
            "themes": [
                {"theme": theme, "count": count}
                for theme, count in themes
            ],
            "source": "data/feedback.csv",
        }
    finally:
        conn.close()
