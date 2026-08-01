# ECDLP-IDEA-149 — Lifted affine-invariant scalar-orbit decoder

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk-theorem-gated`
- Top lane: `high-risk`
- State: `deferred_needs_orbit_code_membership_and_typed_decoder_theorem`
- Cohort: `20260718-a`
- Evidence scale: paper preflight only; no experiment ran
- Contract posture: retired `review_required` preflight under `ideas/rejected/contracts/`; zero runs permitted
- Scale labels: every prospective finite test is `toy`; complexity projections are `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; local correction, a decoded predicate, a source tuple, or a toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is one fixed public rational observable `Phi` such that the target-shifted scalar-orbit word built from `Phi(R+[a]P)` lies in a target-uniform lifted affine-invariant code of sublinear query complexity. A typed local message decoder would return either a hidden scalar digit or an exact factor-base source atom—not merely a publicly recomputable symbol—and repeated decoding would support complete relation generation and blind masked-target descent below rho and BSGS.

## Mechanism-new operation

The proposed operation is **lifted affine-invariant local decoding of a public elliptic scalar-orbit word**. Public affine forms select scalar shifts, group operations answer oracle queries, and the decoder maps the corrected local view to hidden-shift or exact-source information. This differs from P1479 linear feature interpolation and bounded phase lifts: promotion requires a proved code-membership theorem, distance, and typed scalar/source output without an `N`-entry orbit dictionary.

## Assumptions

1. `E/F_p` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target `Q=[x]P`, and public factor base `F` of size `B=N^beta`.
2. A fixed public family of affine forms over the scalar field and rational observable `Phi` defines every queried symbol using only `R+[a]P` and public arithmetic.
3. For every admitted `R`, the resulting word belongs to one lifted affine-invariant code with explicit degree, distance, rate, and target-independent decoder.
4. The decoder's output is algebraically typed as a scalar digit or exact signed source atom and is not just `Phi(R+[a]P)`, a predicate value, or a list requiring scalar-labelled calibration.
5. Signs, zero, infinity, collisions, list size, exceptional observables, and every affine-chart ambiguity are complete and charged.
6. Code construction, calibration, queries, relation output, rank, factor logs, blind descent, final verification, and peak bit memory are charged.

## Semantic fingerprint

`public_target_shifted_scalar_orbit_word | lifted_affine_invariant_code_membership | sublinear_local_message_decoder | typed_hidden_shift_or_source_output | blind_masked_target_reuse`

