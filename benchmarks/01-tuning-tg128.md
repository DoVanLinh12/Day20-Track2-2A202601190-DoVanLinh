# 01 - Tune: thread-count sweep

Model `Qwen3.5-0.8B-Q4_K_M.gguf` · host `Windows-AMD64` · llama.cpp `b10488`
CPU: **6 physical · 12 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 35.5 | 99% |
| 3 | 35.2 | 98% |
| 6 | 35.2 | 98% |
| 12 | 35.7 | 99% |
| 24 | 36.0 | 100% |

**Best**: `-t 24` at 36.0 tok/s
**Slowest tested**: `-t 6` at 35.2 tok/s (1.02x spread)
**Against the physical-core default** (`-t 6`, 35.2 tok/s): 1.02x

Use this in your run:

```bash
LAB_N_THREADS=24 make bench
```

## My explanation

There is no meaningful CPU-thread knee in this sweep: every point lies between
35.2 and 36.0 tok/s. Moving from the six-core default to 24 threads improves only
1.02x, which is within the scale of run-to-run noise. This differs from the usual
CPU-only curve because `ngl=99` offloads the model through Vulkan; CPU threads are
not the main decode bottleneck, so oversubscribing them neither helps nor hurts much.
I would retain six threads rather than spend extra scheduling overhead for a marginal
0.8 tok/s peak.
