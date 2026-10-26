from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3
import os
import io
import csv
import json
from datetime import datetime, timedelta
from collections import Counter
from werkzeug.security import generate_password_hash, check_password_hash
from ml_model import predict_cognitive_state, predict_state, RECOMMENDATIONS, COGNITIVE_LOAD_MAP
from adaptive_engine import (
    TOPICS, QUESTION_BANK, select_adaptive_question,
    get_adaptive_intervention, get_adaptive_lesson, get_questions_for_topic
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "emotion-aware-adaptive-secret-key-2026")
DB_PATH = "project.db"

ALL_STATES = ["Focused", "Motivated", "Confused", "Stressed", "Fatigued", "Neutral"]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'learner',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        state TEXT NOT NULL,
        confidence REAL DEFAULT 85.0,
        recommendation TEXT NOT NULL,
        modality TEXT NOT NULL DEFAULT 'text',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS study_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT NOT NULL,
        duration_seconds INTEGER DEFAULT 0,
        total_questions INTEGER DEFAULT 0,
        score INTEGER DEFAULT 0,
        dominant_state TEXT DEFAULT 'Focused',
        status TEXT DEFAULT 'completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS quiz_attempts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        session_id INTEGER,
        question_id TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        state_at_attempt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS seen_questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        question_id TEXT NOT NULL,
        topic TEXT NOT NULL DEFAULT 'python',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, question_id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # Safe migration: ensure status column exists in existing study_sessions table
    try:
        conn.execute("ALTER TABLE study_sessions ADD COLUMN status TEXT DEFAULT 'completed'")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Seed Default Accounts
    seed_users = [
        ("Demo Learner", "learner@gmail.com", "1234", "learner"),
        ("Demo Admin", "admin@gmail.com", "1234", "admin"),
        ("Alex Chen", "alex@learner.edu", "1234", "learner"),
        ("Sarah Jenkins", "sarah@learner.edu", "1234", "learner")
    ]

    for name, email, pwd, role in seed_users:
        try:
            conn.execute(
                "INSERT INTO users(name, email, password, role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(pwd), role)
            )
        except sqlite3.IntegrityError:
            pass

    conn.commit()

    # Seed sample historical activities if table is empty
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM activities")
    if cursor.fetchone()[0] == 0:
        sample_activities = [
            (1, "I understand the lesson on loops and I am ready to continue", "Focused", 91.2, "Maintain momentum and attempt a slightly harder problem.", "text", -4),
            (1, "I am excited to conquer this machine learning exercise today", "Motivated", 88.5, "Capitalize on high motivation by setting ambitious milestones.", "text", -3),
            (1, "I do not understand how recursion unwinds and feel stuck", "Confused", 85.0, "Review simpler base cases and use scaffolded hints.", "text", -2),
            (1, "Webcam telemetry: high stress indicators detected during timed quiz", "Stressed", 89.4, "Take a 3-minute calming breathing reset.", "webcam", -1),
            (1, "My eyes are heavy, I am exhausted and yawning", "Fatigued", 82.0, "Take a 5-minute restorative stretch break and do a bite-sized review.", "text", -1),
            (1, "Just doing standard study routine at a steady normal pace", "Neutral", 86.0, "Proceed with core curriculum modules.", "text", 0),
            (3, "Too many project deliverables due tomorrow, feeling overwhelmed", "Stressed", 92.0, "Break assignment into micro-tasks and take a short pause.", "text", -1),
            (3, "Panicking about the upcoming midterm exam", "Stressed", 87.5, "Engage in guided breathing and review core formulas.", "text", 0),
            (4, "I feel drained and sleepy after five hours of study", "Fatigued", 84.0, "Take a restful nap and drink water.", "text", -1),
            (4, "Finished the reading and feeling enthusiastic to build a project", "Motivated", 90.0, "Channel motivation into building a hands-on app.", "text", 0)
        ]
        for uid, desc, state, conf, rec, mod, days_ago in sample_activities:
            date_str = (datetime.now() + timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO activities(user_id, description, state, confidence, recommendation, modality, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """, (uid, desc, state, conf, rec, mod, date_str))

        # Seed sample completed study sessions
        sample_sessions = [
            (1, "Python & Algorithmic Problem Solving", 1240, 5, 400, "Focused", -3),
            (1, "AI & Machine Learning Foundations", 960, 4, 300, "Motivated", -2),
            (1, "Data Structures & Algorithms", 840, 3, 200, "Neutral", -1),
            (3, "Python & Algorithmic Problem Solving", 720, 3, 100, "Confused", -1)
        ]
        for uid, top, dur, tq, sc, dom, d_ago in sample_sessions:
            c_str = (datetime.now() + timedelta(days=d_ago)).strftime("%Y-%m-%d %H:%M:%S")
            conn.execute("""
                INSERT INTO study_sessions(user_id, topic, duration_seconds, total_questions, score, dominant_state, status, created_at)
                VALUES(?, ?, ?, ?, ?, ?, 'completed', ?)
            """, (uid, top, dur, tq, sc, dom, c_str))

        conn.commit()

    conn.close()

def format_duration(seconds):
    if not seconds:
        return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

app.jinja_env.filters["format_duration"] = format_duration

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("admin") if session.get("role") == "admin" else url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!")
            return redirect(url_for("admin") if user["role"] == "admin" else url_for("dashboard"))
        
        flash("Invalid email or password. Please try again.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.")
            return render_template("register.html")

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users(name, email, password, role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), "learner")
            )
            conn.commit()
            flash("Account registered successfully! Please log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered. Please log in.")
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") == "admin":
        return redirect(url_for("admin"))

    user_id = session["user_id"]
    conn = get_db()

    # User's recent activities
    activities = conn.execute("""
        SELECT * FROM activities WHERE user_id=? ORDER BY id DESC LIMIT 15
    """, (user_id,)).fetchall()

    # Aggregates for Chart.js across all 6 states
    state_counts_rows = conn.execute("""
        SELECT state, COUNT(*) as count FROM activities WHERE user_id=? GROUP BY state
    """, (user_id,)).fetchall()

    state_counts = {s: 0 for s in ALL_STATES}
    for row in state_counts_rows:
        if row["state"] in state_counts:
            state_counts[row["state"]] = row["count"]
        elif row["state"] == "Bored":
            state_counts["Fatigued"] += row["count"]

    total_activities = sum(state_counts.values())
    dominant_state = max(state_counts, key=state_counts.get) if total_activities > 0 else "Neutral"

    # Productivity Score Calculation:
    # (Focused + Motivated + Neutral) are positive/productive states
    positive_count = state_counts.get("Focused", 0) + state_counts.get("Motivated", 0) + (state_counts.get("Neutral", 0) * 0.75)
    productivity_score = round((positive_count / total_activities) * 100) if total_activities > 0 else 75

    # Study sessions history
    sessions = conn.execute("""
        SELECT * FROM study_sessions WHERE user_id=? ORDER BY id DESC LIMIT 10
    """, (user_id,)).fetchall()

    total_study_seconds = conn.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0) FROM study_sessions WHERE user_id=?
    """, (user_id,)).fetchone()[0]

    total_sessions_completed = conn.execute("""
        SELECT COUNT(*) FROM study_sessions WHERE user_id=?
    """, (user_id,)).fetchone()[0]

    total_quiz_correct = conn.execute("""
        SELECT COUNT(*) FROM quiz_attempts WHERE user_id=? AND is_correct=1
    """, (user_id,)).fetchone()[0]

    total_quiz_attempts = conn.execute("""
        SELECT COUNT(*) FROM quiz_attempts WHERE user_id=?
    """, (user_id,)).fetchone()[0]

    quiz_accuracy = round((total_quiz_correct / total_quiz_attempts) * 100) if total_quiz_attempts > 0 else 0

    conn.close()

    return render_template(
        "dashboard.html",
        activities=activities,
        state_counts=state_counts,
        total_activities=total_activities,
        dominant_state=dominant_state,
        productivity_score=productivity_score,
        study_sessions=sessions,
        total_study_seconds=total_study_seconds,
        total_sessions_completed=total_sessions_completed,
        total_quiz_attempts=total_quiz_attempts,
        quiz_accuracy=quiz_accuracy
    )

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if session.get("role") != "admin":
        flash("Admin privilege required.")
        return redirect(url_for("dashboard"))

    conn = get_db()

    # KPI Metrics
    total_learners = conn.execute("SELECT COUNT(*) FROM users WHERE role='learner'").fetchone()[0]
    total_activities = conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0]
    total_sessions = conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]

    # Overall State Distribution
    state_counts_rows = conn.execute("""
        SELECT state, COUNT(*) as count FROM activities GROUP BY state
    """).fetchall()

    state_counts = {s: 0 for s in ALL_STATES}
    for row in state_counts_rows:
        if row["state"] in state_counts:
            state_counts[row["state"]] = row["count"]
        elif row["state"] == "Bored":
            state_counts["Fatigued"] += row["count"]

    # At-risk learners alert (learners with high stress or confusion flags)
    at_risk_learners = conn.execute("""
        SELECT u.id, u.name, u.email, COUNT(a.id) as stress_count
        FROM users u
        JOIN activities a ON u.id = a.user_id
        WHERE a.state IN ('Stressed', 'Confused', 'Fatigued')
        GROUP BY u.id
        ORDER BY stress_count DESC LIMIT 5
    """).fetchall()

    # All Recent Activities with User Info
    all_activities = conn.execute("""
        SELECT a.*, u.name as user_name, u.email as user_email
        FROM activities a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.id DESC LIMIT 50
    """).fetchall()

    conn.close()

    # Load ML Benchmark Report
    report_path = os.path.join("models", "evaluation_report.json")
    ml_report = None
    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                ml_report = json.load(f)
        except Exception as e:
            print("Failed loading evaluation report:", e)

    return render_template(
        "admin.html",
        total_learners=total_learners,
        total_activities=total_activities,
        total_sessions=total_sessions,
        state_counts=state_counts,
        at_risk_learners=at_risk_learners,
        all_activities=all_activities,
        ml_report=ml_report
    )

