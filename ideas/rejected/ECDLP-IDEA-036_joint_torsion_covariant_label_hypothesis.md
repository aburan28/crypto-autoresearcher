# ECDLP-IDEA-036 — Joint torsion covariant label

## Status and claim labels

- Class: `mechanism`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` preflight only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; computing a correct covariant or separating toy marked pairs is not an ECDLP break.

## Falsifiable hypothesis

For a fixed-degree elliptic-normal embedding of a generic `E/F_p`, the section-ring
multiplication tensor together with the two evaluation covectors defined by public
`P` and `Q=[x]P` admits a target-independent family of joint projective covariants.
From those covariants one can construct, without enumerating multiples or supports,
a scalar-label polynomial whose complete root list contains `x` and whose degree,
construction time, coefficient size, root-solving time, ambiguity, and bit memory
all have exponent below `1/2` in the prime subgroup order `N=p^(1+o(1))`.

The proposed information is a simultaneous invariant of the marked pair, not an
invariant of the unmarked curve.  Its existence and sub-square-root separating
degree are conjectural, toy, heuristic, model-bound, and novelty-unverified.

## Mechanism-new operation

Freeze an elliptic-normal section ring and its multiplication tensor `M_E`.  Encode
`P` and `Q` only as evaluation covectors `epsilon_P` and `epsilon_Q`.  Apply explicit
tensor contractions and invariant-theoretic covariant operations simultaneously to
`(M_E,epsilon_P,epsilon_Q)` to produce a basis-independent marked-pair signature and
a directly defined label polynomial `H_(P,Q)(T)`.  Solve that polynomial for the
integer multiplier rather than translating points, decomposing a target, or taking
a matrix-power logarithm.

This is distinct from `ECDLP-IDEA-015`: it constructs no translation operator,
theta representation, stable subquotient, eigenvalue, or operator power.  It is
also distinct from the support-oracle lane: it has no factor base, secant support,
membership test, relation collection, or atom decoder.  If the covariants merely
repackage a coordinate model, require `T_P^x`, enumerate the orbit of `P`, expose
only a support/membership certificate, use a dense resultant without a new
separating theorem, or rely on a scalar lookup table, this record must be rejected
or merged with the corresponding occupied lane.

## Assumptions

1. `<P>` has public prime order `N=p^(1+o(1))`, `Q=[x]P`, and the construction is uniform over generic prime-field curves.
2. Embedding degree, section basis, multiplication tensor, and evaluation covectors are chosen deterministically without `x` or target selection.
3. The joint covariant family is proved invariant under every allowed section-basis and projective-coordinate change while retaining scalar-label information.
4. `H_(P,Q)` is constructed directly from bounded covariant contractions, not from enumerated multiples, a target support search, an order-`N` operator, or a known-log interpolation table.
5. Every root, sign, projective, field-extension, and normalization ambiguity is retained and verified on `E`.
6. Covariant degree, count, coefficient height, field degree, contraction arithmetic, root solving, failures, and bit memory are charged; all scaling remains heuristic and model-bound.

## Semantic fingerprint

`elliptic_normal_section_ring_tensor | two_marked_evaluation_covectors | simultaneous_projective_covariants | direct_scalar_label_polynomial | no_translation_or_support_oracle`

## Five closest ledger entries

1. `ledger/H-REP-001.yaml` — prevents ordinary elliptic-normal coordinates or covariants of the unmarked curve from counting as a mechanism.
2. `ledger/EV-REP-002.yaml` — supplies explicit branch and representation-equivalence checks.
3. `ledger/DEC-20260716-001.yaml` — requires a new mathematical operation that removes the measured representation obstruction.
4. `ledger/FINDING-PF-IC-001.md` — supplies the full rho, target-recovery, and memory accounting boundary.
5. `ledger/SYNTHESIS-20260716.md` — requires a verified end-to-end scalar rather than a relation, invariant, or applicability result.

## Closest primary literature

- Fisher, [The invariants of a genus one curve](https://doi.org/10.1112/plms/pdn021), develops invariant theory for degree-two through degree-five genus-one models and the recovery of their Jacobians.
- Fisher, [Invariant theory for the elliptic normal quintic, I: twists of `X(5)`](https://arxiv.org/abs/1110.3520), gives explicit nearby elliptic-normal invariant and covariant constructions.
- Fisher, [Invariant theory for the elliptic normal quintic, II: the covering map](https://arxiv.org/abs/1303.2550), demonstrates explicit covariant maps while also bounding what ordinary covering covariants already provide.
- Shoup, [Lower bounds for discrete logarithms and related problems](https://www.shoup.net/papers/dlbounds1.pdf), is the generic lower-bound boundary if the proposed covariants are simulable using only generic group operations.

None of these sources supplies a low-degree joint covariant whose label is the
integer multiplier between two marked points.  This limited proximity check does
not prove novelty; novelty remains unverified.

## Complete factor-base-to-target-descent path

There is no factor base in this direct route; the replacement object is the frozen
joint covariant basis.

1. Freeze a constant embedding degree, deterministic section basis, tensor grammar, covariant degree schedule, and normalization using only `(E,P,N)`.
2. Construct and checksum `M_E`, `epsilon_P`, and the covariant grammar before admitting `Q` to the computation.
3. Encode `Q` only as `epsilon_Q`, evaluate the complete joint covariant family, and certify invariance under held-out random basis changes.
4. Construct `H_(P,Q)(T)` from the preregistered contraction formulas without enumerating `[i]P`, solving a support problem, or constructing a translation operator.
5. Factor or root-solve `H_(P,Q)` over its explicitly charged coefficient ring, preserve every normalization and extension-field branch, and map all integral residue candidates to `Z/NZ`.
6. Accept only the unique candidate `x` for which `[x]P=Q`; record an empty, multiple, or oversized root list as failure rather than selecting post hoc.

## Full rho/BSGS cost model

Let reciprocal construction-applicability density be `N^zeta`; embedding and tensor
construction cost `N^c`; required coefficient-field degree and coefficient height
contribute `N^phi` and `N^h`; number of retained covariant coordinates be `N^rho`;
maximum covariant degree be `N^delta`; contraction/evaluation cost be `N^kappa`;
label-polynomial construction and root solving cost `N^q`; residual root list
`N^u`; per-list verification contribution `N^v`; and other bit storage `N^s`.

- Pollard rho: `N^(1/2+o(1))` time with negligible memory.
- BSGS: `N^(1/2+o(1))` time and memory.
- Output-size-aware proposed time exponent:
  `lambda=max(zeta+c,phi+h,rho+delta,kappa,q,u+v)`.
- Proposed bit-memory exponent:
  `mu=max(s,phi+h,rho+delta,u)`.

All invariant generators searched, failed contractions, basis conversion matrices,
polynomial coefficients, field representations, root lists, and verification work
are included.  A degree, signature, field, root list, search space, or precomputed
label dictionary of exponent `1/2` or larger kills promotion.

## Likely fatal obstruction

The `N` marked pairs `(P,[i]P)` must be separated.  A basis-independent invariant
family may therefore need degree, output dimension, coefficient height, or a label
dictionary of order `N`; ordinary genus-one invariants usually recover the curve or
covering data, not the integer relating two points.  If a small signature does retain
the cyclic action, labeling its values may be exactly the original DLP or an
order-`N` operator/orbit problem in disguise.

## Proof track

Give explicit contraction formulas for the joint covariants and `H_(P,Q)`, prove
projective and basis invariance, prove that every `Q=[x]P` yields a complete bounded
root list containing `x`, prove that neither construction nor labeling enumerates
the subgroup or invokes a support/operator oracle, and bound `lambda,mu<1/2` on a
generic family.

## Disproof track

Prove a separating-degree, output-dimension, or coefficient-height lower bound of
`N^(1/2-o(1))`; show all bounded covariants are independent of `x` or collide on an
oversized set; reduce their labeling to generic DLP; or demonstrate that construction
necessarily becomes a translation operator, orbit enumeration, support oracle, dense
resultant, or scalar table already covered by an occupied lane.

## Positive and negative controls

- Positive instrumentation control: exhaustive prime-order toy curves, with logs revealed only after covariant and root-list artifacts are sealed.
- Invariance control: at least 100 random section-basis and projective-coordinate changes per marked pair.
- Negative representation control: invariants of `E` alone and single-point covariants, which must not be credited with scalar information.
- Operator-duplication control: build the full translation matrix separately and verify that no production covariant depends on it or its powers.
- Support-duplication control: audit every contraction for factor-base, secant, membership, relation, and atom-recovery dependencies.
- Generic lower-bound control: matched random cyclic labels and generic-group encodings with the same output dimension.
- Leakage control: hash and dependency-audit the grammar before toy logarithms are computed.

## Quantitative promotion and falsification gates

The theorem preflight uses exhaustive prime subgroup orders through at least 43 and
then generic 10–20-bit prime-order curves where formulas remain executable.  Promotion
to scaling requires all of the following:

- exact invariance under every held-out basis change and zero incorrect scalar outputs;
- a grammar frozen before targets and logs, with no enumerated multiple, translation operator, support oracle, dense membership resultant, or scalar-indexed table;
- scalar separation on at least 99% of preregistered generic instances and a 95% upper bound `u<=0.10` on root-list exponent;
- upper 95% bounds `rho<=0.20`, `delta<=0.20`, `phi+h<=0.25`, `lambda<=0.45`, and `mu<=0.45`;
- an independent symbolic proof that the label polynomial is complete for every scalar, not merely correlated on sampled targets.

Falsify the scoped hypothesis if bounded joint covariants are target-blind, omit a
true scalar, produce an incorrect accepted scalar, require degree/output/list exponent
at least `0.50`, or cross any explicit reject/merge boundary.  Failure to implement
high-degree invariant arithmetic is infrastructure evidence only unless accompanied
by a mathematical lower bound.

## Artifact plan

- Planned contract: `ideas/contracts/ECDLP-EXP-CONTRACT-036_joint_covariant_preflight.yaml`
- Planned specification: `ideas/artifacts/ECDLP-IDEA-036/preflight_spec.yaml`
- Planned implementation: `ideas/artifacts/ECDLP-IDEA-036/joint_covariants.sage`
- Planned frozen grammar: `ideas/artifacts/ECDLP-IDEA-036/covariant_grammar.json`
- Planned instances: `ideas/artifacts/ECDLP-IDEA-036/instances.jsonl`
- Planned runs: `ideas/artifacts/ECDLP-IDEA-036/runs/<run_id>/`
- Planned invariant certificates: `ideas/artifacts/ECDLP-IDEA-036/runs/<run_id>/invariants.jsonl`
- Planned cost fits: `ideas/artifacts/ECDLP-IDEA-036/runs/<run_id>/costs.tsv`
- Planned analysis: `ideas/artifacts/ECDLP-IDEA-036/analysis.md`

## Interpretation boundary

This hypothesis is toy, heuristic, model-bound, high-risk, and
novelty-unverified.  A covariant identity, coordinate-invariant signature, or
correct toy label is not a breakthrough.  Promotion requires a new separating
operation, complete scalar recovery, and measured generic time and bit memory below
rho/BSGS.  If the operation collapses to idea `015`, a support oracle, an alternate
curve model, an orbit/table, or a relation-only certificate, it must be rejected or
merged rather than retained under new terminology.

## Exactly one next executable action

1. Enumerate the minimal joint separating covariant degrees for exhaustive prime subgroup orders through 43 using a grammar frozen before logarithm disclosure, and record every collision and operator/support dependency.
