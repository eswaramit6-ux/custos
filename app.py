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
from utils.pdf_advisor import extract_text_from_pdf, generate_book_based_advice
from utils.splitwise_integration import get_splitwise_expenses, get_splitwise_user, get_splitwise_groups, parse_splitwise_expenses, analyze_splitwise_spending
from utils.financial_advisor import (
    generate_rule_based_advice, analyze_spending_health,
    get_savings_rate_advice, calculate_financial_health_score,
    FINANCIAL_GURUS, INDIAN_FINANCIAL_ADVICE,
    get_80c_recommendations, get_tax_saving_summary,
    get_indian_investment_plan, calculate_sip_returns
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

/* FORCE SIDEBAR ALWAYS VISIBLE */
[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    width: 280px !important;
    min-width: 280px !important;
    transform: none !important;
    position: relative !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}
section[data-testid="stSidebar"] > div {
    width: 280px !important;
}
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
        ["🏠 Dashboard", "📸 Add Expense", "📊 Analytics", "🤖 AI Advisor", "🎯 Goals & Budget",
    "📚 Book Advisor",
    "🤝 Splitwise"],
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
                color_discrete_sequence=['#c4a050','#4ade80','#60a5fa','#f87171','#a78bfa','#fb923c','#34d399','#f472b6','#facc15','#38bdf8','#818cf8','#e879f9'],
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
        st.markdown("Upload a payment screenshot — Tesseract OCR will automatically read it!")
        st.markdown('<div class="alert-info">📸 Supports UPI, PhonePe, GPay, Paytm, bank receipts</div>', unsafe_allow_html=True)

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
                with st.spinner("🔍 Reading screenshot with Tesseract OCR..."):
                    result = extract_expense_from_image(image)

                if result.get('raw_text'):
                    with st.expander("📄 Extracted Text"):
                        st.text(result.get('raw_text', ''))

                st.success("✅ Review and confirm details:")
                with st.form("confirm_screenshot_expense"):
                    amount = st.number_input("Amount (₹) *", value=float(result.get('amount', 0.0)), min_value=0.0, step=10.0)
                    exp_date = st.date_input("Date", value=date.today())
                    description = st.text_input("Description *", value=result.get('description', ''), placeholder="e.g. Zomato order, Uber ride...")
                    category = st.selectbox("Category", CATEGORIES,
                        index=CATEGORIES.index(result.get('category', 'Others')) if result.get('category') in CATEGORIES else 0)

                    if st.form_submit_button("💾 Save Expense", use_container_width=True):
                        if amount <= 0 or not description:
                            st.error("Please fill in amount and description!")
                        else:
                            add_expense(str(exp_date), amount, category, description, source='screenshot')
                            st.success(f"✅ ₹{amount:,.0f} saved under {category}!")
                            st.balloons()

        st.divider()
        st.markdown("**📱 Or Paste Your UPI/Bank SMS Message**")
        st.markdown('<div class="alert-info">Paste any bank SMS like: <em>"₹500 debited from SBI for Zomato on 01-03-2026"</em></div>', unsafe_allow_html=True)

        sms_text = st.text_area("Paste SMS or transaction message here", placeholder="Your account XX1234 is debited by Rs.500 on 01-Mar-26...", height=100)

        if st.button("📱 Extract from SMS", use_container_width=True):
            if sms_text:
                from utils.ocr_extractor import extract_from_text
                result = extract_from_text(sms_text)
                st.session_state['sms_result'] = result
            else:
                st.error("Please paste a message first!")

        if 'sms_result' in st.session_state:
            result = st.session_state['sms_result']
            st.success("✅ Details extracted! Review and save below:")
            with st.form("sms_expense_form"):
                amount = st.number_input("Amount (₹)", value=float(result.get('amount', 0.0)), min_value=0.0)
                exp_date = st.date_input("Date", value=date.today())
                description = st.text_input("Description", value=result.get('description', ''))
                category = st.selectbox("Category", CATEGORIES,
                    index=CATEGORIES.index(result.get('category', 'Others')) if result.get('category') in CATEGORIES else 0)
                if st.form_submit_button("💾 Save Expense", use_container_width=True):
                    add_expense(str(exp_date), amount, category, description, source='sms')
                    st.success(f"✅ ₹{amount:,.0f} saved under {category}!")
                    del st.session_state['sms_result']
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
                            st.info(category_tips[category])

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
    all_expenses = get_expenses(limit=500)

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

        # Indian Finance Tabs
        advisor_tab1, advisor_tab2, advisor_tab3 = st.tabs(["🤖 Guru Advice", "🇮🇳 Indian Investment Plan", "💰 Tax Calculator"])

        with advisor_tab2:
            st.markdown("### 🇮🇳 Your Personalized Indian Investment Plan")
            if income <= 0:
                st.warning("Set your monthly income in the sidebar first!")
            else:
                total_exp = cat_totals['total'].sum() if not cat_totals.empty else 0
                plan, savings, savings_rate = get_indian_investment_plan(income, total_exp)

                savings_color = "#4ade80" if savings >= 0 else "#f87171"
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem">
                    <div style="display:flex; justify-content:space-between">
                        <div>
                            <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">MONTHLY SAVINGS</div>
                            <div style="font-family:Cinzel,serif;font-size:1.8rem;color:{savings_color}">₹{savings:,.0f}</div>
                        </div>
                        <div>
                            <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">SAVINGS RATE</div>
                            <div style="font-family:Cinzel,serif;font-size:1.8rem;color:{savings_color}">{savings_rate:.1f}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Step-by-step investment roadmap:**")
                for step in plan:
                    with st.expander(f"{step['icon']} Priority {step['priority']}: {step['step']} — ₹{step['monthly']:,}/month"):
                        st.markdown(f"**Where:** {step['where']}")
                        st.markdown(f"**Why:** {step['why']}")
                        if step['target']:
                            st.markdown(f"**Annual Target:** ₹{step['target']:,}")

                # SIP Calculator
                st.markdown("---")
                st.markdown("### 📊 SIP Returns Calculator")
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    sip_amt = st.number_input("Monthly SIP (₹)", min_value=500, max_value=100000, value=max(500, int(savings*0.5) if savings > 0 else 500), step=500)
                with col_s2:
                    sip_years = st.selectbox("Duration", [5, 10, 15, 20, 25, 30], index=1)
                with col_s3:
                    sip_return = st.selectbox("Expected Return %", [8, 10, 12, 15], index=2)

                maturity, invested, returns = calculate_sip_returns(sip_amt, sip_years, sip_return)
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:1rem">
                        <div style="text-align:center">
                            <div style="font-size:0.75rem;color:rgba(232,224,208,0.5)">INVESTED</div>
                            <div style="font-family:Cinzel,serif;font-size:1.3rem;color:#c4a050">₹{invested:,.0f}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.75rem;color:rgba(232,224,208,0.5)">RETURNS</div>
                            <div style="font-family:Cinzel,serif;font-size:1.3rem;color:#4ade80">₹{returns:,.0f}</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:0.75rem;color:rgba(232,224,208,0.5)">MATURITY VALUE</div>
                            <div style="font-family:Cinzel,serif;font-size:1.3rem;color:#c4a050">₹{maturity:,.0f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with advisor_tab3:
            st.markdown("### 💰 Indian Tax Calculator & Savings")
            if income <= 0:
                st.warning("Set your monthly income in the sidebar first!")
            else:
                tax_data = get_tax_saving_summary(income)

                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    st.markdown(f"""
                    <div class="advice-card">
                        <div style="color:#c4a050;font-family:Cinzel,serif;margin-bottom:0.8rem">NEW TAX REGIME</div>
                        <div style="font-size:1.5rem;font-family:Cinzel,serif">₹{tax_data['tax_new_regime']:,.0f}</div>
                        <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">No deductions needed. Simpler filing.</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_t2:
                    st.markdown(f"""
                    <div class="advice-card">
                        <div style="color:#c4a050;font-family:Cinzel,serif;margin-bottom:0.8rem">OLD REGIME + DEDUCTIONS</div>
                        <div style="font-size:1.5rem;font-family:Cinzel,serif">₹{tax_data['tax_old_with_deductions']:,.0f}</div>
                        <div style="font-size:0.8rem;color:rgba(232,224,208,0.5)">With 80C + 80D + NPS deductions.</div>
                    </div>
                    """, unsafe_allow_html=True)

                better = tax_data['better_regime']
                tax_benefit = tax_data['tax_new_regime'] - tax_data['tax_old_with_deductions']
                if better == "old":
                    st.success(f"✅ Old regime saves you ₹{tax_benefit:,.0f}/year! Invest in 80C instruments.")
                else:
                    st.info(f"ℹ️ New regime is better for you by ₹{abs(tax_benefit):,.0f}/year. No need for complex investments.")

                st.markdown("### 🎯 80C Investment Recommendations")
                recs = get_80c_recommendations(income, 20)
                for rec in recs:
                    with st.expander(f"{rec['icon']} {rec['product']} — ₹{rec['monthly_amount']:,}/month"):
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.markdown(f"**Annual Amount:** ₹{rec['annual_amount']:,}")
                            st.markdown(f"**Risk Level:** {rec['risk']}")
                        with col_r2:
                            st.markdown(f"**Platform:** {rec['platform']}")
                        st.markdown(f"**Benefit:** {rec['benefit']}")

        with advisor_tab1:
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


# ═══ BOOK ADVISOR PAGE ════════════════════════════════════════════
elif page == "📚 Book Advisor":
    st.markdown('<div class="section-header">FINANCIAL BOOK ADVISOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Upload any financial book PDF and get personalized advice based on its principles applied to YOUR spending!</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Upload Your Book")
        st.markdown("**Supported books:**")
        st.markdown("- Rich Dad Poor Dad — Robert Kiyosaki")
        st.markdown("- The Intelligent Investor — Benjamin Graham")
        st.markdown("- Let's Talk Money — Monika Halan")
        st.markdown("- Psychology of Money — Morgan Housel")
        st.markdown("- Or any other financial book PDF!")

        uploaded_pdf = st.file_uploader(
            "Upload Financial Book PDF",
            type=['pdf'],
            label_visibility="collapsed"
        )

        if uploaded_pdf:
            with st.spinner("Reading book..."):
                pdf_text, total_pages = extract_text_from_pdf(uploaded_pdf)

            if pdf_text:
                st.success(f"Book uploaded! {total_pages} pages read successfully.")
                with st.expander("Preview extracted text"):
                    st.text(pdf_text[:500] + "...")
            else:
                st.error("Could not extract text. Try another PDF.")

    with col2:
        st.markdown("### Book-Based Advice")
        if uploaded_pdf and pdf_text:
            now = datetime.now()
            income = st.session_state.get('monthly_income', 0)
            cat_totals = get_category_totals(now.year, now.month)

            if income <= 0:
                st.warning("Please set your monthly income in the sidebar first!")
            else:
                if st.button("Generate Book-Based Advice", use_container_width=True):
                    with st.spinner("Applying book wisdom to your finances..."):
                        advice = generate_book_based_advice(
                            pdf_text,
                            uploaded_pdf.name,
                            cat_totals,
                            income
                        )
                    st.markdown(advice)
        else:
            st.info("Upload a financial book PDF on the left to get started!")

    st.markdown('<div class="section-header" style="margin-top:2rem">FEATURED FINANCIAL BOOKS</div>', unsafe_allow_html=True)
    books = [
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "Assets vs Liabilities"),
        ("The Intelligent Investor", "Benjamin Graham", "Value Investing"),
        ("Let's Talk Money", "Monika Halan", "Indian Personal Finance"),
        ("Psychology of Money", "Morgan Housel", "Behavioral Finance"),
        ("The Millionaire Next Door", "Thomas Stanley", "Wealth Building"),
    ]
    cols = st.columns(3)
    for i, (title, author, theme) in enumerate(books):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="advice-card" style="padding:1rem; margin-bottom:0.5rem">
                <div style="color:#c4a050; font-weight:bold; font-size:0.9rem">{title}</div>
                <div style="font-size:0.8rem; color:rgba(232,224,208,0.7)">by {author}</div>
                <div style="font-size:0.75rem; color:rgba(232,224,208,0.5); margin-top:0.3rem">{theme}</div>
            </div>
            """, unsafe_allow_html=True)


# ═══ SPLITWISE PAGE ════════════════════════════════════════════
elif page == "🤝 Splitwise":
    st.markdown('<div class="section-header">SPLITWISE GROUP EXPENSES</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Import your group expenses from Splitwise and analyze your shared spending!</div>', unsafe_allow_html=True)

    # Get Splitwise API key
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
        )

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
