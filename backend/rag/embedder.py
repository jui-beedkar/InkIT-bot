import json
import os
import logging
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from rag.config import PINECONE_API_KEY, PINECONE_INDEX

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Embedder")

# -----------------------------
# Initialize Pinecone
# -----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# -----------------------------
# Load Embedding Model
# -----------------------------
logger.info("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

def load_website_data():
    """
    Loads data exclusively from the website crawler output.
    As per mentor instructions: only scrape website text for Pinecone.
    """
    documents = []
    
    # Path to website crawler output
    data_path = os.path.join("data", "website_data.json")
    
    if not os.path.exists(data_path):
        logger.error(f"Critical Error: {data_path} not found. Please run the crawler first.")
        return []

    with open(data_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    
    logger.info(f"Loaded {len(documents)} chunks from {data_path}")
    return documents

def run_embedding():
    documents = load_website_data()
    if not documents:
        return

    vectors = []
    logger.info(f"Processing {len(documents)} documents for Pinecone...")

    for doc in documents:
        content = doc.get("content", "").strip()
        if not content:
            continue
            
        # Use content for embedding
        embedding = model.encode(content).tolist()

        vectors.append({
            "id": doc.get("id", os.urandom(4).hex()),
            "values": embedding,
            "metadata": {
                "content": content,
                "url": doc.get("url", "https://www.inkitsolutions.com.au/"),
                "title": doc.get("title", "INK IT Solutions"),
                "category": doc.get("category", "general")
            }
        })

    # -----------------------------
    # Upload to Pinecone
    # -----------------------------
    logger.info(f"Uploading {len(vectors)} vectors to index '{PINECONE_INDEX}'...")

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i : i + batch_size]
        index.upsert(vectors=batch)
        logger.info(f"Uploaded batch {i // batch_size + 1}")

    logger.info("Sync complete. Pinecone is now up-to-date with website content.")

if __name__ == "__main__":
    run_embedding()