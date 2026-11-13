# DMart Regional Analytics Agent — Release Gate Report

## 1. Acceptance Testing

- Total cases: 20
- Passed: 20
- Failed: 0
- Result: PASS (per latest acceptance run)
- Evidence: `outputs/acceptance_transcript.md`

## 2. Golden-Set Evaluation

- Total cases: 34
- Passed: 34
- Failed: 0
- Pass rate: 100.00%
- Required pass rate: at least 90%
- Result: PASS
- Evidence: `eval/eval_results.csv`, `eval/eval_runs.jsonl`, `eval/eval_summary.md`

## 3. Independent Numerical Grounding

- Cases audited: 34/34 PASS
- Numeric values independently checked: 49
- Audit decision: PASS
- Method: compare logged answers, evidence and grounded values with source CSV calculations and documented deterministic weather fixtures.
- Evidence: `eval/grounding_audit.py`, `eval/grounding_audit_report.md`
- Scope: the evaluated golden set only; this is not a guarantee for arbitrary future inputs.

## 4. Safety and Reliability

- Safety and ambiguity cases: PASS in the 34-case evaluation.
- Retry behavior and simulated failures: PASS in the evaluation.
- Evidence: `eval/eval_results.csv`, `eval/eval_summary.md`.

## 5. Budget Gate

- The automated evaluator checks the agent-reported `budget_exceeded` field for all evaluated cases.
- Latest evaluator release decision: GO, indicating its configured budget gate passed.
- Limitation: the budget flag is agent-reported; this is not an independent external API-cost audit. Inspect `agent/run_agent.py` and `eval/run_eval.py` before claiming actual provider spending is verified.

## 6. Weather Tool

- Evaluated weather responses use deterministic offline stub values.
- Stub weather values are simulated, not observed weather.
- Live-weather availability and behavior are not established by the golden-set audit.

## 7. Release Decision

**GO — for the evaluated offline assignment release gate.**

Basis: latest `py eval\\run_eval.py` output showed 34/34 evaluation cases PASS, independent audit 34/34 PASS with 49 numeric values checked, and `RELEASE DECISION: GO`.

This decision does not imply independent verification of real-world operational data, live API reliability or external provider costs.

## 8. Evidence and Reproduction

From the repository root, run:

```bash
python scripts/run_acceptance.py
python eval/run_eval.py
python eval/grounding_audit.py
```

Review:

- `outputs/acceptance_transcript.md`
- `eval/golden_set.csv`
- `eval/golden_set_derivation.md`
- `eval/eval_results.csv`
- `eval/eval_runs.jsonl`
- `eval/eval_summary.md`
- `eval/grounding_audit_report.md`
