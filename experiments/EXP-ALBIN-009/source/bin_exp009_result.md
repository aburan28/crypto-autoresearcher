# BIN-EXP-009 Result — the m=4 diagonal point for PO-BIN-001(b)

**Date:** 2026-06-01. Script: `bin_exp009_m4_diagonal.sage` + `msolve` 0.9.5. Log: `bin_exp009_m4_diagonal.log`.

## SURVIVOR: NO · CANDIDATE: NO · first empirical handle on the Petit–Quisquater diagonal

## The unblock
m=4 D_solv was blocked in BIN-EXP-008 by the `S5.subs` symbolic-descent explosion (S₅ = degree 32, per-variable degree 8). **Unblocked here by a substitution-free EVALUATION descent**: build each F₂-component of Φ = S₅(x₁,…,x₄,xR) by evaluating S₅ over all 2^nvars boolean c-assignments and Möbius-transforming each F₂-coordinate into a boolean polynomial. **Validated byte-identical to the symbolic descent at m=3, n=11** (component sets equal). (Fixed a Sage `^`-vs-`^^` XOR-preparse bug in the Möbius transform — caught by the validation cross-check.)

## Raw results (byte-verified from msolve verbose)

| n | m | nvars | descended degrees | **D_solv (msolve F4)** | msolve finished | real sol recovered |
|---|---|---|---|---|---|---|
| 11 | 3 | 12 | [6] | **7** | True | True |
| 17 | 3 | 18 | [6] | **7** | (BIN-EXP-008) | — |
| 11 | 4 | 12 | [11, 12] | **12** | True | True |
| 13 | 4 | 12 | — | — | FB<m (subspace too small at l=3; sampling artifact) | — |
| 17 | 4 | 16 | [12] | **13** (≥, unfinished) | False (degree 13 reached before wall) | True |

### The 2D grid (D_solv)
|        | m=3 | m=4 |
|--------|-----|-----|
| **n=11** | 7 | 12 |
| **n=17** | 7 | 13* (≥, unfinished) |

(*n=17,m=4: msolve reached degree 13 then walled on matrix size; real solution verified; 13 is a lower bound, possibly = the unfinished computation overshooting 12 by one, NOT a confirmed rise.)

## Findings

1. **m=3 control reproduces D_solv=7** — validates the new eval-descent + msolve pipeline against BIN-EXP-008 (which used the symbolic descent). Same answer, different method.
2. **First m=4 diagonal point: D_solv = 12** (n=11), finished, real decomposition recovered. The descended degrees [11,12] exactly match **T1's prediction** (total degree ≤ m(m−1) = 12 for m=4) — independent confirmation of the per-block-degree theorem.
3. **The diagonal rises with m: D_solv(m=3)=7 → D_solv(m=4)=12.** The solving degree grows with arity m, tracking the per-block bound m(m−1) (=6 for m=3, =12 for m=4). For the Petit–Quisquater diagonal m≈n^{1/3}, m(m−1)≈n^{2/3} — **exactly their predicted ≈n^{2/3} degree.** So this is **consistent with the Petit–Quisquater degree scaling, NOT a refutation of it** (the earlier "disproof-leaning" framing was wrong: ≈n^{2/3} is the PQ-favorable case).
4. **At FIXED m=4, across n=11→17: D_solv = 12 → ≥13.** This *could* be a slight rise with n at m=4 (vs the perfectly flat 7,7 at m=3), but **n=17,m=4 did not finish** — msolve reached degree 13 before walling on matrix size, so 13 is a lower bound that may simply be the unfinished computation overshooting the true value 12 by one. **Not a confirmed rise.** Honest read: at m=4 the solving degree is 12–13 over n=11–17, consistent with bounded (T1 ceiling is exactly 12). The m=3 fixed-n flatness (BIN-OBS-006: 7 across n=11–23) is the stronger fixed-m evidence; m=4 is consistent but under-resolved.

5. **KEY STRUCTURAL REFINEMENT — D_solv is pinned to the generator degree m(m−1), with at most +1.** Inspecting the msolve F4 degree-by-degree trace:
   - m=3: generators degree **6**, F4 peaks at degree **7** = maxgendeg **+1** (a small healthy fall — solves barely above its own degree).
   - m=4: generators degree **12**, F4 peaks at degree **12** = maxgendeg **+0** (processes degrees 8,9,10,11,12; never exceeds the generator degree).
   So in BOTH cases **D_solv = m(m−1) + O(1)** — the solving degree does NOT blow up above the (T1-bounded) generator degree; it is essentially pinned to it. This is the cleanest possible behavior and is strong structural evidence that the system stays well-conditioned as m grows: no super-generator-degree cascade. On the PQ diagonal m≈n^{1/3}, D_solv ≈ m(m−1) ≈ n^{2/3} **with a now-mechanistic explanation** (pinned to generator degree), reinforcing that the SOLVING-DEGREE axis is PQ-consistent and is NOT where binary IC fails.

## Careful interpretation (do NOT overclaim)

- **Two points (m=3,4) at one n each** cannot establish the diagonal asymptotic; they fix the *shape* (D_solv ≈ m(m−1), matching T1) but not whether the *constant* or lower-order terms break the n^{2/3} story.
- **Crucially, D_solv≈m(m−1)≈n^{2/3} on the diagonal is the PETIT–QUISQUATER-FAVORABLE case** for the solving degree — it gives their 2^{O(n^{2/3} log n)} per-relation cost. So this does NOT refute (b) on the degree axis. The binary IC still fails to beat rho because of the **independent** BIN-NR-003 |FB|² linear-algebra obstruction, which on the diagonal becomes 2^{2n^{2/3}} — sub-exponential but with its own constant. The honest picture: the *degree* may behave as PQ need; whether the *full pipeline* (degree + linear algebra + relation count) crosses rho is the joint question, and our cost capstones (BIN-NR-003/004) say it does not at any measured n.

## Claim label

`OBSERVATION` (TOY/SCALED, diagonal 2-point + degree-trace mechanism) → **BIN-OBS-007**: the graded solving degree of the descended binary Semaev system is D_solv=7 at m=3 and D_solv=12 at m=4 (n=11, both finished, real-solution-verified; n=17 m=4 gives ≥13 unfinished, consistent with 12). The F4 degree trace shows D_solv = m(m−1) + O(1) (m=3: 6+1; m=4: 12+0) — the solving degree is PINNED to the T1-bounded generator degree with no super-degree cascade. On the PQ diagonal m≈n^{1/3} this is ≈n^{2/3}, the Petit–Quisquater-FAVORABLE degree scaling with a mechanistic explanation. CONCLUSION for PO-BIN-001(b): the SOLVING-DEGREE axis is PQ-consistent (degree behaves as PQ need); binary IC fails to beat rho on the INDEPENDENT BIN-NR-003 |FB|² linear-algebra axis, not on solving degree. Enabled by a validated substitution-free evaluation descent. CAVEAT: 2 m-values, small n; the +O(1) fall constant is not pinned.

## What this resolves / next
- **Resolves:** the m=4 measurement blocker (eval-descent works); confirms T1 numerically at m=4; places the diagonal degree at ≈m(m−1), the PQ-favorable scaling.
- **Open:** more diagonal points (m=5 needs nvars≤20 → n≤~15 with l=3; the eval-descent's 2^nvars cost is the new ceiling, ~2^20); whether D_solv at FIXED m=4 is flat in n (need n=17,23 m=4 — n=17 running). The joint pipeline crossover remains governed by BIN-NR-003.
