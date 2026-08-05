# Memory-charged re-derivation of the FIPS 203 NIST margin under RC.MATZOV

**Task** TASK-20260803-648a0b · **Batch** BATCH-010 · **Goal** GOAL-MLKEM-003
**Role** Executor (observations only; no status change, no promotion, no closure)
**Date** 2026-08-03

> **What kind of numbers these are.** Every figure in this document is a
> **cost-model estimate** produced by a pinned estimator plus numbered modelling
> choices. Nothing here was measured. **No ML-KEM break is claimed.** Equally, a
> memory charge that *raises* the estimated attack cost above a NIST cutoff is
> **not a proof of security** — it is a statement about one cost model, at one
> parameter set, under the heuristics in `heuristics.yaml`. Scope is
> `primal_bdd` under `RC.MATZOV`; Arora–Gröbner is unavailable in this harness,
> so no "best attack overall" phrasing applies (H12).
>
> **Rule 12 status.** AGENTS.md rule 12 is UNMET and UNWAIVED for this batch.
> Nothing here changes, or treats as corrected, EV-MLKEM-011, EV-MLKEM-013,
> EV-MLKEM-017, KN-FIND-012 or KN-FIND-014. This is a fresh derivation.

---

## 0. The known-answer control (CTRL-0), verbatim

The control was run first. No number below was produced before it passed.

```
$ PYTHONPATH=/home/user/crypto-autoresearcher/tools/sage_free_estimator/shim:/tmp/le /usr/local/bin/python3 /home/user/crypto-autoresearcher/tools/sage_free_estimator/known_answer_control.py
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

PASS: every reference value reproduced exactly (delta 0.0) against lattice-estimator 3e48ef421ec2.
Scope: primal_bdd under RC.MATZOV. Arora-GB is unavailable in this harness; 'best attack' claims are scoped to the attacks served.
[control exit code: 0]
```

`git -C /tmp/le rev-parse HEAD` → `3e48ef421ec256afddb3e7d2249a77eab6e9ba12`
(matches the pin; the derivation script re-checks this and aborts otherwise).

β / η / d reported by the control — **389/422/1005, 606/640/1420, 855/889/1867** —
match the values named in the handoff exactly.

---

## 1. Baseline reproduced (H1)

| set | β | η | d | log2(rop) | NIST classical cutoff | free-memory margin |
|---|---:|---:|---:|---:|---:|---:|
| Kyber-512 | 389 | 422 | 1005 | 140.1994731076 | 143 | **+2.800527** (undercut) |
| Kyber-768 | 606 | 640 | 1420 | 200.9587149141 | 207 | **+6.041285** (undercut) |
| Kyber-1024 | 855 | 889 | 1867 | 270.7236234535 | 272 | **+1.276377** (undercut) |

Margin is defined throughout as `cutoff − log2(cost)`; **positive means the
estimated attack is cheaper than the cutoff.** These reproduce
RUN-MLKEM-015-001 / EV-MLKEM-015 at delta `0.0` (CTRL-2).

The total decomposes exactly into a lattice-reduction term and an SVP term, and
both were independently recomputed (CTRL-1, `red + svp − rop == 0.0`):

| set | log2 red (BKZ) | log2 svp (final BDD call) |
|---|---:|---:|
| Kyber-512 | 139.108730 | 139.284845 |
| Kyber-768 | 199.909206 | 200.006581 |
| Kyber-1024 | 269.812506 | 269.628903 |

---

## 2. Which dimension does the cost model actually sieve in? (H2)

**Neither β nor η, as printed.** Read out of the pinned source rather than
asserted:

- `estimator/lwe_primal.py:465` — `bkz_cost = costf(red_cost_model, beta, d)`
- `estimator/lwe_primal.py:482` — `eta = svp_dim - 1` (Kyber params are
  non-homogeneous), so the final call runs at rank `svp_dim = eta + 1`
- `estimator/lwe_primal.py:488` — `svp_cost = costf(red_cost_model, svp_dim, svp_dim)`
- `estimator/lwe_primal.py:490` — plus `babai_cost(d - eta)` for the lift
- `estimator/reduction.py:800` — inside `class Kyber` (inherited by `GJ21` →
  `MATZOV`): `beta_ = beta - self.d4f(beta)`, and the gate count at line 808 is
  `C · 2^(a·beta_ + b)`.

