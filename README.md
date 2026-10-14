# Emotion-Aware Adaptive Learning & Productivity System
### With Real-Time Cognitive State Modeling

An end-to-end intelligent educational and productivity platform that detects, models, and adapts to a learner's real-time cognitive and emotional states (**Focused**, **Motivated**, **Confused**, **Stressed**, **Bored**) using multimodal natural language processing (NLP) and browser-based facial telemetry.

---

## 🌟 Key Features & System Modules

### 1. Multimodal Cognitive State Detection
- **Text Reflection Analysis (NLP):** Natural language reflections are processed using TF-IDF vectorization (unigrams & bigrams, sublinear term frequency) and classified across 5 distinct cognitive states.
- **Real-Time Webcam Facial Telemetry:** Lightweight, privacy-first client-side computer vision tracks facial expressions and head stability in real-time, mapping optical motion and facial patterns to emotional load without uploading raw video.
- **Confidence Scoring & Probability Distribution:** Calibrated probabilistic outputs provide granular likelihoods across all 5 states.

### 2. Machine Learning Pipeline & Benchmarking (`train_model.py`)
- Evaluates and benchmarks 4 algorithms using an 80/20 stratified split:
  1. **Calibrated Linear Support Vector Machine (Champion Model)**
  2. **Multinomial Logistic Regression**
  3. **Multinomial Naive Bayes**
  4. **Random Forest Classifier**
- Computes comprehensive evaluation metrics:
  - **Accuracy**
  - **Precision** (Weighted & Macro)
  - **Recall** (Weighted & Macro)
  - **F1-Score** (Weighted & Macro)
  - **Confusion Matrix**
- Exports serialized artifacts: `models/best_model.pkl`, `models/vectorizer.pkl`, and `models/evaluation_report.json`.

### 3. Adaptive Learning & Productivity Engine (`adaptive_engine.py`)
- **Dynamic Difficulty Adjustment:**
  - *Confused / Stressed*: Automatically drops difficulty to foundational level (`easy`) and unlocks scaffolded step-by-step hints.
  - *Focused / Motivated*: Escalates challenge to `medium` or `hard` (Mastery Mode) with bonus XP.
  - *Bored*: Engages interactive speed challenges and diverse domain questions to counter attention decay.
- **Pedagogical Interventions:**
  - **Scaffolded Conceptual Hints:** 2-tier hints (Conceptual intuition + Step-by-step deduction).
  - **De-Stress 4-7-8 Breathing Reset:** Interactive calming modal with animated breathing circle to reduce cognitive overload.
- **Adaptive Focus Timer (Pomodoro):** 25-minute deep-work timer with automated break suggestions.

### 4. Visual Analytics Dashboards
- **Learner Dashboard (`/dashboard`):**
  - KPI Stat Cards: Total Reflections, Dominant State, Productivity Score, Focus Streak.
  - Interactive Chart.js Doughnut Chart of Cognitive State Distribution.
  - Interactive Focus Timer.
  - Activity audit table with state badges, modality indicators, and recommendations.
- **Educator / Admin Command Center (`/admin`):**
  - Class-Wide Emotional Distribution Bar Chart.
  - **At-Risk Learner Alerts:** Flags students experiencing repeated stress or confusion.
  - Complete ML Model Comparison table and interactive Confusion Matrix grid.
  - **CSV Export (`/admin/export_csv`):** One-click download of all activity records for academic reporting.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### 2. Installation
Open a terminal in the project directory:
```bash
cd c:\Users\shabr\Downloads\Emotion_Aware_Adaptive_Learning_Project\emotion_adaptive_project
pip install -r requirements.txt
```

### 3. (Optional) Train & Benchmark ML Models
To re-train or generate new benchmark metrics:
```bash
python generate_dataset.py
python train_model.py
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Accounts

Use the **One-Click Quick Login** buttons on the login page, or log in with:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Learner** | `learner@gmail.com` | `1234` |
| **Admin** | `admin@gmail.com` | `1234` |

---

## 📁 Project Architecture

```
emotion_adaptive_project/
│
├── app.py                     # Main Flask web application, routing, and database handlers
├── adaptive_engine.py         # Adaptive learning engine, question banks, and pedagogical rules
├── ml_model.py                # Cognitive state prediction inference engine
├── train_model.py             # ML pipeline: multi-model training, benchmarking, and evaluation
├── generate_dataset.py        # Balanced 250-sample cognitive state dataset generator
├── requirements.txt           # Python dependency requirements
├── README.md                  # Project documentation
│
├── data/
│   └── cognitive_states_dataset.csv  # 5-class labeled dataset
│
├── models/
│   ├── best_model.pkl         # Serialized champion classifier (Linear SVM)
│   ├── vectorizer.pkl         # Serialized TF-IDF feature extractor
│   └── evaluation_report.json # Accuracy, F1-scores, and confusion matrix JSON
│
├── static/
│   ├── style.css              # Modern CSS design system with state tokens and animations
│   └── webcam.js              # Real-time client-side facial emotion & attentiveness tracker
│
└── templates/
    ├── base.html              # Core layout, navigation bar, and Chart.js integration
    ├── login.html             # Login card with 1-click demo credentials
    ├── register.html          # Registration card
    ├── dashboard.html         # Comprehensive learner analytics & focus timer
    ├── admin.html             # Educator command center, heatmaps, and ML confusion matrix
    ├── activity.html          # Multimodal input (text reflection & real-time webcam)
    ├── result.html            # Diagnostic result with confidence bar & adaptive interventions
    └── study.html             # Adaptive study studio with scaffolded hints & 4-7-8 breathing modal
```
