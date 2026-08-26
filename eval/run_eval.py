# eval/run_eval.py
"""Chay toan bo eval/questions.json qua Agent va ghi lai ket qua.

YEU CAU TRUOC KHI CHAY:
  1. GraphDB dang chay, repository "Farming" da import agri-ontology.ttl + crops_data.ttl
  2. GraphQL server dang chay: uvicorn main:app --host 0.0.0.0 --port 8001
  3. chroma_db/ va chunks_cache.pkl da duoc sinh (python ingest_rag.py)
  4. Bien moi truong GOOGLE_API_KEY hop le (file .env o thu muc goc)

Chay tu thu muc goc project:
  python eval/run_eval.py
  python eval/run_eval.py --limit 5        # chi chay 5 cau dau de test nhanh
  python eval/run_eval.py --output eval/results_raw.json

Ket qua ghi ra eval/results_raw.json (mac dinh), gom: cau tra loi cua agent,
tool nao duoc goi, thoi gian phan hoi (giay), va loi (neu co).
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_eval_agent_executor():
    """Tao AgentExecutor giong agent.py nhung bat return_intermediate_steps
    de biet duoc tool nao da duoc Agent goi cho tung cau hoi."""
    from langchain_classic.agents import AgentExecutor
    from agent import agent, tools

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True,
    )


def extract_output_text(output):
    if isinstance(output, list):
        texts = []
        for item in output:
            if isinstance(item, dict):
                texts.append(item.get("text", str(item)))
            else:
                texts.append(str(item))
        return "\n".join(texts)
    return output


def run(questions_path: Path, output_path: Path, limit: int | None, sleep_sec: float, categories: list[str] | None = None):
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    if categories:
        questions = [q for q in questions if q["category"] in categories]
    if limit:
        questions = questions[:limit]

    executor = build_eval_agent_executor()

    results = []
    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['id']}: {q['question']}")
        record = {
            "id": q["id"],
            "category": q["category"],
            "crop": q["crop"],
            "question": q["question"],
            "expected_tool": q["expected_tool"],
        }
        start = time.perf_counter()
        try:
            result = executor.invoke({"input": q["question"]})
            elapsed = time.perf_counter() - start
            tools_called = [
                step[0].tool for step in result.get("intermediate_steps", [])
            ]
            record["answer"] = extract_output_text(result["output"])
            record["tools_called"] = tools_called
            record["latency_sec"] = round(elapsed, 2)
            record["error"] = None
        except Exception as exc:  # ghi lai loi de khong mat toan bo eval neu 1 cau fail
            elapsed = time.perf_counter() - start
            record["answer"] = None
            record["tools_called"] = []
            record["latency_sec"] = round(elapsed, 2)
            record["error"] = f"{type(exc).__name__}: {exc}"
            print(f"   LOI: {record['error']}")

        results.append(record)
        if sleep_sec:
            time.sleep(sleep_sec)

    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDa chay xong {len(results)} cau -> {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", default=str(Path(__file__).parent / "questions.json"))
    parser.add_argument("--output", default=str(Path(__file__).parent / "results_raw.json"))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sleep", type=float, default=1.0, help="Giay nghi giua 2 cau (tranh rate-limit API)")
    parser.add_argument("--categories", default=None, help="Loc theo category, vd: rag,multi (mac dinh: tat ca)")
    args = parser.parse_args()

    cats = args.categories.split(",") if args.categories else None
    run(Path(args.questions), Path(args.output), args.limit, args.sleep, cats)
