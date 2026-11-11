# DMart Regional Director Assistant — Work in Progress

**Status: Part A implemented and verified. Parts B, C and D are not yet implemented. Do not submit this repository as the final 100-mark deliverable.**

All datasets are synthetic training data generated with seed 2604, not actual DMart operational data.

## Purpose
Investigate whether Pune's low average daily revenue is explained by stockouts, starting with trustworthy data.

## Offline setup (Python 3.9+)
```bash
python -m pip install -r requirements.txt
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/analyze.py
```

The raw generator is copied unchanged from the assignment. Do not manually modify the raw CSVs.

## Part A files
- `scripts/generate_data.py`: creates three raw datasets
- `scripts/clean_data.py`: removes duplicates, treats negatives, caps IQR outliers, imputes per-store medians, adds six features
- `scripts/analyze.py`: writes data-quality, findings and executive summary reports
- `data/`: raw and cleaned CSVs
- `analysis/`: data quality, change log, findings, executive summary

## Key finding
Pune is lowest in mean daily revenue but fourth of five in mean stockout hours; the observed gap aligns more closely with lower footfall. Correlation does not prove causation.

## Remaining work before submission
Part B documentation, Part C executable analytics agent and its acceptance logs, Part D weather tool, evaluation harness, golden set, release decision and full README instructions. All must be committed on branch `main` and linked as `https://github.com/USERNAME/REPOSITORY/tree/main`.
