import os

import requests
from flask import Flask
from google.cloud import bigquery

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

# Active subscribers with fewer than 2 attended lessons in the last 30 days.
SQL = f"""
SELECT
  c.customer_id,
  c.country,
  s.subscription_id,
  s.monthly_price_usd,
  COUNT(b.booking_id) AS lessons_30d
FROM `{BQ_PROJECT}.marts.dim_customers` c
JOIN `{BQ_PROJECT}.marts.fct_subscriptions` s USING (customer_id)
LEFT JOIN `{BQ_PROJECT}.marts.fct_bookings` b
  ON b.customer_id = c.customer_id
 AND b.booking_type = 'LESSON'
 AND b.status = 'ATTENDED'
 AND b.scheduled_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
WHERE s.status = 'ACTIVE'
GROUP BY 1, 2, 3, 4
HAVING lessons_30d < 2
"""


def build_worklist():
    rows = list(bigquery.Client(project=BQ_PROJECT).query(SQL).result())
    return {
        "customers_at_risk": len(rows),
        "mrr_at_risk": sum(r.monthly_price_usd for r in rows),
        "tasks": [{"customer_id": r.customer_id, "reason": f"{r.lessons_30d} lessons in 30d"} for r in rows],
    }


@app.route("/health")
def health():
    return "ok"


@app.route("/cron")
def cron():
    payload = build_worklist()
    requests.post(os.environ["CRM_WEBHOOK_URL"], json=payload, timeout=30)
    return {"customers_at_risk": payload["customers_at_risk"]}
