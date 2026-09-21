# GOAL-MCE-001 BATCH-001 — opening

**Goal:** GOAL-MCE-001 · **Question:** RQ-MCE-e65b3c · **Opened:** 2026-08-03
**Coordinator authority:** user direction this session,
`/coordinate-research-goal attack mceliece`.

BATCH-001 acquires and transcribes primary text. **It designs no experiment,
forms no hypothesis, runs no solver, and asserts nothing about Classic
McEliece's security in either direction.** Nothing in it is admissible toward
an AGENTS.md rule 13 closure quorum.

---

## 1. Why this batch is not an attack

The user asked to attack McEliece. This batch does not attack it, and the
reason is a rule this program already wrote down.

Section 8 of `docs/inventor-protocol.md` (`KN-TECH-080`) requires a
proof-oriented proposal to establish **the exact bottleneck and reproduce the
baseline** before the Coordinator approves implementation or expensive
experiments. For this target that ordering is not bureaucratic. The single
highest-value fact available — whether the 2026 heuristic subexponential
attack reaches Classic McEliece's parameters — is currently **unknown to this
program**, and it is knowable by reading one paper. Dispatching a solver before
reading it would be spending the campaign budget to rediscover, badly, what
four authors published in April.

`KN-LIT-f1073f` (Panny, *On breaking McEliece keys using brute force*, 2025) is
the standing embarrassment this ordering avoids: a 2025 paper still had to
establish the honest brute-force baseline for a 1978 system. The
sophisticated-attack-that-loses-to-brute-force failure mode is real in this
exact literature.

## 2. Corpus census — broad, and unread

| | |
|---|---|
| KN-LIT entries mentioning McEliece | **169** |
| …filed 2026-08-03 by GATHER-20260803 | 137 |
| …pre-existing | 32 |
| Of the 137, papers actually read | **0** |
| KN-TECH entries on ISD or code-based cryptanalysis | **0** |

The corpus gained a complete map of the Classic McEliece bibliography this
session and **not one of those papers was read**. Every one of the 137 entries
carries an explicit statement to that effect, and where the entry's description
of an algorithm comes from general knowledge rather than the cited source it
says *"recalled, not read from this source"*.

**A broad unread corpus is more dangerous than a narrow one**, because it
returns confident answers to novelty and dedup queries that it has no basis to
answer. RQ-MCE-e65b3c therefore forbids designing any experiment until primary
text is in hand, and this batch exists to convert a small decisive slice of
that breadth into read text.

Zero `KN-TECH` entries on ISD is a separate, real gap: this program has no
committed technique record for the algorithm family it is about to cost.
It is **not** patched in this batch — a technique entry states applicability
conditions and known limits, and nothing has been read yet.

## 3. Provenance hazards carried into this batch

Three, all inherited, all recorded so the red team can check them rather than
rediscover them.

**KN-OPEN-3f7a21.** GOAL-HQC-001 BATCH-001 found that 7457 of 7666 literature
entries carried `citation_verified: read` against a `downloads/` tree that is
absent, never git-tracked and not gitignored. Any pre-2026-08-03 McEliece
entry's `read` provenance is therefore **unconfirmed**. The 137 new entries
deliberately use `web` (118) or `false` (19) and never `read` — that choice was
made independently of KN-OPEN-3f7a21 and happens to be the behaviour it argues
for.

**The eprint PDF endpoint.** On 2026-08-03 this harness got HTTP 200 from
`eprint.iacr.org` **abstract** pages on 75 of 75 requests. That is a measured
precondition and it is why this goal's first task is expected to succeed where
GOAL-HQC-001's had to fight. It is **not** a claim that PDF retrieval works.
GOAL-HQC-001 BATCH-001's red team established that the PDF endpoint still
returns 403 and that a contrary Coordinator claim was **false** because only
HTML endpoints had been tested. This batch does not re-make that error and the
producer is directed to test the PDF endpoint separately and report it
separately.

**The two-campaign overread pattern.** In GOAL-HAWK-001 BATCH-001 and again in
GOAL-HQC-001 BATCH-001, a Coordinator claim that a prior record was defective
was found by that batch's own red team to be an overread. This opening makes
several framing claims — section 2's "0 read", section 4's characterisation of
KN-LIT-7c4620, section 5's ISD-convention deferral — and
`TASK-20260803-08e883` is directed to attack all of them.

## 4. The primary target, stated at the level the evidence supports

`KN-LIT-7c4620` — Briaud, Lemoine, Randriambololona, Tillich, *A heuristic
subexponential attack on the McEliece cryptosystem*, `iacr:2026/1232`.

What is **established**: the paper exists, the citation is verified against the
IACR ePrint record (title and four authors checked, 2026-08-03), and its title
claims a heuristic subexponential attack on McEliece.

What is **not established, by anything this program holds**: whether the attack
is correct; its complexity exponent; what its heuristics assume; which code
families and rates it reaches; whether it touches binary Goppa codes at all;
and whether it has any bearing on Classic McEliece's parameter sets. The
KN-LIT entry states this refusal explicitly and this opening repeats it.

