import re
import google.generativeai as genai
from PIL import Image
import io

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

def configure_gemini(api_key):
    genai.configure(api_key=api_key)

def extract_expense_from_image(image, api_key):
    try:
        configure_gemini(api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""You are an expert at reading Indian payment screenshots (UPI, PhonePe, Google Pay, Paytm, bank receipts).

Extract the following from this payment screenshot:
1. Amount (in INR)
2. Date of transaction
3. Merchant/Recipient name
4. Transaction type (debit/credit)

Categorize into ONE of: {', '.join(CATEGORIES)}

Respond in EXACT format:
AMOUNT: <number only>
DATE: <YYYY-MM-DD>
DESCRIPTION: <merchant or purpose>
CATEGORY: <category from list>
TYPE: <debit or credit>"""

        response = model.generate_content([prompt, image])
        return parse_extraction_response(response.text)

    except Exception as e:
        return {"error": str(e)}

def parse_extraction_response(response_text):
    result = {}
    lines = response_text.strip().split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip()
            if key == 'AMOUNT':
                try:
                    result['amount'] = float(re.sub(r'[^\d.]', '', value))
                except:
                    result['amount'] = 0.0
            elif key == 'DATE':
                result['date'] = value
            elif key == 'DESCRIPTION':
                result['description'] = value
            elif key == 'CATEGORY':
                result['category'] = value if value in CATEGORIES else 'Others'
            elif key == 'TYPE':
                result['type'] = value.lower()
    return result

def categorize_text_expense(description, amount, api_key):
    try:
        configure_gemini(api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"Categorize this expense into ONE category.\nDescription: {description}\nAmount: {amount}\nCategories: {', '.join(CATEGORIES)}\nReply with ONLY the category name."
        )
        category = response.text.strip()
        return category if category in CATEGORIES else categorize_by_keywords(description)
    except Exception:
        return categorize_by_keywords(description)

def categorize_by_keywords(description):
    description_lower = description.lower()
    keyword_map = {
        "Food & Dining": ["restaurant", "cafe", "food", "zomato", "swiggy", "pizza", "burger", "hotel", "dhaba", "biryani", "coffee"],
        "Transportation": ["uber", "ola", "auto", "bus", "metro", "petrol", "fuel", "rapido", "taxi", "train", "ticket"],
        "Groceries": ["bigbasket", "grofers", "blinkit", "zepto", "grocery", "vegetables", "milk", "dmart", "supermarket"],
        "Shopping": ["amazon", "flipkart", "myntra", "ajio", "clothes", "shoes", "mall", "shop"],
        "Entertainment": ["netflix", "hotstar", "spotify", "prime", "movie", "cinema", "pvr", "inox", "game"],
        "Healthcare": ["pharmacy", "hospital", "doctor", "medicine", "clinic", "medical", "apollo", "1mg"],
        "Utilities & Bills": ["electricity", "water", "gas", "internet", "wifi", "broadband", "jio", "airtel", "vodafone", "recharge"],
        "Education": ["course", "book", "college", "school", "tuition", "udemy", "coursera"],
        "Travel": ["flight", "makemytrip", "goibibo", "airbnb", "oyo", "booking"],
        "Investment & Savings": ["sip", "mutual fund", "zerodha", "groww", "stock", "fd", "ppf", "insurance"],
        "Rent & Housing": ["rent", "maintenance", "society", "apartment"],
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
