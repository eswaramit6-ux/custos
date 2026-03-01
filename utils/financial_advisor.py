import google.generativeai as genai

FINANCIAL_GURUS = {
    "Warren Buffett": {
        "philosophy": "Value investing, long-term thinking, living below your means",
        "principles": [
            "Never lose money. Rule No. 2: Never forget rule No. 1.",
            "Don't save what is left after spending; spend what is left after saving.",
            "Price is what you pay. Value is what you get.",
            "The stock market transfers money from the Active to the Patient.",
        ],
        "indian_context": "Focus on quality Indian blue-chip stocks like Reliance, TCS, HDFC. Consider long-term SIPs in index funds."
    },
    "Robert Kiyosaki": {
        "philosophy": "Assets vs liabilities, passive income, financial education",
        "principles": [
            "The rich don't work for money — they make money work for them.",
            "An asset puts money in your pocket. A liability takes money out.",
            "It's not how much money you make, but how much money you keep.",
            "Financial freedom is available to those who learn about it and work for it.",
        ],
        "indian_context": "Build assets through real estate, REITs, dividend stocks. Reduce liabilities like unnecessary EMIs."
    },
    "Ramit Sethi": {
        "philosophy": "Conscious spending, automation, guilt-free spending on what you love",
        "principles": [
            "Spend extravagantly on things you love, cut costs mercilessly on things you don't.",
            "Automate your finances so you don't have to think about it.",
            "Invest early and consistently — time in the market beats timing the market.",
            "Focus on big wins, not cutting out small pleasures.",
        ],
        "indian_context": "Set up automatic SIPs, emergency fund first, then invest in NPS, ELSS for tax savings under 80C."
    },
    "Benjamin Graham": {
        "philosophy": "Margin of safety, intrinsic value, disciplined investing",
        "principles": [
            "Invest only when there is a margin of safety.",
            "The intelligent investor is a realist who sells to optimists and buys from pessimists.",
            "In the short run the market is a voting machine, in the long run a weighing machine.",
        ],
        "indian_context": "Apply value investing to NSE/BSE stocks. Look for companies with strong fundamentals, low P/E ratios."
    }
}

INDIAN_FINANCIAL_ADVICE = {
    "Tax Saving": {
        "Section 80C": "Invest up to ₹1.5L in ELSS, PPF, EPF, NSC, tax-saving FDs, LIC premiums",
        "Section 80D": "Health insurance premium deduction up to ₹25,000 (₹50,000 for senior citizens)",
        "Section 24": "Home loan interest deduction up to ₹2L per year",
        "NPS": "Additional ₹50,000 deduction under Section 80CCD(1B)",
        "HRA": "House Rent Allowance exemption if living in rented accommodation"
    },
    "Investment Options": {
        "SIP": "Systematic Investment Plan — invest as little as ₹500/month in mutual funds",
        "PPF": "Public Provident Fund — 7.1% interest, 15-year lock-in, tax-free returns",
        "ELSS": "Equity Linked Savings Scheme — 3-year lock-in, market returns, 80C benefit",
        "FD": "Fixed Deposit — safe, 6-7% returns, good for emergency fund",
        "Stocks": "Direct equity — higher risk, higher returns via Zerodha, Groww, Upstox",
        "Gold": "Sovereign Gold Bonds (SGBs) — 2.5% interest + gold price appreciation"
    },
    "Budgeting Rules": {
        "50-30-20 Rule": "50% needs, 30% wants, 20% savings/investments",
        "Emergency Fund": "Keep 3-6 months of expenses in a liquid fund or savings account",
        "Insurance First": "Term insurance (10-15x annual income) + health insurance before investing"
    }
}

SPENDING_INSIGHTS = {
    "Food & Dining": {"healthy_percent": 15, "tip": "Try cooking at home 4-5 days a week to reduce dining costs by 40%."},
    "Transportation": {"healthy_percent": 10, "tip": "Consider a metro pass or carpooling to cut commute costs."},
    "Shopping": {"healthy_percent": 10, "tip": "Wait 48 hours before any purchase over ₹2,000 to avoid impulse buying."},
    "Entertainment": {"healthy_percent": 5, "tip": "Bundle OTT subscriptions with family to save on streaming costs."},
    "Groceries": {"healthy_percent": 15, "tip": "Buy monthly staples in bulk. Use quick delivery apps only for urgent items."},
    "Utilities & Bills": {"healthy_percent": 10, "tip": "Switch to annual plans for mobile/broadband — typically 20-30% cheaper."}
}

def get_personalized_advice(expenses_summary, total_income, api_key, guru="Warren Buffett"):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        guru_data = FINANCIAL_GURUS.get(guru, FINANCIAL_GURUS["Warren Buffett"])

        prompt = f"""You are a financial advisor channeling the wisdom of {guru}.

GURU PHILOSOPHY: {guru_data['philosophy']}
KEY PRINCIPLES: {' | '.join(guru_data['principles'])}
INDIAN CONTEXT: {guru_data['indian_context']}

USER'S FINANCIAL DATA:
Monthly Income: ₹{total_income:,.0f}
Spending Summary:
{expenses_summary}

INDIAN INVESTMENT OPTIONS: {str(INDIAN_FINANCIAL_ADVICE['Investment Options'])}
TAX SAVING: {str(INDIAN_FINANCIAL_ADVICE['Tax Saving'])}

Provide personalized financial advice in the style of {guru}. Be specific, actionable, reference actual Indian financial products (SIP, PPF, ELSS, etc.).

Structure:
1. **Assessment** (2-3 sentences on their spending)
2. **Top 3 Action Items** (specific, numbered, actionable)
3. **Investment Recommendation** (specific Indian products)
4. **Motivational Quote** from {guru}

Keep it under 300 words. Be direct and practical."""

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Unable to generate advice: {str(e)}"

def analyze_spending_health(category_totals, total_income):
    alerts = []
    suggestions = []
    if total_income <= 0:
        return alerts, suggestions
    for _, row in category_totals.iterrows():
        category = row['category']
        total = row['total']
        percent = (total / total_income) * 100
        if category in SPENDING_INSIGHTS:
            healthy = SPENDING_INSIGHTS[category]['healthy_percent']
            tip = SPENDING_INSIGHTS[category]['tip']
            if percent > healthy * 1.5:
                alerts.append(f"⚠️ **{category}**: ₹{total:,.0f} is {percent:.1f}% of income (recommended: {healthy}%)")
                suggestions.append(f"💡 {tip}")
            elif percent > healthy:
                suggestions.append(f"📊 **{category}** at {percent:.1f}% — slightly above {healthy}% guideline. {tip}")
    return alerts, suggestions

def get_savings_rate_advice(total_expenses, total_income):
    if total_income <= 0:
        return ""
    savings = total_income - total_expenses
    savings_rate = (savings / total_income) * 100
    if savings_rate < 0:
        return "🚨 **Critical**: You're spending more than you earn! Immediate budget review needed."
    elif savings_rate < 10:
        return f"⚠️ **Low savings rate**: {savings_rate:.1f}%. Target at least 20%. Consider the 50-30-20 rule."
    elif savings_rate < 20:
        return f"📈 **Improving**: {savings_rate:.1f}% savings rate. Push towards 20% by reducing discretionary spending."
    elif savings_rate < 30:
        return f"✅ **Good**: {savings_rate:.1f}% savings rate. Consider investing surplus in ELSS or index funds."
    else:
        return f"🌟 **Excellent**: {savings_rate:.1f}% savings rate! Maximize your ₹1.5L 80C limit and explore NPS."
