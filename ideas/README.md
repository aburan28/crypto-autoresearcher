# ECDLP idea registry

This directory contains mechanism-first, falsifiable research hypotheses for generic
prime-field ECDLP. These records are proposals, not coordinator-approved experiments and
not evidence of a breakthrough. Every crypto-scale implication is `novelty-unverified`;
all executable preflights are explicitly toy or model-bound until independently replicated.

## Current corpus

| ID | Short name | Class | Risk | Disposition | Contract |
|---|---|---|---|---|---|
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
| [ECDLP-IDEA-158](ECDLP-IDEA-158_x_only_nonfaithful_wnu_signed_lift_hypothesis.md) | Nonfaithful x-only WNU signed lift | algorithm | conservative | proposed, unapproved; theorem preflight only | [contract](contracts/ECDLP-EXP-CONTRACT-158_x_only_nonfaithful_wnu_preflight.yaml) |
| [ECDLP-IDEA-159](ECDLP-IDEA-159_non_diagonal_conormal_polar_source_blowup_hypothesis.md) | Non-diagonal conormal-polar source blowup | algebraic-representation | representation-changing | proposed, unapproved; theorem preflight only | [contract](contracts/ECDLP-EXP-CONTRACT-159_conormal_polar_source_preflight.yaml) |
| [ECDLP-IDEA-160](ECDLP-IDEA-160_nonlogarithmic_ramification_break_scalar_digits_hypothesis.md) | Nonlogarithmic ramification-break scalar digits | arithmetic-transfer | high-risk | proposed, unapproved; theorem preflight only | [contract](contracts/ECDLP-EXP-CONTRACT-160_ramification_break_digits_preflight.yaml) |
| [ECDLP-IDEA-434](ECDLP-IDEA-434_isogeny_class_decomposition_yield_invariance_hypothesis.md) | Isogeny-class variation of Semaev decomposition yield | representation | representation-changing | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-434_isogeny_class_yield_preflight.yaml) |
| [ECDLP-IDEA-435](ECDLP-IDEA-435_function_field_lift_target_coefficient_audit_hypothesis.md) | Target-coefficient audit of the function-field lifting face | control | conservative | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-435_target_coefficient_audit_preflight.yaml) |
| [ECDLP-IDEA-436](ECDLP-IDEA-436_local_torsion_coordinate_valuation_profile_hypothesis.md) | Coordinate-valuation profile of the canonical prime-to-p torsion lift | mechanism | high-risk | proposed, unapproved | [contract](contracts/ECDLP-EXP-CONTRACT-436_valuation_profile_preflight.yaml) |

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
[DEDUP-20260718T003947-0700.md](reviews/DEDUP-20260718T003947-0700.md), with independent
findings in [REDTEAM-20260718T010518-0700.md](reviews/REDTEAM-20260718T010518-0700.md)
and a stricter correction in
[REDTEAM-20260718T012521-0700-ADDENDUM.md](reviews/REDTEAM-20260718T012521-0700-ADDENDUM.md).
It produced no active promotion. Only the rectangular BGG/Tate successor `152` remains
theorem-deferred; strict review rejected `146`–`151` and `153`–`157`, including `150`
at the prime-to-`p` additive-syndrome no-go. The complete corpus is 15 active
proposed/unapproved, 20 deferred, and 122 rejected records across unique IDs `001`–`157`,
with 35 retired contracts. The active-only registry remains byte-stable at 15 rows. No
contract ran, and no correctness, relation, representation, or theorem receipt is a
breakthrough.

The `158`–`169` generation pass is recorded in
[DEDUP-20260718T015523-0700.md](reviews/DEDUP-20260718T015523-0700.md), with independent
findings in [REDTEAM-20260718T015524-0700.md](reviews/REDTEAM-20260718T015524-0700.md).
Operation-level review left three proposed, unapproved theorem preflights: conservative
`158`, representation-changing `159`, and high-risk `160`. Their contracts remain
`review_required`, unapproved, and permit zero runs. IDs `161`, `163`–`165`, and `167`
are theorem-deferred; `162`, `166`, `168`, and `169` are preserved scoped negatives.
The complete corpus is 18 active proposed/unapproved, 25 deferred, and 126 rejected
records across unique IDs `001`–`169`, with nine active contracts and 35 retired
contracts. No experiment ran, and none of these states, theorems, relations, or
representations is a breakthrough.

