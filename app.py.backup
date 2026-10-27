import os
import json
import math
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from database import init_db,execute_db,query_db,get_db
import ml_engine
from chatbot import get_chatbot_response
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database on startup
with app.app_context():
    init_db()


# ----------------------------------------------------
# Authentication Decorator & Helpers
# ----------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your fitness dashboard.", "info")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    if "user_id" in session:
        return query_db("SELECT * FROM users WHERE id = ?", (session["user_id"],), one=True)
    return None


@app.context_processor
def inject_user():
    user = get_current_user()
    active_reminders_count = 0
    if user:
        r = query_db("SELECT COUNT(*) as count FROM reminders WHERE user_id = ? AND is_active = 1", (user["id"],), one=True)
        active_reminders_count = r["count"] if r else 0
    return dict(current_user=user, active_reminders_count=active_reminders_count)


# ----------------------------------------------------
# Video Catalog Data
# ----------------------------------------------------

VIDEOS_DATABASE = [
    {
        "id": "v1",
        "title": "Barbell Squat Perfect Form Masterclass",
        "category": "workout",
        "subcategory": "Strength",
        "difficulty": "Beginner to Intermediate",
        "duration": "8:35",
       "embed_url": "https://www.youtube.com/embed/gcNh17Ckjgg",
"thumbnail": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?auto=format&fit=crop&w=600&q=80",
"description": "Learn proper squat stance, hip hinge, knee tracking, and barbell bar path for maximum leg development and knee safety."
},
    {
        "id": "v2",
        "title": "Bench Press Technique: Chest Activation Guide",
        "category": "workout",
        "subcategory": "Strength",\

        "difficulty": "All Levels",
        "duration": "7:12",
        "embed_url": "https://www.youtube.com/embed/rT7DgCr-3pg",
        "thumbnail": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=600&q=80",
        "description": "Scapular retraction, arch positioning, leg drive, and elbow angle to prevent shoulder impingement and target pectorals."
    },
    {
        "id": "v3",
        "title": "Conventional Deadlift: Complete Step-by-Step",
        "category": "workout",
        "subcategory": "Strength",
        "difficulty": "Intermediate",
        "duration": "10:18",
        "embed_url": "https://www.youtube.com/embed/op9kVnSso6Q",
        "thumbnail": "https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?auto=format&fit=crop&w=600&q=80",
        "description": "Master the hip hinge, spine bracing, and leg drive for the king of posterior chain compound lifts."
    },
    {
        "id": "v4",
        "title": "15-Minute Fat-Burning HIIT Workout (No Equipment)",
        "category": "workout",
        "subcategory": "Cardio",
        "difficulty": "All Levels",
        "duration": "15:00",
        "embed_url": "https://www.youtube.com/embed/ml6cT4AZdqI",
        "thumbnail": "https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=600&q=80",
        "description": "High-intensity intervals designed to burn maximum calories, boost cardiovascular fitness, and accelerate fat loss at home."
    },
    {
        "id": "v5",
        "title": "10-Minute Core & Abs Shred Routine",
        "category": "workout",
        "subcategory": "Core",
        "difficulty": "Beginner to Advanced",
        "duration": "10:24",
        "embed_url": "https://www.youtube.com/embed/DHD1-2P94DI",
        "thumbnail": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?auto=format&fit=crop&w=600&q=80",
        "description": "Target the rectus abdominis, obliques, and transverse abdominis with progressive planks, flutter kicks, and leg raises."
    },
    {
        "id": "v6",
        "title": "How to Do Perfect Push-ups for Beginners",
        "category": "workout",
        "subcategory": "Strength",
        "difficulty": "Beginner",
        "duration": "6:45",
        "embed_url": "https://www.youtube.com/embed/IODxDxX7oi4",
        "thumbnail": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?auto=format&fit=crop&w=600&q=80",
        "description": "Progress from incline push-ups to strict floor push-ups with proper hand placement and core engagement."
    },
  {
    "id": "v7",
    "title": "High-Protein Meal Prep for the Week",
    "category": "diet",
    "subcategory": "Meal Prep",
    "difficulty": "Easy",
    "duration": "12:40",
    "embed_url": "https://www.youtube.com/embed/0GNfATCkS8g",
    "thumbnail": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=600&q=80",
    "description": "Budget-friendly high-protein meal preparation for the week."
},
{
    "id": "v8",
    "title": "5 Healthy Breakfast Ideas | Easy High-Protein Recipes",
    "category": "diet",
    "subcategory": "Breakfast",
    "difficulty": "Easy",
    "duration": "9:15",
    "embed_url": "https://www.youtube.com/embed/EyFcGkeL_kA",
    "thumbnail": "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=600&q=80",
    "description": "Five healthy and easy high-protein breakfast ideas."
},
{
    "id": "v9",
    "title": "Crispy Tofu & Vegetable Stir Fry",
    "category": "diet",
    "subcategory": "Dinner",
    "difficulty": "Intermediate",
    "duration": "11:20",
    "embed_url": "https://www.youtube.com/embed/EcKMdSXbIiI",
    "thumbnail": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=600&q=80",
    "description": "Crispy tofu and vegetables prepared as a healthy high-protein meal."
},
{
    "id": "v10",
    "title": "Healthy High-Protein Smoothie Bowl",
    "category": "diet",
    "subcategory": "Snacks",
    "difficulty": "Easy",
    "duration": "5:50",
    "embed_url": "https://www.youtube.com/embed/Dm86d7C6AZs",
    "thumbnail": "https://images.unsplash.com/photo-1590301157890-4810ed352733?auto=format&fit=crop&w=600&q=80",
    "description": "A high-protein smoothie bowl made with healthy ingredients."
}
]


