# Consolidated L(1, χ) result: two independent studies agree

Recorded 2026-10-30 UTC. Two studies asked the same question independently,
in separate sessions with separate code:

- `research/nist_seed_lvalue_20261030/` (**lvalue**). Its protocol was
  committed before data (`dd218eb5`). It estimates L to x = 10⁸, uses exact
  D_K from PARI `coredisc`, and checks the estimator against exact class
  numbers. Population: 61 curves. **It is the canonical measurement and the
  one the paper cites.**
- `research/nist_seed_l1chi_20261030/` (**l1chi**, this directory). Its frozen
  `experiment.protocol/v1` record (`039665e8`) was merged before data. It
  estimates L to x = 10⁶, strips the conductor prime by prime, and uses
  secp256k1 as a positive control. Population: 69 curves. **It is an
  independent replication.**

`crosscheck.py` compares their committed outputs on the 61 curves they share
and recomputes nothing. Results are in `runs/crosscheck.json`.

| Check | Result |
|---|---|
| log L at x = 10⁶ (l1chi `logP_DK` against lvalue `logL[1e6]`) | equal to within **2.9 × 10⁻¹⁴** on all 61 curves |
| change from 10⁶ to 10⁸ (lvalue) | at most 7.3 × 10⁻⁴ in log L |
| null percentiles, conductor f_π = 1 (48 curves) | agree within 0.35 points (Monte Carlo and null implementation) |
| null percentiles, f_π ∈ {3, 5, 13} (12 curves) | differ by up to 35 points, by design (see below) |
| prime239v1 (f_π = 1) | log L = −1.40201 (10⁶) and −1.40194 (10⁸); 0.246th and 0.247th percentile; lowest in both |

**Why the conductor curves differ.** l1chi's decisive statistic used χ_Δ,
which is 0 at the conductor primes. lvalue's used χ_{D_K}, which can be ±1
there. These are different statistics on those 12 curves, not a
disagreement. Both studies' χ_{D_K} values agree exactly.

## The consolidated statement

- **The low value replicates.** prime239v1's L(1, χ_{D_K}) ≈ 0.246 sits at
  about the 0.25th percentile of the prime-order null and is the lowest of
  the 61 (or 69) eligible curves. Both studies reach this independently, and
  their L-values match to floating-point precision.
- **It is the same anomaly, not new evidence.**
  - The primes 3 ≤ ℓ ≤ 691 carry it: −0.998 of log L.
  - The terms for 5003 < ℓ ≤ 10⁶ are ordinary (l1chi post-hoc: z = −0.26).
  - The curve was selected for an extreme split count. The chance that some
    curve among 61 reaches this level by chance is about 0.14.
- **It doesn't support the CM-method story.** f_π = 1, so D_K = Δ with
  |D_K| ≈ 2²⁴¹. That gives h ≈ 2^116.8, within a factor of about 2 of the
  null median, and nowhere near the small |D_K| a CM-method generator
  produces.
- **There is no ECDLP consequence.** No known attack depends on L(1, χ) or h.

## Procedural notes

- **Same deviation in both.** Neither study's protocol record yields a fully
  conforming export. lvalue has no `experiment.export/v1`. l1chi's export
  carries structural `check-export` findings (`EXPORT_DEVIATION.md`).
- **Records untouched.** Both directories keep their own run records; nothing
  in either was moved or rewritten. Only pointers were added.
