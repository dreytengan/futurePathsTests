# resume_upload_and_predict_page.py
import streamlit as st
import numpy as np
# No need to import faiss or SentenceTransformer directly if using functions from career_pivot_page
# from sentence_transformers import SentenceTransformer
# import faiss

# Import functions from other files in the src directory
from utils.resume_parser import parse_resume_data
from career_pivot_page import load_predictor, extract_job_title_and_description

def generate_suggestions_from_text(model, index, next_jobs_data, query_text, top_n=5):
    """
    Generates suggestions based on a query text.
    This is similar to the logic in career_pivot_page but generalized.
    """
    if not query_text or not model or index is None or next_jobs_data is None:
        return []
        
    input_embedding = model.encode([query_text])
    input_embedding = input_embedding / np.linalg.norm(input_embedding, axis=1, keepdims=True)
    input_embedding = input_embedding.astype('float32')

    try:
        distances, indices = index.search(input_embedding, top_n)
    except Exception as e:
        st.error(f"FAISS search error: {e}. Ensure the index is loaded correctly and compatible.")
        return []
    
    results = []
    if indices.size > 0 and len(indices[0]) > 0:
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(next_jobs_data):
                # This case should ideally not happen if index and data are consistent
                # print(f"Warning: Index {idx} out of bounds for next_jobs_data (size {len(next_jobs_data)})")
                continue
            
            # In career_pivot_page, 'distances' are used directly as 'confidence'.
            # For IndexFlatIP (cosine similarity) with normalized vectors, this is correct.
            # Higher values mean higher similarity.
            confidence_score = distances[0][i] 
            
            raw_job_text = next_jobs_data[idx]
            job_title, job_desc = extract_job_title_and_description(raw_job_text) # Reusing this
            results.append({
                "title": job_title,
                "description": job_desc,
                "confidence": confidence_score 
            })
    return results