The `170`–`181` generation pass is recorded in
[DEDUP-20260718T025205-0700.md](reviews/DEDUP-20260718T025205-0700.md), with independent
findings in [REDTEAM-20260718T030059-0700.md](reviews/REDTEAM-20260718T030059-0700.md).
Strict operation-level review left only gain-graph successor `173` theorem-deferred;
`170`–`172` and `174`–`181` are preserved as semantic merges or scoped negatives.
The initially selected conservative `170`, representation-changing `174`, and high-risk
`180` contracts are retired under rejected evidence, remain `review_required` and
unapproved, and permit zero experiment and handoff runs. The complete corpus is now 18
active proposed/unapproved, 26 deferred, and 137 rejected records across unique IDs
`001`–`181`, with nine active and 38 retired contracts. The active-only registry remains
at 18 rows. No experiment ran, and no correctness, relation, representation, theorem,
or validator result is a breakthrough.

The `182`–`193` generation pass is recorded in
[DEDUP-20260718T033001-0700.md](reviews/DEDUP-20260718T033001-0700.md), with fresh
independent findings in
[REDTEAM-20260718T033600-0700.md](reviews/REDTEAM-20260718T033600-0700.md). Strict
operation-level and primary-literature review left no active or deferred survivor:
all twelve records are preserved as semantic merges or scoped negatives. In particular,
`182` requires the missing endpoint-only marked-coefficient oracle, `183` evaluates an
antipode only after the decomposition fiber is supplied, and `192` remains a valuation
backend unless a new compact endpoint-derived key chain and exact all-strata source lift
are proved under a successor ID. Relative top-lane contracts for conservative `182`,
high-risk `183`, and representation-changing `192` are retired under rejected evidence,
remain `review_required` and unapproved, and permit zero experiment and handoff runs.
The cohort itself adds twelve rejected records and no active or deferred record. A
concurrent independently reviewed P1525 receipt also moves the pre-existing IDEA-001
exact linear one-witness mechanism to scoped-rejected; a nonlinear implicit-batch/multirow
router is a different unspecified successor operation. The complete corpus is now 17
active proposed/unapproved, 26 deferred, and 150 rejected records across exact IDs
`001`–`193`, with nine active and 41 retired contracts. The active-only
`idea_registry.tsv` now has 17 rows. A late P1524 non-run
receipt removes raw pairwise Kummer trace/norm as a mechanism-new P1523 exception but
leaves genuinely list-specific support-changing routers open; P1525 is a resource
tradeoff, not a standalone time or Shoup-style lower bound. No experiment ran, and no
correctness, relation, representation, theorem receipt, or validator result is a
breakthrough.

The `194`–`205` theorem-first pass is recorded in
[DEDUP-20260718T043510-0700.md](reviews/DEDUP-20260718T043510-0700.md), with fresh
independent findings in
[REDTEAM-20260718T044328-0700.md](reviews/REDTEAM-20260718T044328-0700.md). Strict
operation-level and primary-literature review leaves only non-Cartesian complete-branch
intertwiner `195` theorem-deferred; `194` and `196`–`205` are preserved as semantic
merges or scoped negatives. The review incorporates P1526's auxiliary-isogeny gate,
P1527's canonical `psi_c` branch-locus gate, and P1528's same-field rational-kernel and
duplicate-column gate without claiming that they close non-group, extension-field, or
genuinely non-Cartesian support laws. Relative top-lane contracts for conservative
`194`, representation-changing `195`, and high-risk `202` are retired,
`review_required`, unapproved, and permit zero experiment and handoff runs. The complete
corpus is now 17 active proposed/unapproved, 27 deferred, and 161 rejected records
across exact IDs `001`–`205`, with nine active and 44 retired contracts. The active-only
`idea_registry.tsv` remains byte-stable at 17 rows. No contract or experiment ran, and
no correctness, relation, representation, theorem receipt, or validator result is a
breakthrough.

