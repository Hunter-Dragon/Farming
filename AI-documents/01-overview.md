# 01. Tổng quan Project

## Tên project

**Trợ lý AI Nông nghiệp Rau củ (Agri AI Assistant)** — thư mục gốc: `Farming/`.

## Bài toán

Người làm nông nghiệp / kỹ sư nông học / người trồng trọt cần tra cứu nhanh
thông tin canh tác rau củ (giai đoạn sinh trưởng, sâu bệnh, kỹ thuật chăm
sóc chi tiết) nhưng thông tin thường nằm rải rác: một phần là dữ liệu có
cấu trúc rõ ràng (bảng: cây nào, giai đoạn nào, kéo dài bao lâu, dễ mắc
bệnh gì), một phần là hướng dẫn kỹ thuật dạng văn bản dài, khó tra cứu
nhanh bằng từ khóa đơn thuần.

## Giải pháp

Một chatbot hỏi-đáp (Streamlit UI) chạy trên nền **LLM Agent** (Google
Gemini + LangChain Tool-Calling), có 2 "công cụ" (tools) để tự quyết định
gọi khi cần:

1. **Knowledge Graph (KG) tool** — truy vấn dữ liệu có cấu trúc (ontology
   nông nghiệp trên GraphDB, qua SPARQL, expose ra ngoài qua GraphQL API).
   Dùng khi câu hỏi cần dữ kiện chính xác: "Cà chua có mấy giai đoạn sinh
   trưởng?", "Bắp cải hay mắc bệnh gì?".
2. **Hybrid RAG tool** — tìm kiếm lai (Vector Search + BM25) trên kho tài
   liệu kỹ thuật canh tác (`docs/*.txt`). Dùng khi câu hỏi cần giải thích,
   hướng dẫn quy trình: "Cách bón phân cho cà chua khi ra hoa?".

Agent tự suy luận nên gọi tool nào (hoặc cả hai), rồi tổng hợp câu trả lời
**chỉ dựa trên dữ liệu tool trả về** (được ràng buộc trong system prompt),
nhằm hạn chế hallucination.

## Ý tưởng cốt lõi mang tính đóng góp (đáng đưa vào bài báo)

- **Ontology-enhanced RAG**: kết hợp semantic knowledge graph (độ chính xác
  cao, dữ liệu định lượng) với retrieval phi cấu trúc (độ phủ ngữ nghĩa
  cao, giải thích chi tiết) trong cùng một agent, thay vì chỉ dùng RAG
  thuần túy.
- **Hybrid Retrieval tối ưu cho tiếng Việt**: BM25 (lexical) + Vector
  Search với embedding tiếng Việt chuyên biệt
  (`bkai-foundation-models/vietnamese-bi-encoder`), trọng số mặc định
  0.4 (BM25) / 0.6 (Semantic).
- **Multi-tool reasoning**: agent tự quyết định phối hợp cả hai nguồn khi
  câu hỏi cần cả dữ kiện lẫn giải thích quy trình.

## Trạng thái hiện tại của công việc

Chủ project (không phải người viết code gốc — được bạn nhờ) đang muốn viết
một **bài báo khoa học** dựa trên project này, theo mẫu cấu trúc của một
bài báo có sẵn trong `bài báo mẫu/` (chủ đề tương tự: Ontology-enhanced RAG
cho hệ thống tư vấn — xem file 07). Máy đang dùng để viết bài báo **không
có sẵn công cụ để chạy được hệ thống** (không có GraphDB, không chắc có
GPU/model embedding sẵn sàng...) — do đó phần thực nghiệm (chạy Agent,
thu thập số liệu) được thiết kế để **một máy khác** (của người bạn) chạy
sau khi code được push lên git. Xem file 06 để biết chi tiết pipeline này.
