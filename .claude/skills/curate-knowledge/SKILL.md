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

## Promotion triggers

This skill is not only for ad-hoc ingestion — it is the required back half
of the review lifecycle. Invoke it whenever:

- **A result is proven.** Every `/review-evidence` decision of `support` or
  `reject_scoped` backed by `replicated`/`strong` evidence must promote a
  `KN-FIND` entry (or record `not_warranted` in the decision's
  `knowledge_promotion` field — see `templates/research-records.md`).
  Proven negatives are findings too: a replicated scoped rejection is a
  boundary future ideation must not re-cross. The entry copies the
  evidence record's `proof_status` and `proof_refs` (counterexample
  certificate, derivation note, or a declared `empirical_only`) so the
  finding's basis travels with it.
- **An unknown crystallizes.** An `inconclusive`/`pause` decision, a
  red-team report, or a failed approach that leaves a precisely statable
  question → `KN-OPEN`, citing the records that raised it.
- **A method matures.** An instrument, solver configuration, or analysis
  technique validated across two or more experiments → `KN-TECH`, with its
  applicability conditions and known limits.
- **A source is read.** A paper/preprint consulted during ideation or
  review that is not yet in `knowledge/literature/` → `KN-LIT`.

The test at the end of any review or goal batch: could a fresh agent,
reading only `knowledge/` and the ledger, rediscover what this program has
proven so far? If a proven claim lives only in an experiment directory,
promote it.

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
   Before curating, merge `origin/main` into the working branch (merge,
   never rebase) so the entry and index are built against current knowledge —
   see "Branch and PR hygiene" below.
2. Pick the next free ID in that class (grep existing files).
3. Write the entry using the frontmatter schema from `knowledge/README.md`
   (id, type, title, tags, confidence, source/citation or internal refs,
   added date, superseded_by).
4. Regenerate both derived indexes — entries and `inputs/` are the source of
   truth, the indexes are rebuilt from them:
   - `knowledge/INDEX.md` (`tools/build_knowledge_index.py`): one line per
     entry — ID, title, type, confidence, tags — sorted by ID.
   - `knowledge/SOURCES.md` + `knowledge/sources.json` (`make sources`):
     source provenance. Required whenever a `KN-LIT` entry is added or a
     source is vendored under `inputs/`. It also re-hashes every vendored
     source artifact, so a red run here is either a stale index or a
     corrupted source — check which before regenerating.
   A `KN-LIT` entry whose `identifiers` are all empty lands in the
   `SOURCES.md` gap table. That is the correct outcome when the identifier is
   genuinely unknown; never populate the field with a guess to clear the row
   (AGENTS.md rule 5).
5. The Coordinator creates an isolated snapshot or ledger archive commit for
   the exact entry, index, and any cited internal evidence/decision records.
   Report the item only after the post-commit verifier accepts its declared
   paths and hashes.
6. Push the branch and open or refresh a PR against `main` naming the new
   `KN-*` records (see "Branch and PR hygiene"). A knowledge entry that exists
   only in a local commit is not part of the corpus — it is unpublished.
7. Report what was added and any related entries found while grepping.

## Branch and PR hygiene

Curating knowledge changes the shared corpus, so every run of this skill also
pulls in `main` and surfaces the entry as a PR:

- **Before curating:** `git fetch origin && git merge origin/main` — merge,
  never rebase. If the merge conflicts, stop and report; never resolve a
  conflict by editing a record. Re-run `tools/validate_ledger.py`,
  `tools/build_knowledge_index.py --check` and
  `tools/build_source_index.py --check` after the merge.
- **After the archive commit:** `git push -u origin <branch>` then
  `gh pr create --base main --head <branch> --title "knowledge: <KN-ID>" --body "<KN-* IDs>"`
  (or `gh pr edit <number>` when a PR for the branch already exists).

## Rules

- Entries are corrected by superseding: new entry, old one gets
  `superseded_by`, never silently rewritten (typo fixes excepted).
- Confidence is `established | reported | unverified` — an unread paper's
  abstract is `reported` at best.
- Internal findings never state more than their evidence record's scoped
  claim.
