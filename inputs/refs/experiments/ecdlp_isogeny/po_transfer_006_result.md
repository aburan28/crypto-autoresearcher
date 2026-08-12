# PO-transfer-006 Result: Trielliptic Cofiber Decomposition

Date: 2026-07-13

## Result

Status: `NEGATIVE RESULT / TOY-EVIDENCE / UNRAMIFIED-AFFINE / MODEL-BOUND`.

Candidate: **Trielliptic Cofiber Decomposition (TCD)**.

TCD uses the exact generic degree-3 formulas for a `(3,3)`-split genus-2 curve

```text
C: y^2=P(x)Q(x)
```

with complementary maps `phi1:C->E1` and `phi2:C->E2`.  A complete rational
`phi2` fiber has three points, and their `phi1` images sum to a fixed point on
`E1`.  In all tested unramified affine fibers that point is the identity, so a
lift of a target point gives a native two-point decomposition of the target.

The relation mechanism is exact.  It does not produce useful factor-base rank
or beat a relation-valid EC-addition control.

## Restricted Theorems

1. A nonconstant map from a genus-2 curve to an elliptic curve induces an
   elliptic factor of the Jacobian.  A faithful homomorphic genus-2 transfer is
   therefore split, not absolutely simple.
2. For complementary maps, `phi1_* phi2^*=0`.  Differences of `phi2` fibers
   push to zero on `E1`, so their three-point `phi1` sums are constant.
3. A fixed `(3,3)` cover supplies at most three generic cofiber completions per
   target.  Constant fiber degree alone cannot change an exponent.

The proof sketches and limitations are recorded in
`research/PO_transfer_006_theory.md`.

## Frozen Cells

| p | #E1 | j(E1) | #E2 | j(E2) | a | b | c |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 89 | 5 | 86 | 61 | 13 | 40 | 21 |
| 211 | 223 | 46 | 208 | 45 | 48 | 144 | 173 |
| 431 | 443 | 350 | 419 | 96 | 214 | 204 | 253 |

Every `E1` has prime order, is ordinary, and excludes `j in {0,1728}`.  The
curve, parameters, factor bases, targets, and edge ordering are public and
deterministic.  Target or factor-base logs are not used by collection.

## Cofiber And Rank Results

| p | affine C points | mapped | cofiber rows | E1 columns | rank | 2-core edges | EC-add columns/rank | floor/rho |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 71 | 68 | 6 | 18 | 6 | 0 | 17 / 6 | 26.92x |
| 211 | 217 | 212 | 34 | 78 | 34 | 0 | 81 / 34 | 56.16x |
| 431 | 428 | 424 | 74 | 174 | 74 | 0 | 170 / 74 | 80.33x |

Each production edge contributes one independent row but introduces about
`2.3..3.0` columns.  Every selected hypergraph has an empty two-core, and no
public edge prefix reaches `rank=columns-1`.  The matched public EC-addition
source `(A,B,-A-B)` has the same rank-per-row and nearly the same vertex count.

The optimistic affine-enumeration cost floor fits approximately `n^1.188` over
these three tiny cells.  This is not an asymptotic estimate, but it is adverse:
the floor is already `26.9..80.3x` rho before projective completion, cubic
fiber inversion, sparse linear algebra, or target descent.

## Factor-Base Gate

Deterministic public factor bases were tested near `n^(1/3)`, `n^(1/2)`, and
`n^(2/3)`.

- No factor base reached the required `B-1` rank.
- Eight of nine cells had zero all-in-factor-base cofiber rows.
- The only hit was `p=101, B=20`: one row, rank `1`, versus rank `19` needed.
- No blind target was recovered.
- No fourfold completion excess over matched EC-addition trials occurred.

The one tiny completion hit is not a positive signal: it has no reusable rank,
no target solve, and no replication.

## Controls

- Both explicit quotient maps were evaluated and curve-checked for every
  retained affine cover point.
- All `114` complete production cofibers have constant sum `O`.
- Flipping one point sign never preserves the relation.
- Shuffled labels produced `0`, `0`, and `1` accidental constant-sum triples,
  consistent with the finite-group null.
- The actual log vector was checked only after collection and lies in every
  production row kernel.  This is a correctness check, not target recovery.
- Public EC addition generated relation-valid matched triples and reproduced
  the production rank profile.

## Independent Replay

