def is_off_topic(query):
    """Detects if the query is in the disallowed topics list."""
    disallowed_keywords = [
        "python", "java", "c++", "javascript", "code", "programming", "coding", "script",
        "math", "solve", "equation", "calculus", "geometry",
        "politics", "election", "government", "policy",
        "weather", "forecast", "temperature",
        "sports", "football", "cricket", "basketball", "score", "match", "winner",
        "entertainment", "movie", "song", "actor", "music", "joke", "tell me a joke",
        "recipe", "cook", "food", "ingredient",
        "religion", "god", "faith", "spiritual",
        "medical", "doctor", "health", "disease", "treatment", "medicine",
        "legal", "lawyer", "law", "attorney", "court",
        "finance", "stock", "invest", "crypto", "trading",
        "school", "homework", "exam", "assignment", "university",
        "interview prep", "career advice", "job interview",
        "general ai", "who are you", "what can you do", "chatgpt"
    ]
    
    query_lower = query.lower().strip()
    
    # Check for direct matches or contains
    for keyword in disallowed_keywords:
        if keyword in query_lower:
            return True
            
    return False

def is_on_topic(query):
    """Checks if the query is related to the whitelist domains."""
    whitelist_keywords = [
        "ink it solutions", "ink it", "inkie",
        "services", "technologies", "solutions", "company", "about us",
        "ai", "artificial intelligence", "chatbot", "automation",
        "cloud", "cybersecurity", "software development", "analytics",
        "digital transformation", "enterprise", "support", "contact",
        "website", "office", "location", "partnership", "certification"
    ]
    
    query_lower = query.lower().strip()
    
    # If the query is a simple greeting or small talk, we handle it in llm.py
    # For factual queries, we check against the whitelist
    for keyword in whitelist_keywords:
        if keyword in query_lower:
            return True
            
    return False

def validate_answer(answer):
    if not answer:
        return False
    
    # Minimum length for a meaningful answer
    if len(answer.strip()) < 15:
        return False
        
    # Check for AI refusal or uncertainty phrases
    refusal_indicators = [
        "i don't know",
        "i'm not sure",
        "i cannot answer",
        "i do not have information",
        "as an ai",
        "unfortunately",
        "i am unable to"
    ]
    
    answer_lower = answer.lower()
    for indicator in refusal_indicators:
        if indicator in answer_lower:
            return False
            
    # Check if it sounds like a placeholder
    if "lorem ipsum" in answer_lower:
        return False
        
    return True