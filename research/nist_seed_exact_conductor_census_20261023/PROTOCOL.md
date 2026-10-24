# Exact Frobenius-order conductor census for comparable seed classes

Frozen 2026-10-23 UTC before the 17 new discriminant factorizations. This is a
structural catalog and a retrospective selector check, not an ECDLP experiment.

## Inputs and fixed scope

- `research/nist_seed_skipped_curves_20261016/assessed.json`, SHA-256
  `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`:
  all 11 omitted seed-level classes, retaining one class for the isomorphic
  P-224 sign pair.
- `research/nist_seed_skipped_curves_20261016/traits.json`, SHA-256
  `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`:
  the eight published classes over the same four fields (P-192, the 239-bit
  ANSI prime, P-224, P-256). Exclude P-384 and P-521 because their timestamp
  streams contain no named omitted candidate and offer no within-field control.
- Reuse only the two already sealed P-256 results from
  `research/nist_seed_exact_conductor_20261023/runs/first-stage-20261023T1720Z/verification.json`,
  SHA-256 `520c8d373e0f6d7eff8ab0d65acf28b0bff5c0ff0e7afaa7b53b841916b14e9e`.
  Its omitted block 876 and published block 1842 both have `f_pi=1`.

The remaining fixed set is ten omitted blocks `36, 1562, 2491, 2682, 2863,
2198, 5405, 777, 1485, 5736` and seven published controls `prime192v1,
prime192v2, prime192v3, prime239v1, prime239v2, prime239v3, secp224r1`.
Bind every row by its EC1 UID, p, n, source digest, seed ordinal and label.

## Arithmetic and controls

For each row, compute `t=p+1-n` and `Delta_pi=t^2-4p`, then completely factor
`|Delta_pi|` with GP/PARI. Derive the fundamental discriminant `D_K` and the
positive integer `f_pi` from `Delta_pi=f_pi^2 D_K`. Retain every GP input,
stdout, stderr, exit status, full factor list, process wall time and sampled
peak resident memory. Sage separately re-reads each source row, checks every
factor with `is_prime(proof=True)`, recomputes full products and identities,
and binds the raw transcripts by SHA-256. The two tools may share PARI
internals; this is a separate arithmetic check, not a second factorization.

Run three fixed synthetic controls `(-75,-3,5)`, `(-7,-7,1)`, and
`(-12,-3,2)` as `(Delta_pi,D_K,f_pi)`. Inject an unexpected exception and an
early return in separate launcher controls; each must fail nonzero without a
completion marker. Each GP call has a 180-second wall watchdog, a 1 GiB GP
arithmetic stack and a sampled 2 GiB resident-memory watchdog. Run cases
serially. A timeout or crash is censored and retained, never called a
mathematical negative. Write a completion marker only after all 20 cases
(three synthetic, 17 new real) and Sage verification pass; otherwise retain a
partial progress record. New run directories are write-once.

## Precommitted interpretation

Tabulate the exact 19 `f_pi` values by label and field; compare any nontrivial
conductors and the squarefree fundamental discriminants. This cannot restore
the already falsified universal rule `all omissions have f_pi>1`. A different
perfect split, if found, is a candidate retrospective criterion only and
requires an explicit attack mechanism, a matched control and independent
historical prediction before it can explain selection. If no split appears,
conclude only that exact Frobenius-order conductor does not separate the named
labels. Class-wide implications use only `f_E | f_pi`; no representative
endomorphism ring, rational isogeny degree, or ECDLP cost is inferred from a
nontrivial `f_pi` alone.

Retain code, raw receipts, verifier output, a dated report, an editable graph,
vector figure and visually checked PDF. Do not modify the prior sealed run.
