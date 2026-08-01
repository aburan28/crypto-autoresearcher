# ECDLP-IDEA-062 — Different-filtered ramification norm

## Status and claim labels

- Class: `representation`
- Risk band: `representation-changing`
- State: `rejected_no_go`
- Evidence scale: `toy` symbolic-cover derivation only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Deduplication verdict: the different is branch-locus supported, while growing ramification pays matching genus and representation growth
- Breakthrough claim: **none**; a ramification label or norm identity is not an ECDLP break.

## Falsifiable hypothesis

A target-independent ramified cyclic cover `pi:C->E` has a positive-density family of
fibers whose different-ideal filtration yields source-labelled local norm factors, not
mere bounded lift multiplicity. Fitting ideals of the finite fiber algebra expose these
labels before parameter enumeration; their pushforward gives rank-productive factor-base
relations and masked target descent with full time and memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation was **different-filtered norm factorization with a scheme-theoretic
source lift**. Ramification length and higher local factors would be retained through the
norm rather than collapsed to the ordinary trace/cofiber multiplicity already closed in
the ledger. A factor in a Fitting filtration must identify the upstairs branch and its
downstairs endpoint.

Changing cover degree, counting exceptional fibers, enumerating projective parameters,
or emitting only a norm relation is a duplicate/control.

## Assumptions

1. `E/F_p` has a known prime-order subgroup `<P>` of order `N` and challenge `Q=[x]P`.
2. A public bounded-description ramified cyclic cover is constructed independently of `Q` and `x`.
3. Informative filtered fibers occur with density `N^(-delta)` that is not just the finite branch locus.
4. Fitting/different factors are computable without enumerating every cover parameter or fiber point.
5. Each accepted factor has an exact upstairs and downstairs source witness on complete charts.
6. Cover construction, genus, field extensions, output, rank, descent, verification, and memory are charged.
7. All extrapolations are toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`ramified_cyclic_cover | local_different_filtration | Fitting_factor_before_enumeration | branch_source_label | norm_pushforward_relation | masked_target_descent`

For the stated fixed bounded cover, the different is supported on the finite ramification
locus and cannot yield a positive-density source family. Enlarging the branch divisor
changes the representation and pays the corresponding genus cost.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `TRANSFER-H004`, the closest non-homomorphic cyclic-cover label and norm-smoothness lane.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, the closest multiplicity-bearing factor-fiber control.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H682`, the closest local-algebra/fiber-state source control.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H675`, the adjacent cover-fiber multiplicity boundary.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H633`, which requires relation density and fresh-rank gain rather than exceptional fibers.

## Closest primary literature

- Fitting, [Die Determinantenideale eines Moduls](https://eudml.org/doc/146122), supplies Fitting ideals but no point-source parametrization.
- Gille, Neher, and Ruether, [The Kähler different](https://arxiv.org/abs/2401.15051), studies the different and its ramification support, not an ECDLP source channel.
- Cutkosky, Kuhlmann, and Rzepka, [The Kähler different and ramification](https://arxiv.org/abs/2305.10022), supplies the closest different/ramification boundary.
- Lange and Ortega, [Prym varieties of cyclic coverings](https://arxiv.org/abs/0805.1020), supplies the nearby cyclic-cover geometry.

No checked source proves the required positive-density filtered norm law; novelty and
algorithmic applicability are unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N`, cover `C`, branch divisor, local charts, and a downstairs factor base.
2. Compute the finite fiber algebra, different, and Fitting filtration symbolically.
3. On exhaustive curves, map every filtered factor to all upstairs branches and downstairs endpoint sources.
4. Generate known-scalar rows from the filtered fibers and verify norm/pushforward relations independently.
5. Collect enough independent downstairs rows and solve verified factor-base logarithms.
6. Apply the identical filtration to randomized `Q+[t]P` fibers.
7. Lift a successful filtered factor to source atoms, substitute factor logs, and remove `t`.
8. Verify the recovered scalar by `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time and constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let cover setup/genus exponent be `a`, factor-base size
`N^beta`, reciprocal informative-fiber densities `N^delta,N^delta_t`, filtration plus
source-lift exponent `kappa`, output exponent `omega`, sparse linear algebra `2beta`, and
memory `mu`. Then
`lambda=max(a,delta+kappa,delta+omega,2beta,delta_t+kappa,delta_t+omega)`.
For a fixed bounded cover only `O(1)` branch fibers are informative. If branch degree is
grown to improve density, Riemann–Hurwitz makes genus and representation size grow with
it; those losses are charged in `delta,a,kappa,mu` and remove the claimed free density.

## Likely fatal obstruction

Ramification is supported on a fixed finite divisor, so filtered local information may
affect only `O(1)` fibers and cannot supply a growing relation base. Norms can erase the
very branch label being used as provenance; retaining it may require enumerating the
whole fiber algebra. Growing the branch divisor raises genus, coefficient size, and output
at the same rate as any apparent density gain.

## Proof track

Prove a positive-density family of informative fibers, a pre-enumeration Fitting-factor
algorithm, exact branch-to-endpoint inversion, and full relation/rank/descent bounds with
`lambda,mu<1/2`.

## Disproof track

Prove informative factors are supported only at the branch divisor, show the norm forgets
source labels, show Fitting computation enumerates the fiber, or derive `lambda>=1/2`.

## Positive and negative controls

- Positive ramification control: a tiny cover with known different exponents and branch labels.
- Positive norm control: exhaustive divisors with exact pushforward sources.
- Negative etale control: a matched unramified cover with the same degree and genus band.
- Negative multiplicity control: raw fiber count with labels erased.
- Leakage control: no target-dependent branch divisor, scalar-labelled point, or post-hoc fiber choice.

## Quantitative promotion and falsification gates

No promotion gate remains for the stated fixed-cover mechanism. Its historical gate
would have required informative-fiber density at least `N^(-0.20)` and source lift
`N^(0.20)` or better on a stated growing family. A later
preflight would require zero factor/source errors, 1,000 relations, 100 blind descents,
and upper 95% `lambda,mu<=0.45`. Falsify if informative density is `O(1/N)`, source
output is full-fiber size, or lower 95% `lambda>=0.50`; infrastructure failure is not a disproof.

## Artifact plan

- Missing theorem: `ideas/artifacts/ECDLP-IDEA-062/density_and_source_theorem.md`
- Symbolic cover: `ideas/artifacts/ECDLP-IDEA-062/ramification_filtration.sage`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-062/verify_norm_sources.sage`
- Future runs: `ideas/artifacts/ECDLP-IDEA-062/runs/<run-id>/`
- Retain equations, differents, Fitting ideals, fiber factors, sources, norms, costs, commands, seeds, environment, stdout, and stderr.

## Interpretation boundary

This rejected hypothesis is toy, heuristic, model-bound, and novelty-unverified. Exact
ramification and norm identities do not imply enhanced smoothness or a breakthrough.

## Exactly one next executable action

1. Preserve `ideas/artifacts/ECDLP-IDEA-062/density_and_source_theorem.md` as an unexecuted proof boundary; do not reopen this lane without a non-ramification invariant on étale fibers whose full source and genus costs evade the stated no-go.
