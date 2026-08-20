# Bonus C9 — Embedding serving regime (offline logic demo)

Host `Windows-AMD64` · backend `deterministic bag-of-words` · vector dimension `69` ·
corpus `8 documents`

Query: *Does embedding serving use a KV cache and a decode loop like chat serving?*

| Rank | Cosine | Retrieved document |
|--:|--:|---|
| 1 | 0.572 | Embedding serving is prefill-bound: one forward pass, no KV cache, no decode loop. |
| 2 | 0.211 | PagedAttention stores the KV cache in non-contiguous virtual-memory pages. |
| 3 | 0.000 | Continuous batching lets requests join and leave the running batch every step. |

## Finding

Embedding serving has no autoregressive decode loop or persistent KV cache: each text
needs one prefill-style forward pass. Consequently its throughput knob is a large,
token-sorted static batch, unlike chat serving where continuous batching admits and
retires sequences during decode. The offline result validates the retrieval/control
flow but not production embedding quality or accelerator throughput; bag-of-words
cannot match lexically different paraphrases. A real deployment should repeat the
batch-size sweep with a dedicated encoder such as Qwen3-Embedding or BGE-M3.
