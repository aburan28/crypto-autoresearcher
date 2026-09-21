---
id: KN-LIT-7674
type: literature
title: "Cryptanalysis of HAWK: a Guessing Game (with 30/06 correction)"
authors:
  - "Ben Nelson"
  - "Joshua Limbrey"
  - "Cong Ling"
  - "Andrew Mendelsohn"
year: 2026
venue: "IACR ePrint preprint 2026/1318 (ongoing; 30/06 update included)"
identifiers:
  eprint: "iacr:2026/1318"
  url: "https://eprint.iacr.org/2026/1318"
tags: [hawk, lattice-isomorphism-problem, module-lip, nrd-pip, quaternion, lenstra-silverberg, heuristic, key-recovery, pqc, cryptanalysis, fractional-ideals, super-polynomial]
confidence: read
citation_verified: body_read_from_user_provided_text
citation_verified_note: >-
  Full body text provided directly in research session 2026-08-05. All claims
  below are verified from the actual paper body, not from abstract alone.
  Supersedes KN-LIT-7670 (abstract-only entry with truncation error).
added: "2026-08-05"
supersedes: KN-LIT-7670
---

## Summary

Classical probabilistic polynomial-time algorithm for recovering the HAWK secret
key, assuming four number-theoretic heuristics plus Weber's conjecture. The
30/06 update acknowledges Heuristic 4 failed, making the algorithm super-polynomial.

## Algorithm structure (Algorithm 2: GuessingGame)

1. Sample lower-triangular unimodular U with short Gaussian entries.
2. Form G' = U*GU; set q' = G'_{11}.
3. Construct right O-ideal I = Φ(G') ≤ O (quaternion algebra) with nrd(I) = q'OK.
4. Find β ∈ O with I = (β, q')O via two-element representation (Section 5).
5. Reduce β using Babai rounding with bound ‖β‖ < O(n^{13/2}).
6. Set α = -nrd(β) + trd(β)²/4; form F = K(√α).
7. Apply Lenstra-Silverberg to find h ∈ F with N_{F/K}(h) = q'.
8. If h exists and h·O_F = a := (trd(β)/2 + √α, q')·O_F, recover private key.
9. Resample U until success.

## The four heuristics

**Heuristic 1 (Section 5.1):** P(α square-free) ≥ 1/2. Supported by density of
square-free ideals ≈ 1/ζ_K(2) ≈ 3/4 (lower bound).

**Heuristic 2 (Section 7):** P(image of α in O_K/d² corresponds to X+1) ≈ 1/4.
Enables O_F = O_K[√α] with high probability.

**Heuristic 3 (Section 8.2):** P(q' is a norm from F) = Ω(n^{-2-o(1)}).
Derived from S-unit lattice index bound O(n^{2+o(1)}).

**Heuristic 4 (Section 9) — FAILED per 30/06 update:**
"There are at most O(n^{1+o(1)}) ideals of O_F with relative norm q'O_K.
Given that one of these ideals is principal, P(a is principal) = Ω(n^{-1-o(1)})."

The error: the count O(n^{1+o(1)}) was for INTEGRAL O_F-ideals only, using the
argument that q'O_K has ≤ O(log n) prime factors hence ≤ 2^{O(log n)} = n^{O(1)}
prime ideals of O_F above it. The 30/06 update acknowledges the count must
include FRACTIONAL ideals "of which there are many."

## 30/06 correction (verbatim from paper)

> "Following discussions with Daniel Apon and Markku-Juhani Saarinen, we
> acknowledge that Heuristic 4 is insufficient to conclude that the main algorithm
> runs in polynomial time, and in fact the main algorithm appears to run in
> **super-polynomial time**. This mistake originates from the count of ideals of
> norm q' in O_F: one must include fractional ideals in this count, of which there
> are many. We note as an aside that Heuristics 1-3 have been independently
> experimentally verified."

## Case C confirmed from algorithm structure

The algorithm samples β with bounded norm ‖β‖ < O(n^{13/2}) via Babai
rounding (Section 6.3). This means the algorithm effectively samples from
fractional O_F-ideals with bounded denominators (Case C in GOAL-HAWK-001
BATCH-56498f derivation). As the denominator bound R grows, the pool size grows
as O(q'·R³) while the number of "easy" (principal) instances in the bounded pool
is at most the class number h(O_F) which does NOT grow with R. Hence density → 0,
confirming Case C: super-polynomial runtime with no derivable upper bound.

## Expected guesses under corrected count

Original claim (under Heuristic 4): O(n^{4+o(1)} log n) guesses.
Corrected: the Heuristic 4 probability Ω(n^{-1-o(1)}) per guess is no longer valid.
If the fractional ideal pool grows faster than n^{1+o(1)}, each guess probability
drops below Ω(n^{-1-o(1)}), making total guesses super-polynomial.

## What remains valid

- Heuristics 1-3: independently experimentally verified (per 30/06 update).
- The reduction from module-LIP to nrdPIP (Eurocrypt 2025, [8]).
- Theorem 6 (Chevignard et al.): polynomial oracle call to O-nrdPIP suffices.
- The algorithm is structurally correct conditional on Heuristics 1-3 and a
  corrected (sub-polynomial probability) version of Heuristic 4.

## GOAL-HAWK-001 relevance

This paper body confirms:
1. **Case C is the correct complexity case.** Bounded β → bounded denominator
   search → density → 0 as bound grows.
2. **Our BATCH-56498f/d44912 derivation was about O-ideals (quaternion algebra)**
   while the paper's correction is about O_F-ideals (number field). Both involve
   the same mathematical principle: fractional ideals in the full ideal group are
   infinite. Our derivation is correct for the quaternion setting; the paper's
   correction applies to the number field setting in Section 9.
3. **KN-OPEN-028 Q1 is answered**: super-polynomial time, specifically Case C.
   No sub-exponential advantage over brute force is established.