@app.route("/admin/export_csv")
def export_csv():
    if session.get("role") != "admin":
        return redirect(url_for("dashboard"))

    conn = get_db()
    activities = conn.execute("""
        SELECT a.id, u.name, u.email, a.modality, a.state, a.confidence, a.description, a.recommendation, a.created_at
        FROM activities a
        JOIN users u ON a.user_id = u.id
        ORDER BY a.id DESC
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Activity ID", "Learner Name", "Learner Email", "Modality", "Cognitive State", "Confidence (%)", "Reflection / Telemetry", "Recommendation", "Timestamp"])

    for r in activities:
        writer.writerow([r["id"], r["name"], r["email"], r["modality"], r["state"], r["confidence"], r["description"], r["recommendation"], r["created_at"]])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cognitive_learning_activities.csv"}
    )

@app.route("/activity", methods=["GET", "POST"])
def activity():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        modality = request.form.get("modality", "text")
        manual_state = request.form.get("manual_state", "")

        # If manual state was explicitly picked from fallback buttons
        if manual_state and manual_state in ALL_STATES:
            state = manual_state
            confidence = 90.0
            recommendation = RECOMMENDATIONS.get(state, RECOMMENDATIONS["Neutral"])
            probabilities = {s: (90.0 if s == state else round(10.0 / (len(ALL_STATES) - 1), 1)) for s in ALL_STATES}
            intervention = get_adaptive_intervention(state, confidence)
            if not description:
                description = f"Manual state override: Selected {state} state."
        else:
            if len(description) < 3:
                flash("Please enter a slightly more descriptive reflection or select a state.")
                return render_template("activity.html")

            # Run cognitive state inference
            pred = predict_cognitive_state(description)
            state = pred["state"]
            confidence = pred["confidence"]
            recommendation = pred["recommendation"]
            probabilities = pred["probabilities"]
            intervention = pred["intervention"]

        # Record into database
        conn = get_db()
        conn.execute("""
            INSERT INTO activities(user_id, description, state, confidence, recommendation, modality)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (session["user_id"], description, state, confidence, recommendation, modality))
        conn.commit()
        conn.close()

        # Update current session state if in an active study session
        session["current_cognitive_state"] = state

        return render_template(
            "result.html",
            description=description,
            state=state,
            confidence=confidence,
            probabilities=probabilities,
            recommendation=recommendation,
            intervention=intervention,
            modality=modality
        )

    return render_template("activity.html")

