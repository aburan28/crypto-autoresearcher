# POKE-4D Norm-Fiber Reassessment

This directory contains the arXiv-ready source for:

> Adam Buran, "Exact Enumeration of the POKE-4D Norm Fiber: A Conditional
> OW-KCA Security Reassessment," July 20, 2026.

## Build

```bash
tectonic -X compile --keep-logs paper.tex
```

## Reproduce the arithmetic validation

From the repository root:

```bash
python3 -B experiments/ecdlp_isogeny/iso_poke4d_norm_circle_enumeration.py \
  --output experiments/ecdlp_isogeny/iso_poke4d_norm_circle_enumeration_result.json
python3 -B experiments/ecdlp_isogeny/iso_poke4d_norm_circle_enumeration_verify.py \
  --input experiments/ecdlp_isogeny/iso_poke4d_norm_circle_enumeration_result.json \
  --output experiments/ecdlp_isogeny/iso_poke4d_norm_circle_enumeration_verify.json
```

The arithmetic artifact checks the exact norm-circle count and concrete
parameter translation.  It does not implement the higher-dimensional recovery
subroutine; its cost remains explicit as `C_HD` in the paper.
