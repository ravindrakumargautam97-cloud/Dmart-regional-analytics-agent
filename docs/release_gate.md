

\# DMart Regional Analytics Agent

\## Release Gate Report



\### 1. Acceptance Testing

\- Total Cases: 20

\- Passed: 20

\- Failed: 0

\- Status: PASS



\### 2. Evaluation Testing

\- Total Cases: 36

\- Passed: 36

\- Failed: 0

\- Accuracy: 100%

\- Required Accuracy: 90%

\- Status: PASS



\### 3. Numerical Grounding

\- Revenue and Target: 10/10 PASS

\- Inventory and Feedback: 7/7 PASS

\- Store Comparison: 3/3 PASS

\- Weather Stub: 4/4 PASS

\- Total Verified: 24/24

\- Status: PASS for evaluated numerical cases



\### 4. Safety and Reliability

\- Safety evaluation cases: 7/7 PASS

\- Maximum Retry Attempts: 3

\- Retry Escalation: PASS

\- Error Logging: PASS



\### 5. Budget Verification

\- External API references in agent/ and tools/: None found

\- Budget tracking fields in logs: Not implemented

\- Explicit budget limit: Not specified

\- Budget-exceeded cases: Not independently verified

\- Status: PENDING



\### 6. Known Limitations

\- Weather live mode is not implemented.

\- Weather stub produces simulated, not observed, weather.

\- Budget tracking requires a documented policy and evidence.

\- Numerical grounding checks cover evaluated cases only.



\### 7. Release Decision



Decision: NO-GO (pending budget verification)



Reason:

Acceptance, evaluation, safety and numerical source checks

passed. However, the budget-exceeded release criterion

has not yet been independently verified.



\### 8. Evidence

\- outputs/acceptance\_transcript.md

\- outputs/final\_acceptance\_logs.jsonl

\- eval/eval\_results.csv

\- eval/eval\_runs.jsonl

\- eval/eval\_summary.md

\- eval/eval\_results.json

\- eval/eval\_report.md



