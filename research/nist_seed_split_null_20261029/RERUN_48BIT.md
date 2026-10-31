# Rerun of the 48-bit validation with rows kept (written before the run)

Written 2026-10-30 UTC, before `validate48_rows.py` ran. It clears deviation D2
in `DEVIATIONS.md`.

**What changes.** `validate48_rows.py` is `validate48.py` plus row output. It
uses the same seed (20261029), the same RNG call order and the same PARI calls.
It writes one JSONL row per sampled prime-order curve: trial, p, b, N, t and
the split count over odd ℓ ≤ 691. It also writes a summary with unrounded
aggregates and the rows' SHA-256.

**Success criterion, fixed in advance.** The rerun reproduces the original run
when both printed lines match `runs/validation48_stdout.log` character for
character:

- the same two primes p = 265379731317611 and 226472989768877;
- the same model and empirical means, SDs, KS D values and tail
  probabilities, at the printed precision.

A mismatch means the original run is **not** reproduced. That would be
reported as a finding, and the old aggregates would stay unauditable.

**Gate.** The run starts only after `scripts/checkpoint.sh gate` passes.
