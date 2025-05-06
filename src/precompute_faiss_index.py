import numpy as np
import faiss
from predictor import LabelSpace
from sentence_transformers import SentenceTransformer
from utils import load_prepare_karrierewege

# Load data (just once)
train_pairs, _, _ = load_prepare_karrierewege(minus_last=False, language='en')
next_jobs = list(set([pair[1] for pair in train_pairs]))

# Build label space (embeds & builds FAISS index)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
label_space = LabelSpace(model, next_jobs)

# Save FAISS index + job labels
faiss.write_index(label_space.index, 'faiss_index.index')
np.save('next_jobs.npy', np.array(next_jobs))

print("✅ Precompute done! Saved faiss_index.index + next_jobs.npy")
