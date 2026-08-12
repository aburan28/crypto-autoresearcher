# Experiment Contract: PO-transfer-004 Plucker Incidence Compression Gate

## Candidate

Candidate: batch BNIT's target-plus-four-point co-cubic condition as a finite
projective incidence problem, then test whether its structured pair set admits a
rank-producing search materially below explicit cubic tuple enumeration.

Status before execution: `HYPOTHESIS / UNTESTED / MODEL-BOUND`.

Novelty status: `OPEN`.  The Plucker reformulation is classical geometry; a
cryptanalytic gain would require a new incidence algorithm or a measurable
non-random bias in this specific cover/factor-base family.

## Formalization

For a cover point `P=(x,y)`, define

```text
m(P) = (1,x,x^2,x^3,y) in F_p^5.
```

For a fixed target lift `T`, target plus four factor-base lifts
`P1,P2,P3,P4` lie on one cubic `v(x)` exactly when the five rows

```text
m(T), m(P1), m(P2), m(P3), m(P4)
```

are linearly dependent.  Quotient by `<m(T)>` to obtain four vectors `w_i` in
a four-dimensional space `W_T`.  The condition is

```text
(w1 wedge w2) wedge (w3 wedge w4) = 0 in Lambda^4(W_T).
```

Equivalently, the two Plucker points in `Lambda^2(W_T)` are orthogonal under
the natural split bilinear form.  A hit gives one-large-prime BNIT partial:
the target and four factor-base points determine a cubic with one remaining
intersection point.

## Hypothesis

The Plucker vectors arising from liftable points on the bielliptic cover have
enough algebraic concentration, repeated subspaces, or rank bias that
target-coupled co-cubic incidences can be found with fewer than `B^3` kernels
and with rank gained per charged operation improving across size.

## Null Hypothesis

The pair bivectors behave like a random subset of the Klein quadric.  Testing
orthogonality is not an equality hash, naive pair-pair search costs `B^4`, and
even an ideal `B^2` incidence oracle needs `B about p^(1/3)` to supply `B`
relations, giving a `p^(2/3)` pair-table barrier above rho.

## Parameters

- field/curve family: the four frozen BNIT cells plus at least one fresh
  generated cell per size class;
- seeds: frozen BNIT seeds for replay; fresh seeds pre-registered before run;
- factor base: BNIT liftable canonical points, swept over at least three `B`
  values per field;
- target lifts: the same public `-lambda*Q` rule;
- relation shape: one-large-prime co-cubic incidence, followed by public
  large-prime cancellation and online rank;
- baseline: rho, BSGS, BNIT `003c/003d`, explicit `B^3` interpolation, random
  projective points of equal cardinality, and planted co-cubic incidences.

## Model Of Computation

- Construct quotient vectors and normalized Plucker coordinates publicly.
- Charge all pair construction, normalization, lookup/query, candidate replay,
  false positives, cache entries, rank tests, and target descent.
- Do not count an orthogonality query as an equality lookup unless a concrete
  data structure proves that cost.
- Do not use fixture scalars, factor-base logs, accepted-row labels, or hidden
  rank gain in pair selection.

## Metrics

- factor-base points and lift multiplicity;
- pair bivectors, unique normalized bivectors, and repeated 2-planes;
- orthogonal incidences and nontrivial disjoint-index incidences;
- planted recall and random-control precision;
- public relation replay rate;
- target rows, rank, target recovery;
- pair construction/query/verification operations;
- field-operation proxy and wall-clock time;
- peak memory entries;
- charged operations / rho and / BNIT;
- empirical exponents for pairs, incidences, attempts/rank, and memory;
- incidence excess over a matched random Klein-quadric control.

## Positive Control

Plant cubics through one target lift and four factor-base lifts.  The Plucker
predicate must recover every planted disjoint-index incidence, and the resulting
partial row must replay with its residual large prime.

## Negative Control

Use matched random vectors in `W_T`, random decomposable bivectors on the Klein
quadric, and sign/coordinate-scrambled cover points.  False incidence and rank
rates must match the declared finite-field model.

