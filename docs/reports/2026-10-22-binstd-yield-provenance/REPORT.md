# BINSTD toy-yield evidence provenance audit

This audit adds named source readings to the two archived BINSTD yield
evidence records. The originals, run artifacts, ratios, decisions and
performance claims are unchanged. The [editable graph](audit.dot),
[SVG](audit.svg), [PNG](audit.png), [figure PDF](audit-figure.pdf) and
[report PDF](report.pdf) show the evidence chain and the scoped result.

## Source reading and arithmetic

I read the hypothesis and its source heuristic, the parent experiment
contract, the structural evidence and refine decision, the two additive
amendments, their approval decisions, the first yield evidence and its
weaken decision. The first yield record tests the approved n=17,
ell={8,9} panel after the original ell={3,4} panel was found
structurally inadmissible. The second record repeats the same toy
panel, solver and threshold under a distinct frozen seed. The archival
scope is exhaustive FB-sum m=3, 40 targets per cell, Stages 0-1 only.

The [focused checker](verify.py) establishes structured equality after
removing the 16 new `verified_by` notes. It also checks that both
archived Stage-1 matrices match the SHA-256 values in their run results,
then recomputes all four ratios from the published aggregate hit
counts. First seed: tau/open hits are 16/40 vs 40/40 at ell=8 and
40/40 vs 40/40 at ell=9, giving 0.4 and 1.0. Second seed: 20/40 vs
40/40 and 40/40 vs 40/40, giving 0.5 and 1.0. The open arm reaches
40/40 in every cell, so the pre-registered 1.25 ratio is unattainable
at those observed open-arm rates. The [receipt](verification.json)
records exact source and replacement hashes.

This is an aggregate-arithmetic and provenance check. It does not
replay the per-target solver, independently establish target sampling,
or prove a relation-yield theorem in Lean. The historical decisions
remain preliminary `weaken` after one seed and `reject_scoped` after
replication, confined to n=17, ell={8,9}, the frozen solver pin and
40-target toy setting. No break, asymptotic exponent, deployed
insecurity or larger-n claim follows.

## Ledger gate

Both frozen records remain unchanged. Their additive replacements
are bound to original and replacement SHA-256 values in
`tools/schema_supersession_registry.yaml`. On the exact parent PR
commit `5e499ba86dfa5fde589c353d446433ad0cdcab3e`, the
complete-tree validator reported 136 unsuppressed errors in 38 paths.
With only these two replacements and the registry overlay, it reports
120 in 36 paths: precisely the 16 citation-reader errors disappear,
none is added. Both runs exit 1. The [delta receipt](validation.json),
[baseline log](../2026-10-22-binstd-source-provenance/validator.log) and
[new log](validator.log) preserve the comparison. The all-corpus
integrity gate remains red.
