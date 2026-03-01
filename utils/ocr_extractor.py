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
        # Extract text from image using Tesseract
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text.strip():
            return {
                'amount': 0.0,
                'date': str(date.today()),
                'description': 'Payment',
                'category': 'Others',
                'type': 'debit',
                'raw_text': 'Could not extract text from image'
            }

        # Parse the extracted text
        result = extract_from_text(extracted_text)
        result['raw_text'] = extracted_text[:200]
        return result

    except Exception as e:
        return {
            'amount': 0.0,
            'date': str(date.today()),
            'description': 'Payment',
            'category': 'Others',
            'type': 'debit',
            'raw_text': f'OCR Error: {str(e)}'
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
    amount_patterns = [
        r'[₹₹]\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'(?:rs\.?|inr)\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'([0-9,]+(?:\.[0-9]{2})?)\s*(?:rs\.?|inr)',
        r'(?:amount|amt|paid|debited|credited|total)\s*:?\s*[₹₹]?\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'(?:for|of)\s+[₹₹]\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'(?:debit|credit)\s+(?:of\s+)?[₹₹]?\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'([0-9]{2,6}(?:\.[0-9]{2})?)',
    ]

    for pattern in amount_patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                result['amount'] = float(amount_str)
                break
            except:
                continue

    # ── Date Detection ──
    date_patterns = [
        r'(\d{2}[-/]\d{2}[-/]\d{4})',
        r'(\d{4}[-/]\d{2}[-/]\d{2})',
        r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4})',
        r'(\d{2}[-/]\d{2}[-/]\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['date'] = match.group(1)
            break

    # ── Merchant Detection ──
    merchant_patterns = [
        r'(?:to|at|from|paid to|sent to)\s+([A-Za-z][A-Za-z0-9\s]{2,25}?)(?:\s+on|\s+for|\s+ref|\s+upi|$|\n)',
        r'([A-Za-z][A-Za-z0-9\s]{3,20}?)(?:\s+upi|\s+payment|\s+merchant|\s+store)',
    ]
    for pattern in merchant_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['description'] = match.group(1).strip().title()
            break

    if not result['description']:
        words = [w for w in text.split() if len(w) > 3 and w.isalpha()]
        if words:
            result['description'] = ' '.join(words[:3]).title()

    # ── Debit/Credit Detection ──
    if any(w in text_lower for w in ['debited', 'debit', 'paid', 'sent', 'withdrawn', 'payment made']):
        result['type'] = 'debit'
    elif any(w in text_lower for w in ['credited', 'credit', 'received', 'added', 'refund']):
        result['type'] = 'credit'

    # ── Category Detection ──
    result['category'] = categorize_by_keywords(text_lower)

    return result

def categorize_text_expense(description, amount, api_key=None):
    return categorize_by_keywords(description.lower())

def categorize_by_keywords(description):
    description_lower = description.lower()
    keyword_map = {
        "Food & Dining": ["restaurant", "cafe", "food", "zomato", "swiggy", "pizza", "burger", "dhaba", "biryani", "coffee", "dining", "lunch", "dinner", "breakfast", "dominos", "kfc", "mcdonalds", "subway", "chai", "canteen", "eat"],
        "Transportation": ["uber", "ola", "auto", "bus", "metro", "petrol", "fuel", "rapido", "taxi", "train", "ticket", "transport", "cab", "rickshaw", "irctc", "redbus", "toll", "parking", "rapido"],
        "Groceries": ["bigbasket", "grofers", "blinkit", "zepto", "grocery", "vegetables", "milk", "dmart", "supermarket", "kirana", "fruits", "rice", "dal", "atta", "reliance fresh"],
        "Shopping": ["amazon", "flipkart", "myntra", "ajio", "clothes", "shoes", "mall", "shop", "meesho", "nykaa", "decathlon", "croma", "purchase", "bought", "store"],
        "Entertainment": ["netflix", "hotstar", "spotify", "prime", "movie", "cinema", "pvr", "inox", "game", "youtube", "disney", "zee5", "sonyliv", "bookmyshow", "concert", "event"],
        "Healthcare": ["pharmacy", "hospital", "doctor", "medicine", "clinic", "medical", "apollo", "1mg", "netmeds", "pharmeasy", "health", "lab", "diagnostic", "wellness"],
        "Utilities & Bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "jio", "airtel", "vodafone", "recharge", "bsnl", "bill", "utility", "tata"],
        "Education": ["course", "book", "college", "school", "tuition", "udemy", "coursera", "byju", "unacademy", "fees", "exam", "study", "class"],
        "Travel": ["makemytrip", "goibibo", "airbnb", "oyo", "booking", "yatra", "cleartrip", "resort", "trip", "tour", "holiday", "vacation", "flight", "hotel"],
        "Investment & Savings": ["sip", "mutual fund", "zerodha", "groww", "stock", "fd", "ppf", "insurance", "nps", "elss", "investment", "trading", "lic", "policy"],
        "Rent & Housing": ["rent", "maintenance", "society", "apartment", "housing", "pg", "hostel", "landlord", "lease"],
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
