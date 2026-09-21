# PO42 Result: Principal-Divisor Rank Is Source Invariant

## Claim

`OBSERVATION / TOY-EVIDENCE`: the registered PO42 sweep reaches exact
post-large-prime rank `2B-2` at `B=56`, with both nontrivial deck characters
at rank `B-1`.

`RESTRICTED THEOREM / MODEL-BOUND`: under PO42's source-only factor base and
principal-divisor row model, that rank cannot distinguish the joint hidden
labels from any one valid correspondence coordinate.  The single-map control
must accept the same source rows and has the same support matrix.  PO42's
joint-over-single promotion criterion is therefore unattainable without
changing the relation object.

This is not a negative result for target-conditioned divisors, adjoint fibers,
map-dependent factor bases, compressed divisor states, or other transfer
algorithms.

## Registered Run

```bash
HOME=/private/tmp/codex-sage-home sage -python \
  experiments/ecdlp_isogeny/po_transfer_042_deck_orbit_relation_pilot.sage \
  --contract research/PO_transfer_042_relation_contract.md \
  --po40 experiments/ecdlp_isogeny/po_transfer_040_native_candidate_replay.json \
  --po41 experiments/ecdlp_isogeny/po_transfer_041_actual_torsion_quotient.json \
  --B-list 8,15,32,56 \
  --source-attempts 65536 \
  --seed 42042 \
  --controls single_map,random_label,visible_map,pkm \
  --rank-modulus 1021 \
  --rho-baseline 28.3 \
  --out experiments/ecdlp_isogeny/po_transfer_042_deck_orbit_relation_pilot.json
```

Bindings:

- contract SHA256: `97ac9158765b492725c95c6886bb54a9c00c99979867efcb7bbcbd9e813bcae6`;
- PO42 source SHA256: `e222b7d8cb9516868c35daaa1b27505debd9ffa257c7f8bb3f4b5058b808c83f`;
- PO42 result SHA256: `8a1be1d1f3af2caf24615ef04c09f88e3d6be36325bd6ae1bd59c7189ebe33c2`;
- wall time: `92.51` seconds.

All PO40, PO41, and contract hash gates pass.  The run enumerates `981`
rational source points, including `326` nontrivial `C3` orbits and `2` fixed
orbits.  All `980` affine points have supported joint labels.

## Independent Audit Boundary

`experiments/ecdlp_isogeny/po_transfer_042_independent_verify.json` has status
`RED_TEAM_COMPLETE / NO_PROMOTION / RANK_CERTIFICATION_REJECTED`.  It passes
the frozen hashes, independently reconstructs the source inventory and all
four factor bases, hard-replays `156` serialized sample witnesses, and rejects
the contract, row, large-prime, and orientation mutations.

It does not independently certify rank `110`, because the producer JSON stores
only `48/909` accepted row witnesses and `48/251` nonzero projected rows.  It
stores hashes, but not vectors, for the other accepted rows and stores no full
smooth row vectors.  The `110` rank is therefore a producer observation until
a complete compact row/matrix certificate is emitted and replayed.  The
verifier also notes that sample witnesses omit the explicit infinity pole
order `10`; it can infer that value and replay their hashes, but strict
serialization fails.

Verifier bindings:

- source SHA256: `a8bb2a0ae904c510af616244d438e129a5a05eebbf119280e8daf81ef58eb051`;
- result SHA256: `1630b1c67a0fb4ba2f2c0c0990f2e5de3ada2728f120b0acff2a223d310986a9`.

## Relation Evidence

| `B` | accepted | full | one LP | two LP | post-LP rank | character ranks |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 12 | 0 | 0 | 12 | 0 | `0,0` |
| 15 | 57 | 0 | 0 | 57 | 0 | `0,0` |
| 32 | 339 | 0 | 18 | 321 | 0 | `0,0` |
| 56 | 909 | 12 | 102 | 795 | 110 | `55,55` |

