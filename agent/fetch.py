
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
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


def round_half_up(value, places=2):
    """Round numerical values using ROUND_HALF_UP."""
    quantum = Decimal("1").scaleb(-places)
    return float(
        Decimal(str(value)).quantize(
            quantum, rounding=ROUND_HALF_UP
        )
    )


def load_data():
    """Load the cleaned DMart datasets."""
    daily = pd.read_csv(
        DATA_DIR / "store_daily_clean.csv"
    )
    inventory = pd.read_csv(
        DATA_DIR / "inventory.csv"
    )
    feedback = pd.read_csv(
        DATA_DIR / "feedback.csv"
    )

    return daily, inventory, feedback


def get_store_day(store, date, metric="revenue_inr"):
    """Get an approved metric for a store and date."""
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
    value = row[metric]

    if hasattr(value, "item"):
        value = value.item()

    return {
        "store": str(row["store"]),
        "date": str(row["date"]),
        "metric": metric,
        "value": value,
        "source": "data/store_daily_clean.csv",
    }


def get_target_vs_actual(store, date):
    """Get revenue, target, achievement and band."""
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
        "daily_target_inr": float(
            row["daily_target_inr"]
        ),
        "achievement_pct": float(
            row["achievement_pct"]
        ),
        "performance_band": str(
            row["performance_band"]
        ),
        "source": "data/store_daily_clean.csv",
    }


def compare_store_revenue(
    start_date=None,
    end_date=None,
    ascending=False
):
    """Compare average revenue across stores."""
    daily, _, _ = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        daily.to_sql(
            "store_daily", conn, index=False
        )

        query = """
            SELECT
                store,
                AVG(revenue_inr) AS avg_revenue
            FROM store_daily
            WHERE (? IS NULL OR date >= ?)
              AND (? IS NULL OR date <= ?)
            GROUP BY store
        """

        rows = conn.execute(
            query,
            (
                start_date, start_date,
                end_date, end_date,
            ),
        ).fetchall()

        results = [
            {
                "store": store,
                "avg_revenue": round_half_up(value),
            }
            for store, value in rows
        ]

        results.sort(
            key=lambda x: x["avg_revenue"],
            reverse=not ascending,
        )

        return results

    finally:
        conn.close()

def compare_store_metric(
    metric="revenue_inr",
    start_date=None,
    end_date=None,
    ascending=False,
):
    """Compare approved numeric metrics across stores."""
    allowed = {
        "revenue_inr",
        "footfall",
        "stockout_hours",
        "achievement_pct",
    }

    if metric not in allowed:
        raise ValueError("Unsupported comparison metric")

    daily, _, _ = load_data()
    conn = sqlite3.connect(":memory:")

    try:
        daily.to_sql("store_daily", conn, index=False)

        query = f"""
            SELECT store, AVG({metric}) AS avg_value
            FROM store_daily
            WHERE (? IS NULL OR date >= ?)
              AND (? IS NULL OR date <= ?)
            GROUP BY store
        """

        rows = conn.execute(
            query,
            (start_date, start_date, end_date, end_date),
        ).fetchall()

        results = [
            {
                "store": store,
                "avg_value": round_half_up(value),
                "metric": metric,
            }
            for store, value in rows
        ]

        results.sort(
            key=lambda row: row["avg_value"],
            reverse=not ascending,
        )
        return results

    finally:
        conn.close()


def get_inventory(store=None, product=None):
    """Get inventory for one store or all stores."""
    _, inventory, _ = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        inventory.to_sql(
            "inventory", conn, index=False
        )

        query = """
            SELECT
                store,
                product,
                stock_units,
                reorder_threshold
            FROM inventory
            WHERE (? IS NULL OR LOWER(store) = LOWER(?))
              AND (? IS NULL OR LOWER(product) = LOWER(?))
            ORDER BY store, product
        """

        rows = conn.execute(
            query,
            (store, store, product, product)
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
    """Summarize store feedback and frequent themes."""
    _, _, feedback = load_data()

    conn = sqlite3.connect(":memory:")

    try:
        feedback.to_sql(
            "feedback", conn, index=False
        )

        summary = conn.execute(
            """
            SELECT
                AVG(rating),
                COUNT(rating),
                COUNT(*)
            FROM feedback
            WHERE LOWER(store) = LOWER(?)
            """,
            (store,),
        ).fetchone()

        themes = conn.execute(
            """
            SELECT
                theme,
                COUNT(*) AS total
            FROM feedback
            WHERE LOWER(store) = LOWER(?)
            GROUP BY theme
            ORDER BY total DESC, theme ASC
            """,
            (store,),
        ).fetchall()

        avg_rating = (
            round_half_up(summary[0])
            if summary[0] is not None
            else None
        )

        return {
            "store": store,
            "average_rating": avg_rating,
            "rated_count": summary[1],
            "total_feedback": summary[2],
            "themes": [
                {
                    "theme": theme,
                    "count": count,
                }
                for theme, count in themes
            ],
            "source": "data/feedback.csv",
        }

    finally:
        conn.close()
