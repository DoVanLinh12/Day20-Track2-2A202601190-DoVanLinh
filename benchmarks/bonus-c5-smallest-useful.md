# Bonus C5 — Smallest useful quantization

Model `Qwen3.5 0.8B` · temperature `0` · five fixed prompts · same Vulkan runtime and
serving flags. Full raw answers are in `bonus-c5-quality-eval.json`.

A response passes only when it is semantically correct **and** follows the requested
format. This strict rule matters for production extraction/tool-calling workloads.

| Test | Q4_K_M | UD-Q2_K_XL | Evidence |
|---|---|---|---|
| `17 × 23` | PASS | FAIL | Q4 returned 391; Q2 returned 371. |
| JSON extraction | PASS | FAIL | Q4 returned only the object; Q2 wrapped it in a Markdown fence. |
| goodput vs throughput | FAIL | FAIL | Both definitions missed SLO-qualified throughput; Q2 invented a caching layer. |
| PagedAttention | FAIL | FAIL | Neither answer identified KV-cache fragmentation correctly. |
| Vietnamese P95 saturation | FAIL | FAIL | Q4 confused P95 with problem difficulty; Q2 repeated the prompt. |
| **Strict total** | **2/5** | **0/5** | Q2 loses both factual accuracy and instruction following. |

## Finding

Q4_K_M is the smallest of these two quantizations I would consider deploying, and
even it needs domain evaluation because this 0.8B model scored only 2/5. The next lower
UD-Q2_K_XL is where usefulness breaks: it saves 0.11 GB but becomes wrong on arithmetic,
hallucinates the definition of goodput, and fails strict JSON formatting. Combined with
the baseline where Q2 was also 2% slower, there is no speed, quality, or operational
reason to ship Q2 on this 14.8 GB machine. I would keep Q4 and control memory through
context/queue limits instead.
