# Project Workflow Explanation
## Emotion-Aware Adaptive Learning & Productivity System
**Project Code:** `2026MIN198`

This document provides a comprehensive end-to-end breakdown of how a learner interacts with the application, how cognitive-state estimates are produced, how the adaptive curriculum engine operates, and how session tracking persists data.

---

## 1. End-to-End Learner Journey

```
[ Step 1: Authentication ]
      │
      ▼ (Logs in as learner@gmail.com)
[ Step 2: Learner Analytics Dashboard ]
      │
      ├── Inspects historical cognitive state distribution
      ├── Reviews past completed study sessions
      └── Starts an adaptive study session OR logs a new reflection
      │
      ├─── Option A: Log New Reflection / Webcam Telemetry (/activity)
      │       │
      │       ├── Submits natural language text, webcam telemetry, or manual override
      │       ├── Machine learning models infer cognitive state (e.g. Confused: 86.4%)
      │       ├── Diagnostic result page displays probability distribution & adaptation plan
      │       └── 1-click launcher immediately starts tailored study session
      │
      └─── Option B: Launch Adaptive Study Session Directly (/study)
              │
              ├── Live session timer starts counting elapsed duration
              ├── System retrieves current cognitive state
              ├── Adaptive Engine generates state-tailored micro-lesson
              ├── System selects adaptive quiz question matching target difficulty
              ├── Learner reviews concept explanation and code example
              ├── Learner attempts quiz (scaffolded hints available)
              ├── Evaluates answer, awards XP (+100, +200, +300), displays explanation
              └── Learner clicks "End & Save Session"
                      │
                      ▼
[ Step 3: Session Finalization & Persistent Logging ]
      ├── Calculates total duration in seconds
      ├── Computes total score and questions completed
      ├── Determines dominant cognitive state
      ├── Inserts record into SQLite `study_sessions` table
      └── Flashes summary alert and updates learner dashboard
```

---

## 2. How Cognitive-State Estimates Are Produced

The system supports three complementary sensing modalities:

### A. Natural Language Reflection (NLP Classification)
1. **Learner Input:** The student writes a short text reflection describing their current mental state (e.g., *"I do not understand how recursion unwinds and feel stuck"*).
2. **Text Preprocessing & Feature Extraction:**
   - Text is normalized (lowercased, stripped).
   - A `TfidfVectorizer` transforms the string using unigram and bigram tokenization (`ngram_range=(1, 2)`) with sublinear term frequency weighting (`sublinear_tf=True`).
   - Vocabulary size: 2,319 extracted n-gram features.
3. **Classification & Calibration:**
   - The serialized champion classifier—a **Calibrated Linear Support Vector Machine** (`LinearSVC` wrapped in `CalibratedClassifierCV`)—computes decision boundaries across the 6 classes:
     - `Focused`
     - `Confused`
     - `Stressed`
     - `Fatigued`
     - `Neutral`
     - `Motivated`
   - Calibrated sigmoid probability scaling maps distances from the hyperplanes into class probabilities summing to 100%.
   - The class with maximum probability is selected as the primary state, and its confidence percentage is extracted.

### B. Real-Time Client-Side Facial Telemetry (WebRTC + HTML5 Canvas)
1. **Privacy-Preserving Camera Stream:** The user grants webcam permission through the browser's standard `navigator.mediaDevices.getUserMedia()` API. No raw video or image frames are ever transmitted across the network or stored on disk.
2. **Optical Frame Telemetry:**
   - The browser draws the current video frame onto an in-memory `<canvas>`.
   - Every 1,500ms, pixel differentials between successive frames are calculated across downsampled blocks (`step = 8`).
   - An optical motion metric is computed:
     $$\text{Motion Score} = \frac{1}{N} \sum_{i=1}^{N} |I_t(i) - I_{t-1}(i)|$$
   - A 5-frame moving average filters out single-frame camera noise.
3. **Cognitive Heuristic Mapping:**
   - **Stressed:** High jitter / agitated restless movements ($\text{Motion} > 16$).
   - **Confused:** Micro-head tilts and hesitation pauses ($9 < \text{Motion} \le 16$).
   - **Fatigued:** Prolonged near-zero motion, drooping eyelids, inactive gaze ($\text{Motion} < 1.0$).
   - **Neutral:** Normal, steady baseline reading pace ($1.0 \le \text{Motion} \le 3.5$).
   - **Focused:** Sustained, steady, concentrated eye-contact ($3.5 < \text{Motion} \le 6.5$).
   - **Motivated:** Active, smiling, energetic engagement ($6.5 < \text{Motion} \le 9.0$).