`po_transfer_006_verify.sage` independently reconstructs each curve and both
maps from the exported parameters.  It re-enumerates all affine cover points,
rebuilds both fiber partitions, checks every constant-sum and wrong-sign
relation, regenerates shuffled and EC-addition controls, recomputes production
and control ranks, and replays every factor-base/target count.

Verifier status: `VERIFIED`.

- generator source SHA-256:
  `5478456bac6dd5d7bc93ffb38a60fc163c2be0deee5c17fb434aea435b863cee`
- result JSON SHA-256:
  `858a5a10c748b828fc20078c4fb53a7e1b1df8bc9d3151c01770d06ff45bf226`
- verifier source SHA-256:
  `f022e66db4a71d3c195d33376b221b99d52cd6e55e8f1616598afb8df5ee0e84`

## Narrow Negative Result

On the three frozen ordinary prime-order toy targets, the unramified affine
cofiber hypergraph of an exact generic `(3,3)` split cover does not expose
factor-base completion or rank beyond relation-valid EC addition.  Fixed cover
degree provides valid target decompositions but only bounded multiplicity.
Rank remains proportional to rows while columns grow faster, and the optimistic
collection floor is already far above rho.

This does **not** close:

- branch, pole, or infinity fibers;
- a projective theta/Kummer implementation;
- growing-degree correspondences;
- complementary labels with independently proved norm/factorization bias;
- a public quotient-label sieve that avoids full cover enumeration.

## Literature And Novelty Boundary

The split covers and explicit maps are established in Shaska and Djukanovic.
Small-genus Jacobian decomposition is established in Gaudry and Sarkar-Singh.
TCD was a local candidate use of those objects, not a novelty claim.  The
negative result makes no claim about all correspondence-labeled algorithms.

## Next Three Theories

1. `CONSERVATIVE`: projectively replay exceptional `(3,3)` fibers as a control.
   Promote only if their normalized completion/rank rate exceeds the affine and
   EC-addition baselines; otherwise preserve them as a completeness check.
2. `REPRESENTATION CHANGE`: use a cyclic Kummer cover
   `X_d: z^d=h(P)` and factor the norm of `z-v` after target interpolation.
   The label must change norm-smoothness or solver cost after image
   deduplication; `d` preimages alone receive no credit.
3. `HIGH-RISK`: construct a growing-degree correspondence family whose fibers
   carry factorization labels and whose batch inversion/sieve costs
   sublinearly in the degree.  Require degree growth, rank, and target descent
   to fit below exponent `0.5`; otherwise derive a degree-versus-query barrier.

Priority: theory 2.  It tests semantics not bounded by fixed fiber count while
retaining exact principal-divisor and pushforward verification.

## Handoff: fixed-degree cofibers to norm-labeled covers

### Claim or task

Find a correspondence label that changes factorization or solver cost, rather
than merely giving a constant number of representations of the same elliptic
point.

### Status

NEGATIVE RESULT

### Assumptions

- unramified affine fibers only;
- three tiny ordinary prime-order cells;
- full affine enumeration used as a discovery oracle;
- optimistic operation floor;
- no deployment or novelty claim.

### Evidence so far

- all exact cofiber relations and controls replay independently;
- production and EC-addition rank profiles match;
- all two-cores are empty;
- no small factor base closes rank or recovers a target;
- cost floor is already far above rho.

### Failure modes

- projective exceptional fibers are untested;
- the public label-generation algorithm is absent;
- tiny cells cannot support asymptotic extrapolation;
- a different label may carry genuine norm-smoothness information.

### Next concrete action

Write `PO-transfer-007` for a target-coupled cyclic-cover norm relation.  Prove
the pushforward relation, deduplicate base-group images, and compare actual
norm factorization against a pushed-forward EC-function-field baseline before
implementing a large relation collector.

### Artifact paths

- `research/PO_transfer_006_contract.md`
- `research/PO_transfer_006_theory.md`
- `experiments/ecdlp_isogeny/po_transfer_006_trielliptic_cofiber.sage`
- `experiments/ecdlp_isogeny/po_transfer_006_result.json`
- `experiments/ecdlp_isogeny/po_transfer_006_result.md`
- `experiments/ecdlp_isogeny/po_transfer_006_verify.sage`
- `experiments/ecdlp_isogeny/po_transfer_006_verify.json`
