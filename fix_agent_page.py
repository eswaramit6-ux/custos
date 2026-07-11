content = open('app.py', encoding='utf-8').read()

old = '''            with st.spinner("CUSTOS thinking..."):
                try:
                    income = st.session_state.get('monthly_income', 50000)
                    enhanced_input = f"{user_input} (User monthly income: ₹{income:,})"
                    response = st.session_state['custos_agent'].invoke(
                        {"input": enhanced_input}
                    )
                    answer = response.get('output', 'Sorry, I could not process that.')
                except Exception as e:
                    answer = f"Error: {str(e)}"'''

new = '''            with st.spinner("CUSTOS thinking..."):
                try:
                    income = st.session_state.get('monthly_income', 50000)
                    enhanced_input = f"{user_input} (User monthly income: Rs.{income:,})"
                    
                    # Build chat history for context
                    from langchain_core.messages import HumanMessage, AIMessage
                    history = []
                    for msg in st.session_state['chat_history'][:-1]:
                        if msg['role'] == 'user':
                            history.append(HumanMessage(content=msg['content']))
                        else:
                            history.append(AIMessage(content=msg['content']))
                    
                    response = st.session_state['custos_agent'].invoke({
                        "input": enhanced_input,
                        "chat_history": history
                    })
                    answer = response.get('output', 'Sorry, I could not process that.')
                except Exception as e:
                    answer = f"Error: {str(e)}"'''

content = content.replace(old, new, 1)
open('app.py', 'w', encoding='utf-8').write(content)
print('Done!')
