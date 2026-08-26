# 07. Bối cảnh viết bài báo khoa học

## Ai đang làm gì

Chủ project hiện tại (email `afc.it.dev@asiafoods.vn`) **không phải người
viết code gốc** của repo này — code được một người bạn đưa/nhờ, và chủ
project đang dùng project này làm cơ sở để viết một bài báo khoa học. Máy
đang thao tác (nơi các file AI-documents/ và eval/ này được tạo) **không
cài đặt được GraphDB/toàn bộ hệ thống** — chỉ dùng để đọc code, soạn văn
bản, và soạn sẵn script đánh giá. Việc **chạy thực tế** (thu số liệu thực
nghiệm) sẽ do người bạn thực hiện trên máy khác, sau khi code được `git
push` lên và người bạn `git pull` về.

## File mẫu tham khảo

`bài báo mẫu/2026_Ontology-enhanced RAG for a personalised and sustainable
food advisory system.pdf` — bài báo có chủ đề rất sát với project này
(Ontology-enhanced RAG cho hệ thống tư vấn), dùng làm khuôn mẫu về **cấu
trúc/bố cục** (các mục: Abstract, Introduction, Related Work, Methodology,
Experiments/Evaluation, Results, Discussion, Conclusion...) và văn phong
học thuật.

> Lưu ý kỹ thuật: công cụ đọc PDF theo trang (`pdftoppm`) không có sẵn trên
> máy này (thiếu `poppler-utils`), nên trước đây chỉ đọc được phần text
> layer của vài trang đầu, chưa đọc hết toàn văn. **Trước khi viết outline
> chi tiết bám sát 100% cấu trúc file mẫu, cần đọc lại toàn văn PDF này**
> (thử cách khác: trích xuất text trực tiếp bằng thư viện Python như
> `pypdf`/`pdfplumber` thay vì render ảnh từng trang, vì mục tiêu chỉ là
> lấy text, không cần hình ảnh).

## Quy trình đã thống nhất với người dùng

1. AI (trên máy này) soạn: bộ câu hỏi đánh giá + script chạy/chấm điểm
   (đã xong, nằm trong `eval/`), cộng với các file mô tả kiến trúc/dữ liệu
   (đang làm, `AI-documents/`).
2. Người dùng `git push` code lên remote.
3. Người bạn `git pull`, cài đặt đầy đủ (GraphDB, dependencies, API key),
   chạy theo `eval/README.md`, rồi gửi lại các file kết quả JSON
   (`eval/results_raw.json`, `eval/scored_results.json`,
   `eval/results_ablation_*.json`, `eval/scored_ablation_*.json`).
4. AI dùng các file kết quả đó để viết phần Kết quả thực nghiệm của bài
   báo, dựa trên số liệu thật (không được tự bịa số liệu thực nghiệm).

## Trạng thái tại thời điểm viết các file AI-documents/ này (2026-08-25)

- Đã xong: bộ câu hỏi đánh giá (`eval/questions.json`, 24 câu), toàn bộ
  script chạy/chấm điểm/ablation trong `eval/`, sửa `hybrid_retriever.py`
  để hỗ trợ trọng số qua env var.
- Chưa xong: chưa có kết quả thực nghiệm thật nào (chưa chạy trên máy
  người bạn) — mọi phần "Kết quả" của bài báo hiện vẫn đang chờ dữ liệu.
- Chưa bắt đầu: soạn nội dung văn bản của bài báo (Abstract, Introduction,
  Related Work, Methodology...) — có thể bắt đầu song song phần
  Introduction/Methodology (không phụ thuộc số liệu thực nghiệm) trong khi
  chờ kết quả từ `eval/`.

## Việc cần làm tiếp theo (gợi ý cho phiên làm việc kế tiếp)

1. Đọc lại toàn văn PDF mẫu bằng cách trích text trực tiếp (không qua
   render ảnh) để nắm đúng cấu trúc mục/heading thật của bài mẫu.
2. Soạn outline bài báo cho project này, ánh xạ từng mục của bài mẫu sang
   nội dung tương ứng của project (dùng file 01, 02, 04 trong thư mục này
   làm nguồn cho phần Introduction/System Architecture/Methodology).
3. Viết trước các phần không phụ thuộc số liệu thực nghiệm (Introduction,
   Related Work, Methodology/Architecture).
4. Khi có file kết quả từ `eval/` gửi về, viết phần Results/Discussion dựa
   trên số liệu thật, đối chiếu với giới hạn đã nêu ở file 06.
