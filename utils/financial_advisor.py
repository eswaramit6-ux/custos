# Rule-based Financial Advisor — No API needed!

FINANCIAL_GURUS = {
    "Warren Buffett": {
        "philosophy": "Value investing, long-term thinking, living below your means",
        "principles": [
            "Never lose money. Rule No. 2: Never forget rule No. 1.",
            "Don't save what is left after spending; spend what is left after saving.",
            "Price is what you pay. Value is what you get.",
            "The stock market transfers money from the Active to the Patient.",
            "It's far better to buy a wonderful company at a fair price than a fair company at a wonderful price.",
        ],
        "indian_context": "Focus on quality Indian blue-chip stocks like Reliance, TCS, HDFC. Consider long-term SIPs in index funds.",
        "icon": "🏦"
    },
    "Robert Kiyosaki": {
        "philosophy": "Assets vs liabilities, passive income, financial education",
        "principles": [
            "The rich don't work for money — they make money work for them.",
            "An asset puts money in your pocket. A liability takes money out.",
            "It's not how much money you make, but how much money you keep.",
            "Financial freedom is available to those who learn about it and work for it.",
            "The more you learn, the more you earn.",
        ],
        "indian_context": "Build assets through real estate, REITs, dividend stocks. Reduce liabilities like unnecessary EMIs.",
        "icon": "💼"
    },
    "Ramit Sethi": {
        "philosophy": "Conscious spending, automation, guilt-free spending on what you love",
        "principles": [
            "Spend extravagantly on things you love, cut costs mercilessly on things you don't.",
            "Automate your finances so you don't have to think about it.",
            "Invest early and consistently — time in the market beats timing the market.",
            "Focus on big wins, not cutting out small pleasures.",
            "The 85% solution: Getting started is more important than being perfect.",
        ],
        "indian_context": "Set up automatic SIPs, emergency fund first, then invest in NPS, ELSS for tax savings under 80C.",
        "icon": "🎯"
    },
    "Benjamin Graham": {
        "philosophy": "Margin of safety, intrinsic value, disciplined investing",
        "principles": [
            "Invest only when there is a margin of safety.",
            "The intelligent investor is a realist who sells to optimists and buys from pessimists.",
            "In the short run the market is a voting machine, in the long run a weighing machine.",
            "Confronted with a challenge to distill the secret of sound investment into three words, we venture the motto: Margin of Safety.",
        ],
        "indian_context": "Apply value investing to NSE/BSE stocks. Look for companies with strong fundamentals and low P/E ratios.",
        "icon": "📚"
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
    "Transportation": {"healthy_percent": 10, "tip": "Consider a metro pass or carpooling to cut commute costs significantly."},
    "Shopping": {"healthy_percent": 10, "tip": "Wait 48 hours before any purchase over ₹2,000 to avoid impulse buying."},
    "Entertainment": {"healthy_percent": 5, "tip": "Bundle OTT subscriptions with family to save on streaming costs."},
    "Groceries": {"healthy_percent": 15, "tip": "Buy monthly staples in bulk. Use quick delivery apps only for urgent items."},
    "Utilities & Bills": {"healthy_percent": 10, "tip": "Switch to annual plans for mobile/broadband — typically 20-30% cheaper."},
    "Healthcare": {"healthy_percent": 5, "tip": "Invest in a good health insurance plan to avoid large unexpected medical bills."},
    "Personal Care": {"healthy_percent": 5, "tip": "Look for combo deals and monthly subscriptions for personal care products."},
    "Education": {"healthy_percent": 10, "tip": "Look for free resources on YouTube and Coursera before paying for courses."},
}

# Rule-based advice templates per guru
GURU_ADVICE_TEMPLATES = {
    "Warren Buffett": {
        "high_food": "Your food spending is high. As I always say — 'Do not save what is left after spending, but spend what is left after saving.' Cut dining out and redirect that money into index fund SIPs.",
        "high_shopping": "Excessive shopping is a liability trap. Ask yourself — does this purchase put money IN my pocket or TAKE money out? Stick to needs, invest the rest in quality assets.",
        "high_entertainment": "Entertainment spending should be minimal. Every rupee spent on entertainment today is a rupee that cannot compound over 20 years. Think long term.",
        "good_savings": "Excellent savings rate! Now put that money to work. Invest in fundamentally strong Indian companies — TCS, HDFC Bank, Reliance. Buy and hold for decades.",
        "low_savings": "Your savings rate is dangerously low. Rule #1: Never lose money. Rule #2: Never forget Rule #1. Stop unnecessary expenses immediately and start a SIP today.",
        "investment_tip": "Start a monthly SIP in a Nifty 50 index fund. Even ₹1,000/month compounded over 20 years at 12% becomes ₹9.9 lakhs. Time in market beats timing the market.",
    },
    "Robert Kiyosaki": {
        "high_food": "You're spending too much on food — a pure liability! Rich people buy assets first, then spend from the returns. Cut food expenses and buy a REIT or dividend stock instead.",
        "high_shopping": "Shopping is the #1 liability trap of the middle class! Every item you buy loses value. Instead, buy assets that appreciate — stocks, gold, real estate.",
        "high_entertainment": "The poor spend on entertainment, the rich invest in education. Cut Netflix, buy a finance book. Knowledge is the best asset you can own.",
        "good_savings": "Good savings! Now convert those savings into ASSETS immediately. Don't let cash sit idle — inflation eats it. Put it in REITs, dividend stocks, or start a side hustle.",
        "low_savings": "You're trapped in the Rat Race! Income - Expenses = nothing. You need to build assets that generate passive income. Start with a ₹500 SIP today, no matter what.",
        "investment_tip": "Focus on passive income streams. Start with Sovereign Gold Bonds (2.5% interest + gold appreciation) and ELSS mutual funds for tax-free returns.",
    },
    "Ramit Sethi": {
        "high_food": "I actually don't mind spending on food IF you love it. But if you're spending on mediocre meals just out of habit — cut those and spend only on food experiences you truly love.",
        "high_shopping": "Unconscious shopping is the enemy. Use my 72-hour rule — wait 3 days before any purchase. If you still want it, buy it guilt-free. If not, invest that money.",
        "high_entertainment": "Entertainment is fine if it's intentional! But automate your savings FIRST. Set up auto-SIP on salary day so you never have to think about saving again.",
        "good_savings": "Love the savings rate! Now automate everything — salary comes in, SIP goes out automatically, bills paid automatically. Spend the rest guilt-free on what you love!",
        "low_savings": "The 85% solution — you don't need to be perfect, just start. Set up even a ₹500 auto-SIP right now. Starting beats perfecting every single time.",
        "investment_tip": "Automate your finances: Day 1 of month — SIP deducted automatically. Bills paid automatically. Whatever remains — spend GUILT FREE on things you love!",
    },
    "Benjamin Graham": {
        "high_food": "Disciplined spending is the foundation of disciplined investing. Your food expenses exceed the recommended margin. Reduce by 20% and redirect to a value-oriented mutual fund.",
        "high_shopping": "Every purchase should have a margin of safety — meaning you should be able to afford it AND still save 20%. If you can't, don't buy it.",
        "high_entertainment": "Entertainment provides zero financial return. Apply the margin of safety principle — only spend on entertainment after your savings target is met.",
        "good_savings": "A sound savings rate! Now apply margin of safety to investing — never invest in overvalued assets. Look for fundamentally strong NSE stocks trading below intrinsic value.",
        "low_savings": "Without savings there can be no investment, and without investment there can be no financial security. Achieve a minimum 20% savings rate before any discretionary spending.",
        "investment_tip": "Invest in undervalued quality companies on NSE/BSE. Look for low P/E ratios, strong balance sheets, consistent dividends. Hold for minimum 5 years.",
    }
}

def generate_rule_based_advice(category_totals, total_income, guru="Warren Buffett"):
    """Generate smart rule-based financial advice based on spending patterns"""
    
    if total_income <= 0:
        return "Please set your monthly income in the sidebar to get personalized advice."

    guru_data = FINANCIAL_GURUS.get(guru, FINANCIAL_GURUS["Warren Buffett"])
    templates = GURU_ADVICE_TEMPLATES.get(guru, GURU_ADVICE_TEMPLATES["Warren Buffett"])
    
    total_expenses = category_totals['total'].sum()
    savings = total_income - total_expenses
    savings_rate = (savings / total_income) * 100

    # Build spending dict
    spending = {}
    for _, row in category_totals.iterrows():
        spending[row['category']] = {
            'amount': row['total'],
            'percent': (row['total'] / total_income) * 100
        }

    advice_parts = []

    # ── ASSESSMENT ──
    advice_parts.append("## 📊 Assessment")
    if savings_rate >= 30:
        advice_parts.append(f"Your savings rate is **{savings_rate:.1f}%** — outstanding financial discipline! You're saving ₹{savings:,.0f} this month.")
    elif savings_rate >= 20:
        advice_parts.append(f"Your savings rate is **{savings_rate:.1f}%** — solid performance! You're saving ₹{savings:,.0f} this month.")
    elif savings_rate >= 10:
        advice_parts.append(f"Your savings rate is **{savings_rate:.1f}%** — room for improvement. Target 20% savings rate as a minimum.")
    elif savings_rate >= 0:
        advice_parts.append(f"Your savings rate is only **{savings_rate:.1f}%** — this needs immediate attention. You're saving just ₹{savings:,.0f} from ₹{total_income:,.0f} income.")
    else:
        advice_parts.append(f"⚠️ **You are overspending by ₹{abs(savings):,.0f}!** Your expenses exceed your income — this is a financial emergency.")

    # ── SPENDING ANALYSIS ──
    advice_parts.append("\n## 🔍 Spending Analysis")
    
    problem_areas = []
    good_areas = []

    for category, data in spending.items():
        if category in SPENDING_INSIGHTS:
            healthy = SPENDING_INSIGHTS[category]['healthy_percent']
            if data['percent'] > healthy * 1.3:
                problem_areas.append((category, data['amount'], data['percent'], healthy))
            elif data['percent'] <= healthy:
                good_areas.append((category, data['amount'], data['percent']))

    if problem_areas:
        for cat, amount, pct, healthy in problem_areas[:3]:
            advice_parts.append(f"- ⚠️ **{cat}**: ₹{amount:,.0f} ({pct:.1f}% of income) — recommended max is {healthy}%")
    
    if good_areas:
        for cat, amount, pct in good_areas[:2]:
            advice_parts.append(f"- ✅ **{cat}**: ₹{amount:,.0f} ({pct:.1f}%) — well managed!")

    # ── GURU SPECIFIC ADVICE ──
    advice_parts.append(f"\n## 💡 {guru}'s Advice For You")

    # Check specific high spending areas
    food_pct = spending.get("Food & Dining", {}).get('percent', 0)
    shopping_pct = spending.get("Shopping", {}).get('percent', 0)
    entertainment_pct = spending.get("Entertainment", {}).get('percent', 0)

    if food_pct > 20:
        advice_parts.append(f"**On your food spending:** {templates['high_food']}")
    if shopping_pct > 15:
        advice_parts.append(f"**On your shopping:** {templates['high_shopping']}")
    if entertainment_pct > 8:
        advice_parts.append(f"**On entertainment:** {templates['high_entertainment']}")

    if savings_rate >= 20:
        advice_parts.append(f"**On your savings:** {templates['good_savings']}")
    else:
        advice_parts.append(f"**On your savings rate:** {templates['low_savings']}")

    # ── TOP 3 ACTION ITEMS ──
    advice_parts.append("\n## 🎯 Top 3 Action Items")
    
    actions = []
    
    if savings_rate < 20:
        gap = total_income * 0.20 - savings
        actions.append(f"Increase savings by ₹{gap:,.0f}/month to reach the 20% savings target")
    
    if problem_areas:
        top_problem = problem_areas[0]
        target = total_income * (top_problem[3] / 100)
        save = top_problem[1] - target
        actions.append(f"Reduce **{top_problem[0]}** spending by ₹{save:,.0f} to bring it within healthy limits")

    actions.append(f"Start or increase a monthly SIP — even ₹{min(max(int(savings * 0.5), 500), 5000):,}/month makes a significant difference over time")
    
    if total_income > 50000:
        actions.append("Maximize your Section 80C deduction (₹1.5L limit) through ELSS or PPF to save on taxes")
    else:
        actions.append("Build an emergency fund of at least ₹{:,.0f} (3 months expenses) in a liquid fund".format(int(total_expenses * 3)))

    for i, action in enumerate(actions[:3], 1):
        advice_parts.append(f"{i}. {action}")

    # ── INVESTMENT RECOMMENDATION ──
    advice_parts.append("\n## 📈 Investment Recommendation")
    advice_parts.append(templates['investment_tip'])

    if savings > 0:
        sip_amount = max(int(savings * 0.6), 500)
        fd_amount = max(int(savings * 0.2), 500)
        advice_parts.append(f"\nBased on your ₹{savings:,.0f} monthly savings, consider:")
        advice_parts.append(f"- **₹{sip_amount:,}/month** → Nifty 50 Index Fund SIP")
        advice_parts.append(f"- **₹{fd_amount:,}/month** → Emergency Fund FD")

    # ── MOTIVATIONAL QUOTE ──
    advice_parts.append(f"\n## 💬 {guru} Says")
    import random
    quote = random.choice(guru_data['principles'])
    advice_parts.append(f"*\"{quote}\"*")

    return "\n".join(advice_parts)


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


def calculate_financial_health_score(category_totals, total_income):
    """Calculate a financial health score out of 100"""
    if total_income <= 0:
        return 0, "No income data"

    score = 100
    reasons = []

    total_expenses = category_totals['total'].sum()
    savings_rate = ((total_income - total_expenses) / total_income) * 100

    # Savings rate scoring (40 points)
    if savings_rate >= 30:
        reasons.append("✅ Excellent savings rate (+40)")
    elif savings_rate >= 20:
        score -= 10
        reasons.append("✅ Good savings rate (+30)")
    elif savings_rate >= 10:
        score -= 20
        reasons.append("⚠️ Low savings rate (+20)")
    elif savings_rate >= 0:
        score -= 35
        reasons.append("⚠️ Very low savings rate (+5)")
    else:
        score -= 40
        reasons.append("🚨 Overspending (-40)")

    # Category overspending (60 points)
    spending = {row['category']: (row['total'] / total_income) * 100
                for _, row in category_totals.iterrows()}

    overspend_count = 0
    for category, pct in spending.items():
        if category in SPENDING_INSIGHTS:
            healthy = SPENDING_INSIGHTS[category]['healthy_percent']
            if pct > healthy * 1.5:
                score -= 10
                overspend_count += 1

    if overspend_count == 0:
        reasons.append("✅ All categories within healthy limits")
    else:
        reasons.append(f"⚠️ {overspend_count} categories overspent")

    score = max(0, min(100, score))

    if score >= 80:
        grade = "A — Excellent 🌟"
    elif score >= 60:
        grade = "B — Good ✅"
    elif score >= 40:
        grade = "C — Needs Work ⚠️"
    else:
        grade = "D — Critical 🚨"

    return score, grade, reasons
