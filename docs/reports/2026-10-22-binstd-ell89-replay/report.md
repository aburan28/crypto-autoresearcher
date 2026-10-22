# Source-pinned replay of the BINSTD ell89 toy panels

2026-10-22 · EXP-BINSTD-8bdf86 · H-BINSTD-5a212b · GOAL-ECDLP2M-001

This is a validation replay of the already recorded Stage-1 packages, not a new experiment or evidence decision. The frozen run records and earlier reviews remain unchanged. The output is bound by [receipt.json](receipt.json); [replay.py](replay.py) verifies both historical source commits and reruns the same toy computation in temporary directories. The quantitative view is [yield-ratios.svg](yield-ratios.svg).

Source records: [ell89 run environment](../../../experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-43abd4/environment.json), [ell89 yield matrix](../../../experiments/EXP-BINSTD-8bdf86/stage1-ell89/yield-matrix.json), [ell89r1 run environment](../../../experiments/EXP-BINSTD-8bdf86/runs/RUN-BINSTD-a2a24c/environment.json), and [ell89r1 yield matrix](../../../experiments/EXP-BINSTD-8bdf86/stage1-ell89r1/yield-matrix.json).

## Observation

The archived `command.txt` files require `--ells`, `--artifact-tag`, and, for the second panel, `--seed`. The current `implementation/run.py` on this branch does not accept those flags. The `environment.json` files identify the historical runnable commits; all three recorded source SHA-256 values, the dated specification hash, and the three Stage-0 freeze artifact hashes match Git history and committed artifacts. The replay extracted those pinned sources, copied the frozen Stage-0 artifacts, and ran Stage 1 only. It did not write into any frozen run directory.

| Panel / Stage-1 run | Pinned source commit | Seed | ell | Tau hits / 40 | Open hits / 40 | Derived ratio | Frozen band |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ell89 / `RUN-BINSTD-43abd4` | `93d9ac619d82ec8bb3856837526386bdac84cc8e` | 9049049433885666 | 8 | 16 | 40 | 0.4 | 1.25 |
| ell89 / `RUN-BINSTD-43abd4` | same | same | 9 | 40 | 40 | 1.0 | 1.25 |
| ell89r1 / `RUN-BINSTD-a2a24c` | `9932b86fc0c61b215429725b66042fef1d99c50c` | 8999122336642658 | 8 | 20 | 40 | 0.5 | 1.25 |
| ell89r1 / `RUN-BINSTD-a2a24c` | same | same | 9 | 40 | 40 | 1.0 | 1.25 |

For both panels, the newly generated yield matrix, admissible-dimension file, and results note match the archived files **byte for byte**. The `raw-result.json` payloads match after excluding their new `recorded_at` timestamps. The recorded ratio for each cell is `hits_tau / hits_open`; all four are below the pre-registered 1.25 threshold. The elapsed local replay times were 355.8 and 315.6 seconds on Python 3.9.25; these timings are operational observations, not benchmark measurements. CPU time was not recorded. No uncertainty interval was recorded for the 40-target hit rates.

A second end-to-end invocation through the committed `replay.py --run` path completed both panels. Running the final verifier over those new temporary outputs reproduced the committed `receipt.json` byte for byte.

## Code controls

The replay script checks the pinned polynomial `t^17 + t^3 + 1` by an independent Rabin irreducibility calculation over F2. It also multiplies the degree-1 and two degree-8 irreducible factors `3`, `313`, and `471` to recover `x^17-1`, then obtains factor-degree subset sums `{0,1,8,9,16,17}`. This checks the recorded polynomial arithmetic; connecting those sums to every Frobenius-invariant subspace still uses the normal-basis module argument and has no Lean proof here. On each pinned runner, its pair-membership shortcut agreed with direct enumeration of all `8^3` ordered triples for 12 constructed hits and 12 sampled misses on the same toy curve. The previous 12 random targets were all misses, so they did not test the shortcut's true branch; the strengthened control now requires both outcomes. These are bounded checks. The archived `implementation/check.py` checks status and outcome labels only; it does not recompute the hit counts or inspect the source pins. The full isolated replay supplies that missing deterministic-output check.

The verifier also passed under `python3 -O`, and a one-count mutation in a copied replay matrix made it exit with an output-hash mismatch before writing a receipt. Its checks therefore remain active when Python assertions are disabled.

## Interpretation and limits

The two seed-specific archived outputs are reproducible from their recorded code and freeze artifacts. This supports the narrow record that the **toy** tau-closed factor-base yield did not reach the stated 1.25 band at `n=17`, `ell` 8 or 9, under the frozen exhaustive `m=3` pin. The open arm hit all 40 targets in every cell. At that observed open rate, any tau arm has success rate at most 1 and therefore ratio at most 1; the 1.25 band was unreachable. That ceiling limits how much these cells can say about tau geometry outside the exact tested protocol. It does not provide an independent implementation of the elliptic-curve group law, independently reconstruct every sampled target, prove the code correct in Lean, or change the existing evidence decision. The two runs use distinct pseudorandom seeds, while the tau-closed subspace constructor is deterministic. No ECDLP break, exponent, `n>=131` transfer, runtime advantage, or Pollard-rho comparison follows.

The canonical performance dashboard and claim registry were checked for impact: this is a negative toy yield result and adds no speedup or attack-cost claim, so no leaderboard row or performance curve changes. The [graph source](render.py) draws only the four archived hit ratios; its threshold and run IDs are labeled. Publication of the separate Pages reader remains under the owner-controlled disabled workflow.

## Reproduction

From the repository root, `python3 docs/reports/2026-10-22-binstd-ell89-replay/replay.py --run --receipt /tmp/binstd-replay-receipt.json` creates fresh temporary directories, runs both panels, and fails if any pinned source, freeze artifact, output file, or non-timestamp raw result differs. Expect roughly 12 minutes on the host used here. `python3 docs/reports/2026-10-22-binstd-ell89-replay/render.py` regenerates the SVG from the committed receipt. In this report directory, `rsvg-convert -f pdf -o yield-ratios.pdf yield-ratios.svg` and `tectonic report.tex` regenerate the [PDF](report.pdf) with the graph embedded.
