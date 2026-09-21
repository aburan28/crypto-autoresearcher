---
id: KN-OPEN-3f7a21
type: open_problem
title: Can this program's literature corpus support its own citation_verified markings, when 7457 of 7666 entries claim read against a downloads/ tree that has never existed in the repository?
tags: [corpus-integrity, provenance, citation-verified, seeding, novelty-screen, knowledge-base, meta, open, tooling, audit]
confidence: reported
status: open
source_refs: [EV-HQC-9906b9, DEC-20260802-344883, KN-LIT-2141, KN-LIT-7565, KN-LIT-7586]
added: 2026-08-02
superseded_by: null
---

## The observation

Discovered incidentally by `GOAL-HQC-001` BATCH-001, which was doing something
else entirely. Two producers with disjoint write scopes each hit a fragment of
it; the batch's validator measured its scope; the Coordinator re-measured every
headline number independently before filing this entry.

Measured on the repository tree at commit `8b20ddda` (2026-08-02):

| Quantity | Count |
|---|---:|
| `knowledge/literature/*.md` entries | 7666 |
| carrying `citation_verified: read` | 7457 |
| carrying `citation_verified: web` | 192 |
| citing a path under `downloads/` | 7421 |
| carrying an in-record bulk-seed note (first-two-pages / heuristic metadata) | 7477 |
| backing artifacts under `downloads/` actually present | **0** |

`downloads/` does not exist in the working tree, is **not** listed in
`.gitignore`, and `git log --all --diff-filter=A -- 'downloads/*'` returns
nothing — it has never been tracked in this repository's history.

## Why this is stated carefully rather than dramatically

The obvious reading — "7457 records lie about having been read" — **is not
supported**, and the batch's red team was right to push back on the
Coordinator's first framing of it.

1. **`read` is an act, not a retained artifact.** `knowledge/SEEDING.md` defines
   the upgrade as "only after fetching the actual source". Nothing in the
   contract requires the PDF be kept. The absence of `downloads/` is therefore
   *not* proof that any individual fetch never happened.
2. **Two producers converging on this is a controlled null, not evidence.** At
   7421/7666 ≈ 96.8% prevalence, *any* two agents touching the corpus would hit
   it. The Coordinator initially called that convergence "the most consequential
   thing in this batch"; that inference is withdrawn in `DEC-20260802-344883`
   D-7. The finding stands on the measurement, not on the coincidence.

What **is** supported is narrower and still serious:

- **≈99.5% of the corpus is un-re-verifiable in place.** A reviewer who wants to
  check what an entry claims must re-acquire from the network, and this batch
  demonstrated that re-acquisition can fail (paywalls) or be blocked
  (`eprint.iacr.org` PDF endpoint returns HTTP 403 while its HTML endpoint
  returns 200).
- **7477 entries carry a bulk-seed note that is in direct tension with their own
  `read` marking.** An entry whose body says it was generated from a PDF's first
  two pages with heuristically parsed metadata is not obviously an entry whose
  bibliographic reference was confirmed against a primary index in the sense
  `SEEDING.md` means.

## The concrete instance that made it visible

`KN-LIT-2141` (Guo–Johansson, *A New Decryption Failure Attack against HQC*) is
the single corpus record sitting directly on `GOAL-HQC-001`'s DFR-attack lane.
It carries `citation_verified: read`, its `year`, `venue`, `identifiers.*` and
`url` are all `null`, and its recorded key claim reads `264` where the
publisher abstract reads `2^64` — confirmed by the batch validator as a
flattened superscript, i.e. a lost exponent.

That is the failure mode in miniature: a record marked as fully read, backed by
nothing retained, carrying a silently corrupted number, on the exact lane a live
research goal depends on.

## Why it matters beyond bookkeeping

Every `novelty_screen` this program runs greps this corpus. A screen that
concludes "no existing work does X" is only as strong as the corpus's coverage
and the fidelity of its claims. If ~97% of entries are abstract-level seeds
marked as full reads, then:

- novelty claims are systematically weaker than their `read` markings imply;
- a lost exponent (the `2^64` → `264` shape) can silently invert a magnitude
  comparison in exactly the cost-model reasoning this program does constantly;
- `docs/inventor-protocol.md`'s closure standard — a negative result needs a
  named obstruction, not a fatigue report — is harder to meet honestly against a
  corpus whose negative space is unmeasured.

## Open questions

- **Q1.** How many of the 7457 `read`-tier entries were in fact fetched in full,
  and how many are abstract-level seeds mismarked? The bulk-seed note count
  (7477) is an upper bound on the mismarked set but not a measurement of it.
- **Q2.** What is the correct repair? Candidates, none costed yet: mass
  downgrade `read` → `web` for entries carrying the bulk-seed note; introduce a
  distinct level meaning "seeded from an abstract"; retain content hashes rather
  than PDFs so re-acquisition is checkable without redistributing copyrighted
  text; or re-fetch and re-verify on demand at first use.
- **Q3.** How many entries carry a corrupted numeric claim of the `2^64` → `264`
  shape? A regex census over claim lines for bare integers in the 100–999 range
  adjacent to complexity language would bound this cheaply.
- **Q4.** Does `tools/validate_ledger.py` have any check that could have caught
  a declared-but-absent backing artifact, and should it?

## Concrete successor action

**A dedicated audit task, outside any scheme goal.** The red team's objection O9
against `GOAL-HQC-001` BATCH-001 was that the finding, though real, had *no
successor task*; this entry exists to give it one. The cheapest first step is
Q3's regex census, because it is zero-network, bounded, and directly measures
whether the corpus has silently corrupted numbers rather than merely
un-re-verifiable ones.

**This entry performs no repair.** No corpus record is downgraded, edited, or
superseded by filing it. `DEC-20260802-344883` D-7 records why: downgrading 7457
records is a program-level act far outside `GOAL-HQC-001`'s mandate, and doing
it inside an HQC batch would be precisely the scope creep this harness exists to
prevent.

## Provenance of the numbers in this entry

Every count above was produced by the Coordinator directly against the working
tree, not taken from either producer's report. The validator's independent
measurement agreed; one correction was applied from it — `KN-LIT-7586` is at
`web`, not `read`, so the sibling task's 13-record list is 12 of 13. No number
here is relayed from a source this entry did not check.
