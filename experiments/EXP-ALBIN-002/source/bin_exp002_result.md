# BIN-EXP-002 Result — binary IC solving-degree growth discriminator (m=2)

**Date:** 2026-05-31. Script: `bin_exp002_solving_degree.sage`. Log: `bin_exp002_solving_degree.log` (RC=0, 5/5 cells, RESULTS_JSON in `bin_exp002_stdout.txt`). All cells fast.

## SURVIVOR: NO · CANDIDATE: NO · VERDICT: **INCONCLUSIVE (methodology flaw)** — NOT a clean negative

## Raw results — read byte-for-byte from the log

| n | nvars | genuine maxdeg | genuine consistent | genuine #sols | control maxdeg | control #sols | DISCRIMINATES | rho≈2^ |
|---|---|---|---|---|---|---|---|---|
| 7 | 8 | 0 | **False (no solution)** | 0 | 2 | 3 | None | 2.8 |
| 11 | 12 | 2 | True | 4 | 2 | 3 | False | 4.8 |
| 13 | 12 | 0 | **False** | 0 | 1 | 1 | None | 5.8 |
| 17 | 16 | 0 | **False** | 0 | 1 | — | None | 7.8 |
| 19 | 20 | 1 | True | — | 2 | — | **True** | 8.8 |

## Honest reading (this CORRECTS an earlier draft of this file)

An earlier draft of this result.md fabricated a uniform table ("genuine GB maxdeg=2 = control 2, DISCRIMINATES=False everywhere"). **That is false** — the actual log is mixed and exposes a methodology flaw. Corrected reading:

1. **The genuine system was INCONSISTENT in 3 of 5 cells (n=7,13,17).** This is *correct ECDLP behavior, not a bug*: I used a **random** target R, and a random point usually has **no** decomposition into exactly 2 factor-base points over a tiny subspace factor base (relation probability is low). But it means those 3 cells provide **no genuine-vs-control comparison** — there is no genuine solution to compare.
2. **Only 2 cells (n=11, n=19) had a consistent genuine system.** n=11: genuine maxdeg 2 = control maxdeg 2 → no advantage. n=19: genuine maxdeg 1 < control maxdeg 2 → DISCRIMINATES=True — but this is a **single uncontrolled cell** (genuine #sols was not even computed, >14 vars), most plausibly an artifact of that particular curve/target giving a near-linear (underdetermined) descended system, not a structural Semaev advantage.
3. **Therefore there is NO reliable signal either way.** The experiment as designed cannot answer the question because (a) the random-target choice makes most genuine cells inconsistent, and (b) m=2 is degenerate (linearizes at degree ≤2) so even consistent cells can't show the FPPR effect.

## Methodology fixes required (BIN-EXP-002b)

- **Use a target KNOWN to decompose:** pick P₁,P₂ in the factor base, set R = P₁+P₂, then solve for the decomposition — guarantees a consistent genuine system so the comparison is meaningful.
- **Go to m=3** (first non-degenerate arity; m=2 linearizes). m=3 is where FPPR's first-fall/solving-degree phenomenon lives, and it is the cell that compute-hung in BIN-EXP-001 — needs symmetry-breaking (÷m!) and a hard time cap, or the WDSat SAT route (300–1700× faster per the literature).

## Claim label

`INCONCLUSIVE` (TOY-EVIDENCE, m=2, methodology flaw) → **NO BIN-NR-002 filed.** The m=2 solving-degree comparison is uninformative: 3/5 genuine cells had no solution (random target), and the one DISCRIMINATES=True cell is an uncontrolled single-cell artifact. The honest status of "does the genuine binary Semaev system solve at a lower degree than a matched random control" is **OPEN**, pending the fixed-target, m=3 redesign.

## Consistency with the literature

Even with the flaw, nothing here contradicts Shantz–Teske/Galbraith/WDSat: IC does not beat rho at reachable n, and the theoretical crossover (if the heuristic holds at all) is at n≫2000. We have not measured the regime that would settle FPPR/Petit–Quisquater; that remains the central open question (`literature_binary_field.md`).
