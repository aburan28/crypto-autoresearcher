# ECDLP known-results map

**What the literature has already established about elliptic-curve discrete
logarithms, one claim per file, written so an idea generator can see it
*before* it proposes the same thing.**

`knowledge/literature/` answers "what does this paper say". It could not stop
this program from re-deriving published results, because the failure was never
a missing paper:

- IDEA-20260915-8fe0ef re-derived Galbraith–Granger–Merz–Petit's
  Frobenius-invariant factor base for subfield curves (DEC-20260916-3c0cf5).
  The paper was in the corpus the whole time, as a bulk stub (KN-LIT-796).
- The isogeny-transfer lane spent eight evidence records before being closed by
  Tate's isogeny theorem (EV-IT-511f3d). JMV 2005 was in the corpus, uncited.
- The four strongest July "publication candidates" were all known
  (`docs/novelty-screen-20260729.md`). One decisive paper, HKY 2015, was
  present as KN-LIT-475, and it was useless: the title was garbled and the
  body read "No abstract was extractable".

So the unit here is the **claim**, not the paper. A row states what is known,
under which heuristic, and at what cost. It names the curated sources that
establish it. Its `forecloses` list holds the phrases an agent would use when
it is about to rediscover it. A plain `Grep` over this directory, or
`tools/build_frontier_map.py --match "<idea text>"`, then finds the collision
without the retrieval index, without ePrint access, and without trusting stub
tags.

## Layout

```text
knowledge/frontiers/ecdlp/
  README.md                         this file (schema and rules)
  MAP.md                            GENERATED, gitignored: python3 tools/build_frontier_map.py --out ...
  generic-rho/KR-RHO-<tok>.yaml     Pollard rho, kangaroo, BSGS, collision search, records, hardware
  index-calculus/KR-IC-<tok>.yaml   summation polynomials, Weil descent, Gröbner/SAT, covers, IC negatives
```

## Row schema

```yaml
id: KR-IC-3f9a21              # python3 tools/allocate_id.py --next known_result --area IC
area: index-calculus          # must equal the directory; the id's area code must match (RHO | IC)
kind: known_mechanism         # known_mechanism | known_bound | known_negative | record | dispute | textbook_fact
title: Frobenius-invariant factor bases on subfield curves
claim: >-
  Precise statement, scoped exactly as the sources scope it: curve family,
  field, heuristic, cost with units. No paraphrase that is stronger than the
  paper.
status: heuristic             # proven | heuristic | conjectured | disputed | refuted | measured | reported
setting: {field: binary, curve_family: koblitz, model: single_target}   # optional
cost: "time ~ ..., memory ~ ..."                                         # optional, with units
sources:                      # >= 1, and at least one not recalled_unverified
  - ref: KN-LIT-xxxxxx        # must resolve to knowledge/*/KN-*.md
    locator: "Thm 3; §4.1"    # where the claim is stated ('abstract' if that is all that was read)
    verification_state: full_text_read   # full_text_read | abstract_read | secondary_source | recalled_unverified
forecloses:                   # >= 1 phrase an idea would use when re-deriving this
  - Frobenius-stable factor base
  - tau-invariant decomposition
internal:                     # optional: where THIS program touched the result
  - ref: IDEA-20260915-8fe0ef
    relation: rederived       # rederived | measured | extends | contradicts | applies | cites
    note: one line
open: []                      # optional KN-OPEN ids this leaves open
dominated_by: null            # optional KR id of a row that strictly improves on this one
added: 2026-09-26
superseded_by: null           # set ONLY when a newer row replaces this one
```

`tools/build_frontier_map.py --check` enforces this in CI and in `make check-ledger`.

## Rules

1. **Rows are write-once.** A correction is a new row, and the old row's
   `superseded_by` points at it. Editing is allowed only for typos, and for
   setting `superseded_by`.
2. **Sources are curated entries.** A row may cite a bulk stub, but if so it
   also cites a curated entry or a frozen `inputs/` package. Its
   `verification_state` records what was actually read. A row resting only on
   `recalled_unverified` sources fails the check.
3. **Scope as the source scopes.** Heuristic results say which heuristic they
   rest on (first fall degree assumption, the Petit–Quisquater degree of
   regularity conjecture, Semaev's Assumption 1, ...). Records carry hardware,
   year and units.
4. **Disputes are rows too.** When the literature disagrees, as with the first
   fall degree assumption, the row is `kind: dispute` and cites both sides.
   Agents must not pick a side silently.
5. **`internal` records re-derivations honestly.** When the program
   rediscovers a row, the row gains nothing, but the next agent learns the
   lane was already walked.
6. **The map is curated, not exhaustive.** No matching row is *not* evidence
   of novelty. The literature search in `agents/idea-generator.md` still
   applies. The map removes the known collisions from the path.

## How ideation uses it

- `/propose-ideas` and `/deep-research` render the map for the area and paste
  it into the idea-generator handoff (the idea generator has no Bash).
- Each new idea records what it was positioned against in a `prior_art` block
  (`templates/research-records.md`). From IDEA-20261001-* onward,
  `tools/validate_ledger.py` requires the block and checks that every row id
  resolves.
- `python3 tools/build_frontier_map.py --match "<claim + mechanism>"` is the
  quick check for the top-level session and for reviewers.

## Adding rows

Add rows through `/curate-knowledge`:

1. Write or upgrade the KN-LIT entry first, from a source you actually opened.
2. Mint a row id with `python3 tools/allocate_id.py --next known_result --area IC`
   (or `RHO`), then `--check` it.
3. Write the row and run `python3 tools/build_frontier_map.py --check`.

A weekly literature gather (`knowledge/gathers/`) should propose rows, not just
KN-LIT entries.
