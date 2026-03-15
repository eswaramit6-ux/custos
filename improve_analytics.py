content = open('app.py', encoding='utf-8').read()

# Find the analytics page section
idx = content.find('elif page == "📊 Analytics":')
end_idx = content.find('\nelif page == "🤖 AI Advisor":', idx)

old_analytics = content[idx:end_idx]

new_analytics = '''elif page == "📊 Analytics":
    st.markdown('<div class="section-header">SPENDING ANALYTICS</div>', unsafe_allow_html=True)

    now = datetime.now()
    income = st.session_state.get('monthly_income', 0)

    # ── Date Filter ──
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_year = st.selectbox("Year", [2024, 2025, 2026], index=2)
    with col_f2:
        selected_month = st.selectbox("Month", list(range(1, 13)), 
                                       index=now.month-1,
                                       format_func=lambda x: datetime(2026, x, 1).strftime('%B'))

    cat_totals = get_category_totals(selected_year, selected_month)
    all_expenses = get_expenses(selected_year, selected_month)

    if cat_totals.empty:
        st.info("No expenses found for this period. Add some expenses to see analytics!")
    else:
        total_spent = cat_totals['total'].sum()
        savings = income - total_spent if income > 0 else 0

        # ── Key Metrics ──
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:0.75rem;color:rgba(232,224,208,0.5);letter-spacing:2px">TOTAL SPENT</div>
                <div style="font-family:Cinzel,serif;font-size:1.5rem;color:#c4a050">₹{total_spent:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:0.75rem;color:rgba(232,224,208,0.5);letter-spacing:2px">TRANSACTIONS</div>
                <div style="font-family:Cinzel,serif;font-size:1.5rem;color:#c4a050">{len(all_expenses)}</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            avg = total_spent / len(all_expenses) if len(all_expenses) > 0 else 0
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:0.75rem;color:rgba(232,224,208,0.5);letter-spacing:2px">AVG TRANSACTION</div>
                <div style="font-family:Cinzel,serif;font-size:1.5rem;color:#c4a050">₹{avg:,.0f}</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            savings_rate = (savings/income*100) if income > 0 else 0
            color = "#4ade80" if savings_rate >= 20 else "#f87171"
            st.markdown(f"""<div class="metric-card">
                <div style="font-size:0.75rem;color:rgba(232,224,208,0.5);letter-spacing:2px">SAVINGS RATE</div>
                <div style="font-family:Cinzel,serif;font-size:1.5rem;color:{color}">{savings_rate:.1f}%</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Row 1: Pie Chart + Bar Chart ──
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">SPENDING BY CATEGORY</div>', unsafe_allow_html=True)
            fig_pie = px.pie(
                cat_totals, values='total', names='category',
                hole=0.4,
                color_discrete_sequence=['#c4a050','#4ade80','#60a5fa','#f87171',
                                         '#a78bfa','#fb923c','#34d399','#f472b6',
                                         '#facc15','#38bdf8','#818cf8','#e879f9']
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8e0d0'),
                showlegend=True,
                legend=dict(font=dict(size=10))
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">TOP CATEGORIES</div>', unsafe_allow_html=True)
            top_cats = cat_totals.nlargest(8, 'total')
            fig_bar = px.bar(
                top_cats, x='total', y='category',
                orientation='h',
                color='total',
                color_continuous_scale=['#604820', '#c4a050', '#f0d080']
            )
            fig_bar.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8e0d0'),
                showlegend=False,
                coloraxis_showscale=False,
                xaxis_title="Amount (₹)",
                yaxis_title=""
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Row 2: Daily Spending Trend ──
        if not all_expenses.empty and 'date' in all_expenses.columns:
            st.markdown('<div class="section-header">DAILY SPENDING TREND</div>', unsafe_allow_html=True)
            
            try:
                all_expenses['date'] = pd.to_datetime(all_expenses['date'])
                daily = all_expenses.groupby('date')['amount'].sum().reset_index()
                daily = daily.sort_values('date')
                daily['cumulative'] = daily['amount'].cumsum()

                fig_trend = px.line(
                    daily, x='date', y='amount',
                    title='',
                    markers=True,
                    color_discrete_sequence=['#c4a050']
                )
                fig_trend.add_scatter(
                    x=daily['date'], y=daily['cumulative'],
                    mode='lines', name='Cumulative',
                    line=dict(color='#4ade80', dash='dash')
                )
                fig_trend.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8e0d0'),
                    xaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                    yaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                    legend=dict(font=dict(size=10))
                )
                st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                st.info("Add more expenses to see daily trends!")

        # ── Row 3: Spending Anomaly Detection ──
        st.markdown('<div class="section-header">SPENDING INSIGHTS & ANOMALIES</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Anomaly detection - categories over healthy limit
            healthy_limits = {
                'Food & Dining': 15, 'Transportation': 10, 'Shopping': 10,
                'Entertainment': 5, 'Groceries': 15, 'Utilities & Bills': 10,
                'Healthcare': 5, 'Personal Care': 5
            }
            
            anomalies = []
            if income > 0:
                for _, row in cat_totals.iterrows():
                    cat = row['category']
                    pct = (row['total'] / income) * 100
                    if cat in healthy_limits and pct > healthy_limits[cat] * 1.5:
                        anomalies.append((cat, pct, healthy_limits[cat], row['total']))
            
            if anomalies:
                st.markdown("**⚠️ Spending Anomalies Detected:**")
                for cat, pct, limit, amount in anomalies:
                    st.markdown(f"""
                    <div class="alert-danger">
                        <b>{cat}</b>: ₹{amount:,.0f} ({pct:.1f}% of income) — 
                        recommended max is {limit}%
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="alert-info">
                    ✅ No spending anomalies detected! All categories within healthy limits.
                </div>
                """, unsafe_allow_html=True)

        with col4:
            # Spending forecast
            if income > 0:
                days_in_month = 30
                days_passed = now.day
                daily_rate = total_spent / days_passed if days_passed > 0 else 0
                projected = daily_rate * days_in_month
                
                proj_color = "#4ade80" if projected < income * 0.8 else "#f87171"
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">MONTHLY FORECAST</div>
                    <div style="font-family:Cinzel,serif;font-size:1.8rem;color:{proj_color}">
                        ₹{projected:,.0f}
                    </div>
                    <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">
                        Based on ₹{daily_rate:,.0f}/day average
                    </div>
                    {'<div style="color:#4ade80;font-size:0.85rem">✅ On track to save this month!</div>' 
                     if projected < income * 0.8 
                     else '<div style="color:#f87171;font-size:0.85rem">⚠️ Projected to overspend!</div>'}
                </div>
                """, unsafe_allow_html=True)

        # ── Transaction Table ──
        st.markdown('<div class="section-header">TRANSACTION DETAILS</div>', unsafe_allow_html=True)
        if not all_expenses.empty:
            display_df = all_expenses[['date', 'amount', 'category', 'description']].copy()
            display_df['amount'] = display_df['amount'].apply(lambda x: f"₹{x:,.2f}")
            display_df.columns = ['Date', 'Amount', 'Category', 'Description']
            st.dataframe(display_df, use_container_width=True, hide_index=True)

'''

content = content[:idx] + new_analytics + content[end_idx:]
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! Analytics page improved successfully.')
