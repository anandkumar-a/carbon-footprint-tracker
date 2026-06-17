from modules.simulator import run_simulation


def test_run_simulation_reduces_emissions():
    form_data = {
        "transport": "car",
        "food": "mixed",
        "electricity": "medium",
        "shopping": "medium",
        "flight": "occasionally",
    }
    result = run_simulation(form_data, "transport")
    assert result["current_total"] > result["projected_total"] or result["savings"] == 0
    assert result["reduction"] >= 0


def test_run_simulation_same_if_no_change():
    form_data = {
        "transport": "bus",
        "food": "vegetarian",
        "electricity": "low",
        "shopping": "low",
        "flight": "never",
    }
    result = run_simulation(form_data, "transport")
    assert result["savings"] == 0
    assert result["projected_total"] == result["current_total"]
