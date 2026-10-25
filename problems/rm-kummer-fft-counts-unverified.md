# RM Kummer FFT census lacks all-member exact validation

- **Status:** `open`
- **Kind:** implementation validation gap and execution provenance gap
- **Affected work:** 2026-10-08 RM Kummer survey item 7; `harness/endosweep/rmkummer.py`; [rounding guard audit](../docs/reports/2026-10-25-rm-fft-rounding-guard/REPORT.md); the broader [formal target semantic-fidelity gap](formal-target-semantic-fidelity-unreviewed.md)
- **Next action owner:** Coordinator to assign an independent exact-replay implementation and review
- **Last updated:** 2026-10-25

## Problem

The archived `1000 < p < 1600` survey's claim that every member's Jacobian order is exact remains unestablished: its all-`t` point counter uses floating point FFT output rounded to integers, and neither a bound on that computation's absolute error nor an independent exact replay of every member is archived. The inspected archive directory has no process receipt binding the source loaded during the original run. The survey reports 56,630 nonsingular RM members, 56,686 translation-control members and 1,891 split-control members; these totals must remain reported as archived computed results until the validation is complete.

## Evidence and uncertainty

- **Observed:** The frozen survey README states that an error is raised when an FFT output is more than `10^-3` from an integer, while the original source at main `af671797aac46cee67b8781ade98d331c4711f4e` additionally required a relative threshold. A synthetic `6000.003` output and nonfinite outputs bypassed that guard. The [2026-10-25 audit](../docs/reports/2026-10-25-rm-fft-rounding-guard/REPORT.md) repairs future code and records the regression. The named archive directory at `0b38ac1157f777cb4a77d35e53d7ed583c541eb4` contains a README with reproduction commands, `SHA256SUMS`, and RM/Q-curve JSON and Markdown outputs; it contains no process receipt or executed-source hash manifest. Other possible custody records were not exhaustively searched. The archive reports 12 of 12 PARI spot checks and small-prime brute-force tests; no actual historical wrong member has been identified.
- **Derived or proved:** A residual smaller than `10^-3` does not by itself prove a floating point result is within `1/2` of its true integer character sum; an independent error bound or exact computation is required. A local read-only check of pinned summary bytes and arithmetic found internally consistent totals, rates and histograms, but did not replay the members.
- **Suspected explanation:** No numerical error was observed in the archived counts. The gap is missing evidence, not an established incorrect result.
- **Missing capability:** A sealed per-member exact-count successor or a rigorous error bound for the frozen FFT implementation and parameter range, plus a receipt binding the executed source. Historical loaded-source custody may be irrecoverable; a fresh successor can establish a new result.
- **What this evidence does not establish:** It does not invalidate the reported hit counts, validate every archived count, or prove a performance advantage. The Lean golden-norm parity theorem concerns an algebraic norm and does not prove the survey frequencies or FFT output.

## What would unblock it

- [ ] Freeze the three survey arms, seed, prime range, nonsingularity rule, output schema and controls in a successor protocol before inspecting new exact results.
- [ ] Recompute `N1`, `N2`, `#J` and `#J_twist` with an exact integer method for every member of all three arms. Archive per-prime and per-member outputs with source/environment hashes, compare every available archived aggregate and the 12 PARI controls, and independently review discrepancies and summary reconstruction.
- [ ] Establish executed-source custody for the successor and pass independent code, numerical and claim-scope review. State separately whether any original-run custody gap remains.

These conditions would establish the successor's exact census within the frozen scope if the controls and review pass. They would not prove Kummer theta-model availability, a full ECDLP cost claim, or retroactive original-process custody.

## Next discriminating step

- **Action or proof obligation:** Implement one exact per-prime correlation prototype for a frozen survey prime and compare every `t` in its RM and translation arms with the rounded FFT output, retaining an exact integer certificate or direct sum.
- **Inputs and controls:** Use the frozen `D_5+t` arm, the fixed-seed random-quintic arm, the split-by-construction arm where applicable, and the existing small-prime brute-force/PARI controls. Pin the selected prime and protocol before execution; do not choose a prime after seeing discrepancies.
- **Execution limits and stop condition:** Start with one prime and an explicit memory/time watchdog under the existing research execution rules; no new survey or job is launched by this record. Stop on the first mismatch for triage or after all frozen `t` at that prime match.
- **Outcomes and next actions:** A mismatch requires source and arithmetic triage without altering frozen outputs. Agreement supports expanding to the full fixed range, but does not alone validate it. Infrastructure failure preserves the inconclusive status and the saved partial artifacts.
- **Recheck trigger:** A committed exact prototype, error-bound proof, full successor run receipt, or new custody evidence.

## Resolution and history

Unresolved. The 2026-10-25 future-code guard repair and spot tests do not meet the all-member exit conditions.
