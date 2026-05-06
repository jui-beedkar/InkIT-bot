import os
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

# Load environment variables
if env_path.exists():
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = "inkit-knowledge"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1")
if LM_STUDIO_URL and not LM_STUDIO_URL.endswith("/v1"):
    LM_STUDIO_URL = LM_STUDIO_URL.rstrip("/") + "/v1"
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "google/gemma-2-9b-it:free")
