from .carbon_calculator import CATEGORY_LABELS


def _classify_transport(value):
    if value <= 1.0:
        return "Low Impact"
    if value <= 2.5:
        return "Medium Impact"
    return "High Impact"


def _classify_electricity(value):
    if value <= 1.8:
        return "Efficient"
    if value <= 3.5:
        return "Average"
    return "Heavy Usage"


def _classify_food(value):
    if value <= 2.5:
        return "Sustainable"
    if value <= 4.0:
        return "Moderate"
    return "High Emission"


def _classify_shopping(value):
    if value <= 1.5:
        return "Minimal"
    if value <= 3.0:
        return "Moderate"
    return "Frequent"


def _classify_flight(value):
    if value == 0:
        return "Low"
    if value <= 3.0:
        return "Moderate"
    return "High"


def build_context_summary(record):
    if not record:
        return {}

    transport_pattern = _classify_transport(record["transport_emission"])
    energy_pattern = _classify_electricity(record["electricity_emission"])
    diet_pattern = _classify_food(record["food_emission"])
    shopping_pattern = _classify_shopping(record["shopping_emission"])
    flight_pattern = _classify_flight(record["flight_emission"])

    categories = {
        "Transportation": record["transport_emission"],
        "Food": record["food_emission"],
        "Electricity": record["electricity_emission"],
        "Shopping": record["shopping_emission"],
        "Air Travel": record["flight_emission"],
    }
    ranked = sorted(categories.items(), key=lambda item: item[1], reverse=True)
    primary = ranked[0][0] if ranked else "None"
    secondary = ranked[1][0] if len(ranked) > 1 else "None"

    return {
        "transport_pattern": transport_pattern,
        "energy_pattern": energy_pattern,
        "diet_pattern": diet_pattern,
        "shopping_pattern": shopping_pattern,
        "flight_pattern": flight_pattern,
        "primary_source": primary,
        "secondary_source": secondary,
        "sustainability_score": record.get("carbon_score", 0),
        "monthly_total": record.get("total_emission", 0),
        "annual_total": round(record.get("total_emission", 0) * 12, 2),
        "profile_summary": f"Primary source: {primary}. Secondary source: {secondary}.",
    }
