import re
import logging
from typing import List, Optional

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# RAG modules
from rag.language_detector import detect_language

from rag.translator import (
    translate_to_english,
    translate_to_user_language
)

from rag.retriever import retrieve
from rag.llm import generate_answer, validate_response
from rag.validator import validate_answer
from rag.intent_handler import detect_intent
from rag.persona import persona_responses

# --------------------------------------------------
# LOGGING
# --------------------------------------------------
session = {
    "name": None,
    "country": None,
    "language": None
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InkieAPI")

# --------------------------------------------------
# FASTAPI APP
# --------------------------------------------------

app = FastAPI(
    title="Inkie RAG API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ROOT CHECK
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Inkie API is running"
    }

@app.get(
    "/favicon.ico",
    include_in_schema=False
)
async def favicon():
    return Response(status_code=204)

# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ChatRequest(BaseModel):

    message: str

    user_name: Optional[str] = None

    user_country: Optional[str] = None

    language: Optional[str] = "en"

    stage: Optional[str] = "ask_name"

    last_doc_url: Optional[str] = None

# --------------------------------------------------
# RESPONSE MODEL
# --------------------------------------------------

class ChatResponse(BaseModel):

    response: str

    answer: Optional[str] = ""

    suggestions: List[str] = []

    type: str = "text"

    link: Optional[str] = None
    stage: Optional[str] = "chat"

    url: Optional[str] = None

    title: Optional[str] = None

    updated_name: Optional[str] = None

    updated_country: Optional[str] = None

    updated_language: Optional[str] = None

    updated_stage: Optional[str] = None

    last_doc_url: Optional[str] = None

# --------------------------------------------------
# NAME VALIDATION
# --------------------------------------------------

INVALID_NAMES = [
    "yes",
    "no",
    "what",
    "ok",
    "hello",
    "hey",
    "hi",
    "test",
    "didnt",
    "understand",
    "123"
]

def is_valid_name(text: str):

    text = text.strip().lower()

    if len(text) < 2:
        return False

    if text in INVALID_NAMES:
        return False

    # Contain letters, spaces, and basic punctuation
    if not re.search(
        r'^[a-zA-Z\s.,!\'?]+$',
        text
    ):
        return False
    
    # Not contain numbers (already covered by letters only regex, but good to be explicit)
    if any(char.isdigit() for char in text):
        return False

    return True

# --------------------------------------------------
# NAME EXTRACTION
# --------------------------------------------------

def extract_name(text: str):

    patterns = [

        r"(?:my name is|i am|this is|call me|i'm)\s+([a-zA-Z\s]+)",

        r"^(?:hello|hi|hey)?\s*([a-zA-Z\s]+)$"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            candidate = match.group(1).strip()

            if is_valid_name(candidate):

                return candidate.title()

    words = text.strip().split()

    if words:

        last_word = words[-1]

        if is_valid_name(last_word):

            return last_word.title()

    return text.strip().title()

# --------------------------------------------------
# MAIN CHAT ENDPOINT
# --------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(request: ChatRequest):

    msg_raw = request.message.strip()
    msg_lower = msg_raw.lower()

    stage = request.stage or "ask_name"
    user_lang = request.language or "en"
    user_name = request.user_name or "User"
    
    GREETINGS = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    SHORT_MESSAGES = ["hey", "hi", "ok", "yes", "no", "what", "test", "123"]

    # --------------------------------------------------
    # STAGE 1 — ASK NAME
    # --------------------------------------------------

    if stage == "ask_name":
        
        if msg_lower in GREETINGS:
            greeting_msg = (
                "Hello! I'm Inkie, your virtual assistant from INK IT Solutions.\n"
                "May I please know your name so I can assist you better?"
            )
            return ChatResponse(
                response=greeting_msg,
                answer=greeting_msg,
                updated_stage="ask_name",
                updated_name=None,
                updated_country=None,
                updated_language="en"
            )

        if msg_lower in SHORT_MESSAGES:
            retry_msg = "May I please know your name so I can assist you better?"
            return ChatResponse(
                response=retry_msg,
                answer=retry_msg,
                updated_stage="ask_name"
            )

        # If it's a very long greeting or doesn't look like a name, ask again
        if not is_valid_name(msg_raw) or len(msg_raw) > 50:
             retry_msg = "I'm sorry, I didn't catch that. May I please know your name?"
             return ChatResponse(
                response=retry_msg,
                answer=retry_msg,
                updated_stage="ask_name"
            )

        name = extract_name(msg_raw)

        res = (
            f"Thank you, {name}. Which country are you connecting from today?"
        )

        return ChatResponse(
            response=res,
            answer=res,
            updated_name=name,
            updated_stage="ask_country"
        )

    # --------------------------------------------------
    # STAGE 2 — ASK COUNTRY
    # --------------------------------------------------

    if stage == "ask_country":

        country = msg_raw.strip().title()

        res = (
            f"Great, {user_name}. Which language would you prefer to communicate in?"
        )

        return ChatResponse(
            response=res,
            answer=res,
            suggestions=[
                "English",
                "Arabic",
                "French",
                "Spanish",
                "German"
            ],
            updated_country=country,
            updated_stage="ask_language"
        )

    # --------------------------------------------------
    # STAGE 3 — ASK LANGUAGE
    # --------------------------------------------------

    if stage == "ask_language":

        lang_map = {

            "english": "en",
            "arabic": "ar",
            "french": "fr",
            "spanish": "es",
            "german": "de"

        }

        chosen = msg_raw.lower()

        lang_code = "en"

        for k, v in lang_map.items():

            if k in chosen:

                lang_code = v

                break

        res = (
            f"Great, {user_name}! "
            "How can I assist you today?"
        )

        return ChatResponse(

            response=translate_to_user_language(
                res,
                lang_code
            ),

            answer=res,

            updated_language=lang_code,

            updated_stage="chatting"
        )

    # --------------------------------------------------
    # STAGE 4 — CHATTING (RAG)
    # --------------------------------------------------

    try:
        
        # Check short message rule
        if msg_lower in SHORT_MESSAGES:
            res = f"{user_name}, how can I assist you with INK IT Solutions today?"
            return ChatResponse(
                response=translate_to_user_language(res, user_lang),
                answer=res,
                updated_stage="chatting"
            )

        # Detect language
        detected_language = detect_language(msg_raw)

        # Translate to English
        msg_en = msg_raw
        if user_lang != "en":
            msg_en = translate_to_english(msg_raw)

        # Handle Greetings without retrieval
        if msg_lower in GREETINGS:
            greeting_res = f"Hello, {user_name}! How can I help you with INK IT Solutions today?"
            return ChatResponse(
                response=translate_to_user_language(greeting_res, user_lang),
                answer=greeting_res,
                updated_stage="chatting"
            )

        # Spell correction rule
        spell_corrections = {
            "s4hanaa": "s4hana",
            "clod": "cloud",
            "sappp": "sap"
        }
        
        msg_en_lower = msg_en.lower()
        for wrong, correct in spell_corrections.items():
            if wrong in msg_en_lower:
                msg_en = re.sub(rf'\b{wrong}\b', correct, msg_en, flags=re.IGNORECASE)

        # Keyword Expansion Rule for short inputs
        keyword_expansions = {
            "ink": "company overview and history of INK IT Solutions",
            "sap": "SAP S/4HANA, SAP CX, SuccessFactors, and SAP BTP solutions",
            "hr": "SAP HR Imprint, SuccessFactors, and human resources solutions",
            "services": "IT consulting, implementation, and managed services by INK IT",
            "cloud": "SAP Commerce Cloud, Sales Cloud, Service Cloud, and Oracle Cloud",
            "premium": "premium packaged solutions, HR Imprint, and expert consultations",
            "products": "software products like ChatINK, DocuSign with SAP, and Council Software",
            "chatink": "ChatINK bi-directional messaging for SuccessFactors",
            "council": "INK Council Management Software for smart cities",
            "oracle": "Oracle E-Business Suite, Oracle Cloud, and PeopleSoft services",
            "docusign": "DocuSign eSignature integration with SAP systems"
        }
        
        msg_en_lower = msg_en.strip().lower()

        # STEP 1: Detect Intent (Industry Standard - Social Talk first)
        intent = detect_intent(msg_en_lower)
        if intent != "query":
            persona_answer = persona_responses.get(intent, "I'm here to help! How can I assist you today?")
            return ChatResponse(
                response=translate_to_user_language(persona_answer, user_lang),
                answer=persona_answer,
                suggestions=["List all services", "Tell me about SAP", "Cloud solutions"],
                stage="chat"
            )

        # STEP 2: Keyword Expansion for technical queries
        if len(msg_en_lower.split()) <= 3:
            for keyword, expansion in keyword_expansions.items():
                if keyword in msg_en_lower:
                    msg_en = expansion
                    logger.info(f"Keyword detected: {keyword}. Expanding query to: {msg_en}")
                    break

        logger.info(f"Query in English (technical): {msg_en}")

        # STEP 3: RAG Retrieval
        matches = retrieve(msg_en)
        
        if not matches:
            fallback = f"{user_name}, I couldn't find exact information for that request. Should I connect you with our support team?"
            return ChatResponse(
                response=translate_to_user_language(fallback, user_lang),
                answer=fallback,
                link="https://www.inkitsolutions.com.au/contact-us",
                stage="chat"
            )

        # STEP 4: Build Context and Call LLM
        context = "\n---\n".join([m["content"] for m in matches])
        link = matches[0]["url"]

        # Step 3: Call LLM with Context
        answer = generate_answer(msg_en, context, user_name)
        
        # Final validation
        if not validate_response(answer):
             answer = f"I'm here to help, {user_name}! You can ask me about INK IT's services like SAP, Oracle, or custom development. How can I assist you today?"

        return ChatResponse(
            response=translate_to_user_language(answer, user_lang),
            link=link,
            suggestions=["List all services", "Tell me about SAP", "Cloud solutions"],
            stage="chat"
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return ChatResponse(
            response=f"I'm sorry {user_name}, I encountered a small hiccup. Could you try again?",
            stage="chat"
        )

# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        app,

        host="127.0.0.1",

        port=8000

    )