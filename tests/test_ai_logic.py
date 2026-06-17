from modules.ai_coach import build_ai_response


def test_ai_response_without_record():
    response = build_ai_response(None, "How can I reduce my footprint?")
    assert "Please submit your lifestyle profile first" in response


def test_ai_response_reduce_question():
    record = {
        "transport_emission": 10.0,
        "food_emission": 1.0,
        "electricity_emission": 1.0,
        "shopping_emission": 1.0,
        "flight_emission": 0.0,
        "total_emission": 13.0,
        "carbon_score": 10,
    }
    response = build_ai_response(record, "How do I reduce emissions?")
    assert "transportation" in response.lower() or "transport" in response.lower()


def test_ai_response_score_question():
    record = {
        "transport_emission": 1.0,
        "food_emission": 1.0,
        "electricity_emission": 1.0,
        "shopping_emission": 1.0,
        "flight_emission": 0.0,
        "total_emission": 4.0,
        "carbon_score": 72,
    }
    response = build_ai_response(record, "What is my score?")
    assert "72" in response
