# DRAFT — Why index calculus still can't touch binary elliptic curves (and where it might)

*Isogeny Labs blog draft, 2026-09-28. Not for publication until the checklist
at the end is done. Every number cites a record in this repository. The
literature position is in `docs/ecdlp-literature-review-20260926.md` §5
(items I2 and I3).*

## The promise

For finite fields, index calculus gives subexponential discrete logarithms.
Since Semaev (2004) there has been hope for elliptic curves too, via
summation polynomials: decompose a random point as a sum of points from a
small factor base, collect relations, and solve a linear system. For
curves over F_{2^n} with n prime, the best-known heuristic analyses
(Petit–Quisquater 2012; Semaev 2015; Nagao 2015) claim subexponential time.
Those analyses rest on a *first fall degree assumption* about the
Weil-descended polynomial systems. Semaev 2015 goes further: it declares the
NIST curves K/B-409 and K/B-571 "theoretically broken".

We asked a narrower, concrete question. For the binary curves people
actually use or benchmark, what would each step cost, measured in the same
units as Pollard rho?

## Finding 1: below about 300 bits, you can't even write the equations down

To decompose a point you Weil-descend a summation polynomial to F_2 and get
a Boolean system. Before any solver runs, that system has to exist in
memory.

We measured the descended algebraic normal form. Its Boolean degree is
exactly m·min(m−1, ℓ) on all 14 measured cells, and it is dense (0.27–0.87
of the dense bound). We then compared the cost of merely writing it down
against the entire Pollard rho budget for the curve, at the best viable
decomposition arity:

| curve (n) | ANF size minus whole rho budget |
|---|---:|
| 113 | +24.2 bits |
| 127 | +25.6 bits |
| ECC2K-130 (131) | +40.8 bits |
| K-163 | +37.4 bits |
| 233 | +6.3 bits |
| K/B-283 | +18.8 bits |
| K/B-409 | **−4.9 bits** |

(EV-ICPERF-784b25, strength *moderate*.)

For every curve up to n = 283, writing the decomposition system costs more
than solving the whole ECDLP with rho. The sign flips between 283 and 409.
That is the first place index calculus is not ruled out before the solver
starts.

The existing literature says this only qualitatively ("too many variables";
experiments "limited more by the memory requirements"). We did not find a
per-curve bound.

## Finding 2: ECC2K-130 needs a decomposition oracle that is nearly free

On the ECC2K-130 Koblitz curve we can price the whole pipeline around an
idealized decomposition oracle. The number of oracle calls needed is fixed
by arithmetic, not by how clever the oracle is (KN-FIND-aa2efc):

- Decomposing into m = 3 points costs **2^68.58** calls even with a free
  oracle, against rho's **2^60.81**. It loses before the oracle does any
  work.
- At m = 4 the free-oracle floor is 2^56.40, so there is at most **2^4.41**
  of headroom. An oracle would have to decompose a point in about 20 group
  operations. Every oracle we built costs far more.

## Finding 3: charge memory, and Semaev 2015 no longer breaks K-409

Semaev 2015 compares running time only, and finds his algorithm below rho
for n > 310. Van Oorschot–Wiener collision search, however, gets to trade
memory for time. Charging both algorithms coherently for memory moves the
crossover by +85 in n (−29.0 bits at n = 409). The crossovers land at
**n = 460 (sparse storage) and n = 520 (dense storage)**, both above 409
(EV-SEMBIN-4125ec, strength *moderate*). This result is still conditional on
Semaev's degree assumption, which is itself disputed.

## What this does and doesn't say

- **It does not prove binary index calculus is exponential.** It shows
  where the known pipelines lose, in concrete units, on concrete curves.
- **It points at where the question is actually open:** n ≥ 409, at
  decomposition arity m ≥ 4, where the remaining problem is to solve a
  degree-12 Boolean system in about 392 variables within 2^79.3 operations.
- **Every deployed binary curve up to 283 bits is protected by a margin
  that does not depend on any Gröbner-basis heuristic.**

## Checklist before publishing

- [ ] Independent replication of EXP-SEMBIN-992e73's per-curve table (the
      Semaev 2015 row numbers are not yet approved; this post quotes only
      the crossovers from EV-SEMBIN-4125ec).
- [ ] State the dense-ANF charge and the linear-algebra cap (ℓ ≲ n/4 +
      log₂(R)/2) up front, in a box. Finding 1 is conditional on both.
- [ ] Human expert read of Findings 1–3, including one reader from the
      Gröbner-basis community.
- [ ] Cite Petit–Quisquater 2012, Semaev 2015, Galbraith–Gebregiyorgis
      2014, Shantz–Teske 2013, Huang–Kosters–Yeo 2015 and the Galbraith–Gaudry
      2016 survey.