The removal test is a target-uniform code theorem plus typed scalar/source inverse. Interpolating public values, supplying a labelled orbit table, or renaming a full-degree word is a control.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `P1474`, where a large known-scalar CM orbit fails to compress a noninvariant sparse deck.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1474`, which records the exact failure of the tested orbit deck and transition structure.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, where rational addition-law phases reproduce public points and tuples but do not yet compress complete source state.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1425-BOUNDED-PHASE-LIFT-NO-PROMOTION`, where bounded polynomial phase lifts do not express factor membership below the public expansion floor.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1479`, where true factor logs lie outside tested public low-dimensional linear feature spaces.

## Closest primary literature

- Guo, Kopparty, and Sudan, [New affine-invariant codes from lifting](https://arxiv.org/abs/1208.5413), construct lifted affine-invariant code families but do not place generic elliptic scalar-orbit words in such a family or decode their hidden shift.
- Semaev, [Summation polynomials and the discrete logarithm problem on elliptic curves](https://eprint.iacr.org/2004/031), supplies the neighboring elliptic relation equations but no orbit-code source decoder.

No checked primary source proves this exact orbit-code membership and typed inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,Q,F,B,beta`, `Phi`, affine forms, code parameters, decoder, masks, corruption/list policy, and exceptional charts.
2. For a public endpoint `R`, answer orbit-word queries only by computing `R+[a]P` and evaluating `Phi`; do not build a scalar-labelled orbit table.
3. Run the fixed local decoder and convert its typed message output to an exact signed factor-base source tuple, retaining all list candidates and collisions.
4. Verify every emitted tuple by factor-base membership and direct elliptic addition; a decoded public predicate value is recorded as failure.
5. Apply the identical word/decoder to known `R_j=[r_j]P` until `B+sigma` independently verified rows have rank `B`.
6. Solve and independently verify all factor-base logarithms.
7. Decode fresh `Q+[t]P` words, substitute verified logs, subtract `t`, and retain every scalar candidate; if the decoder returns scalar digits directly, charge the same construction, calibration, list, and verification costs.
8. Accept only `[x]P=Q` and preserve complete degree, distance, query, output, rank, time, and memory receipts.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected time with constant state; BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`; observable/code construction and calibration cost `N^a,N^a_m`; reciprocal relation and target decode densities `N^delta,N^delta_t`; one complete local-decode/source query `N^q,N^q_m`; output and list ambiguity `N^o,N^u`; and factor-log linear algebra `N^ell,N^ell_m`. The complete exponents are

`lambda=max(a,beta+delta+q+o,ell,delta_t+q+o+u,beta)`

`mu=max(a_m,q_m,beta+o,ell_m,u)`.

For `beta=0.20` and constant density/output/list size, promotion requires `q<=0.25`. An `N^(1/2)` query decoder, `N^(1/2)` calibration table, or full-degree interpolation cannot beat rho after construction and descent.

## Likely fatal obstruction

Generic elliptic scalar-orbit words appear full-degree and lack the distance/rate structure needed for low-query local decoding. Affine lifting can only reproduce publicly computable symbols, while extracting the hidden shift or a source atom requires a message map not supplied by code membership. Calibration that assigns messages to scalar shifts is an `N`-entry DLP dictionary, and source-tagged symbols restore the missing relation fiber.

## Proof track

Specify one fixed `Phi` and lift, prove code membership, degree/distance/rate, a target-uniform local decoder with a typed scalar/source biconditional, and complete `lambda,mu<=0.45` through relation rank, factor logs, and blind descent.

## Disproof track

Prove generic full degree or vanishing distance, exhibit two scalar shifts with indistinguishable permitted local views but different messages, show decoder output is only public evaluation, or reduce calibration/source typing to an orbit dictionary or factor-log interpolation.

## Positive and negative controls

- Supplied lifted affine-invariant codewords with planted messages and corruptions.
- Degree-matched random orbit words and random public predicates.
- Full scalar-orbit tables as inadmissible dictionary controls.
- P1474 orbit compression, bounded phase lifts, and P1479 public-feature interpolation controls.
- Exhaustive tiny known-log and blind unknown-log targets with matched rho and BSGS accounting.

## Quantitative promotion and falsification gates

Remain deferred. Before any run, independent review must prove one fixed observable, target-uniform code parameters, and a typed local decoder. A later toy gate requires exact predicted degree/distance on all fixtures, `100%` scalar/source recovery with `0` false outputs, no calibration larger than `N^0.20`, at least `100` blind descents at each of the two largest sizes, and complete `lambda,mu<=0.45`. Falsify on generic full degree, one typed-output failure, an `N^(1/2)` or larger query/calibration stage, a scalar-labelled dictionary, or complete time or memory exponent at least `0.50`.

## Artifact plan

- Orbit-code degree gate: `ideas/artifacts/ECDLP-IDEA-149/orbit_code_degree_gate.md`
- Observable specification: `ideas/artifacts/ECDLP-IDEA-149/observable_spec.md`
- Frozen fixtures: `ideas/artifacts/ECDLP-IDEA-149/fixtures.json`
- Independent verifier: `ideas/artifacts/ECDLP-IDEA-149/independent_verifier.py`
- Complete cost receipt: `ideas/artifacts/ECDLP-IDEA-149/cost_analysis.md`
- Retired review-required contract: `ideas/rejected/contracts/ECDLP-EXP-CONTRACT-149_affine_invariant_orbit_preflight.yaml`

All experiment artifacts are prospective. The retired contract permits zero runs.

## Interpretation boundary

This is a deferred, high-risk, theorem-gated, novelty-unverified proposal. All finite evidence would be toy and all scaling claims remain heuristic and model-bound. Local correction, a public symbol, a valid source tuple, or a toy scalar would establish only scoped correctness, not a generic ECDLP improvement or breakthrough.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-149/orbit_code_degree_gate.md` proving or refuting target-uniform low-degree code membership and a typed scalar/source decoder for one frozen public observable before implementing local correction.
