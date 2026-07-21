> **⚠ SUPERSEDED by `FINDING_v2.md` (kept for provenance, not overwritten).**
> This v1 is correct on the family, the semi-regular series, the linear d_reg law,
> and the n=9/D6 = d_reg-degeneracy mechanism (claims 1–4, independently validated).
> Its **claim 5** (`d_reg(sem) > d_reg(null)`) was argued from a raw subset-column
> corank — a method the independent RED-TEAM.md correctly refuted (H-DREG-001
> pre-labels it an artifact). The conclusion was **re-established honestly** in v2 by
> the corrected graded-Hilbert-function instrument and by an independent q→s
> solution-count adjudication (s=1; see `ADJUDICATION_solcount.txt`). Its **claim 6**
> ("no sub-rho signal") is re-supported in v2 via a first-fall completeness census,
> not by assuming sem ≥ semi-regular. Read `FINDING_v2.md`.

# Finding — the boolean Semaev t=3 degree of regularity grows **linearly**, and the n=9 "D6 null break" is a d_reg degeneracy, not an instrument defect

Thread: SIG asymptotics + DREG audit. Feeds **H-DREG-001** (degree axis) and
**H-SIG-001**. Follows the two most recent decisions
`DEC-20260720-001` (H-SIG-001 supported_scoped, cascade valid D<=5) and
`DEC-20260720-002` (H-DREG-001 inconclusive; "repair the D6 semi-regular null,
then measure D=6 deficit at n=12" flagged as the single highest-value next step).

Author: independent Claude session (2026-07-20), worked in isolation (no shared
commit; a live co-driver owns ledger archival).

## TL;DR

1. The support-matched **null is not miscalibrated at D6 by a code bug**. It fails
   its C5 control at **n=9, D6** for a *mathematical* reason: **d_reg(n=9) = 6**.
   At D = d_reg the random null reaches full rank (its quotient collapses to the
   constants), so the pre-collapse semi-regular formula `sr_pred` necessarily
   under-shoots the null's actual rank there. n=9 is "anomalous" precisely because
   the probe degree D6 coincides with its degree of regularity.

2. The instrument's semi-regular series is **correct** and was independently
   re-validated. The robust invariant, confirmed at **two** independent sizes:
   the null's **collapse degree** (where its quotient ncols-rank drops to ~1)
   equals the predicted **d_reg exactly** — n=6 collapses at D5 (=d_reg(6)),
   n=9 collapses at D6 (=d_reg(9)). Below d_reg the null's measured rank tracks
   `sr_pred` (exactly at n=9: D2..D5 incl. the non-trivial 9504; within a 4-dim
   finite-size wobble at n=6/D4 that shrinks with n). My initial
   "convolution-direction bug" hypothesis was **falsified empirically** — the
   ascending in-place recurrence computes the intended boolean series
   `A(z)=(1+z)^{2n}/[(1+z^2)^n(1+z^3)^n]` and the null obeys it.

3. Therefore **no D6-null instrument repair is needed** to unblock the degree axis.
   The valid measurement rule is simply: the semi-regular baseline is well-defined
   at probe degree D iff **D < d_reg(n)**. Since **d_reg(12) = 7**, the coordinator's
   target measurement — D6 at n=12 — is a clean sub-d_reg point and its null
   baseline WILL pass C5 (predicted). n=9 (d_reg=6) was the one degenerate size.

4. The scientifically decisive result: for this family
   (nb = 2n boolean vars, n quadratics + n cubics) the semi-regular degree of
   regularity has the **closed form** d_reg(n) = first non-positive coefficient of
   `B(z)^n`, `B(z) = (1+z)^2 / [(1+z^2)(1+z^3)]`, and it grows **linearly**:

   | n | 6 | 9 | 12 | 15 | 18 | 24 | 48 | 96 | 161 | 1000 | 8000 |
   |---|---|---|----|----|----|----|----|----|-----|------|------|
   | d_reg | (emp) | 6 | 7 | 8 | 9 | 10 | 17 | 30 | 46 | 252 | 1929 |

   d_reg/n → **c\* ≈ 0.238** (marginal slope over [4000,8000] = 0.239). d_reg/√n is
   strictly increasing (2.0 → 4.4), so growth is Θ(n), **not** O(√n).

5. **Consequence for the degree axis (H-DREG-001).** Linear d_reg forces the
   Gröbner/Macaulay solve to touch ~ `C(2n, 0.24n) ≈ 2^{1.06 n}` monomials, so the
   linear-algebra cost is `2^{(2..2.4) n}` (ω ∈ [2, 2.37]). Rho on an n-bit
   binary-field curve costs `2^{n/2}`. The Semaev-t3 Gröbner route is therefore
   **super-exponentially worse than rho** — no sub-rho signal on the degree axis,
   even in this binary Weil-descent case (a known negative control for the
   prime-field target). Moreover the true (sem) system carries **extra syzygies**
   (the cascade), which only **raise** d_reg above the null — the wrong direction
   for an attack. n=9: at D6 the null has collapsed (quotient 1) while the sem
   quotient is still 2040.

## Empirical validation (Sage, against the live SIG-005 instrument)

Per-degree quotient `q = ncols - rank` for the support-matched null and the true
Semaev (sem) system; null "collapses" (q → ~1) exactly at the predicted d_reg,
and the sem system is still far from collapse there (higher d_reg):

| n | pred d_reg | D | null rank vs sr_pred | q_null | q_sem |
|---|---|---|---|---|---|
| 6 | 5 | 3 | 84 = 84 (OK) | 149 | 77 |
| 6 | 5 | 4 | 527 vs 531 (−4, finite size) | 243 | 171 |
| 6 | 5 | **5** | 1584 (collapse) | **1** | **95** |
| 9 | 6 | 5 | 9504 = 9504 (OK) | 3111 | 2437 |
| 9 | 6 | **6** | 31179 (collapse) | **1** | **2040** |

Reading: at D = d_reg the **null** quotient is 1 (solved / full-support−1) while the
**sem** quotient is still 95 (n=6) / 2040 (n=9) — so **d_reg(sem) > d_reg(null)**,
replicated at two sizes. This directly contradicts H-DREG-001's support clause
(`d_reg(sem) < d_reg(null)`): the Semaev structure **raises** the solving degree.
n=9 receipts reproduced bit-for-bit from `RUN-EXP-SIG-005-h/-k`
(sem D6 29332/27292; null D6 31180/31179/28068).

## What this changes vs. the recorded decisions

- `DEC-20260720-002` treated the D6 null failure as a "miscalibrated D6 null"
  (instrument defect) and gated any status change on **repairing** it. This finding
  shows the failure is a **d_reg degeneracy at n=9**, the instrument is sound, and
  the fix is to **choose n with d_reg(n) > probe degree** (n>=12 for D6). The
  "prerequisite repair" is discharged conceptually.

- The degree axis — flagged as "the only live route" and "unmeasured past D=5" —
  is now **characterized in closed form** and points **negative**: d_reg = Θ(n)
  (density 0.24), Gröbner cost 2^{Θ(n)} ≫ rho. This does not by itself earn a
  scoped KILL of H-DREG-001 (that needs the coordinator + a direct sem-vs-null
  d_reg-drop measurement), but it converts "inconclusive, unmeasured" into
  "predicted no-signal with a validated model and a concrete confirmable test."

## Scope / honesty

- Toy scale. d_reg(n) is the **semi-regular** prediction, validated to match the
  random support-matched null exactly for D < d_reg at n=6, 9 (empirical) and by
  the exact closed form elsewhere. It is the standard proxy for the true solving
  degree; the sem system's own solving degree is >= this (extra syzygies).
- This is the **t=3** boolean Weil-descent family (binary field), a negative
  control for the generic prime-field target — not a prime-field result. AGENTS
  rules 4–7: no crypto-scale or prime-field claim is made or implied.
- No break claimed. This sharpens/【trends-weaken】s H-DREG-001 on the degree axis.

## Reproduce

- Pure-Python d_reg law + asymptotics: `dreg_growth_law.py` (no Sage).
- Sage validation (null matches sr_pred for D<d_reg; collapse at D=d_reg; sem
  quotient > null quotient): `validate_fast.sage` against the SIG-005 instrument
  `experiments/EXP-SIG-005/src/h013_f5_signatures.sage`.
- Recorded receipts cross-check: n=9 sem D6 (ncols 29332, rank 27292),
  null D6 (ncols 31180, rank 31179, sr_pred 28068) all reproduced bit-for-bit
  (`RUN-EXP-SIG-005-h`, `-k`).
