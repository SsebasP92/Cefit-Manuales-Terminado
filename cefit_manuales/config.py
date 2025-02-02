import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cefit_manuales")

MANUAL_UPLOAD_FOLDER = os.getenv("MANUAL_UPLOAD_FOLDER", "manuales")
