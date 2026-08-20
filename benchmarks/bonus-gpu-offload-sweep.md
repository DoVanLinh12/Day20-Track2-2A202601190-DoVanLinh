# Bonus - GPU offload sweep

Host `Windows-AMD64` · backend(s) `vulkan` ·
llama.cpp `b10488` · `threads=6` · metric `tg128`

| -ngl | tg128 (tok/s) | vs -ngl 0 | vs best |
|:--|--:|--:|--:|
| 0 | 34.1 | 1.00x | 90% |
| 8 | 14.2 | 0.42x | 38% |
| 16 | 18.4 | 0.54x | 49% |
| 24 | 33.3 | 0.98x | 88% |
| 32 | 37.7 | 1.11x | 100% |
| 99 | 37.5 | 1.10x | 99% |

Best: `-ngl 32` at 37.7 tok/s
-- 1.11x faster than CPU-only.

Where the curve flattens tells you the model ran out of layers to move. Where it
*peaks below* full offload tells you something did not fit and the accelerator
started paying to fetch weights it could not hold.

## My finding

Full offload is effectively best: `-ngl 32` reaches 37.7 tok/s and `-ngl 99`
reaches 37.5 tok/s, a difference below 1%. The plateau shows that 32 already covers
all useful model layers; asking for 99 cannot move more work. Partial offload at 8–16
layers is much worse than CPU-only (0.42–0.54x), indicating that split execution pays
host/device synchronization and transfer overhead before enough compute has moved to
Vulkan. Once almost every layer resides on the integrated GPU, that boundary cost is
amortized and throughput becomes 1.11x CPU-only.
