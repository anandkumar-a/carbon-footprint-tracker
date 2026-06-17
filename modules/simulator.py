from .carbon_calculator import calculate_emissions


def run_simulation(form_data, scenario):
    current = calculate_emissions(form_data)
    modified = form_data.copy()

    if scenario == "transport":
        modified["transport"] = form_data.get("simulate_transport", form_data.get("transport"))
    elif scenario == "food":
        modified["food"] = form_data.get("simulate_food", form_data.get("food"))
    elif scenario == "electricity":
        modified["electricity"] = form_data.get("simulate_electricity", form_data.get("electricity"))
    elif scenario == "shopping":
        modified["shopping"] = form_data.get("simulate_shopping", form_data.get("shopping"))
    elif scenario == "flight":
        modified["flight"] = form_data.get("simulate_flight", form_data.get("flight"))

    projected = calculate_emissions(modified)
    savings = round(current["total"] - projected["total"], 2)
    reduction = round((savings / current["total"] * 100) if current["total"] else 0, 1)
    trees = round(savings * 0.05, 2)

    return {
        "scenario": scenario,
        "current_total": current["total"],
        "projected_total": projected["total"],
        "savings": savings,
        "reduction": reduction,
        "trees": trees,
        "current": current,
        "projected": projected,
    }
