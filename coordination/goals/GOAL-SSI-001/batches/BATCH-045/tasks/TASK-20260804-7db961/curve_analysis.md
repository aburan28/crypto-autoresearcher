# Orientation Lane Structural Analysis: Curves with Known End(E)

**Task**: TASK-20260804-7db961 (GOAL-SSI-001 / BATCH-045, Lane A)

## Core finding

The orientation lane for classical endomorphism-ring/path-finding is **closed**
by a structural argument (the Deuring-correspondence dichotomy):

> For any supersingular E where an O-orientation is publicly available without
> solving EndRing(E), either (i) End(E) is fully known (making EndRing trivial
> via KLPT), or (ii) the hard residual problem is class-group-action
> vectorization (a different problem with its own specialized attacks).

There is no intermediate regime where "orientation helps path-finding but
path-finding remains hard."

## Classification of curves with known End(E)

| Class | Curves | Count | End known why | Attack relevance |
|-------|--------|-------|---------------|------------------|
| j=0 | p≡2 mod 3 | 1 | Aut(E)=Z/6Z | None (KLPT trivializes) |
| j=1728 | p≡3 mod 4 | 1 | Aut(E)=Z/4Z | None (KLPT trivializes) |
| CM reductions | small |D| | O(polylog(p)) | CM theory | None (KLPT trivializes) |
| Recorded walks | secret | exponential | Path IS solution | Circular (prover's knowledge) |
| CSIDH keys | partial | ~√p | Construction | Different hard problem |

Fraction with publicly known full End: O(polylog(p)/p) → 0 (measure-zero).

## Density: measure-zero

At cryptographic primes (256+ bits), only ~2 + a few thousand curves (out of
~p/12 ≈ 2^252) have publicly known full endomorphism rings. This is effectively
zero density.

## Why SSI-O2 cannot work

**Trilemma**: SSI-O2 ("endomorphism-assisted meet-in-the-middle") requires
publicly known endomorphism information as uncharged preprocessing. But:

- Where End is known: problem is already trivial (KLPT poly-time)
- Where partial orientation exists: different hard problem (CSIDH vectorization)
- Where neither: cannot instantiate the method

**Comparison with Wesolowski 2026**: Achieves p^{1/3+o(1)} on ALL curves without
requiring orientation. Strictly dominates SSI-O2 on the time axis.

## RT-CTRL-002/003 resolution

- **RT-CTRL-002** (uncharged preprocessing): Validated. The uncharged "endomorphism
  computation" either costs nothing (at special curves where problem is trivial)
  or costs ≥ p^{1/3+o(1)} (at generic curves, i.e., solving the target problem).
- **RT-CTRL-003** (Pareto honesty): Validated. SSI-O2 dominated_by =
  [Wesolowski-2026, Kuperberg-2011, VW-p^{1/2}]. Not on frontier on any axis.

## Lane status: CLOSED

Named obstruction: Deuring-correspondence dichotomy.
This is a structural closure (not search exhaustion or fatigue).
