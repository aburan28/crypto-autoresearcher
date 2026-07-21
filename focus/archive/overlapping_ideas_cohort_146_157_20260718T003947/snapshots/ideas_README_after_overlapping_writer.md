# ECDLP idea registry

This directory contains mechanism-first, falsifiable research hypotheses for generic
prime-field ECDLP. These records are proposals, not coordinator-approved experiments and
not evidence of a breakthrough. Every crypto-scale implication is `novelty-unverified`;
all executable preflights are explicitly toy or model-bound until independently replicated.

## Current corpus

| ID | Short name | Class | Risk | Disposition | Contract |
|---|---|---|---|---|---|
| [ECDLP-IDEA-001](ECDLP-IDEA-001_ambient_spectral_incidence_oracle_hypothesis.md) | Ambient spectral incidence oracle | algorithm | conservative | proposed, unapproved | — |
| [ECDLP-IDEA-002](ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md) | Split-Jacobian projected smoothness | representation | representation-changing | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-002_split_jacobian_projection_preflight.yaml) |
| [ECDLP-IDEA-003](ECDLP-IDEA-003_partial_scalar_power_correspondence_hypothesis.md) | Partial scalar-power correspondence | mechanism | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-004](ECDLP-IDEA-004_prime_to_p_jet_logarithm_hypothesis.md) | Prime-to-p jet logarithm | mechanism | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-005](ECDLP-IDEA-005_height_compressing_global_lift_hypothesis.md) | Height-compressing global lift | representation | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-006](ECDLP-IDEA-006_elliptic_net_short_annihilator_hypothesis.md) | Elliptic-net short annihilator | algorithm | high-risk | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-006_elliptic_net_rank_preflight.yaml) |
| [ECDLP-IDEA-007](ECDLP-IDEA-007_miller_s_unit_descent_hypothesis.md) | Miller S-unit descent | algorithm | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-008](ECDLP-IDEA-008_partial_pairing_return_cycle_hypothesis.md) | Partial pairing-return cycle | mechanism | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-009](ECDLP-IDEA-009_nonequivariant_trace_zero_transfer_hypothesis.md) | Nonequivariant trace-zero transfer | representation | representation-changing | proposed, unapproved | — |
| [ECDLP-IDEA-010](ECDLP-IDEA-010_torsor_deck_orbit_descent_hypothesis.md) | Torsor deck-orbit descent | representation | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-011](ECDLP-IDEA-011_scalar_orbit_elliptic_period_descent_hypothesis.md) | Scalar-orbit elliptic-period descent | algorithm | high-risk | proposed, unapproved | — |
| [ECDLP-IDEA-012](ECDLP-IDEA-012_aggregate_complement_divisor_compression_hypothesis.md) | Aggregate complement-divisor compression | algorithm | conservative | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-012_aggregate_divisor_preflight.yaml) |
| [ECDLP-IDEA-050](ECDLP-IDEA-050_spinor_matchgate_addition_transform_hypothesis.md) | Spinor-matchgate addition transform | representation | representation-changing | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-050_matchgate_identity_preflight.yaml) |
| [ECDLP-IDEA-056](ECDLP-IDEA-056_block_krylov_transition_intersection_extractor_hypothesis.md) | Block-Krylov transition-intersection extractor | algorithm | conservative | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-056_transition_intersection_preflight.yaml) |
| [ECDLP-IDEA-059](ECDLP-IDEA-059_cremona_shrunk_toric_decomposition_hypothesis.md) | Cremona-shrunk toric decomposition | representation | high-risk | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-059_cremona_toric_preflight.yaml) |

