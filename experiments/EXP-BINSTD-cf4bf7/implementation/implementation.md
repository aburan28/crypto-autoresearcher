# Implementation note — EXP-BINSTD-cf4bf7 / TASK-20261001-18804b

## Scope executed

Required Stages **0, 1, 4** completed. Optional Stages **2–3** probed;
WDSat/CNF-XOR absent → `instrument_unavailable` (infrastructure), not
mathematical evidence.

## Code layout (write_scope only)

- `implementation/gf2n.py` — schoolbook `F_{2^n}`, Artin–Schreier solver, F_4 embed
- `implementation/curve.py` — binary Weierstrass + Hasse/BSGS order via point-order LCM + Weil n|(q−1) filter
- `implementation/arithmetic.py` — corrected ladder, ord/f census, `ord_17(4)` lattice, f certificates
- `implementation/runpack.py` — immutable run packages (`certificate.kind` vocabulary enforced)
- `implementation/stage0_run.py`, `stage1_run.py`, `stage4_run.py`, `stage2_3_probe.py`

## Protocol deviations

1. **Ladder error_pp rounding.** Frozen H-BINSTD-4a2f99 errors use 3-decimal
   deployed/toy ratios then 1-decimal pp. Recomputation matches that convention
   (pair 1: exact 4.405…pp → frozen +4.5pp via `round(ratio,3)` intermediates).
2. **Stage 1 order method.** No Sage/PARI in environment. Orders obtained by
   deterministic Hasse-interval BSGS annihilators → LCM of point orders →
   filter candidates with structure `E ≅ Z/n × Z/m`, `n|m`, `n|(q-1)`.
   Cross-checked on n∈{5…12} against exhaustive counts before n=34/37 runs.
3. **Stages 2–3.** No WDSat binary on PATH and no `tools/` engine →
   `stage2/instrument_unavailable.yaml` + `stage3/skip-with-stage2.md`.
4. **Curve coefficients.** First successful F_4 (resp. F_2) candidates were
   `(A,B)=(0,1)` for both arms; frozen in `stage1/curve-construction.yaml`.

## Non-deviations (guards held)

- n=31 labeled `contrast_not_null` only; never a null arm
- n=41 labeled `rejected_poor_control`; not used as poor lattice control
- No deployed n≥131 attack runs
- No break / rho claim
- All run manifests use `certificate.kind: none`
- Amazon Bedrock not used

## Runs

| RUN ID | Stage | Status | Notes |
|---|---|---|---|
| RUN-BINSTD-7d4512 | 0 | completed_valid | ladder+census+lattice+predictions |
| RUN-BINSTD-847e2c | 1 | completed_valid | composite F_{2^{34}} + null F_{2^{37}} |
| RUN-BINSTD-bfa01e | 4 | completed_valid | null n=37 f=2 |
| RUN-BINSTD-0f3a44 | 4 | completed_valid | contrast n=31 f=7 |
| RUN-BINSTD-068959 | 2 | failed_infrastructure | instrument_unavailable |
| RUN-BINSTD-c302de | 3 | failed_infrastructure | skip-with-stage2 |

## Observations (no hypothesis status change)

- Corrected ladder errors match frozen table exactly under disclosed rounding.
- `ord_n(2)/f` census matches frozen cells; `ord_17(4)=4`, 32 subspaces, stated dims.
- `#E(F_{2^{34}})=17180121128` (A=B=1? A=0,B=1), `l=65587` probable prime, verified.
- `#E(F_{2^{37}})=137439487532` (A=0,B=1), `l=230603167` probable prime, verified.
- f(n=37)=2; f(n=31)=7; formula↔cyclotomic-sum agreement.
- WDSat unavailable — optional conflict-ratio arm not measured; modeled prior not recorded as measured.
