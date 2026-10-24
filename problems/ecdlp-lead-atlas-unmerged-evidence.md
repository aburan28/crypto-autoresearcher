# ECDLP lead atlas cites unmerged cross-repository evidence

- **Status:** `investigating`
- **Kind:** evidence provenance and independent-validation gap
- **Affected work:** [ECDLP lead atlas](../knowledge/leads/ecdlp/README.md), its [report](../docs/reports/ecdlp-lead-atlas-20261024/README.md), [crypto PR #2495](https://github.com/aburan28/crypto/pull/2495), and [ecc-challenges PR #56](https://github.com/aburan28/ecc-challenges/pull/56)
- **Next action owner:** atlas reviewer after the two source PRs reach final states
- **Last updated:** 2026-10-24

## Problem

Six atlas citations for the rule-v4, IC validation-gate and hybrid-guess studies point to files present at crypto PR #2495 head `1397a09db5fb48edc2f9c2edca78035a2e4da5ca`, but absent from crypto main `ec77beacc97af1db0b22530d620c2eb39ac9fbd7` and the atlas review's pinned crypto commit `da3a1b5d53323a4fb14ed761ca269e84b6018089`. Two negation-walk citations similarly exist at ecc-challenges PR #56 head `1f49962624b13fbed4a3e9ad980d757f5fa5bc59`, but not at the review's pinned ecc-challenges commit `3a71596ba85434bd98604cfda1e974c5b6c2dcc3` or current main. The atlas therefore cannot present these studies as published-main, independently validated results. The same full four-repository path check used by the original review has not been reproduced from this checkout.

## Evidence and uncertainty

- **Observed:** `tools/lead_atlas.py --check --strict-paths` with a crypto PR #2452 checkout and a cryptanalysis sheriff checkout reported seven missing crypto paths before correction: six are files in open crypto PR #2495, and one was a symlink alias for the committed `.agents/skills/ecdlp-surfaces/SKILL.md`. GitHub's content API found each of the four distinct study files at PR #2495 head. Six citations are now pinned to that immutable head and the skill path uses the canonical tracked file. The corrected local strict check has zero errors and 12 warnings: four cryptanalysis refs not fetched and eight ecc-challenges citations without a local checkout. The [source-path receipt](../docs/reports/ecdlp-lead-atlas-20261024/source-path-check.json) records 16 of 16 targeted GitHub blobs found at their named commits, including the four cryptanalysis branch-ref paths and both open PR #56 walk paths. This verifies path presence, not scientific claims.
- **Observed:** The current committed lead rows tally 147 total, including 51 `open_next_step` and eight `open_unexamined`. The original `REVIEW_STATE.json` is a historical 50/9 stamp. The changed row `LEAD-ICE-hybrid-guess-determine-l7` cites the open PR for its new measured numbers.
- **Derived or proved:** The path and tally discrepancies above are direct Git-tree and row-count facts. The scientific claims in PR #2495 have not been independently replayed in this atlas audit.
- **Suspected explanation:** The original survey read a crypto feature checkout while recording a main-branch review pin; its report treated the feature checkout paths as already published. This needs confirmation from the original survey's receipt.
- **Missing capability:** A current four-repository exact-tree verification and independent replay of the cited raw studies after their source PR reaches a final state.
- **What this evidence does not establish:** File presence at an unmerged commit does not validate the experiments, make leaderboard rows admissible, or prove any ECDLP claim. The four cryptanalysis refs and eight ecc-challenges paths have remote Git-object evidence, but their contents and scientific semantics have not been independently replayed here.

## What would unblock it

- [ ] Reconcile crypto PR #2495 and ecc-challenges PR #56 final commits and all applicable current-head checks; inspect any failed check and confirm the eight cited files and their content hashes are in final reviewed trees.
- [ ] Independently replay the rule-v4 validator numbers and hybrid-guess conclusions from committed raw artifacts, with their stated controls and limitations, before promoting atlas wording from provisional to validated.
- [ ] Run `tools/lead_atlas.py --check --strict-paths` against pinned checkouts of all four repositories, fetching the named cryptanalysis ref and both source PR commits, and recording every unresolved warning and path hash.

These conditions would establish source availability and scoped replay for the cited studies. They would not turn the atlas's coverage map into a proof of all past experiments.

## Next discriminating step

- **Action or proof obligation:** Validate the eight pinned citations against both source PRs' final heads, then run their source scripts and report validators on committed inputs.
- **Inputs and controls:** Use the PRs' frozen protocols, raw ledgers, scalar checks, matched rho arms, negation-walk correctness controls and independent recompute scripts; compare resulting hashes and numbers to their reports.
- **Execution limits and stop condition:** Do not launch new scientific trials through this audit. Stop at a missing input, failing control, incomplete current-head CI or source mismatch and report that exact condition.
- **Outcomes and next actions:** A passing final source tree and replay permits a new review stamp; a failed replay keeps the claims provisional; a missing file requires correcting or removing its citation; runner or access failures remain infrastructure gaps.
- **Recheck trigger:** Either source PR merges, closes, changes head, or a new four-repository checkout becomes available.

## Resolution and history

- 2026-10-24: Initial cross-repository path audit found seven crypto errors. Six study citations were source-pinned to open PR #2495; one symlink alias was corrected. Remote path inspection then found two ecc-challenges walk citations present only at open PR #56, which were also source-pinned. Scientific results remain under review.
