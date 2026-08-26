# eval/score_answers.py
"""Cham diem ket qua trong eval/results_raw.json (sinh boi run_eval.py).

Cau hoi loai "kg": cham tu dong bang cach kiem tra cau tra loi co chua dung
  cac gia tri ground truth (ten giai doan, so ngay, ten benh) hay khong
  -> tinh Precision / Recall / F1 tren tap "field" ky vong xuat hien.

Cau hoi loai "rag" va "multi": dung LLM-as-judge (goi lai Gemini/Claude) de cham
  diem 1-5 theo 3 tieu chi: do chinh xac, do day du, co can cu (khong bia).
  Can GOOGLE_API_KEY hop le. Neu muon bo qua buoc nay (vi du chi can so lieu
  KG truoc), dung --skip-llm-judge.

Chay tu thu muc goc project:
  python eval/score_answers.py
  python eval/score_answers.py --skip-llm-judge
"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

load_dotenv()
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFC", text)
    return text


def score_kg(record, ground_truth):
    """Kiem tra tung field ground truth (ten giai doan/benh, so ngay) co
    xuat hien trong cau tra loi khong. Tra ve (matched, total, missing)."""
    answer = normalize(record.get("answer") or "")
    expected_fields = []

    if "growth_stages" in ground_truth:
        for stage in ground_truth["growth_stages"]:
            expected_fields.append(stage["name"])
            expected_fields.append(str(stage["duration_days"]))
    if "diseases" in ground_truth:
        expected_fields.extend(ground_truth["diseases"])

    matched, missing = [], []
    for field in expected_fields:
        if normalize(field) in answer:
            matched.append(field)
        else:
            missing.append(field)

    total = len(expected_fields)
    recall = len(matched) / total if total else None
    return {
        "matched": matched,
        "missing": missing,
        "total_expected": total,
        "recall": round(recall, 3) if recall is not None else None,
    }


def score_keypoints(record, ground_truth):
    """Kiem tra tung 'key_point' (cau tom tat y chinh, viet tay tu docs/*.txt)
    co xuat hien (dang gan dung, theo tu khoa) trong cau tra loi khong.
    Day la proxy metric re tien, khong thay the LLM-judge nhung dung tot
    de so sanh nhanh giua cac cau hinh ablation (khong ton API call)."""
    answer = normalize(record.get("answer") or "")
    key_points = ground_truth.get("key_points", [])
    matched, missing = [], []
    for point in key_points:
        # so khop tho: cat point thanh cum tu 4-6 ky tu dau de khoan dung
        # (khong doi hoi answer phai chua nguyen van ca cau)
        probe = normalize(point)[:40]
        if probe in answer:
            matched.append(point)
        else:
            missing.append(point)
    total = len(key_points)
    recall = len(matched) / total if total else None
    return {
        "matched": matched,
        "missing": missing,
        "total_expected": total,
        "recall": round(recall, 3) if recall is not None else None,
    }


LLM_JUDGE_PROMPT = """Ban la giam khao danh gia chat luong cau tra loi cua mot chatbot tu van nong nghiep.

Cau hoi: {question}

Cac y chinh PHAI co trong cau tra loi dung (ground truth, tom tat tu tai lieu ky thuat goc):
{key_points}

Cau tra loi cua chatbot can cham:
{answer}

Hay cham diem theo 3 tieu chi, moi tieu chi thang diem 1-5 (1=rat kem, 5=rat tot):
- accuracy: cau tra loi co dung, khong mau thuan voi cac y chinh o tren khong
- completeness: cau tra loi co bao quat du cac y chinh khong
- groundedness: cau tra loi co ve dua tren du lieu that (khong bia dat, khong noi chung chung vo nghia) khong

Chi tra ve JSON theo dung format sau, khong giai thich them:
{{"accuracy": <so 1-5>, "completeness": <so 1-5>, "groundedness": <so 1-5>, "note": "<1 cau ly do ngan>"}}
"""


def llm_judge(record, ground_truth, llm):
    key_points = "\n".join(f"- {p}" for p in ground_truth.get("key_points", []))
    if not key_points:
        # cau hoi multi-tool dung ground_truth dang growth_stages/diseases
        parts = []
        for stage in ground_truth.get("growth_stages", []):
            parts.append(f"- Giai doan {stage['name']}: {stage['duration_days']} ngay")
        for d in ground_truth.get("diseases", []):
            parts.append(f"- Benh: {d}")
        key_points = "\n".join(parts)

    prompt = LLM_JUDGE_PROMPT.format(
        question=record["question"],
        key_points=key_points,
        answer=record.get("answer") or "(khong co cau tra loi - agent bi loi)",
    )
    response = llm.invoke(prompt)
    text = response.content if hasattr(response, "content") else str(response)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {
            "accuracy": None,
            "completeness": None,
            "groundedness": None,
            "note": f"khong parse duoc: {text[:200]}",
        }
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {
            "accuracy": None,
            "completeness": None,
            "groundedness": None,
            "note": f"JSON loi: {text[:200]}",
        }


def run(
    results_path: Path,
    questions_path: Path,
    output_path: Path,
    skip_llm_judge: bool,
    sleep_sec: float,
):
    results = {
        r["id"]: r for r in json.loads(results_path.read_text(encoding="utf-8"))
    }
    questions = {
        q["id"]: q for q in json.loads(questions_path.read_text(encoding="utf-8"))
    }

    llm = None
    if not skip_llm_judge:
        load_dotenv("api-key.env")
        llm = ChatAnthropic(
            model="claude-haiku-4-5",
            temperature=0,
            api_key=os.getenv("GOOGLE_API_KEY"),
            base_url="https://chat.trollllm.xyz",
            default_headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                    " AppleWebKit/537.36"
                )
            },
        )

    scored = []
    for qid, record in results.items():
        q = questions.get(qid)
        if q is None:
            continue
        entry = {
            "id": qid,
            "category": q["category"],
            "crop": q["crop"],
            "question": q["question"],
        }

        if record.get("error"):
            entry["error"] = record["error"]
            scored.append(entry)
            continue

        if q["category"] == "kg":
            entry["kg_score"] = score_kg(record, q["ground_truth"])
        elif q["category"] in ("rag", "multi"):
            if q["category"] == "multi":
                entry["kg_score"] = score_kg(record, q["ground_truth"])
            if "key_points" in q["ground_truth"]:
                entry["keypoint_recall"] = score_keypoints(
                    record, q["ground_truth"]
                )
            if not skip_llm_judge:
                print(f"Cham LLM-judge: {qid}")
                entry["llm_judge"] = llm_judge(record, q["ground_truth"], llm)
                if sleep_sec:
                    time.sleep(sleep_sec)

        entry["latency_sec"] = record.get("latency_sec")
        entry["tools_called"] = record.get("tools_called")
        scored.append(entry)

    output_path.write_text(
        json.dumps(scored, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nDa cham diem {len(scored)} cau -> {output_path}")
    print_summary(scored)


def print_summary(scored):
    kg_recalls = [
        e["kg_score"]["recall"]
        for e in scored
        if "kg_score" in e and e["kg_score"]["recall"] is not None
    ]
    judged = [
        e["llm_judge"]
        for e in scored
        if "llm_judge" in e and e["llm_judge"].get("accuracy") is not None
    ]

    print("\n=== TOM TAT ===")
    if kg_recalls:
        print(
            f"KG recall trung binh: {sum(kg_recalls)/len(kg_recalls):.2%}"
            f" ({len(kg_recalls)} cau)"
        )
    if judged:
        for key in ("accuracy", "completeness", "groundedness"):
            vals = [j[key] for j in judged if j.get(key) is not None]
            if vals:
                print(
                    f"LLM-judge {key} trung binh:"
                    f" {sum(vals)/len(vals):.2f}/5 ({len(vals)} cau)"
                )
    latencies = [
        e["latency_sec"] for e in scored if e.get("latency_sec") is not None
    ]
    if latencies:
        print(
            f"Latency trung binh: {sum(latencies)/len(latencies):.2f}s"
            f" (min={min(latencies):.2f}s, max={max(latencies):.2f}s)"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results", default=str(Path(__file__).parent / "results_raw.json")
    )
    parser.add_argument(
        "--questions", default=str(Path(__file__).parent / "questions.json")
    )
    parser.add_argument(
        "--output", default=str(Path(__file__).parent / "scored_results.json")
    )
    parser.add_argument("--skip-llm-judge", action="store_true")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    run(
        Path(args.results),
        Path(args.questions),
        Path(args.output),
        args.skip_llm_judge,
        args.sleep,
    )