@app.route("/study", methods=["GET", "POST"])
def study():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    topic_id = request.args.get("topic", "python")

    # Match topic
    topic_obj = next((t for t in TOPICS if t["id"] == topic_id), TOPICS[0])

    # Manage study session lifecycle in Flask session
    if "study_session_start" not in session or request.args.get("restart") == "1":
        session["study_session_start"] = datetime.now().isoformat()
        session["study_session_topic"] = topic_id
        session["study_questions_answered"] = 0
        session["study_score"] = 0
        session["study_states_seen"] = []

    # Check cognitive state
    # 1. First priority: state passed as query param (e.g. ?state=Confused)
    param_state = request.args.get("state")
    if param_state and param_state in ALL_STATES:
        current_state = param_state
        session["current_cognitive_state"] = current_state
        # Also record this interaction so it reflects on dashboard and charts
        conn = get_db()
        conn.execute("""
            INSERT INTO activities(user_id, description, state, confidence, recommendation, modality)
            VALUES(?, ?, ?, ?, ?, 'manual_override')
        """, (
            user_id,
            f"State adapted to {current_state} during {topic_obj['name']} session.",
            current_state,
            92.0,
            RECOMMENDATIONS.get(current_state, "")
        ))
        conn.commit()
        conn.close()
    elif "current_cognitive_state" in session:
        current_state = session["current_cognitive_state"]
    else:
        conn = get_db()
        last_act = conn.execute("""
            SELECT state FROM activities WHERE user_id=? ORDER BY id DESC LIMIT 1
        """, (user_id,)).fetchone()
        conn.close()
        current_state = last_act["state"] if last_act else "Focused"
        session["current_cognitive_state"] = current_state

    # Track states seen in this study session
    states_seen = session.get("study_states_seen", [])
    states_seen.append(current_state)
    session["study_states_seen"] = states_seen

    # Connect to SQLite for session and history tracking
    conn = get_db()

    # Optional user action: Reset seen question history for this topic to practice fresh
    if request.args.get("reset_history") == "1":
        conn.execute("DELETE FROM seen_questions WHERE user_id=? AND topic=?", (user_id, topic_id))
        conn.commit()

    # Retrieve comprehensive history of answered AND seen questions across all sessions
    history_rows = conn.execute("""
        SELECT question_id FROM quiz_attempts WHERE user_id=?
        UNION
        SELECT question_id FROM seen_questions WHERE user_id=?
    """, (user_id, user_id)).fetchall()
    history_ids = [r["question_id"] for r in history_rows]

    # Handle Answer Submission
    if request.method == "POST":
        action = request.form.get("action", "submit_answer")

        # Check if user clicked "End Study Session"
        if action == "end_session":
            conn.close()
            return redirect(url_for("end_study_session"))

        question_id = request.form.get("question_id")
        selected_index = int(request.form.get("selected_option", -1))
        current_state_input = request.form.get("current_state", current_state)

        matched_q = next((q for q in QUESTION_BANK if q["id"] == question_id), None)
        if matched_q:
            is_correct = 1 if selected_index == matched_q["correct_index"] else 0
            conn.execute("""
                INSERT INTO quiz_attempts(user_id, question_id, is_correct, state_at_attempt)
                VALUES(?, ?, ?, ?)
            """, (user_id, question_id, is_correct, current_state_input))

            # Ensure attempted question is permanently logged in seen_questions
            conn.execute("""
                INSERT OR IGNORE INTO seen_questions(user_id, question_id, topic)
                VALUES(?, ?, ?)
            """, (user_id, question_id, topic_id))
            conn.commit()

            # Update session stats
            answered = session.get("study_questions_answered", 0) + 1
            session["study_questions_answered"] = answered
            pts = 100 if matched_q["difficulty"] == "easy" else (200 if matched_q["difficulty"] == "medium" else 300)
            if is_correct:
                session["study_score"] = session.get("study_score", 0) + pts

            # Calculate session elapsed time
            start_dt = datetime.fromisoformat(session.get("study_session_start", datetime.now().isoformat()))
            elapsed_sec = int((datetime.now() - start_dt).total_seconds())

            # Pedagogical Intervention & Lesson
            intervention = get_adaptive_intervention(current_state_input, 88.0)
            lesson = get_adaptive_lesson(topic_id, current_state_input)

            conn.close()

            return render_template(
                "study.html",
                topics=TOPICS,
                selected_topic=topic_id,
                current_state=current_state_input,
                all_states=ALL_STATES,
                question=matched_q,
                submitted=True,
                is_correct=is_correct,
                selected_index=selected_index,
                intervention=intervention,
                lesson=lesson,
                elapsed_sec=elapsed_sec,
                session_score=session.get("study_score", 0),
                questions_answered=session.get("study_questions_answered", 1)
            )

    # Select adaptive question from unseen bank and adapted learning material
    next_question, difficulty = select_adaptive_question(topic_id, current_state, history_ids)

    # Record the presented question as seen in SQLite across sessions
    conn.execute("""
        INSERT OR IGNORE INTO seen_questions(user_id, question_id, topic)
        VALUES(?, ?, ?)
    """, (user_id, next_question["id"], topic_id))
    conn.commit()
    conn.close()

    intervention = get_adaptive_intervention(current_state, 88.0)
    lesson = get_adaptive_lesson(topic_id, current_state)

    start_dt = datetime.fromisoformat(session.get("study_session_start", datetime.now().isoformat()))
    elapsed_sec = int((datetime.now() - start_dt).total_seconds())

    return render_template(
        "study.html",
        topics=TOPICS,
        selected_topic=topic_id,
        current_state=current_state,
        all_states=ALL_STATES,
        question=next_question,
        difficulty=difficulty,
        submitted=False,
        intervention=intervention,
        lesson=lesson,
        elapsed_sec=elapsed_sec,
        session_score=session.get("study_score", 0),
        questions_answered=session.get("study_questions_answered", 0)
    )

