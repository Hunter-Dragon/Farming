# 03. Cài đặt & Chạy hệ thống

Tóm tắt từ `README.md` gốc — xem file đó để có bản đầy đủ với giải thích.
Đây là bản rút gọn dạng checklist cho AI agent cần tự chạy/hướng dẫn chạy.

## Yêu cầu

- Python 3.10 hoặc 3.11 (khuyến nghị — bản mới hơn như 3.14 có thể gặp vấn
  đề tương thích với `torch`/`chromadb`/`sentence-transformers`, chưa kiểm
  chứng đầy đủ).
- Java JDK 11+ (chạy Ontotext GraphDB).
- Ontotext GraphDB (Free/SE), chạy local hoặc Docker, Workbench tại
  `http://localhost:7200`.
- Google Gemini API Key (từ Google AI Studio).

## Các bước theo thứ tự

1. **Tạo venv + cài dependencies**
   ```bash
   python -m venv venv
   # kích hoạt venv rồi:
   pip install -r requirements.txt
   ```

2. **Cấu hình API key — BẮT BUỘC phải tự tạo, không có sẵn trong git**

   Kể từ khi repo có `.gitignore` đúng chuẩn, các file chứa secret
   (`.env`, `api-key.env`, `*.env`) **không được push lên GitHub** — khi
   `git pull` về sẽ **không thấy** các file này. Đây là hành vi có chủ ý
   (bảo mật), không phải thiếu sót.

   Người chạy hệ thống (kể cả AI agent) phải **tự tạo file `.env` mới** ở
   thư mục gốc project (`Farming/`) với nội dung:
   ```env
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   ```
   Lấy key thật tại [Google AI Studio](https://aistudio.google.com/) —
   **không** dùng lại key cũ từng thấy trong lịch sử chat/tài liệu, vì đó
   là key demo có thể đã hết hạn hoặc bị thu hồi vì lý do bảo mật.

   Kiểm tra nhanh `.env` đã đúng chưa (không cần chạy cả hệ thống):
   ```bash
   python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OK' if os.getenv('GOOGLE_API_KEY') else 'THIEU GOOGLE_API_KEY')"
   ```

3. **Các giá trị cấu hình KHÔNG phải biến môi trường** (dễ nhầm lẫn — liệt
   kê rõ để khỏi mất công tìm biến môi trường không tồn tại):

   | Giá trị | Nằm ở đâu (hard-code trong code) | Ghi chú |
   |---|---|---|
   | GraphDB endpoint | `sparql_client.py`, biến `GRAPHDB_ENDPOINT` = `http://localhost:7200/repositories/Farming` | Sửa trực tiếp trong code nếu GraphDB chạy ở host/port khác |
   | GraphQL URL Agent gọi tới | `tools.py`, biến `transport` = `http://localhost:8001/graphql` | Tương tự, sửa trực tiếp trong code nếu cần |
   | Embedding model | `rag_retriever.py`, `ingest_rag.py` — `bkai-foundation-models/vietnamese-bi-encoder` | Tải tự động từ HuggingFace lần đầu chạy (cần internet, ~500MB) |
   | LLM model | `agent.py` — `gemini-3.6-flash` | — |
   | Trọng số Hybrid Retriever | `hybrid_retriever.py` — **CÓ đọc qua env var** `BM25_WEIGHT` / `SEMANTIC_WEIGHT`, mặc định `0.4`/`0.6` nếu không set | Đây là biến môi trường DUY NHẤT ngoài `GOOGLE_API_KEY` mà hệ thống thực sự đọc — chỉ cần set khi chạy `eval/ablation_run.py`, không cần set khi chạy app bình thường |

4. **Thiết lập GraphDB**
   - Mở Workbench (`http://localhost:7200`) → Setup → Repositories → Create
     new repository → chọn **GraphDB Free** → `Repository ID = Farming`
     (phải khớp đúng tên trong `sparql_client.py`, biến `GRAPHDB_ENDPOINT`).
   - Nếu `crops_data.csv` mới thay đổi, sinh lại RDF: `python csv_to_rdf.py`
     (ghi ra `crops_data.ttl`).
   - Import vào GraphDB (Import → User data → Upload RDF files): cả
     `agri-ontology.ttl` (schema/ontology) và `crops_data.ttl` (dữ liệu
     thực thể).

5. **Nạp dữ liệu RAG (Vector DB + BM25 cache)**
   ```bash
   python ingest_rag.py
   ```
   Tạo ra `chroma_db/` và `chunks_cache.pkl`. **Lưu ý**: `chroma_db/` và
   `chunks_cache.pkl` hiện đang được commit sẵn trong git (không bị
   `.gitignore` loại bỏ vì đã tồn tại trong lịch sử trước khi có
   `.gitignore` đúng chuẩn) — sau khi `git pull`, 2 thứ này **đã có sẵn**,
   không bắt buộc phải chạy lại bước này trừ khi `docs/*.txt` thay đổi
   hoặc file bị thiếu/hỏng. Nếu muốn thêm tài liệu mới mà không ingest lại
   từ đầu, dùng `add_document.py` (sửa danh sách `new_files` trong file đó
   trước).

6. **Chạy GraphQL backend** (terminal riêng):
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

7. **Chạy giao diện chat** (terminal riêng):
   ```bash
   streamlit run app.py
   ```
   Mở `http://localhost:8501`.

## Thứ tự phụ thuộc quan trọng

`app.py` → `agent.py` → `tools.py` → (`sparql_client.py` cần GraphDB đã
chạy VÀ đã import data) + (`hybrid_retriever.py` cần `chunks_cache.pkl` đã
tồn tại VÀ `chroma_db/` đã có dữ liệu). Nếu thiếu bất kỳ điều kiện nào,
Agent sẽ lỗi khi gọi tool tương ứng (không phải lỗi ở tầng UI).

## Kiểm tra nhanh từng phần độc lập (debug)

- Kiểm tra GraphQL: mở `http://localhost:8001/graphql` (GraphiQL UI), chạy:
  ```graphql
  query { crop(name: "Cà chua") { growthStages { name durationDays } diseases { name } } }
  ```
- Kiểm tra Hybrid RAG độc lập (không qua Agent, không cần API key):
  ```python
  from hybrid_retriever import hybrid_search
  print(hybrid_search("cách bón phân cho cà chua"))
  ```
- Kiểm tra Agent end-to-end (cần cả GraphDB + GraphQL server + API key):
  ```python
  from agent import ask
  print(ask("Cây cà chua có những giai đoạn sinh trưởng nào?"))
  ```

## Máy hiện tại (viết bài báo) không chạy được hệ thống

Máy đang dùng để soạn bài báo/tài liệu **không có GraphDB, có thể không có
GPU hoặc chưa cài đủ dependency nặng** (torch, sentence-transformers) —
chỉ dùng để đọc/sửa code và soạn văn bản tĩnh. Phần chạy thực nghiệm được
giao cho máy khác qua bộ script trong `eval/` (xem file 06). Đừng giả định
agent code này chạy được ngay tại đây — luôn kiểm tra bằng
`python -m py_compile <file>.py` (chỉ bắt lỗi cú pháp) thay vì chạy thật
nếu cần xác minh nhanh trên máy này.
