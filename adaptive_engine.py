"""
Adaptive Learning & Productivity Engine.
Provides genuine state-dependent content adaptation, dynamic difficulty adjustment,
scaffolded pedagogical hints, de-stress interventions, and micro-learning activities
based on real-time cognitive states: Focused, Confused, Stressed, Fatigued, Neutral, Motivated.
"""

import random
import copy

TOPICS = [
    {
        "id": "python",
        "name": "Python & Algorithmic Problem Solving",
        "icon": "🐍",
        "description": "Core syntax, mutable objects, list/dict comprehensions, memory model, and OOP architecture."
    },
    {
        "id": "ai_ml",
        "name": "AI & Machine Learning Foundations",
        "icon": "🤖",
        "description": "Supervised modeling, TF-IDF vectorization, evaluation metrics, overfitting, and loss functions."
    },
    {
        "id": "dsa",
        "name": "Data Structures & Algorithms",
        "icon": "⚡",
        "description": "Stacks, queues, BST complexity, sorting bounds, and graph search paradigms."
    }
]

# State-dependent learning materials (Micro-Lessons adapted to cognitive states)
LEARNING_MATERIALS = {
    "python": {
        "Focused": {
            "title": "Deep Dive: Memory References & Python Object Mutability",
            "tag": "Mastery Challenge",
            "summary": (
                "In Python, variables do not store values directly; they store memory references to objects. "
                "Mutable objects (lists, dictionaries, sets) can be altered in-place, meaning aliased variables "
                "(`y = x`) will observe all mutations made through either reference. Understanding the difference "
                "between shallow copies (`copy.copy()`) and deep copies (`copy.deepcopy()`) is crucial for building "
                "robust concurrent and recursive algorithms."
            ),
            "code_example": (
                "# Memory alias demonstration\n"
                "x = [1, 2, 3]\n"
                "y = x          # y references the exact same list object in memory\n"
                "y.append(4)   # Mutating through y directly alters x\n"
                "print(x)      # Output: [1, 2, 3, 4] (len is 4, not 3!)\n"
                "print(id(x) == id(y)) # True: identical memory address"
            ),
            "key_takeaway": "Assignment in Python never copies data; it binds names to existing memory addresses.",
            "recommended_action": "Tackle the Hard synthesis question below to verify mastery of object lifecycles."
        },
        "Confused": {
            "title": "Concept Breakdown: What Really Happens in `y = x`?",
            "tag": "Scaffolded Revision",
            "summary": (
                "Think of a Python variable like a nametag or sticky note stuck onto a box, rather than the box itself. "
                "When you write `x = [1, 2, 3]`, Python creates a list box in memory and puts the nametag 'x' on it. "
                "When you write `y = x`, you are NOT making a second box! You are simply sticking a second nametag 'y' "
                "onto the exact same box. If you put another item inside that box through 'y', looking in the box through 'x' "
                "reveals that new item too!"
            ),
            "code_example": (
                "# Visual nametag analogy:\n"
                "box = [1, 2, 3]\n"
                "# Both 'x' and 'y' point to ONE box:\n"
                "# [x] ---> [ 1, 2, 3 ] <--- [y]\n"
                "# If y adds 4:\n"
                "# [x] ---> [ 1, 2, 3, 4 ] <--- [y]"
            ),
            "key_takeaway": "To create a truly independent new list, use `y = list(x)` or `y = x.copy()`.",
            "recommended_action": "Read Hint 1 and Hint 2 on the quiz below to build step-by-step confidence."
        },
        "Stressed": {
            "title": "Manageable Micro-Task: Python List Fundamentals",
            "tag": "Gentle Pace",
            "summary": (
                "Take a deep breath. Let's step back from heavy syntax and remember the core essentials. "
                "Lists in Python are ordered collections written inside square brackets `[...]`. "
                "Items are accessed using zero-based indices: the first item is `items[0]`, and the last is `items[-1]`. "
                "You can add items using `.append(val)` and check the total count with `len(items)`."
            ),
            "code_example": (
                "# Keep it simple:\n"
                "fruits = ['apple', 'banana']\n"
                "fruits.append('cherry')\n"
                "print(len(fruits))  # Output: 3"
            ),
            "key_takeaway": "Focus on one simple operation at a time. No complex logic required right now.",
            "recommended_action": "Take a 2-minute calming breathing break if needed, then answer this straightforward question."
        },
        "Fatigued": {
            "title": "Quick Flash-Review: Python Built-In Functions",
            "tag": "Low-Load Flashcard",
            "summary": (
                "When your brain is fatigued, avoid heavy code traces. Here is a quick 30-second memory saver: "
                "1. `len(seq)`: returns element count. "
                "2. `enumerate(seq)`: yields `(index, item)` pairs for easy looping. "
                "3. `zip(a, b)`: pairs up elements from two lists side by side."
            ),
            "code_example": (
                "# 30-Second Glance:\n"
                "for i, val in enumerate(['a', 'b']):\n"
                "    print(i, val)  # 0 a, then 1 b"
            ),
            "key_takeaway": "Use `enumerate()` whenever you need both the loop counter and the value.",
            "recommended_action": "Complete this low-intensity review question, then consider a 5-minute screen rest."
        },
        "Neutral": {
            "title": "Standard Curriculum: Python Collections & Iteration Patterns",
            "tag": "Core Curriculum",
            "summary": (
                "Python provides powerful idiomatic patterns for data processing. "
                "Comprehensions allow constructing lists and dictionaries with readable, concise syntax. "
                "Standard functions like `enumerate()` and `zip()` streamline iteration without manual counters."
            ),
            "code_example": (
                "# Common Pythonic Idiom:\n"
                "squares = [x**2 for x in range(5) if x % 2 == 0]\n"
                "print(squares)  # Output: [0, 4, 16]"
            ),
            "key_takeaway": "Comprehensions combine mapping and filtering into a single expressive expression.",
            "recommended_action": "Proceed with the standard medium-difficulty practice question."
        },
        "Motivated": {
            "title": "Mastery Challenge: Dunder Methods & Metaclass Object Construction",
            "tag": "Mastery Sprint (+XP)",
            "summary": (
                "Channel your high motivation into deep Python internals! "
                "In Python's object model, object instantiation happens in two distinct phases: "
                "`__new__(cls)` is the static allocator that creates the raw instance in memory, "
                "while `__init__(self)` initializes instance attributes. Understanding `__new__` is essential "
                "for implementing singletons, immutable subclasses (like subclassing `tuple`), and custom metaclasses."
            ),
            "code_example": (
                "class Singleton:\n"
                "    _instance = None\n"
                "    def __new__(cls, *args, **kwargs):\n"
                "        if not cls._instance:\n"
                "            cls._instance = super().__new__(cls)\n"
                "        return cls._instance"
            ),
            "key_takeaway": "`__new__` creates and returns the instance; `__init__` sets its initial state.",
            "recommended_action": "Attempt the Hard mastery question below to lock in bonus mastery points."
        }
    },
    "ai_ml": {
        "Focused": {
            "title": "Deep Dive: Imbalanced Classification & Metric Discriminability",
            "tag": "Mastery Challenge",
            "summary": (
                "In real-world machine learning, datasets frequently exhibit extreme class skew (e.g. 98% negative, 2% positive). "
                "In such settings, simple Accuracy is dangerously deceptive because a trivial model predicting the majority class "
                "attains 98% accuracy while failing 100% of the critical cases. To properly assess model utility, engineers use "
                "Precision-Recall AUC, Balanced Accuracy, and Macro F1-Score, which computes an unweighted average across classes."
            ),
            "code_example": (
                "# Metric comparison in imbalanced scenario:\n"
                "# Majority: 950 samples, Minority: 50 samples\n"
                "# Trivial classifier predicting all Majority:\n"
                "# Accuracy = 950 / 1000 = 95.0% (Misleading!)\n"
                "# Minority Recall = 0 / 50 = 0.0% (Complete Failure!)"
            ),
            "key_takeaway": "Never rely solely on Accuracy when class distributions are asymmetrical.",
            "recommended_action": "Test your knowledge on the evaluation metric challenge below."
        },
        "Confused": {
            "title": "Concept Breakdown: Precision vs. Recall Made Simple",
            "tag": "Scaffolded Revision",
            "summary": (
                "Let's clear up the confusion between Precision and Recall using a simple medical test analogy: "
                "1. **Precision** answers: 'Of all patients the model flagged as SICK, how many were ACTUALLY sick?' "
                "   Formula: True Positives / (True Positives + False Positives). "
                "2. **Recall** answers: 'Of all people who were ACTUALLY sick, how many did the model FIND?' "
                "   Formula: True Positives / (True Positives + False Negatives)."
            ),
            "code_example": (
                "# Quick Reference:\n"
                "# Precision = Quality of positive predictions (avoiding false alarms)\n"
                "# Recall    = Quantity of positive instances captured (avoiding missed cases)"
            ),
            "key_takeaway": "Precision cares about avoiding false alarms; Recall cares about not missing real cases.",
            "recommended_action": "Use the scaffolding hints below to solve the foundational question."
        },
        "Stressed": {
            "title": "Manageable Micro-Task: Core Machine Learning Categories",
            "tag": "Gentle Pace",
            "summary": (
                "No need to worry about complex mathematical derivations right now. Let's keep it grounded: "
                "Machine learning is broadly split into two primary paradigms: "
                "1. **Supervised Learning**: The algorithm learns from labeled data with known correct answers (e.g. predicting house prices or sentiment labels). "
                "2. **Unsupervised Learning**: The algorithm finds hidden patterns in unlabeled data (e.g. customer segmentation clustering)."
            ),
            "code_example": (
                "# Keep it clear:\n"
                "# Labeled data (Input X + Target Y)  -> Supervised\n"
                "# Unlabeled data (Input X only)       -> Unsupervised"
            ),
            "key_takeaway": "Labels define supervised learning; pattern grouping defines unsupervised learning.",
            "recommended_action": "Take your time and answer this gentle foundational question."
        },
        "Fatigued": {
            "title": "Quick Flash-Review: Common AI/ML Terminology",
            "tag": "Low-Load Flashcard",
            "summary": (
                "Rest your eyes and review this bite-sized flashcard: "
                "- **Overfitting**: Model memorizes training noise and fails on new test data. "
                "- **Underfitting**: Model is too simple to capture even the basic training patterns. "
                "- **Feature**: An individual measurable property or variable used as input."
            ),
            "code_example": (
                "# 30-Second Summary:\n"
                "# High train score + Low test score  = Overfitting\n"
                "# Low train score + Low test score   = Underfitting"
            ),
            "key_takeaway": "Good models generalize well to unseen test data rather than memorizing training data.",
            "recommended_action": "Answer this quick check-in question, then take a short rest."
        },
        "Neutral": {
            "title": "Standard Curriculum: Feature Representation with TF-IDF",
            "tag": "Core Curriculum",
            "summary": (
                "To process text in machine learning algorithms, strings must be transformed into numerical vectors. "
                "TF-IDF (Term Frequency - Inverse Document Frequency) improves on raw word counts by rewarding terms "
                "that appear frequently in a specific text while penalizing common stopwords that appear across all documents."
            ),
            "code_example": (
                "# TF-IDF Intuition:\n"
                "# TF:  How often word appears in document D\n"
                "# IDF: Log(Total Documents / Docs containing word)\n"
                "# Result: Common words ('the', 'is') get near 0 weight."
            ),
            "key_takeaway": "TF-IDF provides high weights to words that are uniquely discriminative of a topic.",
            "recommended_action": "Answer the standard question on feature extraction."
        },
        "Motivated": {
            "title": "Mastery Challenge: Loss Functions & Regularization Tradeoffs",
            "tag": "Mastery Sprint (+XP)",
            "summary": (
                "Ready for an advanced challenge! "
                "In high-dimensional feature spaces, linear classifiers can overfit without regularization. "
                "L1 regularization (Lasso) encourages parameter sparsity by penalizing the absolute sum of weights, "
                "effectively performing automated feature selection. L2 regularization (Ridge) penalizes squared weights, "
                "shrinking coefficients evenly and handling multicollinearity."
            ),
            "code_example": (
                "# Regularization penalties:\n"
                "# L1 Loss = Data_Loss + lambda * sum(|w_i|)      (Sparse weights)\n"
                "# L2 Loss = Data_Loss + lambda * sum(w_i^2)     (Smooth weights)"
            ),
            "key_takeaway": "L1 produces sparse feature sets; L2 prevents individual features from dominating.",
            "recommended_action": "Conquer the advanced machine learning challenge below."
        }
    },
    "dsa": {
        "Focused": {
            "title": "Deep Dive: Asymptotic Complexity & Worst-Case Guarantees",
            "tag": "Mastery Challenge",
            "summary": (
                "When selecting algorithms for mission-critical software, worst-case upper bounds dictate system reliability. "
                "While Quicksort achieves O(N log N) average runtime, unbalanced pivots degrade it to O(N^2) worst case. "
                "Merge Sort guarantees O(N log N) worst-case time and is stable, but requires O(N) auxiliary space. "
                "Heapsort achieves O(N log N) in-place (O(1) aux space) but is not stable. Understanding these tradeoffs is essential."
            ),
            "code_example": (
                "# Algorithm Tradeoff Summary:\n"
                "# Quicksort:  Avg O(N log N), Worst O(N^2), Space O(log N), Unstable\n"
                "# Merge Sort: Avg O(N log N), Worst O(N log N), Space O(N), Stable\n"
                "# Heapsort:   Avg O(N log N), Worst O(N log N), Space O(1), Unstable"
            ),
            "key_takeaway": "Choose Merge Sort when stability and strict O(N log N) worst-case bounds are required.",
            "recommended_action": "Solve the Hard complexity analysis problem below."
        },
        "Confused": {
            "title": "Concept Breakdown: Stack (LIFO) vs. Queue (FIFO) Visualized",
            "tag": "Scaffolded Revision",
            "summary": (
                "Let's make Stacks and Queues crystal clear with everyday real-world objects: "
                "1. **Stack = A stack of cafeteria plates**. The LAST plate placed on top is the FIRST plate you pick up. "
                "   This is **LIFO** (Last-In, First-Out). Operations are `push()` (add to top) and `pop()` (remove from top). "
                "2. **Queue = A line of people at a cinema ticket counter**. The FIRST person to arrive is the FIRST person served. "
                "   This is **FIFO** (First-In, First-Out). Operations are `enqueue()` (join back) and `dequeue()` (leave front)."
            ),
            "code_example": (
                "# Stack (LIFO):\n"
                "# push(1) -> push(2) -> pop() returns 2!\n\n"
                "# Queue (FIFO):\n"
                "# enqueue(1) -> enqueue(2) -> dequeue() returns 1!"
            ),
            "key_takeaway": "Stack = undo button / plate stack (LIFO). Queue = ticket line / printer queue (FIFO).",
            "recommended_action": "Review the hints on the question below to solidify your understanding."
        },
        "Stressed": {
            "title": "Manageable Micro-Task: Arrays & Direct Index Access",
            "tag": "Gentle Pace",
            "summary": (
                "Take it easy. Let's look at the simplest, most fundamental data structure: the Array. "
                "An array stores items in contiguous (touching) blocks of computer memory. "
                "Because every element has a fixed size and elements are placed side-by-side, finding an item by its index "
                "is instantaneous! The computer calculates the memory address directly: `base_address + index * item_size`."
            ),
            "code_example": (
                "# Direct Instant Access:\n"
                "nums = [10, 20, 30, 40]\n"
                "print(nums[2])  # 30 (instant O(1) lookup)"
            ),
            "key_takeaway": "Array lookup by index is instantaneous O(1) time because memory is contiguous.",
            "recommended_action": "Answer this friendly data structures check-in."
        },
        "Fatigued": {
            "title": "Quick Flash-Review: Big-O Time Complexities at a Glance",
            "tag": "Low-Load Flashcard",
            "summary": (
                "Quick energy-saving reference: "
                "- `O(1)`: Constant time (instant, like array index access). "
                "- `O(log N)`: Logarithmic time (cutting search space in half, like binary search). "
                "- `O(N)`: Linear time (looking at every single item once). "
                "- `O(N^2)`: Quadratic time (nested loops over all items)."
            ),
            "code_example": (
                "# Efficiency Hierarchy (Fastest to Slowest):\n"
                "# O(1) < O(log N) < O(N) < O(N log N) < O(N^2)"
            ),
            "key_takeaway": "Logarithmic O(log N) algorithms scale exceptionally well even for billions of records.",
            "recommended_action": "Answer one brief review question, then rest your eyes."
        },
        "Neutral": {
            "title": "Standard Curriculum: Binary Search Trees & Divide-and-Conquer",
            "tag": "Core Curriculum",
            "summary": (
                "A Binary Search Tree (BST) organizes data such that for every node, all keys in its left subtree are smaller, "
                "and all keys in its right subtree are larger. When searching for a target key, the algorithm compares the target "
                "with the current node and discards half the remaining tree at each step. In a balanced BST, this yields O(log N) search."
            ),
            "code_example": (
                "# BST Search Logic:\n"
                "# If target == node.val: Found!\n"
                "# If target < node.val:  Go Left\n"
                "# If target > node.val:  Go Right\n"
                "# Each step eliminates 50% of remaining candidates."
            ),
            "key_takeaway": "Balanced BST search takes O(log N) average time by halving the search space at each node.",
            "recommended_action": "Proceed with the standard medium-difficulty question below."
        },
        "Motivated": {
            "title": "Mastery Challenge: Graph Search Algorithms & Dijkstra's Invariant",
            "tag": "Mastery Sprint (+XP)",
            "summary": (
                "Challenge yourself with advanced graph theory! "
                "Dijkstra's shortest path algorithm greedily settles vertices in order of their tentative distance from the source. "
                "By maintaining a Min-Priority Queue (Min-Heap), extracting the minimum distance vertex takes O(log V) time, "
                "yielding a total runtime of O((V + E) log V). It relies on the invariant that edge weights must be non-negative; "
                "for negative weights, the Bellman-Ford algorithm O(V * E) must be used instead."
            ),
            "code_example": (
                "# Dijkstra Complexity:\n"
                "# Vertices V, Edges E\n"
                "# Min-Heap operations: O((V + E) log V)\n"
                "# Requires: Non-negative edge weights!"
            ),
            "key_takeaway": "Dijkstra fails on negative edge cycles; Bellman-Ford is required for negative weights.",
            "recommended_action": "Tackle the Hard data structures question to earn bonus XP."
        }
    }
}

