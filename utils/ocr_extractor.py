import re
import pytesseract
import shutil
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
from PIL import Image
import PIL.ImageEnhance as enhance
from datetime import date

# ─── EXPANDED INDIAN CATEGORIES ────────────────────────────────────────────────
CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Education", "Utilities & Bills", "Groceries",
    "Travel", "Investment & Savings", "Personal Care", "Rent & Housing",
    "EMI & Loans", "Chai & Snacks", "Religious & Donations", "Family & Gifts",
    "Others"
]

# ─── UPI APP DETECTION ─────────────────────────────────────────────────────────
UPI_APPS = {
    'phonepe': 'PhonePe',
    'gpay': 'Google Pay',
    'google pay': 'Google Pay',
    'paytm': 'Paytm',
    'bhim': 'BHIM UPI',
    'amazon pay': 'Amazon Pay',
    'cred': 'CRED',
    'mobikwik': 'MobiKwik',
    'freecharge': 'FreeCharge',
    'airtel money': 'Airtel Money',
    'jio money': 'JioMoney',
}

# ─── EXPANDED INDIAN MERCHANT LIST ─────────────────────────────────────────────
INDIAN_MERCHANTS = {
    # Food & Dining
    'zomato': 'Food & Dining',
    'swiggy': 'Food & Dining',
    'dominos': 'Food & Dining',
    'dominoes': 'Food & Dining',
    'pizza hut': 'Food & Dining',
    'kfc': 'Food & Dining',
    'mcdonalds': 'Food & Dining',
    'mcdonald': 'Food & Dining',
    'subway': 'Food & Dining',
    'burger king': 'Food & Dining',
    'haldiram': 'Food & Dining',
    'barbeque nation': 'Food & Dining',
    'cafe coffee day': 'Food & Dining',
    'starbucks': 'Food & Dining',
    'chaayos': 'Chai & Snacks',
    'chai point': 'Chai & Snacks',
    'tea post': 'Chai & Snacks',
    'magic pin': 'Food & Dining',
    'eatsure': 'Food & Dining',
    'box8': 'Food & Dining',
    'freshmenu': 'Food & Dining',
    'faasos': 'Food & Dining',
    'rebel foods': 'Food & Dining',

    # Groceries
    'bigbasket': 'Groceries',
    'blinkit': 'Groceries',
    'zepto': 'Groceries',
    'dunzo': 'Groceries',
    'grofers': 'Groceries',
    'jiomart': 'Groceries',
    'dmart': 'Groceries',
    'reliance fresh': 'Groceries',
    'more supermarket': 'Groceries',
    'star bazaar': 'Groceries',
    'spencer': 'Groceries',
    'swiggy instamart': 'Groceries',
    'bb daily': 'Groceries',
    'milkbasket': 'Groceries',
    'country delight': 'Groceries',

    # Transportation
    'uber': 'Transportation',
    'ola': 'Transportation',
    'rapido': 'Transportation',
    'indrive': 'Transportation',
    'meru': 'Transportation',
    'irctc': 'Transportation',
    'redbus': 'Transportation',
    'abhibus': 'Transportation',
    'yatri': 'Transportation',
    'ixigo': 'Transportation',
    'fasttag': 'Transportation',
    'paytm fasttag': 'Transportation',
    'best bus': 'Transportation',
    'metro': 'Transportation',
    'bmtc': 'Transportation',
    'apsrtc': 'Transportation',
    'ksrtc': 'Transportation',
    'msrtc': 'Transportation',

    # Shopping
    'amazon': 'Shopping',
    'flipkart': 'Shopping',
    'myntra': 'Shopping',
    'ajio': 'Shopping',
    'meesho': 'Shopping',
    'nykaa': 'Shopping',
    'snapdeal': 'Shopping',
    'tatacliq': 'Shopping',
    'reliance digital': 'Shopping',
    'croma': 'Shopping',
    'vijay sales': 'Shopping',
    'decathlon': 'Shopping',
    'lifestyle': 'Shopping',
    'shoppers stop': 'Shopping',
    'westside': 'Shopping',
    'zara': 'Shopping',
    'h&m': 'Shopping',
    'pantaloons': 'Shopping',
    'fabindia': 'Shopping',
    'damensch': 'Shopping',
    'bewakoof': 'Shopping',
    'boat': 'Shopping',
    'noise': 'Shopping',

    # Entertainment
    'netflix': 'Entertainment',
    'hotstar': 'Entertainment',
    'disney': 'Entertainment',
    'spotify': 'Entertainment',
    'prime video': 'Entertainment',
    'amazon prime': 'Entertainment',
    'zee5': 'Entertainment',
    'sonyliv': 'Entertainment',
    'voot': 'Entertainment',
    'jiocinema': 'Entertainment',
    'mxplayer': 'Entertainment',
    'bookmyshow': 'Entertainment',
    'pvr': 'Entertainment',
    'inox': 'Entertainment',
    'cinepolis': 'Entertainment',
    'carnival cinemas': 'Entertainment',
    'playo': 'Entertainment',
    'dream11': 'Entertainment',
    'mpl': 'Entertainment',

    # Healthcare
    'apollo': 'Healthcare',
    '1mg': 'Healthcare',
    'netmeds': 'Healthcare',
    'pharmeasy': 'Healthcare',
    'medplus': 'Healthcare',
    'practo': 'Healthcare',
    'lybrate': 'Healthcare',
    'healthkart': 'Healthcare',
    'cult fit': 'Healthcare',
    'cult.fit': 'Healthcare',
    'mfine': 'Healthcare',
    'tata health': 'Healthcare',
    'tata 1mg': 'Healthcare',

    # Education
    'byju': 'Education',
    'byjus': 'Education',
    'unacademy': 'Education',
    'vedantu': 'Education',
    'udemy': 'Education',
    'coursera': 'Education',
    'upgrad': 'Education',
    'simplilearn': 'Education',
    'skillshare': 'Education',
    'toppr': 'Education',
    'doubtnut': 'Education',
    'whitehat jr': 'Education',

    # Utilities & Bills
    'jio': 'Utilities & Bills',
    'airtel': 'Utilities & Bills',
    'vodafone': 'Utilities & Bills',
    'vi ': 'Utilities & Bills',
    'bsnl': 'Utilities & Bills',
    'tata sky': 'Utilities & Bills',
    'dish tv': 'Utilities & Bills',
    'sun direct': 'Utilities & Bills',
    'bescom': 'Utilities & Bills',
    'tneb': 'Utilities & Bills',
    'msedcl': 'Utilities & Bills',
    'bses': 'Utilities & Bills',
    'tpddl': 'Utilities & Bills',
    'mahanagar gas': 'Utilities & Bills',
    'indraprastha gas': 'Utilities & Bills',

    # Travel
    'makemytrip': 'Travel',
    'goibibo': 'Travel',
    'yatra': 'Travel',
    'cleartrip': 'Travel',
    'oyo': 'Travel',
    'airbnb': 'Travel',
    'trivago': 'Travel',
    'booking.com': 'Travel',
    'indigo': 'Travel',
    'air india': 'Travel',
    'spicejet': 'Travel',
    'vistara': 'Travel',
    'akasa': 'Travel',
    'thomas cook': 'Travel',
    'cox and kings': 'Travel',

    # Investment & Savings
    'zerodha': 'Investment & Savings',
    'groww': 'Investment & Savings',
    'upstox': 'Investment & Savings',
    'angel broking': 'Investment & Savings',
    'angel one': 'Investment & Savings',
    'hdfc securities': 'Investment & Savings',
    'icicidirect': 'Investment & Savings',
    'icicid direct': 'Investment & Savings',
    'sbismart': 'Investment & Savings',
    'coinswitch': 'Investment & Savings',
    'wazirx': 'Investment & Savings',
    'kuvera': 'Investment & Savings',
    'paytm money': 'Investment & Savings',
    'et money': 'Investment & Savings',
    'navi': 'Investment & Savings',
    'scripbox': 'Investment & Savings',

    # Personal Care
    'urbanclap': 'Personal Care',
    'urban company': 'Personal Care',
    'mcaffeine': 'Personal Care',
    'mamaearth': 'Personal Care',
    'wow skin': 'Personal Care',
    'sugar cosmetics': 'Personal Care',
    'purplle': 'Personal Care',
    'man matters': 'Personal Care',
    'bombay shaving': 'Personal Care',
    'beardo': 'Personal Care',

    # EMI & Loans
    'bajaj finserv': 'EMI & Loans',
    'hdfc bank emi': 'EMI & Loans',
    'axis bank emi': 'EMI & Loans',
    'icici emi': 'EMI & Loans',
    'emi': 'EMI & Loans',
    'loan': 'EMI & Loans',
    'equitas': 'EMI & Loans',
    'lending kart': 'EMI & Loans',
    'money tap': 'EMI & Loans',
    'slice': 'EMI & Loans',
    'uni card': 'EMI & Loans',

    # Religious & Donations
    'temple': 'Religious & Donations',
    'mandir': 'Religious & Donations',
    'mosque': 'Religious & Donations',
    'church': 'Religious & Donations',
    'gurudwara': 'Religious & Donations',
    'donation': 'Religious & Donations',
    'charity': 'Religious & Donations',
    'give india': 'Religious & Donations',
    'milaap': 'Religious & Donations',
    'ketto': 'Religious & Donations',
    'tirupati': 'Religious & Donations',
    'iskcon': 'Religious & Donations',

    # Family & Gifts
    'archies': 'Family & Gifts',
    'hallmark': 'Family & Gifts',
    'ferns n petals': 'Family & Gifts',
    'fnp': 'Family & Gifts',
    'igp': 'Family & Gifts',
    'giftease': 'Family & Gifts',
    'flowera': 'Family & Gifts',
}

