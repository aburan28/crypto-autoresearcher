# Protocol: the full isogeny volcano of a Koblitz curve, compared on equal terms

Frozen 2026-10-05, before any rho data for this study was collected. It
extends `../isogeny_rho_study` (the earlier run, whose 8 curves were all on
the 73-floor) to every level of the isogeny class.

## Object
Koblitz curve E0: y^2 + xy = x^3 + 1 over F_2^37 (modulus x^37+x^9+x^2+x+1).
#E = 4 * 149 * l, l = 230603167. Frobenius pi = tau^37, trace -534059.
[O_K : Z[pi]] = 73 * 2663, K = Q(sqrt(-7)), h(O_K) = 1; both 73 and 2663 are
inert in K. The isogeny class with a2 = 0 is therefore a product of two
depth-1 volcanoes, with 199,875 curves:

| level      | conductor of End | curves  |
|------------|------------------|---------|
| crater     | 1                | 1       |
| floor-73   | 73               | 74      |
| floor-2663 | 2663             | 2,664   |
| bottom     | 194399           | 197,136 |

## Finding and classifying curves
- floor-73: all 74 curves, by explicit 73-isogenies from E0 (`floor73.gp`).
- floor-2663 and bottom: random b in F_2^37, sieved in C by [N]P = O for two
  random points (`search.c`), then re-verified with PARI `ellcard`
  (`#E_b = N` exactly).
- Level test (exact): 73 | [End E : Z[pi]] iff pi is a scalar on E[73] iff
  E(F_q^18)[73^inf] = (Z/73)^2 (otherwise it is Z/73^2). A curve with that
  property other than E0 is on floor-2663; one without it is on floor-73 (if
  it is in the enumerated set) or at the bottom.
- Independent check: the length of the horizontal 11-isogeny cycle through
  the curve (11 splits in K) must equal the order of [l_11] in Cl(End E):
  1, 74, 2664, 2664 for the four levels. This check is run on every floor-2663
  hit and on every sampled bottom and floor-73 curve.

## Rho sample (selection rule fixed now)
- crater: E0, n = 5000 with negation only and n = 5000 with negation plus
  Frobenius.
- floor-73: all 74 curves, n = 1000 each.
- floor-2663: every distinct hit from the scan (whole scan; no stopping on
  results), n = 1000 each.
- bottom: 30 curves from distinct Galois orbits, the first 30 classified hits
  in ascending b with a distinct orbit, n = 1000 each.
Every non-crater curve runs with negation only. That is the full automorphism
group of every curve in the class (ordinary, j != 0). The solver refuses
Frobenius mode on any curve where the Frobenius eigenvalue check fails.

Solver: `rho.c` from the earlier study, unchanged (sha256 recorded in
`PROTOCOL.sha256`). Solves run on 4 pinned cores with a shuffled job order,
so level is not tied to core or time. Per-step cost: separate pinned,
sequential benchmark, 5 reps of 2^20 steps per curve, shuffled order.

## Traits computed per curve
level; conductor f; disc(End) = -7 f^2; h(End); j, b; #E; group structure;
Galois-orbit size; rational 73- and 2663-isogeny counts and directions;
smallest isogeny degree to the crater; smallest k with tau^k in End(E);
minimal degree of a non-integer endomorphism; for each k | l-1 with k <= 1000,
the minimal degree of an endomorphism acting on <P> as a primitive k-th
root of unity (this is what an equivalence-class speedup of size k requires);
GHS magic number m(b) and descent genus; 11-cycle length (measured).
Class invariants are reported once: embedding degree, twist order,
anomalous check.

## Pre-declared analysis (alpha = 0.05)
0. 100% verified solutions per curve, or that curve is invalid.
1. H1: is any curve faster than crater + Frobenius? One-sided Mann-Whitney
   per curve (ops and seconds), Holm over all curves.
2. H2: does level change rho cost with negation only? Kruskal-Wallis over the
   4 levels (pooled solves) for ops and seconds; one-way ANOVA on per-curve
   mean ops (curve as unit); TOST of each level vs the crater with negation
   only, ratio of means, margin +-3% (90% bootstrap CI).
3. Within-level heterogeneity: Kruskal-Wallis across curves inside each level.
4. Per-step ns: Kruskal-Wallis across levels; TOST +-3% vs crater (negation
   only).
5. Trait association: Spearman correlation of per-curve mean ops with
   conductor, GHS m, and orbit-k endomorphism degree (descriptive).

## Scope
m = 37, this solver, this machine. Transfer to ECC2K-130 (m = 131, conductor
263 * 146505763881528721) rests on the algebra, which is identical in form.
