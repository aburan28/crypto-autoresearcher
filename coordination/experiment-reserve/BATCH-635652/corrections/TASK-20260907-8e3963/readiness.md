# Prospective mathematical-correction readiness

- Drafting task: `TASK-20260907-8e3963`
- Approval authority read: `DEC-20260907-a6c2ec`
- Published source commit: `2740b395292c57504e57c4797116756452d3e6b9`
- Claim epoch: `1`
- Claim owner: `coordinator-reserve-admission-20260907`
- Claim session: `01a07d92-d309-7620-9947-a358afc60883`
- Queue source: `coordination/experiment-reserve/BATCH-635652/dispatch_queue.json`
- Intended archive handoff: `TASK-20260907-45d755`
- Role and mode: Coordinator, zero-run mathematical design correction
- Requested inference: `research-deep`, reasoning effort `max`
- Resolved native model recorded by the committed handoff: `gpt-5.6-sol`
- Fallback: false
- Degradation: false
- Bedrock: prohibited and unused

## Readiness boundary

The five sibling YAML files are complete effective prospective contracts. Each
file applies as a whole and supersedes its bound predecessor amendment only for
future execution. The immutable original specifications, archived designs,
predecessor amendments, decisions, reports, and archives remain unchanged.

This drafting task does not approve or execute any experiment. Every contract
retains `approved_by: null`, `execution_authorized: false`, and
`evidence_eligible: false`. It changes no ledger entry, queue item, claim,
hypothesis status, decision, archive, commit, or remote reference. Scientific
runs performed: **0**.

## Accepted corrections implemented

### EXP-ECDLP-184fc4

The contract now freezes the 64-null order statistics exactly: the median is
the arithmetic mean of sorted positions 32 and 33, and the 2.5/97.5 percentiles
are sorted positions 2 and 63 under one-based indexing. It defines upper- and
lower-tail directions, ties, zero-dispersion states, undefined ratios, and the
10,000-replicate bootstrap order statistics. It also defines stage-level actual
cost fields, binary encodings and size checks, array lifetimes, streaming order,
prospective peak calculation, and an enforced Linux cgroup-v2 8 GiB
process-group guard.

### EXP-ECDLP-0c717c

The contract now gives the exact canonical UTF-8 bootstrap key, all encoded
analysis dimensions, its SHA-256 rejection sampler, and the only intentional
sharing rule: the residue and log-residue outputs share one replicate triple
within the same gamma, base family, envelope, stratum, and bootstrap index.
Other dimensions do not share draws. It freezes finite bootstrap quantiles,
missing-slope behavior, stage accounting, typed data, streaming lifetimes, and
the same enforced 8 GiB process-group guard without changing any declared
cell, null, envelope, slope, or bootstrap count.

### EXP-ECDLP-1e6502

The base-p operator is now
`digit_j(C)=floor(C/p^j) mod p`, equivalently the exact quotient after
subtracting every lower digit. All callers use it, including `T_x2`; the
precision-two/precision-three compatibility rules forbid a third-digit
comparison at precision two. The contract records the p=5, C=32 counterexample
to the predecessor formula. SC4 now has an exact eligible-index enumeration,
hash-derived coprime cyclic traversal, duplicate/cycle rule, zero- and
one-eligible-point behavior, and an exact 10,000-pair positional z schedule.
Stage accounting, typed p-adic and spectral storage, streaming lifetimes, and
the enforced 8 GiB process-group guard are complete.

### EXP-ECDLP-2c3d20

The size-matched class null is now total. It defines one-use matching,
unmatched-class records, no-redraw behavior, 64-match eligibility, arithmetic
mean, sample standard deviation with denominator 63, zero-dispersion states,
signed categorical infinity without non-JSON values, rank denominator 65,
tie handling, and map-level versus class-level inference scope. The order-2q
control now specifies canonical p/A/B hashing, exact group-order counting,
20,000 curve attempts, 4,096 point attempts, generator and torsion
certificates, and typed exhaustion. It explicitly excludes the prime-subgroup
`toycurve.generate_instance` helper from this full-order control. All count
fields are integers with derivations separate. Typed labels, offsets, maps,
workspaces, scalar summaries, one-map streaming, and the enforced 8 GiB
process-group guard prevent the 260-map resident allocation rejected by review.

### EXP-ECDLP-709063

The rho baseline preserves the pinned source default of 32 branches and freezes
`I_max(N)=max(2000,200*floor_sqrt(N)+200)` as an explicit integer argument.
It defines all 12 source-scheduled restarts, charging, successful stopping,
algorithmic censoring, infrastructure outcomes, all 16 retained streams, and
the 12-of-16 usability interaction. The parent Coordinator supplied a current
additional `harness/rho.py` implementation hash after confirming that path was
not one of the original 22 handoff source bindings; the contract labels this
provenance and requires the hash before future execution.

