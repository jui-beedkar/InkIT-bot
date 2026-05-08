import os

file_path = r'f:\bot-inkIT-RAG\frontend\dist\assets\src-ZdJW9-T4.js'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

index = content.find('139.84.194.96')
if index != -1:
    print(f"Found at index {index}")
    print("Context:", content[index-20:index+30])
else:
    print("Not found")
