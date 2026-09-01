import os
import re

for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find openDetail('module', {{d.id}}) and add quotes around {{d.id}}
            new_content = re.sub(r"openDetail\('([^']+)',\s*\{\{d\.([^\}]+)\}\}\)", r"openDetail('\1', '{{d.\2}}')", content)
            
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
print('Fixed quotes in openDetail')
