# eval/compare_ablation.py
"""In bang so sanh 3 cau hinh ablation sau khi da chay ablation_run.py va
score_answers.py cho tung file ket qua.

Chay:
  python eval/compare_ablation.py
"""
import json
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
CONFIGS = ["hybrid", "bm25_only", "vector_only"]


def summarize(scored_path: Path):
    if not scored_path.exists():
        return None
    entries = json.loads(scored_path.read_text(encoding="utf-8"))

    kp_recalls = [e["keypoint_recall"]["recall"] for e in entries if e.get("keypoint_recall", {}).get("recall") is not None]
    judged = [e["llm_judge"] for e in entries if e.get("llm_judge", {}).get("accuracy") is not None]
    latencies = [e["latency_sec"] for e in entries if e.get("latency_sec") is not None]

    out = {"n": len(entries)}
    if kp_recalls:
        out["keypoint_recall_avg"] = sum(kp_recalls) / len(kp_recalls)
    for key in ("accuracy", "completeness", "groundedness"):
        vals = [j[key] for j in judged if j.get(key) is not None]
        if vals:
            out[f"llm_{key}_avg"] = sum(vals) / len(vals)
    if latencies:
        out["latency_avg_sec"] = sum(latencies) / len(latencies)
    return out


def main():
    rows = {}
    for name in CONFIGS:
        path = EVAL_DIR / f"scored_ablation_{name}.json"
        rows[name] = summarize(path)

    print(f"{'config':<14}{'n':>4}  {'keypoint_recall':>16}  {'llm_accuracy':>13}  {'llm_complete':>13}  {'llm_ground':>11}  {'latency(s)':>11}")
    for name, s in rows.items():
        if s is None:
            print(f"{name:<14} -- chua co file scored_ablation_{name}.json (chay score_answers.py truoc) --")
            continue
        print(
            f"{name:<14}{s['n']:>4}  "
            f"{s.get('keypoint_recall_avg', float('nan')):>15.2%}  "
            f"{s.get('llm_accuracy_avg', float('nan')):>13.2f}  "
            f"{s.get('llm_completeness_avg', float('nan')):>13.2f}  "
            f"{s.get('llm_groundedness_avg', float('nan')):>11.2f}  "
            f"{s.get('latency_avg_sec', float('nan')):>11.2f}"
        )


if __name__ == "__main__":
    main()
