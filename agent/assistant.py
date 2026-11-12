
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "store_daily_clean.csv"

def load_data():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")
    return pd.read_csv(DATA_FILE)

def answer_question(question, df):
    q = question.lower().strip()

    if "pune" in q and any(word in q for word in ["why", "reason", "cause", "क्यों"]):
        pune = df[df["store"] == "Pune"]
        revenue = pune["revenue_inr"].mean()
        footfall = pune["footfall"].mean()
        regional_revenue = df["revenue_inr"].mean()
        regional_footfall = df["footfall"].mean()

        return (
            f"Pune average daily revenue: INR {revenue:,.2f}; "
            f"regional average: INR {regional_revenue:,.2f}. "
            f"Pune average footfall: {footfall:,.2f}; "
            f"regional average: {regional_footfall:,.2f}. "
            "Pune has lower revenue and footfall, but these figures "
            "do not establish the cause. Further investigation is required. "
            "Source: data/store_daily_clean.csv."
        )

    if "stockout" in q:
        result = df.groupby("store")["stockout_hours"].mean()
        store = result.idxmax()
        return (
            f"{store} has the highest average stockout duration: "
            f"{result.max():.2f} hours per day. "
            "Source: data/store_daily_clean.csv."
        )

    if "target" in q:
        result = df.groupby("store")["achievement_pct"].mean().sort_values(
            ascending=False
        )
        details = ", ".join(
            f"{store}: {value:.2f}%"
            for store, value in result.items()
        )
        return (
            f"Average daily target achievement: {details}. "
            "Source: data/store_daily_clean.csv."
        )

    if "revenue" in q:
        result = df.groupby("store")["revenue_inr"].mean().sort_values(
            ascending=False
        )
        details = ", ".join(
            f"{store}: INR {value:,.2f}"
            for store, value in result.items()
        )
        return (
            f"Average daily revenue: {details}. "
            "Source: data/store_daily_clean.csv."
        )

    return (
        "I cannot answer this question using the currently supported "
        "analysis rules. Please ask about Pune's performance, revenue, "
        "stockout hours, or target achievement."
    )

def main():
    df = load_data()
    print("DMart Regional Analytics Assistant")
    print("Loaded records:", len(df))
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        print("\nAnswer:", answer_question(question, df))

if __name__ == "__main__":
    main()
