---
name: curate-knowledge
description: >-
  Add or update entries in the knowledge corpus (knowledge/): literature
  notes, technique references, established results, internal findings
  promoted from evidence, and open problems. Use when ingesting a paper,
  recording a known technique, or promoting a validated internal result.
---

# Curate knowledge

Maintain the corpus under `knowledge/`. Read `knowledge/README.md` first —
it defines the record format, ID scheme, and provenance classes.

## Steps

1. Classify the entry:
   - `literature` → `knowledge/literature/KN-LIT-NNN.md` — external paper,
     book, or preprint note. Requires a precise citation; mark every claim
     you did not verify.
   - `technique` → `knowledge/techniques/KN-TECH-NNN.md` — established
     algorithm or method: complexity, applicability, known limits, key
     references.
   - `internal_finding` → `knowledge/findings/KN-FIND-NNN.md` — distilled
     from this program's own evidence. ONLY promoted from an existing
     evidence record with strength `replicated` or `strong`, and only with
     a Coordinator decision; must cite the EV-/DEC-/EXP- IDs.
   - `open_problem` → `knowledge/open-problems/KN-OPEN-NNN.md` — precisely
     stated unknown worth future work.
2. Pick the next free ID in that class (grep existing files).
3. Write the entry using the frontmatter schema from `knowledge/README.md`
   (id, type, title, tags, confidence, source/citation or internal refs,
   added date, superseded_by).
4. Regenerate `knowledge/INDEX.md`: one line per entry — ID, title, type,
   confidence, tags — sorted by ID. The index is derived; entries are the
   source of truth.
5. The Coordinator creates an isolated snapshot or ledger archive commit for
   the exact entry, index, and any cited internal evidence/decision records.
   Report the item only after the post-commit verifier accepts its declared
   paths and hashes.
6. Report what was added and any related entries found while grepping.

## Rules

- Entries are corrected by superseding: new entry, old one gets
  `superseded_by`, never silently rewritten (typo fixes excepted).
- Confidence is `established | reported | unverified` — an unread paper's
  abstract is `reported` at best.
- Internal findings never state more than their evidence record's scoped
  claim.
