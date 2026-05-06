import functools
import logging
import time
from openai import OpenAI

from rag.config import (
    OPENROUTER_API_KEY, 
    LLM_PROVIDER, 
    LM_STUDIO_URL, 
    PRIMARY_MODEL, 
    FALLBACK_MODEL
)
from rag.validator import validate_answer

# -----------------------------
# Logging Configuration
# -----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("InkieLLM")

# -----------------------------
# LLM Client Initialization
# -----------------------------
local_client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")
cloud_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# -----------------------------
# System Prompt Template
# -----------------------------
SYSTEM_PROMPT_TEMPLATE = """
You are Inkie, the expert AI assistant for INK IT Solutions. 

PERSONALITY:
- Friendly, professional, and precise.
- Address the user as {user_name}.
- Act like a helpful agent who is happy to assist.

CORE RULES:
1. **Context Usage**: Use the provided Context to answer factual questions about INK IT Solutions.
2. **Social & Casual**: If the user says "hello", "thanks", "how are you", or other small talk, respond warmly and naturally as Inkie. You do NOT need context for these. 
3. **Hierarchy & Lists**: For services/products, use BOLD headers for categories and bullet points for items.
4. **Brevity**: No long paragraphs. Keep factual answers concise.
5. **No Info Fallback**: If a factual question is asked but not in context, say: "I couldn't find specific details on that, {user_name}. Should I connect you with our team?"

MANDATORY FOOTER (Only for factual/service answers):
Visit Official Page: [Source URL from context]

CONTEXT:
{context}
"""

# -----------------------------
# Answer Generator
# -----------------------------

def validate_response(answer):
    if not answer or len(str(answer).strip()) < 5:
        return False
        
    answer_lower = str(answer).lower()
    
    # Factual answers must have a link
    if "visit official page:" in answer_lower:
        return True
        
    # Social answers don't need a link, check for friendly keywords
    social_keywords = ["hello", "welcome", "pleasure", "happy to help", "how can i", "thanks", "thank you", "nice to meet"]
    if any(k in answer_lower for k in social_keywords):
        return True
        
    # Check for the specific fallback message
    return "connect you to our support team" in answer_lower

@functools.lru_cache(maxsize=128)
def generate_answer(query: str, context: str, user_name: str) -> str:
    start_time = time.time()
    logger.info(f"Generating answer for: {query}")
    
    # Safely inject values into template
    system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{user_name}", user_name).replace("{context}", context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query}
    ]

    def call_llm(model_name):
        # Determine primary and secondary clients
        if LLM_PROVIDER == "lm-studio":
            primary_client, primary_name = local_client, "LM Studio"
            secondary_client, secondary_name = cloud_client, "OpenRouter"
        else:
            primary_client, primary_name = cloud_client, "OpenRouter"
            secondary_client, secondary_name = local_client, "LM Studio"

        try:
            logger.info(f"Routing to {primary_name}: {model_name}")
            response = primary_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=350,
                timeout=45.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"{primary_name} failed: {str(e)}")
            if secondary_client:
                try:
                    logger.info(f"Attempting fallback to {secondary_name}...")
                    # If falling back to local, use a generic model name if the specific one isn't loaded
                    fallback_model = model_name if secondary_name == "OpenRouter" else "local-model"
                    response = secondary_client.chat.completions.create(
                        model=fallback_model,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=350,
                        timeout=45.0
                    )
                    return response.choices[0].message.content.strip()
                except Exception as e2:
                    logger.error(f"{secondary_name} also failed: {str(e2)}")
                    raise e2

    # Attempt 1: Primary Model
    try:
        answer = call_llm(PRIMARY_MODEL)
        # Use both the mandatory link check and the semantic validator
        if validate_response(answer) and validate_answer(answer):
            logger.info(f"Success with {PRIMARY_MODEL} in {time.time() - start_time:.2f}s")
            return answer
        logger.warning(f"Validation failed for {PRIMARY_MODEL}. Content: {answer[:100]}...")
    except Exception as e:
        # This error is caught here and logged to the terminal, which is why it doesn't appear in the chat.
        # We catch it to allow the fallback model to attempt a response.
        logger.error(f"PRIMARY MODEL ERROR ({PRIMARY_MODEL}): {str(e)}")

    # Attempt 2: Fallback Model
    try:
        answer = call_llm(FALLBACK_MODEL)
        logger.info(f"Success with fallback {FALLBACK_MODEL} in {time.time() - start_time:.2f}s")
        return answer
    except Exception as e:
        # Final catch-all error. We log the raw error (e.g., 404, 401) to terminal
        # but return a safe, user-friendly message to the chat interface.
        logger.error(f"CRITICAL LLM FAILURE: Fallback {FALLBACK_MODEL} also failed. Error: {str(e)}")
        return f"I'm sorry, {user_name}, I encountered a technical issue with my AI engine. Please try again in a moment or contact our support team at https://www.inkitsolutions.com.au/contact-us"
