# Verified fixed-circuit transfer study

The complete classical experiment used 40 fresh curves, 2,508 public targets and 102,828 primary attempts. Independent verification passed with no errors; both original and canonical unified exports passed their file checks. Eight candidate arms produced 226 verified recovery events covering 181 target-arm pairs. BSGS solved all 2,508 targets. All 320 candidate cells, including 301 zero-success cells, remain visible.

The finite F23/order17 domain has exact validator recovery probability 8/16 under fresh nonzero blinding. The actual candidate recovered 40/64 attempts and all16 targets at least once. Its modeled cold group-call component was 89.675, compared with11.75 for matched BSGS. Other operation families and common work remain separate; these are emitted counters, not qualified time or attack-cost bounds.

- [Readable report](report.pdf) and [Markdown report](report.md).
- [Working domains, exact small probability and paired costs](working-scope.md).
- [Postprocessing corrections and original refusals](postprocessing-provenance.md).
- [Committed neutral observations](observations.json) and [all positive domains](working-domain-supplement.json).
- Canonical unified export: `evidence/export.json`; actual independent verifier: `evidence/verification/report.json`. Their logical gzip pointers bind complete content hashes.

Oversized JSON, CSV, PDF and archives are in the content-addressed artifact store with one logical blob pointer each. [Artifact documentation](../../../../docs/artifact-storage.md) describes hydration. `artifact-readback.json` records complete S3 GET checks. Every outside postrun/renderer/refusal tree is retained in `evidence/*.tar.gz` with member inventories and verified archive hashes. The original frozen renderer and its initial presentation issues are preserved separately; the readable presentation changes no data or statistical criteria.

The predecessor operational attempt is retained under EXP-ECDLP-ef7323/reports/run-20261028T1702Z. It stopped before any VM or scientific data. Its zero-row export passes the generic schema but does not meet planned cohort/arm coverage; its exact refusal remains preserved. The successor is the sole actual scientific invocation. Hypothesis remains specified and goal active; no exponent or global novelty claim follows from this finite cohort.
