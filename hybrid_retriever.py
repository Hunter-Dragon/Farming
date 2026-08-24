# hybrid_retriever.py
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from rag_retriever import vectordb

# Cần load lại toàn bộ chunk gốc để build BM25 (từ bước ingest)
import pickle
with open("chunks_cache.pkl", "rb") as f:
    all_chunks = pickle.load(f)

bm25_retriever = BM25Retriever.from_documents(all_chunks)
bm25_retriever.k = 4

semantic_retriever = vectordb.as_retriever(search_kwargs={"k": 4})

hybrid_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, semantic_retriever],
    weights=[0.4, 0.6]
)

def hybrid_search(query: str):
    docs = hybrid_retriever.invoke(query)
    return [d.page_content for d in docs]