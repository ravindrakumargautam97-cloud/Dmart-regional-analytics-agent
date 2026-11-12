

\# DMart Regional Analytics Agent - Data Context



\## 1. Dataset Overview



This project uses synthetic training data for five stores:

Mumbai, Pune, Hyderabad, Bengaluru and Ahmedabad.



Analysis period: 2026-04-01 to 2026-06-29.



| Dataset | Rows | Purpose |

|---|---:|---|

| store\_daily\_clean.csv | 450 | Daily store performance |

| inventory.csv | 40 | Product inventory and reorder levels |

| feedback.csv | 200 | Customer ratings and feedback themes |



The data is synthetic and does not represent actual DMart business records.



\## 2. Store Daily Dataset



Source: `data/store\_daily\_clean.csv`



Grain: One row per store per date.



Keys and filters:

\- `store\_id`: Store identifier

\- `store`: Store name

\- `date`: Date in YYYY-MM-DD format



Approved reportable metrics:



| Column | Type | Meaning |

|---|---|---|

| revenue\_inr | Numeric | Daily revenue in INR |

| daily\_target\_inr | Numeric | Daily revenue target in INR |

| footfall | Numeric | Daily customer footfall |

| stockout\_hours | Numeric | Daily stockout duration |

| discount\_pct | Numeric | Discount percentage |

| achievement\_pct | Numeric | Revenue target achievement percentage |

| performance\_band | Category | Daily performance classification |



\## 3. Inventory Dataset



Source: `data/inventory.csv`



Grain: One row per store-product combination.



Keys and labels:

\- `store\_id`

\- `store`

\- `product\_id`

\- `product`



Approved reportable metrics:

\- `stock\_units`: Available stock quantity

\- `reorder\_threshold`: Threshold for replenishment review



Inventory can be flagged when stock units fall below the reorder threshold.



\## 4. Customer Feedback Dataset



Source: `data/feedback.csv`



Grain: One row per customer feedback record.



Keys and labels may be used to identify and group records.



Approved reportable metrics:

\- `rating`: Customer rating

\- `theme`: Feedback category or theme



Supported summaries include average rating and most frequent feedback theme.



\## 5. Approved Metric Whitelist



The agent may report only these eleven metrics:



1\. revenue\_inr

2\. daily\_target\_inr

3\. footfall

4\. stockout\_hours

5\. discount\_pct

6\. achievement\_pct

7\. performance\_band

8\. stock\_units

9\. reorder\_threshold

10\. rating

11\. theme



Store, date, product and identifier fields may be used as filters, grouping keys or labels, but not as business metrics.



Marketing spend, profit margin, conversion rate and other non-whitelisted metrics must not be reported.



\## 6. Data Relationships



\- Store daily data joins to inventory using `store\_id`.

\- Store daily data joins to feedback using the appropriate store identifier.

\- Daily store data has a date dimension.

\- Inventory and feedback must not be treated as daily records unless their actual date fields support that interpretation.

\- Avoid row multiplication when joining datasets with different grains.



\## 7. Data Quality



Raw daily dataset:

\- 453 records

\- 3 exact duplicate records

\- 4 missing footfall values

\- 1 negative footfall value

\- 2 extreme footfall values capped



Cleaned daily dataset:

\- 450 records

\- 90 records per store

\- No missing values

\- No negative footfall

\- Six derived analytical fields



Cleaning details are recorded in:

\- `analysis/data\_quality\_report.md`

\- `analysis/cleaning\_log.csv`



\## 8. Supported Questions



Examples:



\- What was Pune's revenue on 15 May 2026?

\- Did Pune achieve its daily target?

\- Which store had the highest revenue in May 2026?

\- What was Mumbai's performance band on 21 May 2026?

\- Is Amul Milk below its reorder threshold in Hyderabad?

\- What is Hyderabad's average customer rating?

\- Which feedback theme occurs most often in Hyderabad?



\## 9. Unsupported Questions



The agent must refuse or clarify requests for:

\- Profit margin or other unapproved business metrics

\- Stores absent from the dataset

\- Dates outside the available period

\- Unavailable data or unsupported calculations



The agent must not invent missing values.



\## 10. Data Limitations



The datasets are synthetic, cover only five stores and a limited historical period.



Observed correlations and descriptive patterns do not establish causation.



Weather information is obtained separately through the weather tool and is not a column in the store datasets.



