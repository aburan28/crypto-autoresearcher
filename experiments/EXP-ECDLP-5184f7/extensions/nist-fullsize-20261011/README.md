# Full-size P-192 / P-224 prospective extension

RUN-ECDLP-d0e449 compares the exact fixed primes with 288 random control fields
each. The contract fixes selection, controls, stopping and 99.9% inference
before sampling. It is separate from RUN-ECDLP-a24605 and RUN-ECDLP-07aad1;
no old observations are pooled.

`implementation/prepare_nist.py` generates 512 uniform nonsingular models per
fixed prime, four per random field, exact curve orders and bounded partial
factorization. `run_attacks_nist.py` runs public synthetic targets with the
multiprecision C++ kernel. Only 16–20-bit subgroups are solved to completion.
128-bit-and-larger prime subgroup walks stop at 4,096 search calls and cannot
settle full-size ECDLP. Known NIST standard-curve anchors are distinct from the
uniform random-curve models. `arithmetic_nist.py` measures full-field operations;
`analyze_nist.py` performs the frozen statistical summaries.

Inference clusters random control fields. The 512 S models are independent
curve draws over **one fixed prime**, not independent prime draws. Matched
assignments are held fixed during bootstrap; confidence coverage is approximate.
The three-family primary interval reserves error probability for the wider
Solinas test and these two fixed-prime cases. It does not simultaneously cover
every diagnostic.

Use `execute_nist.py` after source commit/build/instrument checks. All output
directories are fresh, observations immutable, and reports/source/raw results
remain in the new run directory. PRs publish observations without scientific
promotion. Historical graphs, runs and reports remain as archived.
