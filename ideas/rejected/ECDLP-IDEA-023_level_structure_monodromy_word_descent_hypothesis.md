# ECDLP-IDEA-023 — Level-structure monodromy-word descent

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a correct monodromy matrix or toy path is not a break.

## Falsifiable hypothesis

The marked fibers `(E,P)` and `(E,Q=[x]P)` in a universal level-`N` family admit a
publicly constructible compressed monodromy word carrying one marking to the other. The
word's explicit mod-`N` matrix reveals `x`, while level construction, auxiliary torsion,
path search, word length, basis ambiguity, and memory all have exponent below `1/2`.

## Mechanism-new operation

Recover a **word in the level-structure monodromy representation**, then read the scalar
from its matrix action. This is not idea 010's branch selection in a fixed cover or idea
011's invariant on a scalar orbit. A path algorithm that enumerates the orbit or merely
evaluates a modular invariant is a duplicate/control.

## Assumptions

1. Level data and an auxiliary torsion basis are constructible from public data with all extension degrees charged.
2. The path/word is canonical enough to map the declared markings without using `x`.
3. Generator matrices and basis changes are explicit modulo `N`.
4. Word search, collisions, stabilizers, and residual scalar candidates are retained.
5. No explicit table of the `N` marked fibers is used.
6. Scaling is toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`universal_elliptic_level_family | marked_torsion_fiber_path | compressed_monodromy_generator_word | mod_N_matrix_scalar_label`

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — motivates a non-PDP direct descent.
2. `ledger/H-ISO-001.yaml` — distinguishes a universal level path from an isogeny walk.
3. `ledger/H-REP-001.yaml` — distinguishes moduli monodromy from a curve-model rewrite.
4. `ledger/H-FB-001.yaml` — no ordinary factor-base structure is claimed.
5. `ledger/SYNTHESIS-20260716.md` — supplies the complete-cost and review boundary.

## Closest primary literature

- Lvovski, [On monodromy in families of elliptic curves over `C`](https://arxiv.org/abs/1705.02129), supplies the elliptic-family monodromy setting.
- Hall, [Big symplectic or orthogonal monodromy modulo `l`](https://arxiv.org/abs/math/0608718), gives the nearby mod-`l` monodromy boundary.
- Derickx and van Hoeij, [Gonality of the modular curve `X_1(N)`](https://arxiv.org/abs/1307.5719), quantifies a likely degree obstruction.

The literature makes level covers and monodromy known but not the claimed compressed word
recovery. Novelty remains unverified.

## Complete factor-base-to-target-descent path

Here the replacement factor base is a frozen generating set of the monodromy group.

1. Construct the level object, auxiliary torsion basis, marked fibers, and certified generator matrices.
2. Compute a target-independent navigation structure without enumerating all level points.
3. Recover every generator word whose endpoint maps the `P` marking to the `Q` marking.
4. Multiply word matrices, resolve stabilizers/basis ambiguity, and extract all candidate scalar labels.
5. Verify every candidate on `E` and return only `[x]P=Q`.

## Full rho/BSGS cost model

Let level construction/degree costs be `N^c,N^k`, word search `N^w`, per-step evaluation
`N^q`, reciprocal valid-word density `N^delta`, matrix decoding `N^u`, and storage `N^s`.
Rho is `N^1/2` time; BSGS is `N^1/2` time/memory. The proposal has
`lambda=max(c,k,w+q+delta,u)` and `mu=s`. Orbit tables, auxiliary torsion fields, and
residual stabilizer lists contribute their measured exponents.

## Likely fatal obstruction

The level cover has degree and gonality growing with `N`; constructing a full torsion basis
can require an extension of comparable size. Selecting the endpoint word is a hidden-shift
labeling problem equivalent to the original DLP, while many words share the same endpoint.

## Proof track

Construct a compressed level navigation method, prove endpoint correctness and scalar
readout, and bound cover degree, word search, ambiguity, and storage below square root.

## Disproof track

Prove the required level representation or navigation structure has `N^(1/2-o(1))` size,
reduce word recovery to scalar-orbit search, or show basis/stabilizer ambiguity remains
square-root scale.

## Positive and negative controls

- Positive control: a small modular cover with a planted short generator word.
- Positive instrumentation control: exhaustive level graphs through the toy boundary.
- Negative control: random regular covering graphs with matched degree and monodromy group.
- Duplicate controls: fixed-cover deck descent and scalar-orbit periods.
- Circularity control: reject lookup by known scalar or explicit orbit index.

## Quantitative promotion and falsification gates

Use prime levels 7–24 bits where construction is feasible, at least 50 marked curves per
size, and exhaustive level graphs through 14 bits. Promotion requires exact endpoints and
zero wrong scalars, 100 recoveries at the two largest sizes, upper 95% `c<=0.35`,
`k<=0.35`, `w+q+delta<=0.45`, `u<=0.30`, `lambda<=0.45`, `mu<=0.45`.
Falsify if an explicit orbit table is required, level/basis degree has lower 95% exponent
`>=0.50`, any accepted scalar is wrong, or every complete-cost lower bound reaches `0.50`.
Unsupported level arithmetic is infrastructure evidence.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-023/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-023/monodromy_word.sage`
- `ideas/artifacts/ECDLP-IDEA-023/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-023/runs/<run_id>/words.jsonl`
- `ideas/artifacts/ECDLP-IDEA-023/runs/<run_id>/matrices.jsonl`
- `ideas/artifacts/ECDLP-IDEA-023/analysis.md`

## Interpretation boundary

All observations are toy, heuristic, model-bound, and novelty-unverified. A valid word or
matrix action does not establish a sub-rho target recovery.

## Exactly one next executable action

1. Enumerate the smallest supported level graphs and compare exhaustive shortest endpoint words with a target-blind compressed navigation prototype.
