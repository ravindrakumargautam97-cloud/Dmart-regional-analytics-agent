# DMart Regional Analytics Agent

**Status:** Parts A–D implemented and evaluated. **Release decision: GO** for the tested golden-set scope (34/34 evaluation cases passed; independent grounding audit passed 34/34 cases and verified 49 numeric values).

> **Data notice:** All datasets are synthetic training data generated using seed `2604`. They do not represent actual DMart operations.

## Purpose

Analyze regional store performance and investigate whether Pune's lower average daily revenue is associated with stockouts, footfall, or other measurable factors. The project includes a rule-based analytics assistant that answers supported store questions using local datasets and records its evidence.

## Requirements and setup

- Python 3.9 or newer
- Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

To regenerate and analyze the synthetic data:

```bash
python scripts/generate_data.py
python scripts/clean_data.py
python scripts/analyze.py
```

The raw data generator is supplied for the assignment; do not manually edit generated raw CSV files.

## Project structure

| Path | Purpose |
| --- | --- |
| `data/` | Synthetic daily store, inventory, feedback, and cleaned datasets |
| `scripts/generate_data.py` | Deterministic synthetic data generation |
| `scripts/clean_data.py` | Data cleaning and derived features |
| `scripts/analyze.py` | Analysis and report generation |
| `analysis/` | Data quality report, cleaning log, findings, executive summary |
| `docs/` | Requirements, data context, agent specification, release criteria |
| `agent/` | Intent understanding, data retrieval, answer generation, orchestration |
| `tools/weather.py` | Weather lookup with deterministic offline stub |
| `scripts/run_acceptance.py` | Acceptance test runner |
| `outputs/` | Acceptance transcript and run records |
| `eval/golden_set.csv` | Evaluation cases |
| `eval/run_eval.py` | Evaluation runner and integrated release gate |
| `eval/grounding_audit.py` | Independent numeric grounding verifier |
| `eval/eval_results.csv` | Per-case evaluation results |
| `eval/eval_runs.jsonl` | Golden-set run logs |
| `eval/eval_summary.md` | Evaluation summary and release decision |
| `eval/grounding_audit_report.md` | Independent grounding audit results |

## How to test

From the repository root, run:

```bash
python scripts/run_acceptance.py
python eval/run_eval.py
```

To run the independent numeric audit separately, after generating evaluation logs:

```bash
python eval/grounding_audit.py
```

The evaluation runner also executes the independent audit as part of the release gate. Review `eval/eval_summary.md` and `eval/grounding_audit_report.md` for the recorded results.

## Verified evaluation results

| Check | Result |
| --- | --- |
| Golden-set evaluation | 34/34 passed (100%) |
| Independent grounding audit | 34/34 passed |
| Independently verified numeric values | 49 |
| Evaluation log records | 34 |
| Automated release decision | **GO** |

These results describe the tested golden-set cases, **not** a guarantee that arbitrary future questions or live weather results are correct. The audit verifies numeric claims against the included CSV data and documented deterministic weather fixtures. Weather responses using the offline stub are simulated, not live observations.

## Key analysis finding

Pune has the lowest mean daily revenue in the generated dataset but ranks fourth of five stores by mean stockout hours. The revenue gap aligns more closely with lower footfall in this synthetic sample. **Correlation does not establish causation.** See `analysis/findings.md` and `analysis/executive_summary.md` for details.

## Submission notes

- Commit project code, documentation, datasets, and evaluation evidence to the `main` branch.
- Do not commit `.env`, credentials, backup copies, or unrelated temporary files.
- Include the repository URL in the assignment submission.