The surrounding line is held at the same level and no better:
`KN-LIT-71d1a0` (syzygy distinguisher, Eurocrypt 2025), `KN-LIT-4c8135`
(polynomial-time key recovery, **high-rate** random alternant codes, IEEE-IT
2024), `KN-LIT-7ee1a9` (degree-2 alternant distinguisher),
`KN-LIT-d6d510` (attack on CFS and TII McEliece challenges, 2026),
`KN-LIT-e4a472` (tangent space attack, 2025), `KN-LIT-e37d4c` (Goppa
distinguishing, 2025).

**The rate threshold is the whole question.** `KN-LIT-4c8135` is genuinely
polynomial-time and genuinely confined to high rate. Classic McEliece's rate is
a number this program has not transcribed. The distance between those two is
what BATCH-001 exists to measure, and until it is measured neither "the
structural line threatens Classic McEliece" nor "it does not" is a statement
this program is entitled to make.

## 5. Coordination with the two live code-based goals

`GOAL-HQC-001` and `GOAL-SDITH-001` are both code-based and both need a
memory-charged ISD cost. GOAL-HQC-001 dispatched `TASK-20260802-0100a5` to
derive that costing convention **scheme-independently, with no parameter
numbers**, precisely so the code-based goals would not each invent their own.

This goal **binds to that convention and does not derive a competing one.**
RQ-MCE-e65b3c states it as a constraint. That is why BATCH-001's second
producer transcribes Classic McEliece's *parameters* and stops there: applying
a convention that another goal is still finalising would either duplicate it or
fork it, and both are worse than waiting one batch.

Whether `TASK-20260802-0100a5`'s output is final is **not asserted here** —
GOAL-HQC-001's record shows BATCH-001 closed and the campaign now at BATCH-003,
but this Coordinator has not read that convention artifact. `TASK-20260803-409c5e`
is directed to establish its status as a fact rather than accept this
paragraph's guess.

## 6. Batch shape

Two producers, disjoint write scopes, neither depending on the other.

| Task | Role | Duty |
|---|---|---|
| `TASK-20260803-292b99` | executor | Obtain and transcribe `iacr:2026/1232` and the nearest primary statements of the 2026 line; enumerate heuristics; state the rate regime |
| `TASK-20260803-f3aece` | executor | Transcribe Classic McEliece's parameter sets, rates, and claimed categories from primary specification; settle standardization status |
| `TASK-20260803-f3beb0` | coordinator | Snapshot archive — freeze both producers before review |
| `TASK-20260803-409c5e` | validator | Transcription fidelity, source re-acquisition, ISD-convention status |
| `TASK-20260803-08e883` | red-team | Attack this opening's framing claims and the scoping of both transcriptions |
| `TASK-20260803-a561d8` | coordinator | Ledger archive — `EV-MCE-332f99`, `DEC-20260803-a5b9b1` |

## 7. What would make this batch a failure

Not "no attack was found" — no attack is sought. This batch fails if it
produces a **confident characterisation of KN-LIT-7c4620 that the primary text
does not support**, in either direction. Reporting the paper as a threat it may
not be, and dismissing it as irrelevant on a rate argument nobody transcribed,
are the same error with opposite signs, and `docs/inventor-protocol.md` treats
premature closure as symmetric with overclaiming.

## 8. Unexpected observation, recorded under AGENTS.md rule 8

Merging `origin/main` into this branch on 2026-08-03 changed
`inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json` from a URL-retrieval log
carrying **25 `attempts` plus 3 `addendum_attempts`** to a different document
at the same path (run provenance: `command`, `cwd`, `baseline_hashes`), with no
`attempts` key.

`tools/build_source_index.py` reads retrieval attempts only from
`provenance.json:attempts` / `addendum_attempts`. Consequently
`knowledge/SOURCES.md` regenerated on the merged tree reports **0 per-URL
retrieval attempts**, where the pre-merge tree reported 29 — including recorded
**failures**, which `knowledge/README.md` says the source index exists to carry
honestly.

The underlying evidence is **not lost from the tree**: `main` holds
`source_reads.json` and numerous `*_attempt.body` files in the same package.
What is lost is their representation in the generated index.

This is `origin/main`'s condition, not a regression introduced here: the
conflict was in two generated files (`SOURCES.md`, `sources.json`) and was
resolved by **regenerating** them from the merged corpus, which is the
prescribed handling for derived artifacts and not a choice between sides.
It is recorded rather than fixed because it belongs to the ML-KEM campaign's
artifacts and is outside this goal's mandate.

## 9. Validation state at open

`tools/validate_ledger.py` reports **110 errors** on this branch. `origin/main`
reports **the same 110** — checked in a scratch worktree at the same commit.
This branch adds none. The errors sit in `ledger/evidence/` and
`ledger/decisions/` records this goal does not touch.
