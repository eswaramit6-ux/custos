content = open('app.py', encoding='utf-8').read()

old = "                    st.success(f\"✅ ₹{amount:,.0f} added under **{category}**!\")"

new = """                    st.success(f"✅ ₹{amount:,.0f} added under **{category}**!")
                    
                    # ── UNIFIED PIPELINE: Auto Analysis After Adding Expense ──
                    from utils.financial_advisor import analyze_spending_health, get_savings_rate_advice, calculate_financial_health_score
                    from datetime import datetime as dt2
                    now2 = dt2.now()
                    cat_totals2 = get_category_totals(now2.year, now2.month)
                    income2 = st.session_state.get('monthly_income', 0)
                    
                    if not cat_totals2.empty and income2 > 0:
                        score, grade, reasons = calculate_financial_health_score(cat_totals2, income2)
                        score_color = '#4ade80' if score >= 80 else '#facc15' if score >= 60 else '#f87171'
                        st.markdown(f'<div class="metric-card" style="margin-top:1rem"><b>Financial Health Score: <span style="color:{score_color}">{score}/100 — {grade}</span></b></div>', unsafe_allow_html=True)
                        
                        alerts, suggestions = analyze_spending_health(cat_totals2, income2)
                        if alerts:
                            st.markdown("**⚠️ Budget Alerts:**")
                            for alert in alerts[:2]:
                                st.markdown(f'<div class="alert-danger">{alert}</div>', unsafe_allow_html=True)
                        
                        savings_advice = get_savings_rate_advice(cat_totals2['total'].sum(), income2)
                        if savings_advice:
                            st.markdown(f'<div class="alert-info">{savings_advice}</div>', unsafe_allow_html=True)
                        
                        category_tips = {
                            'Food & Dining': 'Tip: Cooking at home 3x a week can save up to 2000/month!',
                            'Shopping': 'Tip: Wait 48 hours before purchases over 2000 to avoid impulse buying!',
                            'Entertainment': 'Tip: Share OTT subscriptions with family to cut costs by 50%!',
                            'Transportation': 'Tip: A monthly metro pass saves more than daily tickets!',
                            'Groceries': 'Tip: Buy staples in bulk monthly — saves 15-20% on grocery bills!',
                        }
                        if category in category_tips:
                            st.info(category_tips[category])"""

content = content.replace(old, new, 1)
open('app.py', 'w', encoding='utf-8').write(content)
print('Done! Pipeline integrated.')
