import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from PIL import Image
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import (
    init_db, add_expense, get_expenses, get_category_totals,
    get_expenses_by_month, set_budget, get_budgets, add_goal, get_goals, delete_expense
)
from utils.ocr_extractor import (
    extract_expense_from_image, categorize_text_expense,
    parse_csv_bank_statement, CATEGORIES
)
from utils.financial_advisor import (
    generate_rule_based_advice, analyze_spending_health,
    get_savings_rate_advice, calculate_financial_health_score,
    FINANCIAL_GURUS, INDIAN_FINANCIAL_ADVICE
)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Custos — Your Financial Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Raleway:wght@300;400;500;600&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Raleway', sans-serif;
    background-color: #0a0e1a;
    color: #e8e0d0;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1628 50%, #0a0e1a 100%);
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hero Header */
.custos-header {
    background: linear-gradient(135deg, #0f1628 0%, #1a2444 50%, #0f1628 100%);
    border: 1px solid rgba(196, 160, 80, 0.3);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.custos-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: radial-gradient(ellipse at 20% 50%, rgba(196,160,80,0.08) 0%, transparent 60%);
}
.custos-title {
    font-family: 'Cinzel', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #c4a050;
    letter-spacing: 4px;
    margin: 0;
    text-shadow: 0 0 40px rgba(196,160,80,0.3);
}
.custos-subtitle {
    font-family: 'Raleway', sans-serif;
    font-size: 0.95rem;
    color: rgba(232,224,208,0.6);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* Metric Cards */
.metric-card {
    background: linear-gradient(135deg, #111827 0%, #1a2444 100%);
    border: 1px solid rgba(196, 160, 80, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-card:hover {
    border-color: rgba(196, 160, 80, 0.5);
    transform: translateY(-2px);
}
.metric-value {
    font-family: 'Cinzel', serif;
    font-size: 1.8rem;
    font-weight: 600;
    color: #c4a050;
}
.metric-label {
    font-size: 0.8rem;
    color: rgba(232,224,208,0.5);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.3rem;
}

/* Section Headers */
.section-header {
    font-family: 'Cinzel', serif;
    font-size: 1.2rem;
    color: #c4a050;
    letter-spacing: 2px;
    border-bottom: 1px solid rgba(196,160,80,0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Alert Boxes */
.alert-danger {
    background: rgba(220, 53, 69, 0.1);
    border: 1px solid rgba(220,53,69,0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}
.alert-success {
    background: rgba(40, 167, 69, 0.1);
    border: 1px solid rgba(40,167,69,0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}
.alert-info {
    background: rgba(196, 160, 80, 0.08);
    border: 1px solid rgba(196,160,80,0.3);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
}

/* Advice Card */
.advice-card {
    background: linear-gradient(135deg, #111827 0%, #1a2444 100%);
    border: 1px solid rgba(196, 160, 80, 0.25);
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1rem;
    font-family: 'Raleway', sans-serif;
    line-height: 1.7;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e1a 0%, #0f1628 100%);
    border-right: 1px solid rgba(196,160,80,0.15);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #c4a050 0%, #a08040 100%);
    color: #0a0e1a;
    font-family: 'Raleway', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    letter-spacing: 1px;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.5rem;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(196,160,80,0.3);
}

/* Inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: #111827 !important;
    border: 1px solid rgba(196,160,80,0.2) !important;
    border-radius: 8px !important;
    color: #e8e0d0 !important;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid rgba(196,160,80,0.2);
    border-radius: 8px;
}

/* Plotly charts background */
.js-plotly-plot {
    border-radius: 12px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid rgba(196,160,80,0.2);
    gap: 1rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Raleway', sans-serif;
    letter-spacing: 1px;
    color: rgba(232,224,208,0.5);
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #c4a050 !important;
    border-bottom: 2px solid #c4a050 !important;
}

/* File uploader */
.stFileUploader > div {
    background: #111827;
    border: 2px dashed rgba(196,160,80,0.3);
    border-radius: 12px;
}

/* Success/Error messages */
.stSuccess { background: rgba(40,167,69,0.1); border-radius: 8px; }
.stError { background: rgba(220,53,69,0.1); border-radius: 8px; }
.stWarning { background: rgba(255,193,7,0.1); border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── INIT ───────────────────────────────────────────────────────────────────────
init_db()

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-family: Cinzel, serif; font-size: 1.8rem; color: #c4a050; letter-spacing: 3px;'>🛡️ CUSTOS</div>
        <div style='font-size: 0.7rem; color: rgba(232,224,208,0.4); letter-spacing: 3px; text-transform: uppercase;'>Financial Guardian</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()

    # API Key
    st.markdown("#### 🔑 API Configuration")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Your Gemini API key for AI-powered features"
    )
    if api_key:
        st.session_state['api_key'] = api_key
        st.success("API Key saved ✓")

    st.divider()

    # Monthly Income
    st.markdown("#### 💰 Monthly Income")
    monthly_income = st.number_input(
        "Enter your monthly income (₹)",
        min_value=0,
        value=st.session_state.get('monthly_income', 50000),
        step=1000,
        format="%d"
    )
    st.session_state['monthly_income'] = monthly_income

    st.divider()

    # Navigation
    st.markdown("#### 📍 Navigation")
    page = st.radio(
        "",
        ["🏠 Dashboard", "📸 Add Expense", "📊 Analytics", "🤖 AI Advisor", "🎯 Goals & Budget"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("""
    <div style='font-size:0.7rem; color:rgba(232,224,208,0.3); text-align:center; padding: 0.5rem;'>
        ⚠️ Not financial advice.<br>Consult a certified advisor for major decisions.
    </div>
    """, unsafe_allow_html=True)

# ─── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="custos-header">
    <div class="custos-title">CUSTOS</div>
    <div class="custos-subtitle">Guardian of Your Wealth · AI-Powered Financial Intelligence</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    now = datetime.now()
    expenses_month = get_expenses_by_month(now.year, now.month)
    expenses_all = get_expenses()
    total_month = expenses_month['amount'].sum() if not expenses_month.empty else 0
    total_all = expenses_all['amount'].sum() if not expenses_all.empty else 0
    income = st.session_state.get('monthly_income', 0)
    savings = income - total_month

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">₹{total_month:,.0f}</div>
            <div class="metric-label">This Month's Spend</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        savings_color = "#4ade80" if savings >= 0 else "#f87171"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{savings_color}">₹{savings:,.0f}</div>
            <div class="metric-label">Monthly Savings</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        num_tx = len(expenses_month) if not expenses_month.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{num_tx}</div>
            <div class="metric-label">Transactions</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        save_rate = ((savings / income) * 100) if income > 0 else 0
        rate_color = "#4ade80" if save_rate >= 20 else "#facc15" if save_rate >= 10 else "#f87171"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{rate_color}">{save_rate:.1f}%</div>
            <div class="metric-label">Savings Rate</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown('<div class="section-header">SPENDING BY CATEGORY</div>', unsafe_allow_html=True)
        cat_totals = get_category_totals(now.year, now.month)
        if not cat_totals.empty:
            fig = px.pie(
                cat_totals, values='total', names='category',
                color_discrete_sequence=['#c4a050','#a08040','#806030','#604820','#e8c070',
                                          '#d4b060','#b09050','#907040','#705030','#504020',
                                          '#f0d080','#3a2010'],
                hole=0.4
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8e0d0', family='Raleway'),
                legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True
            )
            fig.update_traces(textinfo='percent', textfont_color='#0a0e1a')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded this month. Add some to see insights!")

    with col_right:
        st.markdown('<div class="section-header">SAVINGS HEALTH</div>', unsafe_allow_html=True)
        if income > 0:
            advice = get_savings_rate_advice(total_month, income)
            st.markdown(f'<div class="alert-info">{advice}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header" style="margin-top:1.5rem">RECENT TRANSACTIONS</div>', unsafe_allow_html=True)
        if not expenses_all.empty:
            recent = expenses_all.head(5)[['date', 'amount', 'category', 'description']]
            recent['amount'] = recent['amount'].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(
                recent,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "date": "Date",
                    "amount": "Amount",
                    "category": "Category",
                    "description": "Description"
                }
            )
        else:
            st.info("No transactions yet.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD EXPENSE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📸 Add Expense":
    st.markdown('<div class="section-header">ADD NEW EXPENSE</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📸 Upload Screenshot", "✏️ Manual Entry", "📄 Import CSV"])

    # ── TAB 1: Screenshot Upload ──
    with tab1:
        st.markdown("Upload a payment screenshot (UPI, PhonePe, GPay, Paytm, bank receipt)")
        uploaded_file = st.file_uploader(
            "Drop your payment screenshot here",
            type=['png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )

        if uploaded_file:
            image = Image.open(uploaded_file)
            col_img, col_result = st.columns(2)

            with col_img:
                st.image(image, caption="Uploaded Screenshot", use_container_width=True)

            with col_result:
                st.markdown("**Extracting expense details...**")
                api_key = st.session_state.get('api_key', '')

                if not api_key:
                    st.error("Please add your Anthropic API key in the sidebar first!")
                else:
                    with st.spinner("🔍 Reading screenshot with Claude AI..."):
                        result = extract_expense_from_image(image, api_key)

                    if 'error' in result:
                        st.error(f"Extraction failed: {result['error']}")
                    else:
                        st.success("✅ Expense extracted successfully!")

                        with st.form("confirm_screenshot_expense"):
                            st.markdown("**Confirm or edit the extracted details:**")
                            amount = st.number_input("Amount (₹)", value=result.get('amount', 0.0), min_value=0.0)
                            exp_date = st.date_input("Date", value=date.today())
                            description = st.text_input("Description", value=result.get('description', ''))
                            category = st.selectbox(
                                "Category",
                                CATEGORIES,
                                index=CATEGORIES.index(result.get('category', 'Others')) if result.get('category') in CATEGORIES else 0
                            )

                            if st.form_submit_button("💾 Save Expense"):
                                add_expense(str(exp_date), amount, category, description, source='screenshot')
                                st.success(f"✅ Expense of ₹{amount:,.0f} saved under {category}!")
                                st.balloons()

    # ── TAB 2: Manual Entry ──
    with tab2:
        with st.form("manual_expense_form"):
            col1, col2 = st.columns(2)
            with col1:
                amount = st.number_input("Amount (₹) *", min_value=0.0, step=10.0)
                exp_date = st.date_input("Date *", value=date.today())
            with col2:
                description = st.text_input("Description *", placeholder="e.g. Zomato dinner, Uber ride...")
                use_ai_cat = st.checkbox("🤖 Auto-categorize with AI", value=True)

            if use_ai_cat:
                category_options = ["(Auto-detect)"] + CATEGORIES
                category = st.selectbox("Category", category_options)
            else:
                category = st.selectbox("Category", CATEGORIES)

            submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)

            if submitted:
                if amount <= 0 or not description:
                    st.error("Please fill in all required fields!")
                else:
                    if use_ai_cat and category == "(Auto-detect)":
                        api_key = st.session_state.get('api_key', '')
                        with st.spinner("Categorizing..."):
                            category = categorize_text_expense(description, amount, api_key) if api_key else 'Others'

                    add_expense(str(exp_date), amount, category, description, source='manual')
                    st.success(f"✅ ₹{amount:,.0f} added under **{category}**!")

    # ── TAB 3: CSV Import ──
    with tab3:
        st.markdown("Import your bank statement or transaction CSV file")
        st.markdown("""
        <div class="alert-info">
        📋 <strong>Supported formats:</strong> SBI, HDFC, ICICI bank statement exports. 
        CSV should have columns: Date, Amount/Debit, Description/Narration
        </div>
        """, unsafe_allow_html=True)

        csv_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")

        if csv_file:
            try:
                df = pd.read_csv(csv_file)
                st.markdown(f"**Preview ({len(df)} rows):**")
                st.dataframe(df.head(5), use_container_width=True)

                if st.button("🚀 Import All Transactions"):
                    expenses, error = parse_csv_bank_statement(df)
                    if error:
                        st.error(error)
                    else:
                        for exp in expenses:
                            add_expense(exp['date'], exp['amount'], exp['category'],
                                        exp['description'], source='csv_import')
                        st.success(f"✅ Successfully imported {len(expenses)} transactions!")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Analytics":
    st.markdown('<div class="section-header">SPENDING ANALYTICS</div>', unsafe_allow_html=True)

    expenses_all = get_expenses(500)

    if expenses_all.empty:
        st.info("No expenses yet. Start adding expenses to see analytics!")
    else:
        expenses_all['date'] = pd.to_datetime(expenses_all['date'])
        expenses_all['month'] = expenses_all['date'].dt.to_period('M').astype(str)
        expenses_all['week'] = expenses_all['date'].dt.isocalendar().week

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Monthly Spending Trend**")
            monthly = expenses_all.groupby('month')['amount'].sum().reset_index()
            fig = px.bar(
                monthly, x='month', y='amount',
                color_discrete_sequence=['#c4a050']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8e0d0', family='Raleway'),
                xaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                yaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Category Breakdown (All Time)**")
            cat_all = expenses_all.groupby('category')['amount'].sum().reset_index()
            cat_all = cat_all.sort_values('amount', ascending=True).tail(8)
            fig2 = px.bar(
                cat_all, x='amount', y='category', orientation='h',
                color_discrete_sequence=['#c4a050']
            )
            fig2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8e0d0', family='Raleway'),
                xaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                yaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Full transaction table
        st.markdown('<div class="section-header" style="margin-top:1rem">ALL TRANSACTIONS</div>', unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            cat_filter = st.multiselect("Filter by Category", options=expenses_all['category'].unique())
        with col_f2:
            source_filter = st.multiselect("Filter by Source", options=expenses_all['source'].unique())

        filtered = expenses_all.copy()
        if cat_filter:
            filtered = filtered[filtered['category'].isin(cat_filter)]
        if source_filter:
            filtered = filtered[filtered['source'].isin(source_filter)]

        display = filtered[['date', 'amount', 'category', 'description', 'source']].copy()
        display['amount'] = display['amount'].apply(lambda x: f"₹{x:,.0f}")
        display['date'] = display['date'].dt.strftime('%d %b %Y')
        st.dataframe(display, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AI ADVISOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🤖 AI Advisor":
    st.markdown('<div class="section-header">AI FINANCIAL ADVISOR</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Choose Your Financial Guru**")
        guru = st.selectbox("", list(FINANCIAL_GURUS.keys()), label_visibility="collapsed")
        guru_data = FINANCIAL_GURUS[guru]
        st.markdown(f"""
        <div class="advice-card" style="margin-top:0.5rem">
            <div style="color:#c4a050; font-family: Cinzel, serif; font-size:1.1rem; margin-bottom:0.5rem">{guru_data['icon']} {guru}</div>
            <div style="font-size:0.85rem; color:rgba(232,224,208,0.7); font-style:italic">{guru_data['philosophy']}</div>
            <hr style="border-color:rgba(196,160,80,0.2); margin:0.8rem 0">
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Key Principles**")
        for principle in guru_data['principles'][:3]:
            st.markdown(f'<div class="alert-info" style="font-size:0.82rem; margin:0.3rem 0">💬 {principle}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Indian Investment Guide**")
        for product, desc in INDIAN_FINANCIAL_ADVICE['Investment Options'].items():
            with st.expander(f"📈 {product}"):
                st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)

    with col2:
        now = datetime.now()
        income = st.session_state.get('monthly_income', 0)
        cat_totals = get_category_totals(now.year, now.month)

        if cat_totals.empty:
            st.markdown("""
            <div class="advice-card" style="text-align:center; padding:2rem">
                <div style="font-size:2rem">📊</div>
                <div style="color:#c4a050; margin-top:0.5rem">No expenses yet!</div>
                <div style="font-size:0.85rem; color:rgba(232,224,208,0.6); margin-top:0.5rem">
                    Add some expenses first to get personalized financial advice
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Financial Health Score
            score, grade, reasons = calculate_financial_health_score(cat_totals, income)
            score_color = "#4ade80" if score >= 80 else "#facc15" if score >= 60 else "#f87171"
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:1rem">
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <div>
                        <div style="font-size:0.8rem; color:rgba(232,224,208,0.5); letter-spacing:2px; text-transform:uppercase">Financial Health Score</div>
                        <div style="font-family:Cinzel,serif; font-size:2rem; color:{score_color}">{score}/100</div>
                        <div style="font-size:0.9rem; color:{score_color}">{grade}</div>
                    </div>
                    <div style="font-size:3rem">{guru_data['icon']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Spending alerts
            alerts, suggestions = analyze_spending_health(cat_totals, income)
            if alerts:
                st.markdown("**⚠️ Spending Alerts**")
                for alert in alerts:
                    st.markdown(f'<div class="alert-danger">{alert}</div>', unsafe_allow_html=True)

            if st.button(f"{guru_data['icon']} Generate Advice from {guru}", use_container_width=True):
                with st.spinner(f"Analysing your finances through {guru}'s lens..."):
                    advice = generate_rule_based_advice(cat_totals, income, guru)
                st.markdown(f"""
                <div class="advice-card">
                    <div style="color:#c4a050; font-family:Cinzel,serif; font-size:0.9rem;
                                letter-spacing:2px; margin-bottom:1rem">
                        {guru_data['icon']} ADVICE FROM {guru.upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(advice)

            # Tax saving section
            st.markdown('<div class="section-header" style="margin-top:1.5rem">TAX SAVING TIPS</div>', unsafe_allow_html=True)
            for section, details in INDIAN_FINANCIAL_ADVICE['Tax Saving'].items():
                st.markdown(f'<div class="alert-info"><strong>{section}:</strong> {details}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GOALS & BUDGET
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎯 Goals & Budget":
    st.markdown('<div class="section-header">GOALS & BUDGET MANAGEMENT</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🎯 Financial Goals", "📋 Monthly Budgets"])

    with tab1:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.markdown("**Add a New Goal**")
            with st.form("add_goal_form"):
                goal_name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund, MacBook, Trip to Goa")
                target = st.number_input("Target Amount (₹)", min_value=0.0, step=500.0)
                deadline = st.date_input("Target Date", value=date.today())
                if st.form_submit_button("➕ Add Goal", use_container_width=True):
                    if goal_name and target > 0:
                        add_goal(goal_name, target, str(deadline))
                        st.success(f"✅ Goal '{goal_name}' added!")
                    else:
                        st.error("Please fill in all fields!")

        with col2:
            st.markdown("**Your Financial Goals**")
            goals = get_goals()
            if not goals.empty:
                for _, goal in goals.iterrows():
                    progress = min((goal['current_amount'] / goal['target_amount']) * 100, 100)
                    st.markdown(f"**{goal['goal_name']}**")
                    st.progress(progress / 100)
                    st.markdown(f"₹{goal['current_amount']:,.0f} / ₹{goal['target_amount']:,.0f} ({progress:.1f}%)")
                    st.markdown("---")
            else:
                st.info("No goals yet. Add your first financial goal!")

    with tab2:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.markdown("**Set Monthly Budget**")
            with st.form("budget_form"):
                cat = st.selectbox("Category", CATEGORIES)
                limit = st.number_input("Monthly Limit (₹)", min_value=0.0, step=500.0)
                if st.form_submit_button("💾 Set Budget", use_container_width=True):
                    if limit > 0:
                        set_budget(cat, limit)
                        st.success(f"✅ Budget set for {cat}!")

        with col2:
            st.markdown("**Budget vs Actual (This Month)**")
            budgets = get_budgets()
            now = datetime.now()
            cat_totals = get_category_totals(now.year, now.month)

            if not budgets.empty and not cat_totals.empty:
                merged = budgets.merge(cat_totals, on='category', how='left').fillna(0)
                merged.columns = ['id', 'category', 'budget', 'created_at', 'spent']

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Budget', x=merged['category'], y=merged['budget'],
                                     marker_color='rgba(196,160,80,0.4)'))
                fig.add_trace(go.Bar(name='Spent', x=merged['category'], y=merged['spent'],
                                     marker_color='#c4a050'))
                fig.update_layout(
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e8e0d0', family='Raleway'),
                    xaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                    yaxis=dict(gridcolor='rgba(196,160,80,0.1)'),
                    legend=dict(bgcolor='rgba(0,0,0,0)'),
                    margin=dict(t=20, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)

                for _, row in merged.iterrows():
                    if row['spent'] > row['budget']:
                        overspend = row['spent'] - row['budget']
                        st.markdown(f'<div class="alert-danger">⚠️ <strong>{row["category"]}</strong>: Over budget by ₹{overspend:,.0f}</div>', unsafe_allow_html=True)
            else:
                st.info("Set budgets and add expenses to see budget vs actual comparison.")