The machine-readable index is [idea_registry.tsv](idea_registry.tsv). The originating
semantic audit is [DEDUP-20260717T124917-0700.md](reviews/DEDUP-20260717T124917-0700.md),
and the complete generation closeout is recorded in
[DEDUP-20260717T163711-0700.md](reviews/DEDUP-20260717T163711-0700.md) and
[REDTEAM-20260717T163712-0700.md](reviews/REDTEAM-20260717T163712-0700.md). The previous
generation closeout is
[DEDUP-20260717T173000-0700.md](reviews/DEDUP-20260717T173000-0700.md) and
[REDTEAM-20260717T173100-0700.md](reviews/REDTEAM-20260717T173100-0700.md).
The `049`–`060` generation pass produced three proposed, unapproved survivors (`050`,
`056`, `059`), four theorem/identity-deferred records (`049`, `052`, `053`, `058`),
and five merged/rejected records (`051`, `054`, `055`, `057`, `060`). The `061`–`072`
pass produced no active survivor after independent review, three theorem/identity-deferred
records (`064`, `068`, `069`), and nine merged/no-go records (`061`, `062`, `063`,
`065`, `066`, `067`, `070`, `071`, `072`). The previous generation closeout is
[DEDUP-20260717T184441-0700.md](reviews/DEDUP-20260717T184441-0700.md) and
[REDTEAM-20260717T184442-0700.md](reviews/REDTEAM-20260717T184442-0700.md). The
`073`–`084` pass likewise produced no active survivor: `073`, `075`, and `076` are
theorem-deferred, while `074` and `077`–`084` are merged or rejected, including exact
Lang-orbit and characteristic-cycle no-go boundaries. Deferred records remain under
[deferred evidence](deferred/README.md); all rejected and retired evidence remains under
[rejected evidence](rejected/README.md). The latest generation closeout is
[DEDUP-20260717T194242-0700.md](reviews/DEDUP-20260717T194242-0700.md) and
[REDTEAM-20260717T195357-0700.md](reviews/REDTEAM-20260717T195357-0700.md). The
`085`–`096` pass again produced no active survivor. Independent review rejected
conservative `085` by the all-distinct open-stratum no-go, deferred
representation-changing `086` and high-risk `087` on explicit source-inverse theorems,
and merged or rejected `088`–`096`. The corpus is 15 active proposed/unapproved, 12
deferred, and 69 rejected records, not 96 validated algorithms. The `085`–`087`
top-lane drafts are preserved as retired review evidence, giving 20 retired contracts
in total. No experiment ran. Only the Coordinator may approve a contract or change an
official state.

The newest `097`–`108` pass is recorded in
[DEDUP-20260717T203744-0700.md](reviews/DEDUP-20260717T203744-0700.md) and
[REDTEAM-20260717T210151-0700.md](reviews/REDTEAM-20260717T210151-0700.md). It produced no
active survivor: conservative `098`, high-risk `102`, and representation-changing `103`
are theorem-deferred, while `097`, `099`–`101`, and `104`–`108` are scoped no-gos or
semantic merges. The corpus is now 15 active proposed/unapproved, 15 deferred, and 78
rejected records, not 108 validated algorithms. The three new top-lane contracts are
retired, `review_required`, unapproved, and permit zero runs, giving 23 retired contracts
in total. The active-only `idea_registry.tsv` therefore remains at 15 rows. No experiment
ran, and only the Coordinator may approve a contract or change an official state.

The newest `109`–`120` pass is recorded in
[DEDUP-20260717T213431-0700.md](reviews/DEDUP-20260717T213431-0700.md) and
[REDTEAM-20260717T214500-0700.md](reviews/REDTEAM-20260717T214500-0700.md). It also
produced no active survivor: high-risk `119` and branch-quotient `111` are
theorem-deferred, while representation-changing `115` and conservative `117` are closed
by scoped strict-Ulrich source-length and P1510 product-circuit input-floor proofs;
`109`, `110`, `112`–`114`, `116`, `118`, and `120` are other scoped no-gos or semantic
merges. The corpus is now 15 active proposed/unapproved, 17 deferred, and 88 rejected
records, not 120
validated algorithms. The three relative top-lane contracts are retired,
`review_required`, unapproved, and permit zero runs, giving 26 retired contracts in
total. The active-only `idea_registry.tsv` remains byte-stable at 15 rows. No experiment
ran. Five immutable non-run receipts preserve the two scoped boundaries: two for `115`
and three for `117`. They do not rule out a mechanism-new nonlinear target-specialized
representation for `115` or pre-leaf representation for `117`. Only the Coordinator may
approve a contract or change an official state.

Two late P1513 receipts under the `068` artifact root preserve a mechanism-new shared
bivariate common-norm identity and a standard-route screen. The recovered assignment
review [DEDUP-20260717T223633-0700-IDEA121.md](reviews/DEDUP-20260717T223633-0700-IDEA121.md)
routes the operation to theorem-deferred `ECDLP-IDEA-121`; the current complete review
superseding that transient report is
[DEDUP-20260717T225007-0700.md](reviews/DEDUP-20260717T225007-0700.md), with independent
findings in [REDTEAM-20260717T225100-0700.md](reviews/REDTEAM-20260717T225100-0700.md).

