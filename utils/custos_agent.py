from groq import Groq
import json

FINANCIAL_KNOWLEDGE = """
INDIAN FINANCIAL PLANNING GUIDE
EMERGENCY FUND: 6 months expenses in liquid fund.
INSURANCE: Term 10-15x income. Health min 5 lakhs.
TAX 80C 1.5L: ELSS PPF EPF. 80D Health 25000. NPS 80CCD 50000.
INVEST: SIP Nifty50 PPF ELSS FD Stocks Zerodha Groww.
BUDGET: 50-30-20 rule.
GURUS: Buffett=value Kiyosaki=assets Sethi=automate Graham=safety.
"""

class SimpleRAG:
    def __init__(self, text):
        self.chunks = [text[i:i+300] for i in range(0, len(text), 200)]
    def search(self, query, k=3):
        words = query.lower().split()
        scored = [(sum(1 for w in words if w in c.lower()), c) for c in self.chunks]
        scored.sort(reverse=True)
        return [c for _, c in scored[:k]]

rag = SimpleRAG(FINANCIAL_KNOWLEDGE)

def create_knowledge_base(pdf_text=None):
    global rag
    rag = SimpleRAG(FINANCIAL_KNOWLEDGE + ("\n" + pdf_text if pdf_text else ""))
    return rag

def get_expense_summary_data(db_functions):
    try:
        from datetime import datetime
        now = datetime.now()
        cat_totals = db_functions['get_category_totals'](now.year, now.month)
        if cat_totals.empty:
            return "No expenses recorded yet."
        result = f"Expenses {now.strftime('%B %Y')}:\n"
        total = 0
        for _, row in cat_totals.iterrows():
            result += f"- {row['category']}: Rs.{row['total']:,.0f}\n"
            total += row['total']
        return result + f"Total: Rs.{total:,.0f}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_budget_health_data(db_functions, monthly_income=50000):
    try:
        from datetime import datetime
        from utils.financial_advisor import calculate_financial_health_score, analyze_spending_health
        now = datetime.now()
        cat_totals = db_functions['get_category_totals'](now.year, now.month)
        if cat_totals.empty:
            return "No data yet."
        score, grade, _ = calculate_financial_health_score(cat_totals, monthly_income)
        alerts, tips = analyze_spending_health(cat_totals, monthly_income)
        result = f"Score: {score}/100 - {grade}\n"
        if alerts: result += "\n".join(alerts[:2])
        if tips: result += "\n" + "\n".join(tips[:2])
        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Tool definitions for Groq function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_financial_knowledge",
            "description": "Search Indian financial advice, tax tips, investment options and guru wisdom",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_expense_summary",
            "description": "Get user expense summary by category for current month",
            "parameters": {
                "type": "object",
                "properties": {
                    "period": {"type": "string", "description": "Time period"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_budget_health",
            "description": "Analyze financial health score and budget alerts",
            "parameters": {
                "type": "object",
                "properties": {
                    "monthly_income": {"type": "number", "description": "Monthly income in Rs"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tax_saving_advice",
            "description": "Get personalized Indian tax saving recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "annual_income": {"type": "number", "description": "Annual income in Rs"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_investment_recommendation",
            "description": "Get Indian investment plan based on risk profile and monthly amount",
            "parameters": {
                "type": "object",
                "properties": {
                    "risk_profile": {"type": "string", "description": "conservative, moderate, or aggressive"},
                    "monthly_amount": {"type": "number", "description": "Monthly investment amount in Rs"}
                }
            }
        }
    }
]

def execute_tool(name, args, db_functions, monthly_income):
    if name == "search_financial_knowledge":
        return "\n".join(rag.search(args.get("query", "")))
    elif name == "get_expense_summary":
        return get_expense_summary_data(db_functions)
    elif name == "analyze_budget_health":
        income = args.get("monthly_income", monthly_income)
        return get_budget_health_data(db_functions, income)
    elif name == "get_tax_saving_advice":
        annual = args.get("annual_income", monthly_income * 12)
        return f"""Tax Saving Rs.{annual:,.0f}/year:
1. 80C Rs.1.5L: ELSS SIP Rs.12500/month or PPF (saves Rs.46800 tax)
2. 80D Rs.25000: Health insurance (saves Rs.7800)
3. NPS 80CCD Rs.50000 extra (saves Rs.15600)
Max saving: Rs.{min(int(annual*0.3),70200):,}"""
    elif name == "get_investment_recommendation":
        risk = args.get("risk_profile", "moderate")
        a = args.get("monthly_amount", 5000)
        if "conservative" in risk.lower():
            return f"Conservative Rs.{a:,.0f}/mo: PPF 40% + FD 30% + Debt 20% + Gold 10%"
        elif "aggressive" in risk.lower():
            return f"Aggressive Rs.{a:,.0f}/mo: MidCap 50% + Nifty50 25% + ELSS 15% + Intl 10%"
        return f"Moderate Rs.{a:,.0f}/mo: Nifty50 40% + ELSS 25% + PPF 20% + Gold 15%"
    return "Tool not found"

def create_custos_agent(groq_api_key, db_functions, retriever=None):
    """Returns a callable agent function"""
    client = Groq(api_key=groq_api_key)
    
    def invoke(inputs):
        user_input = inputs.get("input", "")
        chat_history = inputs.get("chat_history", [])
        monthly_income = db_functions.get("monthly_income", 50000)
        
        messages = [
            {"role": "system", "content": """You are CUSTOS, AI financial guardian for Indian users.
Wisdom of Buffett + Kiyosaki + Sethi + Graham combined.
Always use Rs. Give India-specific advice: SIP, PPF, ELSS, NPS, 80C, 80D.
Use tools to get real user data. Be direct and actionable."""}
        ]
        
        for msg in chat_history:
            if hasattr(msg, 'content'):
                role = "user" if msg.__class__.__name__ == "HumanMessage" else "assistant"
                messages.append({"role": role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_input})
        
        # First call with tools
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )
        
        msg = response.choices[0].message
        
        # Handle tool calls
        if msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]})
            
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                result = execute_tool(tc.function.name, args, db_functions, monthly_income)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            
            # Second call with tool results
            final = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                max_tokens=1024
            )
            return {"output": final.choices[0].message.content}
        
        return {"output": msg.content}
    
    # Return object with invoke method
    class Agent:
        def invoke(self, inputs):
            return invoke(inputs)
    
    return Agent()

def load_pdf_to_retriever(pdf_file):
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(pdf_file)
        text = "".join([p.extract_text() for p in reader.pages[:50]])
        global rag
        rag = SimpleRAG(FINANCIAL_KNOWLEDGE + "\n" + text)
        return rag, len(reader.pages)
    except Exception as e:
        return None, 0
