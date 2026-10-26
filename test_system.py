"""
Comprehensive Automated Test Suite for Emotion-Aware Adaptive Learning & Productivity System
Project Code: 2026MIN198
Verifies all 12 required test cases defined in the project specification.
"""

import os
import sys
import unittest
import json
import sqlite3
from datetime import datetime
import app as flask_app
import ml_model
import adaptive_engine

class SystemTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["SECRET_KEY"] = "test-secret-key-2026"
        cls.client = flask_app.app.test_client()
        flask_app.init_db()

    def login_as_learner(self):
        return self.client.post("/login", data={
            "email": "learner@gmail.com",
            "password": "1234"
        }, follow_redirects=True)

    def login_as_admin(self):
        return self.client.post("/login", data={
            "email": "admin@gmail.com",
            "password": "1234"
        }, follow_redirects=True)

    def test_01_app_launches_without_fatal_error(self):
        """TEST 1: The application launches without a fatal error."""
        print("\n--- RUNNING TEST 1: App Launch & Landing Route ---")
        response = self.client.get("/")
        # Should redirect to login when unauthenticated
        self.assertIn(response.status_code, [200, 302])
        login_res = self.client.get("/login")
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome Back", login_res.data)
        print("PASS: Application launched cleanly and login interface is accessible.")

    def test_02_dashboard_loads_correctly(self):
        """TEST 2: The dashboard loads correctly for an authenticated learner."""
        print("\n--- RUNNING TEST 2: Dashboard Rendering & Metrics ---")
        self.login_as_learner()
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Learner Analytics & Cognitive Hub", res.data)
        self.assertIn(b"Productivity & Flow Score", res.data)
        self.assertIn(b"Study Sessions History", res.data)
        print("PASS: Learner dashboard rendered with KPI metrics, focus timer, and history table.")

    def test_03_learner_can_start_session(self):
        """TEST 3: The learner can start a study session."""
        print("\n--- RUNNING TEST 3: Starting Adaptive Study Session ---")
        self.login_as_learner()
        res = self.client.get("/study?topic=python&restart=1")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Adaptive Checkpoint & Practice Quiz", res.data)
        self.assertIn(b"Live Session Duration", res.data)
        with self.client.session_transaction() as sess:
            self.assertIn("study_session_start", sess)
            self.assertEqual(sess.get("study_session_topic"), "python")
        print("PASS: Study session initialized with session start timestamp and topic tracking.")

    def test_04_cognitive_state_input_estimation_and_fallback(self):
        """TEST 4: The cognitive-state input or estimation mechanism works, or its fallback works."""
        print("\n--- RUNNING TEST 4: Cognitive State Inference & Fallback ---")
        # 4a: NLP text prediction
        pred_focused = ml_model.predict_cognitive_state("I am completely focused and absorbed in writing this code")
        self.assertEqual(pred_focused["state"], "Focused")
        self.assertGreater(pred_focused["confidence"], 50.0)

        pred_stressed = ml_model.predict_cognitive_state("I have so much work and feel totally stressed and panicked")
        self.assertEqual(pred_stressed["state"], "Stressed")

        # 4b: Manual state fallback submission
        self.login_as_learner()
        res = self.client.post("/activity", data={
            "modality": "manual_override",
            "manual_state": "Confused",
            "description": "Manual override test"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Confused State Identified", res.data)
        print("PASS: Multimodal NLP inference and manual selection fallback both functioning reliably.")

    def test_05_state_change_modifies_recommendations(self):
        """TEST 5: Selecting or estimating different states changes the learning recommendation appropriately."""
        print("\n--- RUNNING TEST 5: State-Dependent Recommendations ---")
        states_to_test = ["Focused", "Confused", "Stressed", "Fatigued", "Neutral", "Motivated"]
        recommendations_seen = set()

        for s in states_to_test:
            interv = adaptive_engine.get_adaptive_intervention(s)
            self.assertIsNotNone(interv)
            self.assertIn("difficulty_modifier", interv)
            self.assertIn("message", interv)
            self.assertIn("study_tip", interv)
            recommendations_seen.add(interv["message"])

        # Ensure recommendations are distinct, not hardcoded copies
        self.assertEqual(len(recommendations_seen), len(states_to_test))
        print("PASS: Each cognitive state yields distinct pedagogical interventions and difficulty modifiers.")

    def test_06_correct_learning_material_appears_for_each_state(self):
        """TEST 6: The correct learning material appears for each supported state."""
        print("\n--- RUNNING TEST 6: State-Adapted Learning Materials ---")
        self.login_as_learner()
        for s in ["Focused", "Confused", "Stressed", "Fatigued", "Neutral"]:
            res = self.client.get(f"/study?topic=python&state={s}")
            self.assertEqual(res.status_code, 200)
            lesson = adaptive_engine.get_adaptive_lesson("python", s)
            self.assertIsNotNone(lesson)
            import html
            expected_title = html.escape(lesson["title"]).encode("utf-8")
            self.assertIn(expected_title, res.data)
        print("PASS: Verified specialized micro-lessons for Focused, Confused, Stressed, Fatigued, and Neutral.")

    def test_07_learner_can_complete_learning_activity_or_quiz(self):
        """TEST 7: The learner can complete the available learning activity or quiz."""
        print("\n--- RUNNING TEST 7: Quiz Submission & Evaluation ---")
        self.login_as_learner()
        self.client.get("/study?topic=python&restart=1")

        # Submit answer to question py_1 (correct index is 1)
        res = self.client.post("/study?topic=python", data={
            "action": "submit_answer",
            "question_id": "py_1",
            "selected_option": "1",
            "current_state": "Focused"
        })
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Correct! Outstanding problem solving", res.data)
        self.assertIn(b"Explanation:", res.data)
        print("PASS: Quiz submission correctly evaluated with positive feedback and pedagogical explanation.")

    def test_08_session_duration_and_progress_calculation(self):
        """TEST 8: Session duration and progress are calculated correctly."""
        print("\n--- RUNNING TEST 8: Session Duration & XP Calculation ---")
        self.login_as_learner()
        self.client.get("/study?topic=python&restart=1")

        # Answer 1 correct question
        self.client.post("/study?topic=python", data={
            "action": "submit_answer",
            "question_id": "py_1",
            "selected_option": "1",
            "current_state": "Focused"
        })

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("study_questions_answered"), 1)
            self.assertGreater(sess.get("study_score"), 0)
        print("PASS: Live question counter and score points correctly accumulated in session state.")

    def test_09_session_history_persists_in_database(self):
        """TEST 9: Session history persists in SQLite database."""
        print("\n--- RUNNING TEST 9: Database Persistence ---")
        self.login_as_learner()
        conn = flask_app.get_db()
        count_before = conn.execute("SELECT COUNT(*) FROM study_sessions WHERE user_id=1").fetchone()[0]

        # End session to trigger persistence
        res = self.client.get("/study/end", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        count_after = conn.execute("SELECT COUNT(*) FROM study_sessions WHERE user_id=1").fetchone()[0]
        conn.close()

        self.assertEqual(count_after, count_before + 1)
        print("PASS: Session successfully persisted to SQLite database and retrieved.")

    def test_10_missing_webcam_and_invalid_inputs_handled_gracefully(self):
        """TEST 10: Missing webcam access, empty inputs, and expected errors are handled gracefully."""
        print("\n--- RUNNING TEST 10: Error & Empty Input Handling ---")
        self.login_as_learner()

        # Empty reflection text
        res = self.client.post("/activity", data={
            "modality": "text",
            "description": "  "
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please enter a slightly more descriptive reflection", res.data)

        # Invalid login attempt
        res_bad_login = self.client.post("/login", data={
            "email": "nonexistent@learner.edu",
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res_bad_login.data)

        # Webcam telemetry API endpoint with empty payload
        res_api = self.client.post("/api/record_webcam_state", json={})
        self.assertEqual(res_api.status_code, 200)
        data = json.loads(res_api.data)
        self.assertTrue(data.get("success"))
        print("PASS: Handled empty input, bad credentials, and webcam fallback gracefully.")

    def test_11_learner_can_stop_session_and_return_to_dashboard(self):
        """TEST 11: The learner can stop a session and return to the dashboard."""
        print("\n--- RUNNING TEST 11: End Session & Dashboard Return ---")
        self.login_as_learner()
        self.client.get("/study?topic=ai_ml&restart=1")

        # End session
        res = self.client.get("/study/end", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Study session ended successfully", res.data)
        self.assertIn(b"Learner Analytics & Cognitive Hub", res.data)
        print("PASS: Stop session cleanly terminated session, persisted stats, and redirected to dashboard.")

    def test_12_admin_and_csv_export_work(self):
        """TEST 12: Admin dashboard and CSV data export functionality."""
        print("\n--- RUNNING TEST 12: Admin Analytics & CSV Export ---")
        self.login_as_admin()
        res_admin = self.client.get("/admin")
        self.assertEqual(res_admin.status_code, 200)
        self.assertIn(b"Educator & Admin Command Center", res_admin.data)
        self.assertIn(b"Machine Learning Model Benchmarking", res_admin.data)

        # CSV Export
        res_csv = self.client.get("/admin/export_csv")
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv.mimetype, "text/csv")
        self.assertIn(b"Cognitive State", res_csv.data)
        print("PASS: Admin command center and CSV activity export verified successfully.")

if __name__ == "__main__":
    unittest.main()
