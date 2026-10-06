# Implementation notes — EXP-BINSTD-ef7fa4 / TASK-20261001-2fe20a

Observations only. No hypothesis-status change. No break / rho / exponent claim.

## Protocol deviations

1. **l=6 e-count is sampled** (`2^24` assignments per target) as authorized;
   spurious factor reported both as sampled/genuine lower bound and as a
   **scaled estimate** (`× 2^{33-24}`), labeled ESTIMATED — not a retune of the
   frozen prediction band.
2. **l=4 and l=5 poly-basis genuine count was 0** over 50 targets, so P1
   (e/genuine) is undefined there. e-space counts still match
   `2^{∑dim−n}` (16→17.5 at l=4; exactly 1024 at l=5). Lift agreement on the
   empty genuine set treated as vacuous `1.0`.
3. **Stage 2 random subspaces** saturate faster (dims `[4,10,17]` / `[5,15,17]`);
   exhaustive infeasible → sampled `2^24` with disclosed censoring. Poly-basis
   P1 undefined at matched l, so P3≥P1 numeric compare is `null`; random arm
   produced positive genuine counts and large sampled spurious factors.
4. **Stage 3 orbit_closure_ratio** measured as
   `(sum of W_4 work over 17 conjugates or unrelated targets) / (17 × one-instance W_4 work)`
   using S_3 Weil descent over a dim-8 basis (plain descent instrument).
   Koblitz uses `ker g(σ)` with `g=0b100111001`; ordinary null uses poly window
   dim 8 with 17 unrelated on-curve abscissae.
5. Initial l=6 scalar sampler was killed as infrastructure slowness and replaced
   by a vectorized sampler before recording `RUN-BINSTD-0a6a59` (no partial run
   package retained).

## Certificate discipline

- Stage 0 / metric-only runs: `certificate.kind: none`.
- Each enumerated genuine decomposition at l=6 carries an independent
  `decomposition` re-check in `stage1/cell-l6.yaml` (S4=0 on a fresh curve
  object). Pooled run manifests remain `kind: none` with pointers to those
  certs.

## Environment

- Python 3.12 + numpy; CERTBIN `gf2n`/`curve`/`closure` copied under
  `implementation/`. Amazon Bedrock not used. No AUXIN / H/EXP/IDEA status edits.
