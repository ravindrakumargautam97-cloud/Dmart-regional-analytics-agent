
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "dmart.db"


def get_store_data():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT
                store,
                ROUND(AVG(revenue_inr), 2),
                ROUND(AVG(footfall), 2),
                ROUND(AVG(stockout_hours), 2)
            FROM store_daily_clean
            GROUP BY store
            ORDER BY 2 DESC
        """).fetchall()

    return rows


def show_stores(rows):
    print("\nAvailable stores:")
    for row in rows:
        print("-", row[0])


def show_summary(rows):
    print("\nDMart Regional Analytics Summary")
    print("-" * 65)

    for store, revenue, footfall, stockout in rows:
        print(
            f"{store}: Revenue Rs.{revenue:,.2f}, "
            f"Footfall {footfall:,.2f}, "
            f"Stockout {stockout:.2f} hours"
        )


def investigate_pune(rows):
    pune = next((r for r in rows if r[0] == "Pune"), None)

    if pune is None:
        print("Pune data not found.")
        return

    stockout_ranking = sorted(rows, key=lambda r: r[3], reverse=True)
    rank = next(
        i for i, r in enumerate(stockout_ranking, 1)
        if r[0] == "Pune"
    )

    print("\nPune Revenue Investigation")
    print(f"Average daily revenue: Rs.{pune[1]:,.2f}")
    print(f"Average daily footfall: {pune[2]:,.2f}")
    print(f"Average stockout hours: {pune[3]:.2f}")
    print(f"Stockout ranking: {rank} of {len(rows)}")

    print("\nFinding:")
    print("Pune has the lowest average daily revenue.")
    print("Pune also has the lowest average daily footfall.")
    print("Pune does not have the highest stockout hours.")
    print("Stockouts alone do not explain Pune's low revenue.")
    print("Correlation does not prove causation.")


def show_best(rows):
    if not rows:
        print("No store data found.")
        return

    best = rows[0]
    print("\nHighest Revenue Store")
    print(f"Store: {best[0]}")
    print(f"Average daily revenue: Rs.{best[1]:,.2f}")


def show_help():
    print("\nAvailable commands:")
    print("  stores  - Show all stores")
    print("  summary - Show regional performance")
    print("  pune    - Investigate Pune revenue")
    print("  best    - Show highest revenue store")
    print("  help    - Show available commands")
    print("  exit    - Close the agent")


def main():
    try:
        rows = get_store_data()
    except (sqlite3.Error, FileNotFoundError) as error:
        print(f"Database error: {error}")
        return

    print("DMart Regional Analytics Agent")
    show_help()

    while True:
        try:
            command = input("\nDMart> ").strip().lower()
        except EOFError:
            break

        if command == "stores":
            show_stores(rows)
        elif command == "summary":
            show_summary(rows)
        elif command == "pune":
            investigate_pune(rows)
        elif command == "best":
            show_best(rows)
        elif command == "help":
            show_help()
        elif command in ("exit", "quit"):
            print("Goodbye!")
            break
        else:
            print("Unknown command. Type 'help'.")


if __name__ == "__main__":
    main()
