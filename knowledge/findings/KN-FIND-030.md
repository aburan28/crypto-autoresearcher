---
id: KN-FIND-030
type: internal_finding
title: Directory-scan ID allocation is not concurrency-safe across branches; two
  campaigns against one main allocate the same next-free id, and the correction
  record documenting the first collision collided the same way
tags:
- harness-integrity
- ledger
- id-allocation
- concurrency
- merge-conflict
- record-immutability
- process
- methodology
- infrastructure
- scoped-negative
- non-cryptographic
confidence: established
internal_refs:
- TASK-20260731-706
- DEC-20260731-030
- DEC-20260731-032
proof_status: derivation
proof_refs:
- ledger/corrections/CORR-20260731-007.yaml
- ledger/corrections/CORR-20260731-008.yaml
- tools/validate_ledger.py
added: 2026-08-02
superseded_by: null
---

## Why this entry exists

This program allocates record identifiers (`DEC-*`, `KN-FIND-*`, `CORR-*`,
`EV-*`, ...) by **scanning a directory of the local working tree and taking the
next free number**. The convention is written into `CLAUDE.md` ("Find the next
free number by grepping the relevant directory") and is followed carefully by
every role.

It is not concurrency-safe, and the failure is not hypothetical. It has now
occurred **twice in seven days** in this repository, the second time on **twelve
records at once**, and the second occurrence destroyed the identifier of the
very record that documented the first.

**This entry contains no cryptographic content of any kind.** It is not evidence
for or against any hypothesis about AES, ECDLP or anything else, and must never
be cited in support of one. It is a finding about the research harness.

### Where the two incident records are, and why they are not in `internal_refs`

The basis of this entry is two correction records:
**`ledger/corrections/CORR-20260731-008.yaml`** (the first collision, originally
`CORR-20260731-005`) and **`ledger/corrections/CORR-20260731-007.yaml`** (the
second, twelve-way collision, which renumbered the first). They are named here
in prose and carried in `proof_refs` as paths, and they are **deliberately absent
from `internal_refs`**.

The reason is a schema fact, not a judgement about relevance: `internal_refs`
entries must resolve against `ctx.ids` in `tools/validate_ledger.py`, and
`LEDGER_DIRS` registers only `questions`, `proposals`, `hypotheses`, `evidence`,
`decisions` and `handoffs`. **`ledger/corrections/` is not registered** — exactly
as `ledger/goals/` is not, which is why `KN-FIND-028` names `GOAL-AES-001` in
prose rather than in its refs. A `CORR-*` id in `internal_refs` can therefore
never resolve, however correct the reference is, and putting one there produces a
`references unknown record` error rather than a link.

This is written down **at the point of temptation**, because in a record about a
collision between correction records, citing those corrections in `internal_refs`
is the obvious and natural thing to write, and the next author of a
corrections-related finding will reach for it. The linkage is not weaker for
living in prose; it is only differently located.

The irony compounds one turn further, and is recorded rather than smoothed over:
**a finding about an unsafe identifier allocator was itself blocked from the
corpus by an identifier-reference schema rule.** Both are the same shape of
defect — a name-resolution mechanism whose universe is narrower than the set of
things people legitimately name. Neither is anyone's mistake at the point of
writing.

## The mechanism, stated exactly

An allocator that returns `max(ids found in the local tree) + 1` is correct only
under an assumption that is never stated: **that the local tree contains every
allocation that will ever exist at that number**. Under a branch-per-campaign
workflow against a shared `main`, that assumption is false in the ordinary case,
not the exotic one:

1. Branch A and branch B both branch from `main` at a state where the highest
   `DEC-20260731-NNN` is `012`.
2. Both allocate `013`. Both are *correct* with respect to the tree they can
   see. Neither can see the other.
3. Both commit. Both are internally consistent, validate cleanly, and pass every
   post-commit check, because each tree is individually coherent.
4. The collision materialises **only at merge**, as an `add/add` conflict on
   `ledger/decisions/DEC-20260731-013.yaml` — a path that exists on both sides
   with unrelated content.

Two properties of this shape make it worse than an ordinary merge conflict:

- **It is invisible until merge.** There is no local check that can detect it,
  because the information needed is not in the local tree. Every gate the
  program runs before the merge passes.
- **It is a conflict between two records, not two versions of one record.** Git
  presents it as a content conflict, which invites the wrong repair. There is no
  "correct version" to choose: choosing either side **deletes a record**, and
  deleting a committed research record is an evidence-integrity failure under
  AGENTS.md core rule 4. The correct resolution is that both records survive and
  one is renumbered.
- **The dangerous ending is not the conflict.** A conflict is loud. The quiet
  ending is a task card that *reserved* an id, then executed after a merge and
  **wrote over another campaign's record** at that id, with no conflict at all
  because the reservation was prose. This nearly happened: the first occurrence
  was caught one step before `TASK-20260731-706` would have written over
  `GOAL-MLKEM-003`'s decision and the Carrier/Pwrong knowledge entry.

## The two instances

| | first | second |
|---|---|---|
| record | `CORR-20260731-008` (originally `CORR-20260731-005`) | `CORR-20260731-007` |
| date | 2026-08-01 | 2026-08-02 |
| colliding records | 4 remapped by the merge + 2 reserved ids caught before use | **12**, all `add/add` |
| campaigns | AES/FAEST branch vs MLKEM/CRYPTO on main | AES branch vs (in part) `GOAL-ECDLP-001` on main |
| worst near-miss | a task about to overwrite another campaign's `DEC-*` and `KN-FIND-*` | none; caught at merge |

The second instance collided on `DEC-20260731-013..020`, `KN-FIND-017`,
`KN-FIND-018`, `knowledge/INDEX.md`, and `CORR-20260731-005`.

**The recurrence is the finding.** Between the two instances, the program did
everything a careful operator can do: it recorded the first collision, wrote the
precedent, and two later decisions (`DEC-20260731-030` and `-032`, then numbered
`-018` and `-020`) explicitly *predicted* a future collision and pre-committed to
resolving it by a `CORR` record rather than an edit. `CORR-20260731-005` itself
verified its id free by directory listing before using it. All of that care was
correct and none of it helped, because the directory listed was of the wrong
universe. **A procedure cannot fix an allocator.** Two of those pre-commitments
even named `CORR-20260731-006` as the next free correction id — and `006` had
been taken on main by then, so the prediction of the collision was itself a
victim of it.

## Why the obvious mitigations do not work

- **"Scan more carefully."** Refuted by instance 2: the scan was careful and the
  record that recommended care collided.
- **"Merge more often."** Shrinks the window; does not close it. Two branches
  generating in the same interval still collide, and the interval cannot be
  zero.
- **"Leave gaps / start high."** Trades a certain collision for a probabilistic
  one and destroys the density that makes `max + 1` legible in the first place.
- **"Resolve conflicts as they come."** This is the current state, and it costs
  a twelve-record remap with a ~50-file reference-rewrite footprint, of which
  the archived-artifact portion cannot be rewritten at all (immutability) and
  must instead be covered by a reader rule in a correction record. The cost is
  superlinear in the number of records, and it is paid in exactly the artifacts
  the program most wants to keep stable.

## The three designs that would work, with their costs

Recorded so the analysis is not relitigated at the third collision. **None is
adopted here** — adoption is a program change requiring its own coordinator
decision.

1. **Branch-scoped id prefixes** (`DEC-20260731-A013` / a per-campaign or
   per-goal segment). *Pro:* collision becomes structurally impossible, needs no
   network access, no coordination, and no change to the local-scan habit.
   *Con:* ids stop being globally ordered and dense; every regex, validator index
   and template that assumes `NNN` must change; historical ids stay in the old
   shape forever, so the corpus carries two id grammars.
2. **Allocate against `origin/main`, not the local tree** (`max(local ∪
   origin/main) + 1`, after a fetch). *Pro:* smallest change to the existing
   convention; ids stay dense and ordered. *Con:* requires network at allocation
   time; **does not eliminate the race**, only narrows it to the window between
   two branches' fetches — two campaigns generating within the same window still
   collide. It is a mitigation, not a fix, and must be labelled as one.
3. **Reservation before use**: a single append-only registry on `main` that
   records claimed ids, updated by a push that fails on conflict, before the
   record is written. *Pro:* the only one of the three that is actually a fix —
   `main` is the serialization point, and a failed push is an unambiguous "someone
   took it, choose again". *Con:* every generation step needs a round trip to
   `main` and a retry loop; a crashed session leaks a reserved id (harmless but
   permanent); it introduces a shared mutable file, which the program otherwise
   avoids.

A defensible combination is **(1) for new id series** — structural, cheap,
offline — with **(3) reserved for the series where density and global ordering
genuinely matter**. Design (2) alone should not be recorded as a fix.

Whatever is adopted, one property should be stated in the record that adopts it:
**an allocator whose correctness depends on the allocating agent having seen all
concurrent work is not an allocator, it is a convention.**

## Practice rules that hold regardless of which design is adopted

1. **Never resolve an `add/add` conflict on a record path by choosing a side.**
   Both records survive; one is renumbered under a new id; the renumbering is
   itself a `CORR` record. (AGENTS.md, "Durable research commits".)
2. **First author owns the id.** Records already on `main` keep their
   identifiers; the merging branch's records move. Mechanical, decidable without
   judging content, and identical for both branches — unlike "authored first by
   wall clock", which is not.
3. **Renumbering a record means renumbering its citations of other moved
   records, and nothing else.** The test: does the edit *preserve* the referent or
   *change* it? Inside a record being reissued under a new id, leaving a citation
   at an old number silently repoints it at another campaign's record — so
   updating it preserves meaning. In an untouched archived artifact, editing
   would be the change, so the correction's reader rule carries the mapping
   instead.
4. **A prose "reserved id" in a task card is not a reservation.** It is a
   prediction about a future directory scan, and it is the channel through which
   this defect silently overwrites records. Verify at write time, in the record
   that uses the id, and say in that record that you did.
5. **Derived artifacts are regenerated, never hand-merged.** `knowledge/INDEX.md`
   and the dispatch plans are functions of the corpus; hand-resolving them is
   picking a side on a file that has no sides.

## Non-claims — read before citing

- **No cryptographic content.** Nothing here is evidence about AES, ECDLP, or
  any cryptosystem, at any parameter or round count. It is a fact about this
  repository's tooling.
- **n = 2, in one repository, under one workflow.** The mechanism is
  `confidence: established` because it is a deterministic property of
  `max(local) + 1` under concurrent branches, demonstrable from the two recorded
  incidents and from the definition itself. The *frequency*, and any claim about
  how other multi-agent research systems behave, is **not** established and is
  not asserted.
- **No design is adopted and no tooling is changed by this entry.** The three
  options and their costs are recorded; choosing among them requires a
  coordinator decision under its own `DEC-*` id, which does not exist yet.
- **Not a criticism of any agent or session.** Every allocation involved was
  correct with respect to the information available to it. That is precisely the
  point: the defect is in the allocator, and every careful actor reproduces it.
- **This entry does not arise from an evidence review.** Its basis is two
  recorded operational incidents (`CORR-20260731-008`, `CORR-20260731-007`), not
  a `support` or `reject_scoped` decision on `replicated`/`strong` evidence. The
  basis is declared here so no reader mistakes it for evidence-backed research
  content. `internal_refs` therefore carries only the three resolvable records
  the body actually cites — `TASK-20260731-706` (the near-miss overwrite of
  instance 1) and `DEC-20260731-030` / `-032` (the two decisions that predicted
  the second collision, named a next-free correction id that was already taken,
  and were themselves renumbered by it) — and **not** the two correction records
  that are the basis, for the schema reason given above.
- **`proof_status: derivation`, and it does not exceed that.** What is derived is
  the mechanism: `max(local ids) + 1` is correct only if the local tree contains
  every allocation at that number, which is false by construction under
  concurrent branches. That argument is checkable by reading it and does not
  depend on the incidents. The two incidents are reproducible observations that
  the derived failure occurs in practice. **Not machine-checked proof**, and no
  impossibility claim: it is not proved that no scan-based scheme could be made
  safe by other means, only that this one is not.
- **This entry's own id was allocated by the mechanism it describes** — the
  first free `KN-FIND` over the union of both sides, `028` and `029` being
  consumed by the two entries this merge renumbers. It is as vulnerable to a
  third concurrent campaign as everything else, and will stay so until a design
  above is adopted.
