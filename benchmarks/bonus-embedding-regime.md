# Bonus C9 — Local embedding serving regime

Host `Windows-AMD64` · backend `llama-server /v1/embeddings` on `localhost:8081` ·
model `Qwen3.5-0.8B-Q4_K_M.gguf` · vector dimension `1024` · corpus `8 documents`

Query: *Does embedding serving use a KV cache and a decode loop like chat serving?*

| Rank | Cosine | Retrieved document |
|--:|--:|---|
| 1 | 0.895 | Embedding serving is prefill-bound: one forward pass, no KV cache, no decode loop. |
| 2 | 0.846 | RadixAttention reuses a shared prompt prefix across requests via a radix tree. |
| 3 | 0.812 | PagedAttention stores the KV cache in non-contiguous virtual-memory pages. |

## Local batch sweep

| Batch | Wall time (ms) | Throughput (texts/s) |
|--:|--:|--:|
| 1 | 3029.3 | 0.3 |
| 2 | 2464.8 | 0.8 |
| 4 | 2652.1 | 1.5 |
| 8 | 3821.4 | 2.1 |
| 16 | 3960.5 | 4.0 |

## Finding

Embedding serving has no autoregressive decode loop or persistent KV cache: each text
needs one prefill-style forward pass. Consequently its throughput knob is a large,
token-sorted static batch, unlike chat serving where continuous batching admits and
retires sequences during decode. On the local endpoint, increasing the batch from 1
to 16 raised measured throughput from 0.3 to 4.0 texts/s (about 13.3x) while request
latency rose only from 3.03 to 3.96 seconds. The top retrieval result was also the
correct serving-regime document. This uses the already-downloaded chat GGUF to remain
fully local; production retrieval quality should still be evaluated with a dedicated
encoder such as Qwen3-Embedding or BGE-M3.