@app.route("/study/end", methods=["GET", "POST"])
def end_study_session():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    topic_id = session.get("study_session_topic", "python")
    topic_obj = next((t for t in TOPICS if t["id"] == topic_id), TOPICS[0])
    topic_name = topic_obj["name"]

    start_str = session.get("study_session_start")
    if start_str:
        start_dt = datetime.fromisoformat(start_str)
        duration_seconds = max(10, int((datetime.now() - start_dt).total_seconds()))
    else:
        duration_seconds = 180

    total_questions = session.get("study_questions_answered", 0)
    score = session.get("study_score", 0)
    states_seen = session.get("study_states_seen", [])
    dominant_state = Counter(states_seen).most_common(1)[0][0] if states_seen else session.get("current_cognitive_state", "Focused")

    # Persist into study_sessions table
    conn = get_db()
    conn.execute("""
        INSERT INTO study_sessions(user_id, topic, duration_seconds, total_questions, score, dominant_state, status)
        VALUES(?, ?, ?, ?, ?, ?, 'completed')
    """, (user_id, topic_name, duration_seconds, total_questions, score, dominant_state))
    conn.commit()
    conn.close()

    # Clean session tracking keys
    session.pop("study_session_start", None)
    session.pop("study_session_topic", None)
    session.pop("study_questions_answered", None)
    session.pop("study_score", None)
    session.pop("study_states_seen", None)

    flash(f"🎉 Study session ended successfully! Duration: {format_duration(duration_seconds)} | Questions: {total_questions} | Score: {score} XP | Dominant State: {dominant_state}")
    return redirect(url_for("dashboard"))

@app.route("/api/predict_state", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    res = predict_cognitive_state(text)
    return jsonify(res)

@app.route("/api/record_webcam_state", methods=["POST"])
def api_record_webcam():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    state = data.get("state", "Focused")
    conf = float(data.get("confidence", 85.0))
    desc = data.get("description", "Facial expression and attentiveness tracking telemetry.")
    intervention = get_adaptive_intervention(state, conf)

    conn = get_db()
    conn.execute("""
        INSERT INTO activities(user_id, description, state, confidence, recommendation, modality)
        VALUES(?, ?, ?, ?, ?, 'webcam')
    """, (session["user_id"], desc, state, conf, intervention["message"]))
    conn.commit()
    conn.close()

    session["current_cognitive_state"] = state
    return jsonify({"success": True, "state": state, "intervention": intervention})

if __name__ == "__main__":
    init_db()
    print("Starting Emotion-Aware Adaptive Learning & Productivity System on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
