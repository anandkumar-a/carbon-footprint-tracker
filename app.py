import os
import sqlite3
from datetime import datetime
from flask import Flask, g, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.config["DATABASE"] = os.path.join(app.root_path, "carbon.db")
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

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


def get_db():
    db = getattr(g, "db", None)
    if db is None:
        db = g.db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, "db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS carbon_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            transport_emission REAL,
            food_emission REAL,
            electricity_emission REAL,
            shopping_emission REAL,
            flight_emission REAL,
            total_emission REAL,
            carbon_score INTEGER,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action_name TEXT,
            carbon_saved REAL,
            completed_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS simulations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            scenario TEXT,
            current_total REAL,
            projected_total REAL,
            savings REAL,
            reduction REAL,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


def calculate_emissions(form_data):
    transport = TRANSPORT_EMISSIONS.get(form_data.get("transport"), 0) * 4.0
    food = FOOD_EMISSIONS.get(form_data.get("food"), 0) * 1.0
    electricity = ELECTRICITY_EMISSIONS.get(form_data.get("electricity"), 0) * 1.0
    shopping = SHOPPING_EMISSIONS.get(form_data.get("shopping"), 0) * 1.0
    flight = FLIGHT_EMISSIONS.get(form_data.get("flight"), 0) * 1.0
    total = round(transport + food + electricity + shopping + flight, 2)
    score = generate_carbon_score(total)
    breakdown = {
        "Transportation": round(transport, 2),
        "Food": round(food, 2),
        "Electricity": round(electricity, 2),
        "Shopping": round(shopping, 2),
        "Air Travel": round(flight, 2),
    }
    top_category = max(breakdown, key=breakdown.get)
    return {
        "transport": transport,
        "food": food,
        "electricity": electricity,
        "shopping": shopping,
        "flight": flight,
        "total": total,
        "score": score,
        "breakdown": breakdown,
        "top_category": top_category,
    }


def generate_carbon_score(total):
    score = max(0, min(100, int(100 - total * 7)))
    return score


def build_ai_summary(record):
    insights = [
        f"Your monthly footprint is {record['total_emission']} tons of CO₂.",
        f"Transportation and {record['top_category']} are the biggest contributors.",
        "Small daily changes can add up quickly when tracked consistently.",
    ]
    return " ".join(insights)


def build_recommendations(record):
    recommendations = {
        "easy": [],
        "medium": [],
        "advanced": [],
    }
    if record["transport_emission"] > 5:
        recommendations["easy"].append("Take public transport or bike short trips.")
        recommendations["medium"].append("Plan one car-free day each week.")
        recommendations["advanced"].append("Switch to an electric vehicle or carpool regularly.")
    else:
        recommendations["easy"].append("Walk or bike for errands whenever possible.")
        recommendations["medium"].append("Use public transit for daily commuting.")
        recommendations["advanced"].append("Explore long-term green mobility options.")

    if record["food_emission"] > 3.5:
        recommendations["easy"].append("Add one plant-based meal each day.")
        recommendations["medium"].append("Reduce red meat servings to twice weekly.")
        recommendations["advanced"].append("Commit to a vegetarian meal plan several days per week.")
    else:
        recommendations["easy"].append("Keep choosing lower-emission meal options.")
        recommendations["medium"].append("Swap processed snacks for whole foods.")
        recommendations["advanced"].append("Support local seasonal produce and sustainable food brands.")

    if record["electricity_emission"] > 3:
        recommendations["easy"].append("Turn off unused lights and unplug devices.")
        recommendations["medium"].append("Use energy-efficient appliances and LED bulbs.")
        recommendations["advanced"].append("Inspect your home for insulation and renewable energy options.")
    else:
        recommendations["easy"].append("Keep tracking electricity use each week.")
        recommendations["medium"].append("Replace old bulbs with LEDs and use smart power strips.")
        recommendations["advanced"].append("Explore solar panels or green energy tariffs.")

    if record["shopping_emission"] > 2.5:
        recommendations["easy"].append("Buy only what you need and avoid impulse purchases.")
        recommendations["medium"].append("Choose reusable products over single-use items.")
        recommendations["advanced"].append("Support thrift stores and sustainable brands.")
    else:
        recommendations["easy"].append("Maintain mindful and intentional shopping habits.")
        recommendations["medium"].append("Repair items instead of replacing them.")
        recommendations["advanced"].append("Plan purchases around durability and low emissions.")

    return recommendations


