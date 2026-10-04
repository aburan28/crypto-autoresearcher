# Source-pin note: Simon's "n"

Required artifact per specification.yaml required_artifacts item 2
("The source-pin citation for Simon's n ... as a standalone, independently
checkable note").

This pin was done at design time (specification.yaml
`inputs.n_definition.pinned_literal_definition`) and is reproduced here
verbatim, unrecomputed, per that field's own text: "This pin is source-cited
and design-time-complete; it is not recomputed by this experiment's runtime."

## Citation

`inputs/DCP-SIMON-2026/paper_extracted_text.txt`, pages 1-3:

> "p(n)-SVP is the problem of finding a non-zero vector in an n-dimensional
> lattice"

DCP group order `2N ~ 2^(n+1)` post-BKSW; Regev's original quadratic blow-up
`N ~ 2^(n^2)` is removed by BKSW (KN-LIT-4706), per
`knowledge/techniques/KN-TECH-d1bc4f.md` ("The BKSW improvement ... removes
the quadratic dimension blow-up in Regev's original reduction").

So Simon's "n" is the dimension of the SVP/LWE lattice the reduction operates
over -- an unstructured-LWE dimension, by construction of the cited reduction
chain (Regev 2004 -> BKSW -> Simon 2026).

## Working substitution for ML-KEM (disclosed, unverified)

`n := k_mlkem * 256` (module rank times ring degree n_ring=256), stated in
specification.yaml `inputs.n_definition.working_substitution_for_ml_kem` as
an EXPLICITLY DISCLOSED, UNVERIFIED WORKING DEFINITION: "BKSW's reduction is
stated for unstructured LWE, not Module-LWE, and KN-OPEN-8a5965's own Q2 names
this bridge as fully open."

This run carries that caveat forward on every table below: every reported `n`
value (512 / 768 / 1024) is the WORKING SUBSTITUTION, not a citation-backed
equivalence. No claim in this run's outputs asserts the bridge is validated.

Giving: ML-KEM-512 -> n=512, ML-KEM-768 -> n=768, ML-KEM-1024 -> n=1024
(exactly specification.yaml `inputs.n_definition.giving_n`, unaltered).
