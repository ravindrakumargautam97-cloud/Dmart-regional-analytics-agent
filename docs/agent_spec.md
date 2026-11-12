

\# DMart Regional Analytics Agent - Specification



\## 1. Purpose



Build a grounded conversational analytics agent for the Regional Director using synthetic store performance, inventory and feedback data.



The agent must provide accurate answers, use approved metrics, explain uncertainty and record auditable interactions.



\## 2. Architecture



The agent follows eight processing stages:



1\. Interpret

2\. Route

3\. Query

4\. Validate

5\. Calculate

6\. Synthesize

7\. Ground

8\. Record



Validation of requested metrics, stores, dates and query parameters must occur before executing a database query.



\## 3. Processing Pipeline



\### Interpret

Identify user intent, store, date, product and requested metric. Resolve supported follow-up questions using session context.



\### Route

Choose the correct data source or weather tool.



\### Query

Prepare a parameterized SQL query or approved Python lookup. Execute only after validation.



\### Validate

Check metric whitelist, store availability, date range, SQL safety and query parameters before execution. Reject unsupported requests.



\### Calculate

Perform deterministic aggregations, comparisons and target calculations.



\### Synthesize

Generate a concise response using retrieved results.



\### Ground

Attach relevant data source, filters and calculation evidence. Do not invent figures.



\### Record

Save interaction metadata, result status, latency, retries and errors to JSONL logs.



\## 4. Supported Intents



1\. lookup

2\. target\_vs\_actual

3\. comparison

4\. inventory

5\. feedback

6\. weather

7\. unsupported\_metric

8\. out\_of\_scope

9\. diagnostic



\## 5. Agent Status Values



| Status | Meaning |

|---|---|

| Answered | Verified answer returned |

| Drafted | Evidence-based analysis requiring human review |

| Clarification Needed | Missing or ambiguous information |

| Escalated | Human review required |

| Safe Failure | Unsupported or invalid request handled safely |



\## 6. Metric Whitelist



Only eleven metrics may be reported:



\- revenue\_inr

\- daily\_target\_inr

\- footfall

\- stockout\_hours

\- discount\_pct

\- achievement\_pct

\- performance\_band

\- stock\_units

\- reorder\_threshold

\- rating

\- theme



Store names, dates, product names and identifiers are permitted as filters and labels, not business metrics.



\## 7. Date Handling



Reference date: 2026-06-30.



Supported formats:

\- YYYY-MM-DD

\- D Month YYYY, with full month name

\- yesterday

\- between DATE and DATE



"Yesterday" resolves to 2026-06-29.



Supported dataset range: 2026-04-01 through 2026-06-29.



Unrecognized dates require clarification. Dates outside the supported range must produce a safe failure.



\## 8. Store and Context Handling



Supported stores:

\- Mumbai

\- Pune

\- Hyderabad

\- Bengaluru

\- Ahmedabad



Recognize Bangalore as an alias for Bengaluru.



Use fuzzy matching for clear spelling variations. Ask for clarification when a store cannot be resolved.



Maintain session context for follow-up questions such as "What about the next day?"



Do not carry context across unrelated sessions.



\## 9. Query and Safety Rules



\- Use parameterized SQL queries.

\- Permit only read-only queries.

\- Validate requested fields against the whitelist.

\- Do not execute arbitrary user-supplied SQL.

\- Do not report unsupported metrics.

\- Do not modify data.

\- Do not invent missing values.

\- Distinguish facts from unconfirmed hypotheses.

\- Do not claim correlation establishes causation.



\## 10. Confidence and Clarification



Minimum confidence threshold: 0.70.



If interpretation confidence is below 0.70, ask a clarification question rather than guessing.



Missing store, ambiguous date or unclear metric should trigger clarification.



\## 11. Retry Policy



Maximum query attempts: 3.



\- If the first two attempts fail and the third succeeds, return Answered.

\- If all three attempts fail, return Escalated.

\- Log the number of attempts and the error reason.



\## 12. Weather Tool



Use `tools/weather.py`.



Supported modes:

\- stub: deterministic offline weather output

\- live: historical weather through Open-Meteo



The stub must produce repeatable values for the same city and date.



Weather data must be labeled separately from store records.



Tool errors must not produce invented weather values.



\## 13. Agent Interface



Main entry point:



`agent/run\_agent.py`



Required function:



`handle(question, session\_id, user\_id="u1")`



Supporting modules:



\- `agent/understand.py`: intent and entity extraction

\- `agent/fetch.py`: safe data retrieval

\- `agent/answer.py`: grounded response generation



The handler should return the answer, status, supporting evidence and relevant execution metadata.



\## 14. Logging



Write one JSON object per interaction to:



`logs/runs.jsonl`



Include:

\- timestamp

\- session\_id

\- user\_id

\- question

\- intent

\- status

\- answer

\- evidence

\- confidence

\- attempts

\- latency

\- error details, if applicable



Logs must support acceptance testing and evaluation.



\## 15. Acceptance and Evaluation



Run the 20 required acceptance cases using:



`scripts/run\_acceptance.py`



Save results to:



\- `outputs/acceptance\_transcript.md`

\- `logs/runs.jsonl`



Evaluate at least 34 golden cases using:



`eval/run\_eval.py`



Produce:

\- `eval/eval\_results.csv`

\- `eval/eval\_runs.jsonl`

\- `eval/eval\_summary.md`



\## 16. Release Criteria



The agent may receive a GO decision only when:



\- All safety categories pass.

\- Overall evaluation accuracy is at least 90%.

\- Ungrounded numerical claims equal zero.

\- Budget-exceeded cases equal zero.



Otherwise, the release decision is NO-GO.



The decision must be documented in `docs/release\_gate.md`.



\## 17. Limitations



The datasets are synthetic and historical.



The agent is a decision-support tool, not an autonomous manager.



It cannot establish causal relationships from correlations or perform operational changes.



