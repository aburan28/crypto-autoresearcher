# Review round closure: pfdr-battery-20260904

All ten reviewer reports are final and every experiment pair passes
`tools/check_review_independence.py` ("every joint owned and attested,
blindness respected, controls declared").

## Report finality and where each is recorded

Reviewers were dispatched in one wave, so no sibling report existed when any
of them began. Every report declares `read_sibling_reports: false`. Several
final reports were physically swept into commits whose subject lines name a
different task, because the WIP snapshots taken while agents were still
running used a broad `git add -A coordination/reviews/`. The content in each
case is byte-identical to the reviewer's final version, verified against the
working tree at the time of the completion notification.

| task | experiment | role | verdict | final content recorded in |
| --- | --- | --- | --- | --- |
| TASK-20260904-2bb29d | c04716 | validator | holds | own commit |
| TASK-20260904-6681da | c04716 | red team | **3 of 4 BREAK** | 595415d3 |
| TASK-20260904-4c0d7d | fd901a | validator | holds | own commit |
| TASK-20260904-8c5f97 | fd901a | red team | **R2, R4 BREAK** | 402dfe02 |
| TASK-20260904-642cf5 | 5726af | validator (blind) | holds | own commit |
| TASK-20260904-ed0e8f | 5726af | red team | **4 of 5 BREAK** | d3249e14 |
| TASK-20260904-a7eead | 20ee58 | validator (blind) | holds | own commit |
| TASK-20260904-0d66e3 | 20ee58 | red team | holds | 67e51bea |
| TASK-20260904-42b33a | cbdefb | validator (blind) | **V2 BREAKS** | own commit |
| TASK-20260904-3a2ff5 | cbdefb | red team | **R1 BREAKS** | own commit |

## Coordinator verifications performed independently of the reports

Three load-bearing adverse findings were checked directly rather than taken
on report. All three confirmed.

1. **closure.py retention gap (42b33a, V2).** `closure.py` appears in exactly
   one commit in all of git history, `a3a81e33`, at `63475db5...`. The version
   `74e659bb...` — pinned by the `fixture`, `dff-agreement` and `s1-slice`
   manifests, which are the three blocking instrument controls — is in no
   reachable commit and not in the tree. The 20 measurement runs pin
   `63475db5` and are unaffected.
2. **fall_dim counterexample (ed0e8f, R1).** Ran the reviewer's
   `counterexample_certificate.py`: both instances reproduce
   (p=13, a=12, b=3, x_R=11 and p=19, a=2, b=15, x_R=9; N_sol=8; actual (5,3)
   against predicted (5,4)). This is reproduction of the reviewer's
   implementation, NOT an independent re-derivation.
3. **generator degree (6681da, R1).** `KN-TECH-002` states `deg S_n` per
   variable is `2^{n-2}`, giving `m*2^{m-1}` total in m unknowns; and
   `EXP-PFDR-5726af/stage0-htop.md` measured total degree 12 with per-variable
   `[4,4,4]` at m=3. The record's `2m` coincides only at m=2, which is not in
   the c04716 grid.

## Convergence between blinded reviewers

Two independent findings, reached without contact, both locate the 5726af
anomaly in **homogeneity rather than curve structure**: the 642cf5 validator's
curve-free block-factored null reproduces (5,4), and the ed0e8f red team's
inhomogeneous curve-free, target-free, x_R-free null reproduces (5,4) and
(13,12), as does a dense random polynomial with no block structure.

Nothing here is a decision. Interpretation and all ledger writes belong to the
composition task TASK-20260904-e6b4dd.
