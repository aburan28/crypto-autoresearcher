# Orbit-aware relation generation for Koblitz ECDLP

Status: speculative research agenda. No attack, speedup, or sub-square-root claim.

## Core hypothesis

Known Frobenius index-calculus work mostly exploits orbit collapse after a decomposition is found. The more interesting question is whether the *decomposition search itself* can be parameterized modulo Frobenius.

Write a factor-base point as

\[
P = \pi^j(P_{\mathrm{rep}}),
\]

where `P_rep` is a canonical representative of a Frobenius orbit and `j` is a small orbit index. Then solve directly for representatives plus relative Frobenius shifts rather than unconstrained raw coordinates.

For a k-term decomposition

\[
Q = \sum_{i=1}^k \pi^{j_i}(R_i),
\]

the solver should exploit the cyclic action before or during relation generation.

## IDEA-ORB-GAUGE: quotient the global Frobenius symmetry

A simultaneous shift

\[
(j_1,\ldots,j_k) \mapsto (j_1+c,\ldots,j_k+c)
\]

is a global Frobenius action. Gauge-fix it by setting `j_1 = 0` and solve only relative shifts

\[
\delta_i = j_i-j_1 \pmod m.
\]

This is low-risk and should be the first experiment because it removes an exact m-fold symmetry without changing the mathematical solution set.

Questions:
- How much SAT/Groebner search is eliminated?
- Does the canonicalization interact badly with permutation symmetry?
- Does the gain persist as m grows?

## IDEA-ORB-CANON: canonical orbit representatives in the solver

Constrain each representative to a fundamental domain of the Frobenius action, then carry a compact shift variable.

Candidate canonicalization rules:
- lexicographically minimal normal-basis rotation;
- minimum integer encoding among rotations;
- minimum rotation under a cheaper prefix signature plus exact tie-break;
- run-length / necklace canonicalization.

The criterion is solver cost, not aesthetic simplicity. A mathematically clean representative is a failure if enforcing canonicality costs more than the symmetry it removes.

## IDEA-ORB-ROTATE: variable-rotation Semaev/SAT circuits

In a normal basis, Frobenius is a cyclic bit rotation. Encode

`x_i = ROTATE(r_i, j_i)`

and feed the rotated coordinates into the chained S3 system. Reuse one representative circuit while a cyclic selector chooses the shift.

Potential wins:
- squaring remains a free/permutation operation;
- repeated shifted constraints may share structure;
- the same representative variables serve all orbit positions;
- symmetry-related assignments disappear from the raw search region.

Main risk: a variable barrel-rotation / multiplexer network may cost more clauses and propagation depth than it saves.

## IDEA-ORB-REL: solve for relative offsets first

For each tuple of orbit representatives, treat only the relative offsets as discrete variables:

\[
Q = R_1 + \pi^{\delta_2}(R_2)+\cdots+\pi^{\delta_k}(R_k).
\]

Search or rank offset vectors before invoking the expensive full solver.

Possible implementations:
- exhaustive offsets for toy m;
- branch-and-bound over relative offsets;
- SAT assumptions on offset bits;
- learned or Bayesian ranking of offset vectors, always followed by exact verification.

## IDEA-ORB-INVAR: cheap cyclic-invariant prefilters

Construct inexpensive invariants that are unchanged or equivariant under Frobenius rotation and use them to reject impossible relative shifts before full Semaev solving.

Candidate features:
- absolute trace;
- low-order trace correlations such as `Tr(x * pi^d(y))`;
- cyclic autocorrelation spectra of normal-basis bit vectors;
- Hamming-weight and run-structure signatures;
- low-degree symmetric functions over selected orbit coordinates.

The experiment must measure *rejection rate per unit cost*. A prefilter is useful only if false negatives are zero and saved solver time dominates filter overhead.

## IDEA-ORB-PAIR: pair-interaction tables indexed by relative shift

For two orbit representatives `R_a, R_b`, precompute or cheaply estimate properties of

\[
R_a + \pi^d(R_b)
\]

for `d in Z/mZ`. Only relative shift matters, reducing an m^2 pair-position space to m cases.

Potential uses:
- rank offsets likely to extend to k-term decompositions;
- precompute partial S3 compatibility scores;
- cache repeated pair states across targets;
- detect offset classes that are systematically poor.

## IDEA-ORB-MITM: orbit-aware meet-in-the-middle

For k=4, split

\[
Q = (\pi^{j_1}R_1+\pi^{j_2}R_2) + (\pi^{j_3}R_3+\pi^{j_4}R_4).
\]

Canonicalize each two-point sum under global Frobenius before inserting it into a table. Compare against a raw MITM baseline.

Measure:
- table-size reduction;
- duplicate suppression;
- canonicalization cost;
- lookup throughput;
- successful decomposition rate;
- scaling exponent.

This provides an algorithmically different control against SAT/Groebner approaches.

## IDEA-ORB-BURNSIDE: theoretical symmetry ceiling

Before implementing expensive quotient encodings, compute the maximum search-space reduction available from the action of

\[
C_m \times S_k.
\]

Use Burnside's lemma / orbit counting to estimate expected tuple-orbit sizes and exceptional stabilizers. Compare measured solver speedup against this theoretical ceiling.

This prevents over-interpreting tiny practical gains where much larger symmetry is nominally available.

## IDEA-ORB-FOURIER: diagonalize the cyclic action

High-risk representation experiment: move from normal-basis coordinates to a representation adapted to the cyclic Frobenius operator. A cyclic shift operator is diagonalizable after adjoining suitable roots of unity, so repeated Frobenius application may become multiplication by eigenvalues rather than rotation.

Questions:
- Do Semaev constraints acquire block/circulant structure?
- Can elimination split into smaller frequency blocks?
- Does extension-field overhead erase all benefit?

For m=131 in characteristic 2, this may require an inconvenient extension. Treat it as an exploratory representation experiment, not a presumed optimization.

## IDEA-ORB-SLOPE: exponent-first evaluation

Every experiment must report not only constant-factor speedup but the slope of

\[
\log_2 T(m)
\]

across a preregistered toy scaling ladder.

The most important signal is whether orbit-aware relation generation changes the apparent exponent of decomposition cost. A 131x constant-factor gain at m=131 is useful engineering but not an asymptotic break if the decomposition stage still scales as `2^(c*m)` with unchanged c.

## Priority order

1. Global gauge fixing (`j_1=0`).
2. Canonical representative + compact shift encoding.
3. Variable-rotation normal-basis S3/SAT circuit.
4. Cyclic-invariant prefilters for relative shifts.
5. Orbit-aware MITM baseline.
6. Pair-interaction tables.
7. Burnside accounting as a theoretical calibration layer.
8. Fourier/eigenbasis representation as the exotic track.

## Required metrics

All experiments should record:

- factor-base size and orbit count;
- number of solver variables/clauses or polynomial variables/degree proxy;
- solve time per target and per successful decomposition;
- decomposition success probability;
- relation independence/rank contribution;
- canonicalization and preprocessing cost;
- memory footprint;
- total compute per independent usable relation;
- fitted slope of `log2(time)` versus m;
- projected end-to-end cost versus the best applicable Pollard-rho baseline.

## Claim boundary

Whole-relation Frobenius shifts usually yield dependent relations. Orbit-aware solving is valuable only if it reduces the cost of *finding independent relations* or changes decomposition scaling. Nominal symmetry reduction, clause reduction, or smaller matrices alone are not evidence of an ECDLP speedup.
