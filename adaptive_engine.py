"""
Adaptive Learning & Productivity Engine.
Provides dynamic difficulty adjustment, scaffolded pedagogical hints,
de-stress break triggers, and gamified engagement based on cognitive states.
"""

TOPICS = [
    {"id": "python", "name": "Python & Logic Thinking", "icon": "🐍", "description": "Core syntax, functions, loops, and algorithmic problem solving."},
    {"id": "ai_ml", "name": "AI & Machine Learning", "icon": "🤖", "description": "Supervised learning, neural networks, NLP, and model evaluation."},
    {"id": "dsa", "name": "Data Structures & Algorithms", "icon": "⚡", "description": "Arrays, stacks, queues, trees, search & sorting complexities."}
]

QUESTION_BANK = [
    # ================= PYTHON QUESTIONS =================
    {
        "id": "py_1",
        "topic": "python",
        "difficulty": "easy",
        "question": "What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(len(x))",
        "options": [
            "3 (x is unchanged)",
            "4 (y references the same list in memory)",
            "Error: cannot append to y",
            "None"
        ],
        "correct_index": 1,
        "hint_1": "In Python, variable assignment `y = x` assigns the object reference, not a deep copy.",
        "hint_2": "Because both x and y point to the same list in memory, mutating y also mutates x.",
        "explanation": "Lists in Python are mutable objects. When `y = x` is executed, both identifiers point to the identical list object. Mutating `y` with `.append(4)` directly modifies `x`, so `len(x)` is 4."
    },
    {
        "id": "py_2",
        "topic": "python",
        "difficulty": "easy",
        "question": "Which Python built-in function returns an iterator that produces tuples containing an index and the item from an iterable?",
        "options": [
            "zip()",
            "enumerate()",
            "range()",
            "map()"
        ],
        "correct_index": 1,
        "hint_1": "Think about how you loop over a list when you need both the counter index (0, 1, 2...) and the element.",
        "hint_2": "The function name literally means to 'mention a number of things one by one'.",
        "explanation": "`enumerate(iterable, start=0)` returns an enumerate object yielding `(index, value)` pairs."
    },
    {
        "id": "py_3",
        "topic": "python",
        "difficulty": "medium",
        "question": "Consider this dictionary comprehension:\n`d = {k: k**2 for k in range(5) if k % 2 != 0}`\nWhat does `d` evaluate to?",
        "options": [
            "{0: 0, 2: 4, 4: 16}",
            "{1: 1, 3: 9}",
            "{1: 2, 3: 6}",
            "[1, 9]"
        ],
        "correct_index": 1,
        "hint_1": "`range(5)` yields 0, 1, 2, 3, 4. The condition `k % 2 != 0` filters for odd numbers.",
        "hint_2": "Odd numbers in this range are 1 and 3. Their squares are 1**2 = 1 and 3**2 = 9.",
        "explanation": "The comprehension filters for odd integers in 0..4 (which are 1 and 3) and maps each to its square: `{1: 1, 3: 9}`."
    },
    {
        "id": "py_4",
        "topic": "python",
        "difficulty": "hard",
        "question": "What is the primary difference between `__new__` and `__init__` in Python OOP?",
        "options": [
            "`__init__` creates the object instance in memory, whereas `__new__` initializes its attributes.",
            "`__new__` is the static constructor that creates and returns the instance; `__init__` is the initializer that sets up instance state.",
            "`__new__` can only be used with metaclasses, while `__init__` works with standard classes.",
            "There is no functional difference; `__new__` is just deprecated syntax."
        ],
        "correct_index": 1,
        "hint_1": "One method runs before the instance even exists and is responsible for allocating memory.",
        "hint_2": "`__new__` takes `cls` as its first parameter and must return an instance of that class.",
        "explanation": "`__new__(cls, ...)` is the real constructor method that creates and returns a new empty object instance. `__init__(self, ...)` receives the already-created instance and initializes attributes."
    },

    # ================= AI / ML QUESTIONS =================
    {
        "id": "ai_1",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "In classification modeling, what metric represents the proportion of true positive predictions among all instances predicted as positive?",
        "options": [
            "Recall (Sensitivity)",
            "Precision",
            "Accuracy",
            "Specificity"
        ],
        "correct_index": 1,
        "hint_1": "Formula: TP / (TP + FP). It answers: 'Out of all items our model flagged as positive, how many were truly positive?'",
        "hint_2": "Do not confuse this with Recall, which is TP / (TP + FN).",
        "explanation": "Precision = True Positives / (True Positives + False Positives). It quantifies the exactness of the positive predictions."
    },
    {
        "id": "ai_2",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "Why is TF-IDF (Term Frequency-Inverse Document Frequency) advantageous over raw word count (Bag-of-Words)?",
        "options": [
            "It automatically detects grammatical tense and word order.",
            "It penalizes ubiquitous words (like 'the', 'is') and rewards discriminative domain-specific terms.",
            "It creates continuous dense word embeddings similar to Word2Vec.",
            "It reduces the dimensionality of the feature space to a fixed 100 dimensions."
        ],
        "correct_index": 1,
        "hint_1": "Common words appear across almost every document and provide very little informative value for topic classification.",
        "hint_2": "The IDF component takes the logarithm of total documents divided by documents containing the term.",
        "explanation": "TF measures how frequently a term appears in a document, while IDF heavily attenuates terms that appear across almost all documents. This gives high weight to words that are uniquely characteristic of specific categories."
    },
    {
        "id": "ai_3",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "When training a model with significant class imbalance (e.g., 95% Class A and 5% Class B), why is Accuracy a misleading metric?",
        "options": [
            "Because Accuracy cannot be computed when classes have different sizes.",
            "A naive model that predicts Class A 100% of the time achieves 95% accuracy while completely failing to detect Class B.",
            "Accuracy causes the gradient descent optimizer to diverge.",
            "Accuracy is only defined for binary regression, not classification."
        ],
        "correct_index": 1,
        "hint_1": "Consider what happens if a medical model always predicts 'No Disease'.",
        "hint_2": "The majority class dominates the calculation: (TP + TN) / Total. Use F1-Score or PR-AUC instead.",
        "explanation": "In an imbalanced dataset, a dummy classifier predicting the majority class exclusively will yield high accuracy (e.g. 95%), despite having zero utility for detecting the critical minority class. F1-Score or Balanced Accuracy is preferred."
    },

    # ================= DATA STRUCTURES QUESTIONS =================
    {
        "id": "dsa_1",
        "topic": "dsa",
        "difficulty": "easy",
        "question": "Which data structure operates on a Last-In, First-Out (LIFO) principle?",
        "options": [
            "Queue",
            "Stack",
            "Priority Queue",
            "Binary Search Tree"
        ],
        "correct_index": 1,
        "hint_1": "Think of a stack of plates in a cafeteria: the last plate put on top is the first one removed.",
        "hint_2": "Call stack frames and undo mechanisms in text editors use this data structure.",
        "explanation": "A Stack enforces LIFO order where insertions (`push`) and deletions (`pop`) occur at the same end (the top)."
    },
    {
        "id": "dsa_2",
        "topic": "dsa",
        "difficulty": "medium",
        "question": "What is the average time complexity of searching for an element in a balanced Binary Search Tree (BST) of N nodes?",
        "options": [
            "O(1)",
            "O(N)",
            "O(log N)",
            "O(N log N)"
        ],
        "correct_index": 2,
        "hint_1": "At each node, the search compares the target key and eliminates half of the remaining sub-tree.",
        "hint_2": "Repeatedly halving the search space corresponds to a logarithmic mathematical function.",
        "explanation": "In a balanced BST (like AVL or Red-Black tree), the tree height is bounded by O(log N). At each node comparison, one branch is discarded, yielding O(log N) search complexity."
    },
    {
        "id": "dsa_3",
        "topic": "dsa",
        "difficulty": "hard",
        "question": "Which sorting algorithm is guaranteed to run in O(N log N) worst-case time, is stable, but requires O(N) auxiliary space?",
        "options": [
            "Quicksort",
            "Heapsort",
            "Merge Sort",
            "Insertion Sort"
        ],
        "correct_index": 2,
        "hint_1": "This algorithm uses a divide-and-conquer approach: recursively split in halves, sort each half, and merge them.",
        "hint_2": "Heapsort runs in O(N log N) worst case but is not stable. Quicksort has O(N^2) worst case.",
        "explanation": "Merge Sort guarantees O(N log N) across best, average, and worst cases and preserves relative order of duplicate elements (stable). However, merging subarrays requires O(N) additional memory."
    }
]

