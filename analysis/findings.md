# DMart Regional Analytics - Findings

## Dataset Overview

- Period: 2026-04-01 to 2026-06-29
- Cleaned records: 450
- Stores: 5
- Source: Synthetic practice data

## Store Performance Summary

| Store | Mean Daily Revenue | Mean Footfall | Mean Stockout Hours | Revenue per Footfall | Mean Achievement % | Poor Days |
|---|---:|---:|---:|---:|---:|---:|
| Ahmedabad | 782647.37 | 1922.59 | 3.19 | 407.08 | 92.08 | 1 |
| Bengaluru | 931065.68 | 2076.86 | 2.38 | 448.31 | 98.01 | 0 |
| Hyderabad | 893233.01 | 2209.51 | 3.85 | 404.27 | 94.02 | 0 |
| Mumbai | 1064371.60 | 2391.27 | 1.93 | 445.11 | 101.37 | 0 |
| Pune | 636358.55 | 1517.71 | 2.32 | 419.29 | 70.71 | 70 |
| All stores | 861535.24 | 2023.59 | 2.74 | 425.75 | 91.24 | 71 |

## Pune Stockout Premise Test

Stockout ranking (highest to lowest):

1. Hyderabad: 3.85 hours
2. Ahmedabad: 3.19 hours
3. Bengaluru: 2.38 hours
4. Pune: 2.32 hours
5. Mumbai: 1.93 hours

Pune ranks fourth of five stores by average stockout hours.
Pune does not have the highest stockout hours.
Therefore, the premise that Pune has the most stockouts is not supported.

## Pearson Correlations

| Relationship | Correlation |
|---|---:|
| All stores: Revenue vs Stockout | -0.152 |
| All stores: Revenue vs Footfall | 0.918 |
| Pune: Revenue vs Stockout | -0.254 |
| Pune: Revenue vs Footfall | 0.735 |
| Raw deduplicated: Revenue vs Footfall | 0.548 |

Correlation does not establish causation.

## Facts

- Pune mean daily revenue is INR 636358.55.
- Pune mean daily footfall is 1517.71.
- Hyderabad mean stockout hours is 3.85.
- Mumbai mean daily revenue is INR 1064371.60.

## Insights

- Pune's low footfall is a stronger descriptive explanation of its revenue gap than stockout ranking.
- Hyderabad has the highest stockout hours, but Pune has the lowest revenue.

## Hypotheses (Unconfirmed)

- Hypothesis 1 (unconfirmed): Local demand or store accessibility may contribute to Pune's lower footfall. Needed data: catchment population, competitor locations and customer visits.
- Hypothesis 2 (unconfirmed): Product assortment or pricing may affect Pune's conversion. Needed data: transaction-level sales, SKU availability and competitor prices.
