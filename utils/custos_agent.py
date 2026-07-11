from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
import tempfile
import os

# ── FINANCIAL KNOWLEDGE BASE ──
FINANCIAL_KNOWLEDGE = """
INDIAN FINANCIAL PLANNING GUIDE

EMERGENCY FUND: Keep 6 months expenses in liquid fund or savings account.

INSURANCE FIRST:
- Term Insurance: 10-15x annual income
- Health Insurance: minimum 5 lakhs coverage

TAX SAVING (Section 80C - 1.5L limit):
- ELSS Mutual Funds: 3 year lock-in, market returns
- PPF: 7.1% interest, 15 year lock-in, tax free
- EPF: Employer contribution, retirement focused
- NSC: 5 year lock-in, guaranteed returns

ADDITIONAL TAX SAVING:
- Section 80D: Health insurance premium up to 25000
- NPS: Additional 50000 under 80CCD(1B)
- HRA: House rent allowance if in rented accommodation

INVESTMENT OPTIONS:
- SIP: Start with 500/month in Nifty 50 index fund
- PPF: Safe, tax free, long term
- ELSS: Tax saving + market returns
- FD: Safe, 6-7% returns
- Stocks: Higher risk, higher returns via Zerodha/Groww

BUDGETING RULES:
- 50-30-20: 50% needs, 30% wants, 20% savings
- Emergency fund before any investment
- Insurance before investment

FINANCIAL GURUS:
Warren Buffett: Buy quality assets, hold long term, live below means
Robert Kiyosaki: Build assets, avoid liabilities, create passive income
Ramit Sethi: Automate finances, spend on what you love, cut rest
Benjamin Graham: Margin of safety, value investing, patience

INDIAN EXPENSE CATEGORIES:
Food & Dining, Transportation, Shopping, Entertainment, Healthcare,
Education, Utilities & Bills, Groceries, Travel, Investment & Savings,
Personal Care, Rent & Housing, Chai & Snacks, EMI & Loans, Others
"""

def get_llm(groq_api_key):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-8b-8192",
        temperature=0.3
    )

