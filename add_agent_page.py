content = open('app.py', encoding='utf-8').read()

# Add import at top
old_import = "from utils.splitwise_integration import"
new_import = "from utils.custos_agent import create_custos_agent, create_knowledge_base, load_pdf_to_retriever\nfrom utils.splitwise_integration import"
content = content.replace(old_import, new_import, 1)

# Add to navigation
old_nav = '"🤝 Splitwise"'
new_nav = '"🤝 Splitwise",\n    "🤖 CUSTOS Agent"'
content = content.replace(old_nav, new_nav, 1)

# Add agent page at end
agent_page = '''

# ═══ CUSTOS AGENT PAGE ════════════════════════════════════════════
elif page == "🤖 CUSTOS Agent":
    st.markdown('<div class="section-header">CUSTOS AI FINANCIAL AGENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Powered by LangChain RAG + Groq LLaMA3 — Ask anything about your finances!</div>', unsafe_allow_html=True)

    # Get Groq API key
    groq_key = ""
    try:
        groq_key = st.secrets["GROQ_API_KEY"]
    except:
        groq_key = st.text_input("Enter Groq API Key", type="password", placeholder="gsk_...")

    if not groq_key:
        st.warning("Please add your Groq API key to continue!")
    else:
        # Initialize agent
        if 'custos_agent' not in st.session_state:
            with st.spinner("Initializing CUSTOS Agent with RAG knowledge base..."):
                try:
                    db_functions = {
                        'get_category_totals': get_category_totals,
                        'get_expenses': get_expenses
                    }
                    retriever = create_knowledge_base()
                    st.session_state['custos_agent'] = create_custos_agent(
                        groq_key, db_functions, retriever
                    )
                    st.session_state['chat_history'] = []
                    st.success("CUSTOS Agent ready!")
                except Exception as e:
                    st.error(f"Error initializing agent: {str(e)}")

        # PDF Upload for RAG
        with st.expander("📚 Upload Financial Book to Enhance Agent Knowledge"):
            pdf_file = st.file_uploader("Upload PDF", type=['pdf'])
            if pdf_file and st.button("Load into Agent"):
                with st.spinner("Loading PDF into RAG knowledge base..."):
                    retriever, pages = load_pdf_to_retriever(pdf_file)
                    if retriever:
                        db_functions = {
                            'get_category_totals': get_category_totals,
                            'get_expenses': get_expenses
                        }
                        st.session_state['custos_agent'] = create_custos_agent(
                            groq_key, db_functions, retriever
                        )
                        st.success(f"Loaded {pages} pages into agent knowledge base!")

        # Chat interface
        st.markdown("### 💬 Chat with CUSTOS")
        
        # Display chat history
        if 'chat_history' not in st.session_state:
            st.session_state['chat_history'] = []

        for msg in st.session_state['chat_history']:
            if msg['role'] == 'user':
                st.markdown(f"""
                <div style="background:rgba(196,160,80,0.1); border-left:3px solid #c4a050; 
                            padding:0.8rem; margin:0.5rem 0; border-radius:0 8px 8px 0">
                    <strong style="color:#c4a050">You:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:rgba(255,255,255,0.05); border-left:3px solid #4ade80;
                            padding:0.8rem; margin:0.5rem 0; border-radius:0 8px 8px 0">
                    <strong style="color:#4ade80">CUSTOS:</strong> {msg['content']}
                </div>
                """, unsafe_allow_html=True)

        # Suggested questions
        st.markdown("**Quick Questions:**")
        cols = st.columns(3)
        questions = [
            "Analyze my spending this month",
            "How can I save tax this year?",
            "Give me investment advice for ₹5000/month",
            "What is my financial health score?",
            "Suggest a budget plan for me",
            "How to build emergency fund?"
        ]
        for i, q in enumerate(questions):
            with cols[i % 3]:
                if st.button(q, key=f"q_{i}", use_container_width=True):
                    st.session_state['pending_question'] = q

        # Chat input
        user_input = st.chat_input("Ask CUSTOS anything about your finances...")
        
        if 'pending_question' in st.session_state:
            user_input = st.session_state.pop('pending_question')

        if user_input and 'custos_agent' in st.session_state:
            st.session_state['chat_history'].append({
                'role': 'user', 'content': user_input
            })
            
            with st.spinner("CUSTOS thinking..."):
                try:
                    income = st.session_state.get('monthly_income', 50000)
                    enhanced_input = f"{user_input} (User monthly income: ₹{income:,})"
                    response = st.session_state['custos_agent'].invoke(
                        {"input": enhanced_input}
                    )
                    answer = response.get('output', 'Sorry, I could not process that.')
                except Exception as e:
                    answer = f"Error: {str(e)}"
            
            st.session_state['chat_history'].append({
                'role': 'assistant', 'content': answer
            })
            st.rerun()

        # Clear chat button
        if st.session_state.get('chat_history'):
            if st.button("🗑️ Clear Chat"):
                st.session_state['chat_history'] = []
                if 'custos_agent' in st.session_state:
                    del st.session_state['custos_agent']
                st.rerun()
'''

content = content + agent_page
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! CUSTOS Agent page added.')
