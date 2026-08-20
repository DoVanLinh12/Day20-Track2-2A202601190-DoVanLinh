# 02 - Serve: load test + saturation reading

Host `Windows-AMD64` · llama.cpp `b10488` ·
`--parallel 4` · `ctx=2048` · `threads=6` ·
`ngl=99`

| Users | Reqs | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|:--|--:|--:|--:|--:|--:|--:|--:|
| 10 | 17 | 0.29 | 22000 | 41000 | 41000 | 7.3 | 0.0% |
| 50 | 19 | 0.33 | 32000 | 58000 | 58000 | 10.8 | 0.0% |

*Effective concurrency = RPS x average latency (Little's Law) -- how many requests were
really in flight, regardless of how many users locust simulated. It counts queued requests
too, so the occupancy/slot ratio can legitimately exceed 1.0; it is occupancy, not
utilisation. For true slot utilisation use the server's own gauges (`make metrics`).*

## What these two runs say

| Going from 10 to 50 users | |
|:--|--:|
| Offered load | 5x |
| Throughput actually delivered | **1.13x** (23% of linear) |
| P95 latency | **1.41x** |
| Effective concurrency at 50 users | 10.8 vs `--parallel 4` slots (occupancy/slot ratio 2.70) |

**Saturated.** Throughput delivered only 1.13x for 5x the offered load, and effective concurrency (10.8) is at or above all 4 decode slots. Saturation sets in somewhere at or below 50 users; the load you added beyond that point became queue time rather than throughput.

Throughput moved 1.13x while P95 moved 1.41x. That gap is the goodput argument: past saturation you buy throughput by spending latency, and if your SLO is a P95 target then the requests you added are no longer being served within it. (This lab does not fix an SLO number for you -- pick one in your write-up and state how much goodput you keep at it.)

> **Small sample.** Only 17 requests completed in the
> shorter run, so these percentiles are indicative rather than solid. Note also that
> locust averages only *completed* requests: when the run ends with requests still
> queued, effective concurrency is an **under**-estimate. Trust the throughput-scaling
> row over the concurrency row here, and run longer (`-t 3m`) if you want firmer numbers.

## My reading

The server is already saturated by 10 users and clearly saturated at 50. A 5x
increase in offered users yields only 1.13x throughput (0.29 to 0.33 RPS), while P95
grows 1.41x to 58 s and effective concurrency reaches 10.8 for only four slots.
The native metrics reinforce this with 3.64/4 busy slots and 46 deferred requests.
For a P95 SLO I would first reduce admission concurrency or queue length rather than
add CPU threads: the thread sweep is flat, while the evidence shows waiting—not idle
compute—is the dominant extra latency.
