# Implementation notes — EXP-BINSTD-9d1b8e Stages 0–2

Task: `TASK-20261001-0fc34d`. Observations only; no H/EXP/IDEA status changes.
No break claim.

## Code

| Path | Role |
| --- | --- |
| `implementation/gf2n.py` | Schoolbook `F_{2^n}` + Artin–Schreier solve (even/odd `n`) |
| `implementation/curve.py` | Binary `Y^2+XY=X^3+AX^2+B` arithmetic + Frobenius point map |
| `implementation/stage0_run.py` | Five-row arithmetic certificate + dual rho + ECC2K-130 note |
| `implementation/stage1_extract.py` | Literature fetch/extract / A3 status |
| `implementation/stage2_run.py` | Toy cells, pi₂ checks, null/degenerate/composite controls |

Field/curve arithmetic adapted from `experiments/EXP-CERTBIN-e94b27/impl/`
(schoolbook path). CERTBIN `half_trace` is odd-`n` only; Stage 2 needs
`n∈{20,24,28}`, so Artin–Schreier is solved by `F_2`-linear algebra.

## Protocol deviations

1. **Silverman Appendix A** was not opened as full text (no free fetch). Stage 1
   used the peer-reviewed equivalent allowed by the specification:
   Kronberg–Soomro–Top, *Twists of Elliptic Curves*, SIGMA 13 (2017) 083
   (doi:10.3842/SIGMA.2017.083; arXiv:1707.01139), which states Aut=±1 in
   char 2 unless `j=0` and cites Silverman Appendix A. Washington §2.8
   supplied `j=1/a₆'` for the `y²+xy=x³+a₂x²+a₆` form. Provenance recorded
   as `retrieved` with `verified_by: TASK-20261001-0fc34d`.
2. **Composite-k' SEARCH** exhausted 64 ordinary `E/F₁₆` candidates with odd
   `t` without finding a prime `r>2¹²` dividing `#E(F_{q^{k'/p}})` for
   `p|6`. Outcome `not-found-within-budget` (neither forced success nor
   forced failure). Optimistic-assumption disclosure from the specification
   applies: budget 64 may leave the nearby-object control incomplete.
3. **Stage 2 Weil orders** for `(4,5)`/`(4,7)` used the audited base trace
   `t=5` (`#E(F₁₆)=12`) plus Weil recursion rather than brute-force counting
   `#E(F_{2^{28}})` (infeasible under the wall budget). Base count and the
   `(4,5)` Weil identity were spot-checked by `count_by_trace` on `F₁₆` and
   `F_{2^{20}}`.
4. Run manifests record `code.dirty: true` at execution time because Stage
   artifacts were written before commit (immutable run records; not rewritten
   after commit).

## Seeds / randomness

Primary seed `20260926` (specification). Used for point sampling, null/
degenerate curve draw, and composite candidate shuffle. No other RNG sources.

## Bedrock / AUXIN

No Amazon Bedrock invocation. No AUXIN path edits.

## Comparison vs frozen prediction (observations only)

| Item | Frozen | Observed |
| --- | --- | --- |
| Stage 0 gcd/t-odd/Weil | all five pass | all five pass (`RUN-BINSTD-1ee50c`) |
| Corrected rho bits | [78.10, 93.98, 125.78, 141.71, 173.57] ±0.01 | within tol; dual inherited column present |
| Stage 1 A3 | discharged via retrieved **or** unrecovered | **discharged** / retrieved (`RUN-BINSTD-82b5eb`) |
| Stage 2 ord(π_q) | 5 and 7 | 5 and 7; certificates verified |
| π₂ on B∉F₂ | failures = N/N for x∉F₂ | pass |
| Null / degenerate | no π_q endomorphism / detects π₂ | both pass |
| Composite search | found **or** not-found-within-budget | not-found-within-budget |
| Break claim | none | none |