QUESTION_BANK = [
    # ================= PYTHON QUESTIONS =================
    {
        "id": "py_1",
        "topic": "python",
        "difficulty": "easy",
        "question": "What is the output of the following Python code?\n\nx = [1, 2, 3]\ny = x\ny.append(4)\nprint(len(x))",
        "options": [
            "3 (x is unaffected)",
            "4 (y references the identical list in memory)",
            "Error: cannot append to y",
            "None"
        ],
        "correct_index": 1,
        "hint_1": "In Python, variable assignment `y = x` binds a second name to the same object, not a clone.",
        "hint_2": "Because both x and y point to the same list in memory, mutating y also directly mutates x.",
        "explanation": "Lists in Python are mutable objects. When `y = x` runs, both identifiers reference the identical memory object. Appending to `y` modifies `x` too, resulting in length 4."
    },
    {
        "id": "py_2",
        "topic": "python",
        "difficulty": "easy",
        "question": "Which Python built-in function returns an iterator yielding pairs of (index, item) when iterating over a sequence?",
        "options": [
            "zip()",
            "enumerate()",
            "range()",
            "map()"
        ],
        "correct_index": 1,
        "hint_1": "Think of how you loop through a list when you need both the counter index (0, 1, 2...) and the element itself.",
        "hint_2": "The function name literally means to count or mention things one by one.",
        "explanation": "`enumerate(iterable, start=0)` returns an enumerate object yielding `(index, value)` pairs during iteration."
    },
    {
        "id": "py_3",
        "topic": "python",
        "difficulty": "medium",
        "question": "Consider this dictionary comprehension:\n`d = {k: k**2 for k in range(5) if k % 2 != 0}`\nWhat is the evaluated value of `d`?",
        "options": [
            "{0: 0, 2: 4, 4: 16}",
            "{1: 1, 3: 9}",
            "{1: 2, 3: 6}",
            "[1, 9]"
        ],
        "correct_index": 1,
        "hint_1": "`range(5)` produces numbers 0, 1, 2, 3, 4. The `if k % 2 != 0` condition keeps only odd numbers.",
        "hint_2": "The odd numbers are 1 and 3. Their squares are 1**2 = 1 and 3**2 = 9.",
        "explanation": "The comprehension filters for odd integers in 0..4 (which are 1 and 3) and maps each key to its square: `{1: 1, 3: 9}`."
    },
    {
        "id": "py_4",
        "topic": "python",
        "difficulty": "medium",
        "question": "What is the result of evaluating `bool([])`, `bool([0])`, and `bool('')` in Python?",
        "options": [
            "False, False, False",
            "False, True, False",
            "True, True, True",
            "False, True, True"
        ],
        "correct_index": 1,
        "hint_1": "Empty containers (empty list `[]`, empty string `''`) evaluate to False in boolean context.",
        "hint_2": "A list with any element—even 0 (`[0]`)—is non-empty and evaluates to True.",
        "explanation": "In Python truth-value testing, empty collections (`[]`, `''`, `{}`) are falsy. However, `[0]` is a non-empty list of length 1, so it evaluates to True."
    },
    {
        "id": "py_5",
        "topic": "python",
        "difficulty": "hard",
        "question": "What is the primary difference between `__new__` and `__init__` in Python OOP?",
        "options": [
            "`__init__` creates the object instance in memory, whereas `__new__` initializes its attributes.",
            "`__new__` is the static constructor that creates and returns the instance; `__init__` is the initializer that sets up attributes on the already-created instance.",
            "`__new__` can only be used with metaclasses, while `__init__` works with standard classes.",
            "There is no functional difference; `__new__` is just deprecated syntax."
        ],
        "correct_index": 1,
        "hint_1": "One method runs before the instance exists and allocates memory; the other runs after to initialize values.",
        "hint_2": "`__new__` takes `cls` as its first parameter and must return an instance of that class.",
        "explanation": "`__new__(cls, ...)` is the real constructor method that creates and returns a new empty object instance. `__init__(self, ...)` receives the already-created instance and initializes attributes."
    },
    {
        "id": "py_6",
        "topic": "python",
        "difficulty": "easy",
        "question": "Which of the following built-in data types in Python is IMMUTABLE?",
        "options": [
            "List",
            "Dictionary",
            "Tuple",
            "Set"
        ],
        "correct_index": 2,
        "hint_1": "Once created, elements in this collection cannot be appended, removed, or reassigned in-place.",
        "hint_2": "This collection is written using parentheses `(...)`.",
        "explanation": "Tuples, numbers, strings, and frozensets are immutable in Python. Lists, dictionaries, and sets are mutable and can be altered in-place."
    },
    {
        "id": "py_7",
        "topic": "python",
        "difficulty": "easy",
        "question": "What will `type(3.14)` return in Python 3?",
        "options": [
            "<class 'int'>",
            "<class 'float'>",
            "<class 'double'>",
            "<class 'decimal'>"
        ],
        "correct_index": 1,
        "hint_1": "Numbers containing decimal points are floating-point numbers.",
        "hint_2": "Python does not have a separate 'double' primitive type; decimal numbers are floats.",
        "explanation": "In Python, real numbers with a decimal fraction are instances of `<class 'float'>`."
    },
    {
        "id": "py_8",
        "topic": "python",
        "difficulty": "easy",
        "question": "Which built-in function returns the total count of items in a sequence or collection?",
        "options": [
            "count()",
            "size()",
            "len()",
            "length()"
        ],
        "correct_index": 2,
        "hint_1": "It is a standard 3-letter built-in function.",
        "hint_2": "`len(['a', 'b', 'c'])` evaluates to 3.",
        "explanation": "The built-in `len()` function calls the `__len__()` method of an object to return its item count in O(1) time."
    },
    {
        "id": "py_9",
        "topic": "python",
        "difficulty": "medium",
        "question": "What is the result of evaluating: `' '.join(['Python', 'is', 'awesome'])`?",
        "options": [
            "['Python', 'is', 'awesome']",
            "'Python is awesome'",
            "'Python, is, awesome'",
            "'Pythonisawesome'"
        ],
        "correct_index": 1,
        "hint_1": "The string on which `.join()` is invoked serves as the delimiter placed between each token.",
        "hint_2": "Here, the separator is a single space `' '`.",
        "explanation": "`str.join(iterable)` concatenates string elements of an iterable into a single string separated by the delimiter string."
    },
    {
        "id": "py_10",
        "topic": "python",
        "difficulty": "medium",
        "question": "What is the primary role of `*args` in a Python function definition `def process(*args):`?",
        "options": [
            "It requires arguments to be passed as keyword arguments only.",
            "It allows the function to accept an arbitrary number of positional arguments collected into a tuple.",
            "It automatically casts all arguments into integer values.",
            "It runs the function concurrently across multiple CPU threads."
        ],
        "correct_index": 1,
        "hint_1": "The single asterisk collects extra positional parameters.",
        "hint_2": "Inside the function, `args` behaves as a tuple containing all passed positional arguments.",
        "explanation": "`*args` allows a function to accept any number of positional arguments, which are packed into a tuple named `args`."
    },
    {
        "id": "py_11",
        "topic": "python",
        "difficulty": "medium",
        "question": "In Python, what is the value of the boolean expression: `bool([]) or bool([0])`?",
        "options": [
            "False",
            "True",
            "None",
            "Raises a TypeError"
        ],
        "correct_index": 1,
        "hint_1": "An empty list `[]` evaluates to False in a boolean context.",
        "hint_2": "A list containing elements—even `[0]`—is non-empty and evaluates to True. `False or True` is True.",
        "explanation": "Empty collections (`[]`, `\"\"`, `{}`) are falsy (`bool([]) == False`). Any non-empty container (`[0]`) has length > 0 and is truthy. Thus `False or True` evaluates to `True`."
    },
    {
        "id": "py_12",
        "topic": "python",
        "difficulty": "hard",
        "question": "What is the fundamental architectural difference between a Python generator (using `yield`) and a standard function (using `return`)?",
        "options": [
            "Generators execute on a separate background thread automatically.",
            "Generators yield values lazily one at a time on demand, retaining execution state in memory without allocating the full list in RAM.",
            "Generators can only compute numeric integer sequences.",
            "Standard functions cannot accept mutable parameters, while generators can."
        ],
        "correct_index": 1,
        "hint_1": "Generators adhere to Python's iterator protocol (`__iter__` and `__next__`).",
        "hint_2": "A generator pauses at `yield` and resumes exactly where it stopped on the next call to `next()`.",
        "explanation": "A generator function uses `yield` to return a generator iterator. It produces values lazily as requested, maintaining state between yields and drastically reducing RAM consumption compared to building entire lists in memory."
    },
    {
        "id": "py_13",
        "topic": "python",
        "difficulty": "hard",
        "question": "What unexpected behavior occurs when defining a function with a default mutable argument like `def append_item(val, items=[])`?",
        "options": [
            "Python raises a `SyntaxError` at compile time.",
            "The default list `items` is created once when the function is defined and shared across all future calls that omit the argument.",
            "Python creates a fresh new list in RAM on every invocation.",
            "The list is automatically converted to an immutable tuple."
        ],
        "correct_index": 1,
        "hint_1": "Python evaluates default argument expressions only once, when the `def` statement is executed.",
        "hint_2": "If you mutate `items`, those mutations persist across subsequent calls where `items` is omitted.",
        "explanation": "Default parameter values in Python are evaluated once at function definition time, not at invocation time. Mutating a default list mutates the single shared instance across calls. The standard idiom is `def fn(val, items=None): if items is None: items = []`."
    },
    {
        "id": "py_14",
        "topic": "python",
        "difficulty": "hard",
        "question": "Which algorithm does Python 3 use to compute the Method Resolution Order (MRO) in complex multiple inheritance hierarchies?",
        "options": [
            "Depth-First Search with backtracking",
            "C3 Linearization algorithm",
            "Dijkstra's Shortest Path",
            "Breadth-First Topological Sweep"
        ],
        "correct_index": 1,
        "hint_1": "This algorithm guarantees monotonicity and respects the local precedence order of base classes.",
        "hint_2": "You can inspect the result of this order on any class via `ClassName.__mro__`.",
        "explanation": "Python employs the C3 Linearization algorithm to calculate the Method Resolution Order (MRO), guaranteeing that parent classes appear after their children and preserving declared inheritance order."
    },
    {
        "id": "py_15",
        "topic": "python",
        "difficulty": "hard",
        "question": "What is the primary purpose of using the `@functools.wraps(fn)` decorator when writing custom function decorators in Python?",
        "options": [
            "It compiles the decorated function into machine code for faster execution.",
            "It preserves the original function's introspection metadata, such as `__name__`, `__doc__`, and `__module__`.",
            "It guarantees that the wrapped function can never raise an unhandled exception.",
            "It converts synchronous functions into asynchronous co-routines."
        ],
        "correct_index": 1,
        "hint_1": "Without `@wraps`, inspecting `func.__name__` would return `'wrapper'` instead of the original function's name.",
        "hint_2": "It copies docstrings and parameter signatures to keep debugging and documentation tools accurate.",
        "explanation": "`@functools.wraps` copies metadata attributes (`__name__`, `__doc__`, `__annotations__`) from the original function to the inner wrapper function, preventing loss of function identity."
    },

    # ================= AI / ML QUESTIONS =================
    {
        "id": "ai_1",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "In a medical diagnosis model, which metric represents the proportion of true sick patients correctly identified out of ALL people who were actually sick?",
        "options": [
            "Precision",
            "Recall (Sensitivity)",
            "Accuracy",
            "Specificity"
        ],
        "correct_index": 1,
        "hint_1": "Formula: TP / (TP + FN). It measures how well the model avoids missing real positive cases.",
        "hint_2": "Precision is TP / (TP + FP); Recall is TP / (TP + FN).",
        "explanation": "Recall (Sensitivity) = True Positives / (True Positives + False Negatives). It quantifies the model's ability to locate all actual positive instances."
    },
    {
        "id": "ai_2",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "What type of machine learning problem is it when the training dataset contains both input features and corresponding ground-truth target labels?",
        "options": [
            "Unsupervised Learning",
            "Supervised Learning",
            "Reinforcement Learning",
            "Self-Supervised Clustering"
        ],
        "correct_index": 1,
        "hint_1": "The model has a 'teacher' providing the correct target answer for each training example.",
        "hint_2": "Examples include regression (predicting continuous price) and classification (predicting discrete class).",
        "explanation": "Supervised Learning models learn a mapping function from input features X to known output labels Y."
    },
    {
        "id": "ai_3",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "Why is TF-IDF (Term Frequency-Inverse Document Frequency) advantageous over raw word counts (Bag-of-Words)?",
        "options": [
            "It automatically parses grammatical sentence structure.",
            "It penalizes ubiquitous words (like 'the', 'is') and rewards discriminative domain-specific terms.",
            "It creates continuous dense word embeddings similar to Word2Vec.",
            "It reduces the feature space dimensionality to exactly 10 dimensions."
        ],
        "correct_index": 1,
        "hint_1": "Common words appear across almost every document and provide very little informative value for topic classification.",
        "hint_2": "The IDF component takes the logarithm of total documents divided by documents containing the term.",
        "explanation": "TF measures how frequently a term appears in a document, while IDF heavily attenuates terms that appear across almost all documents. This gives high weight to words that are uniquely characteristic of specific categories."
    },
    {
        "id": "ai_4",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "What is the primary danger when a machine learning model achieves 99.8% training accuracy but only 52.0% validation accuracy?",
        "options": [
            "Underfitting due to excessive regularization",
            "Overfitting: the model memorized training noise rather than generalizable patterns",
            "High bias and low variance",
            "The learning rate was too small"
        ],
        "correct_index": 1,
        "hint_1": "The model performs almost perfectly on seen data, but fails miserably on unseen data.",
        "hint_2": "This is a classic symptom of high variance, also known as overfitting.",
        "explanation": "A large divergence between training performance and validation performance indicates overfitting: the model learned idiosyncratic noise rather than genuine underlying patterns."
    },
    {
        "id": "ai_5",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "When training a model with significant class imbalance (e.g., 95% Class A and 5% Class B), why is raw Accuracy a misleading metric?",
        "options": [
            "Because Accuracy cannot be computed when classes have different sizes.",
            "A dummy model that predicts Class A 100% of the time achieves 95% accuracy while completely failing on Class B.",
            "Accuracy causes the gradient descent optimizer to diverge.",
            "Accuracy is mathematically only defined for linear regression."
        ],
        "correct_index": 1,
        "hint_1": "Consider what happens if a fraud detection model always says 'Not Fraud'.",
        "hint_2": "The majority class dominates the calculation: (TP + TN) / Total. Use F1-Score or PR-AUC instead.",
        "explanation": "In an imbalanced dataset, a naive classifier predicting the majority class exclusively will yield high accuracy (e.g. 95%), despite having zero utility for detecting the critical minority class. F1-Score or Balanced Accuracy is preferred."
    },
    {
        "id": "ai_6",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "Which machine learning algorithm finds a hyperplane that maximizes the geometric margin between two distinct classes?",
        "options": [
            "Linear Regression",
            "Support Vector Machine (SVM)",
            "K-Means Clustering",
            "Principal Component Analysis (PCA)"
        ],
        "correct_index": 1,
        "hint_1": "It focuses on support vectors that lie closest to the decision boundary.",
        "hint_2": "The optimal separating boundary is defined by the maximum margin.",
        "explanation": "A Support Vector Machine (SVM) finds the optimal hyperplane that maximizes the geometric distance (margin) between the nearest data points (support vectors) of competing classes."
    },
    {
        "id": "ai_7",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "What is the output range of the Sigmoid activation function: σ(z) = 1 / (1 + e^(-z))?",
        "options": [
            "[-1, 1]",
            "[0, 1]",
            "[-∞, +∞]",
            "[0, +∞]"
        ],
        "correct_index": 1,
        "hint_1": "It squashes real numbers into values that can be interpreted as probabilities.",
        "hint_2": "As z approaches positive infinity it approaches 1; as z approaches negative infinity it approaches 0.",
        "explanation": "The Sigmoid activation function squashes any real-valued input into the open interval (0, 1), making it ideal for modeling output probabilities in binary classification."
    },
    {
        "id": "ai_8",
        "topic": "ai_ml",
        "difficulty": "easy",
        "question": "In K-Fold Cross-Validation with K = 5, what percentage of the dataset is used for validation in each fold?",
        "options": [
            "10%",
            "20%",
            "50%",
            "80%"
        ],
        "correct_index": 1,
        "hint_1": "The dataset is partitioned into 5 equal subsets: 4 for training and 1 for testing in each iteration.",
        "hint_2": "1 / 5 = 0.20.",
        "explanation": "In 5-fold cross-validation, the dataset is split into 5 equal partitions. In each iteration, 4 folds (80%) are used for training and 1 fold (20%) serves as the validation set."
    },
    {
        "id": "ai_9",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "Which regularization technique adds a penalty proportional to the SQUARE of the magnitude of weight coefficients (λ Σ w_i²)?",
        "options": [
            "L1 Regularization (Lasso)",
            "L2 Regularization (Ridge)",
            "Dropout Regularization",
            "Early Stopping"
        ],
        "correct_index": 1,
        "hint_1": "L1 adds the absolute sum |w|; L2 adds the squared sum w².",
        "hint_2": "L2 shrinks weights toward zero without forcing them to be exactly zero, preserving all features.",
        "explanation": "L2 Regularization (Ridge Regression) adds the sum of squared weights to the loss function, penalizing large weights and preventing multicollinearity."
    },
    {
        "id": "ai_10",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "What critical issue does the Vanishing Gradient problem cause in deep neural networks during backpropagation?",
        "options": [
            "Gradients grow exponentially, causing numerical overflow and NaN weights.",
            "Gradients diminish exponentially as they propagate backward through layers, preventing early layers from updating their weights.",
            "The loss function becomes non-differentiable.",
            "The network stops accepting floating-point inputs."
        ],
        "correct_index": 1,
        "hint_1": "Activation functions like Sigmoid have derivatives ≤ 0.25. Multiplying fractions through many layers approaches zero.",
        "hint_2": "ReLU was widely adopted specifically to alleviate this problem.",
        "explanation": "In deep networks using saturating activations (like Sigmoid or Tanh), repeated chain-rule multiplication of small derivatives causes gradients to shrink exponentially toward zero, preventing early layers from learning."
    },
    {
        "id": "ai_11",
        "topic": "ai_ml",
        "difficulty": "medium",
        "question": "Why does a Random Forest ensemble generally achieve lower variance compared to a single individual Decision Tree?",
        "options": [
            "It uses deeper individual trees with more leaf nodes.",
            "It averages predictions across an ensemble of decorrelated trees trained on bootstrap samples with random feature subsets (Bagging).",
            "It converts non-linear relationships into linear regression lines.",
            "It eliminates all outliers from the training set before fitting."
        ],
        "correct_index": 1,
        "hint_1": "Bagging (Bootstrap Aggregation) + random feature subspace reduces correlation between individual estimators.",
        "hint_2": "Averaging M independent estimators with variance σ² reduces variance to σ² / M.",
        "explanation": "Random Forest combines bootstrap aggregation (bagging) with random feature selection at each split. Averaging the predictions of diverse, decorrelated trees significantly reduces overall model variance without increasing bias."
    },
    {
        "id": "ai_12",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "What is the primary architectural purpose of Batch Normalization in deep neural networks?",
        "options": [
            "To replace gradient descent with closed-form matrix inversion.",
            "To normalize layer inputs across each mini-batch, stabilizing activation distributions and smoothing the loss optimization landscape.",
            "To force all weights in the network to remain strictly non-negative.",
            "To eliminate the need for any activation functions between linear layers."
        ],
        "correct_index": 1,
        "hint_1": "It normalizes activations by subtracting batch mean and dividing by batch standard deviation, then applies learned scale and shift parameters (γ, β).",
        "hint_2": "It enables faster convergence and allows the use of much higher learning rates.",
        "explanation": "Batch Normalization normalizes layer inputs across each mini-batch, stabilizing activation distributions and smoothing the loss landscape. This enables faster convergence, higher learning rates, and reduces sensitivity to weight initialization."
    },
    {
        "id": "ai_13",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "In the standard Transformer architecture, what is the computational and memory complexity of the Scaled Dot-Product Self-Attention mechanism with respect to sequence length N?",
        "options": [
            "O(N)",
            "O(N log N)",
            "O(N²)",
            "O(2^N)"
        ],
        "correct_index": 2,
        "hint_1": "Every token in the sequence computes an attention score with every other token in the sequence.",
        "hint_2": "Multiplying the Query matrix (N x d) by the transposed Key matrix (d x N) produces an (N x N) attention weight matrix.",
        "explanation": "Scaled Dot-Product Attention calculates QK^T, resulting in an N x N attention weight matrix for a sequence of length N. This incurs O(N²) time and memory complexity."
    },
    {
        "id": "ai_14",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "Why is Data Leakage during feature scaling or preprocessing a critical flaw in an ML evaluation pipeline?",
        "options": [
            "It makes the training dataset consume more hard drive space.",
            "Information from the test set leaks into the training pipeline (e.g. fitting a Scaler on the full dataset before splitting), yielding deceptively optimistic evaluation metrics.",
            "It forces the model to use categorical variables instead of continuous numbers.",
            "It causes database deadlocks during multi-threaded training."
        ],
        "correct_index": 1,
        "hint_1": "If you call scaler.fit() on the entire dataset before splitting, test distribution statistics influence the training process.",
        "hint_2": "Always fit scalers and encoders ONLY on training data, then apply .transform() on validation/test data.",
        "explanation": "Data leakage occurs when information outside the training dataset is inadvertently used to create the model. Fitting transformations on the full dataset before splitting leaks distribution knowledge from the evaluation split, masking real-world generalization failure."
    },
    {
        "id": "ai_15",
        "topic": "ai_ml",
        "difficulty": "hard",
        "question": "What is the primary advantage of Cross-Entropy Loss over Mean Squared Error (MSE) when training neural network classifiers with Softmax output?",
        "options": [
            "MSE produces steeper gradients when the model is confidently wrong, whereas Cross-Entropy causes vanishing gradients.",
            "Cross-Entropy heavily penalizes confident incorrect predictions and produces linear error gradients (ŷ - y) that prevent gradient saturation.",
            "Cross-Entropy can only be computed if the number of classes is strictly 2.",
            "MSE cannot be differentiated with respect to weights."
        ],
        "correct_index": 1,
        "hint_1": "Cross-Entropy is -Σ y_i log(ŷ_i).",
        "hint_2": "Coupled with Softmax, the derivative simplifies cleanly to (ŷ_i - y_i), ensuring steady gradient flow even when the network starts far from optimal.",
        "explanation": "Cross-Entropy loss coupled with Softmax provides linear gradient updates (ŷ - y) that don't saturate when predictions are wrong, penalizing confident wrong predictions exponentially. MSE in classification produces small gradients near extreme probabilities, slowing learning."
    },

    # ================= DATA STRUCTURES QUESTIONS =================
    {
        "id": "dsa_1",
        "topic": "dsa",
        "difficulty": "easy",
        "question": "Which data structure enforces a Last-In, First-Out (LIFO) order of operations?",
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
        "difficulty": "easy",
        "question": "What is the time complexity of accessing an element in an array by its index (e.g., `arr[4]`)?",
        "options": [
            "O(1) - Constant Time",
            "O(N) - Linear Time",
            "O(log N) - Logarithmic Time",
            "O(N^2) - Quadratic Time"
        ],
        "correct_index": 0,
        "hint_1": "Array elements are stored in contiguous memory blocks. The address is calculated using a single arithmetic formula.",
        "hint_2": "No looping or traversal is required.",
        "explanation": "Because array memory is contiguous, access by index is direct arithmetic `base_address + index * item_size`, executing in O(1) constant time."
    },
    {
        "id": "dsa_3",
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
        "explanation": "In a balanced BST, tree height is bounded by O(log N). At each node comparison, one branch is discarded, yielding O(log N) search complexity."
    },
    {
        "id": "dsa_4",
        "topic": "dsa",
        "difficulty": "medium",
        "question": "Which data structure is most naturally suited to implement Breadth-First Search (BFS) graph traversal?",
        "options": [
            "Stack",
            "Queue (FIFO)",
            "Min-Heap",
            "Disjoint Set"
        ],
        "correct_index": 1,
        "hint_1": "BFS visits vertices level by level in the order they were first discovered.",
        "hint_2": "First discovered vertices must be explored first (First-In, First-Out).",
        "explanation": "BFS requires exploring neighboring nodes in FIFO order of discovery, which is implemented using a Queue."
    },
    {
        "id": "dsa_5",
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
    },
    {
        "id": "dsa_6",
        "topic": "dsa",
        "difficulty": "easy",
        "question": "Which of the following operations on a Singly Linked List has an O(1) constant time complexity (assuming a head pointer is maintained)?",
        "options": [
            "Searching for a specific element by value",
            "Inserting a new node at the head (beginning)",
            "Accessing the element at index K",
            "Deleting the tail node without a tail pointer"
        ],
        "correct_index": 1,
        "hint_1": "You only need to update the new node's next pointer to point to the current head, and reassign head.",
        "hint_2": "No traversal through the list is needed.",
        "explanation": "Inserting at the head of a singly linked list requires creating the node, setting `new_node.next = head`, and `head = new_node`, executing in strictly O(1) constant time."
    },
    {
        "id": "dsa_7",
        "topic": "dsa",
        "difficulty": "easy",
        "question": "What is the mandatory prerequisite condition required to execute Binary Search on an array?",
        "options": [
            "The array elements must all be positive numbers.",
            "The array must be sorted in ascending or descending order.",
            "The array length must be an exact power of 2.",
            "The array must be implemented as a doubly linked list."
        ],
        "correct_index": 1,
        "hint_1": "To determine whether to search left or right, elements must adhere to monotonic order.",
        "hint_2": "Comparing the target against the middle element only eliminates half the remaining elements if the array is sorted.",
        "explanation": "Binary Search relies on sorted order so that comparison with the median element deterministically rules out half of the search range at each step."
    },
    {
        "id": "dsa_8",
        "topic": "dsa",
        "difficulty": "easy",
        "question": "In a binary min-heap containing N distinct elements, where is the smallest element guaranteed to reside?",
        "options": [
            "At the rightmost leaf node",
            "At the root node",
            "At the leftmost leaf node",
            "Anywhere in the lowest tree level"
        ],
        "correct_index": 1,
        "hint_1": "By definition of the min-heap invariant, every parent node is less than or equal to its children.",
        "hint_2": "Accessing the minimum element (`heap[0]`) is strictly an O(1) operation.",
        "explanation": "The min-heap property ensures each parent node is smaller than or equal to its child nodes. Consequently, the minimum element always resides at the root."
    },
    {
        "id": "dsa_9",
        "topic": "dsa",
        "difficulty": "medium",
        "question": "Which mechanism is used in Hash Tables to handle instances where two distinct keys hash to the exact same bucket index?",
        "options": [
            "Binary search partitioning",
            "Collision resolution (e.g. Separate Chaining or Open Addressing)",
            "Dynamic programming memoization",
            "Tail-call recursion"
        ],
        "correct_index": 1,
        "hint_1": "When two distinct keys produce the same hash code modulo array size, a collision occurs.",
        "hint_2": "Separate chaining stores collisions in linked lists; open addressing probes adjacent slots.",
        "explanation": "Hash collisions are resolved via collision resolution techniques, primarily Separate Chaining (storing colliding items in linked lists or balanced trees at the bucket) or Open Addressing (probing using linear, quadratic, or double hashing)."
    },
    {
        "id": "dsa_10",
        "topic": "dsa",
        "difficulty": "medium",
        "question": "What is the worst-case time complexity of inserting N already-sorted elements into an initially empty, unbalanced Binary Search Tree (BST)?",
        "options": [
            "O(N)",
            "O(N log N)",
            "O(N²)",
            "O(log N)"
        ],
        "correct_index": 2,
        "hint_1": "Inserting sorted elements into an unbalanced BST degenerates the tree into a skewed single-branch linked list.",
        "hint_2": "The 1st insertion takes 1 step, 2nd takes 2 steps ... N-th takes N steps: 1 + 2 + ... + N = O(N²).",
        "explanation": "When keys are inserted in sorted order into an unbalanced BST, each new node becomes the right child of the previous node. The tree degrades into a linked list of depth N, yielding O(N²) cumulative insertion time."
    },
    {
        "id": "dsa_11",
        "topic": "dsa",
        "difficulty": "medium",
        "question": "Which algorithmic design paradigm does Dijkstra's Single-Source Shortest Path algorithm on non-negative weighted graphs employ?",
        "options": [
            "Divide and Conquer",
            "Greedy Algorithm",
            "Genetic Search",
            "Dynamic Programming with Tabulation"
        ],
        "correct_index": 1,
        "hint_1": "At each step, it extracts the unvisited vertex with the minimum tentative distance from a priority queue.",
        "hint_2": "It makes the locally optimal choice at each step without backtracking.",
        "explanation": "Dijkstra's algorithm is a greedy algorithm: at each iteration, it permanently finalizes the shortest distance to the unvisited vertex with the minimum tentative distance from the source."
    },
    {
        "id": "dsa_12",
        "topic": "dsa",
        "difficulty": "hard",
        "question": "Why does Dijkstra's algorithm fail to guarantee correct shortest paths on graphs with NEGATIVE edge weights?",
        "options": [
            "It triggers a stack overflow exception on the priority queue.",
            "Dijkstra greedily marks nodes as permanently visited assuming paths can never become shorter; a negative edge discovered later can invalidate this assumption.",
            "Dijkstra is only mathematically defined on bipartite graphs.",
            "Negative weights make all shortest paths infinite."
        ],
        "correct_index": 1,
        "hint_1": "Once a vertex is marked visited in Dijkstra, its distance is finalized and never re-evaluated.",
        "hint_2": "Use Bellman-Ford or Floyd-Warshall when negative edge weights are present.",
        "explanation": "Dijkstra's greedy choice assumes non-negative weights: once a node is finalized, no future path can be shorter. A negative edge can provide a detour with a smaller total distance after a node has been marked visited, producing wrong results. Bellman-Ford handles this by relaxing all edges V-1 times."
    },
    {
        "id": "dsa_13",
        "topic": "dsa",
        "difficulty": "hard",
        "question": "In algorithm design, what two fundamental properties MUST an optimization problem possess for Dynamic Programming to be applicable?",
        "options": [
            "Linearity and Asymptotic Sparsity",
            "Optimal Substructure and Overlapping Subproblems",
            "Greedy Choice Property and Monotonicity",
            "Commutativity and Idempotence"
        ],
        "correct_index": 1,
        "hint_1": "An optimal solution to the problem can be constructed from optimal solutions to subproblems.",
        "hint_2": "The recursive formulation revisits the identical subproblems repeatedly, making memoization or tabulation beneficial.",
        "explanation": "Dynamic Programming requires: 1) Optimal Substructure (an optimal solution contains optimal solutions to subproblems) and 2) Overlapping Subproblems (the recursive algorithm encounters the exact same subproblems repeatedly rather than generating new subproblems)."
    },
    {
        "id": "dsa_14",
        "topic": "dsa",
        "difficulty": "hard",
        "question": "What is the amortized time complexity per operation in Disjoint Set Union (DSU) when utilizing both Path Compression and Union by Rank heuristics?",
        "options": [
            "O(1) strictly",
            "O(α(N)), where α is the inverse Ackermann function",
            "O(log N)",
            "O(N)"
        ],
        "correct_index": 1,
        "hint_1": "The inverse Ackermann function α(N) grows so slowly that α(N) ≤ 4 for any practical N ≤ 10^600.",
        "hint_2": "Path compression flattens tree structure, and union by rank keeps tree height logarithmic.",
        "explanation": "With both Union by Rank and Path Compression heuristics, the amortized time per operation in DSU is O(α(N)), where α is the inverse Ackermann function, effectively constant time in all physical computing applications."
    },
    {
        "id": "dsa_15",
        "topic": "dsa",
        "difficulty": "hard",
        "question": "Which algorithm can detect whether a directed graph contains a cycle in O(V + E) linear time?",
        "options": [
            "Prim's Minimum Spanning Tree algorithm",
            "Depth-First Search (DFS) tracking nodes currently in the recursion stack (Three-Color Marking)",
            "Kruskal's algorithm with priority queues",
            "Binary Indexed Tree traversal"
        ],
        "correct_index": 1,
        "hint_1": "A cycle in a directed graph exists if and only if a back-edge to an ancestor currently active in the recursion call stack is detected.",
        "hint_2": "Nodes are classified into 3 states: Unvisited (White), In-Progress (Gray), and Completed (Black).",
        "explanation": "In a directed graph, a cycle exists if and only if DFS encounters a back-edge pointing to a node currently active in the recursion stack (Gray node). This runs in O(V + E) time."
    }
]

