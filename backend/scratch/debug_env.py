import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
print(f"BASE_DIR: {BASE_DIR}")
print(f"Env path: {env_path}")
print(f"Env exists: {env_path.exists()}")

load_dotenv(env_path)
print(f"PINECONE_API_KEY from env: {os.getenv('PINECONE_API_KEY')}")
