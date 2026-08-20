# Bonus B1 - Prebuilt vs source build

Host `Windows-AMD64` · CPU `AMD Ryzen 5 7430U with Radeon Graphics`
Vector extensions detected: none
llama.cpp `b10488` both sides · `threads=6` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

> **Backend mismatch, handled.** The prebuilt binary sees
> `['Vulkan0: AMD Radeon (TM) Graphics (8359 MiB, 7941 MiB free)']` and your source build sees `(no devices)`.
> Left at `-ngl 99` this comparison would have measured the accelerator and printed
> it under a compiler headline, so both sides were pinned to `-ngl 0`.

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 33.9 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 15.6 | 0.46x |

On this machine, the prebuilt binary is **2.18x faster**.

before: 33.9 tok/s (prebuilt release)
after:  15.6 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 0.46x

Same source revision, same model, same backend, same `-ngl` -- the only difference
is what the compiler was allowed to assume about the CPU.



## Explanation

The Ryzen 5 7430U is a Zen 3 CPU with AVX2/FMA support; the `none` label above is a
limitation of this lab's Windows hardware probe, not an absence of vector
instructions. Both runs used the same model, six threads, revision `b10488`, and
`-ngl 0`, so Vulkan cannot explain the result.

`-DGGML_NATIVE=ON` only lets the selected compiler target the current CPU. It does
not guarantee better code than the official Windows release, whose optimized CPU
kernels and runtime dispatch were built with a different production toolchain. The
local MinGW/GCC build reached 15.6 tok/s while the release reached 33.9 tok/s, so on
this host the release's code generation/kernel path outweighed native targeting.
Token generation for this small quantized model is strongly affected by memory
bandwidth, but a 2.18x gap is too large to attribute to bandwidth alone because both
binaries read the same weights on the same machine; instruction selection and the
chosen CPU kernel/toolchain are material here. Therefore the honest B1 conclusion is
that this source build did **not** beat the prebuilt binary.
