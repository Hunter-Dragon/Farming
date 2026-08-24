# 🥬 Trợ lý AI Nông nghiệp Rau củ (Agri AI Assistant)

> **Hệ thống trợ lý thông minh tư vấn canh tác rau củ kết hợp Đồ thị Tri thức (Knowledge Graph) và Tìm kiếm Lai (Hybrid Search / Graph-RAG) trên nền tảng LLM Agent.**

---

## 📖 1. Giới thiệu tổng quan (Overview)

**Trợ lý AI Nông nghiệp Rau củ** là một giải pháp hỏi đáp thông minh dành cho người làm nông nghiệp, kỹ sư nông học và người trồng trọt. Hệ thống tích hợp mô hình ngôn ngữ lớn (**Google Gemini Flash**) với cơ chế **Agentic Tool-Calling**, cho phép truy xuất và tổng hợp thông tin từ hai nguồn dữ liệu:

1. **Dữ liệu có cấu trúc (Knowledge Graph)**: Lưu trữ và biểu diễn ontology nông nghiệp trên **GraphDB (RDF / OWL / SPARQL)**, truy vấn linh hoạt qua **GraphQL API** (FastAPI + Strawberry) để cung cấp thông tin chính xác về các loại cây trồng, giai đoạn sinh trưởng, thời gian phát triển, sâu bệnh hại, điều kiện thổ nhưỡng, mùa vụ và phân bón.
2. **Dữ liệu phi cấu trúc (Hybrid RAG)**: Cơ chế tìm kiếm lai kết hợp **Vector Search (ChromaDB + Vietnamese Bi-Encoder)** và **Keyword Search (BM25)** trên kho tài liệu hướng dẫn kỹ thuật canh tác, giúp giải thích chi tiết quy trình chăm sóc, phòng trừ bệnh và kỹ thuật nông nghiệp.

Agent có khả năng tự động suy luận (reasoning) và lựa chọn công cụ truy xuất thích hợp, đảm bảo câu trả lời luôn có dẫn chứng xác thực, chính xác và **hạn chế tối đa hiện tượng ảo giác (hallucination)**.

---

## ✨ 2. Các tính năng nổi bật (Features)

- 🧠 **Cơ chế Agent thông minh (Multi-tool Reasoning)**: Sử dụng LangChain Tool-Calling Agent để tự động phân tích câu hỏi của người dùng và quyết định truy vấn Knowledge Graph, tìm kiếm tài liệu RAG, hoặc kết hợp cả hai nguồn tri thức để đưa ra câu trả lời toàn diện.
- 🕸️ **Đồ thị tri thức Nông nghiệp (Agricultural Knowledge Graph)**:
  - Xây dựng mô hình Ontology hoàn chỉnh cho ngành rau củ (`agri-ontology.ttl`).
  - Hỗ trợ chuyển đổi tự động dữ liệu bảng (`crops_data.csv`) thành đồ thị tri thức chuẩn RDF/Turtle (`crops_data.ttl`).
  - Truy vấn ngữ nghĩa SPARQL thông qua lớp trừu tượng GraphQL API nhanh chóng và dễ mở rộng.
- 🔍 **Tìm kiếm lai tối ưu cho tiếng Việt (Vietnamese Hybrid Retrieval)**:
  - Kết hợp **Semantic Search** (Vector Embedding với mô hình `bkai-foundation-models/vietnamese-bi-encoder`) và **Lexical Search (BM25)** theo trọng số tối ưu (0.6 Semantic + 0.4 BM25).
  - Tăng độ chính xác khi tìm kiếm các thuật ngữ nông nghiệp chuyên ngành và mô tả kỹ thuật chi tiết.
- 💬 **Giao diện hội thoại tương tác (Streamlit Chat UI)**: Giao diện trực quan, hỗ trợ trò chuyện thời gian thực, lưu lịch sử phiên hỏi đáp.
- 📁 **Dễ dàng mở rộng kho tri thức**: Cung cấp script nạp tài liệu hàng loạt (`ingest_rag.py`) và nạp tài liệu bổ sung từng phần (`add_document.py`).

---

