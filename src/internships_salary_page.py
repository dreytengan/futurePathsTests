import streamlit as st
import pandas as pd
import altair as alt

# 🔧 Enhanced salary database with more roles
SALARY_BASE_ESTIMATES = {
    "Data Analyst": 45000,
    "Data Scientist": 52500,
    "UX Designer": 43000,
    "Marketing Manager": 48500,
    "Product Manager": 60000,
    "Software Engineer": 55000,
    "Frontend Developer": 50000,
    "Backend Developer": 53000,
    "Full Stack Developer": 57000,
    "DevOps Engineer": 62000,
    "Machine Learning Engineer": 65000,
    "Business Analyst": 47000,
    "Project Manager": 55000,
    "Content Writer": 40000,
    "Graphic Designer": 42000,
}

# 🌍 Global location adjustment factors (percentage)
LOCATION_ADJUSTMENTS = {
    "New York, USA": 1.0,  # Base reference
    "San Francisco, USA": 0.90,
    "London, UK": 0.78,
    "Zurich, Switzerland": 1.04,
    "Singapore": 0.79,
    "Tokyo, Japan": 0.75,
    "Sydney, Australia": 0.68,
    "Paris, France": 0.68,
    "Amsterdam, Netherlands": 0.68,
    "Dubai, UAE": 0.72,
    "Hong Kong": 0.74,
    "Berlin, Germany": 0.65,
    "Munich, Germany": 0.66,
    "Toronto, Canada": 0.67,
    "Seoul, South Korea": 0.63,
    "Remote": 0.70,
}

# 🛠️ Required tools/software by role
JOB_TOOLS = {
    "Data Analyst": ["Excel", "SQL", "Tableau/Power BI", "Python/R"],
    "Data Scientist": ["Python", "R", "SQL", "TensorFlow/PyTorch", "Jupyter"],
    "UX Designer": ["Figma", "Sketch", "Adobe XD", "InVision", "Zeplin"],
    "Marketing Manager": ["Google Analytics", "HubSpot", "SEO tools", "Social media platforms"],
    "Product Manager": ["Jira", "Confluence", "Figma", "Google Analytics"],
    "Software Engineer": ["Git", "Docker", "CI/CD tools", "Cloud platforms"],
    "Frontend Developer": ["HTML/CSS", "JavaScript", "React/Angular/Vue", "Git"],
    "Backend Developer": ["Node.js/Python/Java", "SQL/NoSQL", "API tools", "Docker"],
    "Full Stack Developer": ["JavaScript", "HTML/CSS", "Backend languages", "Databases", "Git"],
    "DevOps Engineer": ["Docker", "Kubernetes", "AWS/Azure/GCP", "CI/CD pipelines", "Terraform"],
    "Machine Learning Engineer": ["Python", "TensorFlow/PyTorch", "Scikit-learn", "Jupyter", "Git"],
    "Business Analyst": ["Excel", "SQL", "Tableau/Power BI", "Jira"],
    "Project Manager": ["MS Project", "Jira", "Asana", "Slack", "Confluence"],
    "Content Writer": ["CMS platforms", "SEO tools", "Grammarly", "Google Analytics"],
    "Graphic Designer": ["Adobe Creative Suite", "Figma", "Sketch", "Canva"],
}

# 📈 Growth trend indicators (1-5 scale, 5 being highest growth)
JOB_GROWTH = {
    "Data Analyst": 4,
    "Data Scientist": 5,
    "UX Designer": 4,
    "Marketing Manager": 3,
    "Product Manager": 4,
    "Software Engineer": 5,
    "Frontend Developer": 4,
    "Backend Developer": 4,
    "Full Stack Developer": 5,
    "DevOps Engineer": 5,
    "Machine Learning Engineer": 5,
    "Business Analyst": 3,
    "Project Manager": 3,
    "Content Writer": 2,
    "Graphic Designer": 3,
}

# 🔍 Helper to create search links
def internship_search_links(job_title):
    google_link = f"https://www.google.com/search?q={job_title.replace(' ', '+')}+Internships"
    linkedin_link = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}%20Internship"
    indeed_link = f"https://de.indeed.com/jobs?q={job_title.replace(' ', '+')}"
    return google_link, linkedin_link, indeed_link

# 💰 Calculate adjusted salary based on location
def get_adjusted_salary(base_salary, location):
    adjustment_factor = LOCATION_ADJUSTMENTS.get(location, 1.0)
    adjusted_salary = base_salary * adjustment_factor
    return f"€{int(adjusted_salary - 5000)} - €{int(adjusted_salary + 5000)} / year"

