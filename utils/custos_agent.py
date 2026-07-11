from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent
import tempfile
import os

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
"""

def get_llm(groq_api_key):
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-8b-8192",
        temperature=0.3
    )

def create_knowledge_base(pdf_text=None):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = [FINANCIAL_KNOWLEDGE]
    if pdf_text:
        texts.append(pdf_text)
    docs = text_splitter.create_documents(texts)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings)
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def create_custos_tools(db_functions, retriever):
    retriever_tool = create_retriever_tool(
        retriever,
        name="financial_knowledge",
        description="Search Indian financial advice, tax saving tips, investment options and guru wisdom"
    )

    @tool
    def get_expense_summary(period: str = "current month") -> str:
        """Get user expense summary by category"""
        try:
            from datetime import datetime
            now = datetime.now()
            cat_totals = db_functions['get_category_totals'](now.year, now.month)
            if cat_totals.empty:
                return "No expenses recorded yet."
            result = f"Expenses for {now.strftime('%B %Y')}:\n"
            total = 0
            for _, row in cat_totals.iterrows():
                result += f"- {row['category']}: Rs.{row['total']:,.0f}\n"
                total += row['total']
            result += f"\nTotal: Rs.{total:,.0f}"
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @tool
    def analyze_budget_health(monthly_income: float = 50000) -> str:
        """Analyze financial health score and budget alerts"""
        try:
            from datetime import datetime
            from utils.financial_advisor import calculate_financial_health_score, analyze_spending_health
            now = datetime.now()
            cat_totals = db_functions['get_category_totals'](now.year, now.month)
            if cat_totals.empty:
                return "No expense data to analyze."
            score, grade, reasons = calculate_financial_health_score(cat_totals, monthly_income)
            alerts, suggestions = analyze_spending_health(cat_totals, monthly_income)
            result = f"Health Score: {score}/100 - {grade}\n"
            if alerts:
                result += "Alerts:\n" + "\n".join(alerts[:3])
            if suggestions:
                result += "\nTips:\n" + "\n".join(suggestions[:3])
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    @tool
    def get_tax_saving_advice(annual_income: float = 600000) -> str:
        """Get personalized Indian tax saving recommendations"""
        return f"""Tax Saving for Rs.{annual_income:,.0f} annual income:
1. Section 80C (Save Rs.46,800 tax): ELSS SIP Rs.12,500/month or PPF
2. Section 80D (Save Rs.7,800): Health insurance Rs.25,000 premium
3. NPS 80CCD(1B) (Save Rs.15,600): Extra Rs.50,000 investment
4. HRA: Claim if in rented accommodation
Total potential saving: Rs.{min(int(annual_income*0.3), 70200):,}"""

    @tool
    def get_investment_recommendation(risk_profile: str = "moderate", monthly_amount: float = 5000) -> str:
        """Get Indian investment recommendations based on risk profile"""
        if "conservative" in risk_profile.lower():
            return f"""Conservative Plan Rs.{monthly_amount:,.0f}/month:
- 40% PPF: Rs.{monthly_amount*0.4:,.0f}
- 30% FD: Rs.{monthly_amount*0.3:,.0f}
- 20% Debt Fund: Rs.{monthly_amount*0.2:,.0f}
- 10% Gold/SGB: Rs.{monthly_amount*0.1:,.0f}"""
        elif "aggressive" in risk_profile.lower():
            return f"""Aggressive Plan Rs.{monthly_amount:,.0f}/month:
- 50% Mid/Small Cap: Rs.{monthly_amount*0.5:,.0f}
- 25% Nifty 50: Rs.{monthly_amount*0.25:,.0f}
- 15% ELSS: Rs.{monthly_amount*0.15:,.0f}
- 10% International: Rs.{monthly_amount*0.1:,.0f}"""
        else:
            return f"""Moderate Plan Rs.{monthly_amount:,.0f}/month:
- 40% Nifty 50 SIP: Rs.{monthly_amount*0.4:,.0f}
- 25% ELSS: Rs.{monthly_amount*0.25:,.0f}
- 20% PPF: Rs.{monthly_amount*0.2:,.0f}
- 15% Gold/SGB: Rs.{monthly_amount*0.15:,.0f}"""

    return [retriever_tool, get_expense_summary, analyze_budget_health,
            get_tax_saving_advice, get_investment_recommendation]

def create_custos_agent(groq_api_key, db_functions, retriever):
    llm = get_llm(groq_api_key)
    tools = create_custos_tools(db_functions, retriever)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are CUSTOS, an AI-powered personal financial guardian for Indian users.
You combine wisdom of Warren Buffett, Robert Kiyosaki, Ramit Sethi and Benjamin Graham.
Always give advice in Indian Rupees. Reference Indian products (SIP, PPF, ELSS, NPS).
Be direct, actionable and specific. Use tools to get real user data before advising."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=5
    )

def load_pdf_to_retriever(pdf_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_file.read())
            tmp_path = tmp.name
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(pages)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embeddings)
        os.unlink(tmp_path)
        return vectorstore.as_retriever(search_kwargs={"k": 3}), len(pages)
    except Exception as e:
        return None, 0