## 🏗️ 3. Kiến trúc hệ thống & Công nghệ sử dụng (Architecture & Tech Stack)

### Sơ đồ kiến trúc (System Architecture)

```mermaid
flowchart TD
    User([👤 Người dùng]) <--> UI[💻 Streamlit Web UI (app.py)]
    UI <--> Agent[🤖 LangChain AI Agent (Gemini Flash)]

    subgraph Tools [LangChain Tools (tools.py)]
        T1[Tool: query_crop_knowledge_graph]
        T2[Tool: search_agriculture_documents]
    end

    Agent <--> Tools

    subgraph KG_Layer [Lớp Tri thức có cấu trúc (Knowledge Graph)]
        T1 <--> GQL[GraphQL API (FastAPI + Strawberry)]
        GQL <--> SPARQL[SPARQL Client (sparql_client.py)]
        SPARQL <--> GraphDB[(Ontotext GraphDB\nRepository: Farming)]
        CSV[crops_data.csv] -->|csv_to_rdf.py| TTL[crops_data.ttl / agri-ontology.ttl]
        TTL -->|Import| GraphDB
    end

    subgraph RAG_Layer [Lớp Tri thức phi cấu trúc (Hybrid RAG)]
        T2 <--> Hybrid[Hybrid Retriever (BM25 + Semantic)]
        Hybrid <--> Chroma[(ChromaDB Vector Store\nVietnamese Bi-Encoder)]
        Hybrid <--> Cache[chunks_cache.pkl (BM25)]
        Docs[Tài liệu docs/*.txt] -->|ingest_rag.py / add_document.py| Chroma
        Docs -->|ingest_rag.py / add_document.py| Cache
    end
```

### Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ / Thư viện | Mô tả |
| :--- | :--- | :--- |
| **Ngôn ngữ** | Python 3.10+ | Môi trường lập trình chính |
| **LLM & Agent** | Google Gemini (`ChatGoogleGenerativeAI`), LangChain | Mô hình ngôn ngữ lớn và khung điều phối Agent |
| **Knowledge Graph** | Ontotext GraphDB, RDFLib, SPARQLWrapper | Lưu trữ Tri thức Semantic Web, truy vấn SPARQL |
| **GraphQL API** | FastAPI, Strawberry GraphQL, Uvicorn, GQL Client | API trung gian truy vấn GraphDB |
| **Vector DB & Embeddings** | ChromaDB, HuggingFace Transformers (`bkai-foundation-models/vietnamese-bi-encoder`) | Lưu trữ vector & trích xuất đặc trưng ngữ nghĩa tiếng Việt |
| **BM25 Search** | `rank_bm25`, LangChain Community BM25Retriever | Tìm kiếm theo từ khóa / tần suất từ |
| **Giao diện (Frontend)** | Streamlit | Giao diện Chatbot tương tác cho người dùng |
| **Cấu hình & Tiện ích** | `python-dotenv`, `pickle` | Quản lý cấu hình, bộ nhớ đệm chunk dữ liệu |

---

## 📂 4. Cấu trúc thư mục dự án (Project Structure)

