import csv
import io
import os

from flask import Flask
from google.cloud import bigquery, storage

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

SQL = f"""
SELECT
  FORMAT_DATE('%Y-%m', DATE(p.attempted_at)) AS month,
  p.processor,
  SUM(p.amount_usd) AS gross_collected,
  (SELECT SUM(o.amount_usd)
     FROM `{BQ_PROJECT}.marts.fct_orders` o
    WHERE o.status = 'SETTLED'
      AND o.order_type != 'REFUND'
      AND FORMAT_DATE('%Y-%m', DATE(o.paid_at)) = FORMAT_DATE('%Y-%m', DATE(p.attempted_at))) AS recognized_revenue
FROM `{BQ_PROJECT}.marts.fct_payments` p
WHERE p.attempted_at >= TIMESTAMP(DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH), MONTH))
GROUP BY 1, 2
ORDER BY 1, 2
"""


def build_csv():
    rows = bigquery.Client(project=BQ_PROJECT).query(SQL).result()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["month", "processor", "gross_collected", "recognized_revenue"])
    for r in rows:
        writer.writerow([r.month, r.processor, r.gross_collected, r.recognized_revenue])
    return buf.getvalue()


@app.route("/health")
def health():
    return "ok"


@app.route("/cron")
def cron():
    blob = storage.Client().bucket(os.environ["EXPORT_BUCKET"]).blob("finance/monthly_revenue.csv")
    blob.upload_from_string(build_csv(), content_type="text/csv")
    return "exported"
