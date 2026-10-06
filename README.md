# AI-Workout and Diet Plan - Web Application

An integrated, web-based fitness and nutrition platform that leverages Machine Learning, physical metabolic calculations (BMI, BMR, TDEE), and sports science to deliver tailored workout routines and diet charts.

---

## 🌟 Key Features

1. **User Authentication & Profiles**
   - Secure account registration with hashed passwords (Werkzeug).
   - Detailed profile management: Age, Gender, Height, Weight, Target Weight, Fitness Goal, Activity Level, Exercise Frequency, Dietary Preference, and Health Considerations.

2. **Accurate BMI & Metabolic Assessment**
   - Instant Metric BMI calculation: \(\text{Weight (kg)} / \text{Height (m)}^2\).
   - Category classification: Underweight, Normal Weight, Overweight, Obesity (Class I, II, III).
   - Ideal healthy weight range calculations.
   - BMR (Basal Metabolic Rate via Mifflin-St Jeor formula) and TDEE (Total Daily Energy Expenditure).

3. **AI & Machine Learning Recommendation Engine**
   - Random Forest classifiers and regressors (Scikit-Learn) trained on fitness parameters to predict split type, intensity, caloric adjustments, and macronutrient targets.
   - **7-Day Workout Routine**: Push/Pull/Legs, Upper/Lower, Full Body, or Fat-Loss HIIT split with target muscles, sets, reps, rest periods, coaching cues, and demo video links.
   - **7-Day Nutrition Plan**: Calorie deficit/surplus targets, protein/carb/fat macro distributions, meal-by-meal timetable (Breakfast, Morning Boost, Lunch, Pre/Post Snack, Dinner) supporting **Standard Omnivore**, **Vegetarian**, **Vegan**, **Keto**, and **High-Protein** diets.

4. **Curated Video Library**
   - Video demonstrations for compound lifts and exercises (Squats, Bench Press, Deadlifts, Push-ups, HIIT, Planks).
   - Healthy food preparation & cooking tutorials (High-protein meal prep, Overnight oats, Crispy tofu stir-fry, Recovery smoothie bowls).
   - Built-in responsive video modal player.

5. **Nearby Gym & Fitness Locator**
   - Interactive **Leaflet.js** map with OpenStreetMap tiles.
   - Geolocation support ("Near Me") with radius visualization.
   - Gym cards with ratings, addresses, distance in kilometers, driving directions, and personal favorites bookmarking.

6. **Progress Tracking & Interactive Charts**
   - Log daily weight, workouts completed, calories burned, water intake, and body measurements (chest, waist, hips).
   - Interactive **Chart.js** charts for Weight vs Goal trajectory and BMI history.
   - Fast "+250ml" quick-water logger directly from the dashboard.

7. **Fitness & Meal Reminder Module**
   - Set customizable schedules for morning workouts, hydration checks, and meal windows.
   - Web Notification API integration for desktop push alerts and in-app toasts.

8. **Export & Print**
   - Dedicated print-optimized view (`/recommendations/print`) to generate clean PDFs or physical printouts of the workout and meal plans.

---

## 🛠️ Technology Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3 (schema with foreign keys and cascades)
- **Machine Learning & Analytics**: Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend**: HTML5, CSS3 (Modern Dark Theme), JavaScript (ES6)
- **Mapping**: Leaflet.js & OpenStreetMap
- **Data Visualizations**: Chart.js
- **Icons & Typography**: FontAwesome 6, Google Fonts (Inter)
- **Testing**: Pytest

---

## 📁 Directory Structure

```
c:\DIET PLAN\
├── app.py                     # Main Flask application entry point & routes
├── config.py                  # App configuration (secret keys, paths)
├── database.py                # Database connection, schemas, and queries
├── ml_engine.py               # ML recommendation models, BMI/BMR/TDEE calculations
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── test_app.py                # Automated unit and integration test suite
├── static/
│   ├── css/
│   │   └── style.css          # Fitness UI stylesheet & print styles
│   └── js/
│       ├── main.js            # Video modal, mobile nav, quick BMI calculator
│       ├── tracker.js         # Progress tracking & Chart.js charts
│       ├── map.js             # Leaflet.js gym search & geolocation
│       └── reminders.js       # Desktop notifications & reminder schedules
└── templates/
    ├── base.html              # Base navigation layout & footer
    ├── index.html             # Landing page with hero & quick BMI tool
    ├── login.html             # Login screen
    ├── register.html          # Registration screen
    ├── profile.html           # Profile & fitness metrics editor
    ├── dashboard.html         # User dashboard with stats & daily plan
    ├── recommendations.html   # Detailed AI Workout & Diet recommendations
    ├── print_plan.html        # Print/PDF-ready fitness blueprint
    ├── videos.html            # Exercise & cooking video library
    ├── gym_search.html        # Interactive Nearby Gym Finder with Leaflet
    ├── progress.html          # Progress tracker with Chart.js charts
    └── reminders.html         # Reminder management & desktop alerts
```

---

## 🚀 How to Run the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Flask Server
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Run Automated Tests
```bash
pytest test_app.py -v
```
