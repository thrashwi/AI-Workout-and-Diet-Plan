import os
import math
import json
import random
from config import Config

# Safe import of data science packages
try:
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    import joblib
    HAS_ML = True
except ImportError:
    HAS_ML = False


# ==========================================
# 1. PHYSICAL & METABOLIC CALCULATIONS
# ==========================================

def calculate_bmi(weight_kg, height_cm):
    """Calculates BMI and returns value, category, color, and description."""
    if not height_cm or height_cm <= 0 or not weight_kg or weight_kg <= 0:
        return 0, "Unknown", "secondary", "Invalid measurements"

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        category = "Underweight"
        color = "info"
        description = "You are below the standard healthy weight range. A nutrient-dense, muscle-building nutrition plan is advised."
    elif 18.5 <= bmi <= 24.9:
        category = "Normal Weight"
        color = "success"
        description = "You have a healthy body weight. Maintain your fitness with balanced exercise and nutrition."
    elif 25.0 <= bmi <= 29.9:
        category = "Overweight"
        color = "warning"
        description = "You are slightly above the standard healthy weight range. A moderate caloric deficit and regular cardio/strength exercise will help."
    elif 30.0 <= bmi <= 34.9:
        category = "Obesity (Class I)"
        color = "danger"
        description = "Weight loss through structured physical activity and controlled calorie intake is strongly recommended."
    elif 35.0 <= bmi <= 39.9:
        category = "Obesity (Class II)"
        color = "danger"
        description = "High risk for cardiovascular health. Low-impact cardiovascular training and a structured diet plan are essential."
    else:
        category = "Obesity (Class III)"
        color = "dark"
        description = "Very high risk. Focus on gradual sustainable lifestyle modifications and low-impact workouts."

    return bmi, category, color, description


def calculate_ideal_weight_range(height_cm):
    """Calculates healthy weight range based on BMI 18.5 - 24.9."""
    if not height_cm or height_cm <= 0:
        return 50.0, 70.0
    height_m = height_cm / 100.0
    min_weight = round(18.5 * (height_m ** 2), 1)
    max_weight = round(24.9 * (height_m ** 2), 1)
    return min_weight, max_weight


def calculate_bmr(weight_kg, height_cm, age, gender="male"):
    """Calculates Basal Metabolic Rate using Mifflin-St Jeor equation."""
    if not weight_kg or not height_cm or not age:
        return 1600.0
    
    # Men: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) + 5
    # Women: 10 * weight(kg) + 6.25 * height(cm) - 5 * age(y) - 161
    if str(gender).lower() == "female":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    
    return round(max(bmr, 800), 0)


def calculate_tdee(bmr, activity_level="moderate"):
    """Calculates Total Daily Energy Expenditure."""
    multipliers = {
        "sedentary": 1.2,        # Desk job, little to no exercise
        "light": 1.375,          # Light exercise 1-2 days/week
        "moderate": 1.55,        # Moderate exercise 3-4 days/week
        "very_active": 1.725     # Hard exercise 5-7 days/week
    }
    multiplier = multipliers.get(str(activity_level).lower(), 1.5)
    return round(bmr * multiplier, 0)


def calculate_hydration(weight_kg, activity_level="moderate"):
    """Calculates recommended daily water intake in liters."""
    if not weight_kg or weight_kg <= 0:
        return 2.5
    base_liters = (weight_kg * 35) / 1000.0
    if activity_level in ("moderate", "very_active"):
        base_liters += 0.5
    return round(base_liters, 1)


# ==========================================
# 2. MACHINE LEARNING DATASET & MODEL PIPELINE
# ==========================================

GOALS = ["weight_loss", "weight_gain", "muscle_building", "general_fitness", "endurance"]
ACTIVITIES = ["sedentary", "light", "moderate", "very_active"]
FREQUENCIES = ["1-2", "3-4", "5-6", "daily"]

SPLIT_CLASSES = [
    "Full Body 3-Day Split",
    "Upper/Lower 4-Day Split",
    "Push/Pull/Legs 6-Day Split",
    "Fat-Loss HIIT & Cardio Circuit",
    "Endurance & Functional Conditioning"
]

INTENSITY_CLASSES = ["Low-Moderate", "Moderate", "Moderate-High", "High-Intensity"]

