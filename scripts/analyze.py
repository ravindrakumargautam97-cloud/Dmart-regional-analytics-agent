
from pathlib import Path
import pandas as pd

DATA = Path("data")
ANALYSIS = Path("analysis")
ANALYSIS.mkdir(exist_ok=True)

df = pd.read_csv(DATA / "store_daily_clean.csv")
log = pd.read_csv(ANALYSIS / "cleaning_log.csv")

assert len(df) == 450, "Expected 450 cleaned rows"
assert len(log) == 8, "Expected 8 cleaning log entries"

metrics = [
    "revenue_inr",
    "footfall",
    "stockout_hours",
    "achievement_pct",
    "marketing_efficiency",
]

summary = df.groupby("store")[metrics].mean().round(2)
summary.loc["ALL STORES"] = df[metrics].mean().round(2)

summary.to_csv(ANALYSIS / "store_summary.csv")

print("DMart Data Analysis Completed!")
print()
print(summary.to_string())
print()
print("Store summary saved to analysis/store_summary.csv")