The requested `122`–`133` generation pass produced no active survivor. Conservative
`133` remains theorem-deferred behind a compact nonlinear-constructor and P1512/P1513
non-reduction theorem. IDs `122`–`132` are exact scoped no-gos or semantic merges,
including the Maltsev-coset and formal-logarithm torsion no-gos. Relative high-risk
`128`, representation-changing `129`, and conservative `133` contracts are retired,
`review_required`, unapproved, and permit zero runs. The complete corpus is now 15 active
proposed/unapproved, 19 deferred, and 99 rejected records across IDs `001`–`133`, with
29 retired contracts. The active-only `idea_registry.tsv` remains byte-stable at 15
rows. No experiment ran, and no correctness or theorem receipt is a breakthrough.

The newest `134`–`145` generation pass is recorded in
[DEDUP-20260717T235101-0700.md](reviews/DEDUP-20260717T235101-0700.md), with independent
findings in [REDTEAM-20260717T235349-0700.md](reviews/REDTEAM-20260717T235349-0700.md).
Strict review left no active or deferred survivor: all twelve records are exact scoped
no-gos or semantic merges. In particular, `134` mischarged the cited preprocessed-3SUM
universe dimension, `135` is IDEA-120's knowledge-compilation representation, and `142`
is a free-field linearization backend. Relative conservative `134`,
representation-changing `135`, and high-risk `145` contracts are retained only as
retired, `review_required`, unapproved, zero-run evidence. The complete corpus is now 15
active proposed/unapproved, 19 deferred, and 111 rejected records across unique IDs
`001`–`145`, with 32 retired contracts. The active-only registry remains byte-stable at
15 rows. No experiment ran. Correctness, a relation, a compact representation, or a
theorem receipt is not a breakthrough.

Concurrent non-run receipts were also reconciled and hash-indexed during closeout. The
IDEA-121 receipt closes standard KU embeddings but leaves a new output-sensitive locator
open. The immutable IDEA-133 P1514 producer receipts are `REVISE`: an append-only audit
closes supplied moments as constructors, the frozen direct-enumeration tradeoffs, and one
theorem-guaranteed sufficient-cutoff dense Macaulay instantiation only. Adaptive,
smaller-cutoff, sparse, multihomogeneous, and structured target-local routes remain open,
as does a charged primary/nilpotent inverse on nonreduced fibers. Both hypotheses remain
theorem-deferred. The current path-confined verifier is planned and unrun; two rejected
verifier revisions and all of their external executions are preserved as invalid current
evidence. No receipt or verifier pass establishes an ECDLP result.

The `146`–`157` generation pass is recorded in
[DEDUP-20260718T003947-0700.md](reviews/DEDUP-20260718T003947-0700.md). It produced no
active promotion: conservative `146`, high-risk `149`, representation-changing `150`,
and rectangular BGG/Tate successor `152` are theorem-deferred; `147`, `148`, `151`, and
`153`–`157` are scoped negatives or semantic merges. The complete corpus is 15 active
proposed/unapproved, 23 deferred, and 119 rejected records across unique IDs `001`–`157`,
with 35 retired contracts. The active-only registry remains byte-stable at 15 rows. No
contract ran, and no correctness, relation, representation, or theorem receipt is a
breakthrough.

## Required interpretation boundary

- A verifier pass establishes only implementation correctness for the tested artifact.
- A relation, correspondence, or homomorphism certificate is not a speedup by itself.
- Toy effects are not crypto-scale validation.
- Promotion requires the complete precomputation, relation, linear-algebra, target-descent,
  verification, and memory exponents to beat both rho and BSGS under matched accounting.
- A toy gate can promote only to a larger scaling study; finite-size slope confidence is
  still model-bound and cannot establish a cryptographic asymptotic.
- Negative evidence closes only the exact stated test boundary.

## Layout

```text
ideas/
  ECDLP-IDEA-<NNN>_<name>_hypothesis.md
  idea_registry.tsv
  contracts/                 review-required experiment contracts
  deferred/                  preserved candidates blocked on a named theorem or identity
  rejected/                  preserved duplicate, no-go, and retired-contract evidence
  reviews/                   timestamped deduplication and red-team reports
  artifacts/                 planned immutable experiment output roots
  validate_ideas.py          structural and cross-file validator
```
