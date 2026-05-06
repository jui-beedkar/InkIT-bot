import functools
from langdetect import detect

@functools.lru_cache(maxsize=256)
def detect_language(text):

    try:
        return detect(text)

    except:
        return "en"