The `206`–`217` mechanism pass is recorded in
[DEDUP-20260718T053328-0700.md](reviews/DEDUP-20260718T053328-0700.md), with fresh
independent findings in
[REDTEAM-20260718T053556-0700.md](reviews/REDTEAM-20260718T053556-0700.md). Strict
operation-level and primary-literature review preserves all twelve as semantic merges or
scoped negatives; there is no active or deferred survivor. The strongest borderline,
principal-pivot router `212`, is scoped-rejected because odd skew principal minors vanish
and nonzero-minor feasibility is open while exact five-sum equality is closed; auxiliary
coding layers restore source state. A late independent P1530 R1-R2 audit passes its
scoped type-1 reconstruction, makes P1530 terminal inconclusive, and isolates a distinct
partial elliptic-period type-2 successor; both Gallant types remain controls for `209`. Relative
top-lane contracts for conservative `209`, high-risk `211`, and representation-changing
`212` are retired, `review_required`, unapproved, and permit zero experiment and handoff
runs. The complete corpus is now 17 active proposed/unapproved, 27 deferred, and 173
rejected records across exact IDs `001`–`217`, with nine active and 47 retired contracts.
The active-only `idea_registry.tsv` remains byte-stable at 17 rows. No contract or
experiment ran, and no correctness, relation, representation, theorem receipt, validator
result, or toy scalar is a breakthrough.

The `218`–`229` mechanism pass is recorded in
[DEDUP-20260718T063126-0700.md](reviews/DEDUP-20260718T063126-0700.md), with fresh
independent findings in
[REDTEAM-20260718T064451-0700.md](reviews/REDTEAM-20260718T064451-0700.md). Strict
operation-level and primary-literature review preserves all twelve records as semantic
merges or scoped negatives; there is no active or deferred survivor. Zigzag barcode
lift `218` loses generators and exact source labels, RSK router `219` needs the recording
tableau/source word, and twisted torsion `220` consumes a based source complex and
retains basis/unit ambiguity. Live P1532 R1 closes admitted row-producing and
constant-recurrence forms of `221` while correctly leaving a distinct, uninstantiated
P1533 collision-resultant interface open; that interface supplies no Gauss/gamma digit
map. Relative top-lane contracts for
representation-changing `218`, conservative `219`, and high-risk `220` are retired,
`review_required`, unapproved, and permit zero experiment and handoff runs. The complete
corpus is now 17 active proposed/unapproved, 27 deferred, and 185 rejected records
across exact IDs `001`–`229`, with nine active and 50 retired contracts. The active-only
`idea_registry.tsv` remains byte-stable at 17 rows. No contract or experiment ran, and
no correctness, relation, representation, theorem receipt, validator result, or toy
scalar is a breakthrough.

The `230`–`241` mechanism pass is recorded in
[DEDUP-20260718T073057-0700.md](reviews/DEDUP-20260718T073057-0700.md), with independent
findings in
[REDTEAM-20260718T073638-0700.md](reviews/REDTEAM-20260718T073638-0700.md). A complete
ledger, idea-corpus, and 23-operation literature screen left no active or deferred
survivor. All twelve proposed named mechanisms are preserved as semantic merges or
scoped negatives because each named transform acts only after a source-labelled graph,
operator, stratification, complex, matroid, sheaf, current ensemble, lattice, factor
graph, or measurement family is supplied, or it returns an aggregate without a
canonical exact-point inverse. The noncommutative-Hankel backend was rejected before ID
allocation as an exact IDEA-120/142 merge and replaced by the distinct random-current
switching operation under `238`; no prior evidence was overwritten. Relative top-lane
contracts for conservative `230`, representation-changing `231`, and high-risk `233`
are retired, `review_required`, unapproved, and permit zero experiment and handoff runs.
The complete corpus is now 17 active proposed/unapproved, 27 deferred, and 197 rejected
records across exact IDs `001`–`241`, with nine active and 53 retired contracts. The
active-only `idea_registry.tsv` remains byte-stable at 17 rows. P1533-R2 remains
rho-scale/scoped-inconclusive, while P1534 remains IDEA-158/P1515 theorem-gate territory;
neither is a cohort novelty. No contract or experiment ran, and no correctness,
relation, representation, theorem receipt, validator result, or toy scalar is a
breakthrough.

The `242`–`253` mechanism pass is recorded in
[DEDUP-20260718T084037-0700.md](reviews/DEDUP-20260718T084037-0700.md), with independent
findings in
[REDTEAM-20260718T084919-0700.md](reviews/REDTEAM-20260718T084919-0700.md). Complete
operation-level, live-ledger, and primary-literature review preserves all twelve as
semantic merges or scoped negatives; there is no active or deferred survivor. The
strongest provisional candidate, coloured norm-jet tower `242`, is an exact
IDEA-195/P1536/P1537 merge: P1537 proves the seven-channel transport interface but
retains `B^5` leaves, `B^3` state, or whole-fiber first-jet loss, and already routes the
remaining finite-state closure question jointly to IDEA-195/102. Relative top-lane
contracts for representation-changing `242`, conservative `244`, and high-risk `250`
are retired, `review_required`, unapproved, and permit zero experiment and handoff runs.
The complete corpus is now 17 active proposed/unapproved, 27 deferred, and 209 rejected
records across exact IDs `001`–`253`, with nine active and 56 retired contracts. The
active-only `idea_registry.tsv` remains byte-stable at 17 rows. No contract or
experiment ran, and no correctness, relation, representation, theorem receipt,
validator result, or toy scalar is a breakthrough.

