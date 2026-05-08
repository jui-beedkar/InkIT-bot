import os
import re

css_path = r'f:\bot-inkIT-RAG\frontend\dist\assets\src-DEuAi6BJ.css'

if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Replace the media query wrapper with a dummy or just remove it
    # We look for @media (prefers-color-scheme:dark){...}
    # Since it's minified, we need to be careful.
    
    # Let's try to find the start and end of the media query block
    start_tag = '@media (prefers-color-scheme:dark){'
    if start_tag in content:
        start_idx = content.find(start_tag)
        # Find the matching closing brace. Since it's minified, it might be tricky.
        # But usually Tailwind puts it at the end of a block.
        # Let's find the first '}' after the start_tag that is NOT followed by a class.
        # Or better, just replace the tag and the corresponding closing brace.
        
        # Actually, let's just replace '.dark\:' with '.dark .dark\:' globally.
        # This works regardless of the media query if we also fix the media query.
        
        # Replace .dark\: with .dark .dark\: (escaping the colon)
        # In CSS minified, it's often .dark\:
        new_content = content.replace('.dark\\:', '.dark .dark\\:')
        
        # Now remove the media query wrapper but keep the contents
        new_content = new_content.replace(start_tag, '')
        # We need to find the trailing } of that block.
        # Tailwind v4 output seems to have it at the end of the dark section.
        # Let's look for the } before "@property" or similar, or just the last one.
        
        # A safer way: replace @media (prefers-color-scheme:dark){ with nothing,
        # and then find the next } that closes it.
        # But wait, if we keep the media query, it still works if the system is dark.
        # If we want it to work ALWAYS, we must remove it.
        
        # Let's just use a simpler approach: 
        # Replace '@media (prefers-color-scheme:dark){' with '@layer darkmode {'
        # And then replace '.dark\\:' with '.dark .dark\\:'
        new_content = content.replace('@media (prefers-color-scheme:dark){', '@layer darkmode {')
        new_content = new_content.replace('.dark\\:', '.dark .dark\\:')
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("CSS Patched successfully")
    else:
        print("Media query not found")
else:
    print("CSS file not found")
