# Pre-ID duplicate draft — Cipolla quadratic-extension source splitter

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V02`; no canonical ID allocated.
- Disposition: `merged_rejected_quadratic_extension_root_and_conjugate_sign_ambiguity`.
- Class/risk/lane: representation / representation-changing / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; exact extension-field exponentiation or a valid relation is not an ECDLP break.

## Falsifiable hypothesis

Embedding each endpoint fibre in Cipolla's quadratic algebra makes Frobenius
conjugation a canonical source involution. Exponentiation to `(p+1)/2` would split
the fibre into exact signed occurrences, enabling full relation rank and 100 blind
descents with complete exponents at most `0.45`.

## Mechanism-new operation

Cipolla selects `a` with `a^2-n` nonsquare, works in
`F_p[X]/(X^2-(a^2-n))`, and extracts a supplied square root by one fixed
extension-field exponentiation. Novelty would require the endpoint to compile `n`
without source enumeration and conjugation to label elliptic occurrences rather
than only the two algebraic roots.

## Assumptions

1. Endpoint restrictions compile a bounded public radicand for every source fibre.
2. Quadratic conjugation preserves occurrence identity and empty-fibre semantics.
3. The chosen nonsquare and root sign are target-independent and non-post-hoc.
4. Extension construction, exponentiation, replay, logs, and descent meet both caps.
5. No factor-base dictionary or scalar labels enter the quadratic algebra.

## Semantic fingerprint

`public_endpoint_radicand | Cipolla_quadratic_algebra | Frobenius_conjugate_root_split | exact_signed_occurrence_lift | full_descent`

## Five closest ledger entries

1. `ideas/deferred/ECDLP-IDEA-049_bounded_root_decomposition_transducer_hypothesis.md` — bounded roots still need exact source inversion.
2. `ideas/rejected/ECDLP-IDEA-051_hash_restricted_frobenius_isolation_descent_hypothesis.md` — Frobenius isolation is an occupied aggregate lane.
3. `ideas/rejected/ECDLP-IDEA-074_lang_frobenius_coboundary_orbit_lift_hypothesis.md` — extension conjugacy does not canonically orient sources.
4. `ideas/ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md` — point-sign recovery remains explicit.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — exact signed replay cannot be replaced by a root certificate.

## Closest primary literature

- Cipolla's root method is covered as the Cipolla–Lehmer route in Harasawa, Sueyoshi, and Kudo, [Root computation in finite fields](https://doi.org/10.1587/transfun.E96.A.1081), a primary algorithmic comparison of finite-field root methods.
- Adleman, Manders, and Miller, [On taking roots in finite fields](https://doi.org/10.1109/SFCS.1977.18), gives the nearby general root-extraction boundary.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not provide a point-faithful radicand or conjugation-to-source section.

No checked source supplies the ECDLP occurrence lift; novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, factor decks, radicand compiler, `a` search, algebra basis, restrictions, masks, and verifier.
- Build target-independent state below `B^(9/4+o(1))`, excluding source lists, target fitting, and factor logs.
- Charge every nonsquare test, algebra multiplication, exponentiation, conjugate branch, exceptional fibre, replay, and failure.
- Verify at least `max(d_FB+32,1000)` independent rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical state for 100 fresh masked targets, replay tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

With `beta=1/5`, use setup/state `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, algebra/replay costs `N^q,N^q_m`, rank credit `N^r`,
output `N^o`, ambiguity `N^u`, and logs `N^ell,N^ell_m`. Charge
`lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both at most `0.45`,
state at most `B^(9/4+o(1))`, and fresh work/workspace at most
`B^(5/4+o(1))`. Rho/BSGS remain `0.50`.

## Likely fatal obstruction

The quadratic algebra is built after a radicand exists and returns two field roots.
Conjugation does not remember which factor-base point occurrence generated the
radicand, and x-coordinate equations erase elliptic sign. Point-faithful radicands
or backpointers reintroduce the missing source compiler.

## Proof track

Prove endpoint-only radicands, target-independent algebra choice, an injective
conjugation-to-occurrence theorem for all strata, rank/log recovery, descent, and
complete sub-rho accounting.

## Disproof track

Hold the radicand and quadratic algebra fixed while changing exact source fibres,
expose a source-derived radicand or tuned `a`, or show replay/cost reaches `0.50`.

## Positive and negative controls

- Positive: planted quadratic-algebra roots with external occurrence labels.
- Negative: equal radicands/different fibres, conjugate swaps, nonresidues, double roots, x-sign collisions, and fresh targets.
- Baselines: IDEAs 049/051/074/158, P1553 R4, rho, and BSGS.
- Correct exponentiation or roots are representation controls only.

## Quantitative promotion and falsification gates

- Promote only with exact compiler and all-strata lift, zero semantic errors, failure at most `2^-80`, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on one equal-algebra source collision, source-bearing radicand, branch ambiguity, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v02_quadratic_algebra_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v02_conjugate_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v02_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the transplant, not Cipolla's algorithm. Correct roots, conjugation,
relations, or validator results remain `toy`, `heuristic`, `model-bound`,
`novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Build a minimal equal-radicand pair whose Cipolla algebra is identical while the accepting signed elliptic source fibre differs.
