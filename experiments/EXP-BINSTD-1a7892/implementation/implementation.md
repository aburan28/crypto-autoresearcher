# EXP-BINSTD-1a7892 implementation notes

Task: `TASK-20261001-d6b2b5`. Experiment: `EXP-BINSTD-1a7892`.
Authority: `DEC-20261001-bcc056`. Stages 0–2 only.

## Layout

| path | role |
| --- | --- |
| `run_stage0.py` | Arm B arithmetic + dual rho + OPEN cell + corpus + ECC2K-130 |
| `run_stage1.py` | Gorla–Massierer PDF retrieval/extraction + H2 calibration |
| `run_stage2.py` | Toy T_k cost-vs-g, null/non-T_k controls, certificates |
| `stage2_tk.py` | Curve/FB/certificate + truncated Macaulay GE instrument |
| `gf2n.py` / `curve.py` | Adapted from `EXP-CERTBIN-e94b27/impl/` (schoolbook) |
| `common.py` | Run-package writer (`manifest.yaml`, logs, `raw-result.json`) |

## Protocol deviations

1. **Stage 2 cost proxy is a truncated dense F₂ Macaulay GE**, not a full
   Gröbner engine. Fixed instrument degree `D≤3` with equation degree clipped
   to `≤2` so cross-`g` cost is driven by `n_variables=2g`. Full
   Gorla–Massierer `total_degree=(n-1)2^{n-2}` is recorded as modeled shape
   only. Bias (disclosed in spec optimistic assumptions): **optimistic for
   the attack**.
2. **Forward certificates** verify known `g`-sums of factor-base points on
   `E(F_{2^4})` by independent curve addition. No solver verdict is trusted
   alone. Ambient `E(F_{2^{d k'}})` group walks are **not** performed
   (deployed `k` walks forbidden; toys use base-field FB arithmetic).
3. **non-T_k control** uses one seed per `g` (not five) to stay inside
   `maximum_runs: 40` while still reporting the arity-matched GE curve.
4. **Stage 1 g=4 calibration vs H2 `4!`** is marked incomplete because the
   paper’s implemented `n=5` pipeline uses Joux–Vitse arity-3 + hybrid
   search, not full arity-4 Semaev solves. Extracted GB wall seconds are
   still recorded as `extracted`.

## Non-claims

- No `DEFINED` deployed attack cost.
- No break claim; dual-rho canonical margins ~0.5 bit larger than reused
  strengthen the discredited “apparent break”, never license it.
- Extrapolation to `g=22` is labeled `modeled` with stated distance.
- Timeouts/OOM would be `failed_infrastructure` / `instrument_ceiling`,
  never negative math evidence.

## How to reproduce

```sh
python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage0.py
python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage1.py
# Stage 2 requires stage0/ and stage1/ artifacts:
python3 -I experiments/EXP-BINSTD-1a7892/implementation/run_stage2.py
```