So `RC.MATZOV` sieves in the **dimensions-for-free–reduced** dimension, and
`primal_bdd` performs sieves in **two** dimensions:

| set | BKZ sieve dim `β − d4f(β)` | SVP sieve dim `(η+1) − d4f(η+1)` | peak |
|---|---:|---:|:--|
| Kyber-512 | 389 − 35.802619 = **353.197381** | 423 − 37.915470 = **385.084530** | SVP |
| Kyber-768 | 606 − 48.847070 = **557.152930** | 641 − 50.867988 = **590.132012** | SVP |
| Kyber-1024 | 855 − 62.855627 = **792.144373** | 890 − 64.764670 = **825.235330** | SVP |

Because η + 1 > β on all three sets, **the single final BDD/SVP call, not BKZ,
sets peak memory.** Getting this wrong in either direction would have moved
log2 M by roughly 7–13 bits and c\* by a few percent (H2, direction clause) —
not by orders of magnitude, but the choice is sourced, not assumed.

Sequential calls ⇒ peak = max, not sum (H3). Model B below charges each term by
its own sieve's memory, which sidesteps that assumption.

---

## 3. Memory: unit stated, conversion shown (H4, H5)

**Database size.** A list-decoding sieve in dimension *n* holds
`N = 2^(0.2075·n)` **vectors**. The exponent is sourced three ways (H4): the
pinned estimator writes the literal `2 ** (0.2075 * beta_)` at
`reduction.py:415, :854, :936`; it is the rounded closed form
`log2(√(4/3)) = 0.20751874963942182` (checked here, |Δ| = 1.875e−05, CTRL-3);
and it is the kissing-number sieve-memory floor recorded in this repository's
corpus at KN-LIT-104, KN-LIT-6625, KN-LIT-6765, KN-LIT-081, KN-TECH-044,
KN-OPEN-017. *The BDGL16 paper itself was not retrieved in this batch* — what is
sourced is the exponent as the instrument uses it, its closed form, and its
corpus status.

**Unit chain (the conversion the handoff asked to see explicitly):**

```
M_vectors  = 2^(0.2075 · n)                                 [vectors]
M_zq       = n · M_vectors                                  [elements of Z_q]   <- HEADLINE
M_bits     = ceil(log2 q) · n · M_vectors,  q = 3329, ceil(log2 q) = 12  [bits]
```

The Z_q unit is the pinned instrument's **own** sieve-memory convention:
`estimator/lwe_dual.py:172` computes `cost["mem"] += sieve_dim * N` and `:204`
documents `mem` as "memory requirement in integers mod q". Numerator (its gate
count) and denominator (its memory count) therefore live in one convention.

| set | log2 M vectors | log2 M Z_q elements | log2 M bits (12/coeff) |
|---|---:|---:|---:|
| Kyber-512 (peak) | 79.905040 | **88.494071** | 92.079034 |
| Kyber-768 (peak) | 122.452392 | **131.657286** | 135.242249 |
| Kyber-1024 (peak) | 171.236331 | **180.924993** | 184.509955 |

BKZ-sieve memory (Z_q elements) for reference: 81.752787 / 124.731163 / 173.999577.

---

## 4. The charged-cost family (H6, H7)

Charged cost is `T · M^c`. Two charge models are reported; neither is adopted as
"the" answer.

- **Model A (peak):** `log2 cost = log2(rop) + c·log2(M_peak)`.
- **Model B (per-term):** `cost = red·M_bkz^c + svp·M_svp^c`.

Conventions and their provenance (full text in `results.json["charge_conventions"]`):

