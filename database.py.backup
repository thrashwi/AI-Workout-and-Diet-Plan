import os
import sqlite3
from config import Config


class RowDict(dict):
    """Allows both row['username'] and row.username access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"'RowDict' object has no attribute '{name}'"
            )

    def __setattr__(self, name, value):
        self[name] = value


def row_dict_factory(cursor, row):
    d = RowDict()

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


def get_db_connection():
    """Create and return a SQLite database connection."""

    os.makedirs(Config.DATA_DIR, exist_ok=True)

    conn = sqlite3.connect(Config.DATABASE_PATH)

    conn.row_factory = row_dict_factory

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# Keep this name also because app.py may use get_db()
def get_db():
    return get_db_connection()


def init_db():
    """Create database tables if they do not already exist."""

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        age INTEGER,
        gender TEXT DEFAULT 'male',
        height_cm REAL,
        weight_kg REAL,
        target_weight_kg REAL,
        fitness_goal TEXT DEFAULT 'general_fitness',
        activity_level TEXT DEFAULT 'moderate',
        exercise_frequency TEXT DEFAULT '3-4',
        dietary_preference TEXT DEFAULT 'standard',
        health_conditions TEXT DEFAULT '',
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        bmi REAL,
        bmi_category TEXT,
        bmr REAL,
        tdee REAL,
        target_calories REAL,
        protein_g REAL,
        carbs_g REAL,
        fat_g REAL,
        workout_plan TEXT,
        diet_plan TEXT,
        water_intake_liters REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS progress_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        log_date TEXT NOT NULL,
        weight_kg REAL,
        bmi REAL,
        workouts_completed INTEGER DEFAULT 0,
        calories_burned REAL DEFAULT 0,
        water_ml REAL DEFAULT 0,
        chest_cm REAL,
        waist_cm REAL,
        hips_cm REAL,
        notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        reminder_type TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        days_of_week TEXT DEFAULT 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
        is_active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS gym_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        gym_name TEXT NOT NULL,
        address TEXT,
        latitude REAL,
        longitude REAL,
        rating REAL DEFAULT 4.5,
        phone TEXT,
        website TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def query_db(query, args=(), one=False):
    """Run SELECT queries."""

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(query, args)

    rows = cur.fetchall()

    conn.close()

    if one:
        return rows[0] if rows else None

    return rows


def execute_db(query, args=(), commit=True):
    """Run INSERT, UPDATE or DELETE queries."""

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute(query, args)

    last_id = cur.lastrowid

    if commit:
        conn.commit()

    conn.close()

    return last_id