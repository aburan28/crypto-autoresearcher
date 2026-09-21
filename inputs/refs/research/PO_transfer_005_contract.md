# Experiment Contract: PO-transfer-005 Trace-Quotient Algebraic Decomposition

## Candidate

Candidate: lift an ordinary prime-field curve into `E(F_{p^m})`, express the
original target as a trace-kernel coset, and use the Weil-restricted extension
coordinates to solve for structured factor-base tuples faster than direct
search on their pushed-forward traces.

Status before execution: `HYPOTHESIS / UNTESTED / MODEL-BOUND`.

Novelty status: `OPEN`.  Weil descent, small-dimensional abelian-variety index
calculus, trace-zero attacks, cover attacks, summation polynomials, and
prime-field rational-map factor bases are established neighboring work.  No
algorithmic novelty or speedup is claimed before literature comparison,
implementation, public replay, and baseline gates pass.

## Hard Goal

Find a public, reusable factor base `S subset E(F_{p^m})` and a concrete
Weil-restricted algebraic solver such that target-valid tuples are found more
cheaply in extension coordinates than by direct weighted `k`-sum search on
`Tr_m(S)`, while producing rank-diverse relations that recover the original
blind target in `E(F_p)` below Pollard rho.

This is harder than asking whether a target has many trace preimages.  The
preimages are free only set-theoretically; the experiment must exhibit and
charge an algorithmic advantage.

## Formalization

Let `E/F_p` be ordinary with a large prime-order subgroup `G=<P>` of order
`ell`.  For `m in {2,3}`, let

```text
H = E(F_{p^m})
Tr_m(R) = R + Frob_p(R) + ... + Frob_p^(m-1)(R).
```

Use `G` as the codomain after restricting/projecting the trace image.  Require
`gcd(m,ell)=1`.  A public section on `G` is

```text
s(Q) = [m^(-1) mod ell] Q,
```

because `Tr_m(s(Q))=[m]s(Q)=Q` for rational points.  The target fiber is

```text
C_Q = s(Q) + ker(Tr_m).
```

For a public extension factor-base multiset `S`, define the pushed-forward
multiset `A=Tr_m(S)` with multiplicity

```text
mu_A(g) = #{R in S : Tr_m(R)=g}.
```

The relation system is built only after merging columns with equal trace
images.  Kernel-only differences do not count as original-group rank.

## Restricted Theorem: Trace-Quotient Collapse

Let `tau:H->G` be any homomorphism of finite abelian groups.  For every ordered
tuple `(R_1,...,R_k) in S^k`,

```text
R_1+...+R_k in tau^(-1)(Q)
iff tau(R_1)+...+tau(R_k)=Q.
```

Therefore

```text
N_H(Q;k,S) = [Q](mu_A convolved k times).
```

The lifted relation probability is exactly the weighted `k`-sum probability
of the pushed-forward multiset.  Full kernel fibers multiply successful and
total tuples equally.  Repeated trace images create duplicate columns, not new
base-group rank.

Consequence: `trace-coset multiplicity alone improves decomposition` is false
in this model.  The only open loophole is solver time: extension/Weil
coordinates may expose low-degree, multihomogeneous, trace/norm, sparse, or
first-fall structure that finds the same image-valid tuples faster than the
pushed-forward baseline.

## Hypothesis

For at least one public algebraic factor base over `F_{p^2}` or `F_{p^3}`, the
Weil-restricted trace-fiber equations have sufficiently low degree, sparse
elimination, or favorable multihomogeneous structure that cost per new
image-deduplicated rank row is less than half the direct pushed-forward
baseline and remains below `0.8` Pollard-rho cost on three increasing toy
sizes.

## Null Hypothesis

After trace-image deduplication:

- lifted and weighted pushed-forward hit counts agree exactly;
- raw lifted rows collapse to duplicate or rank-poor image rows;
- the algebraic solver has no degree/regularity or charged-cost advantage over
  direct MITM or summation-polynomial solving on `Tr_m(S)`;
- extension arithmetic, trace computation, and target descent dominate any
  apparent relation gain.

## Parameters

- field sizes: preregister `p in {1019,4093,16381}` after primality check;
- curve family: random ordinary, nonsupersingular, nonanomalous curves with a
  large prime subgroup; exclude MOV-small, subfield/Koblitz, and known
  cover-special controls from the main cells;
