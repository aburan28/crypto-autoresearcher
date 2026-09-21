# Expanded idea-to-experiment inventory

This additive inventory expands the canonical-only `coverage-before.json`; that frozen earlier artifact is retained. This is administrative coverage work, not a research finding or goal completion.

The updated census discovers **2,314 unique idea identities**: 1,879 ledger ideas, 413 identified Markdown records under `ideas/`, and 22 additional ideas in archived proposal lists. The archived lists contain 168 entries, including 146 identities also present in the ledger; these copies remain visible for reconciliation and are not counted twice. Source paths, locations, status labels and hashes are retained. All statuses remain in scope.

With this checkpoint's six source specifications present, 745 ideas have explicit experiment lineage and **1,569 do not**; 968 of the latter are classified ECC through the central policy. There are 109 ideas with legacy contract candidates, kept separate from canonical coverage. The inventory reports 18 historical parse uncertainties, 55 unresolved area classifications, and zero unknown source IDs. An explicit link is not a semantic judgement that every source prediction has a complete experiment.

The original canonical-only baseline was 1,879 ideas and 1,146 without explicit experiments. It was an incomplete denominator for the user objective “all ideas.” This expansion corrects discovery scope without rewriting that snapshot or lowering the objective. No legacy record, retired contract or malformed historical artifact was edited.

`tools/idea_experiment_coverage.py` now reads archived YAML/JSON-encoded YAML proposal lists and identified legacy Markdown records, preserves source identity duplicates, and separately inventories legacy preflight contracts. Review quotations do not originate new ideas. Corpus classification comes from the declared `ideas/README.md` scope and the central ECC area policy, never the legacy identifier prefix alone. Fourteen focused unit tests pass, including citation-only noncoverage, hypothesis-only gaps, archived duplicate identities, hash-pinned schema supersessions, legacy unapproved contracts and review-quotation exclusion.

The snapshot `coverage-expanded.json` was generated after the three source archive commits. Its `source_commit` and per-source hashes bind that candidate tree. Final group archives and the published branch provide durable source bindings. The census command exits 1 because the 18 historical parse uncertainties remain visible; this is not a successful complete census or evidence against a mathematical hypothesis.

Next action: reconcile duplicate-source semantics and existing legacy contracts, then continue source-matched experiment design in ECC-first order. Every proposed completion needs source-mechanism and quantitative-prediction mapping, frozen controls, complete costs, artifacts and Coordinator approval. A full-ledger PASS alone cannot discharge this semantic coverage debt.