| c | name | source |
|---|---|---|
| 0 | free memory | **Sourced.** The convention of the NIST cutoffs, of MATZOV, and of lattice-estimator `rop`. This is the convention EV-MLKEM-015 reports in. |
| 1/6 | probe point | **This batch's own construction.** No source; shape only. |
| 1/3 | 3D wiring / Wiener full cost | **Sourced.** KN-LIT-094 (Wiener, *The Full Cost of Cryptanalytic Attacks*, J. Cryptology 17(2):105–124, 2004; corpus `citation_verified: read`) and KN-TECH-035. BSGS: n^{1/2} steps → n^{2/3} full cost is exactly `T·M^{1/3}` at `T = M = n^{1/2}`. KN-OPEN-017 poses this same charge for sieving and records that no corpus source had computed it. |
| 1/2 | 2D planar layout | **This batch's own construction — UNSOURCED.** The same wiring argument specialised to a plane (M cells in a plane have diameter ~M^{1/2}). No primary source located in corpus or retrieved this batch. |
| 1 | hardware × time | **Partial.** The literal definition of full cost in KN-LIT-094, instantiated with hardware ≈ memory. Wiener's n^{2/3} comes from the optimised M^{1/3} access charge, not from T·M; reported as the family's upper end only. |

**Charged cost and margin, unit = Z_q elements** (margin positive = still an
undercut; negative = the estimate now exceeds the cutoff):

Kyber-512 (cutoff 143):

| c | log2 cost A | margin A | log2 cost B | margin B |
|---|---:|---:|---:|---:|
| 0 | 140.1995 | **+2.8005** | 140.1995 | +2.8005 |
| 1/6 | 154.9485 | −11.9485 | 154.5257 | −11.5257 |
| 1/3 | 169.6975 | **−26.6975** | 169.0295 | −26.0295 |
| 1/2 | 184.4465 | −41.4465 | 183.6503 | −40.6503 |
| 1 | 228.6935 | −85.6935 | 227.7908 | −84.7908 |

Kyber-768 (cutoff 207):

| c | log2 cost A | margin A | log2 cost B | margin B |
|---|---:|---:|---:|---:|
| 0 | 200.9587 | **+6.0413** | 200.9587 | +6.0413 |
| 1/6 | 222.9016 | −15.9016 | 222.4553 | −15.4553 |
| 1/3 | 244.8445 | **−37.8445** | 244.1417 | −37.1417 |
| 1/2 | 266.7874 | −59.7874 | 265.9526 | −58.9526 |
| 1 | 332.6160 | −125.6160 | 331.6749 | −124.6749 |

Kyber-1024 (cutoff 272):

| c | log2 cost A | margin A | log2 cost B | margin B |
|---|---:|---:|---:|---:|
| 0 | 270.7236 | **+1.2764** | 270.7236 | +1.2764 |
| 1/6 | 300.8778 | −28.8778 | 300.3779 | −28.3779 |
| 1/3 | 331.0320 | **−59.0320** | 330.2350 | −58.2350 |
| 1/2 | 361.1861 | −89.1861 | 360.2328 | −88.2328 |
| 1 | 451.6486 | −179.6486 | 450.5673 | −178.5673 |

A 1001-point sweep over c ∈ [0,1] is in `results.json`; the margin is monotone
non-increasing in c (CTRL-7).

---

## 5. The headline: c\* per parameter set

**c\* = the smallest c such that charging M^c erases the undercut.** For Model A
it has a closed form, `c* = margin / log2(M)`, verified against bisection to
< 1e−9 (CTRL-6).

| set | free-memory margin | log2 M_peak (Z_q) | **c\* (Model A)** | c\* (Model B) | c\* in vectors | c\* in bits |
|---|---:|---:|---:|---:|---:|---:|
| Kyber-512 | +2.800527 | 88.494071 | **0.03164649** | 0.03277120 | 0.035048 | 0.030414 |
| Kyber-768 | +6.041285 | 131.657286 | **0.04588645** | 0.04701194 | 0.049336 | 0.044670 |
| Kyber-1024 | +1.276377 | 180.924993 | **0.00705473** | 0.00720010 | 0.007454 | 0.006918 |

**Unit robustness (CTRL-4, H5).** Across vectors / Z_q elements / bits, c\*
moves by about 15% — from 0.035048 to 0.030414 on Kyber-512, 0.049336 to
0.044670 on Kyber-768, 0.007454 to 0.006918 on Kyber-1024. The unit slip the
handoff warned about is real but bounded: it does not move c\* by orders of
magnitude and does not change the direction of any statement below.

