# Honest ledger — corrections to the program's self-assessment

*Written in response to an external critique that was correct on essentially every point.
This supersedes the more confident framing in the other review docs where they conflict.*

## The headline that was buried

**Against the program's own stated bar — an exponent change on generic E/F_p — every
red-team pass produced *zero* survivors.** That is the result. It is a legitimate,
useful negative (the core assumptions C, RANK, S6-forward, ICLOSE, DREG took ~30
adversarial mechanisms and none survived in-model). It was wrong to bury it under two
"positive" results that are **textbook reproductions, not discoveries**.

## Overclaim → correction

| Claim as written | Correction |
|---|---|
| EdDSA single-bit nonce fault = "new working attack" | **Reproduction** of a published class (Poddebniak et al., *EuroS&P 2018*; fault attacks on deterministic (EC)DSA/EdDSA). The recovery identity in `review_eddsa_fault.py` is the textbook one. It is "untested *in this corpus*," not new. |
| Deployment gate = "most deployment-relevant gap the red-team surfaced" | It is **the SafeCurves thesis** (SSSA / MOV / twist / small-subgroup; minimal validation misses what full validation catches). Correctly downgraded to a config gap — but it is a reproduction, and both it and EdDSA are **explicitly outside the rubric's bar** (protocol-layer / weak-by-construction). |
| MOV arm "yes(asymptotic)" alongside two measured sub-rho recoveries | The MOV arm **demonstrated transfer correctness only**; the code itself sets `subrho_measured: False`. "Asymptotic" is an assertion, not a measurement, and should not share a column with the SSSA/twist arms that ran to recovery. |
| Defect-B "rigorous KILL … independent confirmation" | The **proof** carries it; the **experiment is near-tautological** — the simulator draws `b` independently of `e`, so "the −b column isn't absorbed" holds by construction. The genuinely adversarial object (a fixed deterministic function of `c_k` chosen before the keys — the black-box-separation setting) was **never simulated**. The information argument is correct; the experiment is not independent evidence. |
| V₃ "evidence for [Proved, m=3]" | Overstated. What was measured is **one invariant** (χ₂ square-class resonance rank) of **one parametrization** (two-chord tower) at **one prime**, 4 w-specializations, D≤6. A flat χ₂-rank is evidence that *this resonance channel* doesn't grow at m=3 — **not** a statement about separability/solving cost in general, which is what the arity reduction is about. Downgrade to "one channel, narrow scope." |
| D5 "KILL (proxy)" | Overstated. The proxy measures **normality** (normalization charts = 1), but Yokoyama's semi-normality is actually a **signature/F5/S-polynomial condition** on `NS(Syz)` and `Phi(s)`, with `#G*` counting nonzero S-polynomial remainders in the computed non-reduced Gröbner basis. Reclassify to **OPEN / wrong-object**; the exact object is now recovered in `D5_YOKOYAMA_OBJECT.md`, but not implemented. |
| D6 "monotone → KILL" | **Under-evidenced** — see §D6 below. Reclassify to **UNRESOLVED / underpowered**. |

## Systematic weaknesses (apply to every KILL)

- **No error bars.** "exponent 0.49," "δ flat ±0.005," "rank ≤ 1" are point estimates
  from few samples. K2's "CM is slower, the opposite of a win" (0.49 vs 1.53 over ~5
  points across a 32× q-range) is **plausibly a constant-term / small-sample artifact**,
  not a structural fact. Every scaling KILL needs bootstrap CIs + a calibrated null.
- **Multiple-comparisons blindness.** The δ-battery is many predicates × d × curves;
  "tracks the matched control" was eyeballed, not tested against a null distribution.
  Several "flat" calls will be false negatives by chance.
- **Confirmation-structured.** Only "exponent < 0.5" counts as a win, and every run is
  toy-scale. That **guarantees a stream of KILLs** whether the assumptions are robust or
  the instruments are simply too small to see a channel. The writeups read KILLs as the
  former without warrant.

## D6 (#153) — the deprioritization was the real miss; here is the honest result

The phase transition past n≈30 is the one experiment that could falsify the core, and it
was deprioritized as "heavy / low-prior" — which **inverts the falsification logic**. Run
this pass (`src/d6_dreg_scaling.py`, `results/d6_dreg_scaling.log`), the honest findings:

