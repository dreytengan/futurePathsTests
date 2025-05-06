import streamlit as st

# 🔧 Mock salary database
SALARY_ESTIMATES = {
    "Data Analyst": "€40,000 - €50,000 / year",
    "Data Scientist": "€45,000 - €60,000 / year",
    "UX Designer": "€38,000 - €48,000 / year",
    "Marketing Manager": "€42,000 - €55,000 / year",
    "Product Manager": "€50,000 - €70,000 / year",
    "Software Engineer": "€45,000 - €65,000 / year",
}

# 🔍 Helper to create search links
def internship_search_links(job_title):
    google_link = f"https://www.google.com/search?q={job_title.replace(' ', '+')}+Internships"
    linkedin_link = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}%20Internship"
    return google_link, linkedin_link

def run():
    st.title("💼 Internship & Salary Insights")
    st.caption("Explore average salary ranges and find real-world internships 🔎")

    # User input: select a job role to explore
    job_title = st.selectbox(
        "Select a job title to explore:",
        list(SALARY_ESTIMATES.keys())
    )

    if job_title:
        st.subheader(f"💰 Salary Estimate for {job_title}:")
        salary = SALARY_ESTIMATES.get(job_title, "No data available.")
        st.info(salary)

        st.subheader(f"🔗 Find {job_title} Internships:")
        google_link, linkedin_link = internship_search_links(job_title)

        st.markdown(f"- [🌐 Google Search]({google_link})")
        st.markdown(f"- [💼 LinkedIn Jobs]({linkedin_link})")

        # (Optional) Add some extra tip/info
        st.markdown(
            f"💡 **Pro Tip:** Consider setting job alerts on LinkedIn to stay updated for new {job_title} internship opportunities!"
        )
