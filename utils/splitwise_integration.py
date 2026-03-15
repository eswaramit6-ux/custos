import requests
from datetime import datetime, timedelta

SPLITWISE_BASE_URL = "https://secure.splitwise.com/api/v3.0"

def get_splitwise_expenses(api_key, days=30):
    """Fetch expenses from Splitwise API"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Get expenses from last N days
        dated_after = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        response = requests.get(
            f"{SPLITWISE_BASE_URL}/get_expenses",
            headers=headers,
            params={
                "dated_after": dated_after,
                "limit": 100
            }
        )
        
        if response.status_code == 200:
            return response.json().get('expenses', []), None
        else:
            return [], f"API Error: {response.status_code}"
            
    except Exception as e:
        return [], str(e)

def get_splitwise_user(api_key):
    """Get current user info from Splitwise"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{SPLITWISE_BASE_URL}/get_current_user", headers=headers)
        if response.status_code == 200:
            return response.json().get('user', {}), None
        return {}, f"Error: {response.status_code}"
    except Exception as e:
        return {}, str(e)

def get_splitwise_groups(api_key):
    """Get all groups from Splitwise"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{SPLITWISE_BASE_URL}/get_groups", headers=headers)
        if response.status_code == 200:
            return response.json().get('groups', []), None
        return [], f"Error: {response.status_code}"
    except Exception as e:
        return [], str(e)

def parse_splitwise_expenses(expenses, current_user_id):
    """Parse Splitwise expenses into Custos format"""
    from utils.ocr_extractor import categorize_by_keywords
    
    parsed = []
    for expense in expenses:
        # Skip deleted expenses
        if expense.get('deleted_at'):
            continue
        
        # Find user's share
        user_share = 0.0
        for user in expense.get('users', []):
            if str(user.get('user_id')) == str(current_user_id):
                owed = user.get('owed_share', '0')
                try:
                    user_share = float(owed)
                except:
                    user_share = 0.0
                break
        
        if user_share <= 0:
            continue
            
        description = expense.get('description', 'Splitwise Expense')
        date = expense.get('date', str(datetime.now()))[:10]
        category = categorize_by_keywords(description.lower())
        
        parsed.append({
            'date': date,
            'amount': user_share,
            'description': f"{description} (Splitwise)",
            'category': category,
            'source': 'splitwise',
            'group': expense.get('group_id', None)
        })
    
    return parsed

def analyze_splitwise_spending(expenses):
    """Analyze group spending patterns"""
    if not expenses:
        return {}
    
    analysis = {
        'total': sum(e['amount'] for e in expenses),
        'count': len(expenses),
        'by_category': {},
        'largest_expense': max(expenses, key=lambda x: x['amount']) if expenses else None
    }
    
    for expense in expenses:
        cat = expense['category']
        if cat not in analysis['by_category']:
            analysis['by_category'][cat] = 0
        analysis['by_category'][cat] += expense['amount']
    
    return analysis