def generate_synthetic_fitness_data(num_samples=1200):
    """Generates synthetic dataset for training recommendation models."""
    data = []
    random.seed(42)

    for _ in range(num_samples):
        gender_code = random.choice([0, 1]) # 0 female, 1 male
        age = random.randint(18, 65)
        
        if gender_code == 1:
            height = random.randint(160, 195)
            weight = random.randint(55, 120)
        else:
            height = random.randint(148, 180)
            weight = random.randint(45, 105)
            
        height_m = height / 100.0
        bmi = round(weight / (height_m ** 2), 1)

        goal_idx = random.randint(0, len(GOALS) - 1)
        goal = GOALS[goal_idx]

        act_idx = random.randint(0, len(ACTIVITIES) - 1)
        act = ACTIVITIES[act_idx]

        freq_idx = random.randint(0, len(FREQUENCIES) - 1)
        freq = FREQUENCIES[freq_idx]

        # Target determinations
        if goal == "weight_loss":
            if freq_idx >= 2:
                split_idx = 3 # Fat-Loss HIIT
                intensity_idx = 2 # Moderate-High
            else:
                split_idx = 0 # Full Body 3-Day
                intensity_idx = 1 # Moderate
            caloric_adjustment = -20 # -20% deficit
            p_ratio, c_ratio, f_ratio = 35, 40, 25

        elif goal == "muscle_building":
            if freq_idx >= 2:
                split_idx = 2 # PPL 6-Day
                intensity_idx = 3 # High
            else:
                split_idx = 1 # Upper/Lower 4-Day
                intensity_idx = 2 # Moderate-High
            caloric_adjustment = +12 # +12% surplus
            p_ratio, c_ratio, f_ratio = 30, 45, 25

        elif goal == "weight_gain":
            split_idx = 1 if freq_idx >= 1 else 0
            intensity_idx = 1
            caloric_adjustment = +20 # +20% surplus
            p_ratio, c_ratio, f_ratio = 25, 55, 20

        elif goal == "endurance":
            split_idx = 4
            intensity_idx = 3
            caloric_adjustment = +5
            p_ratio, c_ratio, f_ratio = 20, 60, 20

        else: # general_fitness
            split_idx = 0 if freq_idx <= 1 else 1
            intensity_idx = 1
            caloric_adjustment = 0
            p_ratio, c_ratio, f_ratio = 25, 50, 25

        data.append({
            "age": age,
            "gender": gender_code,
            "height": height,
            "weight": weight,
            "bmi": bmi,
            "goal": goal_idx,
            "activity": act_idx,
            "frequency": freq_idx,
            "split_label": split_idx,
            "intensity_label": intensity_idx,
            "calorie_adj": caloric_adjustment,
            "p_ratio": p_ratio,
            "c_ratio": c_ratio,
            "f_ratio": f_ratio
        })

    return pd.DataFrame(data)


def train_or_load_models():
    """Trains or loads recommendation models."""
    if not HAS_ML:
        return None

    os.makedirs(Config.DATA_DIR, exist_ok=True)
    model_path = Config.MODEL_PATH

    if os.path.exists(model_path):
        try:
            bundle = joblib.load(model_path)
            return bundle
        except Exception:
            pass

    # Train models
    df = generate_synthetic_fitness_data()
    X = df[["age", "gender", "height", "weight", "bmi", "goal", "activity", "frequency"]]
    
    # Split classifier
    clf_split = RandomForestClassifier(n_estimators=50, random_state=42)
    clf_split.fit(X, df["split_label"])

    # Intensity classifier
    clf_intensity = RandomForestClassifier(n_estimators=50, random_state=42)
    clf_intensity.fit(X, df["intensity_label"])

    # Regressor for calorie adjustment and macro ratios
    reg_macros = RandomForestRegressor(n_estimators=50, random_state=42)
    reg_macros.fit(X, df[["calorie_adj", "p_ratio", "c_ratio", "f_ratio"]])

    bundle = {
        "clf_split": clf_split,
        "clf_intensity": clf_intensity,
        "reg_macros": reg_macros
    }

    try:
        joblib.dump(bundle, model_path)
    except Exception:
        pass

    return bundle


# Initialize models lazily
_MODELS = None

def get_models():
    global _MODELS
    if _MODELS is None and HAS_ML:
        _MODELS = train_or_load_models()
    return _MODELS


# ==========================================
# 3. AI WORKOUT RECOMMENDATION ENGINE
# ==========================================

