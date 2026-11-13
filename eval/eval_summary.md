# DMart Golden Set Evaluation Summary

- Total cases: 34
- Passed: 34
- Failed: 0
- Pass rate: 100.00%

## Cost

- Mean tokens_est: 20.38
- Maximum tokens_est: 37
- Total tool_calls: 21
- Budget-exceeded cases: 0

## Latency

- Mean latency_ms: 10.84
- P90 latency_ms (linear interpolation): 14.07
- Maximum latency_ms: 135.87

## Quality

- Overall pass rate: 100.00%
- Total agent-reported ungrounded_numbers: 0
- Independent numerical grounding audit: PASS
- Audit details: All golden-set cases independently verified

### Category Pass Counts

- ambiguity: 2/2 PASS
- comparison: 3/3 PASS
- diagnostic: 1/1 PASS
- feedback: 1/1 PASS
- follow_up: 2/2 PASS
- injection: 1/1 PASS
- inventory: 1/1 PASS
- lookup: 2/2 PASS
- out_of_range_date: 2/2 PASS
- out_of_scope: 2/2 PASS
- retry: 2/2 PASS
- synonym: 2/2 PASS
- target_vs_actual: 3/3 PASS
- typo: 2/2 PASS
- unresolved_date: 1/1 PASS
- unresolved_store: 3/3 PASS
- unsupported_metric: 2/2 PASS
- weather: 2/2 PASS

## Safety

- Injection / unsupported_metric / out_of_scope pass rate: 100.00% (5/5)
- Non-answer replies containing INR figures: 0
- .gitignore explicitly lists .env: True
- Log validation: PASS

## Release Gate (four mandatory conditions)

- Gate 1, all required safety/ambiguity categories pass: PASS (13/13)
- Gate 2, overall pass rate >= 90%: PASS (100.00%)
- Gate 3, zero ungrounded numbers and independent audit passes: PASS (reported=0; audit=PASS)
- Gate 4, no budget-exceeded cases: PASS (0)
- Release decision: **GO**

## Failed Cases

None

## Limitations

Independent grounding covers this golden set only, not arbitrary future queries.
The agent-reported ungrounded_numbers field is not itself independent evidence.
