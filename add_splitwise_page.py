content = open('app.py', encoding='utf-8').read()

# Add splitwise import at top
old_import = "from utils.pdf_advisor import extract_text_from_pdf, generate_book_based_advice"
new_import = "from utils.pdf_advisor import extract_text_from_pdf, generate_book_based_advice\nfrom utils.splitwise_integration import get_splitwise_expenses, get_splitwise_user, get_splitwise_groups, parse_splitwise_expenses, analyze_splitwise_spending"
content = content.replace(old_import, new_import, 1)

# Add Splitwise page to navigation
old_nav = '"📚 Book Advisor"'
new_nav = '"📚 Book Advisor",\n    "🤝 Splitwise"'
content = content.replace(old_nav, new_nav, 1)

# Add Splitwise page at end
splitwise_page = '''

# ═══ SPLITWISE PAGE ════════════════════════════════════════════
elif page == "🤝 Splitwise":
    st.markdown('<div class="section-header">SPLITWISE GROUP EXPENSES</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Import your group expenses from Splitwise and analyze your shared spending!</div>', unsafe_allow_html=True)

    # Get API key from secrets or sidebar
    splitwise_key = st.secrets.get("SPLITWISE_API_KEY", "") if hasattr(st, 'secrets') else ""
    
    if not splitwise_key:
        splitwise_key = st.text_input("Enter Splitwise API Key", type="password", 
                                       placeholder="Your Splitwise API key...")

    if splitwise_key:
        # Get user info
        user, error = get_splitwise_user(splitwise_key)
        
        if error:
            st.error(f"Connection failed: {error}")
        else:
            st.success(f"Connected as: {user.get('first_name', '')} {user.get('last_name', '')} ({user.get('email', '')})")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### Import Settings")
                days = st.slider("Import expenses from last N days", 7, 90, 30)
                
                if st.button("Import Splitwise Expenses", use_container_width=True):
                    with st.spinner("Fetching expenses from Splitwise..."):
                        expenses, err = get_splitwise_expenses(splitwise_key, days)
                        
                    if err:
                        st.error(f"Error: {err}")
                    elif not expenses:
                        st.info("No expenses found in Splitwise for this period.")
                    else:
                        # Parse expenses
                        parsed = parse_splitwise_expenses(expenses, user.get('id'))
                        
                        if parsed:
                            # Save to database
                            saved_count = 0
                            for exp in parsed:
                                try:
                                    add_expense(exp['date'], exp['amount'], 
                                              exp['category'], exp['description'],
                                              source='splitwise')
                                    saved_count += 1
                                except:
                                    pass
                            
                            st.success(f"✅ Imported {saved_count} expenses from Splitwise!")
                            st.session_state['splitwise_expenses'] = parsed
                        else:
                            st.info("No expenses where you owe money found.")

                # Show groups
                st.markdown("### Your Groups")
                groups, gerr = get_splitwise_groups(splitwise_key)
                if groups:
                    for group in groups[:5]:
                        if group.get('name') != 'Non-group expenses':
                            members = len(group.get('members', []))
                            st.markdown(f"""
                            <div class="advice-card" style="padding:0.8rem; margin-bottom:0.5rem">
                                <div style="color:#c4a050; font-weight:bold">{group.get('name', 'Group')}</div>
                                <div style="font-size:0.8rem; color:rgba(232,224,208,0.6)">{members} members</div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No groups found. Add friends on Splitwise to split expenses!")

            with col2:
                st.markdown("### Spending Analysis")
                
                if 'splitwise_expenses' in st.session_state:
                    parsed = st.session_state['splitwise_expenses']
                    analysis = analyze_splitwise_spending(parsed)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:0.8rem; color:rgba(232,224,208,0.5)">TOTAL GROUP EXPENSES</div>
                        <div style="font-family:Cinzel,serif; font-size:1.8rem; color:#c4a050">₹{analysis['total']:,.2f}</div>
                        <div style="font-size:0.8rem; color:rgba(232,224,208,0.5)">{analysis['count']} transactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if analysis['by_category']:
                        st.markdown("**By Category:**")
                        for cat, amount in sorted(analysis['by_category'].items(), 
                                                   key=lambda x: x[1], reverse=True):
                            st.markdown(f'<div class="alert-info"><b>{cat}:</b> ₹{amount:,.2f}</div>', 
                                       unsafe_allow_html=True)
                    
                    if analysis['largest_expense']:
                        largest = analysis['largest_expense']
                        st.markdown(f"""
                        <div class="advice-card" style="margin-top:1rem">
                            <div style="color:#c4a050; font-size:0.85rem">LARGEST EXPENSE</div>
                            <div style="font-weight:bold">{largest['description']}</div>
                            <div style="color:#c4a050">₹{largest['amount']:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="advice-card" style="text-align:center; padding:2rem">
                        <div style="font-size:2rem">🤝</div>
                        <div style="color:#c4a050; margin-top:0.5rem">No data yet!</div>
                        <div style="font-size:0.85rem; color:rgba(232,224,208,0.6); margin-top:0.5rem">
                            Import your Splitwise expenses to see analysis
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="advice-card" style="text-align:center; padding:2rem">
            <div style="font-size:2rem">🤝</div>
            <div style="color:#c4a050; margin-top:0.5rem">Enter your Splitwise API key above!</div>
            <div style="font-size:0.85rem; color:rgba(232,224,208,0.6); margin-top:0.5rem">
                Get your API key from splitwise.com/apps
            </div>
        </div>
        """, unsafe_allow_html=True)
'''

content = content + splitwise_page
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! Splitwise page added successfully.')
