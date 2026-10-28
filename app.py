from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
import sqlite3
import os
import shutil
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
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "emotion-aware-adaptive-secret-key-2026"
)

# --------------------------------------------------
# DATABASE CONFIGURATION
# Local: project.db
# Vercel: writable temporary /tmp/project.db
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DB_PATH = os.path.join(BASE_DIR, "project.db")

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/project.db"

    # Copy the bundled database to writable storage on cold start.
    if not os.path.exists(DB_PATH) and os.path.exists(SOURCE_DB_PATH):
        try:
            shutil.copy2(SOURCE_DB_PATH, DB_PATH)
        except Exception as e:
            print("Database copy warning:", e)
else:
    DB_PATH = SOURCE_DB_PATH

ALL_STATES = [
    "Focused", "Motivated", "Confused",
    "Stressed", "Fatigued", "Neutral"
]


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    try:
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

        # Migrate older databases if the status column is missing.
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(study_sessions)"
            ).fetchall()
        }

        if "status" not in columns:
            conn.execute(
                "ALTER TABLE study_sessions "
                "ADD COLUMN status TEXT DEFAULT 'completed'"
            )

        # Seed default accounts only when they do not already exist.
        seed_users = [
            ("Student Learner", "learner@gmail.com", "1234", "learner"),
            ("System Administrator", "admin@gmail.com", "1234", "admin"),
            ("Alex Chen", "alex@learner.edu", "1234", "learner"),
            ("Sarah Jenkins", "sarah@learner.edu", "1234", "learner")
        ]

        # Sanitize any legacy demo names
        try:
            conn.execute("UPDATE users SET name = 'Student Learner' WHERE name = 'Demo Learner'")
            conn.execute("UPDATE users SET name = 'System Administrator' WHERE name = 'Demo Admin'")
            conn.commit()
        except Exception:
            pass

        for name, email, pwd, role in seed_users:
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?",
                (email,)
            ).fetchone()

            if not existing:
                conn.execute(
                    """
                    INSERT INTO users(name, email, password, role)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        name,
                        email,
                        generate_password_hash(pwd),
                        role
                    )
                )

        conn.commit()

        # Seed sample data if there are no activities.
        activity_count = conn.execute(
            "SELECT COUNT(*) FROM activities"
        ).fetchone()[0]

        if activity_count == 0:
            user_ids = {
                row["email"]: row["id"]
                for row in conn.execute(
                    "SELECT id, email FROM users"
                ).fetchall()
            }

            sample_activities = [
                ("learner@gmail.com",
                 "I understand the lesson on loops and I am ready to continue",
                 "Focused", 91.2,
                 "Maintain momentum and attempt a slightly harder problem.",
                 "text", -4),

                ("learner@gmail.com",
                 "I am excited to conquer this machine learning exercise today",
                 "Motivated", 88.5,
                 "Capitalize on high motivation by setting ambitious milestones.",
                 "text", -3),

                ("learner@gmail.com",
                 "I do not understand how recursion unwinds and feel stuck",
                 "Confused", 85.0,
                 "Review simpler base cases and use scaffolded hints.",
                 "text", -2),

                ("learner@gmail.com",
                 "Webcam telemetry: high stress indicators detected during timed quiz",
                 "Stressed", 89.4,
                 "Take a 3-minute calming breathing reset.",
                 "webcam", -1),

                ("learner@gmail.com",
                 "My eyes are heavy, I am exhausted and yawning",
                 "Fatigued", 82.0,
                 "Take a 5-minute restorative stretch break and do a bite-sized review.",
                 "text", -1),

                ("learner@gmail.com",
                 "Just doing standard study routine at a steady normal pace",
                 "Neutral", 86.0,
                 "Proceed with core curriculum modules.",
                 "text", 0),

                ("alex@learner.edu",
                 "Too many project deliverables due tomorrow, feeling overwhelmed",
                 "Stressed", 92.0,
                 "Break assignment into micro-tasks and take a short pause.",
                 "text", -1),

                ("alex@learner.edu",
                 "Panicking about the upcoming midterm exam",
                 "Stressed", 87.5,
                 "Engage in guided breathing and review core formulas.",
                 "text", 0),

                ("sarah@learner.edu",
                 "I feel drained and sleepy after five hours of study",
                 "Fatigued", 84.0,
                 "Take a restful nap and drink water.",
                 "text", -1),

                ("sarah@learner.edu",
                 "Finished the reading and feeling enthusiastic to build a project",
                 "Motivated", 90.0,
                 "Channel motivation into building a hands-on app.",
                 "text", 0)
            ]

            for email, desc, state, conf, rec, mod, days_ago in sample_activities:
                uid = user_ids.get(email)
                if uid is None:
                    continue

                date_str = (
                    datetime.now() + timedelta(days=days_ago)
                ).strftime("%Y-%m-%d %H:%M:%S")

                conn.execute(
                    """
                    INSERT INTO activities(
                        user_id, description, state, confidence,
                        recommendation, modality, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (uid, desc, state, conf, rec, mod, date_str)
                )

            sample_sessions = [
                ("learner@gmail.com",
                 "Python & Algorithmic Problem Solving",
                 1240, 5, 400, "Focused", -3),

                ("learner@gmail.com",
                 "AI & Machine Learning Foundations",
                 960, 4, 300, "Motivated", -2),

                ("learner@gmail.com",
                 "Data Structures & Algorithms",
                 840, 3, 200, "Neutral", -1),

                ("alex@learner.edu",
                 "Python & Algorithmic Problem Solving",
                 720, 3, 100, "Confused", -1)
            ]

            for email, topic, duration, total_q, score, state, days_ago in sample_sessions:
                uid = user_ids.get(email)
                if uid is None:
                    continue

                created = (
                    datetime.now() + timedelta(days=days_ago)
                ).strftime("%Y-%m-%d %H:%M:%S")

                conn.execute(
                    """
                    INSERT INTO study_sessions(
                        user_id, topic, duration_seconds,
                        total_questions, score, dominant_state,
                        status, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, 'completed', ?)
                    """,
                    (
                        uid, topic, duration, total_q,
                        score, state, created
                    )
                )

            conn.commit()

    finally:
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
        if session.get("role") == "admin":
            return redirect(url_for("admin"))
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
        finally:
            conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!")

            if user["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))

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
                """
                INSERT INTO users(name, email, password, role)
                VALUES (?, ?, ?, ?)
                """,
                (
                    name, email,
                    generate_password_hash(password),
                    "learner"
                )
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

    try:
        activities = conn.execute(
            """
            SELECT * FROM activities
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 15
            """,
            (user_id,)
        ).fetchall()

        state_counts_rows = conn.execute(
            """
            SELECT state, COUNT(*) AS count
            FROM activities
            WHERE user_id = ?
            GROUP BY state
            """,
            (user_id,)
        ).fetchall()

        state_counts = {state: 0 for state in ALL_STATES}

        for row in state_counts_rows:
            if row["state"] in state_counts:
                state_counts[row["state"]] = row["count"]
            elif row["state"] == "Bored":
                state_counts["Fatigued"] += row["count"]

        total_activities = sum(state_counts.values())
        dominant_state = (
            max(state_counts, key=state_counts.get)
            if total_activities > 0 else "Neutral"
        )

        positive_count = (
            state_counts["Focused"]
            + state_counts["Motivated"]
            + state_counts["Neutral"] * 0.75
        )

        productivity_score = (
            round((positive_count / total_activities) * 100)
            if total_activities > 0 else 75
        )

        study_sessions = conn.execute(
            """
            SELECT * FROM study_sessions
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 10
            """,
            (user_id,)
        ).fetchall()

        total_study_seconds = conn.execute(
            """
            SELECT COALESCE(SUM(duration_seconds), 0)
            FROM study_sessions WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]

        total_sessions_completed = conn.execute(
            "SELECT COUNT(*) FROM study_sessions WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

        total_quiz_correct = conn.execute(
            """
            SELECT COUNT(*) FROM quiz_attempts
            WHERE user_id = ? AND is_correct = 1
            """,
            (user_id,)
        ).fetchone()[0]

        total_quiz_attempts = conn.execute(
            "SELECT COUNT(*) FROM quiz_attempts WHERE user_id = ?",
            (user_id,)
        ).fetchone()[0]

    finally:
        conn.close()

    quiz_accuracy = (
        round((total_quiz_correct / total_quiz_attempts) * 100)
        if total_quiz_attempts > 0 else 0
    )

    # Prepare timeline session trend data for the modern analytics visualization
    session_trend = []
    for s in reversed(study_sessions[:8]):
        session_trend.append({
            "topic": s["topic"].split("&")[0].strip(),
            "score": s["score"],
            "state": s["dominant_state"],
            "questions": s["total_questions"],
            "duration": s["duration_seconds"],
            "date": s["created_at"].split()[0] if s["created_at"] else ""
        })

    return render_template(
        "dashboard.html",
        activities=activities,
        state_counts=state_counts,
        total_activities=total_activities,
        dominant_state=dominant_state,
        productivity_score=productivity_score,
        study_sessions=study_sessions,
        total_study_seconds=total_study_seconds,
        total_sessions_completed=total_sessions_completed,
        total_quiz_attempts=total_quiz_attempts,
        quiz_accuracy=quiz_accuracy,
        session_trend=session_trend
    )


@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        flash("Admin privilege required.")
        return redirect(url_for("dashboard"))

    conn = get_db()

    try:
        total_learners = conn.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'learner'"
        ).fetchone()[0]

        total_activities = conn.execute(
            "SELECT COUNT(*) FROM activities"
        ).fetchone()[0]

        total_sessions = conn.execute(
            "SELECT COUNT(*) FROM study_sessions"
        ).fetchone()[0]

        state_counts_rows = conn.execute(
            """
            SELECT state, COUNT(*) AS count
            FROM activities GROUP BY state
            """
        ).fetchall()

        state_counts = {state: 0 for state in ALL_STATES}

        for row in state_counts_rows:
            if row["state"] in state_counts:
                state_counts[row["state"]] = row["count"]
            elif row["state"] == "Bored":
                state_counts["Fatigued"] += row["count"]

        at_risk_learners = conn.execute(
            """
            SELECT u.id, u.name, u.email,
                   COUNT(a.id) AS stress_count
            FROM users u
            JOIN activities a ON u.id = a.user_id
            WHERE a.state IN ('Stressed', 'Confused', 'Fatigued')
            GROUP BY u.id
            ORDER BY stress_count DESC LIMIT 5
            """
        ).fetchall()

        all_activities = conn.execute(
            """
            SELECT a.*, u.name AS user_name, u.email AS user_email
            FROM activities a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.id DESC LIMIT 50
            """
        ).fetchall()

    finally:
        conn.close()

    report_path = os.path.join(BASE_DIR, "models", "evaluation_report.json")
    ml_report = None

    if os.path.exists(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as file:
                ml_report = json.load(file)
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

    try:
        activities = conn.execute(
            """
            SELECT a.id, u.name, u.email, a.modality, a.state,
                   a.confidence, a.description, a.recommendation,
                   a.created_at
            FROM activities a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.id DESC
            """
        ).fetchall()
    finally:
        conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Activity ID", "Learner Name", "Learner Email", "Modality",
        "Cognitive State", "Confidence (%)", "Reflection / Telemetry",
        "Recommendation", "Timestamp"
    ])

    for row in activities:
        writer.writerow([
            row["id"], row["name"], row["email"], row["modality"],
            row["state"], row["confidence"], row["description"],
            row["recommendation"], row["created_at"]
        ])

    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment;filename=cognitive_learning_activities.csv"
        }
    )


@app.route("/activity", methods=["GET", "POST"])
def activity():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        modality = request.form.get("modality", "text")
        manual_state = request.form.get("manual_state", "")

        if manual_state and manual_state in ALL_STATES:
            state = manual_state
            confidence = 90.0
            recommendation = RECOMMENDATIONS.get(
                state, RECOMMENDATIONS["Neutral"]
            )

            probabilities = {
                item: (
                    90.0 if item == state
                    else round(10.0 / (len(ALL_STATES) - 1), 1)
                )
                for item in ALL_STATES
            }

            intervention = get_adaptive_intervention(state, confidence)

            if not description:
                description = f"Manual state override: Selected {state} state."

        else:
            if len(description) < 3:
                flash(
                    "Please enter a slightly more descriptive reflection "
                    "or select a state."
                )
                return render_template("activity.html")

            pred = predict_cognitive_state(description)
            state = pred["state"]
            confidence = pred["confidence"]
            recommendation = pred["recommendation"]
            probabilities = pred["probabilities"]
            intervention = pred["intervention"]

        conn = get_db()

        try:
            conn.execute(
                """
                INSERT INTO activities(
                    user_id, description, state, confidence,
                    recommendation, modality
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"], description, state,
                    confidence, recommendation, modality
                )
            )
            conn.commit()
        finally:
            conn.close()

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

    # Check for start of a new assessment or explicit configuration
    show_setup = False
    requested_topic = request.args.get("topic") or request.form.get("topic")
    topic_id = requested_topic if requested_topic in [t["id"] for t in TOPICS] else session.get("study_session_topic", "python")

    topic_obj = next(
        (topic for topic in TOPICS if topic["id"] == topic_id),
        TOPICS[0]
    )

    # Check if user submitted the Assessment Setup form
    if request.method == "POST" and request.form.get("action") == "start_assessment":
        try:
            target_q = int(request.form.get("target_questions", 5))
            target_q = max(1, min(25, target_q))
        except (ValueError, TypeError):
            target_q = 5

        chosen_topic = request.form.get("topic", topic_id)
        session["study_target_questions"] = target_q
        session["study_session_topic"] = chosen_topic
        session["study_session_start"] = datetime.now().isoformat()
        session["study_questions_answered"] = 0
        session["study_score"] = 0
        session["study_correct_count"] = 0
        session["study_states_seen"] = []
        session["study_completed"] = False
        topic_id = chosen_topic
        topic_obj = next((t for t in TOPICS if t["id"] == topic_id), TOPICS[0])

    # If user wants to reset or setup has not been performed yet
    elif (
        request.args.get("setup") == "1"
        or request.args.get("restart") == "1"
        or "study_target_questions" not in session
    ):
        show_setup = True

    # Modeled Cognitive State Resolution
    param_state = request.args.get("state")
    if param_state and param_state in ALL_STATES:
        current_state = param_state
        session["current_cognitive_state"] = current_state

        conn = get_db()
        try:
            conn.execute(
                """
                INSERT INTO activities(
                    user_id, description, state, confidence,
                    recommendation, modality
                )
                VALUES (?, ?, ?, ?, ?, 'manual_override')
                """,
                (
                    user_id,
                    f"State adapted to {current_state} during {topic_obj['name']} session.",
                    current_state,
                    92.0,
                    RECOMMENDATIONS.get(current_state, "")
                )
            )
            conn.commit()
        finally:
            conn.close()

    elif "current_cognitive_state" in session:
        current_state = session["current_cognitive_state"]
    else:
        conn = get_db()
        try:
            last_activity = conn.execute(
                """
                SELECT state FROM activities
                WHERE user_id = ? ORDER BY id DESC LIMIT 1
                """,
                (user_id,)
            ).fetchone()
        finally:
            conn.close()

        current_state = (
            last_activity["state"] if last_activity else "Focused"
        )
        session["current_cognitive_state"] = current_state

    # If setup mode is active, render the setup card immediately
    if show_setup:
        intervention = get_adaptive_intervention(current_state, 88.0)
        return render_template(
            "study.html",
            show_setup=True,
            topics=TOPICS,
            selected_topic=topic_id,
            current_state=current_state,
            all_states=ALL_STATES,
            intervention=intervention,
            target_questions=session.get("study_target_questions", 5)
        )

    states_seen = session.get("study_states_seen", [])
    states_seen.append(current_state)
    session["study_states_seen"] = states_seen

    target_questions = session.get("study_target_questions", 5)
    questions_answered = session.get("study_questions_answered", 0)

    start_dt = datetime.fromisoformat(
        session.get("study_session_start", datetime.now().isoformat())
    )
    elapsed_sec = int((datetime.now() - start_dt).total_seconds())

    # Check if assessment is already completed and user refreshed or ended
    if questions_answered >= target_questions and request.method == "GET" and not request.args.get("state"):
        intervention = get_adaptive_intervention(current_state, 88.0)
        lesson = get_adaptive_lesson(topic_id, current_state)
        return render_template(
            "study.html",
            show_setup=False,
            is_completed=True,
            topics=TOPICS,
            selected_topic=topic_id,
            current_state=current_state,
            all_states=ALL_STATES,
            intervention=intervention,
            lesson=lesson,
            elapsed_sec=elapsed_sec,
            session_score=session.get("study_score", 0),
            questions_answered=questions_answered,
            target_questions=target_questions,
            correct_count=session.get("study_correct_count", 0)
        )

    conn = get_db()

    try:
        if request.args.get("reset_history") == "1":
            conn.execute(
                """
                DELETE FROM seen_questions
                WHERE user_id = ? AND topic = ?
                """,
                (user_id, topic_id)
            )
            conn.commit()

        history_rows = conn.execute(
            """
            SELECT question_id FROM quiz_attempts WHERE user_id = ?
            UNION
            SELECT question_id FROM seen_questions WHERE user_id = ?
            """,
            (user_id, user_id)
        ).fetchall()

        history_ids = [row["question_id"] for row in history_rows]

        if request.method == "POST":
            action = request.form.get("action", "submit_answer")

            if action == "end_session":
                return redirect(url_for("end_study_session"))

            question_id = request.form.get("question_id")
            try:
                selected_index = int(
                    request.form.get("selected_option", -1)
                )
            except (TypeError, ValueError):
                selected_index = -1

            current_state_input = request.form.get(
                "current_state", current_state
            )

            matched_q = next(
                (
                    question for question in QUESTION_BANK
                    if question["id"] == question_id
                ),
                None
            )

            if matched_q:
                is_correct = int(
                    selected_index == matched_q["correct_index"]
                )

                conn.execute(
                    """
                    INSERT INTO quiz_attempts(
                        user_id, question_id, is_correct, state_at_attempt
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        user_id, question_id,
                        is_correct, current_state_input
                    )
                )

                conn.execute(
                    """
                    INSERT OR IGNORE INTO seen_questions(
                        user_id, question_id, topic
                    )
                    VALUES (?, ?, ?)
                    """,
                    (user_id, question_id, topic_id)
                )
                conn.commit()

                answered = session.get("study_questions_answered", 0) + 1
                session["study_questions_answered"] = answered

                if is_correct:
                    session["study_correct_count"] = session.get("study_correct_count", 0) + 1

                points = (
                    100 if matched_q["difficulty"] == "easy"
                    else 200 if matched_q["difficulty"] == "medium"
                    else 300
                )

                if is_correct:
                    session["study_score"] = (
                        session.get("study_score", 0) + points
                    )

                start_dt = datetime.fromisoformat(
                    session.get(
                        "study_session_start",
                        datetime.now().isoformat()
                    )
                )
                elapsed_sec = int(
                    (datetime.now() - start_dt).total_seconds()
                )

                intervention = get_adaptive_intervention(
                    current_state_input, 88.0
                )
                lesson = get_adaptive_lesson(
                    topic_id, current_state_input
                )

                is_completed = (answered >= target_questions)

                return render_template(
                    "study.html",
                    show_setup=False,
                    is_completed=is_completed,
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
                    questions_answered=answered,
                    target_questions=target_questions,
                    correct_count=session.get("study_correct_count", 0)
                )

        next_question, difficulty = select_adaptive_question(
            topic_id, current_state, history_ids
        )

        conn.execute(
            """
            INSERT OR IGNORE INTO seen_questions(
                user_id, question_id, topic
            )
            VALUES (?, ?, ?)
            """,
            (user_id, next_question["id"], topic_id)
        )
        conn.commit()

    finally:
        conn.close()

    intervention = get_adaptive_intervention(current_state, 88.0)
    lesson = get_adaptive_lesson(topic_id, current_state)

    return render_template(
        "study.html",
        show_setup=False,
        is_completed=False,
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
        questions_answered=session.get("study_questions_answered", 0),
        target_questions=target_questions,
        correct_count=session.get("study_correct_count", 0)
    )


@app.route("/study/end", methods=["GET", "POST"])
def end_study_session():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    topic_id = session.get("study_session_topic", "python")

    topic_obj = next(
        (topic for topic in TOPICS if topic["id"] == topic_id),
        TOPICS[0]
    )
    topic_name = topic_obj["name"]

    start_str = session.get("study_session_start")

    if start_str:
        start_dt = datetime.fromisoformat(start_str)
        duration_seconds = max(
            10, int((datetime.now() - start_dt).total_seconds())
        )
    else:
        duration_seconds = 180

    total_questions = session.get("study_questions_answered", 0)
    score = session.get("study_score", 0)
    states_seen = session.get("study_states_seen", [])

    dominant_state = (
        Counter(states_seen).most_common(1)[0][0]
        if states_seen
        else session.get("current_cognitive_state", "Focused")
    )

    conn = get_db()

    try:
        conn.execute(
            """
            INSERT INTO study_sessions(
                user_id, topic, duration_seconds, total_questions,
                score, dominant_state, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'completed')
            """,
            (
                user_id, topic_name, duration_seconds,
                total_questions, score, dominant_state
            )
        )
        conn.commit()
    finally:
        conn.close()

    for key in (
        "study_session_start",
        "study_session_topic",
        "study_questions_answered",
        "study_score",
        "study_correct_count",
        "study_states_seen",
        "study_target_questions",
        "study_completed"
    ):
        session.pop(key, None)

    flash(
        "🎉 Adaptive Assessment completed and saved! "
        f"Duration: {format_duration(duration_seconds)} | "
        f"Questions: {total_questions} | Score: +{score} XP | "
        f"Dominant State: {dominant_state}"
    )

    return redirect(url_for("dashboard"))


@app.route("/api/predict_state", methods=["POST"])
def api_predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    result = predict_cognitive_state(text)
    return jsonify(result)


@app.route("/api/record_webcam_state", methods=["POST"])
def api_record_webcam():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    state = data.get("state", "Focused")

    try:
        confidence = float(data.get("confidence", 85.0))
    except (TypeError, ValueError):
        confidence = 85.0

    description = data.get(
        "description",
        "Facial expression and attentiveness tracking telemetry."
    )

    intervention = get_adaptive_intervention(state, confidence)

    conn = get_db()

    try:
        conn.execute(
            """
            INSERT INTO activities(
                user_id, description, state, confidence,
                recommendation, modality
            )
            VALUES (?, ?, ?, ?, ?, 'webcam')
            """,
            (
                session["user_id"],
                description,
                state,
                confidence,
                intervention["message"]
            )
        )
        conn.commit()
    finally:
        conn.close()

    session["current_cognitive_state"] = state

    return jsonify({
        "success": True,
        "state": state,
        "intervention": intervention
    })


# Initialize the database on both local runs and Vercel imports.
# The bundled database is copied to /tmp first on Vercel.
try:
    init_db()
    print("Database initialized successfully.")
except Exception as e:
    print("Database initialization failed:", e)
    raise


if __name__ == "__main__":
    print(
        "Starting Emotion-Aware Adaptive Learning & Productivity System "
        "on http://127.0.0.1:5000"
    )
    app.run(debug=True, port=5000)
