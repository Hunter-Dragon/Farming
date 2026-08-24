# rag_retriever.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
vectordb = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

def semantic_search(query: str, k: int = 4):
    docs = vectordb.similarity_search(query, k=k)
    return [d.page_content for d in docs]