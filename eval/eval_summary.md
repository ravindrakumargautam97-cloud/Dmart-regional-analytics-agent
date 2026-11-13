# DMart Golden Set Evaluation Summary

- Total cases: 34
- Passed: 34
- Failed: 0
- Pass rate: 100.00%
- Average latency: 9.14 ms
- Estimated tokens: 693
- Total tool calls: 21
- Agent-reported ungrounded numbers: 0
- Agent-reported budget violations: 0

## Release Checks

- Quality >= 90%: True
- Safety cases pass: True
- Reported grounding count zero: True
- Reported budget violations zero: True
- Independent numerical grounding audit: PASS
- Audit details: All golden-set cases independently verified
- Release decision: **GO**

## Category Counts

- ambiguity: 2
- comparison: 3
- diagnostic: 1
- feedback: 1
- follow_up: 2
- injection: 1
- inventory: 1
- lookup: 2
- out_of_range_date: 2
- out_of_scope: 2
- retry: 2
- synonym: 2
- target_vs_actual: 3
- typo: 2
- unresolved_date: 1
- unresolved_store: 3
- unsupported_metric: 2
- weather: 2

## Failed Cases

None

## Limitations

Agent-reported ungrounded_numbers is not an independent proof.
The separate grounding audit recomputes source-backed claims
for the 34-case golden set; arbitrary future queries are not audited.
