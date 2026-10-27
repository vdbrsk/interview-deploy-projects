import os

from flask import Flask, jsonify
from google.cloud import bigquery

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

# Ad-hoc: which acquisition channels bring customers who actually show up to the demo?
SQL = f"""
SELECT
  c.acquisition_channel,
  COUNT(DISTINCT b.customer_id) AS customers_with_demo,
  COUNT(DISTINCT IF(b.status = 'ATTENDED', b.customer_id, NULL)) AS customers_attended
FROM `{BQ_PROJECT}.marts.fct_bookings` b
JOIN `{BQ_PROJECT}.marts.dim_customers` c USING (customer_id)
WHERE b.booking_type = 'DEMO'
  AND b.scheduled_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 90 DAY)
GROUP BY 1
ORDER BY 2 DESC
"""


@app.route("/health")
def health():
    return "ok"


@app.route("/")
def analysis():
    rows = bigquery.Client(project=BQ_PROJECT).query(SQL).result()
    return jsonify([
        {
            "channel": r.acquisition_channel,
            "customers_with_demo": r.customers_with_demo,
            "show_up_rate": round(r.customers_attended / r.customers_with_demo, 3),
        }
        for r in rows
    ])
