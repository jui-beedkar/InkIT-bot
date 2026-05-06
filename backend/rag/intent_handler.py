def detect_intent(query):
    q = query.lower().strip()

    greetings = ["hi", "hello", "hey"]
    thanks = ["thanks", "thank you"]
    bye = ["bye", "goodbye"]
    small_talk = ["how are you"]

    if any(word in q for word in greetings):
        return "greeting"

    if any(word in q for word in thanks):
        return "thanks"

    if any(word in q for word in bye):
        return "bye"

    if any(word in q for word in small_talk):
        return "small_talk"

    return "query"
