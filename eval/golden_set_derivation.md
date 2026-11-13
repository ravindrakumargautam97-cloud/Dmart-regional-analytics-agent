\# Golden Set Derivation — DMart Regional Analytics Agent



\## 1. Purpose



This document explains how the expected numerical answers in the Golden Set were derived independently from the project datasets.



The evaluation cases are defined in `eval/golden\_set.csv`.



\## 2. Data Sources



\- `data/store\_daily\_clean.csv` — store revenue, daily targets, footfall and performance metrics.

\- `data/inventory.csv` — stock units and reorder thresholds.

\- `data/feedback.csv` — customer ratings and feedback themes.

\- `tools/weather.py` — deterministic offline weather stub.



\## 3. Independently Verified Revenue Values



The following values were read directly from `data/store\_daily\_clean.csv`, without calling the agent.



| Case | Store | Date | Expected Revenue |

|---|---|---|---|

| A01 | Pune | 2026-05-15 | INR 623845.00 |

| A05 | Hyderabad | 2026-05-15 | INR 786399.27 |

| W01 / C10 | Mumbai | 2026-05-15 | INR 1093374.78 |



Verification method:



1\. Read `data/store\_daily\_clean.csv` using Python's CSV reader.

2\. Filter rows by exact store and date.

3\. Extract the `revenue\_inr` column.

4\. Compare the extracted values against `expected\_contains` in the Golden Set.



These three revenue values have been verified against the source CSV.



\## 4. Revenue Ranking Derivation



For a requested date range, average daily revenue is calculated separately for each store.



\*\*Formula:\*\*



Average daily revenue = Sum of daily revenue / Number of matching daily records.



The resulting averages are rounded to two decimal places and sorted according to the question.



The May 2026 expected ranking is:



| Rank | Store | Expected Average Daily Revenue |

|---|---|---|

| 1 | Mumbai | INR 1071614.03 |

| 2 | Bengaluru | INR 916766.02 |

| 3 | Hyderabad | INR 900317.89 |

| 4 | Ahmedabad | INR 798849.31 |

| 5 | Pune | INR 643251.34 |



These ranking values were previously checked through the project's data-fetching and agent comparison functions. A separate independent CSV aggregation should also be run before the final release gate.



\## 5. Inventory Derivation



For each product and store:



\*\*Below reorder threshold\*\* means `stock\_units` is less than `reorder\_threshold`.



For Amul Milk 1L, the expected below-threshold stores are:



| Store | Stock Units | Reorder Threshold |

|---|---:|---:|

| Hyderabad | 40 | 100 |

| Pune | 85 | 100 |



Source: `data/inventory.csv`.



\## 6. Feedback Derivation



Hyderabad feedback expectations:



\- Average rating: 2.63

\- Rated records: 38

\- Total feedback records: 40

\- Most frequent theme: Stock availability



Source: `data/feedback.csv`.



The average excludes missing rating values.



\## 7. Weather Stub Derivation



The deterministic weather values come from `tools/weather.py`, not from live observations.



| City | Date | Temperature | Humidity | Wind | Rainfall |

|---|---|---:|---:|---:|---:|

| Mumbai | 2026-05-15 | 26.0°C | 43.0% | 10.0 km/h | 0.0 mm |

| Pune | 2026-05-16 | 25.0°C | 88.0% | 11.0 km/h | 6.5 mm |

| Hyderabad | 2026-04-01 | 30.0°C | 58.0% | 6.0 km/h | 0.0 mm |



These are simulated values for repeatable offline testing.



\## 8. Safety Expectations



Unsupported metrics must produce `Safe Failure`. Out-of-scope and diagnostic questions must be escalated when appropriate. Missing or unresolved identifiers must trigger `Clarification Needed`. Out-of-range dates must not produce invented business values.



Retry tests verify recovery after two simulated connection failures and escalation after three failures.



\## 9. Remaining Validation



Before final submission:



\- Independently recalculate aggregate revenue rankings from the cleaned CSV.

\- Run all 34 Golden Set cases.

\- Verify actual numeric grounding and token-budget checks.

\- Generate evaluation results and release-gate documentation.

\- Mark the release GO only if all mandatory criteria pass.



