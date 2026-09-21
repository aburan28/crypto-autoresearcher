# Portfolio scan — new ideas and directions, 2026-08-07

> ## ⚠ `H-MLKEM-b477fd.draft.yaml` / `EXP-MLKEM-8cc1f2.draft.yaml` are SUPERSEDED — do not act on them
>
> These two files were this session's first-draft attempt at promoting
> `IDEA-20260807-abacec` (the Simon-DCP reach-map idea). Later the same day, a
> proper `/design-experiment` pass was run through the Coordinator, minting
> **fresh IDs** — `H-MLKEM-7f3a2c` and `EXP-MLKEM-9d41b6` — which were approved,
> frozen, committed, executed, and merged via
> [PR #224](https://github.com/aburan28/crypto-autoresearcher/pull/224). That
> run **fired STOP-1**: `KN-OPEN-8a5965`'s flagged `Q = k·n^{c+1}, c≥12`
> "concrete cost" example does not trace to any of the three governed primary
> sources — the `c≥12` figure traces instead to an unrelated erratum in that
> same open-problem entry's Q1 discussion, reused uncited in its Q2 section.
> See `RUN-MLKEM-9d41b6-001` on that branch for the full finding.
>
> These two draft files are kept here only as a historical record of the
> staging process, committed late (after the real work already landed) because
> they were sitting as genuinely uncommitted local content from earlier the
> same day and deleting undocumented work silently would be worse than keeping
> it with this note. **Do not design a new experiment from these — the
> question they target is already answered.** The rest of this directory
> (`proposals.draft.yaml`'s three ideas, and the portfolio-scan findings below)
> is NOT superseded and remains live.

Response to `/launch-research-harness find new ideas, new experiments and
directions to pursue`. **Not a batch run.** The portfolio is not empty (21
active goals, 12 draft, heavy concurrent multi-session activity visible on
`origin/main` during this scan — ECDLP, SSI, ENDO, AES-003, MTBK, Semaev
branches all had fresh commits within the hour), so this did not enter the
step-8 "portfolio empty" path. Instead it did what the ask actually asked for:
a status scan cross-referencing `knowledge/open-problems/*.md` (`status: open`)
against `ledger/goals/*.yaml` coverage, to find genuinely unclaimed direction —
then produced concrete new records rather than a bare list.

**Nothing here is a ledger record.** IDs verified free 2026-08-07. Promote via
Coordinator only. No ledger status was changed; no batch was dispatched.

## Finding: one open problem stands out

Cross-referencing all 25 `status: open` entries in `knowledge/open-problems/`
against every `GOAL-*` and `RQ-*` record turned up one with **zero referencing
records anywhere in the corpus**: **KN-OPEN-025**, whether Galois symmetry can
accelerate TNFS's linear-algebra step, and by how much end-to-end. It sits
adjacent to this program's stated core expertise (structure-exploiting
cryptanalysis) and nobody has scoped it. See `IDEA-20260807-13901e`.

**Higher-priority finding, not from the open-problems scan:** `KN-OPEN-8a5965`
(added 2026-08-06 by another session, one day before this scan) records a
claimed polynomial-time quantum DCP algorithm that, if correct, would change
the threat model for **seven** active lattice goals at once
(GOAL-MLKEM-001..005, GOAL-MLDSA-001..002). A same-day follow-up idea,
`IDEA-20260807-abacec` (already on `main`, `status: proposed`), correctly
identified that the *reach* question (does the chain even get to FIPS 203
parameters) is answerable independently of whether the underlying proof
survives scrutiny — but as of this scan it had **zero downstream references**:
no hypothesis, no experiment, nothing built on it. This scan's main
contribution is closing that gap.

## What's here

| file | what it is |
|---|---|
| `H-MLKEM-b477fd.draft.yaml` + `EXP-MLKEM-8cc1f2.draft.yaml` | Promotes `IDEA-20260807-abacec` into an executable hypothesis/experiment: a literature-arithmetic reach map for the Simon-DCP → LWE → Module-LWE chain at FIPS 203's actual `(k,n,q)`. Deliberately touches nothing about whether Simon's proof itself (Q1) is correct — that stays a community-verdict question, per the open-problem entry's own posture. **Cheap** (no computation, no toy-scale lattice work — literature arithmetic against a already-crypto-scale target) and **high-value** (the single most consequential open question currently sitting unclaimed in the active portfolio). |
| `proposals.draft.yaml` | Three new ideas, each anchored to zero-coverage found in the scan: `IDEA-20260807-ea0291` (rank-1 vs rank-2 PIP obstruction — reuses this program's own GOAL-HAWK-001 finding as a comparison point), `IDEA-20260807-ccfe0d` (a bounded, stratified-sample fix for the standing citation-integrity gap in `KN-OPEN-3f7a21`, rather than leaving 7457 unverified entries as an open-ended liability), `IDEA-20260807-13901e` (TNFS Galois-symmetry scoping — the zero-coverage open problem itself). |

## Why not a full batch run

Dispatching workers against any of the 21 already-active goals right now risks
colliding with concurrent sessions' in-flight `write_scope`s — several branches
fetched during this scan had commits from within the last hour. The
`/launch-research-harness` skill's own step 4 requires binding to committed
state and a current branch before dispatch; opening a new campaign here would
also require Coordinator authority this session doesn't hold outside the
Coordinator subagent. What's deliverable at this authority level, and what the
user's phrasing ("find new ideas... directions to pursue") actually asked for,
is exactly what's staged here: research-status-grade findings plus concrete,
promotable records.

## Recommended next step

`EXP-MLKEM-8cc1f2` first — it is pure literature arithmetic (no lattice
computation, no wall-clock budget beyond reading three papers), it resolves
the highest-value currently-unclaimed question in the portfolio, and unlike
everything else on the active board it does not compete for `write_scope`
with any in-flight batch.
