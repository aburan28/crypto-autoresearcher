# Positive-order near-primality replay under the 1997 draft

**Frozen before reading the residual primality outcomes, 2026-10-24 UTC.**
Question: Among already retained *positive exact* `ellsea(E,1)` point-count
outputs in the six recovered prime-field stream prefixes, how many additional
seed positions satisfy the 17 November 1997 X9.62 near-primality check with
the draft's example trial bound `l_max=255`? This is a **lower bound** on the
full draft-compatible set because zero outputs are censored early aborts and
are not proven negative cases.

Inputs: six `research/nist_seed_provenance_20261016/census/orders_<timestamp>.txt`
files for timestamps `863711343`, `863966734`, `871002724`, `871696354`,
`872952608`, and `891607927`; the corresponding field primes in
`research/nist_seed_selection_20261016/targets.json`; the validated
`research/nist_seed_selection_20261016/raw/full_census_crosscheck_v4.json`;
and the source PDF `/private/tmp/x962-11-17-97.pdf` with SHA-256
`0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e`.
The complete input hashes are saved with the run. Do not modify these files.

For each positive selected-root and opposite-root exact order `u`, divide out
*all* factors of every prime `l<=255` exactly as draft §F.2.2 specifies.
Let `u=h*n`. Use PARI/GP `isprime(n)` (a stronger mathematical classification
than the draft's probable-prime test), then check `n>2^160`, `u!=p`, and
`p^k != 1 mod n` for each `1<=k<=20`. Also report a 1998-comparable profile
requiring `n>4*sqrt(p)`, evaluated by the exact integer inequality
`n^2>16p`. The 1997 profile uses `r_min=2^160+1`; the 1998-comparable profile
uses both minima. Count qualifying root branches and distinct seed positions,
deduplicating P-224's isomorphic signs. Compare the previous 69 full-prime
positions as positive controls. Use composites 9, 21 and 341 as negative
primality controls, and the published/omitted 21 positions as indexed controls.

The launcher must retain the exact GP input, stdout, stderr, source hashes,
command, versions and output rows in a fresh run directory. Fail closed on
missing, duplicate or out-of-window indices, a source-hash mismatch, an
unexpected control outcome, or a GP timeout/exit failure. GP gets a 120-second
wall timeout and no per-case retry. The run may be repeated only in a fresh
directory. Report exact observed coverage, censored zero rows, classifications
and limits; do not claim a complete near-prime census or historical visitation.
An independent verifier must recompute all small-prime divisions and both
minima from the archived positive exact orders and compare every GP result.

Deliver report Markdown, exact JSON, editable graph source/SVG, and visually
inspected PDF. Update the open selection problem if the observed lower bound
or next action changes.
