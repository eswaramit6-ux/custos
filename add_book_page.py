content = open('app.py', encoding='utf-8').read()

# Add the Book Advisor page at the end of the file
book_page = '''

# ═══ BOOK ADVISOR PAGE ════════════════════════════════════════════
elif page == "📚 Book Advisor":
    st.markdown('<div class="section-header">FINANCIAL BOOK ADVISOR</div>', unsafe_allow_html=True)
    st.markdown('<div class="alert-info">Upload any financial book PDF and get personalized advice based on its principles applied to YOUR spending!</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Upload Your Book")
        st.markdown("**Supported books:**")
        st.markdown("- Rich Dad Poor Dad — Robert Kiyosaki")
        st.markdown("- The Intelligent Investor — Benjamin Graham")
        st.markdown("- Let's Talk Money — Monika Halan")
        st.markdown("- Psychology of Money — Morgan Housel")
        st.markdown("- Or any other financial book PDF!")

        uploaded_pdf = st.file_uploader(
            "Upload Financial Book PDF",
            type=['pdf'],
            label_visibility="collapsed"
        )

        if uploaded_pdf:
            with st.spinner("Reading book..."):
                pdf_text, total_pages = extract_text_from_pdf(uploaded_pdf)

            if pdf_text:
                st.success(f"Book uploaded! {total_pages} pages read successfully.")
                with st.expander("Preview extracted text"):
                    st.text(pdf_text[:500] + "...")
            else:
                st.error("Could not extract text. Try another PDF.")

    with col2:
        st.markdown("### Book-Based Advice")
        if uploaded_pdf and pdf_text:
            now = datetime.now()
            income = st.session_state.get('monthly_income', 0)
            cat_totals = get_category_totals(now.year, now.month)

            if income <= 0:
                st.warning("Please set your monthly income in the sidebar first!")
            else:
                if st.button("Generate Book-Based Advice", use_container_width=True):
                    with st.spinner("Applying book wisdom to your finances..."):
                        advice = generate_book_based_advice(
                            pdf_text,
                            uploaded_pdf.name,
                            cat_totals,
                            income
                        )
                    st.markdown(advice)
        else:
            st.info("Upload a financial book PDF on the left to get started!")

    st.markdown('<div class="section-header" style="margin-top:2rem">FEATURED FINANCIAL BOOKS</div>', unsafe_allow_html=True)
    books = [
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "Assets vs Liabilities"),
        ("The Intelligent Investor", "Benjamin Graham", "Value Investing"),
        ("Let's Talk Money", "Monika Halan", "Indian Personal Finance"),
        ("Psychology of Money", "Morgan Housel", "Behavioral Finance"),
        ("The Millionaire Next Door", "Thomas Stanley", "Wealth Building"),
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
'''

content = content + book_page
open('app.py', 'w', encoding='utf-8').write(content)

import ast
ast.parse(content)
print('Done! Book Advisor page added and syntax OK.')