def create_knowledge_base(pdf_text=None):
    """Create RAG vector store from financial knowledge + optional PDF"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    texts = [FINANCIAL_KNOWLEDGE]
    if pdf_text:
        texts.append(pdf_text)
    
    docs = text_splitter.create_documents(texts)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    vectorstore = Chroma.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def create_custos_tools(db_functions, retriever):
    """Create LangChain tools from Custos functions"""
    
    retriever_tool = create_retriever_tool(
        retriever,
        name="financial_knowledge",
        description="Search Indian financial advice, tax saving tips, investment options, budgeting rules and guru wisdom"
    )
    
    @tool
    def get_expense_summary(period: str = "current month") -> str:
        """Get user's expense summary and spending breakdown by category"""
        try:
            from datetime import datetime
            now = datetime.now()
            cat_totals = db_functions['get_category_totals'](now.year, now.month)
            if cat_totals.empty:
                return "No expenses recorded yet."
            result = f"Expense Summary for {now.strftime('%B %Y')}:\n"
            total = 0
            for _, row in cat_totals.iterrows():
                result += f"- {row['category']}: ₹{row['total']:,.0f}\n"
                total += row['total']
            result += f"\nTotal Spent: ₹{total:,.0f}"
            return result
        except Exception as e:
            return f"Error getting expenses: {str(e)}"
    
    @tool
    def analyze_budget_health(monthly_income: float = 0) -> str:
        """Analyze financial health score and budget alerts based on spending"""
        try:
            from datetime import datetime
            from utils.financial_advisor import calculate_financial_health_score, analyze_spending_health
            now = datetime.now()
            cat_totals = db_functions['get_category_totals'](now.year, now.month)
            if cat_totals.empty:
                return "No expense data to analyze."
            if monthly_income <= 0:
                monthly_income = 50000
            score, grade, reasons = calculate_financial_health_score(cat_totals, monthly_income)
            alerts, suggestions = analyze_spending_health(cat_totals, monthly_income)
            result = f"Financial Health Score: {score}/100 — {grade}\n"
            if alerts:
                result += "\nAlerts:\n" + "\n".join(alerts[:3])
            if suggestions:
                result += "\nSuggestions:\n" + "\n".join(suggestions[:3])
            return result
        except Exception as e:
            return f"Error analyzing budget: {str(e)}"
    
    @tool
    def get_tax_saving_advice(annual_income: float = 600000) -> str:
        """Get personalized Indian tax saving recommendations based on income"""
        tax_bracket = ""
        if annual_income <= 300000:
            tax_bracket = "No tax liability under new regime"
        elif annual_income <= 700000:
            tax_bracket = "5% slab - consider 87A rebate"
        elif annual_income <= 1000000:
            tax_bracket = "10-15% slab - maximize 80C investments"
        else:
            tax_bracket = "20-30% slab - aggressive tax planning needed"
        
        advice = f"""Tax Saving Advice for Annual Income ₹{annual_income:,.0f}:
Tax Bracket: {tax_bracket}

Priority Actions:
1. Section 80C (Save up to ₹46,800 tax):
   - ELSS Fund SIP: ₹12,500/month = ₹1.5L/year
   - Or PPF: Safe, 7.1% tax-free returns
   
2. Section 80D (Save up to ₹7,800 tax):
   - Health insurance: ₹25,000 premium
   
3. NPS Section 80CCD(1B) (Save up to ₹15,600 tax):
   - Additional ₹50,000 investment
   
4. HRA Exemption:
   - Claim if living in rented accommodation
   
Total Potential Tax Saving: ₹{min(int(annual_income * 0.3), 70200):,}"""
        return advice
    
    @tool  
    def get_investment_recommendation(risk_profile: str = "moderate", amount: float = 5000) -> str:
        """Get Indian investment recommendations based on risk profile and amount"""
        recommendations = {
            "conservative": f"""Conservative Portfolio for ₹{amount:,.0f}/month:
- 40% PPF: ₹{amount*0.4:,.0f} - Safe, tax-free
- 30% FD: ₹{amount*0.3:,.0f} - Guaranteed returns
- 20% Debt Mutual Fund: ₹{amount*0.2:,.0f} - Better than FD
- 10% Gold/SGB: ₹{amount*0.1:,.0f} - Hedge against inflation""",
            
            "moderate": f"""Moderate Portfolio for ₹{amount:,.0f}/month:
- 40% Nifty 50 Index SIP: ₹{amount*0.4:,.0f} - Market returns
- 25% ELSS Fund: ₹{amount*0.25:,.0f} - Tax saving + growth
- 20% PPF: ₹{amount*0.2:,.0f} - Safe component
- 15% Gold/SGB: ₹{amount*0.15:,.0f} - Diversification""",
            
            "aggressive": f"""Aggressive Portfolio for ₹{amount:,.0f}/month:
- 50% Mid/Small Cap SIP: ₹{amount*0.5:,.0f} - High growth
- 25% Nifty 50 Index: ₹{amount*0.25:,.0f} - Stability
- 15% ELSS: ₹{amount*0.15:,.0f} - Tax saving
- 10% Crypto/International: ₹{amount*0.1:,.0f} - High risk"""
        }
        return recommendations.get(risk_profile.lower(), recommendations["moderate"])
    
    return [retriever_tool, get_expense_summary, analyze_budget_health, 
            get_tax_saving_advice, get_investment_recommendation]

def create_custos_agent(groq_api_key, db_functions, retriever):
    """Create the main Custos financial advisor agent"""
    
    llm = get_llm(groq_api_key)
    tools = create_custos_tools(db_functions, retriever)
    
    system_prompt = """You are CUSTOS, an AI-powered personal financial guardian and advisor for Indian users.

Your persona: You combine the wisdom of Warren Buffett (value investing), Robert Kiyosaki (assets vs liabilities), Ramit Sethi (conscious spending), and Benjamin Graham (margin of safety).

Your expertise:
- Indian tax planning (80C, 80D, NPS, HRA)
- Investment options (SIP, PPF, ELSS, FD, Stocks)
- Expense analysis and budgeting
- UPI/PhonePe/GPay transaction analysis
- Indian financial products and regulations

Always:
- Give advice in Indian Rupees (₹)
- Reference Indian financial products
- Be direct and actionable
- Use the tools to get real user data before giving advice

You have access to the following tools:
{tools}

Use this format:
Question: the input question
Thought: think about what to do
Action: tool name
Action Input: tool input
Observation: tool result
... (repeat as needed)
Thought: I have enough information
Final Answer: your response

{agent_scratchpad}

Question: {input}"""

    prompt = PromptTemplate.from_template(system_prompt)
    
    agent = create_react_agent(llm, tools, prompt)
    
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )
    
    return agent_executor

def load_pdf_to_retriever(pdf_file):
    """Load uploaded PDF into RAG retriever"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        docs = text_splitter.split_documents(pages)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embeddings)
        
        os.unlink(tmp_path)
        return vectorstore.as_retriever(search_kwargs={"k": 3}), len(pages)
    except Exception as e:
        return None, 0