1. **The original KILL had ~no data.** `ic_first_fall_t3.json` is **one** point (n=9) with
   `n_over_maxD: 5` — all 5 samples censored at the max_D=4 cap. `dsolv_scaling_t3.json` is
   3 points (n=9/12/15), `sem_dff` flat at 2 where it resolves, mostly `null` (censored).
   "Monotone → KILL" is **not supported by this data**.
2. **d_ff ≠ d_reg.** First-fall=2 is *not* the solving degree. A *bounded* d_reg would make
   the per-PDP solve **polynomial → ECDLP-threatening**. So the KILL actually requires
   d_reg to **grow**, which a flat d_ff does not show.
3. **d_reg is large but unmeasurable.** `dreg_measure.py` at n=21: D=2 and D=3 each solve
   only **1/126** variables, D=4 hits the **memory wall** (78 s). So d_reg is **>4 and not
   bounded** at n=21 — consistent with growth (rules out the polynomial-solve scenario),
   but a single point with no rate.
4. **A clean scaling curve is not achievable with this tooling.** The boolean d_reg
   instrument (`solved-vars-at-D`) does **not resolve the Semaev system even at n=6** (it
   saturates the D-search), and my matched semi-regular null was **miscalibrated** (it
   injected linear monomials the Semaev system lacks, making the null artificially easier —
   disclosed, not trusted). The memory wall ceilings honest measurement at **n≈21 ≪ 30**.

**Verdict: D6 is UNRESOLVED at reachable scale.** The available evidence is *consistent*
with generic d_reg growth (the KILL direction), and *inconsistent* with a bounded-d_reg
polynomial solve — but it **cannot produce a CI-backed scaling law and cannot exclude a
phase transition past n≈21**. A definitive D6 needs (a) a d_reg instrument that resolves
past the D=4 memory wall (sparse/streaming Macaulay or a real F4/F5 with degree
tracking), and (b) a *faithfully* matched semi-regular null. Both are real engineering,
not a toy run — which is exactly why it should have been prioritized, not skipped.

## Corrected status of the prime-field frontier

Not "every cell KILL." Honestly:

- **heavy-tail δ (#156)**: **KILL, now calibrated in the p-value sense**
  (`review_renyi_calibrated.py`). Rényi-2 collision-excess + L∞ min-entropy deficit,
  **permutation null + Holm-Bonferroni** over m=8 tests. No cell survives correction; the
  single raw p=0.05 is the expected chance hit (E[#]=0.4) with its control in the same
  band. The row-bootstrap interval in the script is only a rough stability diagnostic, not
  load-bearing evidence. *Caveat:* one curve at 2³², d≤3; scaling-in-p unrun.
- **stacked constants (#8)**: **KILL, now compatibility-aware** (`review_stacked_compat.py`).
  The naive "2^7.5 product" was a category error — the PDP-solve levers (crossbred/FHJRV/
  MITM) are *alternatives* for one step, not multipliers, and GLV/trace-2 need a *special*
  curve (unavailable on the generic bar). Best achievable generic stack = one solver,
  total exponent ~0.667, loses to rho by **2^43** at n=256. No exponent crossover.
- **K1, Néron–Severi, K2, D1**: KILL *in direction*, but on toy-scale point
  estimates **without CIs**; treat as "no signal seen at small scale," not settled.
- **R6**: narrowed (PKM no-win on the structured base); the arbitrary-index variant is the
  residual.
- **Defect-B**: KILL by **proof**, not by the (tautological) experiment.
- **D5**: **OPEN** — exact Yokoyama object recovered in `D5_YOKOYAMA_OBJECT.md`;
  needs an instrumented signature/F5/S-polynomial `#G*` implementation.
- **D6**: **UNRESOLVED / underpowered** — the one that could move a core assumption.

**Net.** The machinery and the self-correction discipline are sound; the *yield against
the stated bar is zero*, and that — not the two reproductions — is the headline. The two
genuinely open, high-value items are **D6** (a real d_reg-past-the-wall run with CIs and a
faithful null) and **D5** (the recovered but unimplemented Yokoyama `#G*` computation).
Everything else is
"interesting structure," per the framework's own principle.
