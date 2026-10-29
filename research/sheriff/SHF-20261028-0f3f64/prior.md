# Prior (written 2026-10-28, before reading any of the audited changes)

Target: all (deep) on origin/main of crypto-autoresearcher, crypto and
cryptanalysis, plus the five named changes and every finding of
SHF-20261016-3caa6f and SHF-20261017-e4d7f6.

What I expect to find broken, and why:

1. stark_v2 DEEP-ALI (crypto#2439). DEEP additions are where frozen-heart and
   degree bugs live. I expect at least one of: OOD values f(z), f(ωz) absorbed
   after (not before) the DEEP combination challenges, or not at all; the
   verifier taking the DEEP quotient value from the proof rather than
   recomputing it from the opened f(x), f(ωx); a degree bound that ignores
   the division by (x − z) (the quotient has degree deg f − 1, which is fine,
   but the λ-adjustment / degree correction is commonly wrong or untested);
   a soundness ε stated without the DEEP term (ℓ·d/|F| style) or with SHA-256
   collisions ignored. Negative tests likely cover only some of the new checks.
2. complete_manifest (#2488). Likely sound on the happy path; I expect a gap
   in "refuses contradictions" (e.g. a field present in both sources compared
   loosely, or only some fields compared) or in byte preservation (re-serialised
   JSON rather than the driver's bytes).
3. Ledger (#2497). Error count on main has probably moved since the PR (new
   records). I expect the 143 -> 126 figure to be reproducible only at the
   PR's merge commit, not on today's main, and one or more manifest_v2
   records to carry a field not present in archived bytes.
4. cryptanalysis #1077. Op-count band numbers probably reproduce; I expect a
   rounding or a band ordering statement that does not hold across the full
   0/0.1/1 band, and "unresolved vs rho" to be stated loosely.
5. Lean L-N9: still open; TranslationDescent likely still builds; the
   whole-workspace build may exceed disk.
6. Deferred items: unchanged (validate_ledger errors remain; GAE band for the
   rank-finder producer unported; lean-verification still disabled).
