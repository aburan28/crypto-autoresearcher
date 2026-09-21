# Knowledge Corpus

Long-lived, curated knowledge for the research program. Git is the storage
and retrieval layer: entries are markdown files with YAML frontmatter,
stable immutable IDs, and greppable tags. Agents retrieve by `grep`/`glob`;
any future search index (SQLite, embeddings) must be generated from these
files, never replace them as the source of truth.

## Layout

```text
knowledge/
  INDEX.md            Generated index — one line per entry (derived, rebuildable)
  SOURCES.md          Generated source index — provenance of external material
  sources.json        Machine-readable twin of SOURCES.md (derived)
  literature/         KN-LIT-NNN.md   External papers, books, preprints
  techniques/         KN-TECH-NNN.md  Established algorithms and methods
  findings/           KN-FIND-NNN.md  Internal results promoted from evidence
  open-problems/      KN-OPEN-NNN.md  Precisely stated unknowns
```

The two generated indexes answer different questions and neither substitutes
for the other. `INDEX.md` lists what the corpus *believes* — one row per entry,
with confidence and tags. `SOURCES.md` lists what it *read*: every `SRC-*`
package, every recorded URL retrieval including the failed ones, every source
artifact under `inputs/`, and every `KN-LIT-*` citation keyed by its external
identifier. Rebuild it with `make sources`
(`tools/build_source_index.py`).

Its central column is whether the bytes are in the repository. A hash the tool
recomputes is a receipt; a hash it merely relays is an assertion by whoever
recorded it. `SOURCES.md` also carries the gap honestly — entries with no
recorded identifier are listed as having none, never backfilled by title
search — so the count of unreachable citations is visible rather than implied.

## Provenance classes

The directory an entry lives in is a provenance claim:

- **literature** — someone else's published claim. Requires a precise
  citation. Claims you have not personally verified are marked as such.
- **techniques** — established, textbook-level methods with complexity,
  applicability conditions, and known limits.
- **findings** — produced by THIS program. Only the Coordinator promotes a
  finding, only from an evidence record with strength `replicated` or
  `strong`, and the entry must cite its EV-/DEC-/EXP- IDs. A finding never
  claims more than its evidence record's scoped claim.
- **open-problems** — questions, not claims.

This separation exists so speculation can never be laundered into fact:
the Idea Generator's novelty checks and the Coordinator's syntheses may
cite `findings/` as internal ground truth, `literature/` only as reported.

## Entry format

```markdown
---
id: KN-LIT-001
type: literature | technique | internal_finding | open_problem
title: concise name
tags: [semaev, groebner, isogeny, ...]
confidence: established | reported | unverified
source:            # literature/techniques
  citation: full citation
  url: null
internal_refs: []  # findings: EV-/DEC-/EXP- IDs
proof_status: certificate | derivation | empirical_only | not_applicable
                   # findings: strongest checkable basis, copied from the
                   # evidence record (docs/claims-and-verification.md)
proof_refs: []     # findings: certificate / derivation-note paths
added: YYYY-MM-DD
superseded_by: null
---

Body: summary, key claims (verified vs. reported), relevance to the
program, and limits of applicability.
```

## When entries get created

Curation is a lifecycle obligation, not an ad-hoc activity. The binding
trigger points (details in `/curate-knowledge` and
`docs/task-lifecycle.md` step 9):

- Every evidence-review decision fills a `knowledge_promotion` field
  (`templates/research-records.md`). `support`/`reject_scoped` on
  `replicated`/`strong` evidence ⇒ a `KN-FIND` entry is required; anything
  else records why not. Proven scoped negatives are promoted like
  positives.
- Inconclusive outcomes that leave a precisely statable question become
  `KN-OPEN` entries; methods validated across experiments become
  `KN-TECH`; papers read during ideation/review become `KN-LIT`.

The standing test: a fresh agent reading only `knowledge/` and the ledger
should be able to rediscover everything this program has proven. A claim
that lives only in an experiment directory is not yet knowledge.

## Rules

- IDs are immutable and never reused.
- Corrections supersede: write a new entry, set `superseded_by` on the old
  one. Never silently rewrite substance (typo fixes excepted).
- `INDEX.md`, `SOURCES.md` and `sources.json` are derived — regenerate them
  after adding entries or vendoring a source (see the `/curate-knowledge`
  skill); never hand-maintain facts there. `make check-ledger` fails while
  the source index is stale.
- A literature entry names a retrievable source: fill `identifiers` with an
  eprint, arXiv, DOI, ISBN or URL. An entry with none is not rejected, but it
  lands in the gap table of `SOURCES.md` and stays there until someone finds
  the identifier. Do not invent one to clear the row.
- Confidence honesty: an abstract you skimmed is `reported`, not
  `established`.
- Proof honesty: a finding's `proof_status` never exceeds its evidence
  record's. `derivation` means a checkable written argument, not a
  machine-verified proof; `empirical_only` findings say so in the body and
  stay scoped to their tested instances.