# ─── INDIAN SMS PATTERNS ───────────────────────────────────────────────────────
INDIAN_SMS_PATTERNS = [
    # SBI
    r'sbi.*?(?:debited|credited).*?rs\.?\s*([0-9,]+\.?[0-9]*)',
    # HDFC
    r'hdfc.*?(?:debited|credited).*?(?:rs\.?|inr)\s*([0-9,]+\.?[0-9]*)',
    # ICICI
    r'icici.*?(?:debited|credited).*?(?:rs\.?|inr)\s*([0-9,]+\.?[0-9]*)',
    # General UPI
    r'upi.*?(?:rs\.?|inr|₹)\s*([0-9,]+\.?[0-9]*)',
    # General debit
    r'(?:rs\.?|inr|₹)\s*([0-9,]+\.?[0-9]*).*?(?:debited|deducted|paid)',
]


def detect_upi_app(text):
    """Detect which UPI app was used"""
    text_lower = text.lower()
    for app_key, app_name in UPI_APPS.items():
        if app_key in text_lower:
            return app_name
    return None


def extract_expense_from_image(image, api_key=None):
    try:
        image = image.convert('RGB')
        enhancer = enhance.Contrast(image)
        image = enhancer.enhance(2.0)
        extracted_text = pytesseract.image_to_string(image, config='--psm 6')
        if not extracted_text.strip():
            return {'amount': 0.0, 'date': str(date.today()), 'description': '', 'category': 'Others', 'type': 'debit', 'raw_text': 'No text found', 'upi_app': None}
        result = extract_from_text(extracted_text)
        result['raw_text'] = extracted_text[:300]
        result['upi_app'] = detect_upi_app(extracted_text)
        return result
    except Exception as e:
        return {'amount': 0.0, 'date': str(date.today()), 'description': '', 'category': 'Others', 'type': 'debit', 'raw_text': f'Error: {str(e)}', 'upi_app': None}


