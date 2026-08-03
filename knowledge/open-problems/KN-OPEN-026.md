---
id: KN-OPEN-026
type: open_problem
title: How large is the concrete security discount from module/ring structure, and does it grow with better techniques?
tags: [module-lwe, ring-lwe, lwe, structure, hybrid-attack, coefficient-isometry, sparse-secret, fhe, kyber, ml-kem, concrete-security, cost-model, symmetry, open, lattice]
confidence: reported
status: open
source_refs: [KN-OPEN-012, KN-TECH-022, KN-TECH-046, KN-TECH-082, KN-LIT-7663, KN-LIT-7667, KN-LIT-7666, KN-LIT-116]
added: 2026-08-01
superseded_by: null
---

## Statement

[[KN-OPEN-012]] asks the **qualitative** question: do ideal/module lattices admit
structure-exploiting attacks beyond generic BKZ? As of its writing the corpus's answer
was [[KN-TECH-046]]'s: yes in principle, via the class-group/unit-lattice line, but only
at approximation factor `exp(Õ(√n))` — **far above** anything deployed, so no concrete
parameter set was affected.

2026 supplied a **different and quantitative** answer, from a mechanism that has nothing
to do with class groups and that bites **at deployed parameters**:

| Source | Mechanism | Reported gap |
|---|---|---|
| [[KN-LIT-7663]] | **Coefficient isometries** amortise hybrid-attack preprocessing across derived instances sharing a public matrix | up to **15 bits** (sparse-secret RLWE); **2–3 bits** (Kyber/ML-KEM) |
| [[KN-LIT-7667]] | Ring multiplicative structure accelerates the **guessing and decoding** steps of hybrid decoding | `O(N)` asymptotic in sparse-secret setting; up to **13 bits** (FHE sparse Ring-LWE) |
| [[KN-LIT-7666]] | Improved **MITM engine** for hybrid dual on sparse secrets | "consistent and significant" improvement; claims to invalidate an accelerated BGV scheme |

The open problem is therefore no longer *whether* structure helps concretely. It is:

**(Q1) How large is the discount, and is the current 2–15 bit range the true size or
merely the first thing anyone found?** Two independent mechanisms appeared in one year,
neither anticipated by the prior consensus that structure is free. That is weak evidence
the space is not exhausted.

**(Q2) Does the discount grow with dimension, or is it a bounded constant?**
[[KN-LIT-7667]]'s `O(N)` is asymptotic in the ring degree; [[KN-LIT-7663]]'s isometry
count is a property of the ring. Whether the bit gap widens as parameters grow — which
would matter for long-term parameter selection — is not addressed by either.

**(Q3) Is the sparse-secret concentration essential or incidental?** Every large gap
reported is in the sparse-secret regime; ML-KEM's uniform-ish secrets show 2–3 bits.
If sparsity is essential, this is an FHE parameter-selection problem. If it is merely
where the technique matured first, it is a broader one.

## Why it matters

- **Parameter selection is done with the "MLWE ≈ LWE" heuristic.** [[KN-LIT-7663]] says
  that heuristic fails at realistic parameters. Even a 2–3 bit systematic overestimate
  is a calibration error in a standardised scheme's security claim, and the FHE-side
  figures are large enough to matter for scheme selection.
- **It is the sharpest available test of the transfer question.** `KN-OPEN-012`'s second
  half asks whether this program's ECDLP structure-exploitation experience transfers to
  lattices. The 2026 mechanism is **amortisation of expensive preprocessing across
  symmetry-derived instances** — which is, structurally, what index calculus does with a
  factor base and what `glv-gls`-style automorphism speedups do for relation harvesting.
  If that correspondence is real rather than verbal, it is a two-way channel and the
  program has relevant expertise. **Nothing here establishes that it is real.**

## Current state (as reported)

- Two independent 2026 mechanisms, both reported, **neither verified by this program**.
- Figures are **model-relative** (mostly lattice-estimator cost models) and cross-model
  comparison is meaningless — `KN-TECH-040`'s standing warning.
- **No standardised parameter set is claimed compromised** by any of the three sources.
- The class-group line ([[KN-TECH-046]], [[KN-LIT-116]]) remains stuck at
  `exp(Õ(√n))` and is **not** what changed. Conflating the two lines would misstate both.

## What would resolve it

1. **Read [[KN-LIT-7663]] and [[KN-LIT-7667]]** and extract, for each, the cost model and
   the exact regime. Cheap, and required before any figure above is cited as a number
   rather than as a report.
2. Determine whether the two mechanisms **compose** — isometry amortisation of
   preprocessing plus ring-accelerated guessing — or whether they overlap. If they
   compose, the current figures are lower bounds on the discount.
3. Settle (Q2) by asking each mechanism's authors' analysis what happens as `N` grows.
   This is answerable from the papers, not by experiment.
4. Only then, and only if the program has a reason to care beyond adjacency: consider
   whether the amortisation correspondence to index calculus is formalisable. **This is
   the speculative step and should not be attempted before steps 1–3.**

## Not verified here

Every figure in this entry is relayed from an ePrint abstract retrieved 2026-08-01. **No
paper was read in full, no attack reproduced, and no lattice experiment has ever been run
by this program.** No claim is made that ML-KEM, Kyber, Dilithium, or any FHE scheme is
insecure, nor that the discount is larger than reported. The index-calculus
correspondence in "Why it matters" is **this program's own analogy** and appears in none
of the sources. **Does not bear on the ECDLP.**
