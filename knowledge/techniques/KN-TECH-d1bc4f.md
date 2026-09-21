---
id: KN-TECH-d1bc4f
type: technique
title: The dihedral coset problem as the quantum route to lattices, and why noise tolerance is the binding constraint
tags: [quantum, dihedral, dcp, dsp, edcp, hidden-subgroup, kuperberg-sieve, subset-sum, lattice, svp, lwe, mlwe, reduction, pqc, post-quantum, adjacent]
confidence: established
complexity: >-
  DCP/DSP: Kuperberg sieve 2^{O(sqrt(log N))} quantum, requires error-free
  samples. Regev: DSP in quantum poly time GIVEN a modular subset sum oracle.
  Claimed unconditional poly time with 1/O(log n) noise tolerance: Simon 2026,
  UNVERIFIED (KN-LIT-e204ab).
applicability: >-
  Quantum cryptanalysis of lattice assumptions (SVP, LWE, and via EDCP variants
  MLWE); the same dihedral/hidden-shift machinery also bounds commutative
  isogeny group actions (KN-TECH-027).
source_refs: [KN-LIT-21383c, KN-LIT-2c8264, KN-LIT-4706, KN-LIT-1744, KN-LIT-e204ab]
added: 2026-08-06
superseded_by: null
---

## The problem family

**DSP (Dihedral Subgroup Problem).** A function `f` is constant on a subgroup
`H` of a dihedral group and on each of its cosets; identify `H`. Ettinger and
Høyer showed it suffices to handle `|H| = 2`. Standard coset sampling then puts
it in Regev's form: given repeated samples of

    (|0, x> + |1, x + d mod N>) / sqrt(2)

where `2N` is the group order, `d` is fixed and `x` is fresh per sample, find
`d`.

**DCP (Dihedral Coset Problem).** The same, except each sample is **faulty**
with probability `1/a(n)` — a random bit and a random value instead of the
correct superposition.

**EDCP / M-EDCP.** Extrapolated variants over which LWE (KN-LIT-4706) and
Module-LWE (KN-LIT-1744) are shown equivalent or reducible; these are the forms
that touch deployed schemes rather than asymptotic LWE.

Dihedral groups are *slightly* non-abelian, which is exactly why the abelian
HSP result of Boneh–Lipton does not apply.

## Why the difficulty sits in erasing the sample bits

The shared structure of every algorithm here:

1. Fourier-transform the `x + b_i d` register of each sample and measure,
   yielding `y_i` and leaving a two-branch superposition over `b_i` whose
   branches differ in phase by `w^{y_i d}`.
2. Compute the subset sum `z = sum b_i y_i` and measure all but its top bit `h`.
   With `N = 2^n` the residual phase is `w^{z'd} · (-1)^{h·d_n}` — so `h` holds
   the last bit of `d` in the relative phase of its branches.
3. **The obstruction:** the `b_i` registers remain entangled with `h`, so `h`
   cannot be Hadamard-measured. The `b_i` must first be *erased* — mapped to a
   fixed state — without disturbing the phase relationship.

Everything distinguishing the known approaches is step 3.

- **Regev (KN-LIT-21383c)** erases exactly, using a **modular subset sum
  oracle** to invert `sum b_i y_i = z' + hN/2` for each `h`. Polynomial time,
  but conditional on an oracle nobody can instantiate.
- **Kuperberg (KN-LIT-2c8264)** sidesteps erasure entirely by sieving:
  combining coset states pairwise into ever-more-structured phase differences.
  Unconditional, `2^{O(sqrt(log N))}`, but **requires error-free samples**.
- **Simon 2026 (KN-LIT-e204ab), UNVERIFIED,** erases by Hadamard-transforming
  and measuring the `b_i`, accepting the phase cost `(-1)^{sum b_j b'_j}`, then
  keeping only the groups that measured all-zero (hence paid no phase) and
  rebuilding the `d_n`-carrying bit from their partial subset sums.

## Why noise tolerance, not speed, is the binding constraint

This is the load-bearing fact of the whole area and the reason the field
treated DCP as harmless to lattices before 2026.

Regev's reduction converts `a(n)`-approximate lattice problems into DCP
instances **with faulty-sample rate `1/a(n)`**. Better approximation factor
therefore *costs* noise. So a DCP algorithm's usefulness against lattices is
governed by the noise it survives:

| DCP algorithm | Noise tolerated | Resulting SVP approximation factor |
|---|---|---|
| Kuperberg sieve | none (error-free input) | `2^{O(sqrt n)}` — no better than classical BKZ |
| Regev + subset sum oracle | n/a (oracle, not an algorithm) | n/a |
| Simon 2026 (claimed, unverified) | `1/O(log n)` | `sqrt(n) polylog(n)` |

A *faster* error-free DCP algorithm buys nothing against lattices. A
*noise-tolerant* one is what would move the exponent — which is precisely the
axis on which the 2026 claim, if it survives, would matter.

The BKSW improvement (KN-LIT-4706) removes the quadratic dimension blow-up in
Regev's original reduction (`N ~ 2^{n^2}`), which is what makes the composition
give a useful factor rather than a vacuous one.

## Applicability limits

- Adjacent to this program's ECDLP mission; it is the post-quantum lattice
  branch, load-bearing for GOAL-MLKEM-* and GOAL-MLDSA-*.
- **The poly-time row of the table above is an unverified claim days old at the
  time of writing.** The established content of this entry is the problem
  family, the erasure obstruction, the two pre-2026 algorithms, and the
  noise/approximation trade-off. Do not cite this entry as support for the
  poly-time DCP claim itself — that is KN-LIT-e204ab, `confidence: unverified`,
  with its open questions in KN-OPEN-8a5965.
- The reductions are asymptotic and unstructured. Reaching ML-KEM / ML-DSA
  requires the *module* variants (KN-LIT-1744), which is a separate step.
- The same dihedral/hidden-shift machinery governs commutative isogeny actions
  (KN-TECH-027, KN-TECH-051, KN-OPEN-014); a genuine advance on DCP would have
  to be assessed against CSIDH-type targets too, where the noise-free Kuperberg
  regime is the relevant one.
