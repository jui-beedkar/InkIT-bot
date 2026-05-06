import logging
import functools
from deep_translator import GoogleTranslator

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("InkieTranslator")

@functools.lru_cache(maxsize=256)
def translate_to_english(text):
    if not text:
        return text
    try:
        translator = GoogleTranslator(source='auto', target='en')
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation to English failed: {e}")
        return text

@functools.lru_cache(maxsize=256)
def translate_to_user_language(text, language):
    if not text or language == "en":
        return text
    try:
        # Some language codes might differ slightly, deep_translator handles most ISO codes
        translator = GoogleTranslator(source='en', target=language)
        return translator.translate(text)
    except Exception as e:
        logger.error(f"Translation from English failed: {e}")
        return text

# Legacy functions for compatibility with main.py aliases
def to_english(text):
    return translate_to_english(text)

def from_english(text, target):
    return translate_to_user_language(text, target)

