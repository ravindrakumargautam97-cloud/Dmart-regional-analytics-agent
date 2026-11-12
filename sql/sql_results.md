# DMart SQL Analysis — Verified Results

## Execution Details

- Database: SQLite 3.50.4
- Source: `data/store_daily_clean.csv`
- Records imported: 450
- SQL file: `sql/store_analysis.sql`
- Queries executed: 6
- Execution status: All six queries completed without SQL errors

## Key SQL Findings

| Metric | Finding |
|---|---|
| Highest average daily revenue | Mumbai — INR 1,064,371.60 |
| Lowest average daily revenue | Pune — INR 636,358.55 |
| Highest average target achievement | Mumbai — 101.37% |
| Highest average daily stockout hours | Hyderabad — 3.85 |
| Lowest average daily footfall | Pune — 1,517.71 |
| Most days below revenue target | Pune — 90 out of 90 |

## Days Below Daily Revenue Target

| Store | Days Below Target |
|---|---:|
| Pune | 90 |
| Ahmedabad | 76 |
| Hyderabad | 66 |
| Bengaluru | 55 |
| Mumbai | 40 |

## Monthly Revenue

| Store | April 2026 | May 2026 | June 2026 |
|---|---:|---:|---:|
| Ahmedabad | 22,889,946.94 | 24,764,328.70 | 22,783,987.24 |
| Bengaluru | 28,195,040.25 | 28,419,746.76 | 27,181,123.88 |
| Hyderabad | 26,335,304.26 | 27,909,854.71 | 26,145,811.88 |
| Mumbai | 32,065,974.83 | 33,220,035.01 | 30,507,434.11 |
| Pune | 18,905,212.65 | 19,940,791.64 | 18,426,265.49 |

## Interpretation

Pune requires priority management attention because it has the lowest average daily revenue and missed its daily revenue target on all 90 days.

Hyderabad has the highest average daily stockout hours and should be reviewed for inventory availability issues.

Mumbai leads average daily revenue and target achievement.

These findings describe observed performance differences; they do not prove that stockouts or any other individual factor caused the revenue gaps.

## Validation

All six SQL queries executed successfully against the 450-row SQLite table `store_daily_clean`.