# Topic Expansion Pools: Additional questions dynamically registered into QUESTION_BANK
# if a learner exhausts all existing questions in a topic before any question is reused.
TOPIC_EXPANSION_POOLS = {
    "python": [
        {
            "id": "py_16",
            "topic": "python",
            "difficulty": "easy",
            "question": "Which keyword is used to create an anonymous inline function in Python?",
            "options": [
                "def",
                "lambda",
                "func",
                "inline"
            ],
            "correct_index": 1,
            "hint_1": "It takes any number of arguments but can only contain a single expression.",
            "hint_2": "Example: `add = lambda x, y: x + y`.",
            "explanation": "The `lambda` keyword defines small, anonymous inline functions in Python without binding them to a name via `def`."
        },
        {
            "id": "py_17",
            "topic": "python",
            "difficulty": "medium",
            "question": "What is the primary function of the `pass` statement in Python?",
            "options": [
                "It immediately terminates the enclosing loop.",
                "It serves as a syntactic null placeholder where a code statement is required but no action is needed.",
                "It skips to the next iteration of a loop.",
                "It clears the local variable namespace."
            ],
            "correct_index": 1,
            "hint_1": "Unlike `break` or `continue`, `pass` performs no control flow jump.",
            "hint_2": "It is used in empty class or function stubs to satisfy indentation syntax.",
            "explanation": "`pass` is a null operation in Python; nothing happens when it executes. It serves as a placeholder where code is syntactically required."
        },
        {
            "id": "py_18",
            "topic": "python",
            "difficulty": "hard",
            "question": "What is the primary purpose of defining `__slots__` inside a Python class definition?",
            "options": [
                "To enable automatic garbage collection.",
                "To restrict valid instance attributes to a fixed tuple, eliminating the per-instance `__dict__` and significantly saving RAM.",
                "To automatically generate getter and setter properties.",
                "To enforce abstract class interface implementation."
            ],
            "correct_index": 1,
            "hint_1": "By default, every Python instance stores attributes in a dynamic dictionary `__dict__` which has memory overhead.",
            "hint_2": "When millions of instances are created, `__slots__` provides massive memory optimization.",
            "explanation": "Defining `__slots__` reserves space for a declared set of attributes and prevents the creation of `__dict__` and `__weakref__` for each instance, providing substantial memory savings when instantiating large numbers of objects."
        }
    ],
    "ai_ml": [
        {
            "id": "ai_16",
            "topic": "ai_ml",
            "difficulty": "easy",
            "question": "Which classification metric is defined as the ratio of True Positives to all Positive Predictions (TP / (TP + FP))?",
            "options": [
                "Recall",
                "Precision",
                "Accuracy",
                "Specificity"
            ],
            "correct_index": 1,
            "hint_1": "It measures how many of the positively predicted instances were actually correct.",
            "hint_2": "Precision answers: 'When the model predicts positive, how often is it right?'",
            "explanation": "Precision = True Positives / (True Positives + False Positives). It quantifies the reliability of positive classifications."
        },
        {
            "id": "ai_17",
            "topic": "ai_ml",
            "difficulty": "medium",
            "question": "In K-Means clustering, what is the primary role of the Elbow Method?",
            "options": [
                "To calculate gradient descent step sizes automatically.",
                "To help identify the optimal number of clusters K by locating the point where inertia decrease slows noticeably.",
                "To eliminate outlier data points before clustering.",
                "To guarantee global convergence of centroid assignments."
            ],
            "correct_index": 1,
            "hint_1": "It plots within-cluster sum of squares (inertia) against candidate values of K.",
            "hint_2": "The bend or 'elbow' in the curve indicates diminishing returns for adding more clusters.",
            "explanation": "The Elbow Method plots within-cluster sum of squared errors (inertia) versus K. The 'elbow' point indicates the value of K after which adding more clusters yields diminishing explanatory return."
        },
        {
            "id": "ai_18",
            "topic": "ai_ml",
            "difficulty": "hard",
            "question": "What is the primary architectural difference between Bagging and Boosting ensemble paradigms?",
            "options": [
                "Bagging can only be used with decision trees, whereas Boosting works with neural networks only.",
                "Bagging trains estimators independently in parallel to reduce variance; Boosting trains estimators sequentially, focusing each new learner on errors made by previous models to reduce bias.",
                "Bagging uses gradient descent, whereas Boosting uses closed-form inversion.",
                "There is no difference; they are synonymous terms."
            ],
            "correct_index": 1,
            "hint_1": "Bagging = Bootstrap Aggregation (e.g. Random Forest).",
            "hint_2": "Boosting = Sequential adaptive re-weighting of challenging training instances (e.g. XGBoost, AdaBoost).",
            "explanation": "Bagging fits independent base learners in parallel on bootstrap samples to reduce model variance. Boosting fits learners sequentially, with each subsequent model emphasizing training instances misclassified by earlier models, primarily reducing bias."
        }
    ],
    "dsa": [
        {
            "id": "dsa_16",
            "topic": "dsa",
            "difficulty": "easy",
            "question": "Which data structure follows a First-In, First-Out (FIFO) access order?",
            "options": [
                "Stack",
                "Queue",
                "Tree",
                "Heap"
            ],
            "correct_index": 1,
            "hint_1": "Think of people waiting in line at a movie theater ticket counter.",
            "hint_2": "The first person to join the queue is the first person served.",
            "explanation": "A Queue enforces First-In, First-Out (FIFO) order: items are inserted at the rear (enqueue) and removed from the front (dequeue)."
        },
        {
            "id": "dsa_17",
            "topic": "dsa",
            "difficulty": "medium",
            "question": "What is the worst-case time complexity of the Quickselect algorithm when searching for the k-th smallest element with consistently poor pivot choices?",
            "options": [
                "O(N)",
                "O(N²)",
                "O(N log N)",
                "O(1)"
            ],
            "correct_index": 1,
            "hint_1": "Average case is O(N), but if the pivot repeatedly splits into sizes 1 and N-1, what happens?",
            "hint_2": "N + (N-1) + (N-2) + ... = O(N²).",
            "explanation": "While Quickselect achieves O(N) average time complexity, consistently poor pivot choices (such as picking extreme elements on already-sorted arrays) yield O(N²) worst-case performance."
        },
        {
            "id": "dsa_18",
            "topic": "dsa",
            "difficulty": "hard",
            "question": "Which algorithm computes the Minimum Spanning Tree (MST) of a connected graph by greedily adding edges in increasing order of weight, using a Disjoint Set Union (DSU) to avoid cycles?",
            "options": [
                "Dijkstra's Algorithm",
                "Kruskal's Algorithm",
                "Floyd-Warshall Algorithm",
                "Bellman-Ford Algorithm"
            ],
            "correct_index": 1,
            "hint_1": "It sorts all edges by weight upfront, then uses Union-Find to verify if an edge creates a cycle.",
            "hint_2": "Prim's grows a tree from a vertex; Kruskal's adds edges globally.",
            "explanation": "Kruskal's algorithm sorts all edges by non-decreasing weight and greedily incorporates edges that do not form a cycle, using Disjoint Set Union (DSU) for cycle detection in O(E log E) time."
        }
    ]
}

