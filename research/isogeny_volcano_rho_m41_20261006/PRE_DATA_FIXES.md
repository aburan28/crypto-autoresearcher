# Fixes after the protocol hash and before any rho data

`PROTOCOL.sha256` was taken when `PROTOCOL.md` was frozen. These changes came
later, and all of them came before any rho solve for this study was run.
None changes the protocol's design, sample or analysis.

1. **`vert.gp`, Frobenius conjugates.** The minimal-polynomial step used
   `c^(2^41)`, which is the identity on F_2^41, so every "conjugate" equalled
   Δ′ and the step aborted with "minpoly not over F_2". It now uses `c^2`,
   the 2-power Frobenius. That error check is what caught the bug.
2. **`vert.gp`, root finding.** `polrootsmod` rejected the finite-field
   modulus form. Roots are now found with `factor` over F_2^41.
   `conj` (a GP built-in) was renamed `cj`.
3. **`vert.gp` → `vert_lib.gp` plus `v409.gp` / `v1721.gp`.** The two
   isogenies now run as separate processes. The minimal polynomial is written to
   `minpoly_<l>.gp` before the final step, so a late failure does not discard
   about 40 minutes of extension-field work. The finishing step was
   unit-tested first on a synthetic F_2^41 element inside F_2^123: it found all
   41 conjugate roots and rejected a curve outside the class through the
   `ellcard` check.

The char-2 Vélu shortcut itself (b′ = 1 + v + v²) is unchanged. It was
checked against PARI `ellisogeny` on 6 random 73-isogenies at m = 37, and all
6 matched exactly.

`PROTOCOL.sha256` is left as frozen. `PROTOCOL.post-fix.sha256` records the
hashes after these fixes.

## Correction to a statement in the frozen PROTOCOL.md

`PROTOCOL.md` says that at M = 41 the old `Q2[32]` table made "40/40 test
solves" get rejected by the verifier. That overstates the record. The
pre-fix smoke test ran 5 negation-only solves; the rows inspected had
`ok = 0`. A Frobenius-mode run aborted on the canonicalisation self-check
before completing any solve. The 40/40 figures belong to the post-fix runs
(negation only and Frobenius), and every one of those verified. The
protocol text is left unedited, as it was frozen; this note supersedes that
sentence.