# ----------------------------------------------------
# Core Page Routes
# ----------------------------------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        full_name = request.form.get("full_name", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validations
        if not username or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        # Check existing
        existing_user = query_db("SELECT id FROM users WHERE username = ? OR email = ?", (username, email), one=True)
        if existing_user:
            flash("Username or email already registered. Please login.", "warning")
            return render_template("register.html")

        # Create user
        pwd_hash = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (username, email, password_hash, full_name) VALUES (?, ?, ?, ?)",
            (username, email, pwd_hash, full_name)
        )

        # Initialize empty profile
        execute_db("INSERT INTO user_profiles (user_id) VALUES (?)", (user_id,))

        # Create default reminders
        execute_db("INSERT INTO reminders (user_id, title, reminder_type, reminder_time) VALUES (?, ?, ?, ?)",
                   (user_id, "Morning Workout & Warmup", "workout", "07:00"))
        execute_db("INSERT INTO reminders (user_id, title, reminder_type, reminder_time) VALUES (?, ?, ?, ?)",
                   (user_id, "Mid-Day Hydration Check (500ml)", "water", "13:00"))
        execute_db("INSERT INTO reminders (user_id, title, reminder_type, reminder_time) VALUES (?, ?, ?, ?)",
                   (user_id, "Nutritious High-Protein Dinner", "meal", "20:00"))

        session["user_id"] = user_id
        session["username"] = username
        flash(f"Welcome to AI Workout & Diet Plan, {full_name or username}! Let's set up your fitness profile.", "success")
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        user = query_db(
            "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (username_or_email, username_or_email),
            one=True
        )

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome back, {user['full_name'] or user['username']}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("dashboard"))
        else:
            flash("Invalid username or password. Please check your credentials.", "danger")

    return render_template("login.html")
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        username = request.form.get('username')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check empty fields
        if not username or not new_password or not confirm_password:
            flash('Please fill all fields.', 'error')
            return redirect(url_for('forgot_password'))

        # Check passwords
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('forgot_password'))

        # Find user
        user = query_db(
            'SELECT * FROM users WHERE username = ? OR email = ?',
            [username, username],
            one=True
        )

        if not user:
            flash('Username or email not found.', 'error')
            return redirect(url_for('forgot_password'))

        # Hash new password
        hashed_password = generate_password_hash(new_password)

        # Update password
        execute_db(
            'UPDATE users SET password = ? WHERE id = ?',
            [hashed_password, user['id']]
        )

        flash('Password reset successfully. Please sign in.', 'success')

        return redirect(url_for('login'))

    return render_template('forgot_password.html')

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("login"))


