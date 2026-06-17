def build_recommendations(record):
    recommendations = {
        "easy": [],
        "medium": [],
        "advanced": [],
    }

    if record["transport_emission"] > 2.0:
        recommendations["easy"].append("Try one car-free day per week.")
        recommendations["medium"].append("Use public transit for short commutes.")
        recommendations["advanced"].append("Consider switching to an electric vehicle or carpooling.")
    else:
        recommendations["easy"].append("Walk or cycle for short trips.")
        recommendations["medium"].append("Plan errands together to cut extra travel.")
        recommendations["advanced"].append("Maintain efficient route planning and active transport habits.")

    if record["food_emission"] > 3.5:
        recommendations["easy"].append("Add one plant-based meal each day.")
        recommendations["medium"].append("Reduce red meat to twice weekly.")
        recommendations["advanced"].append("Explore a weekly vegetarian meal plan.")
    else:
        recommendations["easy"].append("Choose seasonal vegetables and whole foods.")
        recommendations["medium"].append("Cook more meals at home to avoid processed foods.")
        recommendations["advanced"].append("Support local sustainable producers.")

    if record["electricity_emission"] > 3.0:
        recommendations["easy"].append("Switch off lights when not in use.")
        recommendations["medium"].append("Use energy-efficient appliances and LEDs.")
        recommendations["advanced"].append("Inspect your home for insulation and smart energy controls.")
    else:
        recommendations["easy"].append("Unplug chargers when not in use.")
        recommendations["medium"].append("Choose appliances with better energy ratings.")
        recommendations["advanced"].append("Consider renewable energy or green tariffs.")

    if record["shopping_emission"] > 2.5:
        recommendations["easy"].append("Buy only what you need and avoid impulse purchases.")
        recommendations["medium"].append("Choose durable, reusable products.")
        recommendations["advanced"].append("Repair items instead of replacing them.")
    else:
        recommendations["easy"].append("Keep using mindful shopping habits.")
        recommendations["medium"].append("Reuse and repurpose items you already own.")
        recommendations["advanced"].append("Support brands with strong sustainability practices.")

    if record["flight_emission"] > 3.0:
        recommendations["easy"].append("Reduce short flights and take trains when possible.")
        recommendations["medium"].append("Choose nonstop flights and offset your carbon.")
        recommendations["advanced"].append("Plan travel less frequently and combine trips.")
    else:
        recommendations["easy"].append("Book fewer flights and stay local more often.")
        recommendations["medium"].append("Choose lower-impact travel options.")
        recommendations["advanced"].append("Use digital alternatives for business and leisure travel.")

    return recommendations
