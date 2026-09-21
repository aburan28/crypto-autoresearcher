# EXP-REP-001 analysis — model-native PDP solving degree (Edwards vs Weierstrass)

**Run of record:** `RUN-REP-001-c` (valid; supersedes `-a` strawman, `-b` JSON bug).
**Scope:** `p = next_prime(2^16)`, `m = 2`, factor-base degree `d ∈ {4,6,8,12,16}`,
3 seeds, on twisted-Edwards-admitting curves mapped to their Weierstrass form
(Edwards→Montgomery→Weierstrass map verified on-curve for every seed).

## Result (d_reg = output GB max total degree; all arms dim=0, planted decomposition = root)

| d | W_semaev (fair baseline) | ED_x | ED_y | W_native_x (y-explicit, suboptimal) | random null |
|---|---|---|---|---|---|
| 4  | **2** (vdim 2) | **2** (2) | **2** (2) | 4  (vdim 10) | 6 |
| 6  | **2** (2) | **2** (2) | **2** (2) | 6  (14) | 8 |
| 8  | **2** (2) | **2** (2) | **2** (2) | 6  (18) | 10 |
| 12 | **2** (2) | **2** (2) | **2** (2) | 10 (26) | 14 |
| 16 | **2** (2) | **2** (2) | **2** (2) | 12 (34) | 18 |

Identical across seeds 1–3. Every `d_reg=2` arm is a **genuine non-degenerate solve**:
`dim=0`, `vector_space_dimension = 2` (the two ordered decompositions `{F0,F1},{F1,F0}`),
and the planted decomposition satisfies all generators.

## Interpretation (against the frozen criteria)

- **Falsification criterion MET.** H-REP-001 predicted Edwards `d_reg` scaling *strictly
  below* the matched Weierstrass baseline. The **fair** Weierstrass baseline —
  `W_semaev` (y-eliminated Semaev, x-membership, the standard PDP formulation the
  ecdlp-autolab corpus uses) — is **`d_reg = 2` flat**, identical to Edwards-native at
  every `d`. So the model-native solving degree is **invariant** between the best
  formulation of each model. No scaling advantage.
- **The apparent Edwards win is a formulation artifact, not a model property.** It
  appears only against `W_native_x` (Weierstrass with `y` kept explicit), whose `d_reg`
  and solution count grow (`vdim ≈ 2d+2`) because the explicit `±y` sign branches admit
  spurious solutions. Eliminating `y` — the standard Semaev step — removes them and
  returns `d_reg=2`. Edwards reaches `d_reg=2` *natively* only because its equation is
  biquadratic (quadratic in each coordinate → the GB auto-eliminates); this is a
  **formulation convenience, not a sub-birthday exponent change**: both best-formulations
  sit at `d_reg=2`, so the per-PDP solving-degree exponent in `d` is model-invariant.
- **Consistency check:** `W_semaev = 2` reproduces the corpus T1 result (Weierstrass
  Semaev `d_reg` flat at 2), confirming the instrument.

## Boundaries (per AGENTS.md rules 6–7)

- Toy scale (`p = 2^16`, `m = 2`, `d ≤ 16`); **not** a crypto-scale statement.
- Scoped to curves admitting a twisted-Edwards model (rational order-4 point). Says
  nothing about generic Weierstrass curves without that torsion, nor about `m ≥ 3`.
- `d_reg` (output-GB max degree) is the tested metric; total wall-time was
  sub-millisecond and not exponent-informative at this scale.

## Verdict

**Scoped negative — model-invariant.** No improvement meeting the predefined threshold
(Edwards `d_reg` scaling strictly below the fair Weierstrass Semaev baseline) was observed
over the tested curves, parameters, solver, and budget. The best formulation of each model
solves the `m=2` membership-constrained PDP at `d_reg = 2`. Recommend weakening H-REP-001
to a scoped negative; no escalation to a scaling study is warranted by this evidence.