@app.route("/")
def home():
    init_db()
    return render_template("home.html")


@app.route("/calculator", methods=["GET", "POST"])
def calculator():
    init_db()
    if request.method == "POST":
        data = request.form.to_dict()
        record = calculate_emissions(data)
        db = get_db()
        user_id = ensure_default_user(db)
        now = datetime.utcnow().isoformat()
        db.execute(
            "INSERT INTO carbon_records (user_id, transport_emission, food_emission, electricity_emission, shopping_emission, flight_emission, total_emission, carbon_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                record["transport"],
                record["food"],
                record["electricity"],
                record["shopping"],
                record["flight"],
                record["total"],
                record["score"],
                now,
            ),
        )
        db.commit()
        flash("Carbon footprint estimated successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("calculator.html")


def ensure_default_user(db):
    user = db.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
    if user:
        return user["id"]
    db.execute(
        "INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)",
        ("Guest User", "guest@example.com", datetime.utcnow().isoformat()),
    )
    db.commit()
    return db.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()["id"]


@app.route("/dashboard")
def dashboard():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    record = db.execute(
        "SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    records = db.execute(
        "SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 12",
        (user_id,),
    ).fetchall()
    actions = db.execute(
        "SELECT * FROM actions WHERE user_id = ? ORDER BY completed_date DESC LIMIT 6",
        (user_id,),
    ).fetchall()
    total_saved = db.execute(
        "SELECT COALESCE(SUM(carbon_saved), 0) AS total_saved FROM actions WHERE user_id = ?",
        (user_id,),
    ).fetchone()["total_saved"]
    if record:
        record_data = dict(record)
        record_data["top_category"] = max(
            {
                "Transportation": record["transport_emission"],
                "Food": record["food_emission"],
                "Electricity": record["electricity_emission"],
                "Shopping": record["shopping_emission"],
                "Air Travel": record["flight_emission"],
            },
            key=lambda key: {
                "Transportation": record["transport_emission"],
                "Food": record["food_emission"],
                "Electricity": record["electricity_emission"],
                "Shopping": record["shopping_emission"],
                "Air Travel": record["flight_emission"],
            }[key],
        )
        summary = build_ai_summary(record_data)
        recommendations = build_recommendations(record_data)
        trend = [r["total_emission"] for r in reversed(records)]
        labels = [r["created_at"][0:10] for r in reversed(records)]
        breakdown = {
            "Transportation": record["transport_emission"],
            "Food": record["food_emission"],
            "Electricity": record["electricity_emission"],
            "Shopping": record["shopping_emission"],
            "Air Travel": record["flight_emission"],
        }
        return render_template(
            "dashboard.html",
            record=record_data,
            breakdown=breakdown,
            summary=summary,
            recommendations=recommendations,
            trend=trend,
            labels=labels,
            actions=actions,
            total_saved=total_saved,
        )
    return render_template("dashboard.html", record=None, actions=actions, total_saved=total_saved)


@app.route("/simulator", methods=["GET", "POST"])
def simulator():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    simulation = None
    saved_simulations = []
    if request.method == "POST":
        data = request.form.to_dict()
        current = calculate_emissions(data)
        scenario = request.form.get("scenario")
        modified = data.copy()
        if scenario == "transport":
            modified["transport"] = request.form.get("simulate_transport", data.get("transport"))
        elif scenario == "food":
            modified["food"] = request.form.get("simulate_food", data.get("food"))
        elif scenario == "electricity":
            modified["electricity"] = request.form.get("simulate_electricity", data.get("electricity"))
        elif scenario == "shopping":
            modified["shopping"] = request.form.get("simulate_shopping", data.get("shopping"))
        elif scenario == "flight":
            modified["flight"] = request.form.get("simulate_flight", data.get("flight"))
        projected = calculate_emissions(modified)
        savings = round(current["total"] - projected["total"], 2)
        reduction = round((savings / current["total"] * 100) if current["total"] else 0, 1)
        simulation = {
            "scenario": scenario,
            "current_total": current["total"],
            "projected_total": projected["total"],
            "savings": savings,
            "reduction": reduction,
            "current": current,
            "projected": projected,
        }
        now = datetime.utcnow().isoformat()
        db.execute(
            "INSERT INTO simulations (user_id, scenario, current_total, projected_total, savings, reduction, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                user_id,
                scenario,
                current["total"],
                projected["total"],
                savings,
                reduction,
                now,
            ),
        )
        db.commit()

    saved_simulations = db.execute(
        "SELECT * FROM simulations WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    return render_template("simulator.html", simulation=simulation, saved_simulations=saved_simulations)


@app.route("/tracker", methods=["GET", "POST"])
def tracker():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    if request.method == "POST":
        action_name = request.form.get("action_name")
        carbon_saved = float(request.form.get("carbon_saved", 0))
        completed_date = request.form.get("completed_date") or datetime.utcnow().date().isoformat()
        db.execute(
            "INSERT INTO actions (user_id, action_name, carbon_saved, completed_date) VALUES (?, ?, ?, ?)",
            (user_id, action_name, carbon_saved, completed_date),
        )
        db.commit()
        flash("Action tracked successfully.", "success")
        return redirect(url_for("tracker"))

    record = db.execute(
        "SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    actions = db.execute(
        "SELECT * FROM actions WHERE user_id = ? ORDER BY completed_date DESC",
        (user_id,),
    ).fetchall()
    totals = db.execute(
        "SELECT COUNT(*) AS total_actions, COALESCE(SUM(carbon_saved), 0) AS total_saved FROM actions WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    streak = min(7, totals["total_actions"])
    ai_summary = None
    ai_recommendations = None
    if record:
        record_data = dict(record)
        record_data["top_category"] = max(
            {
                "Transportation": record["transport_emission"],
                "Food": record["food_emission"],
                "Electricity": record["electricity_emission"],
                "Shopping": record["shopping_emission"],
                "Air Travel": record["flight_emission"],
            },
            key=lambda key: {
                "Transportation": record["transport_emission"],
                "Food": record["food_emission"],
                "Electricity": record["electricity_emission"],
                "Shopping": record["shopping_emission"],
                "Air Travel": record["flight_emission"],
            }[key],
        )
        ai_summary = build_ai_summary(record_data)
        ai_recommendations = build_recommendations(record_data)
    return render_template(
        "tracker.html",
        actions=actions,
        total_actions=totals["total_actions"],
        total_saved=totals["total_saved"],
        streak=streak,
        ai_summary=ai_summary,
        ai_recommendations=ai_recommendations,
    )


@app.route("/chat", methods=["GET", "POST"])
def chat():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    record = db.execute(
        "SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    response = None
    if request.method == "POST":
        question = request.form.get("question", "")
        response = generate_chat_response(record, question)
    return render_template("chat.html", record=record, response=response)


def generate_chat_response(record, question):
    if not record:
        return "Please submit your lifestyle profile first so the coach can provide personalized guidance."
    question_text = question.strip().lower()

    inappropriate_terms = ["stupid", "shut up", "idiot", "hate", "kill", "fuck", "damn"]
    if any(term in question_text for term in inappropriate_terms):
        return "I am here to help with carbon awareness. That request is inappropriate or unrelated to sustainability."

    def safe_get(key, default=0):
        try:
            return record[key]
        except (KeyError, IndexError, TypeError):
            return default

    top_category = safe_get("top_category", "your profile")
    category_emissions = {
        "transport": safe_get("transport_emission", 0),
        "food": safe_get("food_emission", 0),
        "electricity": safe_get("electricity_emission", 0),
        "shopping": safe_get("shopping_emission", 0),
        "flight": safe_get("flight_emission", 0),
    }
    total_emission = safe_get("total_emission", 0)

    category_names = {
        "transport": "Transportation",
        "food": "Food",
        "electricity": "Electricity",
        "shopping": "Shopping",
        "flight": "Air Travel",
    }
    top_key = None
    if top_category:
        normalized_top = top_category.strip().lower()
        if normalized_top in ["transport", "transportation"]:
            top_key = "transport"
        elif normalized_top in ["air travel", "flight"]:
            top_key = "flight"
        elif normalized_top == "food":
            top_key = "food"
        elif normalized_top == "electricity":
            top_key = "electricity"
        elif normalized_top == "shopping":
            top_key = "shopping"

    top_emission_value = category_emissions.get(top_key, 0)

    category_map = {
        "transport": ["transport", "transportation", "commute", "car", "bus", "train", "bike", "bicycle", "drive", "vehicle"],
        "food": ["food", "meat", "vegetarian", "vegan", "diet", "eat", "meal", "protein"],
        "electricity": ["electric", "power", "energy", "usage", "electricity", "lights", "appliance"],
        "shopping": ["shopping", "buy", "purchase", "consumer", "store", "mall", "clothes"],
        "flight": ["flight", "travel", "plane", "airline", "airport", "fly"],
    }

    intent_map = {
        "reduce": ["reduce", "lower", "improve", "better", "decrease", "cut", "change", "should"],
        "source": ["source", "habit", "highest", "biggest", "main", "cause", "why"],
        "progress": ["goal", "track", "progress", "streak", "save", "continue", "maintain"],
        "score": ["score", "rating", "impact", "response", "status", "number"],
        "education": ["why", "care", "important", "need"],
    }

    def matches(terms):
        return any(term in question_text for term in terms)

    def find_category():
        for key, terms in category_map.items():
            if matches(terms):
                return key
        return None

    category = find_category()
    answer = None

    denial_terms = ["damage the environment", "hurt the environment", "pollute", "destroy the planet", "not real", "hoax", "fake", "don't care"]
    if any(term in question_text for term in denial_terms):
        return "The goal here is to support carbon awareness and sustainability. It is important to reduce emissions because cleaner air, lower energy bills, and healthier communities benefit everyone."

    if matches(intent_map["reduce"]) and category:
        if category == "transport":
            answer = "Transportation is a strong place to start. Replace short car trips with walking, cycling, or public transit and combine errands to reduce emissions quickly."
        elif category == "food":
            answer = "Food choices can make a real difference. Try plant-forward meals, smaller portions of red meat, and more seasonal produce."
        elif category == "electricity":
            answer = "Energy savings are easy wins. Turn off unused lights, unplug idle chargers, and choose energy-efficient appliances when possible."
        elif category == "shopping":
            answer = "Shopping smarter lowers your footprint. Buy less, choose reusable goods, and repair instead of replacing items."
        elif category == "flight":
            answer = "Air travel is one of the highest-impact areas. Reduce flights, choose direct routes, or use virtual meetings when you can."
        else:
            answer = "Start by reducing your largest source of emissions and build from there with one small habit change each week."
    elif matches(intent_map["source"]):
        if category:
            answer = f"Your {category_names.get(category, category)} emissions are {category_emissions[category]} tons. Focus on changing one key behavior in that area to lower your overall footprint."
        elif top_key:
            answer = f"Your top source is {category_names.get(top_key, top_category)} at {top_emission_value} tons. Target that category first for the best results."
        else:
            answer = "Your top emission source appears to be the highest category in your profile. Focus on that area first."
    elif matches(intent_map["progress"]):
        answer = "Track one sustainable action each day and review it weekly. Small wins add up, and consistency is the most important part of improving your carbon score."
    elif matches(intent_map["score"]):
        answer = f"Your score is based on your category emissions. Lowering your top source and maintaining steady improvement in transport, food, and energy use will raise your score over time."
    elif matches(intent_map["education"]):
        answer = "Carbon awareness matters because lower emissions help protect air quality, reduce climate impact, and create healthier communities. Every small change adds up."
    elif category == "transport":
        answer = f"Transportation emits {category_emissions['transport']} tons in your profile. Try public transit, carpooling, or active travel to lower that number."
    elif category == "food":
        answer = f"Food-related emissions are {category_emissions['food']} tons. Eating more plant-based meals and reducing processed foods can help."
    elif category == "electricity":
        answer = f"Electricity currently contributes {category_emissions['electricity']} tons. Simple steps like LED bulbs and unplugging unused devices will help lower that."
    elif category == "shopping":
        answer = f"Shopping habits add {category_emissions['shopping']} tons. Focus on buying durable, reusable items and avoiding impulse purchases."
    elif category == "flight":
        answer = f"Air travel makes up {category_emissions['flight']} tons. Cutting back on flights helps reduce your footprint quickly."
    else:
        answer = "Ask me about your biggest carbon sources, how to reduce transport or food emissions, or how to track progress with sustainable actions."

    return f"Your latest monthly footprint is {total_emission} tons of CO2, with {top_category} as the largest contributor. {answer}"


if __name__ == "__main__":
    app.run(debug=True)