EXERCISE_DATABASE = {
    "Chest": [
        {"name": "Barbell Bench Press", "sets": "4", "reps": "8-10", "rest": "90s", "cue": "Retract scapulae, touch mid-chest, drive up with explosive control.", "video_tag": "bench_press"},
        {"name": "Incline Dumbbell Press", "sets": "3", "reps": "10-12", "rest": "75s", "cue": "Set bench to 30-45 degrees; emphasize upper pectoral contraction.", "video_tag": "incline_press"},
        {"name": "Push-ups (Bodyweight / Weighted)", "sets": "3", "reps": "15-20", "rest": "60s", "cue": "Keep core tight, elbows tucked at 45 degrees.", "video_tag": "pushups"},
        {"name": "Cable Chest Flyes", "sets": "3", "reps": "12-15", "rest": "60s", "cue": "Hug a barrel motion, pause for 1 second peak contraction.", "video_tag": "chest_fly"}
    ],
    "Back": [
        {"name": "Barbell Deadlift", "sets": "4", "reps": "6-8", "rest": "120s", "cue": "Hips back, flat back, drive through heels into full lockout.", "video_tag": "deadlift"},
        {"name": "Pull-ups / Lat Pulldown", "sets": "4", "reps": "8-12", "rest": "90s", "cue": "Lead with elbows, pull chest to bar, controlled negative.", "video_tag": "pullups"},
        {"name": "Bent-over Barbell Row", "sets": "3", "reps": "8-10", "rest": "75s", "cue": "Torso at 45 degrees, pull barbell towards navel.", "video_tag": "barbell_row"},
        {"name": "Seated Cable Row", "sets": "3", "reps": "10-12", "rest": "60s", "cue": "Squeeze mid-traps and lats together at peak pull.", "video_tag": "cable_row"}
    ],
    "Legs": [
        {"name": "Barbell Back Squat", "sets": "4", "reps": "8-10", "rest": "120s", "cue": "Depth below parallel, knees tracking over toes, brace core.", "video_tag": "squats"},
        {"name": "Romanian Deadlift (RDL)", "sets": "3", "reps": "10-12", "rest": "90s", "cue": "Hinge at hips, keep soft bend in knees, feel hamstring stretch.", "video_tag": "rdl"},
        {"name": "Walking Dumbbell Lunges", "sets": "3", "reps": "12 per leg", "rest": "60s", "cue": "Long strides, upright posture, 90-degree bend in front knee.", "video_tag": "lunges"},
        {"name": "Leg Press & Calf Raises", "sets": "3", "reps": "15", "rest": "60s", "cue": "Smooth cadence, full dorsiflexion and plantar flexion.", "video_tag": "leg_press"}
    ],
    "Shoulders & Arms": [
        {"name": "Overhead Barbell Military Press", "sets": "4", "reps": "8-10", "rest": "90s", "cue": "Braced glutes and core, press directly overhead.", "video_tag": "overhead_press"},
        {"name": "Dumbbell Lateral Raises", "sets": "4", "reps": "12-15", "rest": "60s", "cue": "Lead with elbows, slight forward lean, control eccentric.", "video_tag": "lateral_raise"},
        {"name": "Barbell Bicep Curls", "sets": "3", "reps": "10-12", "rest": "60s", "cue": "Elbows pinned to sides, curl smoothly without swinging.", "video_tag": "bicep_curls"},
        {"name": "Triceps Rope Pushdowns", "sets": "3", "reps": "12-15", "rest": "60s", "cue": "Flare rope outward at bottom for full tricep contraction.", "video_tag": "tricep_pushdown"}
    ],
    "Core & Cardio": [
        {"name": "Plank with Shoulder Taps", "sets": "3", "reps": "45-60s", "rest": "45s", "cue": "Prevent hip swaying, maintain rigid spine and active abs.", "video_tag": "plank"},
        {"name": "Hanging Leg Raises", "sets": "3", "reps": "12-15", "rest": "60s", "cue": "Curl pelvis upwards, avoid relying only on hip flexors.", "video_tag": "leg_raises"},
        {"name": "HIIT Mountain Climbers & Burpees", "sets": "4", "reps": "30s on / 30s off", "rest": "60s", "cue": "High intensity bursts, maintain athletic cadence.", "video_tag": "burpees"},
        {"name": "Zone 2 Steady-State Cardio (Treadmill/Cycle)", "sets": "1", "reps": "25-35 mins", "rest": "N/A", "cue": "Keep heart rate in 65-75% max HR zone.", "video_tag": "cardio"}
    ]
}