- extension degrees: `m in {2,3}`;
- curve seeds: `20260730,20260731,20260801`;
- target rule: deterministic public point outside the factor-base image; never
  construct or consume its discrete logarithm;
- tuple arities: `k in {2,3}` for the collapse audit, then the smallest arity
  supported by a concrete algebraic solver;
- factor-base sizes: at least three public sizes per `(p,m)` cell;
- factor bases of equal cardinality:
  1. `WEIL-SUBSPACE`: extension `x` coordinates in a fixed public affine
     coefficient subspace or low-degree rational image;
  2. `RATIONAL-MAP`: a fixed public rational-map predicate;
  3. `RANDOM-MATCHED`: public random extension points matched for size and
     trace-image multiplicity;
- baselines: rho, parallel/VW rho accounting, BSGS/MITM on `G`, direct weighted
  `k`-sum on `A`, Semaev/rational-map decomposition where available, and the
  nearest small-extension Weil-restriction solver.

## Algebraic Solver Obligation

The experiment must instantiate an actual system, not an oracle.  For each
factor-base element representation, write extension coordinates in a fixed
`F_p` basis, expand EC addition and trace constraints over `F_p`, and record:

- variables and equations by multidegree;
- field equations and denominator exclusions;
- degree of regularity, first fall, last fall if measurable;
- Groebner/SAT/crossbred/hybrid operations;
- number of solutions and false/duplicate solutions;
- conversion of every solution to a public extension tuple and trace row.

The direct pushed-forward baseline receives the same tuple arity, multiplicity
weights, target schedule, and stopping rule.

## Metrics

- `collapse_mismatch_count` between lifted-coset and weighted-image predicates;
- lifted factor-base size, trace-image support size, and fiber histogram;
- duplicate trace rate and image entropy;
- lifted tuple hits, unique pushed rows, and exact weighted expectation;
- raw lifted rank, image-deduplicated rank, target-column rank, and rank gain per
  accepted row;
- kernel samples, Frobenius maps, trace maps, extension additions and
  multiplications in base-field equivalents;
- solver degree/regularity and wall time;
- direct pushed-forward MITM/Semaev operations;
- memory entries and bytes;
- sparse linear algebra and individual-log/target-descent cost;
- charged cost per new image-rank row divided by rho and pushed-forward cost;
- exponent fits over at least three sizes.

## Positive Controls

- Plant public extension tuples whose trace sum is a blind control target; both
  lifted and pushed-forward paths must recover the same row.
- Use a small special extension-field/trace-zero case where known Weil or
  summation structure should lower solver degree; it is a control, not evidence
  for the ordinary prime-field claim.
- Check the public section `Tr_m(s(Q))=Q` and generate kernel points only via
  public `K=U-s(Tr_m(U))`.

## Negative Controls

- Random matched `S` with the same trace-image multiplicity histogram.
- Permute extension coordinate bases while preserving the same image multiset.
- Replace structured equations by random systems of matched variable/degree
  profile.
- Merge all duplicate trace columns before rank and compare with the unmerged
  raw rank report.
- Wrong-coset, wrong-trace, supersingular/MOV-small, and subfield-special cells
  must be labeled separately.

## Success Criterion

Audit correctness requires all of:

- `collapse_mismatch_count=0` exactly;
- measured lifted hit probability divided by weighted pushed-forward
  probability in `[0.95,1.05]` within declared sampling error;
- all raw-minus-deduplicated rank explained by duplicate trace-image columns;
- zero secret-dependent construction or selection;
- every accepted row and recovered target verifies publicly.

Structural success additionally requires all of:

- a concrete extension/Weil algebraic solver, not coset sampling or an oracle;
- at least `2x` lower charged cost per new image-rank row than the direct
  pushed-forward baseline on three sizes;
- no advantage on matched random controls;
- reusable image factor-base rank and successful public target descent;
- memory below `4*sqrt(ell)`.

Algorithmic success additionally requires all of:

- charged cost per new image-rank row below `0.8*rho` on three sizes;
- complete public target recovery below rho on at least one size;
- fitted charged trend at or below exponent `0.5`;
- comparison against parallel rho and the nearest known extension-field
  decomposition baseline.

## Falsification Criterion

The pure multiplicity lane is already falsified by the restricted theorem.
Narrow the algebraic-solver lane if the correctness equalities hold but any of
these persists across the sweep:

- degree/regularity matches or exceeds the pushed-forward solver;
- charged solver cost per new image-rank row is at least half the direct
  baseline;
- trace duplicates explain relation growth and deduplicated rank stalls;
- memory exceeds the gate;
- target descent or full public recovery fails;
- empirical charged exponent is at least `0.5`.

This would not rule out a non-homomorphic correspondence, a norm map with extra
factorization semantics, a different low-dimensional abelian variety, or an
extension representation with a genuinely new solver structure.

## Proof Track

- Formalize the trace-quotient collapse theorem and image-rank consequence.
- Prove the public section and kernel sampler under exact subgroup assumptions.
- Derive the Weil-restricted polynomial systems for `m=2,3`.
- Bound or measure degree/regularity relative to pushed-forward Semaev/MITM.
- Prove that target descent consumes only public reusable image logs.

## Disproof Track

- Compare every lifted tuple to the weighted pushed-forward multiset.
- Merge trace duplicates before rank.
- Search for uniform `1/|G|` trace behavior and low-rank image support.
- Charge extension arithmetic and all failed solver branches.
- Let random-coordinate and random-factor-base controls attempt to reproduce
  any claimed structural advantage.

## Minimal Experiment

1. Generate one ordinary prime-order toy curve at each preregistered `p`.
2. Construct `F_{p^2}` and `F_{p^3}` in fixed public polynomial bases.
3. Verify the public trace section and kernel sampler.
4. Build equal-size structured and random factor bases.
5. Exhaustively audit `k=2` and bounded `k=3` lifted versus weighted-image hit
   counts and deduplicated ranks.
6. Encode the smallest Weil-restricted trace-fiber decomposition system.
7. Compare its solver operations with direct image MITM/Semaev.
8. Replay rows, solve the image matrix, and attempt blind target recovery.

## Planned Reproduction Command

```bash
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_005_trace_quotient_decomposition.sage \
  --out experiments/ecdlp_isogeny/po_transfer_005_result.json
```

## Literature Boundary

The closest established clusters are:

- Gaudry, "Index Calculus for Abelian Varieties of Small Dimension and the
  Elliptic Curve Discrete Logarithm Problem," 2009,
  https://doi.org/10.1016/j.jsc.2008.08.005.
- Joux and Vitse, "Cover and Decomposition Index Calculus on Elliptic Curves
  Made Practical," 2012, https://doi.org/10.1007/978-3-642-29011-4_3.
- Gorla and Massierer, "Index Calculus in the Trace Zero Variety," 2015,
  https://doi.org/10.3934/amc.2015.9.515.
- Tian, "Cover Attacks for Elliptic Curves over Cubic Extension Fields," 2023,
  https://doi.org/10.1007/s00145-023-09474-2.
- Semaev, "Summation Polynomials and the Discrete Logarithm Problem on
  Elliptic Curves," 2004, https://eprint.iacr.org/2004/031.
- Petit, Kosters, and Messeng, "Algebraic Approaches for the Elliptic Curve
  Discrete Logarithm Problem over Prime Fields," 2016,
  https://doi.org/10.1007/978-3-662-49387-8_1.

These works cover extension-field transfer, trace-zero subgroups, cover
decomposition, and prime-field algebraic factor bases.  The current `OPEN` gap
is narrower: whether solving in a trace-quotient representation of an original
prime-field target yields a measured solver-time advantage after exact
pushforward collapse, image deduplication, rank, and descent accounting.

## Three Theory Variants

1. `CONSERVATIVE`: Weil-restricted trace-fiber equations over `m=2` with a
   public affine-subspace factor base; likely failure is exact collapse plus no
   degree advantage.
2. `REPRESENTATION CHANGE`: factor a norm/resultant attached to the trace fiber
   and use Frobenius-orbit trace images as reusable columns; likely failure is
   random trace images or an image factor base of size about `p`.
3. `HIGH-RISK`: replace the homomorphic trace by a non-homomorphic
   correspondence whose fibers carry factorization labels not determined by
   the pushed-forward point; likely failure is loss of composability or a
   hidden decomposition oracle.

## Artifact Paths

- `research/PO_transfer_005_contract.md`
- planned:
  `experiments/ecdlp_isogeny/po_transfer_005_trace_quotient_decomposition.sage`
- planned: `experiments/ecdlp_isogeny/po_transfer_005_result.json`
- planned: `experiments/ecdlp_isogeny/po_transfer_005_result.md`
