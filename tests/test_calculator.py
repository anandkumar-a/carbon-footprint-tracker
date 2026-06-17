import pytest
from modules.carbon_calculator import calculate_emissions, validate_calculator_input


def test_calculate_emissions_baseline():
    form_data = {
        "transport": "car",
        "food": "mixed",
        "electricity": "medium",
        "shopping": "medium",
        "flight": "occasionally",
    }
    result = calculate_emissions(form_data)
    assert result["total"] == 2.5 * 4 + 3.6 + 2.8 + 2.2 + 3.0
    assert result["score"] == 100 - int(result["total"] * 7)
    assert result["top_category"] == "Transportation"


def test_calculate_emissions_high_meat():
    form_data = {
        "transport": "electric_vehicle",
        "food": "heavy_meat",
        "electricity": "high",
        "shopping": "high",
        "flight": "frequently",
    }
    result = calculate_emissions(form_data)
    assert result["breakdown"]["Food"] == 5.2
    assert result["breakdown"]["Air Travel"] == 6.8
    assert result["annual_total"] == round(result["total"] * 12, 2)


def test_validate_calculator_input_valid():
    form_data = {
        "transport": "bus",
        "food": "vegetarian",
        "electricity": "low",
        "shopping": "low",
        "flight": "never",
    }
    errors = validate_calculator_input(form_data)
    assert errors == []


def test_validate_calculator_input_invalid():
    form_data = {
        "transport": "rocket",
        "food": "vegetarian",
        "electricity": "low",
        "shopping": "low",
        "flight": "never",
    }
    errors = validate_calculator_input(form_data)
    assert len(errors) == 1
    assert "Invalid value for Transportation" in errors[0]
