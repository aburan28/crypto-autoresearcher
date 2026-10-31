#set page(paper:"a4",margin:(x:17mm,y:16mm),numbering:"1")
#set text(font:"DejaVu Sans",size:9.2pt)
#set par(leading:0.55em)
#set heading(numbering:none)
= Classical ECDLP run observations
*EXP-ECDLP-080f41 / RUN-ECDLP-939237* \
GOAL-ECDLP-e70832 · H-ECDLP-6674c9 · TASK-20261029-cbafca

Observations only; no scientific status transition. One actual candidate VM. The original native invalid_output/check1/publishedfalse is preserved. A separate complete readonlyJSONview passed independent representation/custody validation before this host analysis.

#table(columns:(1.25fr,1.75fr),inset:4pt,align:left,
[*Recorded quantity*],[*Actual value*],
["Native start / finish UTC"],["2026-10-29T22:58:42.290270+00:00 / 2026-10-29T23:09:08.554907+00:00"],
["Native driver / checker / status"],["0 / 1 / invalid_output"],
["VM creates / engine executions / engine RC"],["1 / 1 / 0"],
["Collection / quiescence / ACK"],["True / True / True"],
["Native dirty field"],["unknown"],
["Host RC / source status / verifier"],["0 / complete / checked"],
["Host observed row counts"],["{\"cells\": 73728, \"intents\": 36864, \"setups\": 216, \"singles\": 345600, \"traces\": 36864}"],
)

#image("observations.svg",width:100%)

Every retained source-analysis curve/cell row is plotted. Six cells share each confirmation trace; the two evaluator aggregates share one physical VM. Fractions are recorded successes divided by recorded attempts. Missing values are not filled. No new interval, p-value or fit.
#pagebreak()
= Recorded outcomes, references and controls
Labelled sums over the same24confirmationcurves; six shared views are dependent. Uniform is one recorded matched-M conditional reference per cell, with M-determination still candidate work. No significance or advantage inference.

#table(columns:(0.7fr,1fr,1fr,1fr),inset:3pt,align:left,[*Cell*],[*Candidate events / attempts*],[*Uniform events / rows*],[*Recovered curve-target pairs*],[t0.e0],[4 / 12288],[3 / 12288],[4],[t0.e2],[4 / 12288],[0 / 12288],[4],[t1.e0],[42 / 12288],[33 / 12288],[38],[t1.e2],[43 / 12288],[35 / 12288],[39],[t2.e0],[214 / 12288],[184 / 12288],[183],[t2.e2],[227 / 12288],[149 / 12288],[196],)

Calibration recorded summary: #text("{\"all_complete_1800\": true, \"arm_records\": 192, \"by_stage\": {\"discovery\": {\"arm_records\": 96, \"retained_draws\": 172800, \"signed_numerator_range\": [-168, 152], \"undefined_draws\": 76}, \"validation\": {\"arm_records\": 96, \"retained_draws\": 172800, \"signed_numerator_range\": [-208, 171], \"undefined_draws\": 51}}, \"n_range\": [1800, 1800], \"retained_draws\": 345600, \"scope\": \"Labelled sums/ranges of192 retained arm records; not independent curve-population samples or a confidence interval.\", \"signed_numerator_range\": [-208, 171], \"undefined_draws\": 127}"). Exact signed numerators, actual retained n, undefined counts and complete1800flags are in observations.json. *Frozen1/512calibrationresolution is NOTQUALIFIED.* Undefined draws remain in the denominator; score grid is not uncertainty.

BSGS source summary: #text("{\"retained_target_records\": 1536, \"scope\": \"Source-generated independent BSGS entries; full cold/warm setup/online vectors remain in references.json. No timing claim.\", \"status_counts\": {\"success\": 1536}}")

Full original/incremental metrics, all six retained cells, error/erasure histograms, source null/support/duplicates/ties, nonzero matched-M uniform streams and BSGS cold/warm/setup/online vectors remain in the unchanged source outputs linked by path/hash. M0 has zero reference guesses, while common/setup/M-determination work remains paid.

Host errors: #text("[]")

Unified export validation: #text("{\"findings\": [], \"protocol_qualified\": true, \"schema_compliant\": true}")

The protocol records absent fresh A/A, positive-arm and inferential-negative controls with descriptive-scope excuses. Prior source fixtures, bridge corruption controls and host references do not become fresh detector/noise-floor outcomes. Curve is the population unit. Source zero-event bounds keep their stated fixed-curve assumption; nonzero fractions are descriptive. No population interval, exchangeable-null p-value or exponent fit is added.

Native clocks/isolation and independent native worker counter replay remain unqualified. NativeRSS, allocations, I/O and integer internals are unmetered. Worker/host/setup/common/list components remain separate. This report adds no attack-cost, speedup or scientific verdict.
#pagebreak()
= Provenance and preservation
Native source authority: #text("6ce9937047cb26279f61a128ecc45751dc135a78")

Derived fullnativeJSONmanifest SHA256: #text("2c60bea2625d1287a1d827afc496b177e0b17a24bd55f6518b2bd16546c2e755")

View provenance SHA256: #text("0e59dd89e53c7012745ba203be4255d09496cdb7c5c5e556d92ca9342ab66684")

Independent TASK-20261029-3b5feb checked five representation/custody joints, ten positive conditions and 48 refused mutants. Unchanged full C4 check passed. All51originalnative bytes/modes remain exact; original failure and later host analysis stay distinct.

Native report path: #text("experiments/EXP-ECDLP-080f41/reports/run-20261029T2258Z")

Unchanged source postrun path: #text("experiments/EXP-ECDLP-080f41/postrun-from-view-346631")

All48 actual exposed model/base/(p,j) identities and original cohort/ledger hashes are retained in exposed-curves.json for future exclusion inputs; no sampling is performed. Complete report prose: report.md. Exact observations, native command/environment/status, final host command, source output paths/bytes/SHA256 and controls/excuses: observations.json. Editable graph: draw_observations.py plus observations.json; rendering observations.svg. Editable PDF source: report.typ. Exact prelaunch qualification and later Coordinator assessment are retained separately in postrun custody, with original timestamps; no retrospective prelaunch claim is created.

Public candidate nonce and any host seed stay in their source custody; the host seed is emitted only after the source authenticated full workload/seal/readback/quiescence/ACK gate. This report draws no entropy. Original source reports/export/checks remain unchanged. Experiment-root derivative paths/checks, if produced, are new records.

Source environment Python/platform and exact argv are retained in observations.json. Native dirty field remains unknown; earlier separate root point-in-time facts do not fill it. This producer report changes no canonical mathematical graph.

Sources/provenance: internal primary protocol/output/bridge contracts; task card; AGENTS and observation/literature rules; Executor/run/research-visuals; source postrun/analysis/renderer/reference. This administrative task performs no external novelty search, model probe, scientific sample or rerun.
