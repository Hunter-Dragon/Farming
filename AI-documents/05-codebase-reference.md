# 05. Tham chiếu mã nguồn (file-by-file)

## Thư mục gốc

| File | Vai trò |
|---|---|
| `app.py` | Streamlit chat UI. Import `ask` từ `agent.py`, giữ lịch sử hội thoại trong `st.session_state.messages`. Không có logic nghiệp vụ, chỉ là lớp trình bày. |
| `agent.py` | Định nghĩa Agent: khởi tạo `ChatGoogleGenerativeAI` (model `claude-haiku-4-5`, `temperature=0`), system prompt ràng buộc chỉ trả lời dựa trên tool, `create_tool_calling_agent` + `AgentExecutor`. Hàm `ask(question)` xử lý luôn phần chuẩn hoá output (Gemini đôi khi trả `output` dạng list content-blocks thay vì string thuần — có 2 nhánh xử lý cho việc này). |
| `tools.py` | Khai báo 2 LangChain `@tool`: `query_crop_knowledge_graph(crop_name)` (gọi GraphQL qua `gql.Client`, endpoint hard-code `http://localhost:8001/graphql`) và `search_agriculture_documents(question)` (gọi `hybrid_search` từ `hybrid_retriever.py`). Danh sách `tools = [...]` được `agent.py` import trực tiếp. |
| `hybrid_retriever.py` | Xây `EnsembleRetriever` (LangChain) gồm `BM25Retriever` (load từ `chunks_cache.pkl`, `k=4`) và Chroma vector retriever (`k=4`, từ `rag_retriever.py`). Trọng số đọc qua env var `BM25_WEIGHT` / `SEMANTIC_WEIGHT` (mặc định 0.4/0.6) — **đã sửa để hỗ trợ ablation study**, xem file 06. Hàm `hybrid_search(query)` trả về list nội dung chunk (string). |
| `rag_retriever.py` | Khởi tạo `HuggingFaceEmbeddings` (model `bkai-foundation-models/vietnamese-bi-encoder`) và `Chroma` vectordb (persist tại `./chroma_db`). Export biến `vectordb` dùng chung bởi `hybrid_retriever.py` và `add_document.py`. Có hàm `semantic_search()` riêng nhưng hiện không được gọi ở đâu khác (chỉ vector search thuần, không phải hybrid). |
| `ingest_rag.py` | Script one-shot: load toàn bộ `docs/*.txt` → chunk (`RecursiveCharacterTextSplitter`, size=500, overlap=50) → embed + ghi vào Chroma → pickle toàn bộ chunks ra `chunks_cache.pkl` (dùng cho BM25). Chạy lại sẽ tạo/ghi đè `chroma_db/` — **không idempotent an toàn nếu chạy nhiều lần** (có thể nhân đôi dữ liệu trong Chroma nếu không xoá `chroma_db/` trước; cần kiểm tra trước khi chạy lại). |
| `add_document.py` | Nạp bổ sung tài liệu mới không cần ingest lại toàn bộ: danh sách file hard-code trong biến `new_files` (**phải sửa tay file này mỗi lần muốn thêm tài liệu** — không nhận tham số dòng lệnh). Thêm chunk mới vào Chroma (`vectordb.add_documents`) và append vào `chunks_cache.pkl`. |
| `csv_to_rdf.py` | Chuyển `crops_data.csv` → `crops_data.ttl` (RDF/Turtle). Xem chi tiết logic ở file 04-data-and-ontology.md. |
| `sparql_client.py` | `run_sparql(query)`: gửi SPARQL SELECT tới GraphDB endpoint hard-code `http://localhost:7200/repositories/Farming`, trả về `results.bindings` (JSON). Có prefix `agri:`/`rdfs:` chèn sẵn vào đầu mọi query. |
| `schema.py` | Định nghĩa GraphQL schema bằng Strawberry: type `Crop`, `GrowthStage`, `Disease`, field resolver `Crop.growth_stages`, `Crop.diseases` (mỗi resolver tự gọi `run_sparql`), `Query.crop(name)`, `Query.all_crops()`. Xem giới hạn field ở file 04. |
| `main.py` | FastAPI app, mount GraphQL router tại `/graphql` (dùng `schema` từ `schema.py`). Chạy bằng `uvicorn main:app`. |
| `agri-ontology.ttl` | Ontology OWL (TBox) — class/property definitions. Soạn bằng Protégé. |
| `crops_data.ttl` | Instance data (ABox) — sinh tự động từ `crops_data.csv`, **không sửa tay**, chạy lại `csv_to_rdf.py` nếu cần cập nhật. |
| `crops_data.csv` | Dữ liệu nguồn dạng bảng — nguồn duy nhất cần sửa nếu muốn thay đổi dữ liệu KG. |
| `docs/*.txt` | 6 file văn bản kỹ thuật canh tác — nguồn cho RAG. |
| `chroma_db/` | Thư mục dữ liệu Chroma tự sinh (binary, không commit sửa tay). |
| `chunks_cache.pkl` | Pickle cache chunk gốc, dùng để build BM25Retriever mỗi lần khởi động — tự sinh, không sửa tay. |
| `requirements.txt` | Toàn bộ dependency Python. |
| `api-key.env` | File **mẫu** chứa `GOOGLE_API_KEY` demo — không phải key production, cần thay bằng key thật khi chạy (đặt trong `.env`, không phải `api-key.env`, theo README). |
| `README.md` | Tài liệu gốc, tiếng Việt, dành cho người vận hành/chạy hệ thống (không phải cho AI agent) — bộ AI-documents/ này bổ sung góc nhìn kỹ thuật sâu hơn, không thay thế README. |