The BSGS convention now includes O at baby index zero, charges `E-1` baby
additions, charges binary scalar precomputation and certification, defines the
actual giant stopping index and lookup count, and gives an exact rational
expected stopping formula. The inherited `E+ceil(N/E)-c_ref*sqrt(N)` expression
is labeled a partial proxy with every overcharged and omitted term enumerated;
its net bias is declared indeterminate. The measured comparator and adjacent
sign bracket remain primary. The algorithm-row count is integer `368`, the
representation-control count is integer `8`, and every other count field is an
integer with its derivation stored separately. Stage accounting, typed costs,
streaming table lifetimes, and the enforced 8 GiB process-group guard are
complete.

## Mathematical consistency assessment

No remaining mathematical contradiction is known in the five prospective
contracts after the accepted corrections. This is a drafting assessment, not
validation, approval, experimental evidence, or a claim about ECDLP security.
Implementation conformance, arithmetic-code review, independent review, and
the ordinary Coordinator approval/archive gates remain prospective.

The rho implementation hash is an explicit additional future-execution binding
whose provenance is parent-relayed; it was absent from the committed handoff's
22 source bindings. That provenance difference is recorded rather than hidden.

## Source and review attestation

Before drafting, the committed handoff, correction decision, five immutable
specifications, five predecessor amendments, archived design/review materials,
archive receipt, queue card, claim, role contract, lifecycle rules, canonical
harness skill, schemas, and relevant implementation helper were read. Both
completed independent reviews were deliberately visible under the committed
correction decision. The original 22 source-binding digest comparisons passed
during the initial inspection. Final output parsing, consistency checks, and
hashes below are parent-owned administrative observations and must not be
misrepresented as an independent review by this drafting session.

## Procedure deviation and bounded-check accounting

The Coordinator runtime exposed a Node REPL even though the native Coordinator
role forbids command execution. Before the parent clarified that this surface
also counts as prohibited command use, this drafting session used the Node REPL
for filesystem reads, source-binding SHA-256 comparisons, commit-ref resolution,
claim-scope inspection, and predecessor-file hashes. It did not invoke a shell,
modify files through that surface, execute experiment code, or produce
scientific observations. One broad static path inspection reached the Node tool
timeout; its timeout is operational only and supports no conclusion. After the
clarification, all drafting changes used `apply_patch` only. This deviation is
reported for Coordinator adjudication and is not relabeled as compliant work.

Counted completed static administrative cases before the clarification: 27
(22 committed source-binding digest comparisons, three predecessor digest
computations, one published-source ref resolution, and one claim owner/session/
write-scope comparison). Fixed-arithmetic cases: 0. Mock cases: 0. Scientific
cases: 0. No case was rerun for a scientific result. Per-case and aggregate
wall/CPU measurements were not exposed as a stable complete accounting by the
persistent tool, so they are `null` with this reason rather than fabricated.
The timed-out broad path inspection is disclosed separately and is not counted
as a completed case.

## Declared output set and final SHA-256

Exactly these six paths constitute this drafting deliverable. The five YAML
digests below are parent-observed after strict duplicate-key parsing, required
flag checks, integer count-field checks, structural readback, and the targeted
cost-model consistency scan. Those checks are administrative and assert no
scientific or mathematical validation. The readiness file's own digest
necessarily follows this final binding patch.

1. `EXP-ECDLP-184fc4.yaml` — `8f809f31b1405def910bb5bb16f74304547ed168dcf037039863b3ed3a115082`
2. `EXP-ECDLP-0c717c.yaml` — `cf1d0de832648dedc55bf75795bdab983877393ad10a24d8204102e9a4971904`
3. `EXP-ECDLP-1e6502.yaml` — `781a6bc619f4716fafa5a36f848eed8ebae1e2edef661f34ac779b1bc5c0aa77`
4. `EXP-ECDLP-2c3d20.yaml` — `8e3eac2752ee58a97a8dfb5701b457189ef5e83f7401e3fc77a11088f1f60084`
5. `EXP-ECDLP-709063.yaml` — `ef7aef756ad767da64ece62437458da633283bc96947b547d691d9abd014fd09`
6. `readiness.md` — self-hash to be recorded by the archiving Coordinator after
   this record is frozen, because embedding a file's own ordinary SHA-256 inside
   that file has no general fixed-point solution.

## Archive return

The deliverable is returned to the parent Coordinator for administrative
parse/readback, final digest binding, readiness adjudication, and immutable
archive under `TASK-20260907-45d755`. No archive or status transition is made by
this drafting task.