def expand_topic_questions(topic_id):
    """
    Dynamically registers additional questions from the topic expansion pool
    into QUESTION_BANK when all current questions for a topic have been exhausted.
    Ensures learners do not silently receive repeated questions.
    """
    pool = TOPIC_EXPANSION_POOLS.get(topic_id, [])
    existing_ids = {q["id"] for q in QUESTION_BANK}
    added = []
    for q in pool:
        if q["id"] not in existing_ids:
            QUESTION_BANK.append(q)
            added.append(q["id"])
    return added

def get_questions_for_topic(topic_id):
    return [q for q in QUESTION_BANK if q["topic"] == topic_id]

def select_adaptive_question(topic_id, current_state, history_ids=None):
    """
    Selects the next question adaptively based on the learner's current cognitive state.
    - Confused: prefers 'easy' questions, unlocks scaffolded hints.
    - Stressed: prefers 'easy' / calming questions, triggers break recommendation.
    - Fatigued: prefers 'easy' / low-load questions.
    - Neutral: targets 'medium' standard questions.
    - Focused: progresses to 'medium' or 'hard' synthesis challenges.
    - Motivated: targets 'hard' mastery questions.

    Anti-Repetition & Randomization Rules:
    1. Filters out questions in history_ids (seen in current and prior sessions).
    2. If all questions in the topic bank are exhausted, automatically expands the question bank
       with fresh questions from the expansion pool BEFORE reusing old questions.
    3. Randomly selects among candidates matching the target difficulty.
    4. If no questions match the target difficulty, falls back to other difficulty tiers
       with unseen questions before recycling.
    5. Shuffles candidate choices to prevent deterministic presentation orders.
    """
    if history_ids is None:
        history_ids = []
    history_ids_set = set(history_ids)

    topic_qs = get_questions_for_topic(topic_id)
    if not topic_qs:
        topic_qs = QUESTION_BANK

    unseen_qs = [q for q in topic_qs if q["id"] not in history_ids_set]

    # If all existing questions for this topic have been exhausted:
    if not unseen_qs:
        # Step 1: Auto-expand question bank with new questions from pool before reusing old ones
        added = expand_topic_questions(topic_id)
        if added:
            topic_qs = get_questions_for_topic(topic_id)
            unseen_qs = [q for q in topic_qs if q["id"] not in history_ids_set]

    # If still exhausted after expansion (user completed all standard + expanded questions):
    # Gracefully cycle through the full bank, but randomize selection so questions don't repeat in static order
    if not unseen_qs:
        unseen_qs = list(topic_qs)

    # Dynamic target difficulty rule based on cognitive state
    if current_state in ("Confused", "Stressed", "Fatigued"):
        target_diff = "easy"
        fallback_diffs = ["medium", "hard"]
    elif current_state in ("Focused", "Motivated"):
        target_diff = "hard"
        fallback_diffs = ["medium", "easy"]
    else:  # Neutral and others
        target_diff = "medium"
        fallback_diffs = ["easy", "hard"]

    matched = [q for q in unseen_qs if q["difficulty"] == target_diff]
    if not matched:
        for diff in fallback_diffs:
            matched = [q for q in unseen_qs if q["difficulty"] == diff]
            if matched:
                target_diff = diff
                break

    if not matched:
        matched = unseen_qs
        target_diff = matched[0]["difficulty"]

    # Randomly select candidate from matched questions to ensure different order every session
    selected_question = random.choice(matched)
    return selected_question, target_diff

