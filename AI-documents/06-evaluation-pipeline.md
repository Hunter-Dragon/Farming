# 06. Pipeline đánh giá thực nghiệm (`eval/`)

Hệ thống này là dạng **chatbot/RAG**, không có "thực nghiệm" kiểu benchmark
tốc độ/tải thông thường — thực nghiệm ở đây nghĩa là đo **chất lượng truy
xuất và câu trả lời** trên một bộ câu hỏi có ground truth, phục vụ phần
Kết quả (Results/Evaluation) của bài báo khoa học. Chi tiết vận hành đầy
đủ nằm ở [eval/README.md](../eval/README.md) — file này chỉ tóm tắt lý do
thiết kế và cách đọc kết quả.

## Vì sao thiết kế theo hướng này

- Không thể "unit test" một câu trả lời tự nhiên ngôn ngữ theo kiểu
  assertEqual — nên dùng kết hợp 2 cách chấm:
  1. **Chấm tự động bằng so khớp chuỗi (string-match) với ground truth**
     cho câu hỏi Knowledge Graph (dữ liệu định lượng, chính xác tuyệt đối
     nên so khớp được) → Recall.
  2. **LLM-as-judge** (gọi lại Gemini để chấm điểm 1-5 theo accuracy/
     completeness/groundedness) cho câu hỏi RAG/multi-tool (câu trả lời tự
     nhiên ngôn ngữ, không so khớp chuỗi trực tiếp được).
- Có thêm **ablation study** (so sánh Hybrid vs BM25-only vs Vector-only)
  vì đây là điểm thiết kế đáng chứng minh nhất của hệ thống (giả thuyết:
  hybrid tốt hơn từng phương pháp đơn lẻ) — phần này thường là một bảng số
  liệu quan trọng trong bài báo dạng "ontology-enhanced RAG".

## Bộ câu hỏi (`eval/questions.json`)

24 câu, chia đều cho 6 loại cây **có cả dữ liệu KG (trong `crops_data.csv`)
lẫn tài liệu RAG (trong `docs/*.txt`)**: Cà chua, Bắp cải, Cà rốt, Dưa leo,
Rau muống, Su hào — chọn 6 cây này vì chỉ chúng mới đánh giá được cả 2 tool
+ multi-tool một cách công bằng (190 loại cây khác trong CSV không có tài
liệu kỹ thuật tương ứng, không dùng được cho câu hỏi RAG).

- 12 câu `kg` (giai đoạn sinh trưởng + bệnh, 2 câu/cây).
- 6 câu `rag` (1 câu kỹ thuật canh tác/cây, ground truth là "key points"
  trích tay từ đoạn văn gốc trong `docs/`).
- 6 câu `multi` (cần cả 2 tool, ground truth giống câu `kg`).

## Quy trình chạy (tóm tắt, xem eval/README.md để có lệnh đầy đủ)

```
python eval/run_eval.py                 # chạy Agent qua 24 câu → results_raw.json
python eval/score_answers.py            # chấm điểm → scored_results.json (+ in tóm tắt)
python eval/ablation_run.py             # ablation 3 cấu hình trọng số → results_ablation_*.json
python eval/score_answers.py --results eval/results_ablation_<config>.json \
       --output eval/scored_ablation_<config>.json   # chấm từng config
python eval/compare_ablation.py         # bảng so sánh 3 cấu hình
```

Yêu cầu môi trường chạy đầy đủ hệ thống thật (GraphDB + GraphQL server +
Chroma đã ingest + `GOOGLE_API_KEY` hợp lệ) — **không chạy được trên máy
chỉ dùng để soạn bài báo**, phải chạy trên máy có đủ công cụ rồi gửi lại
các file JSON kết quả.

## Cách đọc file kết quả cho phần viết bài báo

- `eval/scored_results.json`: mỗi entry có `kg_score.recall` (0-1, chỉ câu
  `kg`/`multi`), `keypoint_recall.recall` (0-1, proxy rẻ tiền, chỉ câu
  `rag`/`multi`), `llm_judge.{accuracy,completeness,groundedness}` (thang
  1-5, chỉ câu `rag`/`multi`, nếu không chạy `--skip-llm-judge`),
  `latency_sec`, `tools_called`.
- Số liệu tổng hợp (trung bình từng metric) được `score_answers.py` in ra
  console ngay sau khi chạy — copy trực tiếp phần "=== TOM TAT ===" vào
  bản nháp phần Kết quả.
- `eval/compare_ablation.py` in bảng 3 dòng (hybrid/bm25_only/vector_only)
  × các cột metric — dùng làm bảng ablation trong bài báo.

## Giới hạn cần nói rõ trong bài báo (tránh phóng đại kết quả)

- Bộ câu hỏi 24 câu là **quy mô nhỏ, tự soạn**, không phải benchmark chuẩn
  hoá công khai — phù hợp để minh hoạ tính khả thi (proof-of-concept),
  không nên diễn giải số liệu như một benchmark có ý nghĩa thống kê mạnh.
- `keypoint_recall` là so khớp chuỗi con thô (rough substring match), có
  thể cho false negative cao nếu Agent diễn đạt lại (paraphrase) thay vì
  lặp nguyên văn — chỉ dùng để so sánh tương đối giữa các cấu hình ablation
  chạy trên cùng bộ câu hỏi, không nên trích dẫn như một con số tuyệt đối
  đáng tin cậy.
- LLM-as-judge dùng cùng họ model (Gemini) với model tạo câu trả lời — có
  rủi ro thiên vị (self-preference bias) đã biết trong nghiên cứu LLM-judge
  nói chung; nếu bài báo cần độ tin cậy cao hơn, nên bổ sung một vòng chấm
  tay (human eval) trên một mẫu con để đối chiếu (xem gợi ý cuối
  `eval/README.md`).
