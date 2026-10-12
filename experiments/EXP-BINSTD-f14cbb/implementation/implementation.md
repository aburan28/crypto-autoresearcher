# Implementation notes — EXP-BINSTD-f14cbb / TASK-20261001-109e55

## Instrument

- `implementation/cyclotomic.py` — Moebius `Phi_k(2)` via `v_p(2^d-1)` modular
  lifting for the k<=20000 census; exact integer Moebius for Phi_130(2).
- `implementation/gf2n_local.py` — self-contained schoolbook `F_{2^n}` (no import
  of `EXP-CERTBIN-e94b27/impl/gf2n.py`).
- `implementation/composite_field.py` — compositum `F_{2^k}·F_{2^n}` with CRT
  relative Frobenius and Hilbert-90 torsor solve.
- `implementation/torus_row.py` — Stage 1 (n=17) and Stage 2 (n=131) Lemma L
  image, nulls, basis-relabel.
- `implementation/run_stages.py` — stage driver + immutable run packages.

## Deliberate non-claims

- Couveignes–Lercier primary text was **not** read.
- No break / factor-base / rho competitiveness.
- `certificate.kind: none` on every run (structural only).
- Amazon Bedrock unused.

## Protocol deviations

1. Stage 0 census uses Moebius **valuation** of `(2^d-1)` (modular) rather than
   building full `Phi_k(2)` integers for every k<=20000. Semantically identical
   to the specified Moebius product; exact `Phi_130(2)` still uses the integer
   product + `(2^65+1)/(8193×11)` cross-check.
2. Composite-field path used for both Stage 1 and Stage 2 (preferred by the
   frozen contract for `F_(2^17030)`).
3. Stage 1 also records a seed-20261002 replication summary inside the same
   run package (spec lists seeds `[20261001, 20261002]`); not a separate RUN id
   (within `maximum_runs: 8`).

## Observed (no interpretation)

- Stage 0: `{k<=20000: 131|Phi_k(2)} = {130,17030}`; phi 48, 6240;
  `Phi_130(2)=409368176241571=131×3124947910241`, `v_131=1`; cross-check OK;
  modulus-swap p=17 → `{8,136,2312}`.
- Stage 1: dim=8, Frobenius-stable, equals `ker m_t(σ)`; both Phi_17 factors
  found (V equals only `m_t`'s ker); random-b stable count 0/10; order-15 nulls
  reported; basis-relabel invariant.
- Stage 2: composite-field completed; dim=130, equals `T_0` / `ker Tr`;
  analytic unknowns/slot 17030 vs 131 one-hot (modeled column).

## Not claimed

- Outcome A/B/C decision (Coordinator/Reviewer).
- Hypothesis status change.
- That infrastructure absence would have been falsification.
