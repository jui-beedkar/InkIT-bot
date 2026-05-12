def detect_intent(query):
    q = query.lower().strip()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "welcome"]
    thanks = ["thanks", "thank you", "thx", "appreciate it"]
    bye = ["bye", "goodbye", "see you", "take care"]
    small_talk = ["how are you", "how's it going", "what's up", "nice to meet you"]

    if any(word in q for word in greetings):
        return "greeting"

    if any(word in q for word in thanks):
        return "thanks"

    if any(word in q for word in bye):
        return "bye"

    if any(word in q for word in small_talk):
        return "small_talk"

    return "query"
