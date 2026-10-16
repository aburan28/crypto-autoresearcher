# Historical selection rule for skipped NIST prime-field seed candidates is unknown

- **Status:** `open`
- **Kind:** unknown cause; missing historical generator program or run log
- **Affected work:** [assessment of eleven skipped seed candidates](../research/nist_seed_skipped_curves_20261016/report.md), [selection comparison](../research/nist_seed_selection_deep_20261016/report.md), and [P-224 twist follow-up](../research/nist_seed_selection_followup_20261016/report.md); interpretation of the recovered NIST/ANSI seed streams
- **Next action owner:** unassigned historical-source investigation; a Coordinator would own any claim-changing experiment
- **Last updated:** 2026-10-16

## Problem

We cannot explain why eleven otherwise qualifying prime-field curves were passed over in the six timestamp streams reported by Valsorda and Anthropic, because the original candidate-acceptance code, its state and a complete run log are unavailable. The tested set is the eleven unpublished candidates explicitly named in those reports: five over the 239-bit ANSI field, two over P-192's field, one over P-256's field and three over P-224's field. A historical selection conclusion must classify the published and omitted candidates under one independently specified rule, rather than infer motive from the final constants alone.

## Evidence and uncertainty

- **Observed:** [The audit code](../research/nist_seed_skipped_curves_20261016/audit.py) reproduces all ten published 160-bit seeds, reconstructs all eleven omitted seeds and checks their SHA-1-derived curve equations, prime group orders and Hasse uniqueness. The [exact records](../research/nist_seed_skipped_curves_20261016/assessed.json) and [PDF](../research/nist_seed_skipped_curves_20261016/report.pdf) report embedding-degree and bounded CM screens, twist factors, and published-curve controls. All eleven pass the visible order-bit-length rule. The [first failed indexing attempt](../research/nist_seed_skipped_curves_20261016/audit_attempt1.log) is preserved; its corrected run is [here](../research/nist_seed_skipped_curves_20261016/audit_attempt2.log).
- **Derived or proved:** Each tested skipped class has a prime-order group with cofactor one and no same-field group-order match to a published curve. Three omitted 239-bit curves have `n>p`, but so does published prime239v2, so `n<p` cannot be the universal missing rule. These facts are bounded to the named streams and candidates.
- **New bounded selector counterexample:** [The P-224 follow-up](../research/nist_seed_selection_followup_20261016/report.md) verifies that passed-over block 1485 has a 122-bit largest prime factor of its quadratic-twist order, versus 118 bits for published P-224. The published curve was not selected by maximizing this metric among the four known qualifying P-224 blocks. Nineteen of the 21 checked twist orders are now fully factored; two 239-bit cases remain censored by the earlier time cap. This excludes one proposed preference, not every twist predicate.
- **Suspected explanations:** The original program may have consumed RNG output during validation, may have had an implementation error, or may have applied an unpublished test. These are alternatives, not observed causes. [Valsorda](https://words.filippo.io/seeds-solved/) and [Anthropic](https://www.anthropic.com/research/ecdsa-curve-origins) report no resolved selection criterion.
- **Missing capability:** Contemporaneous source code, logs or a retained state trace for the candidate generator and acceptance decision. A present-day reimplementation cannot recover those historical facts by itself.
- **What this evidence does not establish:** It does not establish how many timestamps were tried, a deliberate weak-curve choice, the absence of a costly hidden route, the two remaining 239-bit twist factorizations, or a universal rule from a bounded trait screen. Anthropic explicitly says the surviving numbers do not count generator runs.

## What would unblock it

- [ ] Recover contemporaneous code/logs or independent documentation that specifies the acceptance path, RNG consumption and decision for all named accepted candidates in the six streams, and replay it from the stated timestamps to the published seed ordinals.
- [ ] If no historical artifact is recovered, predeclare a deterministic alternative rule with executable code, parameters and inputs, then show that it classifies all eleven omissions and all ten published seeds and correctly predicts at least one independent held-out historical stream or decision not used to construct it. Record counterexamples as well as matches.

The first condition would establish the operational selection mechanism if the artifact's provenance is sound. The second would establish a predictive reconstruction, but would still require external provenance to claim it was the actual 1997–98 program. Neither condition by itself establishes an ECDLP advantage or rules out a separate hidden mathematical route.

## Next discriminating step

- **Action or proof obligation:** Search contemporaneous FreeLIP/NTL and standards-development archives for the candidate-generation and order-validation code or its logs. If a candidate historical procedure is found, freeze it before testing all eleven omitted ordinals and ten published controls.
- **Inputs and controls:** The six timestamps, exact seeds and field equations in the linked audit; the ten published seeds as positive controls; all eleven omissions as negative historical decisions; P-239 prime239v2 as a control against the false `n<p` rule. Keep candidate-generation arithmetic separate from any later base-point search.
- **Execution limits and stop condition:** Read-only archive search first. A test of a recovered program must declare its bounded run length, seeds, dependencies and expected output before execution. Stop and preserve the first mismatch; do not tune a rule after seeing it and then call that run held out. This sets a test boundary, not a research spending cap.
- **Outcomes and next actions:** Exact replay with sound provenance supports the historical explanation; a rule that matches only the observed examples remains a hypothesis; a mismatch rejects that particular rule; missing archives or failed execution leave the question open without a mathematical inference.
- **Recheck trigger:** New primary-source code/logs, independently documented acceptance criteria, or a predeclared predictive reconstruction.

A planned step is not a completed experiment. Apply the existing execution, review and archival rules before a claim-changing run or decision.

## Resolution and history

2026-10-16: Opened after the eleven-curve structural assessment. Unresolved. This record names the missing historical evidence and does not alter a goal or hypothesis status.

2026-10-16: Added the exact P-224 block-1485 twist factorization and its counterexample to maximizing the largest twist prime factor. The historical acceptance path remains unknown.