The `254`–`265` mechanism pass is recorded in
[DEDUP-20260718T093257-0700.md](reviews/DEDUP-20260718T093257-0700.md), with independent
findings in
[REDTEAM-20260718T093524-0700.md](reviews/REDTEAM-20260718T093524-0700.md). Complete
operation-level, live-ledger, and primary-literature review preserves all twelve records
as semantic merges or scoped negatives; there is no active or deferred survivor. P1539
supplies a correct thin singular-transversal-minor predicate but no sub-`B^1.25` row
locator. The new condensation, incidence-form, circuit-polynomial, matroid-intersection,
reverse-derivative, moment-tensor, theta, invariant, centralizer, p-adic, and
higher-residue operations either consume the missing source-side object, lose point
provenance, retain source-sized state, or vanish on a scalar-compatible prime-to-`p`
subgroup. Relative top-lane contracts for conservative `254`, representation-changing
`255`, and high-risk `263` are retired, `review_required`, unapproved, and permit zero
experiment and handoff runs. The complete corpus is now 17 active proposed/unapproved,
27 deferred, and 221 rejected records across exact IDs `001`–`265`, with nine active and
59 retired contracts. The active-only `idea_registry.tsv` remains byte-stable at 17
rows. No contract or experiment ran, and no correctness, relation, representation,
theorem receipt, validator result, or toy scalar is a breakthrough.

The `266`–`277` mechanism pass is recorded in
[DEDUP-20260718T114206-0700.md](reviews/DEDUP-20260718T114206-0700.md), with independent
findings in
[REDTEAM-20260718T114946-0700.md](reviews/REDTEAM-20260718T114946-0700.md). Complete
operation-level, live-ledger, and primary-literature review preserves all twelve records
as semantic merges or scoped negatives; there is no active or deferred survivor.
The 13-file ledger delta that arrived after allocation is preserved separately in
[LATE-LEDGER-20260718T120418-0700.md](reviews/LATE-LEDGER-20260718T120418-0700.md);
its structured-factor-base, incidence, richness, and noncommutative-path evidence
requires no cohort repair.
Equiproj decomposition, Loewner realization, multiplicity decoding, Mordell-Weil
sieving, prismatic and cyclotomic transfers, shtuka and oper spectra, Mather-Yau
reconstruction, arc descent, theta tangent cones, and stable envelopes all consume a
missing source-side object, lose point provenance, retain source-sized state, or fail to
orient the prime-to-`p` scalar. P1540–P1542 sharpen the orbit, S-unit, and pairing-return
controls; P1543-R1 independently sharpens the global-lift arm to a height-zero torsion
lift or an unsolved nonlinear formal-kernel defect. Relative top-lane contracts for conservative
`266`, high-risk `270`, and representation-changing `276` are retired,
`review_required`, unapproved, and permit zero experiment and handoff runs. The complete
corpus is now 17 active proposed/unapproved, 27 deferred, and 233 rejected records
across exact IDs `001`–`277`, with nine active and 62 retired contracts. The active-only
`idea_registry.tsv` remains byte-stable at 17 rows. No contract or experiment ran, and
no correctness, relation, representation, theorem receipt, validator result, or toy
scalar is a breakthrough.

The `278`–`289` mechanism pass is recorded in
[DEDUP-20260718T122324-0700.md](reviews/DEDUP-20260718T122324-0700.md), with independent
findings in
[REDTEAM-20260718T123537-0700.md](reviews/REDTEAM-20260718T123537-0700.md). Complete
operation-level, live-ledger, and primary-literature review preserves all twelve records
as semantic merges or scoped negatives; there is no active or deferred survivor. The
provisional Grothendieck-Springer/cameral and Koopman routes were removed before
closeout as an IDEA-246 duplicate and a live TRA duplicate, respectively; the final
IDEA-278 inverse-scattering operation is distinct but still requires source-faithful
scattering data and a finite-field return. Moment quadrature, exterior sieving, weight
transforms, determinantal sampling, Euler-system and Cassels-Tate transfers, Jacobi
inversion, topological recursion, motivic wall crossing, nonabelian Hodge splitting,
and hyperbolic-cone sections likewise lose provenance, require supplied source-side
objects, pay source density, or materialize source-sized state. Late EQJ/JETB/TTN and
P1544-R1/P1545-R1/P1546 receipts do not change a disposition. Relative top-lane contracts for
representation-changing `278`, conservative `279`, and high-risk `287` are retired,
`review_required`, unapproved, and permit zero experiment and handoff runs. The complete
corpus is now 17 active proposed/unapproved, 27 deferred, and 245 rejected records
across exact IDs `001`–`289`, with nine active and 65 retired contracts. The active-only
`idea_registry.tsv` remains byte-stable at 17 rows. No contract or experiment ran, and
no correctness, relation, representation, theorem receipt, validator result, or toy
scalar is a breakthrough.

