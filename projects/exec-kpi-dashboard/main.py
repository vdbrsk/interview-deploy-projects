from flask import Flask, render_template_string

from cube_client import CubeClient

app = Flask(__name__)

PAGE = """
<h1>Executive KPIs</h1>
<ul>
  <li>Revenue (last 30 days): ${{ "{:,.0f}".format(revenue) }}</li>
  <li>New customers (last 30 days): {{ customers }}</li>
  <li>Active subscriptions: {{ active }}</li>
  <li>Demo show-up rate (last 30 days): {{ "{:.1%}".format(showup) }}</li>
</ul>
<h2>Revenue by month</h2>
<table>{% for r in monthly %}<tr><td>{{ r["revenue.paid_at.month"][:7] }}</td><td>{{ r["revenue.revenue"] }}</td></tr>{% endfor %}</table>
"""


def _scalar(rows, member):
    return float(rows[0][member] or 0) if rows else 0.0


@app.route("/health")
def health():
    return "ok"


@app.route("/")
def dashboard():
    cube = CubeClient()
    revenue = cube.load({
        "measures": ["revenue.revenue"],
        "timeDimensions": [{"dimension": "revenue.paid_at", "dateRange": "last 30 days"}],
    })
    customers = cube.load({
        "measures": ["customers_overview.customers"],
        "timeDimensions": [{"dimension": "customers_overview.signup_at", "dateRange": "last 30 days"}],
    })
    active = cube.load({"measures": ["subscriptions_overview.active_subscriptions"]})
    showup = cube.load({
        "measures": ["bookings_overview.demo_show_up_rate"],
        "timeDimensions": [{"dimension": "bookings_overview.scheduled_at", "dateRange": "last 30 days"}],
    })
    monthly = cube.load({
        "measures": ["revenue.revenue"],
        "timeDimensions": [{"dimension": "revenue.paid_at", "granularity": "month", "dateRange": "last 6 months"}],
    })
    return render_template_string(
        PAGE,
        revenue=_scalar(revenue, "revenue.revenue"),
        customers=int(_scalar(customers, "customers_overview.customers")),
        active=int(_scalar(active, "subscriptions_overview.active_subscriptions")),
        showup=_scalar(showup, "bookings_overview.demo_show_up_rate"),
        monthly=monthly,
    )


@app.route("/cron")
def cron():
    return "ok"
