from flask import Flask, jsonify

from cube_client import CubeClient

app = Flask(__name__)


@app.route("/health")
def health():
    return "ok"


@app.route("/")
def board():
    rows = CubeClient().load({
        "measures": [
            "bookings_overview.total_bookings",
            "bookings_overview.lessons_attended",
            "bookings_overview.demos_attended",
            "bookings_overview.demos_no_show",
        ],
        "dimensions": ["bookings_overview.tutor_id"],
        "timeDimensions": [{"dimension": "bookings_overview.scheduled_at", "dateRange": "last 30 days"}],
        "order": {"bookings_overview.total_bookings": "desc"},
        "limit": 50,
    })
    board = []
    for r in rows:
        total = int(r["bookings_overview.total_bookings"] or 0)
        lessons = int(r["bookings_overview.lessons_attended"] or 0)
        demos_ok = int(r["bookings_overview.demos_attended"] or 0)
        demos_missed = int(r["bookings_overview.demos_no_show"] or 0)
        board.append({
            "tutor_id": r["bookings_overview.tutor_id"],
            "utilization": round(lessons / total, 3) if total else None,
            "demo_show_up_rate": round(demos_ok / total, 3) if total else None,
            "demos_missed": demos_missed,
        })
    return jsonify(board)


@app.route("/cron")
def cron():
    return "ok"
