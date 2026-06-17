from datetime import datetime


def normalize_action_data(form_data):
    action_name = form_data.get("action_name", "").strip()
    carbon_saved = form_data.get("carbon_saved", "0")
    completed_date = form_data.get("completed_date")

    try:
        saved = float(carbon_saved)
        if saved < 0:
            saved = 0.0
    except (TypeError, ValueError):
        saved = 0.0

    if not completed_date:
        completed_date = datetime.utcnow().date().isoformat()

    return {
        "action_name": action_name or "Sustainability action",
        "carbon_saved": round(saved, 2),
        "completed_date": completed_date,
    }
