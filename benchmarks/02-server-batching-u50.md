# 02 - Continuous batching under load (u50)

Host `Windows-AMD64` · `--parallel 4` · 13 samples over
60s at 2.0s intervals · raw CSV: `02-server-metrics-u50.csv`

| Gauge | Peak observed |
|:--|--:|
| `n_busy_slots_per_decode` (avg/decode) | 3.64 of 4 slots (91%) |
| `requests_processing` | 4 |
| `requests_deferred` | 46 |
| `kv_cache_usage_ratio` | n/a — not exported by llama.cpp `b10488` |
| `tokens_predicted_total` (final) | 2118 |

Highest sampled value was **3.64 of 4** slots. Note this gauge is llama.cpp's *average* busy slots per decode step, so the number below is the highest average we sampled, not an instantaneous maximum batch width. A peak near 1 means
requests were served one at a time -- either the load was too light to overlap, or
they arrived too far apart. A peak approaching `--parallel` means the scheduler was
genuinely packing concurrent requests into shared decode steps.
`requests_deferred` went above zero: more requests arrived than there were slots, so some waited. That wait is the queue time in your P95.

## My observation

The peak average batch width was 3.64/4 slots (91%), with four requests processing
and 46 deferred. Effective concurrency was higher at 10.8 because Little's Law also
counts requests waiting in the queue. The figures therefore agree rather than
conflict: the server kept almost every decode slot busy while excess work queued.
For actual slot utilization I trust the native 3.64 gauge; effective concurrency is
the better indicator of total in-system pressure.
