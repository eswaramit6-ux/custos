import re
import pytesseract
from PIL import Image
import PIL.ImageEnhance as enhance
from datetime import date

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Education", "Utilities & Bills", "Groceries",
    "Travel", "Investment & Savings", "Personal Care", "Rent & Housing", "Others"
]

def extract_expense_from_image(image, api_key=None):
    """Extract expense from screenshot using Tesseract OCR"""
    try:
        image = image.convert('RGB')
        enhancer = enhance.Contrast(image)
        image = enhancer.enhance(2.0)
        extracted_text = pytesseract.image_to_string(image, config='--psm 6')

        if not extracted_text.strip():
            return {
                'amount': 0.0, 'date': str(date.today()),
                'description': '', 'category': 'Others',
                'type': 'debit', 'raw_text': 'No text found'
            }

        result = extract_from_text(extracted_text)
        result['raw_text'] = extracted_text[:300]
        return result

    except Exception as e:
        return {
            'amount': 0.0, 'date': str(date.today()),
            'description': '', 'category': 'Others',
            'type': 'debit', 'raw_text': f'Error: {str(e)}'
        }

def extract_from_text(text):
    """Extract expense details from any payment text"""
    result = {
        'amount': 0.0, 'date': str(date.today()),
        'description': '', 'category': 'Others', 'type': 'debit'
    }

    # ── Step 1: Clean text - remove time patterns first ──
    # Remove times like "12:04 pm", "10:30 am", "12:57 pm"
    clean_text = re.sub(r'\b\d{1,2}:\d{2}\s*(?:am|pm)\b', '', text, flags=re.IGNORECASE)
    # Remove years like 2026, 2025
    clean_text = re.sub(r'\b20\d{2}\b', '', clean_text)
    # Remove date patterns like "27 Feb", "12 Feb"
    clean_text = re.sub(r'\b\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', '', clean_text, flags=re.IGNORECASE)

    clean_lower = clean_text.lower()

    # ── Step 2: Amount Detection - Priority Order ──
    amount = 0.0

    # HIGHEST PRIORITY: ₹812.84 or ₹100 (with rupee symbol)
    match = re.search(r'[₹\u20b9]\s*([0-9,]+(?:\.[0-9]{2})?)', clean_text)
    if match:
        try:
            amount = float(match.group(1).replace(',', ''))
        except:
            pass

    # 2nd: Rs.100 or Rs 100
    if amount == 0.0:
        match = re.search(r'rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)', clean_lower)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
            except:
                pass

    # 3rd: INR 100
    if amount == 0.0:
        match = re.search(r'inr\s*([0-9,]+(?:\.[0-9]{2})?)', clean_lower)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
            except:
                pass

    # 4th: amount/paid/total keywords
    if amount == 0.0:
        match = re.search(r'(?:amount|amt|paid|total|debited|credited)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', clean_lower)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
            except:
                pass

    # 5th: Tesseract misreads ₹ as % @ # &
    if amount == 0.0:
        match = re.search(r'[%@#&]\s*([0-9,]+(?:\.[0-9]{2})?)', clean_text)
        if match:
            try:
                amount = float(match.group(1).replace(',', ''))
            except:
                pass

    # 6th: decimal number (very specific like 812.84)
    if amount == 0.0:
        match = re.search(r'\b([1-9][0-9]{1,5}\.[0-9]{2})\b', clean_text)
        if match:
            try:
                amount = float(match.group(1))
            except:
                pass

    result['amount'] = amount

    # ── Step 3: Date Detection (from original text) ──
    date_patterns = [
        r'(\d{4}[/-]\d{2}[/-]\d{2})',
        r'(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
        r'(\d{2}[/-]\d{2}[/-]\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text.lower())
        if match:
            result['date'] = match.group(1)
            break

    # ── Step 4: Merchant Detection ──
    known_merchants = [
        'zomato', 'swiggy', 'amazon', 'flipkart', 'uber', 'ola', 'rapido',
        'phonepe', 'paytm', 'gpay', 'google pay', 'netflix', 'spotify',
        'hotstar', 'bigbasket', 'blinkit', 'zepto', 'myntra', 'ajio',
        'apollo', '1mg', 'jio', 'airtel', 'vodafone', 'irctc', 'makemytrip',
        'oyo', 'zerodha', 'groww', 'dmart', 'meesho', 'nykaa', 'playo',
        'swiggy instamart', 'dunzo', 'byjus', 'unacademy', 'cred'
    ]

    text_lower = text.lower()
    for merchant in known_merchants:
        if merchant in text_lower:
            result['description'] = merchant.title()
            result['category'] = categorize_by_keywords(merchant)
            break

    # If no known merchant, try regex
    if not result['description']:
        patterns = [
            r'(?:paid to|to|sent to)\s+([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)',
            r'(?:merchant|store)\s*:?\s*([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2:
                    result['description'] = name.title()
                    break

    # Fallback description
    if not result['description']:
        lines = [l.strip() for l in text.split('\n')
                 if len(l.strip()) > 3 and l.strip().replace(' ', '').isalpha()]
        if lines:
            result['description'] = lines[0][:50]

    # ── Step 5: Debit/Credit ──
    if any(w in text_lower for w in ['debited', 'debit', 'paid', 'sent', 'withdrawn']):
        result['type'] = 'debit'
    elif any(w in text_lower for w in ['credited', 'credit', 'received', 'added', 'refund']):
        result['type'] = 'credit'

    # ── Step 6: Category ──
    if result['description']:
        result['category'] = categorize_by_keywords(result['description'].lower())

    return result

def categorize_text_expense(description, amount, api_key=None):
    return categorize_by_keywords(description.lower())

def categorize_by_keywords(description):
    description_lower = description.lower()
    keyword_map = {
        "Food & Dining": ["restaurant", "cafe", "food", "zomato", "swiggy", "pizza", "burger", "dhaba", "biryani", "coffee", "dining", "lunch", "dinner", "breakfast", "dominos", "kfc", "mcdonalds", "subway", "chai", "canteen"],
        "Transportation": ["uber", "ola", "auto", "bus", "metro", "petrol", "fuel", "rapido", "taxi", "train", "ticket", "transport", "cab", "rickshaw", "irctc", "redbus", "toll", "parking"],
        "Groceries": ["bigbasket", "grofers", "blinkit", "zepto", "grocery", "vegetables", "milk", "dmart", "supermarket", "kirana", "fruits", "rice", "dal", "atta"],
        "Shopping": ["amazon", "flipkart", "myntra", "ajio", "clothes", "shoes", "mall", "shop", "meesho", "nykaa", "decathlon", "croma", "purchase"],
        "Entertainment": ["netflix", "hotstar", "spotify", "prime", "movie", "cinema", "pvr", "inox", "game", "youtube", "disney", "zee5", "sonyliv", "bookmyshow", "playo"],
        "Healthcare": ["pharmacy", "hospital", "doctor", "medicine", "clinic", "medical", "apollo", "1mg", "netmeds", "pharmeasy", "health", "lab", "diagnostic"],
        "Utilities & Bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "jio", "airtel", "vodafone", "recharge", "bsnl", "bill", "utility"],
        "Education": ["course", "book", "college", "school", "tuition", "udemy", "coursera", "byju", "unacademy", "fees", "exam", "study"],
        "Travel": ["makemytrip", "goibibo", "airbnb", "oyo", "booking", "yatra", "cleartrip", "resort", "trip", "tour", "holiday", "flight"],
        "Investment & Savings": ["sip", "mutual fund", "zerodha", "groww", "stock", "fd", "ppf", "insurance", "nps", "elss", "investment", "trading", "lic"],
        "Rent & Housing": ["rent", "maintenance", "society", "apartment", "housing", "pg", "hostel", "landlord"],
        "Personal Care": ["salon", "haircut", "spa", "gym", "fitness", "beauty", "cosmetics", "grooming", "parlour"],
    }
    for category, keywords in keyword_map.items():
        if any(kw in description_lower for kw in keywords):
            return category
    return "Others"

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
                    expenses.append({
                        'date': str(row[date_col]),
                        'amount': amount,
                        'description': description[:100],
                        'category': categorize_by_keywords(description),
                        'source': 'csv_import'
                    })
        except Exception:
            continue
    return expenses, None
