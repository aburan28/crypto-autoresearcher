#set page(paper: "us-letter", margin: 0.68in)
#set text(font: "Libertinus Serif", size: 9.2pt)
#set par(leading: 0.58em, justify: true)
#show heading.where(level: 1): set text(size: 15pt, weight: "bold")
#show heading.where(level: 2): set text(size: 11pt, weight: "bold")

= EXP-ECDLP-6dacdb execution report

_Observation-only record for_ `RUN-ECDLP-36b2a5` _and_ `RUN-ECDLP-994eb9`.

This report records the completed process, checker outputs, and measured quantities; it does not assign evidence strength, change the hypothesis or experiment state, or make a scientific verdict.

#image("graph.svg", width: 100%)

== Scope and custody

- Goal: `GOAL-ECDLP-001`; question: `RQ-ECDLP-002`; hypothesis: `H-ECDLP-bd1572`; experiment: `EXP-ECDLP-6dacdb`.
- Corrected frozen plan: `experiments/EXP-ECDLP-6dacdb/trial-plan-v2.json`; SHA-256: `798321ec3932d92a09eede9152fe198d72d2aeab6e7e9d6502fafc3790fa0567`.
- Additive correction: `CORR-20261011-2c3e1f`; queue `BATCH-62ac7b`; executor `TASK-20261011-672eaf`; owner `executor-ecdlp-6dacdb-v2`, epoch 1.
- Receipt dispatch-plan SHA-256: `b7940519fd5c0c4068dda9f7f3dbbe030e5598b53ac9ae0c073a7f78c6d4c614`.
- Remote execution commit: `2f5957be13584d31dd0b2ace1815a1d3aec7e6fa`; platform Linux; Python 3.12.11. Specification SHA-256: `2649c4cabb8f97626f9e6406abf80ae51d26fe7b0fa4a882b7d3ac25c751a185`.
- The sealed environments contain the source hashes for `check.py`, `primeset.py`, and `run.py`; complete hashes remain in both run directories. The local archival worktree had unrelated untracked artifacts during import. Hostname, CPU time, and runtime-lock hash were not recorded and are missing rather than inferred.
- Run-record commit `ea813bd52a` was pushed before this report was created.

== Trials and process results

Two trials were requested and two completed. Both receipts have `status: output_validated`, `returncode: 0`, `check_returncode: 0`, and no recorded scientific conclusion. The independent checker returned zero errors for each sealed run.

*Part A — embedding-degree census.* `RUN-ECDLP-36b2a5` ran from `2026-10-11T20:35:23.712268Z` to `2026-10-11T20:35:59.065855Z`; recorded wall time was `34.765450954437256 s`. The command was:

#raw(block: true, "python3 experiments/EXP-ECDLP-6dacdb/implementation/run.py --part A --seeds 1 2 3 --curves 64 --out <run_dir>")

The raw result has 72 cells and records 2,300 special-arm and 2,304 random-arm non-anomalous samples. The checker log reports 12 curve rows recounted and zero errors.

*Part B — deployed-parameter order search and threshold table.* `RUN-ECDLP-994eb9` ran from `2026-10-11T20:35:59.150197Z` to `2026-10-11T20:36:00.910884Z`; recorded wall time was `1.7606866359710693 s`. The command was:

#raw(block: true, "python3 experiments/EXP-ECDLP-6dacdb/implementation/run.py --part B --out <run_dir>")

The six declared public parameter sets were processed with order search bound `10^6`; the checker log reports zero curve-row errors.

== Recorded observations

The graph plots values directly from the raw results. `plot_data.json` is the extracted plotting data and `plot.py` is the SVG renderer.

*Part A.* The recorded `k <= 20` fractions were 0.1591304348 (special, `n=2300`) and 0.1328125 (random, `n=2304`). The recorded difference was 0.0263179348 with standard error 0.0104002785. Mean `log2(t)` was 1.2486514049 and 1.2667237009, with difference -0.0180722961 and recorded permutation p-value 0.6835316468.

The histogram counts in bins `1`, `2`, `3-4`, `5-16`, and `>16` were [851, 725, 288, 309, 127] and [862, 679, 304, 330, 129]. The recorded chi-square was 2.7124839037 with permutation p-value 0.6116941529. The three smallest recorded `(k,l)` pairs were `(1,5)`, `(1,7)`, `(1,11)` for random and `(1,5)`, `(1,7)`, `(1,29)` for special.

The nearby supersingular control list has 43 entries; all 43 recorded `k` values are 2. The Part A checker returned zero errors. These are control and sample observations for the declared scope, not a transition of the hypothesis.

*Part B.* All six rows recorded the first searched embedding degree as `> 1,000,000`; this is a recorded lower bound, not an exact order value.

#table(
  columns: (2.1fr, 0.8fr, 0.8fr, 1fr, 1.25fr),
  table.header([*Parameter set*], [*GNFS*], [*exTNFS*], [*SNFS/STNFS*], [*$log_2$ rho*]),
  [Curve25519], [9], [11], [16], [125.8254],
  [P-256], [9], [12], [17], [127.8254],
  [secp256k1], [9], [12], [17], [127.8254],
  [P-521], [27], [34], [48], [260.3254],
  [Ed448], [21], [27], [37], [222.8254],
  [brainpoolP256r1], [9], [12], [17], [127.5300],
)

The source table labels the constants recalled and optimistic and drops the `o(1)` term. All six rows record prime checks and Hasse checks true. Five rows record a bound-point order check true; Ed448 is `null` because no base point was bound in this invocation and its order is marked recalled-only.

As derived arithmetic only, the largest displayed threshold is 48; combined with the recorded lower bound this gives a lower-bound difference greater than 999,952 in `k` units. This is not an additional measurement.

== Missing data and boundary

CPU time, machine hostname, and runtime-lock hash were not recorded. No extra samples, curves, constants, or secret-dependent computation were run. The graph and report cover only these two completed trials and their declared scopes. Raw results, manifests, receipts, commands, environments, checker logs, and the Part B table remain in the two run directories. Scientific interpretation and any official state transition remain for independent review/archive tasks.
