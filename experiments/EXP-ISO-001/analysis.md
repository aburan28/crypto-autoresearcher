# EXP-ISO-001 analysis — isogeny-neighborhood PDP audit

**Run:** `RUN-ISO-001-a` (valid). `p=8209`, base curve order **8304**, `m=3`, `d=8`.
Neighbors: 2-, 3-, 5-isogeny codomains (all order 8304, per Tate); no distinct rational
7-isogeny neighbor. Controls: 8 random same-p curves (coefficient variance, orders 8068–8374).

## Result

| curve | order | same order | d_reg | yield |
|---|---|---|---|---|
| base | 8304 | ✓ | 2 | 0.01445 |
| iso2 | 8304 | ✓ | 2 | 0.01385 |
| iso3 | 8304 | ✓ | 2 | 0.01445 |
| iso5 | 8304 | ✓ | **3** | 0.01337 |
| ctl (×8) | 8068–8374 | ✗ | mostly 2, one **3** | mean **0.01450**, sd 0.00043 |

## Verdict (against the frozen criteria) — falsification MET

- **d_reg:** no isogeny neighbor has `d_reg < 2`. The occasional `d_reg=3` appears in
  *both* the isogeny set (iso5) and the controls (order 8130) — it is small-factor-base /
  coefficient variance, **not** an isogeny effect.
- **Yield:** isogeny yields [0.0138, 0.0145, 0.0134] all lie **inside** the control band
  (mean 0.0145 ± 0.0004; `mean−3sd = 0.0132`). `any_iso_yield_outlier = False`. Decomposition
  yield ≈ 0.0145 is governed by the `|FB|^3 / N` combinatorics, shared by isogeny neighbors
  and controls alike.

**Scoped negative — no weak isogenous PDP neighbor.** Isogeny structure changes neither the
Semaev solving degree nor the decomposition yield beyond generic coefficient variance, with
matched controls separating the two. Consistent with idea-23 (isogeny-walk falsification).

## Boundaries
Toy (`p≈2^13`); single base curve / audit instance; `l ∈ {2,3,5}` neighbors reached; `d=8`,
`m=3`. Closes only this scope (AGENTS rule 6). Yield is a constant-factor metric, not an exponent.