def run(): # Standardized run function for Streamlit pages
    st.title("📄 Resume Analyzer & Career Suggester")
    
    # Load the model, FAISS index, and job data
    # This uses the cached function from career_pivot_page
    try:
        model, faiss_index, next_jobs_data = load_predictor()
    except Exception as e:
        st.error(f"Failed to load predictor resources: {e}")
        st.error("Please ensure 'src/next_jobs.npy' and 'src/faiss_index.index' exist and are valid, and that 'sentence-transformers/all-MiniLM-L6-v2' can be downloaded/loaded.")
        st.warning("The application might not function correctly without these resources.")
        # Attempt to proceed if only some parts failed, or stop if critical
        if 'faiss_index' not in locals() or 'next_jobs_data' not in locals():
             st.stop() # Stop if critical components are missing

    st.markdown("""
    Upload your resume (PDF) to extract your experience and skills.
    Then, get tailored career suggestions for conventional paths or exciting pivots!
    """)

    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf", key="resume_uploader")
    
    if 'parsed_resume_data' not in st.session_state:
        st.session_state.parsed_resume_data = None
    if 'resume_filename' not in st.session_state:
        st.session_state.resume_filename = None

    if uploaded_file is not None:
        if st.session_state.resume_filename != uploaded_file.name:
            with st.spinner("🔬 Analyzing your resume... This may take a moment."):
                parsed_data = parse_resume_data(uploaded_file) # from src.resume_parser
                if parsed_data and "error" not in parsed_data:
                    st.session_state.parsed_resume_data = parsed_data
                    st.session_state.resume_filename = uploaded_file.name
                    st.success("Resume analyzed successfully!")
                elif parsed_data and "error" in parsed_data:
                    st.error(f"Resume parsing failed: {parsed_data['error']}")
                    st.session_state.parsed_resume_data = None
                    st.session_state.resume_filename = None
                else:
                    st.error("Could not parse the resume or the file is empty. Please try a different PDF.")
                    st.session_state.parsed_resume_data = None
                    st.session_state.resume_filename = None
    
    if st.session_state.parsed_resume_data:
        data = st.session_state.parsed_resume_data
        st.subheader("📝 Extracted Resume Insights")

        # Display extracted info (conditionally)
        if data.get("most_recent_job"):
            mrj = data["most_recent_job"]
            st.write(f"**Most Recent Role (extracted):** {mrj.get('title', 'N/A')}")
            if mrj.get("description"):
                 with st.expander("View Recent Role Description (extracted)"):
                    st.markdown(f"_{mrj.get('company_date_info', '')}_")
                    st.text(mrj['description'][:1000] + ("..." if len(mrj['description']) > 1000 else ""))
        else:
            st.write("Could not identify a most recent job clearly from the resume.")

        if data.get("skills"):
            st.write(f"**Extracted Skills:** {', '.join(data['skills'][:20])}" + ("..." if len(data['skills']) > 20 else ""))
        else:
            st.write("No distinct skills section found or skills could not be automatically extracted.")
        
        st.markdown("---")
        
        suggestion_type = st.radio(
            "Choose suggestion type:",
            ("📈 Conventional Career Path", "↔️ Career Pivot"),
            key="suggestion_type_radio"
        )

        query_text_conventional = ""
        if data.get("most_recent_job"):
            mrj = data["most_recent_job"]
            query_text_conventional = f"Current role: {mrj.get('title', 'Experienced Professional')}. "
            desc_snippet = ""
            if mrj.get("description"):
                desc_snippet = (mrj['description'][:300] + "...") if len(mrj['description']) > 300 else mrj['description']
            if desc_snippet:
                 query_text_conventional += f"Responsibilities and experience include: {desc_snippet}. "
        if data.get("skills"):
            query_text_conventional += f"Key skills include: {', '.join(data['skills'][:15])}."
        else: # If no specific job/skills, use summary or fallback
            summary_text = data.get("summary", "Professional with diverse experience.")
            query_text_conventional = f"Professional profile summary: {summary_text[:500]}. "


        if suggestion_type == "📈 Conventional Career Path":
            st.subheader("📈 Conventional Career Path Suggestions")
            if not query_text_conventional.strip() or query_text_conventional.startswith("Professional profile summary: Professional with diverse experience.") : # check for weak query
                st.warning("Limited information extracted (e.g. recent job title, specific skills). Suggestions might be general. Try adding more details if possible or ensure your resume is clearly formatted.")
            
            if st.button("Suggest Conventional Paths", key="conv_button"):
                if not query_text_conventional.strip():
                    st.error("Cannot generate suggestions without some information from the resume.")
                else:
                    with st.spinner("Finding conventional next steps..."):
                        recommendations = generate_suggestions_from_text(
                            model, faiss_index, next_jobs_data, query_text_conventional, top_n=3
                        )
                        if recommendations:
                            st.success(f"Here are your Top {len(recommendations)} Conventional Suggestions:")
                            for rec in recommendations:
                                with st.expander(f"{rec['title']} (Similarity: {rec['confidence']:.2f})"):
                                    st.markdown(f"**Description Snippet:**\n{rec['description'][:300]}...")
                                    st.markdown(f"**🔗 Learn More:** [Search for {rec['title']}](https://www.google.com/search?q={rec['title'].replace(' ', '+')})")
                        else:
                            st.info("No specific conventional path suggestions found based on the extracted information. The model may not have direct paths from roles very similar to yours, or the extracted info was too generic.")
        
        elif suggestion_type == "↔️ Career Pivot":
            st.subheader("↔️ Career Pivot Suggestions")
            aspirations = st.text_area(
                "Optional: Describe your professional aspirations or interests for a pivot (e.g., 'I want to work in data science', 'Interested in sustainability and tech', 'Enjoy creative problem solving and user-centered design')",
                height=100,
                key="aspirations_input_resume" # Unique key
            )
            
            if st.button("Suggest Career Pivots", key="pivot_button_resume"): # Unique key
                query_text_pivot = ""
                # Prioritize skills for pivot, then job description, then summary
                if data.get("skills"): 
                    query_text_pivot += f"Seeking a new role leveraging skills such as: {', '.join(data['skills'][:20])}. "
                elif data.get("most_recent_job") and data["most_recent_job"].get("description"):
                    mrj_desc = data["most_recent_job"]["description"]
                    desc_snippet = (mrj_desc[:300] + "...") if len(mrj_desc) > 300 else mrj_desc
                    query_text_pivot += f"Experienced in tasks such as: {desc_snippet}. "
                elif data.get("summary"):
                     query_text_pivot += f"Professional summary includes: {data['summary'][:300]}. "


                if aspirations.strip():
                    query_text_pivot += f"Future career aspirations and interests include: {aspirations.strip()}."
                else: 
                    query_text_pivot += "Open to exploring challenging new career directions and pivot opportunities that build upon existing experience."

                if not query_text_pivot.strip() or \
                   (not data.get("skills") and not data.get("most_recent_job") and not data.get("summary") and not aspirations.strip()):
                     st.warning("Not enough information (skills, past experience, or aspirations) to suggest pivots effectively. Please ensure resume has extractable info or add aspirations.")
                else:
                    with st.spinner("Exploring career pivot options..."):
                        recommendations = generate_suggestions_from_text(
                            model, faiss_index, next_jobs_data, query_text_pivot, top_n=3 # Pivots often want a few strong ideas
                        )
                        if recommendations:
                            st.success(f"Here are your Top {len(recommendations)} Pivot Suggestions:")
                            for rec in recommendations:
                                with st.expander(f"{rec['title']} (Similarity: {rec['confidence']:.2f})"):
                                    st.markdown(f"**Description Snippet:**\n{rec['description'][:300]}...")
                                    st.markdown(f"**Why it might be a good pivot:** This role may align with your stated interests or offer a new application for your existing skills and experience.")
                                    st.markdown(f"**🔗 Learn More:** [Search for {rec['title']}](https://www.google.com/search?q={rec['title'].replace(' ', '+')})")
                        else:
                            st.info("No career pivot suggestions found. Try refining your aspirations or ensure your resume has clear, extractable information about your skills and experience.")
    else:
        if uploaded_file is None:
            st.info("👋 Welcome! Please upload your resume (PDF) to get started.")
        # If upload failed or parsing yielded nothing, message already shown