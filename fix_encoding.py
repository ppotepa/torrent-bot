import os
with open('plugins/downloads.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Remove any problematic characters and normalize
content = content.encode('ascii', errors='ignore').decode('ascii')

with open('plugins/downloads.py', 'w', encoding='ascii') as f:
    f.write(content)

print("Fixed encoding issues in downloads.py")
