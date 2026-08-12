# DEV-FIXED-COMPILER-001

Status: `DEVELOPMENT ONLY`, `TOY-EVIDENCE`, and `NON-CANONICAL`.

This directory preserves a deterministic one-seed 12/14/16-bit development sweep and its independent replay certificate. It is not a runner-approved experiment, does not satisfy the frozen three-seed protocol, and cannot be promoted into an ECDLP or preprocessing-frontier claim.

## Integrity

- raw result SHA-256: `fc1a92521e2a2a10b7f56ac18a9ba144ae5b6aa6b9127a1375c95a336acd6b7e`
- verification receipt SHA-256: `c3024bd60f9a3eee6638fc03aa2a36739ba691f908b482d7a5f12ea4b1df0e17`
- generator SHA-256: `f06f56bc659d0ef66c3ad19bf4b97e51a4af8bb9a376030830d1ae3323a9bd76`
- verifier SHA-256: `145641c26f1edb7dab73ff9f3dd99c64de9df57ff7685cf0c61c834e1af99b7c`
- independent arithmetic SHA-256: `d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552`

The receipt reports `canonical_configuration: false`, `development_only: true`, 3 verified instances, 36 verified rows, and no routing rows.

## Reproduce

Run `command.txt` from the repository root with Python 3.13.1, then verify the result with:

```bash
python3 -B experiments/EXP-ECDLP-FIXED-COMPILER-001/src/verify_fixed_curve_compiler.py --input experiments/EXP-ECDLP-FIXED-COMPILER-001/development/DEV-FIXED-COMPILER-001/raw-result.json --allow-development
```
