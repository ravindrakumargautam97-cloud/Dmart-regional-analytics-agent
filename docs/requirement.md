

\# DMart Regional Analytics Agent - Requirements



\## 1. Business Outcome



Provide a grounded conversational analytics assistant that helps the Regional Director understand store performance, investigate operational issues, and identify questions requiring further investigation.



The assistant must use the supplied synthetic datasets rather than inventing business figures.



\## 2. Stakeholders



\- Regional Director: compare store performance and review risks.

\- Store Managers: understand revenue, footfall and target gaps.

\- Inventory Managers: investigate stock availability.

\- Data Analyst: verify calculations, evidence and data quality.



\## 3. Scope



The assistant will:



\- Answer supported questions about store revenue, targets, footfall, stockouts and discounts.

\- Compare stores and report performance bands.

\- Check inventory stock against reorder thresholds.

\- Summarize customer ratings and feedback themes.

\- Provide historical weather information through the weather tool.

\- Understand supported dates, store names and follow-up questions.

\- Provide evidence, calculations and clear uncertainty.

\- Record each interaction for evaluation and audit.



\## 4. Decision Boundary



The assistant provides analysis and recommendations for human review. It does not make autonomous business decisions.



It must distinguish observed facts from interpretations and unconfirmed hypotheses.



\## 5. Prohibited Actions



The assistant must not:



1\. Invent revenue, stock, feedback or weather figures.

2\. Report unsupported metrics such as profit margin.

3\. Modify store records, inventory or financial data.

4\. Place purchase orders or approve inventory transfers.

5\. Claim correlation proves causation.

6\. Present synthetic data as actual DMart business results.



\## 6. Supported Answer Example



Question: What was Pune's revenue on 15 May 2026?



Expected behavior: Retrieve the Pune record for the requested date, report INR 623,845.00, and identify the dataset as the source.



\## 7. Refusal Example



Question: What was Pune's profit margin on 15 May 2026?



Expected behavior: Explain that profit margin is not an approved reportable metric and cannot be calculated from the available approved fields. Do not invent a percentage.



\## 8. Clarification Example



Question: What was Kolkata's revenue?



Expected behavior: Ask for a supported store because Kolkata is not present in the dataset.



\## 9. Success Criteria



\- Answers use only approved metrics and verified records.

\- Unsupported requests are handled safely.

\- Missing or ambiguous information triggers clarification.

\- Answers include relevant evidence.

\- Interactions are logged.

\- Acceptance and evaluation results are documented.



