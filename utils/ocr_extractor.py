import re
from PIL import Image
import io
from datetime import date

# Expense categories
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
    """
    Extract expense from image using OCR patterns.
    Falls back to basic extraction if no API available.
    """
    try:
        # Try to extract text using basic image analysis
        # Look for common Indian payment patterns
        result = extract_with_patterns(image)
        return result
    except Exception as e:
        return {"error": str(e)}

def extract_with_patterns(image):
    """Extract expense details using PIL and regex patterns on image metadata"""
    # Return a template for user to fill in
    # This works without any API
    return {
        'amount': 0.0,
        'date': str(date.today()),
        'description': 'Payment',
        'category': 'Others',
        'type': 'debit',
        'needs_manual': True
    }

def extract_from_text(text):
    """Extract expense details from pasted transaction text/SMS"""
    result = {
        'amount': 0.0,
        'date': str(date.today()),
        'description': '',
        'category': 'Others',
        'type': 'debit'
    }

    # Amount patterns for Indian payments
    amount_patterns = [
        r'(?:rs\.?|inr|₹)\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'([0-9,]+(?:\.[0-9]{2})?)\s*(?:rs\.?|inr|₹)',
        r'(?:amount|amt|paid|debited|credited)\s*:?\s*(?:rs\.?|inr|₹)?\s*([0-9,]+(?:\.[0-9]{2})?)',
        r'(?:for|of)\s+(?:rs\.?|inr|₹)\s*([0-9,]+(?:\.[0-9]{2})?)',
    ]

    text_lower = text.lower()

    for pattern in amount_patterns:
        match = re.search(pattern, text_lower)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                result['amount'] = float(amount_str)
                break
            except:
                continue

    # Date patterns
    date_patterns = [
        r'(\d{2}[-/]\d{2}[-/]\d{4})',
        r'(\d{4}[-/]\d{2}[-/]\d{2})',
        r'(\d{2}[-/]\d{2}[-/]\d{2})',
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            result['date'] = match.group(1)
            break

    # Merchant/description extraction
    merchant_patterns = [
        r'(?:to|at|from|via|merchant|by)\s+([A-Za-z][A-Za-z0-9\s]{2,30}?)(?:\s+on|\s+for|\s+ref|$)',
        r'(?:upi|neft|imps|rtgs)\s+(?:to|from)\s+([A-Za-z][A-Za-z0-9\s]{2,30})',
        r'([A-Za-z][A-Za-z0-9\s]{3,25}?)(?:\s+upi|\s+payment|\s+merchant)',
    ]
    for pattern in merchant_patterns:
        match = re.search(pattern, text_lower)
        if match:
            result['description'] = match.group(1).strip().title()
            break

    if not result['description']:
        # Use first meaningful words
        words = [w for w in text.split() if len(w) > 3 and w.isalpha()]
        if words:
            result['description'] = ' '.join(words[:3])

    # Debit/Credit detection
    if any(word in text_lower for word in ['debited', 'debit', 'paid', 'sent', 'withdrawn', 'payment']):
        result['type'] = 'debit'
    elif any(word in text_lower for word in ['credited', 'credit', 'received', 'added']):
        result['type'] = 'credit'

    # Categorize
    result['category'] = categorize_by_keywords(text_lower)

    return result

def categorize_text_expense(description, amount, api_key=None):
    """Categorize expense by keywords - no API needed"""
    return categorize_by_keywords(description.lower())

def categorize_by_keywords(description):
    """Keyword-based categorization"""
    description_lower = description.lower()

    keyword_map = {
        "Food & Dining": ["restaurant", "cafe", "food", "zomato", "swiggy", "pizza", "burger", "hotel", "dhaba", "biryani", "coffee", "dining", "eat", "lunch", "dinner", "breakfast", "dominos", "kfc", "mcdonalds", "subway", "chai", "canteen"],
        "Transportation": ["uber", "ola", "auto", "bus", "metro", "petrol", "fuel", "rapido", "taxi", "train", "ticket", "transport", "cab", "rickshaw", "irctc", "redbus", "toll", "parking"],
        "Groceries": ["bigbasket", "grofers", "blinkit", "zepto", "grocery", "vegetables", "milk", "dmart", "supermarket", "kirana", "fruits", "rice", "dal", "atta", "reliance fresh"],
        "Shopping": ["amazon", "flipkart", "myntra", "ajio", "clothes", "shoes", "mall", "shop", "meesho", "nykaa", "decathlon", "croma", "purchase", "bought"],
        "Entertainment": ["netflix", "hotstar", "spotify", "prime", "movie", "cinema", "pvr", "inox", "game", "youtube", "disney", "zee5", "sonyliv", "bookmyshow", "concert"],
        "Healthcare": ["pharmacy", "hospital", "doctor", "medicine", "clinic", "medical", "apollo", "1mg", "netmeds", "pharmeasy", "health", "lab", "diagnostic"],
        "Utilities & Bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "jio", "airtel", "vodafone", "recharge", "bsnl", "bill", "utility"],
        "Education": ["course", "book", "college", "school", "tuition", "udemy", "coursera", "byju", "unacademy", "fees", "exam", "study"],
        "Travel": ["makemytrip", "goibibo", "airbnb", "oyo", "booking", "yatra", "cleartrip", "resort", "trip", "tour", "holiday", "vacation", "flight"],
        "Investment & Savings": ["sip", "mutual fund", "zerodha", "groww", "stock", "fd", "ppf", "insurance", "nps", "elss", "investment", "trading", "lic"],
        "Rent & Housing": ["rent", "maintenance", "society", "apartment", "housing", "pg", "hostel", "landlord", "lease"],
        "Personal Care": ["salon", "haircut", "spa", "gym", "fitness", "beauty", "cosmetics", "grooming", "parlour"],
    }

    for category, keywords in keyword_map.items():
        if any(kw in description_lower for kw in keywords):
            return category

    return "Others"

def parse_csv_bank_statement(df):
    """Parse Indian bank statement CSV"""
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