The `290`–`301` mechanism pass is recorded in
[DEDUP-20260718T132546-0700.md](reviews/DEDUP-20260718T132546-0700.md), with fresh
independent findings in
[REDTEAM-20260718T134111-0700.md](reviews/REDTEAM-20260718T134111-0700.md). Complete
operation-level, raw-ledger, cost, and primary-literature review preserves all twelve
records as semantic merges or scoped negatives; there is no active or deferred
survivor. The independent review repaired several source scopes and mathematical
boundaries, most importantly preserving HKR `ell_HKR=N` as allowed but uninstantiated
rather than closing it by a prime-to-characteristic argument. Relative top-lane
contracts for conservative `290`, representation-changing `296`, and high-risk `300`
are retired, `review_required`, unapproved, and permit zero experiment and handoff
runs. P1547/P1548 remain scoped additive/section controls. P1549 completes a
theorem-only scoped-inconclusive IDEA-195 gate: explicit path expansion, global edge
scans, and B^3 provenance fail, while an unsupplied O(D) locator survives only for
`11/12<=gamma<=1`. P1550 closes the globally rational realization of that locator:
one branch captures at most `B` targets independently of degree, explicit catalogs
cost at least `N` for relation collection, and explicit finite-domain rational
branches need degree at least `B^(11/4)`. A dense factor polynomial nevertheless gives
a valid generic-prime `O(B)` one-step membership and source-lift control. P1551 closes
the frozen compact finite-field grammar: the equality mask is the P1536 pointwise
projector, rank-two gates require supplied edges, and every admitted source-faithful
aggregation restores at least `B^3` represented traffic or the full `B^5` quotient.
Its exact endpoint-convolution coefficient identity is a normal form, not an extractor;
unrestricted circuits remain outside the scoped theorem. P1552 assigns only an
operation-level corpus rerank and forbids relabeling the existing coefficient oracle as
a new candidate. Later STR and
NET toy triplets are negative solver/representation controls; BKKMV is neutral
mixed-volume evidence that saturates the multigraded box bound. None supplies a
cohort endpoint-to-source mechanism. The complete corpus is now 17 active
proposed/unapproved, 27 deferred, and 257 rejected records across exact IDs
`001`–`301`, with nine active and 68 retired contracts. The active-only
`idea_registry.tsv` remains byte-stable at 17 rows. No contract or experiment ran,
and no correctness, relation, representation, theorem receipt, validator result, or
toy scalar is a breakthrough.

The pre-ID `20260720-c` mechanism screen is recorded in
[DEDUP-20260720T121629-0700.md](reviews/DEDUP-20260720T121629-0700.md), with independent
working-tree content review in
[REDTEAM-20260720T122506-0700.md](reviews/REDTEAM-20260720T122506-0700.md). Twelve
complete records screen Hopcroft DFA minimization, splay trees, Cartesian-tree RMQ,
treaps, B-trees, R-trees, Fibonacci heaps, Boyer–Moore search, Gale–Shapley deferred
acceptance, Stoer–Wagner min-cut, PageRank, and Rauch–Tung–Striebel smoothing. The
native operations are distinct, but every elliptic transplant consumes a supplied
source-bearing automaton, key set, array, record set, spatial object set, graph,
preference list, text, or state model, or loses exact occurrence provenance. None
constructs P1553 R4's endpoint-derived subset-stable exact Query2P1/common-factor
decision with charged replay, logs, and blind descent. No canonical ID was allocated;
the exact `001`–`410` coverage, 17 active, 27 deferred, 366 rejected, nine active
contracts, 97 retired canonical contracts, and 17-row active registry remain
unchanged. Relative conservative G03, representation-changing G06, and high-risk G12
snapshots are retired `.yaml.txt` records with zero budgets and empty write scopes.
The prospective cohort artifact root is absent and nothing ran. The independent PASS
is scoped to the untracked working-tree snapshot at HEAD `8e8d0f1`; it is not a
Coordinator-committed archival review. No correctness, relation, index, cut, score,
trajectory, validator pass, or toy scalar is a breakthrough.

