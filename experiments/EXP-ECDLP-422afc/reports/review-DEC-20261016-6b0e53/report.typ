#set page(paper: "a4", margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.")

= Evidence review: EXP-ECDLP-422afc (`DEC-20261016-6b0e53`)

*Decision:* `refine`. *Evidence:* `EV-ECDLP-9d41e7`: direction contradicts (the literal hypothesis statement only), strength preliminary, claim tier toy, proof status derivation. *Run:* `RUN-ECDLP-06bb83`, in the working tree and unpublished; its manifest is not schema-complete, so it is not cited as evidence. *Executor return:* `TASK-20261016-c8a7f2`. *Hypothesis:* `H-ECDLP-a1fc69` (no status transition). *Idea, question, goal:* `IDEA-20261009-f24f8a`, `RQ-ECDLP-002`, `GOAL-ECDLP-001`. *Approval:* `DEC-20261012-a0ba67`.

*Exact scoped claim.* On `y^2 = x^3 + x + 1` at p = 101, 211 and 307, with m = 2 and the factor base of x below floor(sqrt p) with square right-hand side, at most |F|(|F|-1) values of x in F#sub[p] decompose under Semaev S3. The fraction over F#sub[p] is therefore at most 0.198, 0.142 and 0.235. The frozen hypothesis (within 0.25 of 1/2) is false at all three primes by derivation, independent of the run. This tests the heuristic p^(m beta - 1)/m! of `IDEA-20261009-f24f8a` in neither direction, because the hypothesis uses a different denominator and reads an expected count as a probability. Nothing here applies to larger p, to m of 3 or more, to SAT or Groebner solvers, or to any deployed curve.

Earlier run reports: none exist (`experiments/EXP-ECDLP-422afc/reports/run-*/` is absent at review time; `TASK-20261016-c8a7f2` owes one).

= Observation

#figure(
  image("fraction.svg", width: 100%),
  caption: [Decomposing fraction c(p)/p (dimensionless) at the three frozen primes. Each point is one deterministic pass (n = 1) with an exact count, so there is no spread. Filled circles: measured values from `RUN-ECDLP-06bb83` raw-result.json (working tree, unpublished). Red bars: the exact derived ceiling |F|(|F|-1)/p (`EV-ECDLP-9d41e7` D1-D3). Open diamonds: a post-hoc Poisson model that was NOT preregistered. Green: the preregistered band [0.25, 0.75] around 1/2. Data: `fraction-data.json`.],
)

#table(
  columns: 7,
  [p], [|F|], [pairs], [c(p)], [fraction], [`abs_error`], [ceiling |F|(|F|-1)/p],
  [101], [5], [10], [17], [0.1683], [0.3317], [0.1980],
  [211], [6], [15], [28], [0.1327], [0.3673], [0.1422],
  [307], [9], [36], [61], [0.1987], [0.3013], [0.2345],
)

`planted_s3_zero` is true at every prime. The reviewer re-derived it by hand at p = 101: x(P1+P2) = 92 and S3(0, 3, 92) = 808 = 8 x 101.

Validity: run count 1 of 1; no seeds (deterministic by contract); raw and manifest agree; frozen inputs match; pairs = C(|F|, 2) in every cell. The factor bases were re-derived by hand at all three primes: `{0,3,5,6,8}`, `{0,2,4,8,12,13}` and `{0,2,4,6,7,10,11,13,16}`. Defects: V-1, the manifest lacks `run.id/status/code/environment/inputs/timing/result`. V-2, there is no command, environment, log or execution receipt. V-3, the run is uncommitted. V-4, the source-hash binding was not re-checked. V-5, a stray `__pycache__` file. V-6, the checker imports the driver it checks. V-7, the band was unreachable before execution.

= Comparison

- Preregistered criteria, taking the values at face value: every `abs_error` is above 0.25 and the planted identity holds, so the falsification criterion fires. By D3 this was fixed by the factor base before execution.
- Derived ceiling: c(p) is at most |F|(|F|-1) at every prime (17 of 20, 28 of 30, 61 of 72).
- Post-hoc Poisson model, with \#E taken as about p: 0.164, 0.124 and 0.187 against 0.168, 0.133 and 0.199 recorded. This is not evidence. It only motivates the successor's prediction.
- Index-calculus baseline and matched rho: not applicable. No ECDLP cost is measured and no improvement over the IC baseline is claimed. The distance remaining to the matched rho is not measured by this experiment.

= Inference

S3 is quadratic in x3 with leading coefficient (x1-x2)^2, which is nonzero, so each unordered pair contributes at most two targets (D1). With |F| about sqrt(p)/2 (D4), the fraction over all of F#sub[p] is capped near 1/4 at every prime. The value 1/2 is the expected number of decompositions per *point* of E(F#sub[p]) (D5). Only about p/2 of the x in F#sub[p] are x-coordinates of points, and an expected count of 1/2 corresponds to a probability of about 1 - e^(-1/2) = 0.39 of at least one decomposition. The literal hypothesis is therefore settled false. The reproduction check of the idea's heuristic has not been performed. Decision: `refine`, not `reject_scoped`, because rejecting a mis-normalized statement would close nothing, the run is unpublished, and the derivation is not independently re-derived.

= Limitation

Toy tier: one curve, three primes of 7 to 9 bits, m = 2, beta = 1/2, enumeration only. D1-D3 are hand derivations not yet re-derived by an independent agent. D4 uses a recalled character-sum estimate, and D5 is heuristic. \#E(F#sub[p]) was not computed. The counts 17, 28 and 61 are confirmed only by a checker that reruns the same driver. The reviewing subagent had no shell, so ids were not run through `allocate_id.py --check`, `validate_ledger.py` was not run, and this PDF was rendered (if at all) by the session.

= Next actions

+ Session: run `allocate_id.py --check` on `EV-ECDLP-9d41e7`, `DEC-20261016-6b0e53` and `TASK-20261016-c8a7f2`; run `validate_ledger.py`; write `analysis.md` from `EV-ECDLP-9d41e7`; render and inspect this PDF.
+ Executor: `TASK-20261016-c8a7f2`: publish `RUN-ECDLP-06bb83` or name its provenance gaps, and write the run report. No new trial.
+ Coordinator ledger archive, run alone; then push and open a PR naming `EV-ECDLP-9d41e7`, `DEC-20261016-6b0e53` and `TASK-20261016-c8a7f2`; then checkpoint `GOAL-ECDLP-001`.
+ Goal next action: design a v2 stage-0 contract with a successor H. Targets are x-coordinates of points of E(F#sub[p]) with an exact denominator; the prediction accounts for saturation or uses a small beta; the |F|(|F|-1) ceiling is preregistered and the band is checked as reachable; at least one prime above 307; a checker independent of `run.py`; a schema-complete manifest.

Canonical graphs checked and left unchanged: no graph source (svg, dot, typ or mmd) exists at the top level of `knowledge/frontiers/ecdlp/`. A refine decision on preliminary evidence changes no supported content.
