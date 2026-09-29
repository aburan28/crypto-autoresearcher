# Pre-authorisation arithmetic checks for IDEA-20260815-f558e4

**These are NOT run records.** They carry no `RUN-*` id, were not executed under
`harness/runner.py`, and produce no evidence. No `EV-*` record may cite them, and
no claim in the ledger may rest on them.

They exist for one reason: `IDEA-20260815-f558e4` quotes specific numbers in its
`claim` section (G) and in `sota_delta`, and AGENTS.md rule 5 forbids asserting a
number that was not measured. These scripts are how those numbers were produced,
committed so a reviewer can re-derive them before any compute is authorised.

## Scripts

| script | what it computes |
| --- | --- |
| `propagation_ceiling_check.py` | `q_strict` and `q_maj` for interval and random balanced partitions of `Z/N`, exhaustively over all `N^2` pairs, at `N` in {11, 23, 31, 37, 41} and `s` in {2..5}. |
| `toy_curve_smoke_check.py` | the same two statistics for an efficiently computable x-coordinate bucket and for the DL-interval partition, on toy curves `p` in {101, 103, 107}. |

Run with `python3 <script>`; no dependencies beyond the standard library, and
each finishes in seconds.

## What they showed

- `q_strict = 0.0000` in **every** tested cell, for both interval and random
  balanced partitions — consistent with the Cauchy–Davenport argument in claim
  (C) with no exception.
- `q_maj` for the interval (arithmetic-progression) partition stayed in
  0.5217–0.5785 and was **flat in `s`**, while random balanced partitions tracked
  the `1/s` baseline downward (0.6198 at `s = 2` to 0.2635 at `s = 5`).
- On the toy curves the efficiently computable x-coordinate bucket exceeded its
  `1/s` baseline by 0.03–0.09, against an expected Weil scale of
  `N^{-1/2} ≈ 0.095` at those sizes; the DL-interval statistic held 0.504–0.524
  flat across all `s`.

## Two limitations, recorded rather than buried

1. **The curve script uses the full group, whose order is composite**
   (`N` = 115, 118, 105). Cauchy–Davenport does not apply there. That script is a
   smoke check on the measurement code, **not** evidence for claim (C). The frozen
   protocol in the proposal requires prime-order subgroups throughout.
2. **Floating-point output.** Both scripts report ratios as floats. The proposal's
   Stage 2 requires exact rational arithmetic, because the quantities are ratios
   of integers and there is no reason to accept floating-point agreement on a
   forced gate.
