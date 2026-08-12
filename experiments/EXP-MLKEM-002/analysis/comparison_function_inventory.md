# Comparison function inventory (EXP-MLKEM-002)
## Source lock
- `v5.9.1-stable` tag object `fb2d72b70f4f823efa7dddf9e427700864adf513` (expected match: True); peeled commit `1d363f3adceba9d1478230ede476a37b0dcdef24`
- `v5.9.2-stable` tag object `a82476d144290bf6a786607a16c224acff63d882` (expected match: True); peeled commit `ac01707f552c611fbd135cc723b2682b3e7f80f2`

## Backends
- scalar `mlkem_cmp_c` in `wc_mlkem_poly.c` lines [4736, 4746] (prefix) / [4746, 4756] (postfix); loops `i < sz`; bodies identical across tags: True
- dispatcher `mlkem_cmp` lines [4757, 4777] (prefix): NEON if aarch64+ARMASM else AVX2 if USE_INTEL_SPEEDUP else scalar
- x64 AVX2 `mlkem_cmp_avx2` in `wc_mlkem_asm.S` [16588, 16755] → [15378, 15548]; ML-KEM-1024 coverage 1536 → 1568 bytes
- aarch64 NEON `mlkem_cmp_neon` in `armv8-mlkem-asm.S` [8669, 8969] → [8681, 8981]; reduction `ins v9.b[0], v8.b[1]` → `ext v9.16b, v8.16b, v8.16b, #8`

## Premise verdicts
- CVE-2026-10097 (ORS-025): **present**
- CVE-2026-6330 (ORS-026): **present**
