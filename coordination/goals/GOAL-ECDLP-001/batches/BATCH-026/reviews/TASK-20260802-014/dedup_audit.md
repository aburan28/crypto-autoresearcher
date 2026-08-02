# TASK-20260802-014 independent deduplication audit

**Verdict: `ZERO_SURVIVORS`.** The committed BATCH-026 producer disposition is
independently supported for all five exact pre-ID objects. This is a bounded
cohort verdict, not closure of `RQ-ECDLP-002`, `GOAL-ECDLP-001`, generic
ordinary prime-field ECDLP, or the tracked-object search space.

No canonical `ECDLP-IDEA-*` id is warranted. No experiment ran, no producer
artifact was repaired, and no ledger, queue, goal, staging area, or commit was
changed by this review.

## Committed-byte binding

Snapshot `01f4aedcb7a9db220b1ce68d0ebc5af52313ff2b` is reachable from
review HEAD `ec1e3f5103662973ee62180a192acc0cc873aaf5` and has the sole parent
`b3f5281cdb10049f8e8dce997f02433d860ea942`. Its delta is exactly three added
paths:

| Path | SHA-256 of committed bytes |
|---|---|
| `.../TASK-20260802-012/idea_cohort.yaml` | `bbfe6393844064f27431fb8f883025e1ef137df5ca05ed805c148bcd3865b1b6` |
| `.../TASK-20260802-012/semantic_dedup.md` | `e9f86c348e0eadbc04818ce45839cdbb2f9afad7bfa38db59eeef6797224a6f8` |
| `.../TASK-20260802-013/snapshot_commit_receipt.json` | `750777fed8d0c3a9cba790405aefdeda7a2aa2aa7c67e3abf71b6f7dcf42c7fe` |

The receipt's internal `commit_sha: null` is intentional: it delegates the
post-commit binding to `dispatch_queue.json`, which records the same commit,
parent, paths, and hashes. Hashes above were recomputed from Git object bytes,
not copied from the producer and not read from working-tree copies.

## Complete corpus recheck

Git-tree enumeration independently reproduces the producer receipt: 1,105
tracked substantive `ideas/` files, 922 `ledger/` files, and 7,766 `knowledge/`
files. The canonical IDEA set is gap-free `001..410`: 17 active, 27 deferred,
366 rejected, and 17 active registry data rows. No AppleDouble path enters
these counts.

Operation-level `git grep` scanned every tracked byte in those three trees.
The five broad screens matched 61 orbit-word/delay/inversion files, 118
Kummer/x-only/deck files, 39 Hasse-jet/principal-part files, 23
isogeny/factor-base/atlas files, and 116 six-list/exterior/tensor files.
Targeted reads then covered the closest canonical, deferred, rejected,
theorem-gate, evidence, finding, and preserved input-ledger records.

One useful refinement emerged: rejected `ECDLP-IDEA-268` is the closest exact
operation-level neighbor to B21-P03's source-Hasse-jet premise. The producer's
IDEA-004/068/160 and `EV-JET-001` anchors are relevant but less direct. This
neighbor-list omission does not rescue P03. `ISO-CW-NR-001` is correctly
recoverable from the preserved input-ledger snapshots named in the producer
receipt even though it is not a file in the structured `ledger/` subtree.

## Primary-literature and lower-bound boundary