def get_questions_for_topic(topic_id):
    return [q for q in QUESTION_BANK if q["topic"] == topic_id]

def select_adaptive_question(topic_id, current_state, history_ids=None):
    """
    Selects the next question adaptively based on the learner's current cognitive state.
    - Confused: prefers 'easy' questions, unlocks scaffolded hints.
    - Stressed: prefers 'easy' / calming questions, triggers break recommendation.
    - Focused: progresses to 'medium' or 'hard'.
    - Motivated: targets 'hard' mastery questions.
    - Bored: triggers speed/bonus questions or shifts topic.
    """
    if history_ids is None:
        history_ids = []

    topic_qs = get_questions_for_topic(topic_id)
    unseen_qs = [q for q in topic_qs if q["id"] not in history_ids]
    if not unseen_qs:
        unseen_qs = topic_qs  # cycle if completed

    target_diff = "medium"
    if current_state in ("Confused", "Stressed"):
        target_diff = "easy"
    elif current_state in ("Focused", "Motivated"):
        target_diff = "hard" if any(q["difficulty"] == "hard" for q in unseen_qs) else "medium"
    elif current_state == "Bored":
        # Give medium or hard for stimulation
        target_diff = "medium"

    matched = [q for q in unseen_qs if q["difficulty"] == target_diff]
    if matched:
        return matched[0], target_diff
    return unseen_qs[0], unseen_qs[0]["difficulty"]

