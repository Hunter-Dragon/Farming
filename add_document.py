# add_document.py
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag_retriever import vectordb
import pickle

# Danh sách các file mới muốn thêm vào RAG
new_files = [
    "./docs/ky-thuat-bi-do.txt",
    "./docs/ky-thuat-bi-xanh.txt",
    "./docs/ky-thuat-ca-chua-2.txt",
    "./docs/ky-thuat-ca-chua-3.txt",
    "./docs/ky-thuat-ca-phao.txt",
    "./docs/ky-thuat-cu-cai-trang.txt",
    "./docs/ky-thuat-cu-den.txt",
    "./docs/ky-thuat-dau-co-leo.txt",
    "./docs/ky-thuat-dau-ha-lan.txt",
    "./docs/ky-thuat-dua-leo-2.txt",
    "./docs/ky-thuat-su-hao-2.txt",
    "./docs/ky-thuat-hanh-tay.txt",
    "./docs/ky-thuat-khoai-tay.txt",
    "./docs/ky-thuat-muop-dang.txt",
    "./docs/ky-thuat-ot-chuong.txt",
    "./docs/ky-thuat-rau-muong-2.txt",
]

all_new_chunks = []
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

for file_path in new_files:
    loader = TextLoader(file_path, encoding="utf-8")
    docs = loader.load()
    chunks = splitter.split_documents(docs)
    all_new_chunks.extend(chunks)
    print(f"Đã xử lý {file_path}: {len(chunks)} đoạn")

vectordb.add_documents(all_new_chunks)

with open("chunks_cache.pkl", "rb") as f:
    all_chunks = pickle.load(f)
all_chunks.extend(all_new_chunks)
with open("chunks_cache.pkl", "wb") as f:
    pickle.dump(all_chunks, f)

print(f"\nHoàn tất: đã thêm {len(all_new_chunks)} đoạn mới từ {len(new_files)} file")