import re
import pytesseract
import shutil
tesseract_path = shutil.which("tesseract")
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
from PIL import Image
import PIL.ImageEnhance as enhance
from datetime import date

CATEGORIES = [
    "Food & Dining", "Transportation", "Shopping", "Entertainment",
    "Healthcare", "Education", "Utilities & Bills", "Groceries",
    "Travel", "Investment & Savings", "Personal Care", "Rent & Housing", "Others"
]

def extract_expense_from_image(image, api_key=None):
    try:
        image = image.convert('RGB')
        enhancer = enhance.Contrast(image)
        image = enhancer.enhance(2.0)
        extracted_text = pytesseract.image_to_string(image, config='--psm 6')
        if not extracted_text.strip():
            return {'amount': 0.0, 'date': str(date.today()), 'description': '', 'category': 'Others', 'type': 'debit', 'raw_text': 'No text found'}
        result = extract_from_text(extracted_text)
        result['raw_text'] = extracted_text[:300]
        return result
    except Exception as e:
        return {'amount': 0.0, 'date': str(date.today()), 'description': '', 'category': 'Others', 'type': 'debit', 'raw_text': f'Error: {str(e)}'}

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
                # Decimal amounts e.g. 52.9, 812.84, 691.20
                for n in re.findall(r'\b([0-9,]+\.[0-9]{1,2})\b', search_line):
                    s = n.replace(',', '')
                    v = float(s)
                    if 10 <= v <= 500000:
                        decimal_candidates.append(v)
                    # Strip first digit - rupee symbol often merges (e.g. 7812.84 -> 812.84)
                    if len(s.split('.')[0]) >= 4:
                        try:
                            trimmed = float(s[1:])
                            if 10 <= trimmed <= 500000:
                                decimal_candidates.append(trimmed)
                        except:
                            pass
                # Whole numbers e.g. 500, 90 (only used if no decimals found)
                for n in re.findall(r'\b([1-9][0-9]{1,3})\b', search_line):
                    v = float(n)
                    if 10 <= v <= 9999:
                        whole_candidates.append(v)
            # Prefer decimal amounts; fall back to whole numbers only if none found
            candidates = decimal_candidates if decimal_candidates else whole_candidates
            if candidates:
                amount = min(candidates)
            break

    # PRIORITY 2: rupee symbol (or misread as & @ # % =)
    if amount == 0.0:
        for n in re.findall(r'[₹\u20b9&@#%=]\s*([0-9,]+(?:\.[0-9]{1,2})?)', clean_text):
            try:
                v = float(n.replace(',', ''))
                if 10 <= v <= 500000:
                    amount = v
                    break
            except:
                pass

    # PRIORITY 3: Rs. or INR
    if amount == 0.0:
        for pattern in [r'rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)', r'inr\s*([0-9,]+(?:\.[0-9]{2})?)']:
            m = re.search(pattern, clean_lower)
            if m:
                try:
                    amount = float(m.group(1).replace(',', ''))
                    break
                except:
                    pass

    # PRIORITY 4: keyword hints
    if amount == 0.0:
        m = re.search(r'(?:amount|amt|paid|total|debited|credited)\s*:?\s*([0-9,]+(?:\.[0-9]{2})?)', clean_lower)
        if m:
            try:
                amount = float(m.group(1).replace(',', ''))
            except:
                pass

    # PRIORITY 5: any decimal number
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

    # Merchant detection
    known_merchants = [
        'zomato', 'swiggy', 'amazon', 'flipkart', 'uber', 'ola', 'rapido',
        'phonepe', 'paytm', 'gpay', 'google pay', 'netflix', 'spotify',
        'hotstar', 'bigbasket', 'blinkit', 'zepto', 'myntra', 'ajio',
        'apollo', '1mg', 'jio', 'airtel', 'vodafone', 'irctc', 'makemytrip',
        'oyo', 'zerodha', 'groww', 'dmart', 'meesho', 'nykaa', 'playo',
        'swiggy instamart', 'dunzo', 'byjus', 'unacademy', 'cred', 'damensch'
    ]
    text_lower = text.lower()
    for merchant in known_merchants:
        if merchant in text_lower:
            result['description'] = merchant.title()
            result['category'] = categorize_by_keywords(merchant)
            break

    if not result['description']:
        for pattern in [r'(?:paid to|received from|sent to)\s+([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)', r'(?:merchant|store)\s*:?\s*([A-Za-z][A-Za-z\s]{2,25}?)(?:\n|\r|$)']:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                name = m.group(1).strip()
                if len(name) > 2:
                    result['description'] = name.title()
                    break

    if not result['description']:
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 3 and l.strip().replace(' ', '').isalpha()]
        if lines:
            result['description'] = lines[0][:50]

    # Debit/Credit
    if any(w in text_lower for w in ['debited', 'debit', 'paid', 'sent', 'withdrawn']):
        result['type'] = 'debit'
    elif any(w in text_lower for w in ['credited', 'credit', 'received', 'added', 'refund']):
        result['type'] = 'credit'

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
        "Shopping": ["amazon", "flipkart", "myntra", "ajio", "clothes", "shoes", "mall", "shop", "meesho", "nykaa", "decathlon", "croma", "purchase", "damensch"],
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
                    expenses.append({'date': str(row[date_col]), 'amount': amount, 'description': description[:100], 'category': categorize_by_keywords(description), 'source': 'csv_import'})
        except Exception:
            continue
    return expenses, None
