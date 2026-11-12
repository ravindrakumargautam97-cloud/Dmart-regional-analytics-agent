# DMart Regional Analytics — Data Quality Report

## 1. Dataset Information

- Data source: Synthetic training data generated with seed 2604
- Analysis period: 1 April 2026 to 29 June 2026
- Stores: Mumbai, Pune, Hyderabad, Bengaluru and Ahmedabad
- Original daily records: 453
- Records after cleaning: 450

## 2. Data Quality Issues

| Issue | Count | Treatment |
|---|---:|---|
| Exact duplicate records | 3 | Removed |
| Negative footfall | 1 | Converted to missing |
| Extreme footfall outliers | 2 | Capped using store-level IQR bounds |
| Missing footfall requiring imputation | 5 | Filled using store-level median |

The five imputed values include four originally missing values and one invalid negative value converted to missing.

## 3. Cleaning Methodology

1. Removed three exact duplicate rows.
2. Converted the negative Hyderabad footfall value (-150) to missing.
3. Calculated the first and third quartiles separately for each store.
4. Applied the 1.5 × IQR rule and capped two extreme footfall values.
5. Imputed five missing footfall values using the median of their respective stores.
6. Generated six analytical columns: `revenue_per_footfall`, `marketing_efficiency`, `achievement_pct`, `shortfall_inr`, `weekend_flag`, and `performance_band`.

## 4. Validation Results

- Final cleaned records: 450
- Stores covered: 5
- Daily records per store: 90
- Negative footfall remaining: 0
- Missing values remaining in the cleaned daily dataset: 0
- Footfall correction log entries: 8

The three removed duplicate records are not included in the eight-entry footfall correction log.

## 5. Audit Trail

Detailed corrections are recorded in `analysis/cleaning_log.csv`.

The cleaned dataset is available at `data/store_daily_clean.csv`.

## 6. Limitations

This report covers the daily store dataset. Inventory and customer feedback datasets require separate validation when used in subsequent analysis.

The dataset is synthetic and should not be interpreted as actual DMart operational performance.
