# Remaining archived ledger schema repair

On main commit `67c47366780470ce1dd27bd4764552f2d0725dcc`, focused native validation reproduces all **32 remaining errors** in the 14 records reported by the complete hosted ledger job. This change removes **31** of those errors; **one remains unresolved**. A complete local corpus pass is not claimed.

## Corrections and source review

Read each archived record, its actual external review plan and the existing native review-plan/supersession contracts before constructing the views. Primary sources and exact field mappings are recorded in [transport-preservation.json](transport-preservation.json). The existing single-quantity contract remains; multiple blind rederivations are now checked separately, each with its own quantity, owner and forbidden inputs. No restrictions are combined or borrowed from a parent.

Twelve additive source-bound record views preserve all original bytes. Four new external plan transports expose existing field names and control statements; a fifth already committed plan transport is reused. Full plans remain external to handoffs. Two IDEA citations keep their exact internal-proposal provenance in a separate related-proposals list while their valid knowledge citations remain unchanged. Ten handoff views retain original priors, roles, controls and scientific statuses. The original 251 registry bindings remain an exact text prefix; 12 new bindings bring this checkpoint to 263. No baseline, approval, trial, result or experimental budget is changed.

## Validation and its limits

The unchanged native validators accept all 13 affected non-run records and verify every one of the 263 source/replacement bindings. Thirty-eight focused tests pass, including five scoped-rederivation controls and five archive-fidelity/native transport controls. Their transcript is preserved alongside the earlier 42-test attempt. The latter had five failures and three errors caused by off-disk integration fixtures, including the complete validator's correct sparse-checkout refusal. Restoring the three exact AUXIN/transfer fixtures makes the applicable 38 tests pass. The four complete-corpus coverage tests remain required in hosted CI; no sparse override or test gate is changed.

The last error concerns the real, invalid-output `RUN-BINSTD-f7ca97` execution. Its frozen flat manifest is not a complete native run envelope. Original command/environment captures are absent from Git history and the seven-file archive receipt. Existing capture requirements remain mandatory; no successor envelope or fabricated capture is added. See the [specific obstruction](../../problems/binstd-f7ca97-original-execution-captures-missing.md).

This is administrative archive repair, with no new mathematical, timing or ECDLP conclusion. Existing research graphs and performance sources are unaffected. Hosted full-ledger/harness checks and review remain required before merge; a 31-error reduction does not establish clean main.
