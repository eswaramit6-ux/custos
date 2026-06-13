content = open('app.py', encoding='utf-8').read()

old = '''    # API Key
    st.markdown("#### 🔑 API Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Your Gemini API key for AI-powered features"
    )
    if api_key:
        st.session_state['api_key'] = api_key
        st'''

new = '''    # API Key loaded silently from secrets
    try:
        st.session_state['api_key'] = st.secrets["GEMINI_API_KEY"]
    except:
        pass
    st'''

content = content.replace(old, new, 1)
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! API key hidden successfully.')