The pre-ID `20260720-d` mechanism screen is recorded in
[DEDUP-20260720T151603-0700.md](reviews/DEDUP-20260720T151603-0700.md), with independent
working-tree review in
[REDTEAM-20260720T153805-0700.md](reviews/REDTEAM-20260720T153805-0700.md). Twelve
complete records screen PATRICIA path compression, Fenwick prefix accumulation,
Dinitz blocking flow, Johnson reweighting, A-star, Tutte/Lovasz randomized matching,
Metropolis-Hastings, simulated annealing, Gibbs sampling, expectation-maximization,
DBSCAN, and Lloyd quantization. The native operations are distinct, but every elliptic
transplant consumes supplied source keys, arrays, compatibility graphs, heuristics,
densities, energies, conditional supports, likelihoods, catalogues, or vectors; or
loses exact occurrence provenance. None constructs P1553 R4's endpoint-derived
subset-stable exact source return with charged relation collection, rank, factor logs,
and scalar-blind descent. No canonical ID was allocated; exact `001`-`410` coverage,
17 active, 27 deferred, 366 rejected, nine active contracts, 97 retired canonical
contracts, and the 17-row active registry remain unchanged. Relative conservative
H02, representation-changing H04, and high-risk H06 snapshots are retired `.yaml.txt`
records with zero budgets and empty write scopes. Independent review upheld all
twelve semantic dispositions but returned REVISE because the exact reviewed package
has no preceding Coordinator snapshot commit; it is content-valid working-tree
negative evidence, not a durable claim transition. No artifact root, run, P1554,
lower bound, scalar recovery, or breakthrough was created.

The pre-ID `20260723-a` numerical-method mechanism screen is preserved in
[DEDUP-20260723T184854-0700.md](reviews/DEDUP-20260723T184854-0700.md). Twelve complete
records test Hestenes–Stiefel conjugate gradients, Saad–Schultz GMRES, Brandt
multigrid, Hutchinson trace probes, Halko–Martinsson–Tropp randomized range finding,
Oja principal-component updates, Karmarkar projective LP optimization, the
Grötschel–Lovász–Schrijver ellipsoid method, Beck–Teboulle mirror descent,
Gabay–Mercier splitting, Littlestone–Warmuth weighted majority, and
Auer–Cesa-Bianchi–Fischer UCB.

Every ECDLP transplant consumes a supplied operator, hierarchy, objective, separator,
proximal component, expert pool, reward stream, or approximate aggregate; none
constructs P1553 R4's endpoint-derived subset-stable exact source return with charged
signed replay, relation rank, factor logs, and fresh scalar-blind descent. All twelve
therefore remain full pre-ID merged/scoped rejections with no canonical or deferred
allocation. Relative conservative R01, representation-changing R03, and high-risk R12
snapshots remain retired, unapproved, zero-run `.yaml.txt` records with empty write
scopes. The active registry remains byte-stable at 17 rows, and the prospective
artifact root is absent.

Initial independent review in
[REDTEAM-20260723T184509-0700.md](reviews/REDTEAM-20260723T184509-0700.md) upheld every
semantic disposition but returned `REVISE` for a concurrent ledger/index rewrite and
stale corpus receipts. The corrected-byte successor review is preserved in
[REDTEAM-20260723T190000-0700.md](reviews/REDTEAM-20260723T190000-0700.md); its verdict
governs. Any content pass remains `REVISE_NOT_DURABLE` until a verified Coordinator
snapshot commit binds the reviewed bytes. No experiment, relation campaign, scalar
recovery, lower bound, or breakthrough was created.

The pre-ID `20260723-b` sampling/statistical-mechanics mechanism screen is preserved in
[DEDUP-20260723T211405-0700.md](reviews/DEDUP-20260723T211405-0700.md), with independent
working-tree review reserved at
[REDTEAM-20260723T213000-0700.md](reviews/REDTEAM-20260723T213000-0700.md). Twelve complete
records test Duane Hamiltonian Monte Carlo, Jordan mean-field variational inference,
Swendsen–Wang replica tempering, Wang–Landau density-of-states sampling, Neal slice
sampling, Smith hit-and-run, Roberts–Tweedie Langevin diffusion, Skilling nested
sampling, Pritchard approximate Bayesian computation, Torrie–Valleau umbrella
sampling, Braunstein–Mézard–Zecchina survey propagation, and Rubinstein's
cross-entropy method.

