# ECDLP retrospective leads: follow-up records (2026-10-26)

Follow-up to the five proposals `IDEA-20261011-{049724, 07c83f, 6bdbe2, dcfc4d,
fb7b7e}` merged in PR #2588 (filing note:
[`../ecdlp_retrospective_leads_20261011/README.md`](../ecdlp_retrospective_leads_20261011/README.md)),
after an independent review of that PR. Records are write-once, so every fix
here is a new record. Nothing existing is edited, no status changes, nothing is
approved, no experiment was run. Filed by an Idea Generator session; the
Coordinator adopts, or not, by decision record. Ledger base: `origin/main`
`6a69b2d02e`.

## The records (all under `ledger/corrections/`)

| record | concerns | what it does |
| --- | --- | --- |
| `CORR-20261026-ed224e` | all five | lead-atlas mapping (`--match` re-run, 11 lead files read) and the escape-premise statement the lead rule requires. Lead 1 escapes none of the closed Frobenius premises: it is a re-measurement. Coverage rows listed for the atlas reviewer. |
| `CORR-20261026-f50bf6` | Lead 1, `049724` | the protocol has run twice (crypto #2583 legacy, #2623 native): results, scope, caveats, stale fields, priority restated low, status of each falsification condition, the rank-5 ceiling, the one-clock-only gap, the closed-lineage dedup omissions. |
| `CORR-20261026-58d9a2` | Lead 2, `07c83f` | the null evidence is larger than "the toy crater-versus-floor null" (H-ECTD-19017a / -ac8627 / -001 / -e88346, DEC-20261015-5a1f2c, the 53-bit campaign with a certified 96-bit floor, crypto #2585); pair supply, WDSat, prime-field arms, binary-only arms under a prime question, "closes the families". |
| `CORR-20261026-7fb5db` | Lead 3, `6bdbe2` | Stage 1 of IDEA-20261001-621974 already lists certificate re-summation; crypto #2591 implemented and measured the direction; the three review findings checked against its receipts; what remains. |
| `CORR-20261026-2cc304` | Lead 4, `dcfc4d` | "CryptoMiniSat stays flat" is wrong (about 7x at s = 4); the estimator double counts; the success criterion cannot discriminate; no noise floor for a rank flip; two near neighbours; crypto #2584 has run it. |
| `CORR-20261026-82b43e` | Lead 5, `fb7b7e` | no positive control for isogeny or cover candidates; the "zero false weak labels" criterion must reference the tool's calibration finding; two near neighbours; crypto #2594 built the tool. |
| `CORR-20261026-2e43c1` | `EV-BINSTD-769c7c` | RE-REVIEW REQUEST with the matched-null result below; downstream citations listed so the Coordinator can re-rank. |
| `CORR-20261026-9a40e2` | the filing README | stale statements (the removed approval cap, branch states) and the registry observation. |

## The matched null for `EV-BINSTD-769c7c`

`EV-BINSTD-769c7c` reads a curve/generic collision ratio of about 3.1 as
structural concentration. The curve census has a negation-closed window and
sign-folded keys `x(L)`; its generic replica is an open random window with
unfolded keys. Each feature alone changes the expected count: the key fold
doubles it, and negation closure makes every attempt `{P,Q}` collide with
`{-P,-Q}` (exactly `T/2` vacuous collisions, a zero relation vector).
Hence reported ratio = `2 + N/T`.

`matched_null/matched_null_check.py` (independent; reproduces the producer's
census to the last digit) gives:

| | n = 17 (RC-1) | n = 19 (Koblitz) |
| --- | --- | --- |
| window, `T`, `N` | 483 points, 116,162, 130,412 | 1005 points, 504,008, 523,492 |
| reported combined / ratio | 160,633 / 3.1049 | 735,192 / 3.0302 |
| vacuous partner collisions (`T/2`) | 58,081 (36.2%) | 252,004 (34.3%) |
| nontrivial collisions, observed | 102,552 | 483,188 |
| nontrivial, uniform expectation | 103,467.7 (0.9911) | 485,247.7 (0.9958) |
| matched generic, 20 windows (ratio) | 3.1088 +/- 0.0199 | 3.0297 +/- 0.0092 |
| producer-style generic replica | 0.9928 | 0.9960 |
| curve over matched generic, combined | 0.9988 | 1.0002 |
| reported curve over generic | 3.131 | 3.034 |

Scope: two toy cells, pair-sum accumulator, `x`-keys. It does not test other
windows (the aligned half `V'_0` does concentrate, for the plain parity reason
checked in the output: all 245 points lie in `2G`, ratio 8.370 against the
predicted 8.381), Frobenius-closed windows, other `n`, the Stage 0 pricing or
the certificate results. The PR #2591 `n = 31` effect is a different observable
(Frobenius-conjugate abscissae); `matched_null/frobenius_window_closure.py`
shows 30 of its 34 merges are forced by the window geometry (460 large
abscissae with a point, 30 exact Frobenius merges; the PR's `L` is 460).
**Correction, 2026-10-31 (`CORR-20261031-855c68`):** the earlier random-window
expectation double-counted conjugates by using `2 * (n - 1) / (2^n - 2)` for
the pair probability. For a uniform size-`s` subset of the `2^n - 2`
non-`F_2` elements at prime degree `n`, each element has `n - 1` distinct
non-self conjugates, so the expected unordered conjugate-pair count is
`C(s, 2) * (n - 1) / (2^n - 3)`. The observed counts and exact forced-merge
counts are unchanged; the corrected expectations are:

| n | observed conjugate pairs | random-subset expectation | ratio |
| ---: | ---: | ---: | ---: |
| 17 | 128 | 63.6893 | 2.01 |
| 19 | 60 | 17.9123 | 3.35 |
| 23 | 54 | 1.3683 | 39.47 |
| 29 | 70 | 0.0272 | 2,572.55 |
| 31 | 338 | 0.0073 | 46,374.44 |

Thus the `n = 17, 19, 23` windows are **not** at the random-window rate. These
are window-level comparisons to a uniform-subset model, not a reanalysis of the
producer's trial stream. The corrected expectation does not change the
separate statement that 30 of 34 `n = 31` observed merges are exact Frobenius
images. The matched-null plot and PDF are generated from `output.json` by
`plot_matched_null.py`; they do not plot this window-closure expectation and
were not regenerated for this correction.

Files: `matched_null/matched_null_check.py`, `output.json`, `summary.txt`,
`frobenius_window_closure.py`, `frobenius_window_closure.json`,
`frobenius_window_closure.txt`, and the graph and report drawn from
`output.json` by `plot_matched_null.py` (recorded values only):
`matched_null.svg`, `matched_null_report.pdf`. Reproduce (about 5 s each, Python 3.13, numpy 2.5):

```sh
cd research/ecdlp_retrospective_followup_20261026/matched_null
python3 matched_null_check.py --out output.json > summary.txt
python3 frobenius_window_closure.py --out frobenius_window_closure.json > frobenius_window_closure.txt
python3 plot_matched_null.py output.json
```

The check is independent in code, not blind: I had the reviewer's numbers
first, and read the producer's `generic_zn_census` to see how its replica forms
keys. I did not open the producer's field and curve code.

## Verified here, and reported only

| statement | status |
| --- | --- |
| lead mapping and dispositions | re-run and read at `6a69b2d02e` |
| existence and status of every cross-referenced ledger record | read at `6a69b2d02e` |
| `EV-BINSTD-769c7c` numbers, the matched null, `V'_0` | reproduced by the independent program |
| window-geometry premise of the `n = 31` merges | computed (30 exact merges, `L` = 460) |
| uniform-subset expectation for Frobenius-conjugate window pairs | corrected and unit-tested in `CORR-20261031-855c68`; not a replay of producer trials |
| accepted-trial superset (2 of 25 pairs differ in accepted count, 6 of 25 in histogram) | counted from 50 receipts of crypto #2591 |
| CryptoMiniSat medians, estimator algebra, FES solver share | read from crypto files / derived arithmetic |
| registry counts (267 / 266, and 111 more) | computed from `ledger/proposals` and `tools/ecc_priority.py` |
| every figure from crypto #2583, #2584, #2585, #2591, #2594, #2623 and the 53-bit campaign | read at the merge commits and `a7c41a4e0f`, not replayed |
| "14 of 34 registry prime curves `class-weak`, mostly BN" and its fix PR | relayed by the review; not reproduced, fix PR not read |
| which individual pairs merged at `n = 31`; whether a cap is "the knee" | reviewer's characterisations; not separately checked |

## Registry gap: a decision for the user (nothing edited)

`orchestration/research-priority.yaml` lists ENDO and ECTD in `ecc_areas`.
The tokens VOLC, ICINV, JINV, EQIC, EQLA, EWALK and TORS (all questions that say
"Lane of GOAL-ENDO-001") are in neither `ecc_areas` nor `excluded_areas`, so
`tools/ecc_priority.py` classifies them non-ECC by the question's area token
and 267 idea records (266 `proposed`; VOLC 28, ICINV 27, JINV 129, EQIC 17,
EQLA 14, EWALK 23, TORS 29) sit outside the ECC-first queue. Six more
ENDO-lane tokens are in the same state (CANL 19, CLGP 19, GGMB 14, INSTR 23,
MODEL 16, MTGT 20 proposed ideas; `excluded_areas` has `CLGRP`, not `CLGP`), so
13 tokens and about 377 proposed ideas in all.

Options, none taken: (A) add the tokens to `ecc_areas` (the file's rule is
membership by reading goal titles, and the lane's goal is ECC); (B) list them in
`excluded_areas` with reasons; (C) leave the file and make the classifier take a
question's area from its goal. This needs your decision because it changes which
ideas AGENTS.md "ECC comes first" requires to be designed rather than shelved.

## Graphs checked (AGENTS.md "Visual research record")

New: `matched_null/matched_null.svg` and `matched_null_report.pdf` (the figure
plus the full numeric summary). Unchanged, and why: the lead-atlas report
`docs/reports/ecdlp-lead-atlas-20261024` (no lead disposition, next action or
evidence entry changed); the index-calculus leaderboards and scoreboards (this
adds no whole-pipeline `S` point and no benchmark row); no canonical graph or
diagram source in `docs/` cites `EV-BINSTD-769c7c`. No edge in the new figure is
conjectural.

## Not done

No atlas row, `coverage.tsv`, registry file, existing record or status was
edited. No experiment, hypothesis, approval or decision was written. The
`validation-backlog-ci` branch (sixth note of the filing README) was not
examined. The Lead 5 calibration finding and the Lead 3 pair-level merge
attribution were not reproduced.
