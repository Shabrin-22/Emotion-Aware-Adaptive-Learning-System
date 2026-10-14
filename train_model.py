"""
ML Model Training and Evaluation Pipeline.
Trains multiple classifiers on the cognitive states dataset, evaluates them using
Accuracy, Precision, Recall, F1-Score, and Confusion Matrix, and saves the best model.
"""

import os
import csv
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix
)

DATA_PATH = os.path.join("data", "cognitive_states_dataset.csv")
MODELS_DIR = "models"

def load_data(csv_path=DATA_PATH):
    texts, labels = [], []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"].strip())
            labels.append(row["state"].strip())
    return texts, labels

def train_and_evaluate():
    os.makedirs(MODELS_DIR, exist_ok=True)
    texts, labels = load_data()
    print(f"Loaded {len(texts)} samples from {DATA_PATH}")

    classes = sorted(list(set(labels)))
    print(f"Classes ({len(classes)}): {classes}")

    # Stratified Train-Test Split (80% train, 20% test)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # TF-IDF Vectorizer with unigrams & bigrams
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    print(f"Vocabulary size: {len(vectorizer.vocabulary_)} features")

    # Candidate Models (with probability calibration where helpful)
    models = {
        "Logistic Regression": LogisticRegression(C=5.0, max_iter=1000, random_state=42),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Linear SVM (Calibrated)": CalibratedClassifierCV(LinearSVC(C=1.5, random_state=42, dual=False)),
        "Random Forest": RandomForestClassifier(n_estimators=150, random_state=42)
    }

    results = {}
    best_name = None
    best_f1 = -1.0
    best_model_obj = None

    print("\n" + "="*70)
    print("MODEL COMPARISON & BENCHMARKING")
    print("="*70)
    print(f"{'Model':<25} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 70)

    for name, clf in models.items():
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        p, r, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)

        cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()
        report_dict = classification_report(y_test, y_pred, labels=classes, output_dict=True, zero_division=0)

        results[name] = {
            "accuracy": round(float(acc), 4),
            "precision_weighted": round(float(p), 4),
            "recall_weighted": round(float(r), 4),
            "f1_weighted": round(float(f1), 4),
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "confusion_matrix": cm,
            "classification_report": report_dict
        }

        print(f"{name:<25} | {acc:<10.4f} | {p:<10.4f} | {r:<10.4f} | {f1:<10.4f}")

        if f1_macro > best_f1:
            best_f1 = f1_macro
            best_name = name
            best_model_obj = clf

    print("=" * 70)
    print(f"-> Selected Champion Model: {best_name} (F1 Macro: {best_f1:.4f})")

    # Save artifacts
    model_path = os.path.join(MODELS_DIR, "best_model.pkl")
    vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")
    report_path = os.path.join(MODELS_DIR, "evaluation_report.json")

    joblib.dump(best_model_obj, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    full_report = {
        "dataset_samples": len(texts),
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "classes": classes,
        "champion_model": best_name,
        "models": results
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(full_report, f, indent=2)

    print(f"Artifacts saved successfully:")
    print(f" - Model: {model_path}")
    print(f" - Vectorizer: {vectorizer_path}")
    print(f" - Metrics & Confusion Matrix: {report_path}")

    # Display Champion Detailed Report
    print("\nChampion Model Classification Report:")
    champion_pred = best_model_obj.predict(X_test)
    print(classification_report(y_test, champion_pred, labels=classes, zero_division=0))

    return full_report

if __name__ == "__main__":
    train_and_evaluate()