4. **Interactive HUD:** The canvas overlays corner bracket bounding boxes and a status badge with confidence level.

### C. Direct Manual Fallback
- If a webcam is unavailable or in a non-GUI test environment, learners can select any of the 6 cognitive state cards directly in `/activity` or switch states directly via 1-click pills on the `/study` page.

---

## 3. How the Adaptive Learning Mechanism Works

The core intelligence of the application resides in `adaptive_engine.py`. When a study session loads, the engine executes the following logic:

### Step 1: Micro-Lesson Adaptation
The system queries `get_adaptive_lesson(topic_id, current_state)` to retrieve tailored pedagogical content:
- **Focused State:** Delivers a "Deep Dive / Mastery Challenge" analyzing memory references, internals, and edge cases.
- **Confused State:** Delivers a "Scaffolded Concept Breakdown" with visual analogies and simplified traces.
- **Stressed State:** Delivers a "Manageable Micro-Task" with calming, low-pressure fundamentals.
- **Fatigued State:** Delivers a "Quick Flash-Review" summarizing bullet-point facts with minimal cognitive load.
- **Neutral State:** Delivers the "Standard Core Curriculum" covering common idioms and practical patterns.
- **Motivated State:** Delivers a "Mastery Challenge" with bonus XP incentives.

### Step 2: Dynamic Question Difficulty Dispatcher
The function `select_adaptive_question(topic_id, current_state, history_ids)` chooses the next question:
```python
if current_state in ("Confused", "Stressed", "Fatigued"):
    target_difficulty = "easy"
elif current_state in ("Focused", "Motivated"):
    target_difficulty = "hard" if unseen_hard_available else "medium"
else: # Neutral
    target_difficulty = "medium"
```
Questions are pulled from `QUESTION_BANK`, filtering out questions the user has already answered in their history to prevent repetitive loops.

### Step 3: Pedagogical Interventions & Support Tools
- **Scaffolded Pedagogical Hints:** Every question contains two tiers of scaffolding:
  - *Hint 1:* High-level conceptual intuition.
  - *Hint 2:* Concrete step-by-step problem deduction.
  - *Rule:* Automatically expanded when in `Confused`, `Stressed`, or `Fatigued` states.
- **De-Stress 4-7-8 Calming Breathing Modal:**
  - Auto-triggers when in `Stressed` state.
  - Provides a guided visual animation: Inhale (4s) $\rightarrow$ Hold (7s) $\rightarrow$ Exhale (8s).
- **Adaptive Focus Timer (Pomodoro):**
  - Configured on the dashboard for 25-minute deep-work sprints with 5-minute restorative breaks.

---

## 4. How Study Session Tracking & Persistence Works

Session tracking is managed through Flask session state and committed to SQLite (`project.db`):

1. **Session Start:**
   - Triggered when visiting `/study?restart=1` or opening `/study` without an active session.
   - Initializes:
     - `study_session_start`: ISO-8601 timestamp.
     - `study_session_topic`: selected curriculum topic.
     - `study_questions_answered`: counter initialized to 0.
     - `study_score`: XP counter initialized to 0.
     - `study_states_seen`: list tracking states encountered.
2. **Item-Level Evaluation:**
   - Every submitted question records an entry in `quiz_attempts`:
     `user_id, question_id, is_correct, state_at_attempt, created_at`.
   - Score awards:
     - Easy question correct: `+100 XP`
     - Medium question correct: `+200 XP`
     - Hard question correct: `+300 XP`
3. **Session Finalization (`/study/end`):**
   - Calculates elapsed duration:
     $$\text{duration\_seconds} = \text{now}() - \text{study\_session\_start}$$
   - Computes dominant cognitive state using statistical mode:
     $$\text{dominant\_state} = \text{Counter}(\text{study\_states\_seen}).\text{most\_common}(1)[0][0]$$
   - Inserts record into `study_sessions`:
     ```sql
     INSERT INTO study_sessions(user_id, topic, duration_seconds, total_questions, score, dominant_state, status)
     VALUES (?, ?, ?, ?, ?, ?, 'completed');
     ```
   - Cleans active session keys and redirects to `/dashboard` with a success summary alert.
4. **Dashboard KPI Aggregation:**
   - Total Study Time is computed as `SUM(duration_seconds)` across all completed sessions.
   - Productivity Score is calculated as:
     $$\text{Productivity Score} = \frac{\text{Focused} + \text{Motivated} + (0.75 \times \text{Neutral})}{\text{Total Activities}} \times 100$$
