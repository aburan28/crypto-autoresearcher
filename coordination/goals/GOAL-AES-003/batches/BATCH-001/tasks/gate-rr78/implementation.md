# GATE-RR78-1 implementation note and protocol deviations

Executor session, 2026-08-01. Start 21:54:30Z, frozen halt boundary 22:34:30Z
(start + 2400 s). `claim_tier: toy`. `certificate.kind: none` (pure measurement;
no solve or relation is claimed, so no solution certificate applies).

**Nothing in this file or in the artifacts asserts anything about AES security.**
No hypothesis is declared supported, rejected, or closed. No heuristic is
declared validated or refuted. Those judgements are the Reviewer's and
Coordinator's.

## 1. Contract status (reported, not repaired)

- No `experiments/<EXP-ID>/specification.yaml` with `status: approved` and
  non-null `approved_by` exists for GATE-RR78-1. The governing document is an
  Idea-Generator **proposal** that self-labels every gate as a proposal.
  This session therefore ran as an exploratory scratchpad gate. Missing
  contract fields are listed in `PREREGISTRATION.md` §0.
- `scratchpad/rr78/candidate_report.yaml` **does not parse as YAML**
  (`ParserError` at line 1307/1313: a block sequence under
  `deferred_unbounded` followed by a mapping key `note:` at the same
  indentation). Read as text as instructed; **not repaired**. Details in
  `PREREGISTRATION.md` §0b.

## 2. What was built

- `gate.c` — AES-NI engine (`-maes`), 4 pthreads. Contains **no RNG**: every
  round key, coset base, matrix and plaintext-stream key is supplied by
  `driver.py` from master seed `20260801`.
- `pin.c` — single-block harness used only for pinning.
- Counting: 2^32-entry `uint8` counter array (4 GB), relaxed atomic
  byte increments, overflow flag on any counter passing 255, then a parallel
  occupancy histogram. `n = Σ_v hist[v]·C(v,2)`, cross-checked against the
  independent identity `n = (Σ m_b² − N)/2` from the same histogram (V6).
  `Σ_b m_b = N` is asserted on every run.

## 3. Pinning (V3 gate) — PASSED before any measurement

- `pin_check.py`: **123 vectors** compared byte-for-byte against
  `aes_reduced.py`, covering `r = 1..10` × `final_mix_columns ∈ {False,True}`
  × 6 random (key, plaintext) pairs, **plus** two independent-random-round-key
  wirings (`r = 4, 6`) exercising the NULL-3 code path, **plus** the FIPS-197
  known-answer vector at `r = 10`
  (`69c4e0d86a7b0430d8cdb78070b4c55a`). **0 failures.**
  `aes_reduced.py` sha256 `2c76f3e5db83ec2500ce1010a392a135869d8b9dd1a534af817e06f15babb447`.
- `pin2_check.py`: **end-to-end** pin of the projection π, the bucketing and
  the pair counter. Three `2^16`-text configs recomputed in pure Python
  (`inv_shift_rows ∘ mix_columns(·, AES_INV_MIX)`), comparing `n`, distinct
  bucket count and max occupancy. **All match exactly** (n = 2, 1, 0).

## 4. Protocol deviations (all recorded, none discarded)

- **D1 — primary arm moved from 2^24 to 2^32, decided before any run.**
  Pre-run fact A5 (`prereg_algebra.py`): for the 3-byte diagonal sub-coset
  `{0,5,10}` the round-1 output space `MC(SR(D'))` has dimension 24 but its
  basis touches **all four** bytes of column 0, so it is **not** byte-aligned
  and SubBytes at round 2 does **not** preserve it. The subspace trail dies at
  round 2 on the sub-coset for a reason unrelated to depth, and no positive
  control exists at 2^24. Recorded in `PREREGISTRATION.md` §1.1 **before**
  execution.
- **D2 — positive-control stage truncated.** Measured cost at 2^32 is
  **147 s per configuration** (4.3e9 atomic random-access counter increments
  dominate; encryption is not the bottleneck). PR-1 was run and passed on
  `j0 = 0`. `PC1-j1..j3` and both PR-1b configurations were **NOT RUN** and are
  recorded as not run — never as passing.
- **D3 — trial multiplicity far below the pre-registered 20.** At 147 s per
  configuration the 2400 s budget admits ~14 configurations total. The 2^32
  arm was run at **1 trial per (arm, round)**. This is a resolution shortfall,
  pre-registered as expected in `PREREGISTRATION.md` §5, and it is the single
  largest limitation of this session.
- **D4 — the 2^24 sub-coset arm (20 trials, all four controls) was NOT RUN.**
  Budget was spent on the exact-algebra 2^32 arm and its controls instead.
  Recorded as not run.
- **D5 — `r = 7` and `r = 8` not run.** Pre-registered as conditional on the
  `r = 6` arm reading residue 0 (`PREREGISTRATION.md` §5 item 5). The
  antecedent did not hold.

## 5. Reproduction

```
gcc -O3 -maes -msse4.1 -pthread -o gate gate.c
gcc -O2 -maes -o pin pin.c
python3 pin_check.py          # V3 gate
python3 driver.py pin2 && python3 pin2_check.py
python3 driver.py pc           # PR-1
python3 driver.py combo32      # AES arm + nulls
python3 driver.py r3
python3 analyze.py
```

Every configuration line fed to `gate` is reconstructible from master seed
`20260801` and the stage name; the exact per-run round-key sha256, coset base,
free byte positions, `j0` and projection matrix are stored in
`raw_*.jsonl` and `meta_*.jsonl`.