```text
Farming/
├── docs/                        # Thư mục chứa tài liệu kỹ thuật canh tác (.txt)
│   ├── ky-thuat-bap-cai.txt
│   ├── ky-thuat-ca-chua.txt
│   ├── ky-thuat-ca-rot.txt
│   ├── ky-thuat-dua-leo.txt
│   ├── ky-thuat-rau-muong.txt
│   └── ky-thuat-su-hao.txt
├── chroma_db/                   # Thư mục cơ sở dữ liệu vector Chroma (tự sinh sau khi nạp)
├── chunks_cache.pkl             # File cache lưu trữ Document Chunks phục vụ BM25 Retriever
├── agri-ontology.ttl            # Định nghĩa Ontology nông nghiệp (OWL / RDF Schema)
├── crops_data.csv               # Bộ dữ liệu gốc cây trồng, bệnh, sâu hại, giai đoạn sinh trưởng
├── crops_data.ttl               # Dữ liệu Triples RDF sinh ra từ CSV để nạp vào GraphDB
├── csv_to_rdf.py                # Script chuyển đổi crops_data.csv -> crops_data.ttl
├── ingest_rag.py                # Script cắt đoạn, nhúng embedding và nạp tài liệu vào ChromaDB & Cache
├── add_document.py              # Script nạp bổ sung tài liệu mới vào VectorDB và BM25 Cache
├── sparql_client.py             # Client thực thi truy vấn SPARQL kết nối GraphDB
├── schema.py                    # Schema định nghĩa các Type và Query GraphQL (Strawberry)
├── main.py                      # FastAPI App chạy GraphQL Server tại endpoint /graphql
├── rag_retriever.py             # Module khởi tạo ChromaDB Vector Store & Semantic Search
├── hybrid_retriever.py          # Module kết hợp BM25 + Vector Search (EnsembleRetriever)
├── tools.py                     # Định nghĩa LangChain Tools cho Agent (GraphQL & RAG)
├── agent.py                     # Cấu hình AI Agent với Google Gemini và Prompt chuyên sâu
├── app.py                       # Giao diện người dùng Streamlit
├── api-key.env                  # File cấu hình mẫu biến môi trường API Key
└── README.md                    # Tài liệu hướng dẫn dự án
```

---

## ⚙️ 5. Yêu cầu môi trường (Prerequisites)

