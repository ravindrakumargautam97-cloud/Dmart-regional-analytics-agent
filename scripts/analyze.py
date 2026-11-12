
from pathlib import Path
import pandas as pd

DATA = Path("data")
ANALYSIS = Path("analysis")
ANALYSIS.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "store_daily_clean.csv")
raw = pd.read_csv(DATA / "store_daily.csv")
log = pd.read_csv(ANALYSIS / "cleaning_log.csv")

assert len(df) == 450, "Expected 450 cleaned rows"
assert len(log) == 8, "Expected 8 cleaning changes"
assert df.isna().sum().sum() == 0, "Missing values found"

def store_metrics(data):
    return {
        "mean_revenue": data["revenue_inr"].mean(),
        "mean_footfall": data["footfall"].mean(),
        "mean_stockout": data["stockout_hours"].mean(),
        "revenue_per_footfall": (
            data["revenue_inr"].sum() / data["footfall"].sum()
        ),
        "mean_achievement": data["achievement_pct"].mean(),
        "poor_days": (data["performance_band"] == "Poor").sum()
    }

rows = []
for store, group in df.groupby("store"):
    rows.append({"Store": store, **store_metrics(group)})

rows.append({"Store": "All stores", **store_metrics(df)})

summary = pd.DataFrame(rows)
summary.to_csv(
    ANALYSIS / "store_summary.csv", index=False
)

# Correlations after cleaning
corr_all_stockout = df["revenue_inr"].corr(
    df["stockout_hours"]
)
corr_all_footfall = df["revenue_inr"].corr(
    df["footfall"]
)

pune = df[df["store"] == "Pune"]
corr_pune_stockout = pune["revenue_inr"].corr(
    pune["stockout_hours"]
)
corr_pune_footfall = pune["revenue_inr"].corr(
    pune["footfall"]
)

# Correlation before cleaning
raw = raw.drop_duplicates()
raw = raw.dropna(subset=["footfall"])
corr_raw_footfall = raw["revenue_inr"].corr(
    raw["footfall"]
)

# Stockout ranking
ranking = (
    df.groupby("store")["stockout_hours"]
    .mean()
    .sort_values(ascending=False)
)

def fmt(value):
    return f"{value:.2f}"

lines = [
    "# DMart Regional Analytics - Findings",
    "",
    "## Dataset Overview",
    "",
    "- Period: 2026-04-01 to 2026-06-29",
    "- Cleaned records: 450",
    "- Stores: 5",
    "- Source: Synthetic practice data",
    "",
    "## Store Performance Summary",
    "",
    "| Store | Mean Daily Revenue | Mean Footfall | "
    "Mean Stockout Hours | Revenue per Footfall | "
    "Mean Achievement % | Poor Days |",
    "|---|---:|---:|---:|---:|---:|---:|",
]

for _, r in summary.iterrows():
    lines.append(
        f"| {r['Store']} | "
        f"{fmt(r['mean_revenue'])} | "
        f"{fmt(r['mean_footfall'])} | "
        f"{fmt(r['mean_stockout'])} | "
        f"{fmt(r['revenue_per_footfall'])} | "
        f"{fmt(r['mean_achievement'])} | "
        f"{int(r['poor_days'])} |"
    )

lines += [
    "",
    "## Pune Stockout Premise Test",
    "",
    "Stockout ranking (highest to lowest):",
    ""
]

for i, (store, value) in enumerate(ranking.items(), 1):
    lines.append(f"{i}. {store}: {value:.2f} hours")

lines += [
    "",
    "Pune ranks fourth of five stores by average stockout hours.",
    "Pune does not have the highest stockout hours.",
    "Therefore, the premise that Pune has the most stockouts "
    "is not supported.",
    "",
    "## Pearson Correlations",
    "",
    "| Relationship | Correlation |",
    "|---|---:|",
    f"| All stores: Revenue vs Stockout | {corr_all_stockout:.3f} |",
    f"| All stores: Revenue vs Footfall | {corr_all_footfall:.3f} |",
    f"| Pune: Revenue vs Stockout | {corr_pune_stockout:.3f} |",
    f"| Pune: Revenue vs Footfall | {corr_pune_footfall:.3f} |",
    f"| Raw deduplicated: Revenue vs Footfall | {corr_raw_footfall:.3f} |",
    "",
    "Correlation does not establish causation.",
    "",
    "## Facts",
    "",
    "- Pune mean daily revenue is INR 636358.55.",
    "- Pune mean daily footfall is 1517.71.",
    "- Hyderabad mean stockout hours is 3.85.",
    "- Mumbai mean daily revenue is INR 1064371.60.",
    "",
    "## Insights",
    "",
    "- Pune's low footfall is a stronger descriptive "
    "explanation of its revenue gap than stockout ranking.",
    "- Hyderabad has the highest stockout hours, "
    "but Pune has the lowest revenue.",
    "",
    "## Hypotheses (Unconfirmed)",
    "",
    "- Hypothesis 1 (unconfirmed): Local demand or store "
    "accessibility may contribute to Pune's lower footfall. "
    "Needed data: catchment population, competitor locations "
    "and customer visits.",
    "- Hypothesis 2 (unconfirmed): Product assortment or "
    "pricing may affect Pune's conversion. "
    "Needed data: transaction-level sales, SKU availability "
    "and competitor prices.",
]

(ANALYSIS / "findings.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8"
)

print("DMart Part A Analysis Completed!")
print()
print(summary.to_string(index=False))
print()
print("Correlations:")
print("All revenue-stockout:", round(corr_all_stockout, 3))
print("All revenue-footfall:", round(corr_all_footfall, 3))
print("Pune revenue-stockout:", round(corr_pune_stockout, 3))
print("Pune revenue-footfall:", round(corr_pune_footfall, 3))
print("Raw revenue-footfall:", round(corr_raw_footfall, 3))
print()
print("Saved analysis/findings.md")
print("Saved analysis/store_summary.csv")
