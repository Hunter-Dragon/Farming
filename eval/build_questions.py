# eval/build_questions.py
"""Sinh bo cau hoi danh gia (eval/questions.json) tu crops_data.csv va docs/*.txt.

Chi dung du lieu tinh (khong can GraphDB / Chroma / API key) nen co the chay
o may khong co day du cong cu, chi de tao lai file questions.json neu can
cap nhat sau khi crops_data.csv hoac docs/ thay doi.

Chay: python eval/build_questions.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "crops_data.csv"
OUT_PATH = Path(__file__).resolve().parent / "questions.json"

# 6 loai cay co ca du lieu KG (crops_data.csv) lan tai lieu ky thuat (docs/*.txt)
# nen dung duoc cho ca cau hoi KG, RAG va multi-tool.
TARGET_CROPS = ["Cà chua", "Bắp cải", "Cà rốt", "Dưa leo", "Rau muống", "Su hào"]

# Ground truth cho cau hoi RAG duoc trich tay tu docs/*.txt (xem file tuong ung
# trong docs/ de doi chieu). Moi muc la 1-2 y chinh ma cau tra loi dung phai co.
RAG_GROUND_TRUTH = {
    "Cà chua": {
        "question": "Cách bón phân và chăm sóc cà chua trong giai đoạn ra hoa như thế nào?",
        "key_points": [
            "bón thêm phân kali để tăng tỷ lệ đậu quả",
            "hạn chế bón đạm quá nhiều vì dễ khiến cây phát triển thân lá mà ít ra hoa",
            "làm giàn hoặc cắm cọc chống đổ",
        ],
    },
    "Bắp cải": {
        "question": "Làm thế nào để phòng trừ bệnh thối nhũn trên bắp cải hiệu quả?",
        "key_points": [
            "đảm bảo hệ thống thoát nước tốt",
            "tránh tưới quá đẫm",
            "luân canh với cây khác họ",
        ],
    },
    "Cà rốt": {
        "question": "Vì sao không nên bón phân chuồng tươi trực tiếp khi trồng cà rốt?",
        "key_points": [
            "dễ làm củ bị phân nhánh",
            "nên dùng phân chuồng đã hoai mục hoàn toàn",
        ],
    },
    "Dưa leo": {
        "question": "Kỹ thuật làm giàn cho dưa leo cần lưu ý gì?",
        "key_points": [
            "làm giàn hoặc cắm cọc ngay khi cây con có 2-3 lá thật",
            "nếu để bò trên đất quả dễ bị cong vẹo, tiếp xúc đất gây thối",
        ],
    },
    "Rau muống": {
        "question": "Rau muống cần được bón phân và tưới nước như thế nào để đạt năng suất cao?",
        "key_points": [
            "bón phân đạm định kỳ 7-10 ngày một lần",
            "tưới nước 2 lần mỗi ngày vào sáng sớm và chiều mát",
        ],
    },
    "Su hào": {
        "question": "Dấu hiệu nào cho biết su hào đã đến độ thu hoạch?",
        "key_points": [
            "củ đạt đường kính khoảng 8-10cm",
            "vỏ củ căng bóng",
        ],
    },
}

MULTI_TOOL_QUESTIONS = {
    "Cà chua": "Cây cà chua có những giai đoạn sinh trưởng nào, và ở giai đoạn ra hoa cần chăm sóc như thế nào để tăng tỷ lệ đậu quả?",
    "Bắp cải": "Bắp cải thường mắc bệnh gì, và cách phòng trừ bệnh đó ra sao?",
    "Cà rốt": "Cà rốt hay bị bệnh gì, và cần chú ý gì về đất trồng để hạn chế bệnh đó?",
    "Dưa leo": "Dưa leo có những giai đoạn sinh trưởng nào, và giai đoạn ra hoa cần chăm sóc gì đặc biệt?",
    "Rau muống": "Rau muống có những giai đoạn sinh trưởng nào, và cần tưới nước ra sao ở giai đoạn thân lá?",
    "Su hào": "Su hào thường gặp sâu bệnh gì, và cần làm gì để phòng trừ trong giai đoạn cây con?",
}


def load_crop_rows():
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    by_crop = {}
    for row in rows:
        by_crop.setdefault(row["crop_name"], []).append(row)
    return by_crop


def build():
    by_crop = load_crop_rows()
    questions = []
    qid = 1

    for crop in TARGET_CROPS:
        rows = by_crop.get(crop, [])
        if not rows:
            continue

        stages = [{"name": r["growth_stage"], "duration_days": int(r["stage_duration"])} for r in rows]
        diseases = sorted({r["disease"] for r in rows})

        # 1) Cau hoi KG - giai doan sinh truong
        questions.append({
            "id": f"kg-{qid:03d}",
            "category": "kg",
            "crop": crop,
            "expected_tool": "query_crop_knowledge_graph",
            "question": f"Cây {crop} có những giai đoạn sinh trưởng nào và kéo dài bao lâu?",
            "ground_truth": {"growth_stages": stages},
        })
        qid += 1

        # 2) Cau hoi KG - benh
        questions.append({
            "id": f"kg-{qid:03d}",
            "category": "kg",
            "crop": crop,
            "expected_tool": "query_crop_knowledge_graph",
            "question": f"{crop} thường mắc những loại bệnh nào?",
            "ground_truth": {"diseases": diseases},
        })
        qid += 1

        # 3) Cau hoi RAG
        rag = RAG_GROUND_TRUTH[crop]
        questions.append({
            "id": f"rag-{qid:03d}",
            "category": "rag",
            "crop": crop,
            "expected_tool": "search_agriculture_documents",
            "question": rag["question"],
            "ground_truth": {"key_points": rag["key_points"], "source_doc": f"docs/ky-thuat-{_slug(crop)}.txt"},
        })
        qid += 1

        # 4) Cau hoi multi-tool
        questions.append({
            "id": f"multi-{qid:03d}",
            "category": "multi",
            "crop": crop,
            "expected_tool": "both",
            "question": MULTI_TOOL_QUESTIONS[crop],
            "ground_truth": {
                "growth_stages": stages,
                "diseases": diseases,
            },
        })
        qid += 1

    OUT_PATH.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Da sinh {len(questions)} cau hoi -> {OUT_PATH}")


def _slug(crop):
    mapping = {
        "Cà chua": "ca-chua",
        "Bắp cải": "bap-cai",
        "Cà rốt": "ca-rot",
        "Dưa leo": "dua-leo",
        "Rau muống": "rau-muong",
        "Su hào": "su-hao",
    }
    return mapping[crop]


if __name__ == "__main__":
    build()