## Thư mục `eval/` (bộ script đánh giá thực nghiệm cho bài báo)

Xem chi tiết ở file [06-evaluation-pipeline.md](06-evaluation-pipeline.md)
và [eval/README.md](../eval/README.md) (hướng dẫn vận hành đầy đủ).

| File | Vai trò |
|---|---|
| `eval/questions.json` | 24 câu hỏi đánh giá + ground truth, sinh từ `crops_data.csv` + trích tay từ `docs/*.txt`. |
| `eval/build_questions.py` | Script sinh lại `questions.json` (không cần chạy hệ thống, chỉ đọc dữ liệu tĩnh). |
| `eval/run_eval.py` | Chạy Agent thật qua toàn bộ câu hỏi, ghi câu trả lời/tool gọi/latency. |
| `eval/score_answers.py` | Chấm điểm: Recall tự động cho câu KG, LLM-as-judge (gọi Gemini) cho câu RAG/multi. |
| `eval/ablation_run.py` | Chạy lại câu hỏi RAG/multi với 3 cấu hình trọng số Hybrid Retriever khác nhau (subprocess + env var). |
| `eval/compare_ablation.py` | In bảng so sánh kết quả giữa các cấu hình ablation. |
| `eval/README.md` | Hướng dẫn vận hành đầy đủ (cho người/máy thực sự chạy hệ thống). |

## `bài báo mẫu/`

Chứa 1 file PDF mẫu (`2026_Ontology-enhanced RAG for a personalised and
sustainable food advisory system.pdf`) — bài báo tham khảo về cấu trúc/văn
phong để soạn bài báo cho project này. Xem file 07.

## Những điểm cần lưu ý khi AI agent sửa code trong tương lai

- Không có test tự động — mọi thay đổi logic Agent/tool nên được xác minh
  thủ công (chạy `agent.ask(...)`) hoặc qua `eval/run_eval.py`.
- `sparql_client.py` và `tools.py` hard-code URL endpoint
  (`localhost:7200`, `localhost:8001`) — không đọc từ `.env`. Nếu deploy
  lên môi trường khác cần sửa trực tiếp trong code (chưa được tham số hoá).
- `agent.py` đọc `GOOGLE_API_KEY` qua `os.getenv`, gọi `load_dotenv()` nên
  cần file `.env` ở đúng working directory lúc chạy script.
