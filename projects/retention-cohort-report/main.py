import os

from flask import Flask, jsonify
from google.cloud import bigquery

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

# Share of each signup cohort that still holds a subscription N months later.
SQL = f"""
WITH cohorts AS (
  SELECT customer_id, DATE_TRUNC(DATE(signup_at), MONTH) AS cohort_month
  FROM `{BQ_PROJECT}.marts.dim_customers`
),
months AS (
  SELECT m AS month_offset FROM UNNEST(GENERATE_ARRAY(0, 11)) AS m
)
SELECT
  c.cohort_month,
  m.month_offset,
  COUNT(DISTINCT c.customer_id) AS cohort_size,
  COUNT(DISTINCT IF(
    s.started_at < TIMESTAMP(DATE_ADD(c.cohort_month, INTERVAL m.month_offset + 1 MONTH))
    AND (s.ended_at IS NULL
         OR s.ended_at >= TIMESTAMP(DATE_ADD(c.cohort_month, INTERVAL m.month_offset MONTH))),
    c.customer_id, NULL)) AS retained
FROM cohorts c
CROSS JOIN months m
LEFT JOIN `{BQ_PROJECT}.marts.fct_subscriptions` s USING (customer_id)
WHERE DATE_ADD(c.cohort_month, INTERVAL m.month_offset MONTH) <= CURRENT_DATE()
GROUP BY 1, 2
ORDER BY 1, 2
"""


@app.route("/health")
def health():
    return "ok"


@app.route("/")
def report():
    rows = bigquery.Client(project=BQ_PROJECT).query(SQL).result()
    return jsonify([
        {
            "cohort": str(r.cohort_month),
            "month": r.month_offset,
            "retention": round(r.retained / r.cohort_size, 4) if r.cohort_size else None,
        }
        for r in rows
    ])


@app.route("/cron")
def cron():
    return "ok"