def get_adaptive_intervention(state, confidence):
    """
    Generates intelligent pedagogical and productivity interventions.
    """
    interventions = {
        "Focused": {
            "badge_color": "success",
            "title": "Deep Work Flow Detected 🎯",
            "action_type": "maintain_flow",
            "difficulty_modifier": "+1 (Mastery Mode)",
            "message": "You are fully dialed into your learning material. We've queued higher-difficulty synthesis problems to maintain optimal challenge.",
            "study_tip": "Keep going! Try completing this 25-minute Pomodoro block before taking a 5-minute break.",
            "show_break_modal": False,
            "show_scaffold_hints": False
        },
        "Motivated": {
            "badge_color": "info",
            "title": "High Energy & Drive 🚀",
            "action_type": "accelerate",
            "difficulty_modifier": "+1 (Bonus XP Mode)",
            "message": "Your enthusiasm is high! Capitalize on this energy by tackling challenging topics or bonus mastery questions.",
            "study_tip": "Set an ambitious goal for this study session (e.g. 5 questions with 100% accuracy).",
            "show_break_modal": False,
            "show_scaffold_hints": False
        },
        "Confused": {
            "badge_color": "warning",
            "title": "Cognitive Obstacle Detected 💡",
            "action_type": "scaffold",
            "difficulty_modifier": "-1 (Foundational Review)",
            "message": "It looks like this concept needs clearer scaffolding. We've unlocked step-by-step hints and adjusted the question difficulty.",
            "study_tip": "Read Hint 1 and breakdown the problem statement into smaller inputs and expected outputs.",
            "show_break_modal": False,
            "show_scaffold_hints": True
        },
        "Stressed": {
            "badge_color": "danger",
            "title": "High Cognitive Overload Alert 🌿",
            "action_type": "de_stress_break",
            "difficulty_modifier": "Paused / Gentle Pace",
            "message": "Your cognitive load is elevated. Research shows high stress hinders working memory. We strongly recommend a 2-minute calming breathing reset.",
            "study_tip": "Step away from the screen for 2 minutes. Follow the guided 4-7-8 breathing exercise below.",
            "show_break_modal": True,
            "show_scaffold_hints": True
        },
        "Bored": {
            "badge_color": "secondary",
            "title": "Disengagement Warning ⚡",
            "action_type": "gamify_stimulate",
            "difficulty_modifier": "Interactive Speed Round",
            "message": "Passive repetition causes attention decay. We've switched you into an interactive challenge mode with streak bonuses.",
            "study_tip": "Try the 60-second speed challenge or switch to a new topic to re-engage your curiosity.",
            "show_break_modal": False,
            "show_scaffold_hints": False
        }
    }
    return interventions.get(state, interventions["Focused"])
