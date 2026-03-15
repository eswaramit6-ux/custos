content = open('app.py', encoding='utf-8').read()

# Add pdf_advisor import at top
old_import = "from utils.financial_advisor import ("
new_import = "from utils.pdf_advisor import extract_text_from_pdf, generate_book_based_advice\nfrom utils.financial_advisor import ("
content = content.replace(old_import, new_import, 1)

# Add new page to navigation
old_nav = '"🎯 Goals & Budget"'
new_nav = '"🎯 Goals & Budget",\n    "📚 Book Advisor"'
content = content.replace(old_nav, new_nav, 1)

# Add new page content before the last elif or at end
old_page = '# ═══ FOOTER'
new_page = '''# ═══ BOOK ADVISOR PAGE ════════════════════════════════════════════
elif page == "📚 Book Advisor":
    st.markdown('<div class="section-header">📚 FINANCIAL BOOK ADVISOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Upload any financial book PDF and get personalized advice based on its principles applied to YOUR spending!</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📖 Upload Your Book")
        st.markdown("**Supported books:**")
        st.markdown("- Rich Dad Poor Dad — Robert Kiyosaki")
        st.markdown("- The Intelligent Investor — Benjamin Graham")
        st.markdown("- Let's Talk Money — Monika Halan")
        st.markdown("- Psychology of Money — Morgan Housel")
        st.markdown("- The Millionaire Next Door — Thomas Stanley")
        st.markdown("- Or any other financial book PDF!")

        uploaded_pdf = st.file_uploader(
            "Upload Financial Book (PDF)",
            type=['pdf'],
            label_visibility="collapsed"
        )

        if uploaded_pdf:
            with st.spinner("📖 Reading book..."):
                pdf_text, total_pages = extract_text_from_pdf(uploaded_pdf)

            if pdf_text:
                st.success(f"✅ Book uploaded! {total_pages} pages read successfully.")
                st.markdown(f"**Preview of extracted text:**")
                st.text_area("", pdf_text[:500] + "...", height=150, disabled=True)
            else:
                st.error("Could not extract text from this PDF. Try another file.")

    with col2:
        st.markdown("### 💡 Book-Based Advice")
        if uploaded_pdf and pdf_text:
            now = datetime.now()
            income = st.session_state.get('monthly_income', 0)
            cat_totals = get_category_totals(now.year, now.month)

            if income <= 0:
                st.warning("Please set your monthly income in the sidebar first!")
            else:
                if st.button("📚 Generate Book-Based Advice", use_container_width=True):
                    with st.spinner("Applying book wisdom to your finances..."):
                        advice = generate_book_based_advice(
                            pdf_text,
                            uploaded_pdf.name,
                            cat_totals,
                            income
                        )
                    st.markdown(advice)
        else:
            st.markdown("""
            <div class="advice-card" style="text-align:center; padding:2rem">
                <div style="font-size:3rem">📚</div>
                <div style="color:#c4a050; margin-top:0.5rem">Upload a book to get started!</div>
                <div style="font-size:0.85rem; color:rgba(232,224,208,0.6); margin-top:0.5rem">
                    Get personalized advice based on financial book principles applied to your actual spending
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Show known books section
    st.markdown('<div class="section-header" style="margin-top:2rem">📖 FEATURED FINANCIAL BOOKS</div>', unsafe_allow_html=True)
    books = [
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "Assets vs Liabilities, Passive Income"),
        ("The Intelligent Investor", "Benjamin Graham", "Value Investing, Margin of Safety"),
        ("Let's Talk Money", "Monika Halan", "Indian Personal Finance, Three-Jar System"),
        ("Psychology of Money", "Morgan Housel", "Behavioral Finance, Long-term Thinking"),
        ("The Millionaire Next Door", "Thomas Stanley", "Frugality, Wealth Building"),
    ]
    cols = st.columns(3)
    for i, (title, author, theme) in enumerate(books):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="advice-card" style="padding:1rem; margin-bottom:0.5rem">
                <div style="color:#c4a050; font-weight:bold; font-size:0.9rem">{title}</div>
                <div style="font-size:0.8rem; color:rgba(232,224,208,0.7)">by {author}</div>
                <div style="font-size:0.75rem; color:rgba(232,224,208,0.5); margin-top:0.3rem">{theme}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══ FOOTER'''

content = content.replace(old_page, new_page, 1)
open('app.py', 'w', encoding='utf-8').write(content)
print('Done! PDF Book Advisor page added.')
