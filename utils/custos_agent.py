from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.agents import AgentExecutor
from langchain_core.agents import create_tool_calling_agent

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

def get_llm(groq_api_key):
    return ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192", temperature=0.3)

def create_knowledge_base(pdf_text=None):
    global rag
    rag = SimpleRAG(FINANCIAL_KNOWLEDGE + ("\n" + pdf_text if pdf_text else ""))
    return rag

def create_custos_tools(db_functions, retriever=None):
    @tool
    def search_financial_knowledge(query: str) -> str:
        """Search Indian financial advice tax tips investment options and guru wisdom"""
        return "\n".join(rag.search(query))

    @tool
    def get_expense_summary(period: str = "current month") -> str:
        """Get user expense summary by category for current month"""
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

    @tool
    def analyze_budget_health(monthly_income: float = 50000) -> str:
        """Analyze financial health score and budget alerts based on spending"""
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

    @tool
    def get_tax_saving_advice(annual_income: float = 600000) -> str:
        """Get personalized Indian tax saving recommendations based on annual income"""
        return f"""Tax Saving Rs.{annual_income:,.0f}/year:
1. 80C Rs.1.5L: ELSS SIP Rs.12500/month or PPF (saves Rs.46800 tax)
2. 80D Rs.25000: Health insurance (saves Rs.7800)
3. NPS 80CCD Rs.50000 extra (saves Rs.15600)
Max saving: Rs.{min(int(annual_income*0.3),70200):,}"""

    @tool
    def get_investment_recommendation(risk_profile: str = "moderate", monthly_amount: float = 5000) -> str:
        """Get Indian investment plan based on risk profile and monthly investment amount"""
        a = monthly_amount
        if "conservative" in risk_profile.lower():
            return f"Conservative Rs.{a:,.0f}/mo: PPF 40% + FD 30% + Debt 20% + Gold 10%"
        elif "aggressive" in risk_profile.lower():
            return f"Aggressive Rs.{a:,.0f}/mo: MidCap 50% + Nifty50 25% + ELSS 15% + Intl 10%"
        return f"Moderate Rs.{a:,.0f}/mo: Nifty50 40% + ELSS 25% + PPF 20% + Gold 15%"

    return [search_financial_knowledge, get_expense_summary, analyze_budget_health,
            get_tax_saving_advice, get_investment_recommendation]

def create_custos_agent(groq_api_key, db_functions, retriever=None):
    llm = get_llm(groq_api_key)
    tools = create_custos_tools(db_functions, retriever)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are CUSTOS, AI financial guardian for Indian users.
Wisdom of Buffett + Kiyosaki + Sethi + Graham.
Always use Rs. Give India-specific advice SIP PPF ELSS NPS.
Use tools to get real data. Be direct and actionable."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True,
                        handle_parsing_errors=True, max_iterations=5)

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
