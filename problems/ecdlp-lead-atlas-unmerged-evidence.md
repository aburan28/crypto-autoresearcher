# ECDLP lead atlas source and validation gap

- **Status:** `investigating`
- **Kind:** evidence provenance and independent-validation gap
- **Affected work:** [ECDLP lead atlas](../knowledge/leads/ecdlp/README.md), its [report](../docs/reports/ecdlp-lead-atlas-20261024/README.md), [crypto PR #2495](https://github.com/aburan28/crypto/pull/2495), and [ecc-challenges PR #56](https://github.com/aburan28/ecc-challenges/pull/56)
- **Next action owner:** atlas reviewer after the remaining source PR and current-main checks reach final states
- **Last updated:** 2026-10-24

## Problem

Six atlas citations for the rule-v4, IC validation-gate and hybrid-guess studies were absent from the original review's pinned crypto main. Crypto PR #2495 has since merged as `19ecb8d37f8d8523a14e5014ba9a7172e02111aa`: the four distinct cited study files have the same Git blob hashes on current crypto main `5cb553810e5bbfbd8691ec614ffcaacefc625757` as on the atlas's immutable source pin. This closes that source-availability gap but does not prove the studies. Two negation-walk citations remain at open ecc-challenges PR #56 head `1f49962624b13fbed4a3e9ad980d757f5fa5bc59`, absent from the original review's pinned main. The full four-repository exact-tree review has not been reproduced.

## Evidence and uncertainty

- **Observed:** `tools/lead_atlas.py --check --strict-paths` with a crypto PR #2452 checkout and a cryptanalysis sheriff checkout reported seven missing crypto paths before correction: six study citations from then-open crypto PR #2495, and one symlink alias for the committed `.agents/skills/ecdlp-surfaces/SKILL.md`. The six citations remain pinned to that immutable study commit and the skill path uses the canonical tracked file. The corrected local strict check had zero errors and 12 warnings: four cryptanalysis refs not fetched and eight ecc-challenges citations without a local checkout. The [source-path receipt](../docs/reports/ecdlp-lead-atlas-20261024/source-path-check.json) records 16 of 16 targeted GitHub blobs found at their named commits. The [merged-source check](../docs/reports/ecdlp-lead-atlas-20261024/crypto-merged-source-check.json) verifies byte-identical Git blobs for all four distinct crypto study files on merged main. These checks establish file identity, not scientific claims.
- **Observed:** The current lead rows tally 149 total, including 53 `open_next_step` and eight `open_unexamined`. The current ledger has 2,078/2,078 coverage after 29 new source records were mapped; the mapping review is `docs/reports/ecdlp-lead-atlas-20261024/coverage-20261024-mapping-review.json`. Two new transfer leads keep the n=7 cover-floor trial and the separate Jacobian-class proposal open. The original `REVIEW_STATE.json` is a historical 50/9 stamp, not a current four-repository review. The changed row `LEAD-ICE-hybrid-guess-determine-l7` cites the open PR for its new measured numbers.
- **Derived or proved:** The path, blob and tally findings above are direct Git-tree and row-count facts. Separate raw audits reproduced the [Table B ledger cost fields](../docs/reports/ecdlp-lead-atlas-20261024/tableb-ledger-audit.json), [rule-v4 paired cold ratios](../docs/reports/ecdlp-lead-atlas-20261024/v4-pair-audit.json), and the [hybrid summary's 83 branch JSONL records, 40 rows and ten minimum guess counts](../docs/reports/ecdlp-lead-atlas-20261024/hybrid-raw-audit.json). The hybrid [recompute script](../docs/reports/ecdlp-lead-atlas-20261024/audit-crypto-hybrid.py) is included. These checks did not rerun the IC or closure binaries, verify every EC scalar or establish a below-rho result. The rule-v4 study still misses its frozen four-of-six criterion.
- **Suspected explanation:** The original survey read a crypto feature checkout while recording a main-branch review pin; its report treated the feature checkout paths as already published. This needs confirmation from the original survey's receipt.
- **Missing capability:** A current four-repository exact-tree verification, completion of the source's applicable hosted checks, and full controlled replay of the cited algorithms and controls.
- **What this evidence does not establish:** Merge status, file identity and summary recomputation do not validate the experiments, make leaderboard rows admissible, or prove any ECDLP claim. The four cryptanalysis refs and eight ecc-challenges paths have remote Git-object evidence, but their scientific semantics have not been independently replayed here.

## What would unblock it

- [ ] Reconcile the remaining ecc-challenges PR #56 and all applicable crypto current-main checks; inspect every failed or cancelled check and confirm the two walk files in its final reviewed tree. Crypto study source presence on merged main is verified; its cancelled or queued checks are not.
- [ ] Complete the independent binary, scalar and control replay beyond the scoped Table B ledger, rule-v4 paired-summary and hybrid JSONL audits before promoting atlas wording from provisional to validated.
- [ ] Run `tools/lead_atlas.py --check --strict-paths` against pinned checkouts of all four repositories, fetching the named cryptanalysis ref and both source PR commits, and recording every unresolved warning and path hash.

These conditions would establish source availability and scoped replay for the cited studies. They would not turn the atlas's coverage map into a proof of all past experiments.

## Next discriminating step

- **Action or proof obligation:** Validate the remaining ecc-challenges citations against PR #56's final head, then complete the missing crypto and walk binary, scalar and control replays on committed inputs.
- **Inputs and controls:** Use the PRs' frozen protocols, raw ledgers, scalar checks, matched rho arms, negation-walk correctness controls and independent recompute scripts; compare resulting hashes and numbers to their reports.
- **Execution limits and stop condition:** Do not launch new scientific trials through this audit. Stop at a missing input, failing control, incomplete current-head CI or source mismatch and report that exact condition.
- **Outcomes and next actions:** A passing final source tree and replay permits a new review stamp; a failed replay keeps the claims provisional; a missing file requires correcting or removing its citation; runner or access failures remain infrastructure gaps.
- **Recheck trigger:** PR #56 merges, closes or changes head; crypto current-main checks finish; or a four-repository checkout becomes available.

## Resolution and history

- 2026-10-24: Initial cross-repository path audit found seven crypto errors. Six study citations were source-pinned to open PR #2495; one symlink alias was corrected. Remote path inspection then found two ecc-challenges walk citations present only at open PR #56, which were also source-pinned. Scientific results remain under review.
- 2026-10-24: Crypto PR #2495 merged at `19ecb8d37`, and all four distinct study files retained their source-pin Git blob hashes on main `5cb553810`. Scoped raw audits reproduced Table B costs, six rule-v4 ratios and ten hybrid minimum guess counts; current-main CI and full algorithmic replay remain open. PR #56 is still open.
