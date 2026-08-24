# add_document.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_retriever import vectordb
import pickle

# Đường dẫn tới file mới muốn thêm
new_file_path = "./docs/ky-thuat-moi.txt"

loader = TextLoader(new_file_path, encoding="utf-8")
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
new_chunks = splitter.split_documents(docs)

vectordb.add_documents(new_chunks)

# Cập nhật lại chunks_cache.pkl (cộng dồn cho BM25)
with open("chunks_cache.pkl", "rb") as f:
    all_chunks = pickle.load(f)
all_chunks.extend(new_chunks)
with open("chunks_cache.pkl", "wb") as f:
    pickle.dump(all_chunks, f)

print(f"Đã thêm {len(new_chunks)} đoạn mới")