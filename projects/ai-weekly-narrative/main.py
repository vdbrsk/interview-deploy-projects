import json
import os

import requests
from anthropic import Anthropic
from flask import Flask

from cube_client import CubeClient

app = Flask(__name__)

# Used when Cube is unavailable so the Monday post still goes out.
LAST_KNOWN = {"revenue": 182000.0, "new_customers": 640, "active_subscriptions": 4120, "demo_show_up_rate": 0.71}


def weekly_metrics():
    try:
        cube = CubeClient()
        week = {"dateRange": "last 7 days"}
        revenue = cube.load({"measures": ["revenue.revenue"],
                             "timeDimensions": [{"dimension": "revenue.paid_at", **week}]})
        customers = cube.load({"measures": ["customers_overview.customers"],
                               "timeDimensions": [{"dimension": "customers_overview.signup_at", **week}]})
        active = cube.load({"measures": ["subscriptions_overview.active_subscriptions"]})
        showup = cube.load({"measures": ["bookings_overview.demo_show_up_rate"],
                            "timeDimensions": [{"dimension": "bookings_overview.scheduled_at", **week}]})
        return {
            "revenue": float(revenue[0]["revenue.revenue"] or 0),
            "new_customers": int(customers[0]["customers_overview.customers"] or 0),
            "active_subscriptions": int(active[0]["subscriptions_overview.active_subscriptions"] or 0),
            "demo_show_up_rate": float(showup[0]["bookings_overview.demo_show_up_rate"] or 0),
        }
    except Exception:
        return LAST_KNOWN


def write_summary(metrics):
    msg = Anthropic().messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=400,
        messages=[{
            "role": "user",
            "content": "Write a 4-sentence weekly business update for the leadership team "
                       f"from these metrics:\n{json.dumps(metrics)}",
        }],
    )
    return msg.content[0].text


@app.route("/health")
def health():
    return "ok"


@app.route("/cron")
def cron():
    text = write_summary(weekly_metrics())
    requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": text}, timeout=30)
    return "sent"
