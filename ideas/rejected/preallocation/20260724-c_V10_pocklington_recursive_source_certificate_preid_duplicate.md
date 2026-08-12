# Pre-ID duplicate draft — Pocklington recursive source certificate

## Status and claim labels

- Provisional ID: `PREID-20260724-c-V10`; no canonical ID allocated.
- Disposition: `merged_rejected_relation_only_primality_certificate_and_supplied_factorization`.
- Class/risk/lane: algorithm / conservative / pre-ID screen.
- Evidence: complete-ledger, complete-idea-corpus, and primary-literature review only; no experiment ran.
- Labels: `toy`, `heuristic`, `model-bound`, `novelty-unverified`.
- Breakthrough claim: none; a verified primality or fibre-existence certificate is not an ECDLP break.

## Falsifiable hypothesis

Every restricted endpoint fibre admits a public integer `M_S` whose Pocklington
certificate exists exactly when that fibre contains a signed factor-base tuple, and
the recursive `M_S-1` factors canonically encode its occurrences. Certificate
generation plus bisection would yield rank, factor logs, and 100 blind descents with
complete exponents `<=0.45`.

## Mechanism-new operation

Pocklington verifies primality of a supplied integer using a sufficiently large
known factor of `M-1` and modular gcd/exponentiation witnesses. It is ECDLP-new only
if endpoints compile `M_S`, its recursive factors, and an exact occurrence inverse
without already solving the restricted source problem.

## Assumptions

1. Each endpoint restriction has a compact public integer certificate instance.
2. Certificate existence distinguishes empty from nonempty fibres without false positives.
3. Recursive factors orient exact signed occurrences rather than only prove primality.
4. Instance/factor construction, certificate search, replay, rank, logs, and descent meet both caps.
5. No source enumeration, target scalar, or relation-only oracle is hidden in `M_S-1`.

## Semantic fingerprint

`public_restricted_endpoint_integer | Pocklington_Mminus1_certificate | recursive_factor_chain | exact_signed_occurrence_inverse | full_descent`

## Five closest ledger entries

1. `ideas/rejected/ECDLP-IDEA-107_finite_field_witness_transport_hypothesis.md` — witness transport is occupied and source inversion remains missing.
2. `ideas/deferred/ECDLP-IDEA-052_elliptic_wedge_witness_identity_hypothesis.md` — an identity/witness is not a full source return.
3. `ideas/rejected/ECDLP-IDEA-157_ppa_parity_path_decomposition_extractor_hypothesis.md` — existence certificates do not orient all occurrences.
4. `ideas/rejected/ECDLP-IDEA-117_degree_aware_provenance_join_hypothesis.md` — recursive factors need charged provenance.
5. `ideas/artifacts/ECDLP-IDEA-012/p1553_target_label_common_factor_gate_r4.md` — Query2P1 existence plus signed replay and blind descent is the live interface.

## Closest primary literature

- Pocklington, [The determination of the prime or composite nature of large numbers by Fermat's theorem](https://archive.org/details/proceedingscambr18camb/page/n51/mode/2up), gives the supplied-`M-1` factor certificate.
- Goldwasser and Kilian, [Almost all primes can be quickly certified](https://doi.org/10.1145/12130.12162), is a later elliptic certificate route and likewise starts from a certificate statement.
- Semaev, [summation polynomials](https://eprint.iacr.org/2004/031), does not compile certificate integers whose factors are elliptic occurrences.

No checked source supplies the endpoint certificate compiler or occurrence inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

- Freeze `B=N^(1/5)`, factor decks, restriction encoding, integer compiler, witness/factor policy, masks, and verifier.
- Build target-independent state within `B^(9/4+o(1))` without source tables, target advice, explicit factor chains, or factor logs.
- Charge every `M_S`, known-factor search, recursion, witness exponentiation, gcd, failed certificate, bisection query, and occurrence replay.
- Verify `max(d_FB+32,1000)` independent relation rows, rank `d_FB`, and solve all factor-base logs.
- Reuse byte-identical state for 100 fresh masked targets, return tuples, subtract masks, and verify scalars.

## Full rho/BSGS cost model

For `beta=1/5`, let setup/state be `N^a,N^a_m`, reciprocal densities
`N^delta,N^delta_t`, certificate/replay costs `N^q,N^q_m`, rank credit
`N^r`, output `N^o`, ambiguity/failure `N^u`, logs `N^ell,N^ell_m`.
Charge `lambda=max(a,beta+delta+q-r+o,ell,delta_t+q+o+u,beta)` and
`mu=max(a_m,q_m,beta+o,ell_m,u)`, `0<=r<=o`; require both `<=0.45`,
state `<=B^(9/4+o(1))`, fresh work/workspace `<=B^(5/4+o(1))`;
rho/BSGS remain `0.50`.

## Likely fatal obstruction

Pocklington checks a supplied primality statement and supplied partial
factorization. Constructing `M_S` so its certificate is equivalent to restricted
elliptic source existence is the missing Query2P1 compiler. A yes/no certificate
does not identify signed occurrences; recursive factors that do so are an explicit
source encoding.

## Proof track

Prove endpoint-only integer/factor construction, exact restriction biconditional,
canonical certificate-to-occurrence inversion, charged bisection, full rank/logs,
blind descent, and both cost caps.

## Disproof track

Expose source information in `M_S` or its factorization, find equal certificates
with different fibres, show the return is existence-only, or reach exponent `0.50`.

## Positive and negative controls

- Positive: supplied Pocklington instances whose factors carry external occurrence labels.
- Negative: equal certificate chains/different fibres, composite pseudowitnesses, incomplete `M-1` factors, empty fibres, and fresh targets.
- Baselines: IDEAS 052/107/117/157, P1553 R4, rho, and BSGS.
- Certificate verification or relation validity is relation-only evidence.

## Quantitative promotion and falsification gates

- Promote only with compiler/biconditional/inverse theorems, zero certificate/source errors on arbitrary restrictions, full rank/logs, 100 blind descents, and both exponents `<=0.45`.
- Falsify on one supplied source factor, equal-chain source collision, existence-only output, cap breach, or exponent `>=0.50`.

## Artifact plan

- `ideas/rejected/preallocation/artifacts/20260724-c/v10_certificate_instance_provenance.md`
- `ideas/rejected/preallocation/artifacts/20260724-c/v10_equal_chain_source_collisions.json`
- `ideas/rejected/preallocation/artifacts/20260724-c/v10_cost_analysis.md`

The prospective artifact root is absent.

## Interpretation boundary

This rejects the ECDLP transplant, not Pocklington certification. A correct
certificate, relation, validator pass, or toy scalar remains `toy`, `heuristic`,
`model-bound`, `novelty-unverified`, and not a breakthrough.

## Exactly one next executable action

1. Attempt to compile one nontrivial restricted endpoint fibre into a Pocklington instance while logging the first datum that depends on an exact source occurrence.
