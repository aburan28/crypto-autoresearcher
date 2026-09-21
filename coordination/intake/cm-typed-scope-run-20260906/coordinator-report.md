# EXP-ENDO-c6c7a7: scoped evidence review

Coordinator task: TASK-20260906-07f803. Evidence: EV-ENDO-545cfd. Decision: DEC-20260906-dec78a. Run: RUN-ENDO-c6c7a7-single. All cited research sources are internal records read directly for this review.

## Observation

The preserved deterministic seed-0 run has twelve cards, sixteen completions and twelve finite-predicate certificates. TASK-20260906-af0691 independently checked the committed receipt at 12d9e2b328bfc6c4310db04e7ec48736afc29e31 with a separately authored checker. Its final report passes both assigned joints; verification-results.json records 287 passing checks, zero failures and one metadata warning. The checker did not import or execute the producer program.

| Quantity | Producer | Independent check |
|---|---:|---:|
| Complete correct certificates | 12 | 12 |
| False certifications among four negative controls | 0 | 0 |
| Positive controls retained | 4 | 4 |
| Underdeclared cards retained with opposite completions | 4 | 4 |
| Unsupported strengthenings | 0 | 0 |

The producer recorded wall time 0.03686962299997276 s, CPU time 0.036504000000000036 s and peak RSS 31309824 bytes. These values and their resource-limit arithmetic were reconciled, not independently remeasured. Sources: experiments/EXP-ENDO-c6c7a7/runs/RUN-ENDO-c6c7a7-single/manifest.yaml, metrics.json, raw-result.json, certificates.json and resource-usage.json; coordination/intake/cm-typed-scope-run-20260906/TASK-20260906-af0691/validation-report.yaml and verification-results.json.

## Comparison

The numeric prediction in the frozen specification is met. V1-V4 retain nonzero scalar restrictions on their declared domains. N1-N4 reject non-invariance, zero restriction, affine-origin shift or an unsupported whole-space scalar claim while retaining weaker true properties. U1-U4 each preserve two completions with opposite target outcomes. The baseline is the declared scalar-2 map on additive F_5; there is no ECDLP solver comparison.

The frozen prediction text is “12/12; zero false certifications;4positive and4underdeclared controls retained.” The run's metrics text is “12/12; zero false certifications; 4 positive and 4 underdeclared retained.” The two added spaces and omitted final word controls are preserved as a metadata warning. They do not change the numerical result or warrant a scientific rerun.

## Inference

Decision: **synthesize**. Evidence strength: **preliminary**, claim tier **toy**. The exact finite diagnostic output agrees with independent checking. Evidence direction is neutral under this observation-only handoff; that label does not imply disagreement with the finite prediction. H-ENDO-b1e638 retains its existing proposed status, and all goal statuses are preserved. The finite review is source-aware verification of a single run, not independent clean-run replication or formal proof.

No knowledge entry is promoted: this fixed synthetic diagnostic has not established a general finding or an instrument validated across experiments. The run's result.certificate.kind=none is appropriate because no solve or relation is claimed; its separate finite witness objects were checked. No obstruction or adverse hypothesis decision is made.

## Limitation

The scope is precisely twelve frozen synthetic cards over F_2/F_5, dimensions one or two and at most twenty-five vectors per completion; integer field bit lengths are two and three. There is no elliptic-curve realization or transfer assumption, cryptographic-size test, distributional result, complexity estimate, or novelty conclusion.

The producer disclosed failed preflight followed by direct in-process deterministic evaluation, and a local-only producer claim before its snapshot. The validator accepted finite semantic validity and custody; original compliant dispatch, launch dirty-tree state, temporal oracle-read order and resource measurements cannot be reconstructed independently. This decision preserves those deviations and grants no prospective routing exception.

The producer's model_verified=true is a deterministic_block sentinel with null model, backend and provider, per the validator's check of orchestration/adapter/manifest.py. It does not certify a serving model. The validator's requested/configured native model was gpt-5.6-sol at xhigh; no probe receipt binds the exact serving session and its model_verified remains false.

Knowledge MCP retrieval was unavailable; direct primary internal records support this review. No claim of exhaustive retrieval or novelty is made.

The next action belongs to the Coordinator archive control plane: archive the three final validator files and these four synthesis files by exact path, verify parent/diff/IDs/hashes, publish/read back the PR, and record the verified binding in the declared queue. Only after that gate is this synthesis durable. This file asserts no future commit or publication outcome.
