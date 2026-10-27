import os

from anthropic import Anthropic
from flask import Flask, jsonify, request
from google.cloud import bigquery

app = Flask(__name__)
BQ_PROJECT = os.environ["BQ_PROJECT"]

SYSTEM = f"""You write BigQuery SQL for business users of Kestrel Learning.
Tables in `{BQ_PROJECT}.marts`: dim_customers, fct_orders, fct_subscriptions, fct_bookings, fct_payments.
Definitions:
- Revenue = SUM(amount_usd) of fct_orders where status = 'SETTLED'.
- Active subscription = fct_subscriptions row with status != 'CANCELED'.
- Demo show-up rate = attended demos / all demo bookings (fct_bookings.booking_type = 'DEMO').
- Customer = row in dim_customers.
Return one SELECT statement and nothing else."""


def generate_sql(question):
    msg = Anthropic().messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=800,
        system=SYSTEM,
        messages=[{"role": "user", "content": question}],
    )
    return msg.content[0].text.strip().strip("`").removeprefix("sql").strip()


@app.route("/health")
def health():
    return "ok"


@app.route("/ask")
def ask():
    question = request.args["q"]
    sql = generate_sql(question)
    if not sql.lower().startswith("select"):
        return jsonify({"error": "not a SELECT", "sql": sql}), 400
    rows = bigquery.Client(project=BQ_PROJECT).query(sql).result()
    return jsonify({"sql": sql, "rows": [dict(r) for r in rows][:200]})
