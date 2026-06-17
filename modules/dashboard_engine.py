from .context_engine import build_context_summary
from .recommendation_engine import build_recommendations


def build_dashboard_payload(record, actions, total_saved, records):
    context = build_context_summary(record) if record else {}
    recommendations = build_recommendations(record) if record else {
        "easy": [],
        "medium": [],
        "advanced": [],
    }
    trend = [r["total_emission"] for r in reversed(records)]
    labels = [r["created_at"][0:10] for r in reversed(records)]
    breakdown = {
        "Transportation": record["transport_emission"],
        "Food": record["food_emission"],
        "Electricity": record["electricity_emission"],
        "Shopping": record["shopping_emission"],
        "Air Travel": record["flight_emission"],
    } if record else {}

    return {
        "context": context,
        "recommendations": recommendations,
        "trend": trend,
        "labels": labels,
        "breakdown": breakdown,
        "actions": actions,
        "total_saved": total_saved,
    }
