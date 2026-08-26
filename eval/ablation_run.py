# eval/ablation_run.py
"""Ablation study: so sanh 3 cau hinh trong so cua Hybrid Retriever
(BM25 + Semantic Vector Search) tren cac cau hoi RAG / multi-tool.

  - hybrid   : BM25=0.4, Semantic=0.6  (mac dinh cua he thong)
  - bm25_only: BM25=1.0, Semantic=0.0
  - vector_only: BM25=0.0, Semantic=1.0

Chi chay lai cac cau hoi loai "rag" va "multi" (cau hoi "kg" khong di qua
Hybrid Retriever nen khong bi anh huong).

Moi cau hinh chay trong 1 tien trinh python con rieng (vi trong so duoc doc
1 lan luc import module hybrid_retriever.py) -> can GraphDB + GraphQL server
+ Chroma + GOOGLE_API_KEY san sang giong nhu run_eval.py binh thuong.

Chay tu thu muc goc project:
  python eval/ablation_run.py
  python eval/ablation_run.py --limit 4   # test nhanh voi it cau hoi hon
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = Path(__file__).resolve().parent

CONFIGS = {
    "hybrid": {"BM25_WEIGHT": "0.4", "SEMANTIC_WEIGHT": "0.6"},
    "bm25_only": {"BM25_WEIGHT": "1.0", "SEMANTIC_WEIGHT": "0.0"},
    "vector_only": {"BM25_WEIGHT": "0.0", "SEMANTIC_WEIGHT": "1.0"},
}


def main(limit, sleep_sec):
    import os

    for name, env_overrides in CONFIGS.items():
        output_path = EVAL_DIR / f"results_ablation_{name}.json"
        print(f"\n=== Chay cau hinh: {name} ({env_overrides}) ===")

        env = os.environ.copy()
        env.update(env_overrides)

        cmd = [
            sys.executable, str(EVAL_DIR / "run_eval.py"),
            "--categories", "rag,multi",
            "--output", str(output_path),
            "--sleep", str(sleep_sec),
        ]
        if limit:
            cmd += ["--limit", str(limit)]

        subprocess.run(cmd, cwd=str(ROOT), env=env, check=True)

    print("\nHoan tat ablation. Dung eval/score_answers.py tren tung file")
    print("results_ablation_<config>.json de cham diem va so sanh, vi du:")
    print("  python eval/score_answers.py --results eval/results_ablation_hybrid.json --output eval/scored_ablation_hybrid.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()
    main(args.limit, args.sleep)
