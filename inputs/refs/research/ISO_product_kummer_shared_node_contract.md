# Experiment Contract: Product-Kummer Shared-Node Isogeny Circuit

## Claim Status

`HYPOTHESIS / UNTESTED / TOY / REPRESENTATION-CHANGE`

## Candidate

Candidate name: **Product-Kummer Shared-Node Isogeny Circuit (PKSNIC)**.

Let `phi:E->E'` be a degree-`ell` isogeny and `hat(phi):E'->E` its dual.  Test
the balanced Kani matrix map

```text
A(P,Q) = (phi(P)+Q, P-hat(phi)(Q)).
```

Its adjoint matrix satisfies `A^dagger A=[ell+1]` on `E x E'`.  For `ell=3`,
this is a balanced `(4,4)` product isogeny.  Pass to product-Kummer invariant
coordinates and test whether both output additions share denominator,
differential-addition, or orientation intermediates unavailable to two
independent one-dimensional rational-map circuits.

## Hypothesis

After exact common-subexpression extraction, exceptional-branch accounting,
orientation recovery, and memory traffic, the genuine balanced product-Kummer
circuit uses at least `1.25x` fewer held-out field operations or DAG edges than
every matched direct-product control while reproducing both output points.

## Null Hypothesis

The two output additions share only input/map evaluations already shared by a
generic direct circuit.  Kummer quotienting saves coordinate storage but
orientation labels, denominator handling, or witness recovery restores the
full computation.

## Parameters

- S1 source curve `E/F_3889` and its registered degree-3 codomain `E'`;
- genuine `phi`, its exact dual, and `N=ell+1=4`;
- deterministic public point pairs, including generic, doubling, inverse,
  denominator-zero, and identity branches when defined;
- source representations: affine product, projective denominator-retaining
  product, and product-Kummer invariant coordinates;
- controls: two independent output circuits, a same-map no-cross-output-share
  circuit, and coefficient-matched random bidegree circuits;
- no ECDLP relation collection until this circuit smoke passes.

## Metrics

- exact `A^dagger A=[4]` point checks;
- rational-function numerator/denominator degrees and support;
- unique DAG nodes/edges before and after common-subexpression elimination;
- additions, multiplications, squarings, inversions, and multiplicative depth;
- common denominator degree and exceptional branch count;
- orientation/sign bits and recovery work;
- serialized bytes, peak live temporaries, and memory-read/write proxy;
- calibration and held-out circuit scores;
- matched-control ratios and wall-clock diagnostics.

## Positive Controls

- `hat(phi)(phi(P))=[3]P` and `phi(hat(phi)(Q))=[3]Q`.
- The adjoint product map composed with `A` returns `[4](P,Q)`.
- Affine and Kummer circuits agree with direct EC arithmetic on every generic
  public point pair.
- A deliberately duplicated algebraic subexpression is removed by the DAG
  counter, validating the common-subexpression instrument.

## Negative Controls

- Disable cross-output sharing while retaining within-output sharing.
- Serialize the same intermediate values independently for each output.
- Match all input degrees/supports with random coefficients.
- Charge every orientation label and exceptional fallback.

## Success Criterion

The genuine product-Kummer circuit must reproduce all outputs and show a frozen
calibration-predicted held-out reduction of at least `1.25x` in both arithmetic
work and DAG/memory work against every control.  The gain must remain after
orientation recovery and exceptional branches.  Only then may a factor-base,
relation-rank, blind-descent, and rho experiment be registered.

## Falsification Criterion

No cross-output nodes survive exact matching, orientation recovery erases the
gain, a control matches the circuit, or either charged ratio is below `1.25x`.
This closes only the balanced degree-3 product-Kummer circuit realization.

## Reproduction Command

```bash
HOME=/private/tmp/codex-sage-home sage -python \
  experiments/ecdlp_isogeny/iso_product_kummer_shared_node.sage.py
```

## ECDLP Candidate Checklist

### Target Curve Family

- Prime fields, ordinary prime-order curves with a public low-degree isogeny.
- Initial evidence is toy-only; P-224/P-256/P-384 applicability is static.

### Structure Exploited

Balanced product-isogeny and Kummer differential-addition node sharing across
`phi` and its dual, not scalar transport to an easier curve.

### Factor Base

Deferred until the circuit gate passes.  Any later base must be matched exactly
against a direct-product control in points, size, and membership cost.

### Relation Generation and Linear Algebra

Deferred.  A promoted follow-up must include exact relation probability, full
rank, sparse linear algebra, blind target descent, and total rho comparison.

### Things That Would Kill the Idea

- no cross-output common subexpressions;
- orientation labels restore all saved work;
- product-state count grows quadratically without relation-density gain;
- direct Kummer controls reproduce the same DAG;
- memory traffic dominates arithmetic savings.

## Handoff: PKSNIC

### Claim or Task

Determine whether the balanced degree-3 Kani product map creates genuine
cross-output computation sharing beyond one-dimensional rational-map circuits.

### Status

HYPOTHESIS / UNTESTED / TOY / REPRESENTATION-CHANGE

### Assumptions

- Product-Kummer invariant coordinates preserve enough orientation data for
  exact witnesses.
- Common-subexpression counts are a useful prefilter for solver work.

### Evidence So Far

- IPRMCA-S1 found no one-dimensional circuit advantage.
- Explicit degree-3 maps and duals verify on the toy fixture and NIST curves.
- The balanced matrix identity gives an exact product-isogeny positive control.

### Failure Modes

- Trivial storage-only compression, hidden orientation work, exceptional
  denominator branches, and random-control equivalence.

### Next Concrete Action

Implement the exact degree-3 matrix-map point controls and symbolic DAG counter
before any relation or ECDLP work.

### Artifact Paths

- `research/ISO_product_kummer_shared_node_contract.md`
- `experiments/ecdlp_isogeny/iso_product_kummer_shared_node.sage.py`