The native operations are distinct, but every ECDLP transplant requires a supplied
density, energy, gradient, factor graph, simulator, likelihood constraint, convex
membership oracle, reaction coordinate, score, or source-bearing transition model;
or returns an approximate/aggregate distribution without exact signed occurrence
replay. None constructs P1553 R4's endpoint-derived subset-stable exact source return
with charged relation rank, factor logs, and fresh scalar-blind descent. All twelve
therefore remain full pre-ID merged/scoped rejections with no canonical or deferred
allocation. Relative conservative S05, representation-changing S02, and high-risk S01
snapshots are retired, unapproved, zero-run `.yaml.txt` records with empty write
scopes. The active registry remains byte-stable at 17 rows, the prospective artifact
root is absent, and no experiment or contract ran. Correct sampling, convergence,
relation validity, a validator pass, or a toy scalar is not a breakthrough.

The pre-ID `20260724-a` coding/network mechanism screen is preserved in
[DEDUP-20260724T001356-0700.md](reviews/DEDUP-20260724T001356-0700.md), with independent
working-tree review reserved at
[REDTEAM-20260724T003000-0700.md](reviews/REDTEAM-20260724T003000-0700.md). Twelve
complete records test Koetter–Vardy soft-decision multiplicity assignment,
Sipser–Spielman expander bit flipping, Luby LT peeling, Shokrollahi Raptor
precoding, Berlekamp–Welch error-location interpolation, Prange
information-set decoding, Wagner generalized-birthday merging,
Koetter–Kschischang subspace decoding, Forney concatenated decoding,
Fossorier–Lin ordered-statistics decoding, Duffy–Li–Médard GRAND, and
Koetter–Médard algebraic network coding.

The native operations are distinct, but every ECDLP transplant consumes a
supplied received word, reliability matrix, sparse graph, precode, syndrome,
explicit list, subspace, inner/outer code, noise law, membership oracle,
network topology, packet family, or transfer polynomial; or loses exact
signed occurrence identity through linear mixing, span/basis quotienting, or
aggregate decoding. None constructs P1553 R4's endpoint-derived subset-stable
exact source return with charged replay, relation rank, factor logs, and fresh
scalar-blind descent. All twelve therefore remain full pre-ID merged/scoped
rejections with no canonical or deferred allocation. Relative conservative
T05, representation-changing T08, and high-risk T12 snapshots are retired,
unapproved, zero-run `.yaml.txt` records with empty write scopes. The
17-row active registry remains byte-stable, the prospective artifact root is
absent, and no experiment or contract ran. Correct native decoding, a valid
relation, transfer rank, a validator pass, or a toy scalar is not a
breakthrough.

The pre-ID `20260724-b` exact-linear-algebra mechanism screen is preserved in
[DEDUP-20260724T031259-0700.md](reviews/DEDUP-20260724T031259-0700.md), with
independent working-tree review reserved at
[REDTEAM-20260724T033000-0700.md](reviews/REDTEAM-20260724T033000-0700.md).
Twelve complete records test Wiedemann coordinate recurrences, Coppersmith
block Wiedemann, Coppersmith block Lanczos, Massey shift-register synthesis,
Keller–Gehrig Frobenius canonicalization, Berkowitz division-free
characteristic circuits, Bareiss fraction-free elimination, Dixon p-adic
lifting, Kannan–Bachem Smith reduction, Storjohann–Labahn Hermite reduction,
Jeannerod–Neiger shifted-Popov approximant bases, and Faddeev–LeVerrier trace
and adjugate recursion.

The native operations are distinct, but every ECDLP transplant consumes a
supplied source-bearing matrix, operator, vector sequence, equation system,
lattice, basis, or interpolation instance; forgets exact signed occurrence
labels through similarity, quotient, trace, recurrence, nullspace, or
canonical-form aggregation; or swaps a downstream solver after the missing
source representation exists. None constructs P1553 R4's endpoint-derived
subset-stable exact source return with charged replay, relation rank, factor
logs, and fresh scalar-blind descent. All twelve therefore remain full pre-ID
merged/scoped rejections with no canonical or deferred allocation. Relative
conservative U07, representation-changing U09, and high-risk U11 snapshots are
retired, unapproved, zero-run `.yaml.txt` records with empty write scopes. The
17-row active registry remains byte-stable, the prospective artifact root is
absent, and no experiment or contract ran. Correct linear solving, a matrix
invariant, canonical form, nullspace, valid relation, validator pass, or toy
scalar is not a breakthrough.