def generate_ai_workout_plan(profile):
    """
    Generates a personalized 7-day workout plan based on user profile and ML recommendations.
    """
    if profile is not None:
        try:
            profile = dict(profile)
        except Exception:
            pass
    else:
        profile = {}

    goal = profile.get("fitness_goal") or "general_fitness"
    activity = profile.get("activity_level") or "moderate"
    frequency = profile.get("exercise_frequency") or "3-4"
    gender = profile.get("gender") or "male"
    age = profile.get("age") or 25
    weight = profile.get("weight_kg") or 70
    height = profile.get("height_cm") or 175
    bmi, _, _, _ = calculate_bmi(weight, height)

    goal_idx = GOALS.index(goal) if goal in GOALS else 3
    act_idx = ACTIVITIES.index(activity) if activity in ACTIVITIES else 2
    freq_idx = FREQUENCIES.index(frequency) if frequency in FREQUENCIES else 1
    gender_idx = 1 if gender == "male" else 0

    split_name = "Full Body 3-Day Split"
    intensity = "Moderate"

    models = get_models()
    if models is not None:
        try:
            X = [[age, gender_idx, height, weight, bmi, goal_idx, act_idx, freq_idx]]
            s_pred = models["clf_split"].predict(X)[0]
            i_pred = models["clf_intensity"].predict(X)[0]
            split_name = SPLIT_CLASSES[min(int(s_pred), len(SPLIT_CLASSES) - 1)]
            intensity = INTENSITY_CLASSES[min(int(i_pred), len(INTENSITY_CLASSES) - 1)]
        except Exception:
            pass

    # Build weekly schedule based on split type
    schedule = []
    
    if "Push/Pull/Legs" in split_name:
        days = [
            {"day": "Monday", "focus": "Push (Chest, Shoulders & Triceps)", "type": "Strength / Hypertrophy", "exercises": EXERCISE_DATABASE["Chest"][:3] + EXERCISE_DATABASE["Shoulders & Arms"][:2]},
            {"day": "Tuesday", "focus": "Pull (Back, Rear Delts & Biceps)", "type": "Strength / Hypertrophy", "exercises": EXERCISE_DATABASE["Back"][:3] + [EXERCISE_DATABASE["Shoulders & Arms"][2]]},
            {"day": "Wednesday", "focus": "Legs & Core Conditioning", "type": "Lower Body Power", "exercises": EXERCISE_DATABASE["Legs"][:3] + EXERCISE_DATABASE["Core & Cardio"][:2]},
            {"day": "Thursday", "focus": "Active Recovery & Mobility", "type": "Rest / Light Walking", "exercises": [EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Friday", "focus": "Push & Upper Body Hypertrophy", "type": "Volume Work", "exercises": EXERCISE_DATABASE["Chest"][1:] + [EXERCISE_DATABASE["Shoulders & Arms"][3]]},
            {"day": "Saturday", "focus": "Pull & Lower Body Finisher", "type": "Compound Athletic", "exercises": EXERCISE_DATABASE["Back"][1:] + [EXERCISE_DATABASE["Legs"][0], EXERCISE_DATABASE["Legs"][2]]},
            {"day": "Sunday", "focus": "Full Rest & Recovery", "type": "Rest Day", "exercises": []}
        ]
    elif "Upper/Lower" in split_name:
        days = [
            {"day": "Monday", "focus": "Upper Body Strength (Chest & Back)", "type": "Compound Strength", "exercises": [EXERCISE_DATABASE["Chest"][0], EXERCISE_DATABASE["Back"][1], EXERCISE_DATABASE["Shoulders & Arms"][0], EXERCISE_DATABASE["Chest"][2]]},
            {"day": "Tuesday", "focus": "Lower Body & Core (Squats & Hamstrings)", "type": "Lower Power", "exercises": [EXERCISE_DATABASE["Legs"][0], EXERCISE_DATABASE["Legs"][1], EXERCISE_DATABASE["Legs"][3], EXERCISE_DATABASE["Core & Cardio"][0]]},
            {"day": "Wednesday", "focus": "Active Recovery & Core Mobility", "type": "Cardio / Core", "exercises": [EXERCISE_DATABASE["Core & Cardio"][0], EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Thursday", "focus": "Upper Body Hypertrophy (Arms & Shoulders)", "type": "Hypertrophy Pump", "exercises": [EXERCISE_DATABASE["Chest"][1], EXERCISE_DATABASE["Back"][2], EXERCISE_DATABASE["Shoulders & Arms"][1], EXERCISE_DATABASE["Shoulders & Arms"][2]]},
            {"day": "Friday", "focus": "Lower Body Volume & Calves", "type": "Leg Sculpting", "exercises": [EXERCISE_DATABASE["Legs"][1], EXERCISE_DATABASE["Legs"][2], EXERCISE_DATABASE["Legs"][3], EXERCISE_DATABASE["Core & Cardio"][1]]},
            {"day": "Saturday", "focus": "HIIT Conditioning / Sport Activity", "type": "Cardiovascular Stamina", "exercises": [EXERCISE_DATABASE["Core & Cardio"][2], EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Sunday", "focus": "Rest & Muscle Repair", "type": "Rest Day", "exercises": []}
        ]
    elif "Fat-Loss" in split_name or goal == "weight_loss":
        days = [
            {"day": "Monday", "focus": "Full Body Metabolic Circuit A", "type": "High Calorie Burn", "exercises": [EXERCISE_DATABASE["Legs"][0], EXERCISE_DATABASE["Chest"][2], EXERCISE_DATABASE["Back"][1], EXERCISE_DATABASE["Core & Cardio"][2]]},
            {"day": "Tuesday", "focus": "HIIT Intervals & Core Stability", "type": "Cardio & Core", "exercises": [EXERCISE_DATABASE["Core & Cardio"][0], EXERCISE_DATABASE["Core & Cardio"][1], EXERCISE_DATABASE["Core & Cardio"][2], EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Wednesday", "focus": "Full Body Resistance Circuit B", "type": "Muscular Endurance", "exercises": [EXERCISE_DATABASE["Legs"][2], EXERCISE_DATABASE["Back"][2], EXERCISE_DATABASE["Shoulders & Arms"][0], EXERCISE_DATABASE["Core & Cardio"][0]]},
            {"day": "Thursday", "focus": "Low-Impact Active Recovery Walk", "type": "Zone 2 Fat Burn", "exercises": [EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Friday", "focus": "Full Body Dynamic Strength & Core", "type": "Tone & Sculpt", "exercises": [EXERCISE_DATABASE["Legs"][1], EXERCISE_DATABASE["Chest"][0], EXERCISE_DATABASE["Shoulders & Arms"][1], EXERCISE_DATABASE["Core & Cardio"][1]]},
            {"day": "Saturday", "focus": "Cardio Blast & Core Finisher", "type": "Metabolic Conditioning", "exercises": [EXERCISE_DATABASE["Core & Cardio"][2], EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Sunday", "focus": "Rest & Reset", "type": "Rest Day", "exercises": []}
        ]
    else: # Default 3-Day Full Body
        days = [
            {"day": "Monday", "focus": "Full Body Power (Squat & Press)", "type": "Compound Strength", "exercises": [EXERCISE_DATABASE["Legs"][0], EXERCISE_DATABASE["Chest"][0], EXERCISE_DATABASE["Back"][1], EXERCISE_DATABASE["Core & Cardio"][0]]},
            {"day": "Tuesday", "focus": "Active Recovery / 30-min Brisk Walk", "type": "Low Intensity Cardio", "exercises": [EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Wednesday", "focus": "Full Body Pull & Core (Hinge & Row)", "type": "Hypertrophy & Posture", "exercises": [EXERCISE_DATABASE["Back"][0], EXERCISE_DATABASE["Shoulders & Arms"][0], EXERCISE_DATABASE["Legs"][1], EXERCISE_DATABASE["Core & Cardio"][1]]},
            {"day": "Thursday", "focus": "Rest Day or Light Mobility", "type": "Mobility & Rest", "exercises": []},
            {"day": "Friday", "focus": "Full Body Athletic & Conditioning", "type": "Muscular Endurance", "exercises": [EXERCISE_DATABASE["Legs"][2], EXERCISE_DATABASE["Chest"][2], EXERCISE_DATABASE["Back"][2], EXERCISE_DATABASE["Shoulders & Arms"][1]]},
            {"day": "Saturday", "focus": "Outdoor Activity or Light Cardio", "type": "Aerobic Health", "exercises": [EXERCISE_DATABASE["Core & Cardio"][3]]},
            {"day": "Sunday", "focus": "Rest & Meal Preparation", "type": "Rest Day", "exercises": []}
        ]

    workout_plan = {
        "split_name": split_name,
        "intensity": intensity,
        "weekly_sessions": frequency,
        "warmup": "5-10 minutes dynamic stretching (arm circles, leg swings, hip openers, bodyweight air squats)",
        "cooldown": "5 minutes static stretching (chest doorway stretch, hamstring fold, child's pose)",
        "days": days
    }

    return workout_plan


# ==========================================
# 4. AI DIET RECOMMENDATION ENGINE
# ==========================================

MEAL_DATABASE = {
    "standard": {
        "breakfast": [
            {"name": "Oatmeal with Whey Protein, Berries & Almonds", "calories": 420, "p": 32, "c": 50, "f": 10, "tag": "protein_oatmeal"},
            {"name": "3 Whole Eggs Scrambled with Whole Grain Toast & Avocado", "calories": 460, "p": 24, "c": 35, "f": 22, "tag": "scrambled_eggs"},
            {"name": "Greek Yogurt Bowl with Honey, Chia Seeds & Banana", "calories": 380, "p": 28, "c": 48, "f": 8, "tag": "greek_yogurt"}
        ],
        "morning_snack": [
            {"name": "Apple Slices with 1 tbsp Natural Peanut Butter", "calories": 180, "p": 5, "c": 24, "f": 8, "tag": "peanut_butter_apple"},
            {"name": "Boiled Eggs (2) with a pinch of sea salt & black pepper", "calories": 140, "p": 12, "c": 1, "f": 10, "tag": "boiled_eggs"}
        ],
        "lunch": [
            {"name": "Grilled Chicken Breast with Brown Rice & Steamed Broccoli", "calories": 520, "p": 45, "c": 55, "f": 12, "tag": "chicken_rice"},
            {"name": "Baked Salmon Fillet with Quinoa & Asparagus", "calories": 540, "p": 40, "c": 45, "f": 20, "tag": "baked_salmon"},
            {"name": "Lean Turkey Wrap in Whole Wheat Tortilla with Greens", "calories": 480, "p": 38, "c": 46, "f": 14, "tag": "turkey_wrap"}
        ],
        "afternoon_snack": [
            {"name": "Protein Shake with Almond Milk & 1 Banana", "calories": 250, "p": 26, "c": 30, "f": 3, "tag": "protein_shake"},
            {"name": "Handful of Raw Mixed Nuts (Walnuts, Almonds)", "calories": 190, "p": 6, "c": 6, "f": 17, "tag": "mixed_nuts"}
        ],
        "dinner": [
            {"name": "Grilled White Fish / Cod with Sweet Potato Mash & Green Salad", "calories": 480, "p": 38, "c": 52, "f": 10, "tag": "grilled_fish"},
            {"name": "Lean Beef Stir-Fry with Bell Peppers, Onions & Jasmine Rice", "calories": 530, "p": 42, "c": 50, "f": 16, "tag": "beef_stirfry"},
            {"name": "Herb Roasted Chicken Thigh with Roasted Veggies", "calories": 490, "p": 36, "c": 32, "f": 22, "tag": "roast_chicken"}
        ]
    },
    "vegetarian": {
        "breakfast": [
            {"name": "Cottage Cheese (Paneer) Scramble with Sprouted Toast", "calories": 410, "p": 28, "c": 36, "f": 18, "tag": "paneer_bhurji"},
            {"name": "Rolled Oats cooked with Soy/Dairy Milk, Walnuts & Apple", "calories": 390, "p": 18, "c": 56, "f": 12, "tag": "protein_oatmeal"},
            {"name": "Moong Dal Cheela (Lentil Pancake) with Mint Chutney", "calories": 360, "p": 20, "c": 48, "f": 8, "tag": "cheela"}
        ],
        "morning_snack": [
            {"name": "Roasted Chickpeas (Chana) & Mixed Seeds", "calories": 160, "p": 8, "c": 22, "f": 5, "tag": "roasted_chickpeas"},
            {"name": "Greek Yogurt with Blueberries", "calories": 150, "p": 15, "c": 16, "f": 3, "tag": "greek_yogurt"}
        ],
        "lunch": [
            {"name": "Tofu & Mixed Veggie Curry with Brown Basmati Rice", "calories": 490, "p": 28, "c": 62, "f": 14, "tag": "tofu_curry"},
            {"name": "Paneer Tikka with Grilled Bell Peppers & Whole Wheat Roti", "calories": 510, "p": 30, "c": 48, "f": 20, "tag": "paneer_tikka"},
            {"name": "Lentil (Dal Tadka) with Quinoa & Fresh Cucumber Salad", "calories": 470, "p": 24, "c": 68, "f": 10, "tag": "dal_rice"}
        ],
        "afternoon_snack": [
            {"name": "Plant-Based Protein Shake or Sattu Drink", "calories": 210, "p": 24, "c": 22, "f": 3, "tag": "protein_shake"},
            {"name": "Sprouted Green Moong Salad with Lemon & Tomatoes", "calories": 140, "p": 9, "c": 22, "f": 1, "tag": "sprout_salad"}
        ],
        "dinner": [
            {"name": "Soya Chunks Curry with Whole Grain Flatbread & Greens", "calories": 460, "p": 38, "c": 50, "f": 10, "tag": "soya_curry"},
            {"name": "Chickpea & Spinach Mediterranean Stew with Brown Rice", "calories": 450, "p": 22, "c": 65, "f": 11, "tag": "chickpea_stew"},
            {"name": "Grilled Halloumi or Paneer Bowl with Roasted Vegetables", "calories": 480, "p": 26, "c": 38, "f": 24, "tag": "paneer_salad"}
        ]
    },
    "vegan": {
        "breakfast": [
            {"name": "Tofu Scramble with Turmeric, Spinach & Sourdough Toast", "calories": 380, "p": 24, "c": 38, "f": 14, "tag": "tofu_scramble"},
            {"name": "Overnight Oats with Chia, Soy Milk, Hemp Seeds & Blueberries", "calories": 410, "p": 20, "c": 58, "f": 12, "tag": "protein_oatmeal"},
            {"name": "Protein Green Smoothie (Pea Protein, Spinach, Banana, Flax)", "calories": 350, "p": 28, "c": 44, "f": 6, "tag": "green_smoothie"}
        ],
        "morning_snack": [
            {"name": "Edamame Beans in the Pod with Sea Salt", "calories": 150, "p": 14, "c": 10, "f": 5, "tag": "edamame"},
            {"name": "Carrot and Celery Sticks with 2 tbsp Hummus", "calories": 130, "p": 4, "c": 16, "f": 6, "tag": "hummus_veggies"}
        ],
        "lunch": [
            {"name": "Tempeh Nourish Bowl with Quinoa, Avocado & Tahini Dressing", "calories": 530, "p": 32, "c": 52, "f": 22, "tag": "tempeh_bowl"},
            {"name": "Black Bean & Sweet Potato Burrito Bowl with Pico de Gallo", "calories": 490, "p": 22, "c": 75, "f": 10, "tag": "burrito_bowl"},
            {"name": "High-Protein Lentil & Mushroom Bolognese over Whole Wheat Pasta", "calories": 510, "p": 28, "c": 78, "f": 8, "tag": "lentil_pasta"}
        ],
        "afternoon_snack": [
            {"name": "Pea / Rice Blend Protein Shake with Water or Oat Milk", "calories": 190, "p": 25, "c": 12, "f": 2, "tag": "protein_shake"},
            {"name": "Roasted Pumpkin Seeds & Dark Chocolate Square (85%)", "calories": 170, "p": 7, "c": 8, "f": 13, "tag": "mixed_nuts"}
        ],
        "dinner": [
            {"name": "Red Lentil Coconut Dahl with Steamed Brown Basmati & Greens", "calories": 470, "p": 24, "c": 68, "f": 12, "tag": "dal_rice"},
            {"name": "Crispy Baked Tofu with Teriyaki Stir-Fried Vegetables & Rice", "calories": 490, "p": 30, "c": 58, "f": 14, "tag": "tofu_stirfry"},
            {"name": "Mediterranean Falafel Bowl with Tabbouleh and Tahini Dip", "calories": 460, "p": 18, "c": 56, "f": 18, "tag": "falafel_bowl"}
        ]
    },
    "keto": {
        "breakfast": [
            {"name": "3 Eggs Scrambled with Butter, Spinach & Avocado", "calories": 440, "p": 22, "c": 4, "f": 36, "tag": "scrambled_eggs"},
            {"name": "Smoked Salmon & Cream Cheese Omelet with Chives", "calories": 460, "p": 30, "c": 2, "f": 36, "tag": "keto_omelet"}
        ],
        "morning_snack": [
            {"name": "String Cheese and Macadamia Nuts (30g)", "calories": 240, "p": 9, "c": 3, "f": 22, "tag": "mixed_nuts"}
        ],
        "lunch": [
            {"name": "Cobb Salad with Chicken, Bacon, Boiled Egg & Blue Cheese Dressing", "calories": 580, "p": 44, "c": 6, "f": 42, "tag": "cobb_salad"},
            {"name": "Grass-Fed Beef Burger Patties with Cheddar & Guacamole (No Bun)", "calories": 610, "p": 46, "c": 4, "f": 46, "tag": "keto_burger"}
        ],
        "afternoon_snack": [
            {"name": "Celery Sticks with Almond Butter", "calories": 170, "p": 5, "c": 4, "f": 15, "tag": "almond_butter"}
        ],
        "dinner": [
            {"name": "Pan-Seared Salmon Fillet with Asparagus in Garlic Butter", "calories": 560, "p": 42, "c": 5, "f": 40, "tag": "baked_salmon"},
            {"name": "Pork Chop or Ribeye Steak with Garlic Butter Mushrooms", "calories": 620, "p": 48, "c": 3, "f": 46, "tag": "keto_steak"}
        ]
    },
    "high_protein": {
        "breakfast": [
            {"name": "Egg White & Whole Egg Omelet (4 whites + 1 whole) with Turkey Bacon & Toast", "calories": 420, "p": 44, "c": 30, "f": 11, "tag": "high_protein_breakfast"},
            {"name": "Double Scoop Whey Protein Pancakes with Blueberries", "calories": 450, "p": 48, "c": 40, "f": 7, "tag": "protein_pancakes"}
        ],
        "morning_snack": [
            {"name": "1 Cup Non-Fat Greek Yogurt with Cinnamon & Walnuts", "calories": 210, "p": 25, "c": 12, "f": 6, "tag": "greek_yogurt"}
        ],
        "lunch": [
            {"name": "Grilled Chicken Breast (220g) with Sweet Potato & Green Beans", "calories": 520, "p": 55, "c": 45, "f": 8, "tag": "chicken_rice"},
            {"name": "Canned Tuna Salad with Olive Oil, Red Onion & Quinoa", "calories": 480, "p": 50, "c": 38, "f": 12, "tag": "tuna_salad"}
        ],
        "afternoon_snack": [
            {"name": "Whey Isolate Shake with 1 Apple", "calories": 220, "p": 30, "c": 22, "f": 1, "tag": "protein_shake"}
        ],
        "dinner": [
            {"name": "Extra Lean Ground Turkey Skillet with Zucchini Noodles & Marinara", "calories": 460, "p": 52, "c": 25, "f": 14, "tag": "turkey_skillet"},
            {"name": "Seared Sirloin Steak (200g) with Steamed Broccoli & Baked Potato", "calories": 540, "p": 54, "c": 40, "f": 16, "tag": "beef_stirfry"}
        ]
    }
}


def generate_ai_diet_plan(profile):
    """
    Calculates metabolic targets and generates a tailored nutrition plan.
    """
    if profile is not None:
        try:
            profile = dict(profile)
        except Exception:
            pass
    else:
        profile = {}

    age = profile.get("age") or 25
    gender = profile.get("gender") or "male"
    height = profile.get("height_cm") or 175
    weight = profile.get("weight_kg") or 70
    goal = profile.get("fitness_goal") or "general_fitness"
    activity = profile.get("activity_level") or "moderate"
    diet_pref = (profile.get("dietary_preference") or "standard").lower()

    if diet_pref not in MEAL_DATABASE:
        diet_pref = "standard"

    # Metabolic calculations
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)
    hydration_liters = calculate_hydration(weight, activity)

    # Goal caloric adjustment
    if goal == "weight_loss":
        target_calories = round(tdee - 500, 0)
        # Minimum safe calories
        target_calories = max(target_calories, 1300 if gender == "female" else 1500)
        p_pct, c_pct, f_pct = 35, 40, 25
    elif goal == "weight_gain":
        target_calories = round(tdee + 450, 0)
        p_pct, c_pct, f_pct = 25, 55, 20
    elif goal == "muscle_building":
        target_calories = round(tdee + 250, 0)
        p_pct, c_pct, f_pct = 30, 45, 25
    elif goal == "endurance":
        target_calories = round(tdee + 150, 0)
        p_pct, c_pct, f_pct = 20, 60, 20
    else: # general_fitness
        target_calories = round(tdee, 0)
        p_pct, c_pct, f_pct = 25, 50, 25

    if diet_pref == "keto":
        p_pct, c_pct, f_pct = 25, 5, 70
    elif diet_pref == "high_protein":
        p_pct, c_pct, f_pct = 40, 35, 25

    # Grams: Protein 4 cal/g, Carbs 4 cal/g, Fat 9 cal/g
    protein_g = round((target_calories * (p_pct / 100.0)) / 4.0, 1)
    carbs_g = round((target_calories * (c_pct / 100.0)) / 4.0, 1)
    fat_g = round((target_calories * (f_pct / 100.0)) / 9.0, 1)

    # Build 7-day meal plan
    pref_meals = MEAL_DATABASE[diet_pref]
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    meal_plan_days = []

    for i, day in enumerate(week_days):
        b = pref_meals["breakfast"][i % len(pref_meals["breakfast"])]
        ms = pref_meals["morning_snack"][i % len(pref_meals["morning_snack"])]
        l = pref_meals["lunch"][i % len(pref_meals["lunch"])]
        as_ = pref_meals["afternoon_snack"][i % len(pref_meals["afternoon_snack"])]
        d = pref_meals["dinner"][i % len(pref_meals["dinner"])]

        day_cals = b["calories"] + ms["calories"] + l["calories"] + as_["calories"] + d["calories"]
        day_p = b["p"] + ms["p"] + l["p"] + as_["p"] + d["p"]
        day_c = b["c"] + ms["c"] + l["c"] + as_["c"] + d["c"]
        day_f = b["f"] + ms["f"] + l["f"] + as_["f"] + d["f"]

        meal_plan_days.append({
            "day": day,
            "totals": {"calories": day_cals, "protein": day_p, "carbs": day_c, "fat": day_f},
            "meals": {
                "Breakfast (08:00 AM)": b,
                "Morning Boost (11:00 AM)": ms,
                "Lunch (01:30 PM)": l,
                "Pre/Post Workout Snack (05:00 PM)": as_,
                "Dinner (08:00 PM)": d
            }
        })

    diet_plan = {
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "macronutrients": {
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "protein_pct": p_pct,
            "carbs_pct": c_pct,
            "fat_pct": f_pct
        },
        "hydration_liters": hydration_liters,
        "dietary_preference": diet_pref.replace("_", " ").title(),
        "guidelines": [
            f"Aim to drink at least {hydration_liters}L of fresh water spaced evenly throughout the day.",
            "Eat lean protein with each primary meal to preserve lean muscle and support recovery.",
            "Keep high-glycemic carbohydrates closer to your workout window for peak performance.",
            "Avoid sugary beverages and late-night heavy snacking at least 2 hours before bedtime."
        ],
        "days": meal_plan_days
    }

    return diet_plan
