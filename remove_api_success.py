content = open('app.py', encoding='utf-8').read()

old = '''    st.success("API Key saved ✓")

    st.divider()

    # Monthly Income'''

new = '''    # Monthly Income'''

content = content.replace(old, new, 1)
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! API Key saved button removed.')
