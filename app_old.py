import os
import sqlite3
from datetime import datetime

from flask import Flask, g, render_template, request, redirect, url_for, flash

import config
from modules.action_tracker import normalize_action_data
from modules.ai_coach import build_ai_response
from modules.carbon_calculator import calculate_emissions, validate_calculator_input
from modules.dashboard_engine import build_dashboard_payload
from modules.recommendation_engine import build_recommendations
from modules.simulator import run_simulation

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['DATABASE'] = os.path.join(app.root_path, config.DATABASE_FILENAME)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_db(exception=None):
    db = getattr(g, 'db', None)
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


def serialize_row(row):
    return dict(row) if row else None


def ensure_default_user(db):
    user = db.execute('SELECT id FROM users ORDER BY id LIMIT 1').fetchone()
    if user:
        return user['id']
    db.execute(
        'INSERT INTO users (name, email, created_at) VALUES (?, ?, ?)',
        ('Guest User', 'guest@example.com', datetime.utcnow().isoformat()),
    )
    db.commit()
    user = db.execute('SELECT id FROM users ORDER BY id LIMIT 1').fetchone()
    return user['id']


@app.route('/')
def home():
    init_db()
    return render_template('home.html')


@app.route('/about')
def about():
    init_db()
    return render_template('about.html')


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    init_db()
    errors = []
    if request.method == 'POST':
        form_data = request.form.to_dict()
        errors = validate_calculator_input(form_data)
        if errors:
            for error in errors:
                flash(error, 'danger')
        else:
            record = calculate_emissions(form_data)
            db = get_db()
            user_id = ensure_default_user(db)
            now = datetime.utcnow().isoformat()
            db.execute(
                'INSERT INTO carbon_records (user_id, transport_emission, food_emission, electricity_emission, shopping_emission, flight_emission, total_emission, carbon_score, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    user_id,
                    record['transport'],
                    record['food'],
                    record['electricity'],
                    record['shopping'],
                    record['flight'],
                    record['total'],
                    record['score'],
                    now,
                ),
            )
            db.commit()
            flash('Carbon footprint estimated successfully.', 'success')
            return redirect(url_for('dashboard'))
    return render_template('calculator.html')


@app.route('/dashboard')
def dashboard():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    record = serialize_row(
        db.execute(
            'SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
            (user_id,),
        ).fetchone()
    )
    records = db.execute(
        'SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 12',
        (user_id,),
    ).fetchall()
    actions = db.execute(
        'SELECT * FROM actions WHERE user_id = ? ORDER BY completed_date DESC LIMIT 6',
        (user_id,),
    ).fetchall()
    total_saved = db.execute(
        'SELECT COALESCE(SUM(carbon_saved), 0) AS total_saved FROM actions WHERE user_id = ?',
        (user_id,),
    ).fetchone()['total_saved']
    payload = build_dashboard_payload(record, actions, total_saved, records)
    return render_template('dashboard.html', record=record, **payload)


@app.route('/simulator', methods=['GET', 'POST'])
def simulator():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    simulation = None
    if request.method == 'POST':
        form_data = request.form.to_dict()
        scenario = request.form.get('scenario', 'transport')
        simulation = run_simulation(form_data, scenario)
        now = datetime.utcnow().isoformat()
        db.execute(
            'INSERT INTO simulations (user_id, scenario, current_total, projected_total, savings, reduction, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (
                user_id,
                scenario,
                simulation['current_total'],
                simulation['projected_total'],
                simulation['savings'],
                simulation['reduction'],
                now,
            ),
        )
        db.commit()
    saved_simulations = db.execute(
        'SELECT * FROM simulations WHERE user_id = ? ORDER BY created_at DESC LIMIT 5',
        (user_id,),
    ).fetchall()
    return render_template('simulator.html', simulation=simulation, saved_simulations=saved_simulations)


@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    if request.method == 'POST':
        action_data = normalize_action_data(request.form.to_dict())
        db.execute(
            'INSERT INTO actions (user_id, action_name, carbon_saved, completed_date) VALUES (?, ?, ?, ?)',
            (
                user_id,
                action_data['action_name'],
                action_data['carbon_saved'],
                action_data['completed_date'],
            ),
        )
        db.commit()
        flash('Action tracked successfully.', 'success')
        return redirect(url_for('tracker'))
    record = serialize_row(
        db.execute(
            'SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
            (user_id,),
        ).fetchone()
    )
    actions = db.execute(
        'SELECT * FROM actions WHERE user_id = ? ORDER BY completed_date DESC',
        (user_id,),
    ).fetchall()
    totals = db.execute(
        'SELECT COUNT(*) AS total_actions, COALESCE(SUM(carbon_saved), 0) AS total_saved FROM actions WHERE user_id = ?',
        (user_id,),
    ).fetchone()
    streak = min(7, totals['total_actions'])
    ai_summary = None
    ai_recommendations = None
    if record:
        ai_summary = build_ai_response(record, 'What can I improve?')
        ai_recommendations = build_recommendations(record)
    return render_template(
        'tracker.html',
        actions=actions,
        total_actions=totals['total_actions'],
        total_saved=totals['total_saved'],
        streak=streak,
        ai_summary=ai_summary,
        ai_recommendations=ai_recommendations,
    )


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    init_db()
    db = get_db()
    user_id = ensure_default_user(db)
    record = serialize_row(
        db.execute(
            'SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC LIMIT 1',
            (user_id,),
        ).fetchone()
    )
    response = None
    if request.method == 'POST':
        question = request.form.get('question', '')
        response = build_ai_response(record, question)
    return render_template('chat.html', record=record, response=response)


if __name__ == '__main__':
    app.run(debug=True)
