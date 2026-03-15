content = open('app.py', encoding='utf-8').read()

old = '''    # Get API key from secrets or sidebar
    splitwise_key = st.secrets.get("SPLITWISE_API_KEY", "") if hasattr(st, 'secrets') else ""
    
    if not splitwise_key:
        splitwise_key = st.text_input("Enter Splitwise API Key", type="password", 
                                       placeholder="Your Splitwise API key...")'''

new = '''    # Get Splitwise API key
    splitwise_key = ""
    try:
        splitwise_key = st.secrets["SPLITWISE_API_KEY"]
    except:
        pass
    
    if not splitwise_key:
        splitwise_key = st.text_input(
            "Enter Splitwise API Key",
            type="password",
            placeholder="Paste your Splitwise API key here...",
            help="Get your key from splitwise.com/apps"
        )'''

content = content.replace(old, new, 1)
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! Splitwise key fix applied.')
