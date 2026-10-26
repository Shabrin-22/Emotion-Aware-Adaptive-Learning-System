"""
Inference Module for Cognitive & Emotional State Modeling.
Loads the trained ML pipeline (Calibrated Classifier + TF-IDF Vectorizer)
and yields granular predictions with class probability distribution and adaptive recommendations.
"""

import os
import joblib
import numpy as np
from adaptive_engine import get_adaptive_intervention

MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
VEC_PATH = os.path.join(MODELS_DIR, "vectorizer.pkl")

_model = None
_vectorizer = None

def _load_artifacts():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        if not (os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH)):
            # If not yet trained, train now
            import train_model
            train_model.train_and_evaluate()
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VEC_PATH)

# Load on module import
_load_artifacts()

RECOMMENDATIONS = {
    "Focused": (
        "You are in an optimal deep-work flow state. Maintain concentration, minimize ambient "
        "interruptions, and tackle higher-complexity synthesis problems."
    ),
    "Motivated": (
        "Your intrinsic drive and energy are peaked. Leverage this momentum to master challenging topics, "
        "set ambitious milestones, or unlock advanced practice challenges."
    ),
    "Confused": (
        "Cognitive dissonance detected. Concept clarity is impaired. Review foundational definitions, "
        "inspect step-by-step scaffolded hints, and solve a simplified practice problem."
    ),
    "Stressed": (
        "High cognitive overload detected. Elevated stress impedes working memory retention. "
        "Take a short 2-5 minute mindfulness or breathing break, break tasks into micro-steps, and pace yourself."
    ),
    "Fatigued": (
        "High mental fatigue and eye strain detected. Working memory capacity is depleted. "
        "Take a restorative pause, do light stretching, and complete a bite-sized micro-activity."
    ),
    "Neutral": (
        "Balanced baseline state. Continue with the standard structured curriculum and "
        "core practice exercises at a steady pace."
    ),
    "Bored": (
        "Understimulation and attention decay detected. Re-engage cognitive faculties with interactive "
        "speed challenges, gamified quiz rounds, or switch to a more stimulating subject."
    )
}

COGNITIVE_LOAD_MAP = {
    "Focused": "Optimal Flow",
    "Motivated": "Moderate / Active Engagement",
    "Confused": "Cognitive Obstacle (Misconception)",
    "Stressed": "Severe Cognitive Overload",
    "Fatigued": "Severe Cognitive Fatigue / Depleted Energy",
    "Neutral": "Standard Baseline Cognitive Load",
    "Bored": "Cognitive Understimulation"
}

def predict_cognitive_state(text: str):
    """
    Predicts cognitive/emotional state from text reflection, returning:
    - state: Primary predicted class
    - confidence: float percentage (e.g. 87.5)
    - probabilities: dict of class -> confidence percent
    - recommendation: textual recommendation
    - cognitive_load: state descriptor
    - intervention: adaptive engine action metadata
    """
    _load_artifacts()
    clean_text = text.strip()
    if not clean_text:
        return {
            "state": "Neutral",
            "confidence": 60.0,
            "probabilities": {},
            "recommendation": RECOMMENDATIONS["Neutral"],
            "cognitive_load": COGNITIVE_LOAD_MAP["Neutral"],
            "intervention": get_adaptive_intervention("Neutral", 60.0)
        }

    vec = _vectorizer.transform([clean_text])

    # Predict class
    state = _model.predict(vec)[0]

    # Predict probabilities if supported
    probs = {}
    confidence = 80.0
    if hasattr(_model, "predict_proba"):
        prob_arr = _model.predict_proba(vec)[0]
        classes = _model.classes_
        for cls_name, p in zip(classes, prob_arr):
            probs[str(cls_name)] = round(float(p) * 100, 1)
        confidence = probs.get(state, 80.0)
    elif hasattr(_model, "decision_function"):
        dec = _model.decision_function(vec)[0]
        exp_d = np.exp(dec - np.max(dec))
        soft = exp_d / np.sum(exp_d)
        for cls_name, p in zip(_model.classes_, soft):
            probs[str(cls_name)] = round(float(p) * 100, 1)
        confidence = probs.get(state, 80.0)

    recommendation = RECOMMENDATIONS.get(state, RECOMMENDATIONS["Neutral"])
    cognitive_load = COGNITIVE_LOAD_MAP.get(state, "Moderate")
    intervention = get_adaptive_intervention(state, confidence)

    return {
        "state": state,
        "confidence": confidence,
        "probabilities": probs,
        "recommendation": recommendation,
        "cognitive_load": cognitive_load,
        "intervention": intervention
    }

def predict_state(text: str):
    res = predict_cognitive_state(text)
    return res["state"], res["recommendation"]
