import os
import json
import pytest
import sqlite3

# Configure test environment
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["FLASK_DEBUG"] = "False"

import app as flask_app
import database
import ml_engine

@pytest.fixture
def client(tmp_path):
    # Use temporary test database
    test_db = tmp_path / "test_fitness.db"
    database.Config.DATABASE_PATH = str(test_db)
    database.Config.DATA_DIR = str(tmp_path)
    flask_app.app.config["TESTING"] = True
    flask_app.app.config["WTF_CSRF_ENABLED"] = False

    with flask_app.app.app_context():
        database.init_db()

    with flask_app.app.test_client() as client:
        yield client


# ==========================================
# 1. ML & NUTRITION ENGINE TESTS
# ==========================================

def test_bmi_calculation_categories():
    # Normal weight
    bmi, cat, color, _ = ml_engine.calculate_bmi(70, 175)
    assert bmi == 22.9
    assert cat == "Normal Weight"
    assert color == "success"

    # Underweight
    bmi, cat, color, _ = ml_engine.calculate_bmi(45, 175)
    assert bmi == 14.7
    assert cat == "Underweight"

    # Overweight
    bmi, cat, color, _ = ml_engine.calculate_bmi(85, 175)
    assert bmi == 27.8
    assert cat == "Overweight"

    # Obese Class I
    bmi, cat, color, _ = ml_engine.calculate_bmi(98, 175)
    assert bmi == 32.0
    assert "Obesity" in cat

    # Edge cases
    bmi, cat, _, _ = ml_engine.calculate_bmi(0, 175)
    assert bmi == 0
    bmi, cat, _, _ = ml_engine.calculate_bmi(70, 0)
    assert bmi == 0


def test_bmr_and_tdee_calculations():
    # Male: 10*80 + 6.25*180 - 5*25 + 5 = 800 + 1125 - 125 + 5 = 1805
    bmr_male = ml_engine.calculate_bmr(80, 180, 25, "male")
    assert bmr_male == 1805.0

    # Female: 10*60 + 6.25*165 - 5*30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25 -> 1320
    bmr_female = ml_engine.calculate_bmr(60, 165, 30, "female")
    assert abs(bmr_female - 1320.0) <= 2.0

    # TDEE
    tdee_moderate = ml_engine.calculate_tdee(2000, "moderate")
    assert tdee_moderate == 3100.0


def test_ideal_weight_range():
    min_w, max_w = ml_engine.calculate_ideal_weight_range(180)
    # 18.5 * 1.8^2 = 59.94 -> 59.9, 24.9 * 1.8^2 = 80.676 -> 80.7
    assert 58.0 <= min_w <= 62.0
    assert 78.0 <= max_w <= 82.0


def test_ai_workout_generation():
    profile = {
        "fitness_goal": "muscle_building",
        "activity_level": "very_active",
        "exercise_frequency": "5-6",
        "gender": "male",
        "age": 24,
        "weight_kg": 78,
        "height_cm": 182
    }
    plan = ml_engine.generate_ai_workout_plan(profile)
    assert "split_name" in plan
    assert "days" in plan
    assert len(plan["days"]) == 7
    assert any(len(d["exercises"]) > 0 for d in plan["days"])


def test_sqlite_row_and_rowdict_compatibility():
    # Test with real sqlite3.Row object
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("CREATE TABLE t (fitness_goal TEXT, activity_level TEXT, exercise_frequency TEXT, gender TEXT, age INT, weight_kg REAL, height_cm REAL, dietary_preference TEXT)")
    cur.execute("INSERT INTO t VALUES ('muscle_building', 'moderate', '3-4', 'male', 25, 75.0, 175.0, 'standard')")
    row = cur.fetchone()
    conn.close()

    # Must not raise AttributeError: 'sqlite3.Row' object has no attribute 'get'
    w_plan = ml_engine.generate_ai_workout_plan(row)
    assert "split_name" in w_plan
    d_plan = ml_engine.generate_ai_diet_plan(row)
    assert "target_calories" in d_plan

    # Test RowDict
    rd = database.RowDict({"fitness_goal": "weight_loss", "weight_kg": 80.0, "height_cm": 180.0})
    assert rd.get("fitness_goal") == "weight_loss"
    assert rd.fitness_goal == "weight_loss"
    assert rd["fitness_goal"] == "weight_loss"



def test_ai_diet_generation_all_preferences():
    preferences = ["standard", "vegetarian", "vegan", "keto", "high_protein"]
    for pref in preferences:
        profile = {
            "age": 28,
            "gender": "male",
            "height_cm": 178,
            "weight_kg": 75,
            "fitness_goal": "weight_loss",
            "activity_level": "moderate",
            "dietary_preference": pref
        }
        diet = ml_engine.generate_ai_diet_plan(profile)
        assert diet["target_calories"] > 1200
        assert "macronutrients" in diet
        assert diet["macronutrients"]["protein_g"] > 0
        assert len(diet["days"]) == 7
        assert "Breakfast (08:00 AM)" in diet["days"][0]["meals"]


