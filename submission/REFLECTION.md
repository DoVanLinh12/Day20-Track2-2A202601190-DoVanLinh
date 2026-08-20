# Reflection — Day 20 Lab (Personal Report)

**Họ Tên:** Đỗ Văn Linh  
**Cohort:** A20-K2  
**Ngày submit:** 2026-08-20

---

## 1. Hardware & runtime *(rubric 1, 2 — 10 điểm)*

- **OS:** Windows 11 AMD64
- **CPU:** AMD Ryzen 5 7430U with Radeon Graphics
- **Cores:** 6 physical / 12 logical
- **CPU extensions:** AVX2
- **RAM:** 14.8 GB
- **Accelerator:** AMD Radeon qua Vulkan
- **llama.cpp asset đã tải:** `llama-b10488-bin-win-vulkan-x64.zip`
- **Model đã dùng:** Qwen3.5 0.8B (`LAB_MODEL=qwen35-0.8b`)
- **Quantization:** Q4_K_M (primary) + UD-Q2_K_XL (compare)

**Chạy ở đâu:** laptop của tôi.

**Setup story:** Repo ban đầu giả định `.venv/bin` và nhận Git Bash là Linux. Tôi sửa
Makefile để nhận MINGW/MSYS, dùng `.venv/Scripts`, gọi công cụ qua `python -m`, và bỏ
self-upgrade pip đang chạy vì Windows khóa file. Tôi chọn Qwen để vòng benchmark/load
test ngắn hơn; runtime Vulkan và hai GGUF được setup tự động.

---

## 2. Đo lường *(rubric 3, 4, 5 — 20 điểm)*

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| Q4_K_M | 0.50 | 2747 | 1749 / 1855 | 29.5 / 31.4 | 3578 / 3737 / 3737 | 33.9 |
| UD-Q2_K_XL | 0.39 | 2660 | 1769 / 1824 | 30.1 / 30.4 | 3678 / 3712 / 3712 | 33.3 |

**Quan sát:** Q2 nhỏ hơn 22% nhưng chậm hơn khoảng 2%, nên không có speedup thực tế.
Với cùng câu hỏi goodput, Q2 trả lời trôi chảy nhưng nhầm sang “độ ổn định”, thay vì
SLO. Tôi chọn Q4 cho serving cần chất lượng; Q2 chỉ đáng dùng khi RAM/đĩa là giới hạn.

---

## 3. Serving under load *(rubric 8, 9, 10 — 20 điểm)*

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 0.29 | 22000 | 41000 | 41000 | 7.3 | 0.0% |
| 50 | 0.33 | 32000 | 58000 | 58000 | 10.8 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 1.13×
- **P95 tăng:** 1.41×
- **Effective concurrency ở 50 users:** 10.8 so với `--parallel=4` slots
- **Peak `llamacpp:n_busy_slots_per_decode`:** 3.64 / 4 slots (91%)

**Saturation reading:** Server đã bão hòa ở 10 users và rất rõ ở 50: tải tăng 5× nhưng
RPS chỉ tăng 1.13×, P95 lên 58 giây, 46 request bị deferred. Effective concurrency
10.8 vượt bốn slot, nên latency thêm chủ yếu là queue time. Với SLO P95, tôi sẽ giới
hạn admission/queue trước; tăng CPU thread không hợp lý vì thread sweep gần như phẳng.

---

## 4. Integration *(rubric 12, 13 — 15 điểm)*

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | localhost | stub |
| N17 Data pipeline | in-memory query/document flow | stub |
| N18 Lakehouse | toy Python document collection | stub |
| N19 Vector + features | `TOY_DOCS` + keyword overlap | stub |
| N20 Serving | `llama-server` OpenAI-compatible HTTP | real |

**Latency split** (mean của 3 query):

- embed: 0.0 ms
- retrieve: 0.0 ms (một query đo 0.1 ms)
- llm: 11273.5 ms
- **stage chiếm nhiều nhất:** llm (xấp xỉ 100% total)

**Reflection:** LLM là bottleneck đúng như kỳ vọng vì embedding bị tắt và retrieval chỉ
là scan in-memory. Muốn giảm pipeline 2×, tôi sẽ giảm output/context hoặc tối ưu đường
accelerator của LLM. Tối ưu retrieval dưới một mili-giây không thể thay đổi E2E đáng kể.