# 📊 Create salary growth chart
def create_salary_growth_chart(job_title, location):
    # Mock data for 5-year salary progression
    base = SALARY_BASE_ESTIMATES.get(job_title, 45000)
    adjustment = LOCATION_ADJUSTMENTS.get(location, 1.0)
    
    years = list(range(2025, 2030))
    salaries = [int(base * adjustment * (1 + 0.05 * i)) for i in range(5)]
    
    df = pd.DataFrame({
        'Year': years,
        'Salary (€)': salaries
    })
    
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y('Salary (€):Q', title='Estimated Salary (€)'),
        tooltip=['Year', 'Salary (€)']
    ).properties(
        title=f'Projected Salary Growth for {job_title} in {location}',
        width=500,
        height=300
    )
    
    return chart

def run():
    st.title("💼 Internship & Salary Insights")
    
    # Replace basic caption with visual header
    st.markdown("""
    <div style="background-color:#1E3A8A; padding:10px; border-radius:10px; margin-bottom:20px">
        <h3 style="color:white; text-align:center">Explore average salary ranges and find real-world internships 🔎</h3>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # User input: select a job role to explore
        job_title = st.selectbox(
            "Select a job title to explore:",
            sorted(list(SALARY_BASE_ESTIMATES.keys()))
        )
        
        # Location selection
        location = st.selectbox(
            "Select a location:",
            sorted(list(LOCATION_ADJUSTMENTS.keys()))
        )

    with col2:
        # Improved growth trend display
        growth_score = JOB_GROWTH.get(job_title, 3)
        growth_color = "#22C55E" if growth_score >= 4 else ("#64748B" if growth_score >= 3 else "#EF4444")
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; text-align:center">
            <h4 style="color:white; margin:0">Market Growth Trend</h4>
            <h2 style="color:{growth_color}; font-size:32px; margin:10px 0">{growth_score}/5</h2>
            <p style="color:{growth_color}; margin:0">
                {"Growing" if growth_score >= 4 else ("Stable" if growth_score >= 3 else "Slow")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    if job_title and location:
        # Styled salary information
        base_salary = SALARY_BASE_ESTIMATES.get(job_title, 45000)
        adjusted_salary = get_adjusted_salary(base_salary, location)
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; margin:10px 0px; border-left:5px solid #3B82F6">
            <h3 style="color:white;">💰 Salary Estimate for {job_title} in {location}:</h3>
            <h2 style="color:#3B82F6; text-align:center; font-size:28px">{adjusted_salary}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Salary growth projection
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; margin:15px 0px">
            <h3 style="color:white;">📈 Salary Growth Projection (5 Years)</h3>
        </div>
        """, unsafe_allow_html=True)
        chart = create_salary_growth_chart(job_title, location)
        st.altair_chart(chart, use_container_width=True)
        
        # Improved tools section
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; margin:15px 0px">
            <h3 style="color:white;">🧰 Required Tools & Software for {job_title}:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        tool_cols = st.columns(2)
        tools = JOB_TOOLS.get(job_title, ["No specific tools data available"])
        for i, tool in enumerate(tools):
            with tool_cols[i % 2]:
                st.markdown(f"""
                <div style="background-color:#1E293B; padding:10px; border-radius:5px; margin:5px 0px">
                    <p style="margin:0; color:white;">⚙️ {tool}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Improved job links section
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; margin:15px 0px">
            <h3 style="color:white;">🔗 Find {job_title} Opportunities:</h3>
        </div>
        """, unsafe_allow_html=True)
        
        link_cols = st.columns(3)
        google_link, linkedin_link, indeed_link = internship_search_links(job_title)
        
        with link_cols[0]:
            st.markdown(f"""
            <a href="{google_link}" target="_blank" style="text-decoration:none">
                <div style="background-color:#1E293B; padding:15px; border-radius:10px; text-align:center">
                    <p style="margin:0; color:white;">🌐 Google Search</p>
                </div>
            </a>
            """, unsafe_allow_html=True)
        
        with link_cols[1]:
            st.markdown(f"""
            <a href="{linkedin_link}" target="_blank" style="text-decoration:none">
                <div style="background-color:#1E293B; padding:15px; border-radius:10px; text-align:center">
                    <p style="margin:0; color:white;">💼 LinkedIn Jobs</p>
                </div>
            </a>
            """, unsafe_allow_html=True)
        
        with link_cols[2]:
            st.markdown(f"""
            <a href="{indeed_link}" target="_blank" style="text-decoration:none">
                <div style="background-color:#1E293B; padding:15px; border-radius:10px; text-align:center">
                    <p style="margin:0; color:white;">🔍 Indeed</p>
                </div>
            </a>
            """, unsafe_allow_html=True)

        # Pro tip section with improved styling
        st.markdown(f"""
        <div style="background-color:#0F172A; padding:15px; border-radius:10px; margin-top:20px; border-left:5px solid #22C55E">
            <p style="margin:0; color:white;">💡 <strong>Pro Tip:</strong> Consider setting job alerts on LinkedIn to stay updated for new {job_title} opportunities in {location}!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style="background-color:#0F172A; padding:10px; border-radius:10px; margin-top:30px; text-align:center">
            <p style="color:#94A3B8; font-size:12px">© 2025 FuturePaths | Career Guidance Platform</p>
        </div>
        """, unsafe_allow_html=True)
