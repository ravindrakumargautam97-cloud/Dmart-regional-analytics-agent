

\# DMart Regional Analytics - Data Quality Report



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



1\. Removed three exact duplicate rows.

2\. Converted the negative Hyderabad footfall value (-150) to missing.

3\. Calculated first and third quartiles separately for each store.

4\. Applied the 1.5 x IQR rule and capped two extreme footfall values.

5\. Imputed five missing footfall values using store-level medians.

6\. Generated six analytical columns: `revenue_per_footfall`, `marketing_efficiency`, `achievement_pct`, `shortfall_inr`, `weekend_flag`, and `performance_band`.



## 4. Validation Results



- Final cleaned records: 450

- Stores covered: 5

- Daily records per store: 90

- Negative footfall remaining: 0

- Missing values remaining: 0

- Footfall correction log entries: 8



The three removed duplicates are not included in the eight-entry footfall correction log.



## 5. Audit Trail



Detailed corrections are recorded in `analysis/cleaning_log.csv`.



The cleaned dataset is available at `data/store_daily_clean.csv`.



## 6. Limitations



This report covers the daily store dataset. Inventory and customer feedback datasets require separate validation when used in subsequent analysis.



The dataset is synthetic and does not represent actual DMart operational performance.



## 7. Raw Data Profile



**Raw shape:** 453 rows x 9 columns



| Column | Data Type | Null Count |

|---|---|---:|

| date | str | 0 |

| store_id | str | 0 |

| store | str | 0 |

| footfall | float64 | 4 |

| revenue_inr | float64 | 0 |

| daily_target_inr | int64 | 0 |

| marketing_spend_inr | int64 | 0 |

| stockout_hours | float64 | 0 |

| discount_pct | float64 | 0 |



**Exact duplicate rows:** 3



**Raw footfall minimum:** -150



**Raw footfall maximum:** 9800



## 8. Store-Level Footfall IQR Bounds



The 1.5 x IQR method was applied separately for each store.



| Store | Lower Bound | Upper Bound |

|---|---:|---:|

| Ahmedabad | 1582.38 | 2281.38 |

| Bengaluru | 1563.50 | 2599.50 |

| Hyderabad | 1598.50 | 2810.50 |

| Mumbai | 1802.00 | 2986.00 |

| Pune | 1194.75 | 1832.75 |



Two extreme values were capped:



- Ahmedabad, 2026-05-26: 9800 to 2281.38

- Mumbai, 2026-04-09: 6100 to 2986.00



One negative value was converted to missing:



- Hyderabad, 2026-04-21: -150 to missing



Five missing values, including the invalid negative value, were subsequently filled using store-level medians.



All eight footfall corrections are documented in `analysis/cleaning_log.csv`.