The pre-ID `20260724-c` classical computational-number-theory mechanism screen
is preserved in
[DEDUP-20260724T101929-0700.md](reviews/DEDUP-20260724T101929-0700.md). Initial
independent working-tree review in
[REDTEAM-20260724T103000-0700.md](reviews/REDTEAM-20260724T103000-0700.md)
returned `CONTENT REVISE` solely because V01 and the producer report
misattributed arXiv:1105.1456. Those producer bytes now name Jan-Christoph
Schlage-Puchta correctly; corrected-byte successor review is reserved at
[REDTEAM-20260724T105500-0700.md](reviews/REDTEAM-20260724T105500-0700.md).
That successor returned `CONTENT REVISE` because V02, V04, and the producer
report misattributed DOI 10.1587/transfun.E96.A.1081. Those producer bytes now
name Ryuichi Harasawa, Yutaka Sueyoshi, and Aichi Kudo correctly; final
corrected-byte review is reserved at
[REDTEAM-20260724T110500-0700.md](reviews/REDTEAM-20260724T110500-0700.md).
Twelve complete records test Tonelli–Shanks two-Sylow root descent, Cipolla
quadratic-extension roots, Cornacchia norm descent, Adleman–Manders–Miller
`r`-th-root extraction, Pollard `p-1`, Williams `p+1`, Morrison–Brillhart
CFRAC, Pomerance's quadratic sieve, Lenstra ECM, Pocklington certificates,
Goldwasser–Kilian elliptic certificates, and Atkin–Morain ECPP.

The native operations are distinct, but every ECDLP transplant consumes a
supplied residue, radicand, norm instance, composite, quadratic irrational,
sieve polynomial, partial factorization, or auxiliary curve/order
certificate; loses exact signed occurrence labels through roots, smoothness,
parity, gcd, order, or certificate aggregation; or repeats H077's auxiliary
ECM smooth-order transplant. None constructs P1553 R4's endpoint-derived
subset-stable exact source return with charged replay, relation rank, factor
logs, and fresh scalar-blind descent. All twelve therefore remain full pre-ID
merged/scoped rejections with no canonical or deferred allocation. Relative
conservative V01, representation-changing V09, and high-risk V12 snapshots are
retired, unapproved, zero-run `.yaml.txt` records with empty write scopes. The
17-row active registry remains byte-stable, the prospective artifact root is
absent, and no experiment or contract ran. Correct roots, factors, smooth
values, parity dependencies, curve orders, certificates, valid relations,
validator passes, or toy scalars are not breakthroughs.

## Required interpretation boundary

- A verifier pass establishes only implementation correctness for the tested artifact.
- A relation, correspondence, or homomorphism certificate is not a speedup by itself.
- Toy effects are not crypto-scale validation.
- Promotion requires the complete precomputation, relation, linear-algebra, target-descent,
  verification, and memory exponents to beat both rho and BSGS under matched accounting.
- A toy gate can promote only to a larger scaling study; finite-size slope confidence is
  still model-bound and cannot establish a cryptographic asymptotic.
- Negative evidence closes only the exact stated test boundary.

The `434`–`436` pass (cohort `20260809-a`) was generated from the
[GATHER-20260809](../knowledge/gathers/GATHER-20260809.md) local-corpus sweep rather
than from a free-generation round, so it is small and source-anchored: one
representation-changing record, one conservative control record, and one high-risk
mechanism record. Two of the three are
deliberately *cheap discriminators over evidence this program already holds* rather
than new constructions — `435` audits the existing `EV-XEDN-*` relations for a target
coefficient, and `436` is gated on a generic-group simulability memo that may reject it
without any run. The same sweep produced two scoped negatives that were filed as
findings instead of ideas, because they are settled by counting rather than by
experiment: `KN-TECH-3b593f` (post-SIDH higher-dimensional isogeny machinery does not
reach genus 1) and `KN-TECH-73630e` (the local-torsion lifting face is closed for
group-theoretic invariants). The corpus is now 18 active proposed/unapproved records.
No experiment ran. Only the Coordinator may approve a contract or change an official
state.

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
