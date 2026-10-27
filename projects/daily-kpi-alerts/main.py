import os

import requests
from flask import Flask

from cube_client import CubeClient

app = Flask(__name__)


def _value(rows, member):
    return float(rows[0][member] or 0) if rows else 0.0


def check_kpis():
    cube = CubeClient()
    alerts = []

    yesterday = _value(cube.load({
        "measures": ["revenue.revenue"],
        "timeDimensions": [{"dimension": "revenue.paid_at", "dateRange": "yesterday"}],
    }), "revenue.revenue")
    week_total = _value(cube.load({
        "measures": ["revenue.revenue"],
        "timeDimensions": [{"dimension": "revenue.paid_at", "dateRange": "last 7 days, excluding today"}],
    }), "revenue.revenue")
    baseline = week_total / 7
    drop = float(os.environ["REVENUE_DROP_THRESHOLD"])
    if baseline and yesterday < baseline * (1 - drop):
        alerts.append(f"Revenue yesterday ${yesterday:,.0f} vs 7-day avg ${baseline:,.0f}")

    showup = _value(cube.load({
        "measures": ["bookings_overview.demo_show_up_rate"],
        "timeDimensions": [{"dimension": "bookings_overview.scheduled_at", "dateRange": "last 7 days"}],
    }), "bookings_overview.demo_show_up_rate")
    if showup < float(os.environ["SHOWUP_FLOOR"]):
        alerts.append(f"Demo show-up rate (7d) {showup:.1%}")

    return alerts


@app.route("/health")
def health():
    return "ok"


@app.route("/cron")
def cron():
    alerts = check_kpis()
    if alerts:
        text = "KPI alert:\n- " + "\n- ".join(alerts)
        requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": text}, timeout=30)
    return {"alerts": len(alerts)}
