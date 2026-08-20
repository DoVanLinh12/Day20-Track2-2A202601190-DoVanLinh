# 03 - Integrate: RAG pipeline run

Host `Windows-AMD64` · llama.cpp `b10488` ·
retrieval backend: **keyword overlap** · 3 queries

| Query | Contexts retrieved | embed (ms) | retrieve (ms) | llm (ms) | total (ms) |
|:--|--:|--:|--:|--:|--:|
| Why is goodput more useful than raw throughp... | goodput, paged, radix | 0.0 | 0.1 | 19227.2 | 19227.3 |
| What problem does PagedAttention actually so... | paged, radix, disagg | 0.0 | 0.0 | 7339.2 | 7339.3 |
| When does splitting prefill and decode help?... | disagg, radix, batching | 0.0 | 0.0 | 7254.0 | 7254.1 |

Mean per stage (ms): embed **0.0** · retrieve **0.0** ·
llm **11273.5** · total **11273.6**
Dominant stage: **llm** (100% of total)

## Answers returned

**Why is goodput more useful than raw throughput?**

> Based on the context provided, **goodput** is more useful than raw throughput because it specifically counts only the requests per second that met the Target Time-to-Fill (TTFT) and Target Time-to-Poll (TPOT) targets, whereas raw throughput ignores SLOs.

This distinction is crucial because throughput at saturation ignores SLOs, meaning that a system might be operating at full capacity (high throu

**What problem does PagedAttention actually solve?**

> PagedAttention solves the problem of **internal fragmentation** in GPU memory by storing the KV cache in non-contiguous pages, thereby removing the wasted space that would otherwise be consumed by the internal fragmentation of contiguous memory blocks.

**When does splitting prefill and decode help?**

> Splitting prefill and decode helps when the **prefill operation is compute-bound** and the **decode operation is memory-bound**.

This is because the context explicitly states that:
*   **Prefill** is compute-bound.
*   **Decode** is memory-bandwidth-bound.

By splitting them, the system can utilize different hardware resources (compute vs. memory) for each phase, optimizing performance where the 


## Which N16-N19 pieces are real

- N16 Cloud/IaC: stubbed as localhost; no cluster or Compose deployment is used.
- N17 Data pipeline: stubbed as the in-memory query/document flow.
- N18 Lakehouse: stubbed as the toy Python document collection.
- N19 Vector + features: stubbed; retrieval is keyword overlap over `TOY_DOCS`.
- N20 Serving: real `llama-server` through its OpenAI-compatible HTTP endpoint.

The LLM dominating at 11273.5 ms (effectively 100% of mean latency) matches my
expectation because embed is disabled and retrieval is a tiny in-memory scan. To halve
latency I would attack LLM generation first—shorten output/context, use an appropriate
quantization, or improve accelerator execution—because optimizing the sub-millisecond
retrieval path cannot materially change end-to-end time.
