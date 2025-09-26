import os
from dotenv import load_dotenv

load_dotenv()

# Persisted Chroma path
VECTOR_DB_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "vector_db")
)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)