**Distance to the named conventions.** c\* is **10.5× / 7.3× / 47.2×** smaller
than the sourced 3D exponent 1/3, and **15.8× / 10.9× / 70.9×** smaller than the
unsourced 2D exponent 1/2.

### What c\* means physically

Charging `M^{c*}` multiplies the estimated cost by exactly `2^{margin}`:

| set | multiplier at c\* | plain statement |
|---|---:|---|
| Kyber-512 | 2^2.8005 = **6.97×** | any uniform surcharge of ≈7 gate-equivalents per charged operation erases the undercut |
| Kyber-768 | 2^6.0413 = **65.86×** | ≈66× |
| Kyber-1024 | 2^1.2764 = **2.42×** | ≈2.4× |

Set against the per-access cost the named conventions actually charge for a
memory of this size: a single access to the Kyber-512 peak database costs
`M^{1/3} = 2^29.5` under the 3D wiring bound and `M^{1/2} = 2^44.2` under the 2D
one (Kyber-768: 2^43.9 / 2^65.8; Kyber-1024: 2^60.3 / 2^90.5). The charge that
erases the undercut is smaller than either by 27 to 89 orders of magnitude in
base 2.

### Sensitivity to the one genuinely optimistic assumption (H9)

The headline charges *every* gate in the MATZOV count as one memory access. If
only a fraction f of gates touch the database, `c* = (margin + log2(1/f)) / log2 M`:

| f | Kyber-512 | Kyber-768 | Kyber-1024 |
|---|---:|---:|---:|
| 1 (headline) | 0.031646 | 0.045886 | 0.007055 |
| 2^−10 | 0.144648 | 0.121841 | 0.062326 |
| 2^−20 | 0.257650 | 0.197796 | 0.117598 |
| 2^−30 | 0.370652 | 0.273751 | 0.172869 |

Even at one database access per **million** gates, c\* stays below the sourced
1/3 on all three sets. Only near f = 2^−30 does Kyber-512's c\* cross 1/3.

---

## 6. Controls

All eight passed; full records in `results.json["controls"]`.

| control | what it checks | result |
|---|---|---|
| CTRL-0 | known-answer control reproduces Sage-computed RUN-MLKEM-015-001 at delta 0.0 | PASS (exit 0) |
| CTRL-1 | `rop == red + svp` exactly, and both terms independently recomputed from `MATZOV(β,d)` and `MATZOV(η+1,η+1) + babai(d−η)` | PASS |
| CTRL-2 | this run's log2(rop) equals RUN-MLKEM-015-001 / EV-MLKEM-015 | PASS (delta 0.0) |
| CTRL-3 | estimator literal 0.2075 vs closed form log2(√(4/3)) | PASS (|Δ| = 1.875e−05) |
| CTRL-4 | c\* scales exactly inversely with log2 M across the three units | PASS (|Δ| < 1e−12) |
| **CTRL-5** | **NULL OBJECT.** Same charging pipeline on a zero-memory attack (log2 M = 0): margin must not move for any c and c\* must not exist | PASS (max movement 0.0 bits) |
| CTRL-6 | Model A closed form vs bisection | PASS (|Δ| < 1e−9) |
| CTRL-7 | margin non-increasing in c over 1001 sweep points | PASS |

CTRL-5 is the inventor-protocol control-before-belief check: it distinguishes
"the memory figure produces the penalty" from "the pipeline manufactures a
penalty for anything fed into it".

---

## 7. What was established, and in which direction

**Direction, stated explicitly.** Charging memory moves the estimated cost of
`primal_bdd`/`RC.MATZOV` **UP**, and the undercut recorded in EV-MLKEM-015
**does not survive** any of the memory charges examined here. The critical
exponent is **c\* ≈ 0.0316 / 0.0459 / 0.0071** for Kyber-512/768/1024 — one to
two orders of magnitude below the smallest sourced convention (1/3). In the
headline unit the entire undercut is bought back by a uniform cost multiplier of
about **7× / 66× / 2.4×**.

