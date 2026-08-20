"""C5: compare the two locally installed quantizations on five fixed prompts."""
from __future__ import annotations

import json
import pathlib
import sys

import httpx

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "lib"))
import labkit  # noqa: E402


PROMPTS = [
    "Return only the number: 17 * 23.",
    'Return only a JSON object with keys "name" and "score" from: Linh scored 92 points.',
    "In one sentence, distinguish goodput from raw throughput in model serving.",
    "What memory problem does PagedAttention solve? Answer in one sentence.",
    "Trả lời đúng một câu: tại sao tăng số người dùng sau điểm bão hòa làm P95 tăng?",
]


def evaluate(label: str, model: pathlib.Path, port: int) -> list[dict[str, str]]:
    rows = []
    print(f"\n==> {label}: {model.name}")
    with labkit.serve_bg(str(model), port=port):
        for index, prompt in enumerate(PROMPTS, 1):
            response = httpx.post(
                f"http://127.0.0.1:{port}/v1/chat/completions",
                json={
                    "model": "local",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0,
                    "max_tokens": 96,
                },
                timeout=180,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            rows.append({"quantization": label, "prompt": prompt, "answer": answer})
            print(f"  [{index}] {answer}")
    return rows


def main() -> int:
    active = labkit.load_active()
    root = labkit.repo_root()
    rows = evaluate(active["primary_quant"], root / active["primary_model"], 8101)
    rows += evaluate(active["compare_quant"], root / active["compare_model"], 8102)
    output = root / "benchmarks" / "bonus-c5-quality-eval.json"
    output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n==> Wrote {output.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
