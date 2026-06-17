import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
DATABASE_FILENAME = os.environ.get("ECOGUIDE_DATABASE", "carbon.db")
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