def get_adaptive_lesson(topic_id, state):
    """
    Retrieves state-adapted pedagogical learning material for the given topic and cognitive state.
    """
    topic_materials = LEARNING_MATERIALS.get(topic_id, LEARNING_MATERIALS["python"])
    lesson = topic_materials.get(state)
    if not lesson:
        # Fallback to Neutral or Focused
        lesson = topic_materials.get("Neutral", topic_materials.get("Focused"))
    return lesson

def get_adaptive_intervention(state, confidence=85.0):
    """
    Generates intelligent pedagogical and productivity interventions tailored to cognitive states.
    """
    interventions = {
        "Focused": {
            "badge_color": "success",
            "title": "Deep Work Flow Detected 🎯",
            "action_type": "maintain_flow",
            "difficulty_modifier": "+1 (Mastery Mode)",
            "message": "You are fully dialed into your learning material. We've queued higher-difficulty synthesis problems to maintain optimal challenge.",
            "study_tip": "Keep going! Work through this challenging problem before taking a structured break.",
            "show_break_modal": False,
            "show_scaffold_hints": False
        },
        "Motivated": {
            "badge_color": "info",
            "title": "High Energy & Drive 🚀",
            "action_type": "accelerate",
            "difficulty_modifier": "+1 (Bonus XP Mode)",
            "message": "Your enthusiasm is high! Capitalize on this energy by tackling challenging mastery questions and earning bonus XP.",
            "study_tip": "Push yourself to achieve 100% accuracy on this advanced challenge.",
            "show_break_modal": False,
            "show_scaffold_hints": False
        },
        "Confused": {
            "badge_color": "warning",
            "title": "Cognitive Obstacle Detected 💡",
            "action_type": "scaffold",
            "difficulty_modifier": "-1 (Foundational Scaffolding)",
            "message": "It looks like this concept needs clearer scaffolding. We've unlocked step-by-step hints and adjusted the question to an approachable difficulty.",
            "study_tip": "Inspect Hint 1 and Hint 2 to break down the concept into smaller, digestible steps.",
            "show_break_modal": False,
            "show_scaffold_hints": True
        },
        "Stressed": {
            "badge_color": "danger",
            "title": "High Cognitive Overload Alert 🌿",
            "action_type": "de_stress_break",
            "difficulty_modifier": "Paused / Gentle Pace",
            "message": "Your cognitive load is elevated. Research shows high anxiety impedes working memory. We strongly suggest a 2-minute calming breathing reset.",
            "study_tip": "Take a pause from the screen. Follow the guided 4-7-8 breathing exercise to reset your nervous system.",
            "show_break_modal": True,
            "show_scaffold_hints": True
        },
        "Fatigued": {
            "badge_color": "secondary",
            "title": "Mental Fatigue Alert 😴",
            "action_type": "rest_and_light_review",
            "difficulty_modifier": "Lightweight Micro-Task",
            "message": "Your energy and attention span are depleted. We've switched to a shorter, low-intensity micro-learning task to avoid burnout.",
            "study_tip": "Rest your eyes, hydrate, do a quick 2-minute shoulder stretch, and answer one quick review question.",
            "show_break_modal": False,
            "show_scaffold_hints": True
        },
        "Neutral": {
            "badge_color": "primary",
            "title": "Balanced Baseline State ⚖️",
            "action_type": "standard_progress",
            "difficulty_modifier": "Standard (Medium)",
            "message": "You are in a balanced, steady study state. Continuing with the standard learning curriculum and core questions.",
            "study_tip": "Maintain a steady pace and test your understanding of core concepts.",
            "show_break_modal": False,
            "show_scaffold_hints": False
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
    return interventions.get(state, interventions["Neutral"])
