# Hướng dẫn chạy Đánh giá Thực nghiệm (Evaluation)

Bộ script trong `eval/` dùng để đo chất lượng của Agent (GraphQL Knowledge Graph +
Hybrid RAG) trên một bộ câu hỏi kiểm thử có sẵn đáp án tham chiếu, phục vụ phần
Thực nghiệm/Kết quả của bài báo.

## 0. Yêu cầu trước khi chạy

Hệ thống chính phải chạy được như README.md gốc mô tả:

1. GraphDB đang chạy, repository `Farming` đã import `agri-ontology.ttl` + `crops_data.ttl`.
2. GraphQL server đang chạy: `uvicorn main:app --host 0.0.0.0 --port 8001`
3. Đã ingest dữ liệu RAG: `chroma_db/` và `chunks_cache.pkl` tồn tại (chạy `python ingest_rag.py` nếu chưa).
4. `GOOGLE_API_KEY` hợp lệ trong file `.env` ở thư mục gốc project.
   **File `.env` không nằm trong git** (bị `.gitignore` loại vì là secret) —
   sau khi `git pull`/`git clone` sẽ **không thấy file này**, phải tự tạo
   mới:
   ```env
   GOOGLE_API_KEY=your_actual_gemini_api_key_here
   ```
   Lấy key tại https://aistudio.google.com/ — không dùng lại key demo cũ
   từng thấy trong `api-key.env` (file đó cũng đã bị gỡ khỏi git, chỉ để
   tham khảo định dạng, không phải key dùng được).
5. Cài thêm (nếu chưa có): không cần thư viện gì thêm ngoài `requirements.txt` gốc.

Chạy toàn bộ lệnh dưới đây **từ thư mục gốc project** (`Farming/`), không phải từ trong `eval/`.

## 1. Bộ câu hỏi đánh giá

File `eval/questions.json` đã có sẵn 24 câu hỏi (không cần sinh lại), chia làm:
- 12 câu **kg**: tra cứu Knowledge Graph (giai đoạn sinh trưởng, bệnh) — có ground truth lấy trực tiếp từ `crops_data.csv`.
- 6 câu **rag**: hỏi kỹ thuật canh tác — có ground truth (key points) trích tay từ `docs/*.txt`.
- 6 câu **multi**: câu hỏi cần cả 2 nguồn.

Chỉ cần sinh lại nếu `crops_data.csv` hoặc `docs/*.txt` thay đổi:
```bash
python eval/build_questions.py
```

## 2. Chạy Agent qua toàn bộ câu hỏi

```bash
python eval/run_eval.py
```
- Kết quả ghi ra `eval/results_raw.json` (câu trả lời, tool đã gọi, latency).
- Test nhanh vài câu trước khi chạy full: `python eval/run_eval.py --limit 3`
- Mỗi câu gọi ít nhất 1 lần Gemini API, cách nhau 1 giây (`--sleep 1.0`) để tránh rate-limit — có thể chỉnh `--sleep` nếu cần.
- Nếu 1 câu bị lỗi (vd GraphDB timeout), script vẫn tiếp tục và ghi lại lỗi vào record đó thay vì dừng cả quá trình.

## 3. Chấm điểm

```bash
python eval/score_answers.py
```
- Câu loại `kg`: chấm tự động (so khớp chuỗi ground truth trong câu trả lời) → Recall.
- Câu loại `rag`/`multi`: gọi lại Gemini làm **LLM-as-judge**, chấm điểm 1-5 theo 3 tiêu chí (accuracy, completeness, groundedness). Tốn thêm ~1 API call/câu.
- Nếu muốn bỏ qua bước LLM-judge (đỡ tốn API call, chỉ lấy số liệu KG): `python eval/score_answers.py --skip-llm-judge`
- Kết quả chi tiết: `eval/scored_results.json`. Script cũng in ra bảng tóm tắt (recall trung bình, điểm LLM-judge trung bình, latency trung bình) — **số liệu này dùng trực tiếp cho phần Kết quả thực nghiệm trong bài báo**.

## 4. Ablation Study (so sánh Hybrid vs BM25-only vs Vector-only)

Đây là phần thực nghiệm chứng minh giá trị thiết kế Hybrid Retrieval — nên có trong bài báo.

```bash
python eval/ablation_run.py
```
Chạy lại các câu hỏi `rag` + `multi` với 3 cấu hình trọng số khác nhau (câu hỏi `kg`
không đi qua Hybrid Retriever nên bỏ qua), ghi ra 3 file:
`eval/results_ablation_hybrid.json`, `results_ablation_bm25_only.json`, `results_ablation_vector_only.json`.

Sau đó chấm điểm từng file:
```bash
python eval/score_answers.py --results eval/results_ablation_hybrid.json --output eval/scored_ablation_hybrid.json
python eval/score_answers.py --results eval/results_ablation_bm25_only.json --output eval/scored_ablation_bm25_only.json
python eval/score_answers.py --results eval/results_ablation_vector_only.json --output eval/scored_ablation_vector_only.json
```

Rồi in bảng so sánh:
```bash
python eval/compare_ablation.py
```

## 5. Kết quả cần gửi lại

Sau khi chạy xong, gửi lại các file sau (không cần gửi lại code, chỉ cần output):
- `eval/results_raw.json`, `eval/scored_results.json`
- `eval/results_ablation_*.json`, `eval/scored_ablation_*.json`
- Ảnh chụp màn hình phần "TOM TAT" in ra ở bước 3 và output của `compare_ablation.py`

## Lưu ý

- `keypoint_recall` trong kết quả chấm điểm câu `rag`/`multi` là proxy metric rẻ tiền
  (so khớp chuỗi thô, không cần gọi API) — chỉ dùng để so sánh nhanh giữa các cấu hình
  ablation, **không thay thế** điểm LLM-judge khi báo cáo số liệu chính trong bài báo.
- Nếu muốn kết quả LLM-judge đáng tin cậy hơn cho bài báo, có thể cho người khác
  (không phải máy đã sinh câu trả lời) chấm tay lại một phần mẫu và so sánh với LLM-judge
  (inter-rater agreement) — làm nếu có thời gian, không bắt buộc.
