# streamlit_app.py
import streamlit as st
import career_pivot_page 
import internships_salary_page 
import resume_upload_and_predict_page # <-- NEW PAGE

# Configure page title and icon
st.set_page_config(page_title="futurePaths", page_icon="🚀", layout="wide")


PAGES = {
    "🎯 Career Pivot Suggestions (Manual Input)": career_pivot_page, # Kept existing key for now
    "📄 Resume Analysis & Pathfinding": resume_upload_and_predict_page, # <-- NEW PAGE
    "💼 Internships & Salary Insights": internships_salary_page,
}

st.sidebar.title("🔀 Navigation")
selection = st.sidebar.radio("Go to:", list(PAGES.keys()), key="main_nav")

page_to_run = PAGES[selection]

# It's good practice to check if the page module has a 'run' function
if hasattr(page_to_run, 'run') and callable(getattr(page_to_run, 'run')):
    page_to_run.run()
else:
    st.error(f"Selected page '{selection}' does not have a callable 'run' function.")