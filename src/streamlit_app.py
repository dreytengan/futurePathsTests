import streamlit as st
import career_pivot_page  # ✅ Page 1
import internships_salary_page  # ✅ Page 2

PAGES = {
    "Career Pivot Suggestions": career_pivot_page,
    "Internships & Salary Insights": internships_salary_page,
}

st.sidebar.title("🔀 Navigation")
selection = st.sidebar.radio("Go to:", list(PAGES.keys()))

page = PAGES[selection]
page.run()
