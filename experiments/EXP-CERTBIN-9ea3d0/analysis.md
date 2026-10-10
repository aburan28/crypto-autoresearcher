# Analysis: EXP-CERTBIN-9ea3d0 (H-CERTBIN-d140ae)

Review plan: `experiments/EXP-CERTBIN-9ea3d0/review/review-plan.yaml`
(`REVIEW-CERTBIN-9ea3d0-20261003`), written before this analysis.
Producer: TASK-20261003-81ebdd. Run tip:
`3c329c257aa489898b6d95c220c29b1c162e6dda`
(`cursor/run-certbin-9ea3d0-stages012-ed0c`, PR #1713).
Approval: DEC-20261003-972240. Decision target: **scoped weaken** of
uniform HEUR-1 at this n=19 cell (O-MIXED; Z/rZ and kernel OK), not
`reject_scoped` (unreplicated empirical_only) and not support.
HEUR-1 is **not** declared supported. n=17 is **not** pooled. No
ECDLP / exponent / KN-FIND. No Bedrock/AUXIN. No re-run this tick.

## Observation

**Validity (J1).** Three run directories under `runs/`:
`RUN-CERTBIN-a8c7f1` (Stage 0), `RUN-CERTBIN-a008c1` (Stage 1),
`RUN-CERTBIN-6319c2` (Stage 2). Each has `manifest.yaml` with
`validity: valid`, `raw-result.json` with `ok: true`, `command.txt`,
`stdout.log` / `stderr.log`, and `check.stdout.log` /
independent re-run of `check.py` = `{"check": "pass", ...}` exit 0.
Within `maximum_runs: 3`. Required artifacts present:
`stage0/preregistered-predictions.json`, `stage0/cell-n19.json`,
`stage1/n19-census.json`, `stage2/n17-nearby.json`, `RESULTS.md`.
Amazon Bedrock not used. No discrete-log certificate (collision-count
measurement; certificate kind none). Producer claims no ECDLP solve
and no exponent.

**Freeze hash (J1/J2).** Independent SHA-256 of
`stage0/preregistered-predictions.json` =
`88dc63059d55c0ba75f8d8930b34688fa33a8777c07bb68a0013d9c3df7956b0`,
matching the Stage-0 file, the RUN-CERTBIN-a8c7f1 copy, and RESULTS.md.
Frozen: C_eff=1145, birthday_expectation=5.004393572394611,
r=130873, r^{0.05}=1.8023639941375367. Recomputed
C(C−1)/(2r) and r^{0.05} agree with the freeze.

**Stage 0 (J2).** Order 523492; r=130873 prime; kernel_G and
kernel_3G true on G and 3G.

**Stage 1 (J2/J3) — blind ratio recompute from census rows.**

| seed_name | k | informative | ratio (recomp) | in [1/2,2] | ≥ r^{0.05} | heaviest_fiber |
| --- | --- | --- | --- | --- | --- | --- |
| primary | 2 | 20 | 3.996… | no | yes | 3 |
| primary | 3 | 22 | 4.396… | no | yes | 3 |
| holdout | 2 | 18 | 3.597… | no | yes | 3 |
| holdout | 3 | 7 | 1.399… | **yes** | no | 2 |

Z/rZ control: colliding_pairs=8, ratio=1.598… ∈ [1/2,2],
heaviest_fiber=2. `zr_ok=true`, `tail_ok=true`, `in_band=false`,
`exponent_read=false`, label **O-MIXED**.

**Stage 2 (J4).** n=17: order=130972, r_is_prime=False, kernel_ok=True,
`pooled_with_n19=false`. Nearby rows disclosed only; **not** a
replicate of n=19 and **not** used in the n=19 label.

**Procedure deviation (PD-2).** Stage 1/2 `run.py` re-invokes Stage 0
and rewrites `stage0/cell-n19.json` wall_seconds; executor restored
the freeze copy; predictions hash unchanged (re-verified). Not
treated as freeze invalidation.

## Comparison

Against H-CERTBIN-d140ae / HEUR-1 and frozen labels:

- Geometric kernel + order: **hold** → not O-ARTIFACT from kernel/order.
- Z/rZ control in [1/2,2] with tail pass: **hold** → not O-ARTIFACT
  from the instrument control.
- O-BIRTHDAY (every n=19 ratio in [1/2,2]): **fails** (3 of 4 ratios
  outside the band).
- O-DELTA-N19 (every n=19 ratio ≥ r^{0.05}): **fails** (holdout k=3
  ratio 1.399 < 1.802).
- O-MIXED: **matches** producer and recomputation.
- Full contract falsification (Z/rZ in band AND every cell ≥ r^{0.05}
  AND heaviest fiber ≤4): **not met** (mixed, not uniform exponent
  reading).
- n=17 pooling: **absent** (`pooled_with_n19=false`).

## Inference

The Stages 0–2 package is **valid**. Instrument controls pass, so
O-MIXED is a scientific observation about the curve cell, not an
automatic O-ARTIFACT. Uniform HEUR-1 — that **every** frozen n=19
(seed, k) informative/birthday ratio lies in [1/2, 2] — does **not**
hold on this unreplicated package (ratios ≈ 3.996, 4.396, 3.597,
1.399). The package also does **not** meet the preregistered full
falsification branch (all ratios ≥ r^{0.05}). Official reading:
**scoped weaken** of uniform HEUR-1 at this toy n=19 E_0 cell, with
`proof_status: empirical_only`, strength **preliminary**. HEUR-1 is
**not** declared supported. Decision is **not** `reject_scoped`
(unreplicated empirical_only; AGENTS.md / claims-and-verification:
weaken + replication). n=17 remains nearby/unpooled. No ECDLP,
exponent, or KN-FIND. Hypothesis and experiment
`approved → analyzed` (weakened reading). Successor: replicate the
n=19 census under a new seed set / locked protocol before any
stronger adverse call.

## Limitation

- First unreplicated observation; Coordinator-direct review only
  (PD-1) — strength capped at preliminary.
- Toy n=19, r=130873, C_eff=1145, expected collisions ≈5 only.
  Transfer of δ to m=83 / m=131 / ECC2K-130 is **not** claimed.
- Birthday theorem cited as recalled (not opened) in the hypothesis;
  this review does not convert that citation.
- Stage-0 wall_seconds rewrite (PD-2) is infra, not math evidence.
- n=17 composite odd order is disclosed; it is not a HEUR-1
  falsifier at n=19.
- No independent validator/red-team; no counterexample certificate
  beyond empirical ratios.
- No break; no exponent; no KN-FIND; no re-run this tick.
