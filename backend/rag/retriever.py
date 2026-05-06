import functools
import logging
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from rag.web_retriever import search_website
from rag.config import PINECONE_API_KEY, PINECONE_INDEX

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Retriever")

# -----------------------------
# Pinecone Connection
# -----------------------------
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

# -----------------------------
# Embedding Model
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

def normalize_query(query):
    return query.lower().strip().replace(".", "").replace("?", "")

# -----------------------------
# Pinecone Retrieval
# -----------------------------
@functools.lru_cache(maxsize=128)
def retrieve_documents(query):
    query = normalize_query(query)
    logger.info(f"Retrieving from Vector DB for: {query}")

    embedding = model.encode(query).tolist()

    results = index.query(
        vector=embedding,
        top_k=10,
        include_metadata=True
    )

    matches = []
    for match in results["matches"]:
        score = match.get("score", 0)
        metadata = match.get("metadata", {})
        
        if not metadata:
            continue

        content = metadata.get("content", "").strip()
        url = metadata.get("url", "").strip()
        title = metadata.get("title", "INK IT Solutions").strip()

        # Threshold calibrated for website content (0.38 is good for granular chunks)
        if content and url and score >= 0.38:
            matches.append({
                "content": content,
                "url": url,
                "title": title,
                "score": score
            })
            logger.info(f"Vector Match (Score: {score:.2f}): {title}")

    return matches

# -----------------------------
# Hybrid Retrieval (Self-Healing)
# -----------------------------
def retrieve(query):
    """
    Self-healing retrieval pipeline:
    1. Check Pinecone (Static indexed content)
    2. Fallback to live web search (Dynamic dynamic content)
    """
    # 1. Try Pinecone first (fastest)
    results = retrieve_documents(query)
    if results:
        return results

    # 2. Fallback to Web Search (Self-healing logic)
    logger.info("No relevant content in Vector DB. Initiating LIVE website search (Self-Healing)...")
    web_results = search_website(query)
    if web_results:
        logger.info(f"Found {len(web_results)} results live from website.")
        return web_results

    # 3. Final Fallback if everything fails
    return []