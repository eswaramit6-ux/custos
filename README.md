# 🛡️ CUSTOS — Financial Guardian

> **AI-Powered Personal Finance Advisor & Expense Manager for India**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://custos-vptrmp3eekpsfpnh6mdmdd.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Project Overview

CUSTOS is an AI-powered financial advisor and expense manager built specifically for Indian users. It automates expense tracking through UPI payment screenshots, bank SMS messages, and CSV bank statements, while providing personalized financial advice based on top financial gurus' philosophies and Indian tax laws.

**Live Demo:** https://custos-vptrmp3eekpsfpnh6mdmdd.streamlit.app/

**Demo Video:** https://drive.google.com/file/d/1haOSCWT-utuc1d-z_mrbCDGElpqxP6ll/view?usp=sharing

**GitHub:** https://github.com/eswaramit6-ux/custos

---

## ✨ Features

### 📸 Expense Tracking
- **OCR Screenshot Extraction** — Upload PhonePe, GPay, Paytm, IRCTC screenshots and auto-extract amount, date, merchant
- **Bank SMS Parsing** — Paste SBI, HDFC, ICICI bank SMS messages to extract transactions
- **Manual Entry** — Add expenses manually with auto-categorization
- **CSV Import** — Import bank statements in CSV format

### 🤖 AI Financial Advisor
- **4 Financial Guru Modes** — Warren Buffett, Robert Kiyosaki, Ramit Sethi, Benjamin Graham
- **Financial Health Score** — 0-100 score with grade (A/B/C/D)
- **Spending Alerts** — Identifies overspending in any category
- **Personalized Advice** — Based on your actual spending patterns

### 🇮🇳 Indian Finance Features
- **Indian Investment Plan** — Step-by-step roadmap (Emergency Fund → Insurance → ELSS → PPF → NPS → SIP)
- **SIP Returns Calculator** — Calculate maturity value for any SIP amount and duration
- **Tax Calculator** — Compare Old vs New tax regime with actual numbers
- **80C Investment Recommendations** — ELSS, PPF, NPS, Health Insurance, SGB
- **80C Progress Tracker** — Dashboard shows how much of ₹1.5L limit you've used
- **Tax Saving Alerts** — Shows how much tax you can save by investing more

### 📊 Analytics
- **Spending by Category** — Pie chart and bar chart
- **Daily Spending Trend** — Line chart with cumulative view
- **Indian Spending Pattern Analysis** — Compare your spending vs Indian lifestyle benchmarks
- **UPI Transaction Analysis** — Spending breakdown by UPI app (PhonePe, GPay, Paytm, etc.)
- **Spending Anomaly Detection** — Flags categories over healthy limits
- **Monthly Forecast** — Projects month-end spending based on daily average

### 🎯 Goals & Budget
- **Financial Goals** — Set targets with deadlines and track progress
- **Monthly Budgets** — Set category-wise limits and compare vs actual

### 📥 Export
- **CSV Export** — Download all transactions
- **Category Summary CSV** — Download category-wise totals
- **Text Report** — Download full financial report with top transactions

### 📚 Book Advisor
- Upload any financial book PDF (Rich Dad Poor Dad, Intelligent Investor, etc.)
- Get personalized advice based on the book's principles applied to your spending

### 🤝 Splitwise Integration
- Connect your Splitwise account to import group expenses
- Analyze shared spending patterns

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| OCR | Tesseract OCR + pytesseract |
| AI Advisor | Google Gemini API |
| Database | SQLite |
| Charts | Plotly |
| PDF Processing | PyPDF2 |
| Data Processing | Pandas, NumPy |
| Deployment | Streamlit Cloud |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Tesseract OCR installed on your system
- Google Gemini API key (free at https://makersuite.google.com/)

### Step 1: Install Tesseract OCR

**Windows:**
1. Download from https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer — check "Add to PATH" during installation
3. Verify: open Command Prompt and run `tesseract --version`

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Mac
brew install tesseract
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/eswaramit6-ux/custos.git
cd custos
```

### Step 3: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Locally
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## ⚙️ API Configuration

### Google Gemini API (Required for AI Advice)
1. Go to https://makersuite.google.com/
2. Sign in with your Google account
3. Click "Get API Key" → "Create API Key"
4. Copy the key (starts with `AIza...`)
5. Paste it in the **API Configuration** section in the sidebar

### Splitwise API (Optional)
1. Go to https://splitwise.com/apps
2. Register a new app
3. Copy your API key
4. Paste it in the **Splitwise** page in the app

---

## 🌐 Deploying to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "deploy"
git push origin main
```

### Step 2: Deploy
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **New app**
4. Select your repository, branch (`main`), and main file (`app.py`)
5. Click **Deploy**

### Step 3: Add Secrets (for Gemini API)
In Streamlit Cloud settings → Secrets, add:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

### Required files for Streamlit Cloud
Make sure your repo has `packages.txt`:
```
tesseract-ocr
tesseract-ocr-eng
```

---

## 📁 Project Structure

```
custos/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── packages.txt                # System packages for Streamlit Cloud
├── README.md                   # This file
└── utils/
    ├── __init__.py
    ├── database.py             # SQLite database operations
    ├── ocr_extractor.py        # Tesseract OCR + text extraction
    ├── financial_advisor.py    # Indian finance advisor logic
    ├── pdf_advisor.py          # PDF book processing
    └── splitwise_integration.py # Splitwise API integration
```

---

## 💡 Usage Examples

### Tracking a UPI Payment
1. Open PhonePe/GPay after a transaction
2. Take a screenshot
3. Go to **Add Expense → Upload Screenshot**
4. Upload the screenshot — amount, date, merchant auto-extracted
5. Review and click **Save Expense**

### Getting Investment Advice
1. Set your monthly income in the sidebar
2. Add a few expenses
3. Go to **AI Advisor → Indian Investment Plan**
4. See your personalized step-by-step investment roadmap

### Checking Tax Savings
1. Set your monthly income in the sidebar
2. Go to **AI Advisor → Tax Calculator**
3. See Old vs New regime comparison
4. Check 80C investment recommendations

### Importing Bank Statement
1. Download CSV from your bank's net banking
2. Go to **Add Expense → Import CSV**
3. Upload the CSV file
4. Preview and click **Import All Transactions**

---

## 🏗️ Architecture

```
User Input
    │
    ├── Screenshot → Tesseract OCR → extract_from_text() → categorize_by_keywords()
    ├── SMS Text → extract_from_text() → INDIAN_SMS_PATTERNS regex
    ├── Manual Entry → categorize_by_keywords() → SQLite
    └── CSV → parse_csv_bank_statement() → SQLite
                                │
                         SQLite Database
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Analytics Page         AI Advisor Page
              (Plotly charts)    (Rule-based + Gemini API)
                    │                       │
              Indian Spending         Indian Finance
              Benchmarks              Investment Plan
                                      Tax Calculator
```

---

## ⚠️ Disclaimer

CUSTOS is an educational tool for personal finance management. It is **not** a certified financial advisor. All advice provided is based on general financial principles and should not be considered as professional financial or investment advice. Please consult a certified financial advisor before making major financial decisions.

---

## 👥 Team

Built as part of the **Capabl AI Agent Development Project** — 8-week fintech project.

- Track: **Track A — Indian Personal Finance Advisor**
- Domain: Financial Technology & Personal Wealth Management
- Deployment: Streamlit Cloud

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
