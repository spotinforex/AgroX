import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
from src.hybrid_llm import HybridLLM

# Load SentenceTransformer model
embedding_model = SentenceTransformer(r"AgroX\models\all-MiniLM-L6-v2")  # or 'sentence-transformers/all-MiniLM-L6-v2'

# Load FAISS index
index_path = Path.home() / "Documents" / "AgroX" / "index" / "faiss_index"
index = faiss.read_index(str(index_path / "index.faiss"))


# Init your local/online LLM
llm = HybridLLM(use_online=True)  # set to True if you want to call Gemini or similar

# Query pipeline
def retrieve_answer(query: str, top_k=3):
    # Embed query
    query_vector = embedding_model.encode([query])

    # Search FAISS
    D, I = index.search(np.array(query_vector).astype("float32"), top_k)

    # Retrieve top_k context docs
    context = I

    # Combine prompt
    prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {query}\nAnswer:"

    # Get response from LLM
    response = llm(prompt)
    return response