---

## 5. The single change that mattered most *(rubric 11 — 10 điểm)*

**Change:** tăng `-t` từ physical-core default 6 lên điểm đo tốt nhất 24.

```text
before:  35.2 tok/s ở -t 6
after:   36.0 tok/s ở -t 24
speedup: 1.02×
```

Curve gần như phẳng: mọi điểm từ 1 đến 24 thread chỉ nằm trong 35.2–36.0 tok/s. Kết
quả này khác kỳ vọng CPU-only (tăng tới physical cores rồi giảm), nhưng phù hợp với
`ngl=99`: model được offload qua Vulkan nên CPU-thread count không còn là bottleneck
decode chính. Thêm thread chỉ thay đổi phần CPU nhỏ như scheduling/tokenization.

Vì 0.8 tok/s có thể nằm trong nhiễu và 24 thread tạo thêm scheduling contention, thay
đổi thực sự quan trọng là nhận ra **không nên tune CPU threads khi accelerator đang giữ
bottleneck**. Tôi sẽ giữ 6 thread và tập trung vào batching/admission control, nơi số đo
cho thấy queue rõ ràng.

---

## 6. Bonus *(optional — tối đa 20 điểm)*

**Đã làm:** B1 tự build và so sánh; B2 GPU-offload sweep; B3 before/after từ
sweep; B4 challenge C5 “smallest useful quantization”; B5/C9 embedding-serving
trên endpoint local thật.

```text
before:  34.1 tok/s (-ngl 0, CPU-only)
after:   37.7 tok/s (-ngl 32, Vulkan)
speedup: 1.11×
```

Partial offload không tạo đường cong tăng đều: `-ngl 8` và `16` chỉ đạt 14.2 và
18.4 tok/s, thấp hơn CPU-only, vì split execution phải đồng bộ/truyền dữ liệu qua ranh
giới host–Vulkan. Khi 32 layer đã chuyển sang accelerator, chi phí đó được amortize;
`-ngl 99` không nhanh thêm vì không còn layer hữu ích để chuyển.

B1 dùng đúng revision `b10488`, cùng Q4, 6 thread và ép cả hai binary về `-ngl 0`.
Bản MinGW/GCC `-DGGML_NATIVE=ON` đạt 15.6 tok/s, trong khi prebuilt đạt 33.9 tok/s.
Ryzen 5 7430U có AVX2/FMA; dòng “none” trong report chỉ do hardware probe Windows
không ghi extension. Kết quả 0.46× cho thấy native targeting không bảo đảm thắng
toolchain và CPU kernel/runtime dispatch của release đã được tối ưu tốt hơn.

C5 cho kết quả Q4 2/5 và Q2 0/5 trên năm prompt strict. Q2 sai phép nhân, bịa goodput
là caching layer và vi phạm JSON-only, nên tiết kiệm 0.11 GB không đáng. C9 chạy
`llama-server /v1/embeddings` local thật: batch 1 đạt 0.3 texts/s và batch 16 đạt
4.0 texts/s, trong khi latency chỉ tăng từ 3.03 lên 3.96 giây. Điều này xác nhận
embedding là prefill-only và static batching quan trọng hơn continuous batching.
Demo tái dùng chat GGUF để không tải thêm; production vẫn cần đánh giá bằng encoder
chuyên dụng như Qwen3-Embedding hoặc BGE-M3.

---

## 7. Điều làm tôi ngạc nhiên nhất

Tăng user 5× gần như không tăng throughput, trong khi 91% decode slots luôn bận. Điều
này cho thấy raw concurrency có thể chủ yếu tạo queue chứ không tạo goodput.

---

## 8. Self-check trước khi push

- [x] `hardware.json`
- [x] `models/active.json`
- [x] baseline và tuning reports
- [x] load 10/50, saturation và batching reports
- [x] integration report
- [x] 5 screenshots
- [x] `make verify` exit 0 sau khi stage artifact
- [x] Repo GitHub public: `https://github.com/DoVanLinh12/Day20-Track2-2A202601190-DoVanLinh`
- [ ] Paste URL repo vào LMS
- [x] Không commit GGUF hoặc `runtime/`
