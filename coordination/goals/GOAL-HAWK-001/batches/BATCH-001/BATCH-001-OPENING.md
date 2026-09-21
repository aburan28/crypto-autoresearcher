# GOAL-HAWK-001 / BATCH-001 — opening

Opened **2026-08-02** by TASK-20260802-003 on explicit user authorization to launch
this goal. GOAL-HAWK-001 moves `draft → active`. Bound to `RQ-HAWK-001`.

## Why this batch and not ideation

`GOAL-HAWK-001.next_action` as recorded on 2026-07-29 forbids ideation until the
primary sources are obtained and filed, and warns: *"this goal must not inherit a
break claim it has not checked."* BATCH-001 does exactly and only that.

It is deliberately a **reading** batch. It runs no experiment, creates no
hypothesis, and asserts nothing about HAWK's security in either direction.
`active_hypothesis_ids` stays empty.

## Scope

| | |
|---|---|
| Tasks | TASK-20260802-003 … -008 (6) |
| Concurrency | 3 |
| Runs authorized | **0** |
| Hypotheses created | **0** |
| Promotion gates addressed | **none** — no asymptotic claim of this program's own is advanced |
| Claim-tier ceiling | unchanged from `RQ-HAWK-001`: toy-tier until a certified instance at scheme scale exists |

## What BATCH-001 found

Three findings, all established against obtained full texts.

**1. The goal's next_action rests on a false premise.** It asks for "the four
heuristics" of the disclosed attack, transcribed verbatim and numbered. The
disclosed attack — Straznickas–Weis, *HAWK-n Key Recovery Reduces to SVP in
Dimension n/2 + 1* — is **unconditional**. A regex census over its full
78,015-character text returns `Heuristic` ×0 and `Conjecture` ×0. Its single
`Assumption` conditions the *cost-comparison table* on HAWK's own `[HAWK25, Table 8]`
model, not the reduction. **The four heuristics belong to eprint 2026/1318**, a
separate attack, whose full text could not be obtained.

**2. The disclosed attack was already in the corpus.** It is `KN-LIT-7592`, filed
2026-07-28 — four days *before* this goal asked for it. The goal named the referent
only as "the disclosed attack" and cited no ID, so the acquisition task found it by
grepping the corpus, not by following the record. Its `citation_verified` is
upgraded `web → read`; no claim in it was edited.

**3. The two obtained papers stand in a relationship no record captured.**
Straznickas–Weis does not merely reuse van Gent–Pulles's descent — it **discharges
that paper's Heuristic 1**, by proving the relevant lattice exactly near-hypercubic
so that Ducas's *provable* block reduction applies. In the authors' words, this
"upgrades the endgame from the heuristic pricing of [GP25, Thm. 1] to the
unconditional accounting of Theorem 6.1." `KN-LIT-7592` already recorded that the
reduction is unconditional; it did **not** record this relationship.

## Source status

| Source | Status |
|---|---|
| SRC-1 van Gent–Pulles 2025 (`iacr:2025/928`, CiC 2(2), DOI 10.62056/a3qjp2w9p) | **Full text** → `KN-LIT-7673` |
| SRC-4 the disclosed attack (Straznickas–Weis, Anthropic) | **Full text** → `KN-LIT-7592` upgraded to `read` |
| SRC-2 `iacr:2026/1318` (four heuristics) | **Abstract only** — PDF Cloudflare-gated |
| SRC-3 `iacr:2026/890` | **Abstract only** — held as `KN-LIT-7648` |

**Pause condition 2 has NOT fired, and the batch does not claim it has.** The
blocker is origin-side bot protection, not the harness network policy — the agent
proxy reported `recentRelayFailures: []` while `eprint.iacr.org` served HTML fine
and refused every PDF across five report numbers. Routes A4 (arXiv) and A5
(Semantic Scholar) returned **temporary 429s caused by this session's own earlier
gathers**, so the declared access order is **not exhausted**. Honest status:
*partially blocked, retry available*.

## Open obligation carried forward

**The four heuristics of `iacr:2026/1318` remain unread.** That is the object the
goal's next_action actually needs, and BATCH-001 does not discharge it. Its
30/06 update — conceding Heuristic 4 insufficient — is truncated mid-sentence in
the only copy obtainable, as `KN-LIT-7670` already records.

## Standing caveats

- **Formula-level transcription is unreliable.** Both transcription files are
  pdfminer.six extractions of two-column LaTeX; damaged renderings are marked
  `[EXTRACTION-DAMAGED]` and none is load-bearing. Verifying that is the
  Validator's named priority duty.
- **Model independence is procedural, not model-level.** Author, validator and red
  team all resolve to `claude-opus-5`. **Nothing in BATCH-001 is admissible toward
  the AGENTS.md rule 13 three-model closure quorum.**
- **Third-party PDFs are not committed** — only hashes, so a reviewer can
  re-acquire and verify byte-identity.
