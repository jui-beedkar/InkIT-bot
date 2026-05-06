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