**Observation, not verdict.** Per the Executor contract, this batch records
these figures and does not conclude that any hypothesis is supported or
refuted, that KN-OPEN-016 is closed, or that a heuristic is validated. That
judgement belongs to the Reviewer, Validator, Red Team and Coordinator.

**What must not be read into this.**

1. **No ML-KEM break is claimed** — and none is implied. This batch *raised* the
   estimated attack cost.
2. **A raised estimate is not a proof of security.** It is one cost model, at
   one parameter set, under H1–H12, several of which are unvalidated.
3. **The charged costs at c = 1/3 and c = 1/2 are upper bounds on a
   memory-aware attacker** (H10). The β/η/d here were chosen by minimising a
   *free-memory* gate count. An attacker paying for memory would re-optimise —
   toward smaller sieve dimensions, lower-memory sieve variants, or enumeration
   hybrids — and would pay less than −26.7 / −37.8 / −59.0 bits of margin. c\*
   itself is unaffected by this, because c\* is a property of the published
   free-memory operating point, which is the point EV-MLKEM-015 reports.
4. **Scope** is `primal_bdd` under `RC.MATZOV` only (H12). Arora–Gröbner is
   unavailable in the harness. If a cheaper attack exists at these parameters,
   the free-memory undercut is larger and c\* rises proportionally.
5. **Estimates, never measurements.**

**Unsourced or unvalidated inputs, listed rather than buried:** H7's c = 1/2 and
c = 1/6 (this batch's own construction); H3 (peak = max over sequential sieves,
argued not tested); H8 (cutoff held fixed under charging, argued from AES key
search using O(1) storage, reference computation not examined); H9 (all gates
charged as accesses — the most optimistic assumption in the direction of the
conclusion, sensitivity tabulated above); H10 (no memory-aware re-optimisation);
H11 (NIST cutoffs inherited from archived records; primary NIST text unreadable
under network policy, exactly as EV-MLKEM-015 recorded); and the BDGL16 primary
source for 0.2075, which was not retrieved this batch.

---

## 8. What remains open

1. **Memory-aware re-optimisation (H10).** The obvious successor: re-run the
   estimator's optimisation *under* a charge M^c, for c across the family, and
   report the attacker's best charged cost rather than the charged cost of the
   free-memory optimum. That is what would turn the c = 1/3 row from an upper
   bound into an estimate. It needs a cost model for lower-memory sieve variants
   that `RC.MATZOV` does not supply.
2. **The access fraction f (H9).** A decomposition of the AGPS20 / MATZOV gate
   count into database-touching and non-touching gates would replace the
   sensitivity table with a number. This is the single input that could move
   c\* into the same range as the named conventions, and only at f ≲ 2^−30.
3. **A source for c = 1/2**, or an argument that the planar case is not the
   right null for this hardware.
4. **KN-OPEN-017** asks exactly where the enumeration/sieving crossover moves
   under full cost. This batch supplies one point on that question — the primal
   BDD side at cryptographic dimensions — but does not compute the crossover,
   because it does not cost enumeration.
5. **Whether the NIST cutoffs should themselves be restated in a charged
   convention (H8).** Argued here to be unchanged because the reference
   computation is memory-light; not verified against the NIST text, which was
   not readable.
6. The Kyber-1024 figure `c* = 0.00705` should not be read as precise to three
   significant figures: a one-bit error in its cutoff or baseline moves it by
   0.006 (H11).

---

## 9. Artifacts

- `memory_charged_derivation.py` — the exact script run, including the control
  invocation as step 0 (it refuses to proceed on a non-zero control exit or a
  missing `delta 0.0`, and re-checks the estimator commit pin).
- `results.json` — per set: β, η, d, log2(rop) and its two terms, NIST cutoff,
  free-memory margin, sieve dimensions, log2 memory in four units with the
  conversion string, charged cost and margin for each named c under both charge
  models, a 19-point sweep, c\* under both models and all units, the access
  fraction sensitivity, the physical-meaning block, and all eight controls.
- `heuristics.yaml` — H1–H12, each with statement, justification, falsifier,
  validation status, and the direction an error would move c\*.
- `receipt.json` — commands, environment, timestamps, budget, policy.
