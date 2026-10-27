import os

import requests
from flask import Flask
from google.cloud import bigquery

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

SQL = f"""
SELECT
  DATE_TRUNC(DATE(o.paid_at), WEEK(MONDAY)) AS week,
  c.country,
  SUM(o.amount_usd) AS revenue
FROM `{BQ_PROJECT}.marts.fct_orders` o
JOIN `{BQ_PROJECT}.marts.dim_customers` c USING (customer_id)
WHERE o.status = 'SETTLED'
  AND o.paid_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 8 WEEK)
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
"""


def build_report():
    rows = list(bigquery.Client(project=BQ_PROJECT).query(SQL).result())
    lines = [f"{r.week}  {r.country:<3} ${r.revenue:>12,.2f}" for r in rows]
    return "Weekly revenue by country\n" + "\n".join(lines)


@app.route("/health")
def health():
    return "ok"


@app.route("/cron")
def cron():
    requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": build_report()}, timeout=30)
    return "sent"