# ----------------------------------------------------
# Dashboard & Profile Routes
# ----------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    profile_row = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
    profile = dict(profile_row) if profile_row else {}
    
    # Check if profile is configured
    if not profile or not profile.get("height_cm") or not profile.get("weight_kg"):
        flash("Please complete your fitness profile to generate your custom AI plan.", "warning")
        return redirect(url_for("profile"))

    # Latest recommendation
    rec = query_db("SELECT * FROM recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    
    # If no recommendation yet, generate one now
    if not rec:
        rec = generate_and_save_recommendations(user_id, profile)

    workout_plan = json.loads(rec["workout_plan"]) if rec and rec["workout_plan"] else None
    diet_plan = json.loads(rec["diet_plan"]) if rec and rec["diet_plan"] else None

    # Calculate BMI metrics
    bmi, bmi_category, bmi_color, bmi_desc = ml_engine.calculate_bmi(profile["weight_kg"], profile["height_cm"])
    min_ideal_wt, max_ideal_wt = ml_engine.calculate_ideal_weight_range(profile["height_cm"])

    # Today's day name
    today_name = datetime.now().strftime("%A")
    today_workout = None
    today_diet = None

    if workout_plan and "days" in workout_plan:
        for d in workout_plan["days"]:
            if d.get("day") == today_name:
                today_workout = d
                break
        if not today_workout and len(workout_plan["days"]) > 0:
            today_workout = workout_plan["days"][0]

    if diet_plan and "days" in diet_plan:
        for d in diet_plan["days"]:
            if d.get("day") == today_name:
                today_diet = d
                break
        if not today_diet and len(diet_plan["days"]) > 0:
            today_diet = diet_plan["days"][0]

    # Today's progress log
    today_str = date.today().isoformat()
    today_log = query_db("SELECT * FROM progress_logs WHERE user_id = ? AND log_date = ?", (user_id, today_str), one=True)

    # Streak calculation
    recent_logs = query_db("SELECT DISTINCT log_date FROM progress_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 30", (user_id,))
    streak_days = len(recent_logs)

    return render_template(
        "dashboard.html",
        profile=profile,
        rec=rec,
        bmi=bmi,
        bmi_category=bmi_category,
        bmi_color=bmi_color,
        bmi_desc=bmi_desc,
        min_ideal_wt=min_ideal_wt,
        max_ideal_wt=max_ideal_wt,
        workout_plan=workout_plan,
        diet_plan=diet_plan,
        today_name=today_name,
        today_workout=today_workout,
        today_diet=today_diet,
        today_log=today_log,
        streak_days=streak_days
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    profile_row = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        age = int(request.form.get("age", 25) or 25)
        gender = request.form.get("gender", "male")
        height_cm = float(request.form.get("height_cm", 175) or 175)
        weight_kg = float(request.form.get("weight_kg", 70) or 70)
        target_weight_kg = float(request.form.get("target_weight_kg", weight_kg) or weight_kg)
        fitness_goal = request.form.get("fitness_goal", "general_fitness")
        activity_level = request.form.get("activity_level", "moderate")
        exercise_frequency = request.form.get("exercise_frequency", "3-4")
        dietary_preference = request.form.get("dietary_preference", "standard")
        health_conditions = request.form.get("health_conditions", "").strip()

        # Update user record
        execute_db("UPDATE users SET full_name = ? WHERE id = ?", (full_name, user_id))

        # Update profile record
        execute_db("""
            UPDATE user_profiles SET
                age = ?, gender = ?, height_cm = ?, weight_kg = ?, target_weight_kg = ?,
                fitness_goal = ?, activity_level = ?, exercise_frequency = ?,
                dietary_preference = ?, health_conditions = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            age, gender, height_cm, weight_kg, target_weight_kg,
            fitness_goal, activity_level, exercise_frequency,
            dietary_preference, health_conditions, user_id
        ))

        # Log current weight in progress logs for today if not already logged
        today_str = date.today().isoformat()
        bmi, _, _, _ = ml_engine.calculate_bmi(weight_kg, height_cm)
        existing_log = query_db("SELECT id FROM progress_logs WHERE user_id = ? AND log_date = ?", (user_id, today_str), one=True)
        if not existing_log:
            execute_db("INSERT INTO progress_logs (user_id, log_date, weight_kg, bmi) VALUES (?, ?, ?, ?)",
                       (user_id, today_str, weight_kg, bmi))
        else:
            execute_db("UPDATE progress_logs SET weight_kg = ?, bmi = ? WHERE id = ?", (weight_kg, bmi, existing_log["id"]))

        # Automatically generate refreshed AI recommendation plan
        updated_profile_row = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
        updated_profile = dict(updated_profile_row) if updated_profile_row else {}
        generate_and_save_recommendations(user_id, updated_profile)

        flash("Fitness profile updated and new AI workout & diet plan generated!", "success")
        return redirect(url_for("dashboard"))

    # Calculate initial BMI preview
    bmi_preview = None
    if profile_row and profile_row["height_cm"] and profile_row["weight_kg"]:
        bmi_preview = ml_engine.calculate_bmi(profile_row["weight_kg"], profile_row["height_cm"])

    return render_template("profile.html", user=user, profile=profile_row, bmi_preview=bmi_preview)


# ----------------------------------------------------
# Recommendation Generation & Views
# ----------------------------------------------------

def generate_and_save_recommendations(user_id, profile):
    """Invokes ML engine to create and persist recommendations."""
    if profile is not None:
        try:
            profile = dict(profile)
        except Exception:
            pass
    else:
        profile = {}

    workout_plan = ml_engine.generate_ai_workout_plan(profile)
    diet_plan = ml_engine.generate_ai_diet_plan(profile)
    
    weight = profile.get("weight_kg") or 70
    height = profile.get("height_cm") or 175
    bmi, bmi_category, _, _ = ml_engine.calculate_bmi(weight, height)
    bmr = diet_plan["bmr"]
    tdee = diet_plan["tdee"]
    target_cals = diet_plan["target_calories"]
    protein_g = diet_plan["macronutrients"]["protein_g"]
    carbs_g = diet_plan["macronutrients"]["carbs_g"]
    fat_g = diet_plan["macronutrients"]["fat_g"]
    hydration = diet_plan["hydration_liters"]

    rec_id = execute_db("""
        INSERT INTO recommendations (
            user_id, bmi, bmi_category, bmr, tdee, target_calories,
            protein_g, carbs_g, fat_g, workout_plan, diet_plan, water_intake_liters
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, bmi, bmi_category, bmr, tdee, target_cals,
        protein_g, carbs_g, fat_g, json.dumps(workout_plan), json.dumps(diet_plan), hydration
    ))

    return query_db("SELECT * FROM recommendations WHERE id = ?", (rec_id,), one=True)


@app.route("/recommendations")
@login_required
def recommendations():
    user_id = session["user_id"]
    profile_row = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
    profile = dict(profile_row) if profile_row else {}
    if not profile or not profile.get("height_cm") or not profile.get("weight_kg"):
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile"))

    rec = query_db("SELECT * FROM recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    if not rec:
        rec = generate_and_save_recommendations(user_id, profile)

    workout_plan = json.loads(rec["workout_plan"]) if rec and rec["workout_plan"] else {}
    diet_plan = json.loads(rec["diet_plan"]) if rec and rec["diet_plan"] else {}
    bmi, bmi_category, bmi_color, bmi_desc = ml_engine.calculate_bmi(profile.get("weight_kg", 70), profile.get("height_cm", 175))

    return render_template(
        "recommendations.html",
        profile=profile,
        rec=rec,
        workout_plan=workout_plan,
        diet_plan=diet_plan,
        bmi=bmi,
        bmi_category=bmi_category,
        bmi_color=bmi_color,
        bmi_desc=bmi_desc
    )


@app.route("/recommendations/generate", methods=["POST"])
@login_required
def regenerate_recommendations():
    user_id = session["user_id"]
    profile_row = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
    profile = dict(profile_row) if profile_row else {}
    if not profile or not profile.get("height_cm") or not profile.get("weight_kg"):
        flash("Please update your fitness profile first.", "warning")
        return redirect(url_for("profile"))

    generate_and_save_recommendations(user_id, profile)
    flash("Your AI Workout & Nutrition plan has been re-optimized with the latest fitness models!", "success")
    return redirect(url_for("recommendations"))


@app.route("/recommendations/print")
@login_required
def print_recommendations():
    user_id = session["user_id"]
    profile = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
    rec = query_db("SELECT * FROM recommendations WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,), one=True)
    user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    
    workout_plan = json.loads(rec["workout_plan"]) if rec and rec["workout_plan"] else {}
    diet_plan = json.loads(rec["diet_plan"]) if rec and rec["diet_plan"] else {}
    
    return render_template(
        "print_plan.html",
        user=user,
        profile=profile,
        rec=rec,
        workout_plan=workout_plan,
        diet_plan=diet_plan
    )


# ----------------------------------------------------
# Video Module
# ----------------------------------------------------

@app.route("/videos")
@login_required
def videos():
    category = request.args.get("category", "all")
    query = request.args.get("q", "").strip().lower()

    filtered_videos = VIDEOS_DATABASE
    if category in ("workout", "diet"):
        filtered_videos = [v for v in filtered_videos if v["category"] == category]

    if query:
        filtered_videos = [
            v for v in filtered_videos
            if query in v["title"].lower() or query in v["subcategory"].lower() or query in v["description"].lower()
        ]

    return render_template("videos.html", videos=filtered_videos, active_category=category, search_query=query)


# ----------------------------------------------------
# Interactive Gym Search Module
# ----------------------------------------------------

DEFAULT_GYMS = [
    {
        "id": 1,
        "name": "Gold's Gym - Elite Fitness Hub",
        "address": "452 Metropolitan Ave, Downtown",
        "lat": 40.7128,
        "lng": -74.0060,
        "rating": 4.8,
        "review_count": 312,
        "phone": "+1 (555) 234-5678",
        "website": "https://www.goldsgym.com",
        "amenities": ["Free Weights", "Cardio Deck", "Sauna & Steam", "Personal Training", "CrossFit Area"],
        "hours": "Open 24/7"
    },
    {
        "id": 2,
        "name": "Anytime Fitness & Wellness Club",
        "address": "780 Broadway, Midtown Plaza",
        "lat": 40.7250,
        "lng": -73.9950,
        "rating": 4.6,
        "review_count": 184,
        "phone": "+1 (555) 876-5432",
        "website": "https://www.anytimefitness.com",
        "amenities": ["24/7 Access", "Functional Turf", "HydroMassage", "Olympic Lifting Platforms"],
        "hours": "Open 24/7"
    },
    {
        "id": 3,
        "name": "Equinox Luxury Health & Fitness",
        "address": "120 Park Avenue, Financial District",
        "lat": 40.7080,
        "lng": -74.0110,
        "rating": 4.9,
        "review_count": 420,
        "phone": "+1 (555) 901-2345",
        "website": "https://www.equinox.com",
        "amenities": ["Rooftop Pool", "Pilates Studio", "Juice Bar", "Spa", "Towel Service"],
        "hours": "05:30 AM - 11:00 PM"
    },
    {
        "id": 4,
        "name": "Planet Fitness Express",
        "address": "330 West 42nd St, Central",
        "lat": 40.7580,
        "lng": -73.9855,
        "rating": 4.4,
        "review_count": 290,
        "phone": "+1 (555) 432-1098",
        "website": "https://www.planetfitness.com",
        "amenities": ["Judgement Free Zone", "Treadmills & Stairmills", "Total Body Circuit", "Showers"],
        "hours": "Open 24 Hours"
    },
    {
        "id": 5,
        "name": "Iron Beast Barbell & Powerlifting Club",
        "address": "15 Industrial Parkway, North Wing",
        "lat": 40.7390,
        "lng": -74.0200,
        "rating": 4.9,
        "review_count": 165,
        "phone": "+1 (555) 654-7890",
        "website": "https://www.ironbeastclub.com",
        "amenities": ["Eleiko Plates", "Chalk Allowed", "Mono-lifts", "Strongman Implements"],
        "hours": "06:00 AM - 10:00 PM"
    },
    {
        "id": 6,
        "name": "Cult.fit Modern Functional Center",
        "address": "22 Silicon Boulevard, Tech Park",
        "lat": 40.7420,
        "lng": -73.9780,
        "rating": 4.7,
        "review_count": 215,
        "phone": "+1 (555) 345-6789",
        "website": "https://www.cult.fit",
        "amenities": ["Boxing Ring", "HIIT Group Classes", "Yoga & Mobility", "Nutrition Bar"],
        "hours": "06:00 AM - 10:00 PM"
    }
]


@app.route("/gyms")
@login_required
def gyms():
    user_id = session["user_id"]
    favorites = query_db("SELECT * FROM gym_favorites WHERE user_id = ? ORDER BY id DESC", (user_id,))
    return render_template("gym_search.html", default_gyms=DEFAULT_GYMS, favorites=favorites)


@app.route("/api/gyms/search")
@login_required
def api_gyms_search():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    query = request.args.get("query", "").strip().lower()

    # Filter or offset coordinates around given coordinates
    results = []
    base_lat = lat if lat is not None else 40.7128
    base_lng = lng if lng is not None else -74.0060

    for i, g in enumerate(DEFAULT_GYMS):
        if query and (query not in g["name"].lower() and query not in g["address"].lower()):
            continue
        
        # Calculate dynamic position around user's requested latitude/longitude
        g_copy = dict(g)
        if lat is not None and lng is not None:
            # Slight random offset so markers fan out realistically around the user's location
            offsets = [(0.005, 0.004), (-0.006, 0.007), (0.008, -0.005), (-0.004, -0.006), (0.010, 0.009), (-0.008, 0.003)]
            d_lat, d_lng = offsets[i % len(offsets)]
            g_copy["lat"] = round(base_lat + d_lat, 5)
            g_copy["lng"] = round(base_lng + d_lng, 5)
            
            # Approximate distance in km
            dist_km = round(math.sqrt((d_lat * 111)**2 + (d_lng * 85)**2), 2)
            g_copy["distance_km"] = dist_km
        else:
            g_copy["distance_km"] = round(1.2 + (i * 0.7), 1)

        results.append(g_copy)

    return jsonify({"status": "success", "gyms": results})


@app.route("/api/gyms/favorite", methods=["POST"])
@login_required
def api_gym_favorite():
    user_id = session["user_id"]
    data = request.get_json() or {}
    gym_name = data.get("gym_name", "").strip()
    address = data.get("address", "").strip()
    lat = data.get("latitude")
    lng = data.get("longitude")
    rating = data.get("rating", 4.5)
    phone = data.get("phone", "")
    website = data.get("website", "")

    if not gym_name:
        return jsonify({"status": "error", "message": "Gym name is required"}), 400

    # Check if already in favorites
    existing = query_db("SELECT id FROM gym_favorites WHERE user_id = ? AND gym_name = ?", (user_id, gym_name), one=True)
    if existing:
        execute_db("DELETE FROM gym_favorites WHERE id = ?", (existing["id"],))
        return jsonify({"status": "removed", "message": f"{gym_name} removed from favorites"})
    else:
        execute_db("""
            INSERT INTO gym_favorites (user_id, gym_name, address, latitude, longitude, rating, phone, website)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, gym_name, address, lat, lng, rating, phone, website))
        return jsonify({"status": "saved", "message": f"{gym_name} added to your favorite gyms!"})


# ----------------------------------------------------
# Notifications & Reminders Module
# ----------------------------------------------------

@app.route("/reminders", methods=["GET", "POST"])
@login_required
def reminders():
    user_id = session["user_id"]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        reminder_type = request.form.get("reminder_type", "workout")
        reminder_time = request.form.get("reminder_time", "08:00").strip()
        days_of_week = request.form.get("days_of_week", "Mon,Tue,Wed,Thu,Fri,Sat,Sun")

        if not title or not reminder_time:
            flash("Please specify a title and time for your reminder.", "danger")
        else:
            execute_db("""
                INSERT INTO reminders (user_id, title, reminder_type, reminder_time, days_of_week, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (user_id, title, reminder_type, reminder_time, days_of_week))
            flash("Fitness reminder scheduled successfully!", "success")
        return redirect(url_for("reminders"))

    user_reminders = query_db("SELECT * FROM reminders WHERE user_id = ? ORDER BY reminder_time ASC", (user_id,))
    return render_template("reminders.html", reminders=user_reminders)


@app.route("/api/reminders/toggle/<int:rem_id>", methods=["POST"])
@login_required
def api_toggle_reminder(rem_id):
    user_id = session["user_id"]
    rem = query_db("SELECT * FROM reminders WHERE id = ? AND user_id = ?", (rem_id, user_id), one=True)
    if not rem:
        return jsonify({"status": "error", "message": "Reminder not found"}), 404

    new_state = 0 if rem["is_active"] else 1
    execute_db("UPDATE reminders SET is_active = ? WHERE id = ?", (new_state, rem_id))
    return jsonify({"status": "success", "is_active": new_state})


@app.route("/api/reminders/delete/<int:rem_id>", methods=["POST"])
@login_required
def api_delete_reminder(rem_id):
    user_id = session["user_id"]
    execute_db("DELETE FROM reminders WHERE id = ? AND user_id = ?", (rem_id, user_id))
    flash("Reminder deleted.", "info")
    return redirect(url_for("reminders"))


@app.route("/api/reminders/active")
@login_required
def api_active_reminders():
    user_id = session["user_id"]
    rems = query_db("SELECT * FROM reminders WHERE user_id = ? AND is_active = 1 ORDER BY reminder_time ASC", (user_id,))
    items = [dict(r) for r in rems]
    return jsonify({"status": "success", "reminders": items})


# ----------------------------------------------------
# Progress Tracking & Analytics Module
# ----------------------------------------------------

@app.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    user_id = session["user_id"]
    profile = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)

    if request.method == "POST":
        log_date = request.form.get("log_date") or date.today().isoformat()
        weight_kg = float(request.form.get("weight_kg") or (profile["weight_kg"] if profile else 70))
        workouts_completed = int(request.form.get("workouts_completed", 0) or 0)
        calories_burned = float(request.form.get("calories_burned", 0) or 0)
        water_ml = float(request.form.get("water_ml", 0) or 0)
        chest_cm = float(request.form.get("chest_cm") or 0) if request.form.get("chest_cm") else None
        waist_cm = float(request.form.get("waist_cm") or 0) if request.form.get("waist_cm") else None
        hips_cm = float(request.form.get("hips_cm") or 0) if request.form.get("hips_cm") else None
        notes = request.form.get("notes", "").strip()

        # Calculate BMI
        height = profile["height_cm"] if profile and profile["height_cm"] else 175
        bmi, _, _, _ = ml_engine.calculate_bmi(weight_kg, height)

        # Check existing log for this date
        existing = query_db("SELECT id FROM progress_logs WHERE user_id = ? AND log_date = ?", (user_id, log_date), one=True)
        if existing:
            execute_db("""
                UPDATE progress_logs SET
                    weight_kg = ?, bmi = ?, workouts_completed = ?, calories_burned = ?,
                    water_ml = ?, chest_cm = ?, waist_cm = ?, hips_cm = ?, notes = ?
                WHERE id = ?
            """, (weight_kg, bmi, workouts_completed, calories_burned, water_ml, chest_cm, waist_cm, hips_cm, notes, existing["id"]))
            flash(f"Progress log updated for {log_date}!", "success")
        else:
            execute_db("""
                INSERT INTO progress_logs (
                    user_id, log_date, weight_kg, bmi, workouts_completed,
                    calories_burned, water_ml, chest_cm, waist_cm, hips_cm, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, log_date, weight_kg, bmi, workouts_completed, calories_burned, water_ml, chest_cm, waist_cm, hips_cm, notes))
            flash(f"New fitness log saved for {log_date}!", "success")

        # Also update current weight in profile if this is the newest log
        execute_db("UPDATE user_profiles SET weight_kg = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (weight_kg, user_id))

        return redirect(url_for("progress"))

    logs = query_db("SELECT * FROM progress_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 60", (user_id,))
    
    # Adherence & metrics summary
    total_workouts = sum(log["workouts_completed"] or 0 for log in logs)
    total_calories_burned = sum(log["calories_burned"] or 0 for log in logs)
    avg_water_ml = round(sum(log["water_ml"] or 0 for log in logs) / max(len(logs), 1), 0)

    # Calculate weight change
    weight_change = 0.0
    if len(logs) >= 2:
        latest_wt = logs[0]["weight_kg"]
        earliest_wt = logs[-1]["weight_kg"]
        if latest_wt and earliest_wt:
            weight_change = round(latest_wt - earliest_wt, 1)

    return render_template(
        "progress.html",
        logs=logs,
        profile=profile,
        total_workouts=total_workouts,
        total_calories_burned=total_calories_burned,
        avg_water_ml=avg_water_ml,
        weight_change=weight_change,
        today_date=date.today().isoformat()
    )


@app.route("/api/progress/quick-water", methods=["POST"])
@login_required
def api_quick_water():
    user_id = session["user_id"]
    data = request.get_json() or {}
    amount_ml = float(data.get("amount_ml", 250))
    today_str = date.today().isoformat()

    log = query_db("SELECT * FROM progress_logs WHERE user_id = ? AND log_date = ?", (user_id, today_str), one=True)
    if log:
        new_total = (log["water_ml"] or 0) + amount_ml
        execute_db("UPDATE progress_logs SET water_ml = ? WHERE id = ?", (new_total, log["id"]))
    else:
        profile = query_db("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
        wt = profile["weight_kg"] if profile and profile["weight_kg"] else 70
        ht = profile["height_cm"] if profile and profile["height_cm"] else 175
        bmi, _, _, _ = ml_engine.calculate_bmi(wt, ht)
        execute_db("INSERT INTO progress_logs (user_id, log_date, weight_kg, bmi, water_ml) VALUES (?, ?, ?, ?, ?)",
                   (user_id, today_str, wt, bmi, amount_ml))
        new_total = amount_ml

    return jsonify({"status": "success", "total_water_ml": new_total})


@app.route("/api/progress/delete/<int:log_id>", methods=["POST"])
@login_required
def api_delete_log(log_id):
    user_id = session["user_id"]
    execute_db("DELETE FROM progress_logs WHERE id = ? AND user_id = ?", (log_id, user_id))
    flash("Progress entry deleted.", "info")
    return redirect(url_for("progress"))


@app.route("/api/progress/stats")
@login_required
def api_progress_stats():
    user_id = session["user_id"]
    logs = query_db("SELECT log_date, weight_kg, bmi, calories_burned, water_ml, waist_cm, chest_cm FROM progress_logs WHERE user_id = ? ORDER BY log_date ASC LIMIT 30", (user_id,))

    labels = [l["log_date"] for l in logs]
    weights = [l["weight_kg"] for l in logs]
    bmis = [l["bmi"] for l in logs]
    calories = [l["calories_burned"] for l in logs]
    water = [l["water_ml"] for l in logs]
    waist = [l["waist_cm"] for l in logs]

    # Target weight
    profile = query_db("SELECT target_weight_kg FROM user_profiles WHERE user_id = ?", (user_id,), one=True)
    target_weight = profile["target_weight_kg"] if profile and profile["target_weight_kg"] else (weights[-1] if weights else 70)

    return jsonify({
        "status": "success",
        "labels": labels,
        "weights": weights,
        "bmis": bmis,
        "calories": calories,
        "water": water,
        "waist": waist,
        "target_weight": target_weight
    })
@app.route("/future-prediction")
def future_prediction():
    # Check login
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get current user's profile
    profile = query_db(
        """
        SELECT
            age,
            gender,
            height_cm,
            weight_kg,
            target_weight_kg,
            fitness_goal,
            activity_level,
            exercise_frequency,
            dietary_preference
        FROM user_profiles
        WHERE user_id = ?
        """,
        (session["user_id"],),
        one=True
    )

    # Profile not found
    if not profile:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("profile"))

    # Check height and weight
    try:
        height_cm = float(profile["height_cm"])
        current_weight = float(profile["weight_kg"])
    except (TypeError, ValueError):
        flash("Please enter valid height and weight in your profile.", "danger")
        return redirect(url_for("profile"))

    if height_cm <= 0 or current_weight <= 0:
        flash("Please enter valid height and weight in your profile.", "danger")
        return redirect(url_for("profile"))

    # Convert height to metres
    height_m = height_cm / 100

    # Current BMI
    current_bmi = current_weight / (height_m * height_m)

    # Get goal
    fitness_goal = str(
        profile["fitness_goal"] or "general_fitness"
    ).lower()

    # Get current activity level
    activity_level = str(
        profile["activity_level"] or "moderate"
    ).lower()

    # --------------------------------------------------
    # Estimated monthly weight change
    # --------------------------------------------------

    if "gain" in fitness_goal:
        monthly_change = 0.7

    elif "loss" in fitness_goal or "lose" in fitness_goal:
        monthly_change = -0.5

    else:
        monthly_change = 0.0

    # --------------------------------------------------
    # Prediction periods
    # --------------------------------------------------

    periods = [
        ("1 Month", 1),
        ("3 Months", 3),
        ("6 Months", 6),
        ("1 Year", 12)
    ]

    predictions = []

    for period_name, months in periods:

        # Calculate predicted weight
        predicted_weight = (
            current_weight +
            (monthly_change * months)
        )

        # Prevent negative weight
        predicted_weight = max(predicted_weight, 1)

        # Calculate predicted BMI
        predicted_bmi = (
            predicted_weight /
            (height_m * height_m)
        )

        # --------------------------------------------------
        # Workout progression
        # --------------------------------------------------

        if activity_level == "sedentary":
            if months >= 6:
                workout_level = "Beginner"
            else:
                workout_level = "Beginner"

        elif activity_level == "light":
            if months >= 6:
                workout_level = "Intermediate"
            else:
                workout_level = "Beginner"

        elif activity_level == "moderate":
            if months >= 6:
                workout_level = "Intermediate"
            else:
                workout_level = "Beginner"

        elif activity_level == "active":
            if months >= 6:
                workout_level = "Advanced"
            else:
                workout_level = "Intermediate"

        else:
            workout_level = "Intermediate"

        # --------------------------------------------------
        # Diet changes
        # --------------------------------------------------

        if "gain" in fitness_goal:

            if months <= 1:
                diet_focus = (
                    "Slight calorie surplus + "
                    "protein-rich foods"
                )

            elif months <= 3:
                diet_focus = (
                    "Increased calories + "
                    "high-protein meals"
                )

            elif months <= 6:
                diet_focus = (
                    "Balanced calorie surplus + "
                    "adequate protein"
                )

            else:
                diet_focus = (
                    "Maintenance/progression diet + "
                    "adequate protein"
                )

        elif "loss" in fitness_goal or "lose" in fitness_goal:

            if months <= 1:
                diet_focus = (
                    "Controlled calories + "
                    "vegetables + protein"
                )

            elif months <= 3:
                diet_focus = (
                    "Moderate calorie deficit + "
                    "high-protein meals"
                )

            elif months <= 6:
                diet_focus = (
                    "Balanced calorie deficit + "
                    "nutrient-rich foods"
                )

            else:
                diet_focus = (
                    "Balanced maintenance diet + "
                    "portion control"
                )

        else:

            diet_focus = (
                "Balanced diet + adequate "
                "protein and nutrients"
            )

        # Add prediction
        predictions.append({
            "period": period_name,
            "months": months,
            "weight": round(predicted_weight, 1),
            "bmi": round(predicted_bmi, 1),
            "workout_level": workout_level,
            "diet_focus": diet_focus
        })

    return render_template(
        "future_prediction.html",
        profile=profile,
        current_weight=round(current_weight, 1),
        current_bmi=round(current_bmi, 1),
        predictions=predictions
    )
# ----------------------------------------------------
# Standalone AJAX BMI Calculator
# ----------------------------------------------------

@app.route("/api/calculate-bmi", methods=["POST"])
def api_calculate_bmi():
    data = request.get_json() or {}
    weight = float(data.get("weight", 0))
    height = float(data.get("height", 0))

    if height <= 0 or weight <= 0:
        return jsonify({"status": "error", "message": "Invalid height or weight values."}), 400

    bmi, category, color, description = ml_engine.calculate_bmi(weight, height)
    min_ideal, max_ideal = ml_engine.calculate_ideal_weight_range(height)

    return jsonify({
        "status": "success",
        "bmi": bmi,
        "category": category,
        "color": color,
        "description": description,
        "ideal_range": f"{min_ideal} kg - {max_ideal} kg"
    })
@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():

    response = ""

    if request.method == 'POST':
        question = request.form.get('question', '').strip()

        if question:
            response = get_chatbot_response(question)
        else:
            response = "Please enter a question."

    return render_template(
        'chatbot.html',
        response=response
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