## Success Criterion

Structural success requires all of:

- public target-coupled rows and full-rank target recovery on at least three
  sizes;
- a concrete incidence data structure with measured query cost, not an oracle;
- at least `16x` fewer charged relation kernels per rank than BNIT `003c` on the
  shared anchor;
- memory below `4*sqrt(n)`;
- incidence/rank excess over matched random controls that persists on fresh
  cells.

Algorithmic success additionally requires charged cost below rho on one size
and a fitted trend at or below exponent `0.5`.  Beating explicit `B^3` alone is
not enough.

## Falsification Criterion

Narrow the Plucker lane if any of these holds across the sweep:

- normalized bivectors and incidences match random controls;
- orthogonality lookup requires pair-pair work or a table above the memory gate;
- the idealized relation supply requires `B about p^(1/3)` with `B^2` work;
- target rows remain rank-deficient;
- full recovery stays above BNIT or rho after all costs are charged.

This would not rule out other incidence embeddings, residual-norm sieves,
non-quadratic split correspondences, or structure outside BNIT.

## Proof Track

- Prove the determinant/Plucker equivalence with index-disjointness conditions.
- Derive the exact bilinear form in the chosen quotient basis.
- Count expected incidences for random projective points and random
  decomposable bivectors.
- Prove or disprove whether the BNIT point set lies in exceptional subvarieties
  that change incidence multiplicity.
- Establish a real data-structure cost for orthogonality queries.

## Disproof Track

- Compare against random points and randomized y signs.
- Remove shared-index and involution-paired trivial incidences.
- Check whether all excess hits are duplicate cubics or dependent rows.
- Compute the ideal-oracle lower envelope and compare it with rho before
  implementing an expensive query engine.

## First Experiment

Implement only the compression gate:

1. reconstruct the four BNIT public cells;
2. enumerate factor-base lift pair bivectors;
3. measure uniqueness, repeated planes, and all nontrivial orthogonal incidences
   at toy scale;
4. compare with random and planted controls;
5. replay incidences as one-large-prime rows and measure rank;
6. stop before claiming an algorithm if no concrete sub-pair-pair query method
   is identified.

## Planned Reproduction Command

```bash
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_004_plucker_incidence_gate.sage \
  --out experiments/ecdlp_isogeny/po_transfer_004_result.json
```

## Results

Status after execution: `NEGATIVE RESULT / TOY-EVIDENCE / MODEL-BOUND`.

- The exact determinant/Plucker equivalence and all planted divisor replays
  passed on eight base cells.
- The 24-configuration frozen/fresh sweep exported 1,603 final public rows.
  An independent verifier replayed 2,973 primitive cubic witnesses, every
  large-prime cancellation, every incidence counter, all 500 target-matched
  random controls, and every matrix rank.  Fresh targets are deterministic
  public points with no fixture discrete logarithm constructed or consumed.
- Base-cell incidence ratios were `0.927..1.110` versus the exact random
  Klein-quadric rate and `0.886..1.150` versus matched controls.  Every
  normalized pair plane was unique; no persistent structural excess appeared.
- Charged brute work was `8652.33..115587.62x` rho on the contracted base
  cells.  The unimplemented oracle floor was still `132.67..451.81x` rho.
- Base-cell memory was `68.3..200.6 sqrt(n)`, above the `4 sqrt(n)` gate.
- At the shared frozen `p=4099`, `B=16` anchor, charged work was `208.25x`
  the BNIT `003c` kernel count.  The oracle floor improved that kernel count by
  only `1.58x`, not `16x`, and rank was `10/16`.
- The charged toy exponent was `0.958`; the oracle-floor toy exponent was
  `0.561`.  Neither supports an exponent at or below `0.5`.

The experiment gate is `success=false`.  This narrows the explicit BNIT
Plucker-pair lane; it does not rule out other correspondences or representations
that give the target a larger family of useful preimages.

Detailed interpretation and reproduction evidence are in
`experiments/ecdlp_isogeny/po_transfer_004_result.md` and
`experiments/ecdlp_isogeny/po_transfer_004_verify.json`.
