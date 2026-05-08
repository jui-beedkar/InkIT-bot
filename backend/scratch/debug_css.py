with open(r'f:\bot-inkIT-RAG\frontend\dist\assets\src-DEuAi6BJ.css', 'r') as f:
    content = f.read()
    print("Content around rgba:")
    idx = content.find('rgba')
    while idx != -1:
        print(content[idx:idx+30])
        idx = content.find('rgba', idx+1)