1. **Hệ điều hành**: Windows 10/11, macOS, hoặc Linux.
2. **Python**: Phiên bản `3.10` hoặc `3.11` (khuyến nghị).
3. **Java**: JDK 11 trở lên (yêu cầu để chạy Ontotext GraphDB).
4. **GraphDB**: Phiên bản [Ontotext GraphDB Free/SE](https://graphdb.ontotext.com/) cài đặt trên máy hoặc chạy qua Docker.
5. **Google Gemini API Key**: Lấy khóa API miễn phí hoặc trả phí tại [Google AI Studio](https://aistudio.google.com/).

---

## 🚀 6. Hướng dẫn cài đặt & Khởi chạy (Installation & Setup)

### Bước 1: Chuẩn bị mã nguồn và môi trường ảo

Mở terminal/PowerShell tại thư mục dự án:

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Trên Windows (CMD):
.\venv\Scripts\activate.bat
# Trên Linux/macOS:
source venv/bin/activate
```

### Bước 2: Cài đặt các thư viện phụ thuộc

Cài đặt các gói cần thiết bằng lệnh:

```bash
pip install fastapi uvicorn strawberry-graphql streamlit langchain langchain-classic langchain-community langchain-core langchain-google-genai langchain-text-splitters google-generativeai gql[requests] SPARQLWrapper rdflib chromadb sentence-transformers transformers rank_bm25 python-dotenv
```

### Bước 3: Cấu hình biến môi trường

Tạo file `.env` tại thư mục gốc của dự án (hoặc sử dụng `api-key.env`) với nội dung:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### Bước 4: Thiết lập Đồ thị tri thức (GraphDB)

1. **Khởi chạy GraphDB**: Mở GraphDB Workbench trên trình duyệt tại `http://localhost:7200`.
2. **Tạo Repository**:
   - Vào menu **Setup** -> **Repositories** -> **Create new repository**.
   - Chọn kiểu **GraphDB Free**.
   - Đặt `Repository ID` là: `Farming` (đúng tên cấu hình trong `sparql_client.py`).
   - Nhấn **Create**.
3. **Sinh dữ liệu RDF Triples (nếu cập nhật CSV)**:
   ```bash
   python csv_to_rdf.py
   ```
4. **Import dữ liệu vào GraphDB**:
   - Trong GraphDB Workbench, chọn repository `Farming` ở góc phải trên.
   - Vào **Import** -> **User data** -> **Upload RDF files**.
   - Upload và import 2 file:
     - `agri-ontology.ttl` (Cấu trúc Ontology)
     - `crops_data.ttl` (Dữ liệu thực thể các loại cây trồng)

### Bước 5: Nạp dữ liệu vào Vector DB và sinh Cache BM25

Chạy script nạp toàn bộ tài liệu từ thư mục `docs/`:

```bash
python ingest_rag.py
```
> Kết quả thành công sẽ tạo thư mục `chroma_db/` và file `chunks_cache.pkl`.

### Bước 6: Khởi chạy GraphQL Backend Server

Mở một cửa sổ terminal riêng và chạy:

```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```
- Endpoint GraphQL sẽ hoạt động tại: `http://localhost:8001/graphql`
- Giao diện kiểm thử truy vấn GraphQL: `http://localhost:8001/graphql` (GraphiQL UI)

### Bước 7: Khởi chạy Giao diện Trợ lý (Streamlit App)

Mở một cửa sổ terminal khác và chạy:

```bash
streamlit run app.py
```
- Giao diện Web sẽ tự động mở trên trình duyệt tại: `http://localhost:8501`

---

## 🔑 7. Biến môi trường & Cấu hình (.env)

| Biến môi trường / Cấu hình | File cấu hình | Giá trị mặc định | Mô tả |
| :--- | :--- | :--- | :--- |
| `GOOGLE_API_KEY` | `.env` hoặc `api-key.env` | `AQ.Ab8RN...` | API Key xác thực với Google Gemini |
| `GRAPHDB_ENDPOINT` | `sparql_client.py` | `http://localhost:7200/repositories/Farming` | Đường dẫn SPARQL endpoint của GraphDB |
| `GRAPHQL_URL` | `tools.py` | `http://localhost:8001/graphql` | Đường dẫn kết nối đến GraphQL API |
| `EMBEDDING_MODEL` | `rag_retriever.py`, `ingest_rag.py` | `bkai-foundation-models/vietnamese-bi-encoder` | Mô hình ngôn ngữ tạo vector nhúng tiếng Việt |
| `LLM_MODEL` | `agent.py` | `gemini-3.6-flash` | Mô hình LLM phục vụ suy luận Agent |

---

## 💡 8. Hướng dẫn sử dụng & Các kịch bản câu hỏi

### Các dạng câu hỏi mẫu trên Chatbot

1. **Tra cứu dữ liệu có cấu trúc (Knowledge Graph)**:
   - *"Cây cà chua có những giai đoạn sinh trưởng nào và kéo dài bao lâu?"*
   - *"Bắp cải thường mắc những loại bệnh nào?"*
   - *"Thời gian thu hoạch của cà rốt là bao nhiêu ngày?"*
2. **Tra cứu hướng dẫn kỹ thuật canh tác (RAG - Hybrid Search)**:
   - *"Cách bón phân và chăm sóc cà chua trong giai đoạn ra hoa như thế nào?"*
   - *"Làm thế nào để phòng trừ bệnh thối nhũn trên bắp cải hiệu quả?"*
   - *"Kỹ thuật ngâm ủ và gieo hạt dưa leo ra sao?"*
3. **Câu hỏi phối hợp (Multi-tool Reasoning)**:
   - *"Cây rau muống phát triển qua các giai đoạn nào và kỹ thuật tưới nước ở giai đoạn thân lá cần chú ý gì?"*

---

## 🛠️ 9. Các lệnh quản trị & tiện ích (Useful Commands)

- **Cập nhật dữ liệu RDF từ file CSV**:
  ```bash
  python csv_to_rdf.py
  ```
- **Nạp lại toàn bộ kho tài liệu RAG**:
  ```bash
  python ingest_rag.py
  ```
- **Nạp thêm 1 file tài liệu mới vào hệ thống (không cần nạp lại từ đầu)**:
  ```bash
  # Đặt file tài liệu vào docs/ và chỉ định đường dẫn trong add_document.py
  python add_document.py
  ```
- **Kiểm tra truy vấn GraphQL mẫu (tại `http://localhost:8001/graphql`)**:
  ```graphql
  query {
    crop(name: "Cà chua") {
      growthStages {
        name
        durationDays
      }
      diseases {
        name
      }
    }
  }
  ```

---

## 📜 10. Giấy phép & Đóng góp (License & Contribution)

Dự án phục vụ mục đích nghiên cứu, học tập và ứng dụng thực tế trong lĩnh vực Nông nghiệp số. Mọi đóng góp (Pull Request, Issue) nhằm hoàn thiện Ontology và kho tài liệu kỹ thuật đều được hoan nghênh!