# ==========================================
# 2. FLASK ROUTES & APPLICATION TESTS
# ==========================================

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"AI-Workout & Diet Plans" in response.data


def test_api_bmi_calculator(client):
    res = client.post("/api/calculate-bmi", json={"height": 180, "weight": 75})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["bmi"] == 23.1
    assert data["category"] == "Normal Weight"


def test_registration_and_login_flow(client):
    # Register new user
    res = client.post("/register", data={
        "username": "fituser1",
        "email": "fituser1@example.com",
        "full_name": "Fitness Enthusiast",
        "password": "password123",
        "confirm_password": "password123"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Fitness Profile & Body Metrics" in response_text(res)

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert b"signed out successfully" in response_text(res)

    # Login
    res = client.post("/login", data={
        "username": "fituser1",
        "password": "password123"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Fitness Profile & Body Metrics" in response_text(res)


def test_profile_update_and_dashboard_render(client):
    # Register & login
    client.post("/register", data={
        "username": "fituser2",
        "email": "fituser2@example.com",
        "full_name": "Jane Doe",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Update profile
    res = client.post("/profile", data={
        "full_name": "Jane Doe",
        "age": "26",
        "gender": "female",
        "height_cm": "168",
        "weight_kg": "62",
        "target_weight_kg": "58",
        "fitness_goal": "weight_loss",
        "activity_level": "moderate",
        "exercise_frequency": "3-4",
        "dietary_preference": "vegetarian",
        "health_conditions": "None"
    }, follow_redirects=True)
    assert res.status_code == 200
    content = response_text(res)
    assert "Fitness Streak" in content or "Dashboard" in content

    # Check Recommendations Page
    res_rec = client.get("/recommendations")
    assert res_rec.status_code == 200
    rec_text = response_text(res_rec)
    assert "AI Workout Routine" in rec_text
    assert "AI Diet & Nutrition" in rec_text


def test_video_library_filtering(client):
    # Register & login
    client.post("/register", data={
        "username": "fituser3",
        "email": "fituser3@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })

    # All videos
    res = client.get("/videos")
    assert res.status_code == 200
    assert b"Barbell Squat" in res.data

    # Filter workout
    res_workout = client.get("/videos?category=workout")
    assert res_workout.status_code == 200
    assert b"Bench Press" in res_workout.data

    # Filter diet
    res_diet = client.get("/videos?category=diet")
    assert res_diet.status_code == 200
    assert b"High-Protein Meal Prep" in res_diet.data


def test_gym_search_and_favorite_api(client):
    # Register & login
    client.post("/register", data={
        "username": "fituser4",
        "email": "fituser4@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Search gyms API
    res = client.get("/api/gyms/search?lat=40.7128&lng=-74.0060")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["gyms"]) > 0

    # Add favorite
    fav_res = client.post("/api/gyms/favorite", json={
        "gym_name": "Gold's Gym - Elite Fitness Hub",
        "address": "452 Metropolitan Ave",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "rating": 4.8
    })
    fav_data = fav_res.get_json()
    assert fav_data["status"] == "saved"

    # Remove favorite
    fav_remove = client.post("/api/gyms/favorite", json={
        "gym_name": "Gold's Gym - Elite Fitness Hub"
    })
    assert fav_remove.get_json()["status"] == "removed"


def test_progress_tracking_and_water_logger(client):
    client.post("/register", data={
        "username": "fituser5",
        "email": "fituser5@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    # Set profile
    client.post("/profile", data={
        "age": "30", "gender": "male", "height_cm": "180", "weight_kg": "80",
        "target_weight_kg": "75", "fitness_goal": "weight_loss", "activity_level": "moderate",
        "exercise_frequency": "3-4", "dietary_preference": "standard"
    })

    # Post progress log
    res = client.post("/progress", data={
        "log_date": "2025-01-15",
        "weight_kg": "79.5",
        "workouts_completed": "1",
        "calories_burned": "500",
        "water_ml": "2500",
        "chest_cm": "102",
        "waist_cm": "86",
        "notes": "Good workout"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert "79.5 kg" in response_text(res)

    # Quick water intake API
    water_res = client.post("/api/progress/quick-water", json={"amount_ml": 500})
    assert water_res.status_code == 200
    assert water_res.get_json()["status"] == "success"

    # Stats endpoint for Chart.js
    stats_res = client.get("/api/progress/stats")
    stats_data = stats_res.get_json()
    assert stats_data["status"] == "success"
    assert len(stats_data["weights"]) >= 1


def test_reminders_system(client):
    client.post("/register", data={
        "username": "fituser6",
        "email": "fituser6@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })

    # Add reminder
    res = client.post("/reminders", data={
        "title": "Evening Protein Shake",
        "reminder_type": "meal",
        "reminder_time": "18:00",
        "days_of_week": "Mon,Tue,Wed,Thu,Fri"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert "Evening Protein Shake" in response_text(res)

    # Fetch active reminders API
    active_res = client.get("/api/reminders/active")
    active_data = active_res.get_json()
    assert active_data["status"] == "success"
    assert len(active_data["reminders"]) >= 1


def response_text(res):
    return res.data.decode("utf-8")
