from .utils import validate_category_value

CATEGORY_LABELS = ["transportation", "electricity", "food", "shopping", "flight"]

TRANSPORT_EMISSIONS = {
    "bicycle": 0.5,
    "walking": 0.4,
    "bus": 1.2,
    "train": 1.0,
    "car": 2.5,
    "electric_vehicle": 1.2,
}

FOOD_EMISSIONS = {
    "vegan": 1.8,
    "vegetarian": 2.5,
    "mixed": 3.6,
    "heavy_meat": 5.2,
}

ELECTRICITY_EMISSIONS = {
    "low": 1.5,
    "medium": 2.8,
    "high": 4.5,
}

SHOPPING_EMISSIONS = {
    "low": 1.0,
    "medium": 2.2,
    "high": 3.8,
}

FLIGHT_EMISSIONS = {
    "never": 0.0,
    "occasionally": 3.0,
    "frequently": 6.8,
}

CATEGORY_OPTIONS = {
    "transport": list(TRANSPORT_EMISSIONS.keys()),
    "food": list(FOOD_EMISSIONS.keys()),
    "electricity": list(ELECTRICITY_EMISSIONS.keys()),
    "shopping": list(SHOPPING_EMISSIONS.keys()),
    "flight": list(FLIGHT_EMISSIONS.keys()),
}

CATEGORY_LABELS = {
    "transport": "Transportation",
    "food": "Food",
    "electricity": "Electricity",
    "shopping": "Shopping",
    "flight": "Air Travel",
}

CATEGORY_DISPLAY = {
    "heavy_meat": "Heavy Meat",
    "mixed": "Mixed Diet",
    "electric_vehicle": "Electric Vehicle",
    "occasionally": "Occasionally",
    "frequently": "Frequently",
    "never": "Never",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
}

EMISSION_MAP = {
    "transport": TRANSPORT_EMISSIONS,
    "food": FOOD_EMISSIONS,
    "electricity": ELECTRICITY_EMISSIONS,
    "shopping": SHOPPING_EMISSIONS,
    "flight": FLIGHT_EMISSIONS,
}

MULTIPLIER = {
    "transport": 4.0,
    "food": 1.0,
    "electricity": 1.0,
    "shopping": 1.0,
    "flight": 1.0,
}


def calculate_emissions(form_data):
    values = {}
    breakdown = {}

    for category, options in EMISSION_MAP.items():
        selected_value = form_data.get(category)
        emission_value = options.get(selected_value, 0)
        total_value = round(emission_value * MULTIPLIER[category], 2)
        values[category] = total_value
        breakdown[CATEGORY_LABELS[category] if category in CATEGORY_LABELS else category.capitalize()] = total_value

    total = round(sum(values.values()), 2)
    score = generate_carbon_score(total)
    top_category = max(values, key=values.get) if values else None

    return {
        "transport": values["transport"],
        "food": values["food"],
        "electricity": values["electricity"],
        "shopping": values["shopping"],
        "flight": values["flight"],
        "total": total,
        "annual_total": round(total * 12, 2),
        "score": score,
        "breakdown": breakdown,
        "top_category": CATEGORY_LABELS.get(top_category, top_category),
        "model_inputs": {
            category: form_data.get(category) for category in EMISSION_MAP
        },
    }


def generate_carbon_score(total):
    return max(0, min(100, int(100 - total * 7)))


def validate_calculator_input(form_data):
    errors = []
    for field, allowed in CATEGORY_OPTIONS.items():
        value = form_data.get(field)
        if not value:
            errors.append(f"{CATEGORY_LABELS[field]} selection is required.")
            continue
        if not validate_category_value(value, allowed):
            errors.append(f"Invalid value for {CATEGORY_LABELS[field]}.")
    return errors
