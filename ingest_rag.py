# ingest_rag.py
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import pickle

loader = DirectoryLoader("./docs", glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="bkai-foundation-models/vietnamese-bi-encoder")
vectordb = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")
vectordb.persist()

with open("chunks_cache.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"Đã nạp {len(chunks)} đoạn văn bản vào vector DB")
