import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.retriever import retrieve
from rag.llm import generate_answer

def test_rag_pipeline(query, user_name="TestUser"):
    print(f"\n--- Testing Query: {query} ---")
    
    # 1. Retrieval
    print("Step 1: Retrieving context...")
    matches = retrieve(query)
    
    if not matches:
        print("No matches found.")
        return

    print(f"Found {len(matches)} matches.")
    
    # 2. Build Context
    context_parts = []
    for m in matches:
        print(f"- Match: {m.get('title')} (Score: {m.get('score', 'N/A')})")
        part = f"Source Title: {m.get('title')}\nSource URL: {m.get('url')}\nContent: {m['content']}"
        context_parts.append(part)
    
    context = "\n\n---\n\n".join(context_parts)

    # 3. Generation
    print("\nStep 2: Generating answer...")
    answer = generate_answer(query, context, user_name)
    
    print("\n--- FINAL ANSWER ---")
    print(answer)
    print("--------------------")

if __name__ == "__main__":
    # Test cases
    test_rag_pipeline("Who is INK IT Solutions?")
    test_rag_pipeline("What SAP services do you provide?")
    test_rag_pipeline("Where are your offices located?")
    test_rag_pipeline("How do I contact support?")
