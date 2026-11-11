
import pandas as pd
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Project folders
DATA = Path("data")
ANALYSIS = Path("analysis")
DATA.mkdir(exist_ok=True)
ANALYSIS.mkdir(exist_ok=True)

# Load original data
df = pd.read_csv(DATA / "store_daily.csv")
print("Raw rows:", len(df))

# Step 1: Remove exact duplicates
df = df.drop_duplicates().copy()
print("Rows after duplicates removed:", len(df))

# Prepare cleaning log
changes = []

def log_change(store, date, old, new, rule):
    changes.append({
        "store": store,
        "date": date,
        "old_footfall": old,
        "new_footfall": new,
        "rule": rule
    })

# Step 2: Treat negative footfall as missing
df["footfall"] = pd.to_numeric(
    df["footfall"], errors="coerce"
)

for idx in df.index[df["footfall"] < 0]:
    old = df.at[idx, "footfall"]
    log_change(
        df.at[idx, "store"],
        df.at[idx, "date"],
        old, "", "negative_to_missing"
    )
    df.at[idx, "footfall"] = np.nan

# Round using HALF_UP
def round_half_up(value):
    return float(
        Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )
    )

# Step 3: Cap extreme values using per-store IQR
for store, group in df.groupby("store"):
    values = group["footfall"].dropna()
    q1 = values.quantile(0.25, interpolation="linear")
    q3 = values.quantile(0.75, interpolation="linear")
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    for idx in group.index:
        old = df.at[idx, "footfall"]
        if pd.isna(old):
            continue

        if old < lower or old > upper:
            new = round_half_up(
                lower if old < lower else upper
            )
            log_change(
                store, df.at[idx, "date"],
                old, new, "iqr_cap"
            )
            df.at[idx, "footfall"] = new

# Step 4: Fill missing footfall with store median
for store, group in df.groupby("store"):
    median = group["footfall"].median()

    for idx in group.index:
        if pd.isna(df.at[idx, "footfall"]):
            log_change(
                store, df.at[idx, "date"],
                "", median, "median_impute"
            )
            df.at[idx, "footfall"] = median

# Step 5: Create six feature columns
df["revenue_per_footfall"] = (
    df["revenue_inr"] / df["footfall"]
).apply(round_half_up)

df["marketing_efficiency"] = (
    df["revenue_inr"] / df["marketing_spend_inr"]
).apply(round_half_up)

df["achievement_pct"] = (
    df["revenue_inr"] / df["daily_target_inr"] * 100
).apply(round_half_up)

df["shortfall_inr"] = (
    df["daily_target_inr"] - df["revenue_inr"]
).apply(round_half_up)

dates = pd.to_datetime(df["date"])

df["weekend_flag"] = np.where(
    dates.dt.dayofweek >= 5, "Yes", "No"
)

df["performance_band"] = np.select(
    [
        df["achievement_pct"] >= 100,
        df["achievement_pct"] >= 75
    ],
    ["Excellent", "Good"],
    default="Poor"
)

# Step 6: Save cleaned data and cleaning log
df.to_csv(
    DATA / "store_daily_clean.csv",
    index=False,
    float_format="%.2f"
)

log_df = pd.DataFrame(
    changes,
    columns=[
        "store", "date", "old_footfall",
        "new_footfall", "rule"
    ]
)

log_df.to_csv(
    ANALYSIS / "cleaning_log.csv",
    index=False
)

# Validation
assert len(df) == 450
assert not df.isna().any().any()
assert (df["footfall"] >= 0).all()

assert (log_df["rule"] == "negative_to_missing").sum() == 1
assert (log_df["rule"] == "iqr_cap").sum() == 2
assert (log_df["rule"] == "median_impute").sum() == 5

print("Cleaning completed successfully!")
print("Clean rows:", len(df))
print("Cleaning log entries:", len(log_df))
print("Files saved successfully.")
