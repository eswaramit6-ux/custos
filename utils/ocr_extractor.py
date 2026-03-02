import re
import pytesseract
from PIL import Image
import io
from datetime import date

CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Education",
    "Utilities & Bills",
    "Groceries",
    "Travel",
    "Investment & Savings",
    "Personal Care",
    "Rent & Housing",
    "Others"
]

def extract_expense_from_image(image, api_key=None):
    """Extract expense from screenshot using Tesseract OCR"""
    try:
        # Preprocess image for better OCR
        import PIL.ImageEnhance as enhance
        image = image.convert('RGB')
        
        # Enhance contrast for better text reading
        enhancer = enhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Extract text
        extracted_text = pytesseract.image_to_string(image, config='--psm 6')
        
        if not extracted_text.strip():
            return {
                'amount': 0.0,
                'date': str(date.today()),
                'description': '',
                'category': 'Others',
                'type': 'debit',
                'raw_text': 'No text found in image'
            }

        result = extract_from_text(extracted_text)
        result['raw_text'] = extracted_text[:300]
        return result

    except Exception as e:
        return {
            'amount': 0.0,
            'date': str(date.today()),
            'description': '',
            'category': 'Others',
            'type': 'debit',
            'raw_text': f'Error: {str(e)}'
        }

def extract_from_text(text):
    """Extract expense details from any text/SMS"""
    result = {
        'amount': 0.0,
        'date': str(date.today()),
        'description': '',
        'category': 'Others',
        'type': 'debit'
    }

    text_lower = text.lower()

    # ── Amount Detection ──
    # Try multiple patterns from most specific to least specific
    amount_patterns = [
        # ₹100 or ₹1,000 or ₹1,000.00
        r'[₹\u20b9]\s*([0-9,]+(?:\.[0-9]{2})?)',
        # Rs.100 or Rs 100
        r'rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)',
        # INR 100
        r'inr\s*([0-9,]+(?:\.[0-9]{2})?)',
        # amount: 100 or paid: 100
        r'(?:amount|amt|paid|total|debited|credited)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)',
        # 100 followed by common words
        r'([0-9,]+(?:\.[0-9]{2})?)\s*(?:paid|debited|credited|transferred)',
        # Tesseract sometimes reads ₹ as % or other chars
        r'[%@#&]\s*([0-9,]+(?:\.[0-9]{2})?)',
        # Last resort: find standalone numbers that look like amounts
        r'\b([1-9][0-9]{1,6}(?:\.[0-9]{2})?)\b',
    ]

    for pattern in amount_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                # Skip years (2020-2030) and very small amounts
                if 2020 <= amount <= 2030:
                    continue
                # Skip transaction IDs (too many digits)
                if len(amount_str.replace('.','')) > 8:
                    continue
                # Reasonable transaction amount
                if 1 <= amount <= 1000000:
                    result['amount'] = amount
                    break
            except:
                continue
        if result['amount'] > 0:
            break

    # ── Date Detection ──
    date_patterns = [
        r'(\d{4}[/-]\d{2}[/-]\d{2})',
        r'(\d{2}[/-]\d{2}[/-]\d{4})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
        r'(\d{2}[/-]\d{2}[/-]\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['date'] = match.group(1)
            break

    # ── Merchant/Description Detection ──
    # Look for known merchants first
    known_merchants = [
        'zomato', 'swiggy', 'amazon', 'flipkart', 'uber', 'ola', 'rapido',
        'phonepe', 'paytm', 'gpay', 'google pay', 'netflix', 'spotify',
        'hotstar', 'bigbasket', 'blinkit', 'zepto', 'myntra', 'ajio',
        'apollo', '1mg', 'jio', 'airtel', 'vodafone', 'irctc', 'makemytrip',
        'oyo', 'zerodha', 'groww', 'dmart', 'meesho', 'nykaa'
    ]
    
    text_lower_check = text.lower()
    for merchant in known_merchants:
        if merchant in text_lower_check:
            result['description'] = merchant.title()
            result['category'] = categorize_by_keywords(merchant)
            break

    # If no known merchant found, try to extract name
    if not result['description']:
        merchant_patterns = [
            r'(?:paid to|to|sent to)\s+([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)',
            r'(?:merchant|store|vendor)\s*:?\s*([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)',
        ]
        for pattern in merchant_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2:
                    result['description'] = name.title()
                    break

    # Final fallback for description
    if not result['description']:
        # Use first meaningful line
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 3 and l.strip().replace(' ', '').isalpha()]
        if lines:
            result['description'] = lines[0][:50]

    # ── Debit/Credit Detection ──
    if any(w in text_lower for w in ['debited', 'debit', 'paid', 'sent', 'withdrawn']):
        result['type'] = 'debit'
    elif any(w in text_lower for w in ['credited', 'credit', 'received', 'added', 'refund']):
        result['type'] = 'credit'

    # ── Category ──
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
        "Entertainment": ["netflix", "hotstar", "spotify", "prime", "movie", "cinema", "pvr", "inox", "game", "youtube", "disney", "zee5", "sonyliv", "bookmyshow"],
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
