import PyPDF2
import io
import re

# Popular financial books and their key principles
KNOWN_BOOKS = {
    "rich dad poor dad": {
        "author": "Robert Kiyosaki",
        "key_principles": [
            "The rich don't work for money — they make money work for them.",
            "An asset puts money in your pocket. A liability takes money out.",
            "The poor and middle class work for money. The rich have money work for them.",
            "Financial education is more important than academic education.",
            "Build assets, minimize liabilities.",
        ],
        "indian_advice": "Focus on building assets like REITs, dividend stocks, and rental income. Avoid EMIs on depreciating items."
    },
    "intelligent investor": {
        "author": "Benjamin Graham",
        "key_principles": [
            "Invest with a margin of safety.",
            "Mr. Market is your servant, not your guide.",
            "The stock market is a device for transferring money from the impatient to the patient.",
            "Never lose money. Never forget rule #1.",
            "Price is what you pay, value is what you get.",
        ],
        "indian_advice": "Look for undervalued NSE/BSE stocks with strong fundamentals. Use SIP in index funds for consistent returns."
    },
    "let's talk money": {
        "author": "Monika Halan",
        "key_principles": [
            "Use the three-account system: income, spending, and investment accounts.",
            "Term insurance and health insurance before any investment.",
            "Emergency fund of 6 months expenses first.",
            "Mutual funds via SIP for long-term wealth creation.",
            "Keep financial products simple — if you don't understand it, don't buy it.",
        ],
        "indian_advice": "Perfect for Indian context — follow the three-jar system with SBI/HDFC savings, term insurance, and Nifty 50 SIP."
    },
    "psychology of money": {
        "author": "Morgan Housel",
        "key_principles": [
            "Wealth is what you don't spend.",
            "Getting money and keeping money are different skills.",
            "Compounding works best when you let it run for a long time.",
            "Saving is the gap between your ego and your income.",
            "Reasonable beats rational in financial decisions.",
        ],
        "indian_advice": "Start SIP early and never stop — even ₹1000/month from age 22 becomes ₹1 crore by 60 at 12% returns."
    },
    "the millionaire next door": {
        "author": "Thomas Stanley",
        "key_principles": [
            "Wealth is built through frugality and discipline, not high income.",
            "Live below your means consistently.",
            "Invest early and consistently.",
            "Avoid lifestyle inflation as income grows.",
            "Financial independence over social status.",
        ],
        "indian_advice": "Avoid upgrading lifestyle with every salary hike. Invest the increment instead — this is the fastest path to financial freedom."
    }
}

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        # Extract first 50 pages max to keep it fast
        max_pages = min(50, len(pdf_reader.pages))
        for page_num in range(max_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        return text, len(pdf_reader.pages)
    except Exception as e:
        return "", 0

def identify_book(text, filename=""):
    """Try to identify the book from text content or filename"""
    text_lower = text.lower()
    filename_lower = filename.lower()
    
    for book_key, book_data in KNOWN_BOOKS.items():
        # Check filename first
        if any(word in filename_lower for word in book_key.split()):
            return book_key, book_data
        # Check content
        if book_key in text_lower or book_data['author'].lower() in text_lower:
            return book_key, book_data
    
    return None, None

def extract_key_financial_concepts(text):
    """Extract financial concepts mentioned in the book"""
    concepts = {
        "savings": ["save", "saving", "savings", "emergency fund"],
        "investment": ["invest", "investment", "portfolio", "stocks", "mutual fund", "sip"],
        "debt": ["debt", "loan", "liability", "emi", "credit"],
        "income": ["income", "salary", "earn", "revenue", "cash flow"],
        "budgeting": ["budget", "expense", "spending", "frugal", "live below"],
        "insurance": ["insurance", "term", "health cover", "protection"],
        "tax": ["tax", "deduction", "80c", "elss", "ppf"],
    }
    
    found_concepts = []
    text_lower = text.lower()
    
    for concept, keywords in concepts.items():
        if any(kw in text_lower for kw in keywords):
            found_concepts.append(concept)
    
    return found_concepts

def generate_book_based_advice(pdf_text, filename, category_totals, total_income):
    """Generate financial advice based on uploaded book + user spending"""
    
    # Try to identify the book
    book_key, book_data = identify_book(pdf_text, filename)
    
    # Extract concepts from text
    concepts = extract_key_financial_concepts(pdf_text)
    
    # Calculate spending summary
    total_expenses = category_totals['total'].sum() if not category_totals.empty else 0
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    advice_parts = []
    
    if book_key and book_data:
        advice_parts.append(f"## 📚 Based on \"{book_key.title()}\" by {book_data['author']}")
        advice_parts.append(f"\n### Key Principles from the Book:")
        for principle in book_data['key_principles']:
            advice_parts.append(f"- *\"{principle}\"*")
        
        advice_parts.append(f"\n### Indian Context:")
        advice_parts.append(book_data['indian_advice'])
    else:
        advice_parts.append("## 📚 Based on Your Uploaded Financial Book")
        advice_parts.append(f"Found these financial topics in your book: {', '.join(concepts)}")
    
    # Personalized advice based on spending
    advice_parts.append(f"\n### 💰 Applied to Your Finances:")
    
    if total_income > 0:
        advice_parts.append(f"Your current savings rate: **{savings_rate:.1f}%**")
        
        if savings_rate < 20:
            advice_parts.append("⚠️ The book's core message applies directly to you — you need to increase your savings rate to at least 20%.")
        elif savings_rate >= 30:
            advice_parts.append("✅ Great savings rate! Now focus on investing that surplus wisely as the book suggests.")
        
        # Top spending category advice
        if not category_totals.empty:
            top_category = category_totals.loc[category_totals['total'].idxmax(), 'category']
            top_amount = category_totals['total'].max()
            advice_parts.append(f"\nYour highest expense is **{top_category}** at ₹{top_amount:,.0f}.")
            
            if book_key == "rich dad poor dad":
                advice_parts.append(f"Ask yourself: Is this ₹{top_amount:,.0f} going towards an ASSET or a LIABILITY?")
            elif book_key == "intelligent investor":
                advice_parts.append(f"Apply margin of safety thinking — could you reduce {top_category} by 20% and invest the difference?")
            elif book_key == "let's talk money":
                advice_parts.append(f"Monika Halan would suggest putting at least 20% of your income into your investment jar before spending on {top_category}.")
            elif book_key == "psychology of money":
                advice_parts.append(f"Remember — wealth is what you DON'T spend. Consider if all ₹{top_amount:,.0f} on {top_category} is truly necessary.")
    
    # Action steps
    advice_parts.append(f"\n### 🎯 Your 3 Action Steps from this Book:")
    if book_key and book_data:
        if book_key == "rich dad poor dad":
            advice_parts.append("1. List all your assets vs liabilities this month")
            advice_parts.append("2. Start one asset-building activity — even ₹500/month SIP counts")
            advice_parts.append("3. Before next purchase ask: 'Is this an asset or liability?'")
        elif book_key == "intelligent investor":
            advice_parts.append("1. Open a Zerodha/Groww account if you don't have one")
            advice_parts.append("2. Start a Nifty 50 index fund SIP — most value for least risk")
            advice_parts.append("3. Never invest in something you don't fully understand")
        elif book_key == "let's talk money":
            advice_parts.append("1. Set up 3 separate accounts: income, spending, investment")
            advice_parts.append("2. Get term insurance (10x annual income) if you haven't already")
            advice_parts.append("3. Start a ₹1,000/month SIP in a Nifty 50 index fund")
        elif book_key == "psychology of money":
            advice_parts.append("1. Automate your savings — set up auto-SIP on salary day")
            advice_parts.append("2. Never check your portfolio more than once a month")
            advice_parts.append("3. Focus on savings rate, not investment returns")
        else:
            advice_parts.append("1. Apply the book's core principle to your biggest expense category")
            advice_parts.append("2. Set a savings target of at least 20% of income")
            advice_parts.append("3. Start a monthly SIP regardless of amount")
    
    return "\n".join(advice_parts)