The independent primary-source pass checked Shoup's
[generic lower bound](https://www.shoup.net/papers/dlbounds1.pdf), the official
[Structured Generic-Group Model](https://eprint.iacr.org/2026/384) record,
Semaev's [summation-polynomial paper](https://eprint.iacr.org/2004/031.pdf),
Amadori–Pintore–Sala on
[prime-field ECDLP](https://eprint.iacr.org/2017/609.pdf), the Kummer
projection/sign-recovery pattern in
[Chung–Costello–Smith](https://eprint.iacr.org/2016/777), and the nearby
exterior-algebra witness technique of
[Koutis](https://doi.org/10.1007/978-3-540-70575-8_47).

The producer states the two lower-bound boundaries accurately, with one
important use restriction:

- Shoup is an `Omega(sqrt(N))` generic-model baseline, not a universal
  impossibility result against public curve encodings.
- Corrigan-Gibbs–Henzinger–Wu state
  `Omega(min(sqrt(q),1/delta))` in their precisely defined structured model.
  None of the five candidates computes the paper's `delta` or proves that its
  oracle fits that interface. The result is therefore a control, not a turnkey
  rejection.

In particular, this audit does not reject P03 by asserting that coordinates or
jets are available in strict Shoup GGM. It rejects P03 because no exact
source-sensitive interface, selectivity theorem, or complete attack path is
supplied. The checked prime-field literature gives relation equations and
solver routes but no complete sub-rho path for any B21 object; the 2017 paper
itself says further work is needed to improve on Pollard rho. Absence from the
literature is not used as novelty proof.

## Candidate-specific audit

| Handle | Independent object/operation finding | Semantic and Pareto finding | Cheapest decisive falsification |
|---|---|---|---|
| `B21-P01` | The public word is well-defined, but at most `2^(s*w)` words cover `N` positions. Its average fibre is at least `N/2^(s*w)`, and singleton probability is at most `2^(s*w)/N`. Thus H1 is false for `s*w=o(log N)`; a nearly injective word still lacks a scalar inverse. | Duplicate of the orbit observer/inversion lane (`IDEA-011`, `329`, `374`). No build, inverse, amplification, or sub-`1/2` cost exists. Supported SOTA delta is zero; rho dominates demonstrated ECDLP performance. | Prove the fibre bound before code. If a successor supplies compressed inversion, trace and charge every scalar-labelled advice bit. |
| `B21-P02` | The proposed deck is not a deterministic translation state. Symmetry gives `K_w(X)=K_w(-X)`, while generally `K_w(X+P) != K_w(-X+P)`. Ordering, sign, centre, or a backpointer restores the discarded orbit state. | Duplicate of `IDEA-010`, `057`, and `158`. Sign quotient is constant-size; the claimed `N^(1/3)` claw path has no correct update or source inverse. | The algebraic sign-symmetry counterexample is already a zero-run falsification; exhaustive toy orbits merely verify it. |
| `B21-P03` | Hasse composition transports a fixed public rational-function jet, but the row never specifies how a source tuple produces `X` or how the jet yields an exact, all-strata source-complete filter. Endpoint jets do not contain occurrence labels. | Duplicate of the public/source-jet lanes, most directly `IDEA-268`. Intended `N^0.4` time/memory and `N^0.2` data omit proved selectivity, recall, rank, factor logs, descent, and amplification. | Symbolically reduce the `h=1` jet equations modulo the base relation ideal, with frozen tuples and a degree/multiplicity-matched random-function null. Stop if no independent constraint remains or real/null selectivity is one. |
| `B21-P04` | Every degree-coprime isogeny is injective on the prime-order subgroup. Pulling each `F_i` back gives an ordinary base on an isomorphic copy of the same group. At fixed total base size and arity, chart partitions do not create a superconstant source-tuple budget. | Duplicate of the fixed-degree transfer/isogeny-atlas lane (`IDEA-002`, `057`, `ISO-CW-NR-001`, `KN-FIND-007`). The claimed `N^(1/6)` density/rank gain and `N^(1/3)` total omit arity, base exponent, solve cost, rank probability, factor logs, and descent. | Pull every base back through `phi_i` and prove the equal-total tuple count. Test a chart only after it names a different solver circuit, then use a matched held-out arithmetic DAG. |
| `B21-P05` | Exterior incidence is an exact predicate only after source-pair state exists. Rank/sketch truncation is not source-biconditional without the missing exact separator-rank and full-recall theorem. | Exact semantic duplicate of the P1539/P1552 exterior/tensor frontier and nearby `IDEA-050/052/056`. The arithmetic `B^2.25=N^0.45` setup and `B * B^1.25=N^0.45` campaign is only conditional on H1. Conditional `-0.05` is not supported SOTA. | Compute exact finite-field separator ranks and all-source recall on the smallest shape-complete real and matched-random tensors. Stop on one missed source or absent scaling gap. |

## Full cost, proof, controls, and Pareto result

All five rows state intended time and memory, name rho/BSGS, sketch
size/runtime/correctness/success lemmas, and include useful same-shape nulls.
Those are proposal fields, not results:

- P01's success assumption contradicts counting.
- P02 fails deterministic correctness before complexity analysis.
- P03 has no source interface on which correctness or selectivity can be
  stated.
- P04 has no density/rank theorem after equal-total pullback accounting.
- P05's size and correctness lemmas are exactly its unproved H1.

No numbered algorithm, proved lemma, per-attempt-cost times inverse-success
assembly, heuristic validation, standardized concrete-cost table, or
cryptographic-scale evidence exists. This is consistent with the declared
proposal-stage ceiling but supplies no admissible survivor.

The producer's Pareto accounting is honest: supported generic-ECDLP time,
memory, data/query, and security deltas are all zero. Its aggregate
`dominated_by: n/a (no result claimed)` is valid. P05's conditional target
delta remains visibly conditional and receives no SOTA credit.

## Scoped obstructions and forward guidance

The five rejections are not a fatigue closure. They establish only these
bounded obstructions:

1. Short orbit words have large fibres; injective words still need the missing
   inverse.
2. Unordered x-only decks alias states with different `+P` successors.
3. Public endpoint jets do not supply source-labelled occurrence leaves.
4. Injective isogeny transports and factor-base partitions do not create an
   exponent gain without a new solver or rank theorem.
5. Exact exterior sketches need the source-complete rank theorem that the
   sketch proposal assumes.

The cheapest next search is theorem-first: discharge P01, P02, and P04 by
counting/algebra; freeze P03's exact jet ideal before one symbolic real/null
screen; run P05 rank measurements only as a theorem-discovery screen with
exact source recall. A genuine successor must still provide a non-permutation
correspondence, nonhomomorphic source-free inverse, or exact rank theorem and
then complete relation rank, factor logs, blind masked-target descent, success
amplification, output verification, and peak memory below the matched
`0.45` rectangle.
