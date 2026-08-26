# 02. Kiến trúc hệ thống

## Sơ đồ luồng dữ liệu

```
Người dùng
   │
   ▼
Streamlit UI (app.py)
   │  gọi hàm ask(question) từ agent.py
   ▼
LangChain Tool-Calling Agent (agent.py)
   │  model: ChatGoogleGenerativeAI (Gemini, model "claude-haiku-4-5", temperature=0)
   │  prompt: hệ thống ràng buộc "chỉ trả lời dựa trên tool trả về, không bịa"
   │
   ├──► Tool 1: query_crop_knowledge_graph (tools.py)
   │      │ gửi GraphQL query tới http://localhost:8001/graphql (gql Client)
   │      ▼
   │    GraphQL API (main.py: FastAPI + strawberry GraphQLRouter, schema.py)
   │      │ resolver Crop.growth_stages / Crop.diseases
   │      ▼
   │    SPARQL Client (sparql_client.py) → GraphDB repository "Farming"
   │      (http://localhost:7200/repositories/Farming)
   │      dữ liệu nạp từ agri-ontology.ttl (schema) + crops_data.ttl (instance data,
   │      sinh từ crops_data.csv qua csv_to_rdf.py)
   │
   └──► Tool 2: search_agriculture_documents (tools.py)
          │ gọi hybrid_search() trong hybrid_retriever.py
          ▼
        EnsembleRetriever (LangChain) = BM25Retriever + Chroma vector retriever
          - BM25Retriever: build từ chunks_cache.pkl (pickle toàn bộ Document chunks)
          - vector retriever: rag_retriever.py → Chroma persist tại ./chroma_db,
            embedding model "bkai-foundation-models/vietnamese-bi-encoder"
          - trọng số: BM25_WEIGHT=0.4, SEMANTIC_WEIGHT=0.6 (đọc qua env var,
            mặc định hard-code nếu không set — xem 05-codebase-reference.md)
          dữ liệu nguồn: docs/*.txt (nạp qua ingest_rag.py hoặc add_document.py)
```

## Hai "lớp" tri thức tách biệt

| | Structured (Knowledge Graph) | Unstructured (Hybrid RAG) |
|---|---|---|
| Nguồn dữ liệu | `crops_data.csv` → `crops_data.ttl` | `docs/*.txt` |
| Lưu trữ | GraphDB (RDF triple store) | ChromaDB (vector) + pickle cache (BM25) |
| Truy vấn | SPARQL (qua lớp GraphQL trung gian) | Ensemble similarity search |
| Nội dung | Giai đoạn sinh trưởng, bệnh, sâu hại, đất, khí hậu, mùa vụ, phân bón (theo từng dòng CSV) | Hướng dẫn kỹ thuật canh tác dạng văn xuôi cho 6 loại rau |
| Truy vấn thực tế hiện expose qua GraphQL | Chỉ `growthStages` và `diseases` (xem `schema.py`) — các field khác (pest, soil, season, fertilizer) **có trong ontology/RDF nhưng chưa có resolver GraphQL**, chưa được Agent dùng tới | — |

**Lưu ý quan trọng khi phân tích/viết bài báo**: dù `agri-ontology.ttl` và
`csv_to_rdf.py` định nghĩa đầy đủ quan hệ `attackedBy` (Pest),
`requiresSoil` (SoilType), `plantedInSeason` (Season), `treatedWith`
(FertilizerType), nhưng `schema.py` (lớp GraphQL) **chỉ resolve
`growthStages` và `diseases`**. Nghĩa là Agent hiện tại chỉ thực sự dùng
được 2/6 loại quan hệ trong ontology. Nếu bài báo mô tả ontology "đầy đủ"
thì nên làm rõ phần nào đã kết nối tới pipeline truy vấn thực tế, phần nào
mới dừng ở mức thiết kế dữ liệu (để tránh nói quá khả năng hệ thống).

## Hai server cần chạy song song

1. **GraphQL backend**: `uvicorn main:app --host 0.0.0.0 --port 8001` — expose `/graphql`.
2. **Streamlit frontend**: `streamlit run app.py` — expose `:8501`, gọi trực tiếp
   `agent.ask()` trong cùng tiến trình Python (không qua HTTP), agent lại gọi
   GraphQL server ở bước trên qua HTTP.

Ngoài ra **GraphDB** là một service riêng (Java, Ontotext GraphDB), phải
chạy độc lập trước (không phải process Python trong repo này) — xem
03-setup-and-run.md.

## Tech stack

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.10+ (môi trường viết bài báo hiện dùng Python 3.14 để soạn script tĩnh, nhưng hệ thống thật nên chạy 3.10/3.11 theo khuyến nghị README gốc) |
| LLM & Agent | Google Gemini (`ChatGoogleGenerativeAI`), LangChain (`langchain-classic` cho `create_tool_calling_agent`/`AgentExecutor`) |
| Knowledge Graph | Ontotext GraphDB, RDFLib (sinh triples), SPARQLWrapper (truy vấn) |
| GraphQL API | FastAPI + Strawberry GraphQL + Uvicorn, client `gql` |
| Vector DB & Embedding | ChromaDB, HuggingFace `bkai-foundation-models/vietnamese-bi-encoder` |
| Lexical Search | `rank_bm25` qua `langchain_community.retrievers.BM25Retriever` |
| Frontend | Streamlit (chat UI đơn giản, lưu lịch sử trong `st.session_state`) |
| Config | `python-dotenv` (`.env` / `api-key.env`) |