For `B=56`, the extended matrix has `909` rows and `572` columns: `112`
factor-base columns plus two columns for each of `230` outside deck orbits.
Its raw rank is `549`.  The left kernel of the large-prime block has dimension
`470`; `251` projected rows are nonzero and span rank `110` over
`F_1021`.  Both character projections have rank `55`.

The exact same `909` rows and rank `110` occur under the single-coordinate
control.  The visible-map check also accepts every row; its reported rank
reuses the two-column source deck module and should be read as a source-rank
calibration, not as the rank of the visible map's trivial deck representation.
The random-label control accepts no rows.  The PKM control is not implemented.

The full pilot charges `262144` source attempts, `261851` polynomial
factorizations, and at least `560700` EC additions.  It does not beat the
negation-aware rho baseline of `28.3` additions.

## Restricted Theorem

Let `X/k` be a smooth projective curve with base point `P0`, let
`f_i : X -> A_i` be morphisms to abelian varieties with `f_i(P0)=0`, and let
`F_i : Jac(X) -> A_i` be their induced homomorphisms.  If a relation generator
emits only principal divisors `D=div(h)`, then

```text
F_i([D]) = 0
```

for every `i`, because `[D]=0` in `Pic^0(X)`.  If matrix rows and large-prime
elimination depend only on the source support, multiplicities, and deck
orientations, then adjoining more valid maps changes verification labels but
does not change the row module or its rank.  Thus a joint tuple
`(f_1,...,f_r)` cannot have better accepted-row rank than a single valid
coordinate on this fixed principal-divisor stream.

PO42 satisfies these hypotheses: the factor base is source-only, every row is
the divisor of `y-g(u)` (including its pole at infinity), and the two target
labels come from `phi` and `phi o sigma`.  The observed single-map equality is
therefore structural rather than an unlucky sample.

## What Is Ruled Out

`NEGATIVE RESULT`: PO42's exact degree-5 `y-g(u)`, source-only,
principal-divisor stream cannot satisfy its joint-over-single rank-specificity
gate.  Increasing the attempt budget or `B` cannot change that theorem.  The
reported full rank remains an observation rather than independently certified
evidence until complete rank inputs are serialized.

Not ruled out:

- a target-conditioned nonprincipal divisor equation;
- factorization of `phi^*(T)` into small Frobenius-stable places;
- a factor base selected by map fibers rather than source hashes;
- a compressed divisor/Kummer representation with lower charged cost;
- a family-level correspondence whose target descent exponent is below
  generic collision search.

## Next Positive Question

Does the degree-146 correspondence expose unusually smooth Frobenius-stable
target fibers that the original curve and the visible degree-three quotient do
not, and can those fibers produce replayable nonhomogeneous descent equations?
PO43 tests this question on `16` precommitted blind targets before any
calibration or algorithm claim.

## Handoff: PO42 rank signal to target-fiber descent

### Claim or task

Replace source-principal rank attribution with exact target-conditioned fiber
factorization and closed-point pushforward witnesses.

### Status

OPEN

### Assumptions

- The exact PO40/PO41 degree-146 correspondence remains hash-bound.
- Closed-point pushforward multiplicity is charged and verified.
- No target scalar may influence factor-base or fiber selection.

### Evidence so far

- Exact post-LP rank `110=2B-2` at `B=56`.
- The same rank under the single-map control proves no joint-label specificity.
- Calibration, target descent, and algorithmic success remain false.

### Failure modes

- Hidden fibers match random degree-146 factorization statistics.
- The visible degree-three quotient gives strictly cheaper lifts.
- Small places do not decompose over the frozen source factor base.
- Factoring and divisor arithmetic already exceed rho.

### Next concrete action

Run the PO43 target-fiber profile on the fixed `16` target scalars and replay
the smallest closed-point lift for every target.

### Artifact paths

- `research/PO_transfer_043_target_fiber_contract.md`
- `experiments/ecdlp_isogeny/po_transfer_043_target_fiber_probe.sage`
- `experiments/ecdlp_isogeny/po_transfer_043_target_fiber_probe.json`
