# 01 - Measure: latency baseline

Model `Qwen3.5 0.8B` · host `Windows-AMD64` · llama.cpp `b10488`
Settings: `threads=6` `ngl=99` `ctx=2048`
`max_tokens=64` · warm-up discarded
Completed requests: `Q4_K_M` 10/10 · `UD-Q2_K_XL` 10/10

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|:--|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2747 | 1749 / 1855 | 29.5 / 31.4 | 3578 / 3737 / 3737 | 33.9 |
| UD-Q2_K_XL | 0.39 | 2660 | 1769 / 1824 | 30.1 / 30.4 | 3678 / 3712 / 3712 | 33.3 |

- **TTFT** = prefill. Short prompts keep it small; long-context RAG is where it explodes.
- **TPOT** = per-output-token decode cost, bounded by memory bandwidth. `decode tok/s = 1000 / TPOT_p50`.
- `UD-Q2_K_XL` and `Q4_K_M` decode within 2% of each other here, for 0.11 GB difference on disk.

## My observation

Q2 saves 0.11 GB (22% of the Q4 file) but is not faster here: decode falls from
33.9 to 33.3 tok/s, while median TTFT rises from 1749 to 1769 ms. On the same
goodput question, Q2 produced a coherent but incorrect explanation about stability
instead of SLO compliance. I would keep Q4 for quality-sensitive serving; Q2's disk
saving is useful only when memory is the binding constraint.