def extract_from_text(text):
    result = {'amount': 0.0, 'date': str(date.today()), 'description': '', 'category': 'Others', 'type': 'debit'}

    # Clean text
    clean_text = re.sub(r'\b\d{1,2}:\d{2}\s*(?:am|pm)\b', '', text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\b20\d{2}\b', '', clean_text)
    clean_text = re.sub(r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', '', clean_text, flags=re.IGNORECASE)

    # Cut off at these to avoid picking wrong numbers
    for cutoff in ['debited from', 'credited to', 'utr:']:
        idx = clean_text.lower().find(cutoff)
        if idx != -1:
            clean_text = clean_text[:idx]

    clean_lower = clean_text.lower()
    amount = 0.0

    # PRIORITY 1: Scan Paid to / Received from / Sent to section
    lines = clean_text.split('\n')
    for i, line in enumerate(lines):
        if any(kw in line.lower() for kw in ['paid to', 'received from', 'sent to']):
            decimal_candidates = []
            whole_candidates = []
            for search_line in lines[i:i+5]:
                for n in re.findall(r'\b([0-9,]+\.[0-9]{1,2})\b', search_line):
                    s = n.replace(',', '')
                    v = float(s)
                    if 10 <= v <= 500000:
                        decimal_candidates.append(v)
                    if len(s.split('.')[0]) >= 4:
                        try:
                            trimmed = float(s[1:])
                            if 10 <= trimmed <= 500000:
                                decimal_candidates.append(trimmed)
                        except:
                            pass
                for n in re.findall(r'\b([1-9][0-9]{1,3})\b', search_line):
                    v = float(n)
                    if 10 <= v <= 9999:
                        whole_candidates.append(v)
            candidates = decimal_candidates if decimal_candidates else whole_candidates
            if candidates:
                amount = min(candidates)
            break

    # PRIORITY 2: Indian SMS patterns
    if amount == 0.0:
        for pattern in INDIAN_SMS_PATTERNS:
            m = re.search(pattern, text.lower())
            if m:
                try:
                    v = float(m.group(1).replace(',', ''))
                    if 10 <= v <= 500000:
                        amount = v
                        break
                except:
                    pass

    # PRIORITY 3: rupee symbol (or misread as & @ # % =)
    if amount == 0.0:
        for n in re.findall(r'[₹\u20b9&@#%=]\s*([0-9,]+(?:\.[0-9]{1,2})?)', clean_text):
            try:
                v = float(n.replace(',', ''))
                if 10 <= v <= 500000:
                    amount = v
                    break
            except:
                pass

    # PRIORITY 4: Rs. or INR
    if amount == 0.0:
        for pattern in [r'rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)', r'inr\s*([0-9,]+(?:\.[0-9]{2})?)']:
            m = re.search(pattern, clean_lower)
            if m:
                try:
                    amount = float(m.group(1).replace(',', ''))
                    break
                except:
                    pass

    # PRIORITY 5: keyword hints
    if amount == 0.0:
        m = re.search(r'(?:amount|amt|paid|total|debited|credited)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', clean_lower)
        if m:
            try:
                amount = float(m.group(1).replace(',', ''))
            except:
                pass

    # PRIORITY 6: any decimal number
    if amount == 0.0:
        m = re.search(r'\b([1-9][0-9]{1,5}\.[0-9]{2})\b', clean_text)
        if m:
            try:
                amount = float(m.group(1))
            except:
                pass

    result['amount'] = amount

    # Date detection
    for pattern in [r'(\d{4}[/-]\d{2}[/-]\d{2})', r'(\d{2}[/-]\d{2}[/-]\d{4})', r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})', r'(\d{2}[/-]\d{2}[/-]\d{2})']:
        m = re.search(pattern, text.lower())
        if m:
            result['date'] = m.group(1)
            break

    # Merchant detection — check Indian merchants first
    text_lower = text.lower()
    matched = False
    for merchant, category in INDIAN_MERCHANTS.items():
        if merchant in text_lower:
            result['description'] = merchant.title()
            result['category'] = category
            matched = True
            break

    if not matched:
        for pattern in [r'(?:paid to|received from|sent to)\s+([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)', r'(?:merchant|store)\s*:?\s*([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)']:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                if len(name) > 2:
                    result['description'] = name.title()
                    result['category'] = categorize_by_keywords(name)
                    break

    if not result['description']:
        lines_list = [l.strip() for l in text.split('\n') if len(l.strip()) > 3 and l.strip().replace(' ', '').isalpha()]
        if lines_list:
            result['description'] = lines_list[0][:50]

    # Debit/Credit
    if any(w in text_lower for w in ['debited', 'debit', 'paid', 'sent', 'withdrawn']):
        result['type'] = 'debit'
    elif any(w in text_lower for w in ['credited', 'credit', 'received', 'added', 'refund']):
        result['type'] = 'credit'

    if result['description'] and result['category'] == 'Others':
        result['category'] = categorize_by_keywords(result['description'].lower())

    return result


def categorize_text_expense(description, amount, api_key=None):
    return categorize_by_keywords(description.lower())


def categorize_by_keywords(description):
    description_lower = description.lower()

    # Check Indian merchants first
    for merchant, category in INDIAN_MERCHANTS.items():
        if merchant in description_lower:
            return category

    keyword_map = {
        "Food & Dining": ["restaurant", "cafe", "food", "pizza", "burger", "biryani", "coffee", "dining", "lunch", "dinner", "breakfast", "canteen", "dhaba", "thali", "tiffin", "mess", "hotel", "eatery", "sweets", "mithai", "bakery"],
        "Chai & Snacks": ["chai", "tea", "snack", "vada pav", "samosa", "pani puri", "bhel", "chaat", "juice", "lassi", "kulfi", "pav bhaji"],
        "Transportation": ["auto", "bus", "metro", "petrol", "fuel", "taxi", "train", "ticket", "transport", "cab", "rickshaw", "toll", "parking", "diesel", "cng", "ev charge", "bike", "scooter"],
        "Groceries": ["grocery", "vegetables", "milk", "supermarket", "kirana", "fruits", "rice", "dal", "atta", "sabzi", "pulses", "spices", "masala", "oil", "ghee"],
        "Shopping": ["clothes", "shoes", "mall", "shop", "purchase", "garment", "fashion", "apparel", "footwear", "accessories", "watch", "bag", "jewellery"],
        "Entertainment": ["movie", "cinema", "game", "sport", "concert", "event", "fun", "amusement", "arcade", "bowling", "cricket", "football"],
        "Healthcare": ["pharmacy", "hospital", "doctor", "medicine", "clinic", "medical", "health", "lab", "diagnostic", "chemist", "nursing", "dental", "eye", "ayurveda", "homeopathy"],
        "Utilities & Bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "recharge", "bill", "utility", "dth", "cable", "broadband", "landline"],
        "Education": ["course", "book", "college", "school", "tuition", "fees", "exam", "study", "coaching", "class", "library", "stationery"],
        "Travel": ["resort", "trip", "tour", "holiday", "flight", "hotel", "hostel", "lodge", "travel", "vacation", "tourism", "passport", "visa"],
        "Investment & Savings": ["sip", "mutual fund", "stock", "fd", "ppf", "insurance", "nps", "elss", "investment", "trading", "lic", "rd", "bond", "demat"],
        "Rent & Housing": ["rent", "maintenance", "society", "apartment", "housing", "pg", "hostel", "landlord", "lease", "deposit", "flat", "house"],
        "EMI & Loans": ["emi", "loan", "credit card", "repayment", "installment", "finance", "interest", "principal", "equated"],
        "Religious & Donations": ["temple", "mandir", "mosque", "church", "gurudwara", "donation", "charity", "prasad", "puja", "pooja", "aarti", "devotional"],
        "Family & Gifts": ["gift", "present", "birthday", "anniversary", "wedding", "baby", "flower", "cake", "celebration", "festive", "diwali", "holi", "eid", "christmas"],
        "Personal Care": ["salon", "haircut", "spa", "gym", "fitness", "beauty", "cosmetics", "grooming", "parlour", "massage", "wax", "facial", "manicure"],
    }

    for category, keywords in keyword_map.items():
        if any(kw in description_lower for kw in keywords):
            return category
    return "Others"


def get_indian_spending_insights(category_totals, monthly_income):
    """Generate Indian-specific spending pattern insights"""
    insights = []
    if monthly_income <= 0:
        return insights

    spending = {row['category']: row['total'] for _, row in category_totals.iterrows()}
    total = sum(spending.values())

    # Indian-specific benchmarks
    benchmarks = {
        "Food & Dining": (15, "Indians spend avg 15-20% on food. Cook at home more often!"),
        "Chai & Snacks": (3, "Keep chai & snacks under 3% of income — small amounts add up!"),
        "Transportation": (10, "Use metro/bus passes to reduce transport costs by 30%."),
        "Groceries": (15, "Buy staples monthly in bulk from D-Mart to save 15-20%."),
        "EMI & Loans": (30, "Keep total EMIs under 30% of income — RBI guideline."),
        "Shopping": (10, "Wait for sale seasons — Flipkart/Amazon Big Billion Days save 40-70%."),
        "Entertainment": (5, "Share OTT subscriptions with family — saves ₹300-500/month."),
        "Religious & Donations": (5, "Donations up to ₹500/month qualify for 80G tax deduction!"),
    }

    for category, (limit_pct, tip) in benchmarks.items():
        if category in spending:
            actual_pct = (spending[category] / monthly_income) * 100
            if actual_pct > limit_pct:
                insights.append({
                    "category": category,
                    "amount": spending[category],
                    "percent": actual_pct,
                    "limit": limit_pct,
                    "tip": tip,
                    "status": "over"
                })
            else:
                insights.append({
                    "category": category,
                    "amount": spending[category],
                    "percent": actual_pct,
                    "limit": limit_pct,
                    "tip": tip,
                    "status": "ok"
                })

    return insights


def parse_csv_bank_statement(df):
    expenses = []
    amount_cols = ['amount', 'debit', 'withdrawal', 'dr', 'transaction amount']
    date_cols = ['date', 'transaction date', 'value date', 'txn date']
    desc_cols = ['description', 'narration', 'particulars', 'remarks', 'details']
    df.columns = [col.lower().strip() for col in df.columns]
    amount_col = next((c for c in amount_cols if c in df.columns), None)
    date_col = next((c for c in date_cols if c in df.columns), None)
    desc_col = next((c for c in desc_cols if c in df.columns), None)
    if not all([amount_col, date_col, desc_col]):
        return expenses, "Could not detect required columns."
    for _, row in df.iterrows():
        try:
            amount_val = str(row[amount_col]).replace(',', '').strip()
            if amount_val and amount_val not in ['', 'nan', '-']:
                amount = float(re.sub(r'[^\d.]', '', amount_val))
                if amount > 0:
                    description = str(row[desc_col])
                    expenses.append({'date': str(row[date_col]), 'amount': amount, 'description': description[:100], 'category': categorize_by_keywords(description), 'source': 'csv_import'})
        except Exception:
            continue
    return expenses, None
