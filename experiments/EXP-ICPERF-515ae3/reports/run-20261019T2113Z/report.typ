#set page(paper: "a4", margin: 14mm)
#set text(size: 8.2pt)
= EXP-ICPERF-515ae3 execution report
This report describes recorded execution outputs only. It makes no scientific verdict, hypothesis transition, factor-base ranking, or end-to-end speedup claim.

*Goal:* `GOAL-ICPERF-e6b6a4`. *Hypothesis:* `H-ICPERF-05021b`. *Run:* `RUN-ICPERF-eb0d88`, trial `prime63-m2-three-arm-diagnostic`. *Frozen plan SHA-256:* `08f32f02a191dfd16f5342540716a327da73f5091528bac07cf5ee77cdb7cbc9`. *Code commit at launch:* `4b197051008fa9abd87ad29c259e553252d196e0`; dirty state was not recorded.

== Recorded execution
One trial launched; zero trials passed the supervisor's required-output check. Supervisor status: `invalid_output`; selector state: `needs_reconciliation`. The required `manifest.yaml` and `raw-result.json` were absent. The child exited 0 after writing the diagnostic receipt and raw archive. The independent checker exited 0 and reported `integrity_pass`, with three positive cells censored and zero verified. This checker result does not override the missing-artifact status.

The injected monitor-null control recorded the specified `infrastructure_monitor_error` with `unreadable_live_root`. All three positive cells were attempted and reached the frozen 600-second cap. Each was recorded `timeout_censored`; none emitted a response or full-point certificate. The last solver phase was Gröbner computation for `coset-m2`, root enumeration for `random-m2` and `small_x-m2`.

#table(
  columns: (1.25fr, 1.45fr, 1fr, 1fr),
  inset: 5pt,
  [*Cell*], [*Stop*], [*Wall (s)*], [*Peak RSS (GiB)*],
  [monitor-null], [expected monitor fault], [0.004162], [missing],
  [coset-m2], [timeout censored], [600.148084], [4.000534],
  [random-m2], [timeout censored], [600.072356], [0.350159],
  [small_x-m2], [timeout censored], [600.058805], [0.226028],
)

Wall and peak process-tree RSS bytes are measured fields in `../../runs/RUN-ICPERF-eb0d88/diagnostic/receipt.json`. GiB is derived as sampled peak bytes divided by 2^30, rounded to six decimals. One execution per arm; no uncertainty estimate was recorded. CPU time was not recorded. Overall supervisor wall, derived from its start and finish, was 1803.422275 seconds including launcher and checker overhead. Resource caps were 8 GiB RSS and scratch, and model cap 64.

#image("graph.svg", width: 83%)

The graph shows sampled resource peaks from this run. Its source is `draw.py`. All three positive calls were censored and each arm had a separate planted target, so this is no runtime comparison. Matched rho, Bernstein–Lange, natural relation yield, useful rank, linear algebra, target DLP, setup amortization, and complete IC time were not measured; their gaps are unavailable.

== Inputs and custody
The archived prime-field instance has `p = 9223372021248595841`, subgroup order `r = 9223372018953067627`, base size 475 per arm and arity `m = 2`. Inputs were frozen by three request hashes: coset `9a172c65375c2d2dc2d73f6232fa52fa281afade4fcb76e00fbbbf32f35ecb91`; random `04e7668f12afb5769ce9f6c8b2e25eb052854c28a846e5e92ab4d19c39291c01`; small-x `88258142099602ebfe156af11f9843e25411b49b6db5675950c4192de27347ee`. No in-run random seed field was recorded.

Supervisor command: `python3 tools/experiment_execution.py run --plan experiments/EXP-ICPERF-515ae3/trial-plan.json --owner executor-prime63-m2-science --epoch 1`. The exact child and checker commands are in `../../runs/RUN-ICPERF-eb0d88/launch.json`. Platform: Darwin; Python 3.13.1; host name not recorded. Start: `2026-10-19T21:13:44.520872+00:00`; finish: `2026-10-19T21:43:47.943147+00:00`.

Raw run commit: `1f857554d6`. Failed lane release commit: `10b962aed4`. The run directory preserves execution and diagnostic receipts, phase traces, empty raw streams, request objects, checker output and raw archive. The two required output files are absent exactly as recorded. No canonical scientific graph changed because this session produced no reviewed finding. The detailed source is `report.md`.
