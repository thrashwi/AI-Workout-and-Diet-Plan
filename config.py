import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ai-workout-diet-super-secret-key-2025")
    DATABASE_PATH = os.path.join(BASE_DIR, "data", "fitness.db")
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODEL_PATH = os.path.join(BASE_DIR, "data", "recommendation_models.pkl")
    DATASET_PATH = os.path.join(BASE_DIR, "data", "fitness_dataset.csv")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    PORT = int(os.environ.get("PORT", 5000))
