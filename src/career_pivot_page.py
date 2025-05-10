import numpy as np
import faiss
import streamlit as st
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_predictor():
    # Load precomputed job labels + FAISS index
    next_jobs = np.load('src/next_jobs.npy', allow_pickle=True)
    index = faiss.read_index('faiss_index.index')

    # Load SentenceTransformer model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return model, index, next_jobs

def extract_job_title_and_description(raw_text):
    """
    Splits the raw job text into (title, description).
    """
    parts = raw_text.split("description:")
    title = parts[0].replace("esco role:", "").strip().capitalize()
    description = parts[1].strip() if len(parts) > 1 else "No description available."
    return title, description

def run():
    st.title("🚀 Career Changer Pathfinder")
    st.caption("Find your next career pivot with smarter AI suggestions! 🎯")

    model, index, next_jobs = load_predictor()

    # User Input
    st.subheader("📝 Enter your career path")
    career_input = st.text_area(
        "Example: Marketing Intern → Marketing Specialist → Digital Marketing Manager"
    )

    if st.button("🔎 Suggest Next Steps"):
        if career_input.strip() == "":
            st.warning("Please enter your career path above.")
        else:
            with st.spinner("Analyzing and generating suggestions..."):
                # Embed user input
                input_embedding = model.encode([career_input])
                input_embedding = input_embedding / np.linalg.norm(input_embedding, axis=1, keepdims=True)
                input_embedding = input_embedding.astype('float32')

                # Search using FAISS index
                distances, indices = index.search(input_embedding, 3)

                st.success("✅ Here are your Top 3 Career Pivot Suggestions:")

                for i, idx in enumerate(indices[0]):
                    confidence = distances[0][i]
                    raw_text = next_jobs[idx]
                    job_title, job_desc = extract_job_title_and_description(raw_text)

                    with st.expander(f"🔎 {job_title} (Similarity: {confidence:.2f})"):
                        st.markdown(f"**📝 What You'll Do:**\n{job_desc[:300]}...")  # Shortened
                        st.markdown("**💼 Why It’s Interesting:**\nThis role is ideal if you want to gain experience in the field and build towards mid- and senior-level positions.")
                        st.markdown(f"**🔗 Learn More:** [Search {job_title} Internships](https://www.google.com/search?q={job_title.replace(' ', '+')}+Internships)")
