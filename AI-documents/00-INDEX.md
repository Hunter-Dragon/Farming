# AI-documents — Tài liệu cho AI Agent

Thư mục này chứa toàn bộ ngữ cảnh cần thiết để bất kỳ AI agent nào (Claude,
GPT, Gemini CLI, v.v.) mở project này lần đầu cũng hiểu được: project làm gì,
kiến trúc ra sao, chạy thế nào, dữ liệu/ontology có cấu trúc gì, từng file mã
nguồn dùng để làm gì, và trạng thái công việc hiện tại (viết bài báo khoa
học). Đọc theo thứ tự dưới đây nếu là lần đầu tiếp cận project.

1. [01-overview.md](01-overview.md) — Project là gì, mục tiêu, bài toán giải quyết.
2. [02-architecture.md](02-architecture.md) — Kiến trúc hệ thống, luồng dữ liệu, tech stack.
3. [03-setup-and-run.md](03-setup-and-run.md) — Cài đặt môi trường và chạy hệ thống.
4. [04-data-and-ontology.md](04-data-and-ontology.md) — Ontology (OWL/RDF), schema CSV, cách sinh RDF.
5. [05-codebase-reference.md](05-codebase-reference.md) — Mô tả từng file mã nguồn trong repo.
6. [06-evaluation-pipeline.md](06-evaluation-pipeline.md) — Bộ script đánh giá thực nghiệm (`eval/`).
7. [07-research-paper-context.md](07-research-paper-context.md) — Bối cảnh viết bài báo khoa học, mẫu tham khảo, trạng thái hiện tại.

## Quy ước

- Toàn bộ code, biến, danh pháp trong repo dùng tiếng Việt cho domain
  (tên cây trồng, bệnh, giai đoạn sinh trưởng...) nhưng code/comment kỹ
  thuật đa phần viết bằng tiếng Việt có dấu trong docstring, English cho
  tên hàm/biến/class theo chuẩn Python thông thường.
- Repo không có test tự động (`pytest` etc.) — kiểm thử chức năng qua
  chạy thủ công hoặc qua bộ `eval/` (xem file 06).
- Các file này là tài liệu tĩnh, viết tại một thời điểm — khi code trong
  repo thay đổi (thêm tool, đổi schema, đổi endpoint...), **phải cập nhật
  lại các file trong AI-documents/ tương ứng**, đừng để lệch pha với code
  thật.
