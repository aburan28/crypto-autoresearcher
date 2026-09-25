# Review Report — TASK-20260925-5842cf

Zero-run independent red-team review of the DRAFT `AMD-EXP-GFPN-05ff43-20260925-admitdev`,
read with the approved launchkind addendum (`DEC-20260924-daf670`, LKA-1..LKA-15) and
everything it incorporates. Static only; `maximum_runs 0` is BINDING; no import of any
scanned-tree module. **Observations only. No approval recommendation. No statement about D,
H-GFPN-9a29be, or HEUR-GFPN-DFLAT.**

Reviewed draft: `experiments/EXP-GFPN-05ff43/amendments/v2_addendum_admitdev.yaml`
(status `draft`, `approved_by: null`). This report is not authorization for anything.

---

## Paths written

| path | sha256 |
| --- | --- |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/review-report.yaml` | computed by the archiving task (TASK-20260925-82235d) after this write |
| `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/review-report.md` | computed by the archiving task (TASK-20260925-82235d) after this write |

---

## Integrity checks (CRA-2), performed before any joint

**Overall: PASS.**

**(a)** admitdev draft sha256 equals the `TASK-20260925-3bd499` receipt's `addendum_sha256`,
and the file reads `status: draft`, `approved_by: null`, `approval_decision: null`.

```
$ sha256sum experiments/EXP-GFPN-05ff43/amendments/v2_addendum_admitdev.yaml
a286d7456499f107180241a745aa3b753a5ec2d09f44d32dfa36db0dbe6deb38  experiments/EXP-GFPN-05ff43/amendments/v2_addendum_admitdev.yaml
```

Expected (card / receipt): `a286d7456499f107180241a745aa3b753a5ec2d09f44d32dfa36db0dbe6deb38`. **MATCH.**
File lines 165–167: `status: draft`, `approved_by: null`, `approval_decision: null`. **MATCH.**

**(b)** the seventeen amendment files hash to `DEC-20260924-daf670` `bound_hashes`
(lines 1052–1068 of that file). All 17 verified byte for byte:

| file | sha256 |
| --- | --- |
| `v1_to_v2_reanchor_and_arm_iii.yaml` | `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3` |
| `v2_addendum_rung31.yaml` | `2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c` |
| `v2_addendum_paristack.yaml` | `856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7` |
| `v2_addendum_seedresolve.yaml` | `dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81` |
| `v2_addendum_solverevent.yaml` | `011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f` |
| `v2_addendum_healthresolve.yaml` | `ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d` |
| `v2_addendum_launchcover.yaml` | `c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447` |
| `v2_addendum_consumercover.yaml` | `a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0` |
| `v2_addendum_valueclose.yaml` | `877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1` |
| `v2_addendum_readbackcover.yaml` | `dcdb08451ec2d57f731d1ed826d58d2cf014d797092c44c9b7de8374af1cb84e` |
| `v2_addendum_readbackfull.yaml` | `0b6315d4b2ef810aa01d1890b39921f153b4d9017903cc5ce023b6dfddfaabc1` |
| `v2_addendum_readbackclose.yaml` | `f949951aca1ab011848048f7735b10d10413dd339e11046089b6f151aec4a48c` |
| `v2_addendum_failclosed.yaml` | `1dec09a9bd6e0a0dea6b8de7f3154c500fa80aafb95a7f862e4b21393b2b834c` |
| `v2_addendum_childend.yaml` | `e02af50bf112dd0a464b96b8858e952a0527097ee38869eebefa23d9a2a49f8b` |
| `v2_addendum_gapattr.yaml` | `919a3610c47ee295aa44317f2f29b43bc427a682fb43e9f87a749750cca274a7` |
| `v2_addendum_attcount.yaml` | `4154fd5206dde2987f9fe049e779078f7212c6d4afd23d9303e880946ea11a48` |
| `v2_addendum_launchkind.yaml` | `ac41f38f0c27d86fa98341e222a7ddd2b3d50d1e4476aaf46e454ad8a3b6a050` |

0 mismatches.

**(c)** every path of `coordination/goals/GOAL-GFPN-380702/archives/TASK-20260925-f0b9f0/preservation-receipt.json`'s
`path_sha256` hashes to its declared value. Verified with a scratch Python script (reproduced
below): 26 paths, 0 mismatches, 0 missing.

```python
# verify_f0b9f0.py — scratch, read-only
import json, hashlib
with open('coordination/goals/GOAL-GFPN-380702/archives/TASK-20260925-f0b9f0/preservation-receipt.json') as f:
    data = json.load(f)
psha = data.get('path_sha256', {})
mismatches, missing = [], []
for p, expected in psha.items():
    try:
        with open(p, 'rb') as fh:
            actual = hashlib.sha256(fh.read()).hexdigest()
    except FileNotFoundError:
        missing.append(p); continue
    if actual != expected:
        mismatches.append((p, expected, actual))
print('num paths:', len(psha), 'mismatches:', len(mismatches), 'missing:', len(missing))
```
Output: `num paths: 26 mismatches: 0 missing: 0`.

**(d)** the two review files of `TASK-20260924-d897a6` equal the `TASK-20260924-68cf6b`
receipt's `path_sha256`; the two of `TASK-20260924-1ecb7d` equal `TASK-20260924-7e8a5d`'s.

```
71d559a0bd3546ffc732d9ad06beaff4ceb27cbafd7f1840e6bb1394096c1f55  coordination/.../TASK-20260924-d897a6/review-report.yaml
d4533a93de84b8c0ebabbfd4b091b68e388b00c43949ac18dbe00d7d4f1a497d  coordination/.../TASK-20260924-d897a6/review-report.md
139f9c7c5583d1f4f99e81bdd16348ec28afb882d5f06af79ac7f8cef0b8a5d4  coordination/.../TASK-20260924-1ecb7d/review-report.yaml
97d1827722760ea64a5dfee107318570370acb7e48a676f44142cca901b27055  coordination/.../TASK-20260924-1ecb7d/review-report.md
```
All four MATCH the receipts.

**(e)** no `implementation-v2-r5*`, `trial-plan-v2-r5.json`, `trial-plan-v2-a1-r5.json`, or
`dev-evidence/stage-r5-dv/` path exists. Confirmed by `find` glob over
`experiments/EXP-GFPN-05ff43`: 0 matches.

**DP-5 sequencing note (not part of CRA-2, checked as a precondition):** `runs/` holds
exactly **54** run directories:
```
$ find experiments/EXP-GFPN-05ff43/runs -mindepth 1 -maxdepth 1 -type d | wc -l
54
```
(A naive `find ... -type d` without `-mindepth 1` returns 55 because it also matches the
`runs/` directory itself — a methodological trap noted as a deviation, not a finding; the
underlying DP-5 fact holds.) No `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/`
path existed before this task wrote it.

---

## AJ-0: known-answer control (reported first, CRA-4)

**Verdict: HOLDS.** The reviewer's satisfiability method — for each predicate, identify the
governing texts, trace the exact behaviour through the frozen/preserved source **as text**
(never imported or executed), and determine whether any assignment of the development
world's free choices can meet the predicate given that the traced behaviour is otherwise
deterministic on the fixed inputs the predicate names — flags **both** (a) and (b), unchanged.

### (a) readbackcover RB-5 (d), without admitdev

**Predicate** (`v2_addendum_readbackcover.yaml` lines 297–300): *"RB-4 exercised on copies
of the DV-18 (a) world: with the copy's manifest read-back list emptied, the wrapper
refuses a later package; with the original, it admits."* Read with RB-4 (lines 254–274) and
childend RG-3 (d) (`v2_addendum_childend.yaml` lines 391–403), under launchkind as approved,
**without** admitdev.

**Derivation.** RB-4 requires, for admission, for EACH of G1..G4: (a) raw-result
`completed_valid` + `gate_pass true`; (b) *"the r4 checker ... exits 0"*; AND *"REG-1
(d-parsed) passed"*. `r3_check_run.py` line 400: `return 1 if (errs or pr.returncode) else 0`
— the checker exits nonzero whenever its `errs` list is non-empty. `reg1()`
(`r3_check_run.py` 154–160) returns `{"verdict": "NOT_EVALUABLE", "reason": ...}` whenever
the plan's designated G1 package has not run under `RUNS`. That condition holds in
**every** development world of this zero-run lineage (CRA-1; `maximum_runs 0` is BINDING;
R4S-12: *"no repaired run package exists when this stage runs"*), because no development
check ever writes a package under the real production `runs/` path. RG-3 (d) states
categorically (and admitdev's own `changes.unchanged` list keeps this "unchanged"):
*"EXPECTED CHECKER ITEMS on a development package are EXACTLY the r4 analogues of
r3_check_run.py 329-330 ..., 331-332 ..., 333-334 ..., because the NOT_EVALUABLE block ...
carries neither key and G1 does not exist."* `reg1_recorded_check`
(`r3_check_run.py` 324–334) therefore always appends exactly three errors on a development
package. `errs` is never empty; the checker never exits 0; RB-4 (b) never holds; **"with the
original, it admits" is UNSATISFIABLE in every development world the texts permit.**

**Primary evidence** (independent of the note's prose): the raw DV-18 (d) attempt record,
extracted from the preserved bundle and verified against `stage-r4-dv/MEMBERS.sha256`
(member `dv18/dv18-summary.json`, sha256
`c41c79823444b71b195608ed7e5e0bbe95678c6f48e44511c76780f3103d8424`), key
`(d).copies.original.r4_checker_on_the_(a)_package`:
```json
{"exit_status": 1, "verdict": "FAIL", "frozen_checker_exit": 0,
 "stop_classes": ["another checker item: ['gate.regression_REG-1 not recorded PASS: NOT_EVALUABLE',
                   'gate.regression_REG-1 d_branch None != d-parsed',
                   \"gate.regression_REG-1 exclusion-list sha256 differs from the plan's\"]"]}
```
The FROZEN checker exits 0 (read-back present) while the FULL r4 checker exits 1 on exactly
the three RG-3(d) items — RB-4(b) refuses ("R-7 (RB-4 (b)) the r4 checker on gate package
DEV-DV18-a-controls: exit 1 verdict FAIL") even on the **unedited, "original"** copy.

**r4 note agreement:** `implementation-v2-r4.md` section 10.4 (lines 426–433): *"Preflight
of the F-4 package: with the ORIGINAL copy, RB-4 (a) holds and the r4 checker on the (a)
package has frozen exit 0 and exactly the three REG-1 items (verdict FAIL); ... Literal
reading NOT MET (the original also yields an RB-4 (b) refusal, because of the three REG-1
items)."* Agrees exactly.

### (b) failclosed RF-4 (c), as first worded

**Predicate** (`v2_addendum_failclosed.yaml` lines 463–471): *"EXPECTED CHECKER ITEM on a
development package: exactly the r4 REG-1 item"* (singular). Read with the r3 layer's
NOT_EVALUABLE block (`r3_run_wrapper.py` line 158, recorded at 565–566), as childend RG-3(d)
and review `TASK-20260924-1ecb7d` FC-1 cite it.

**Derivation.** `r3_run_wrapper.py` line 158: `reg1()` returns a dict with **only**
`{"verdict": "NOT_EVALUABLE", "reason": ...}` — no `d_branch` key, no
`exclusion_list_sha256` key. That dict is not `None`, so lines 565–566 write it verbatim
into every package's manifest (`if info.get("reg1") is not None: run["gate"] =
{"regression_REG-1": info["reg1"]}`). `reg1_recorded_check` then performs THREE independent
tests: (1) `verdict != "PASS"` → *"not recorded PASS: NOT_EVALUABLE"*; (2) `d_branch !=
R.REG1_D_BRANCH` → absent key reads `None`, always unequal → *"d_branch None != d-parsed"*;
(3) `exclusion_list_sha256 != plan's value` → same absent-key mechanism → *"exclusion-list
sha256 differs"*. All three fire together, unconditionally, whenever G1 has not run.
**"Exactly one item" is unsatisfiable: the mechanism always produces exactly three.**

**Primary evidence:** confirmed against the same DV-18(d) record — the `original` copy's
`r4_checker_output` lists all three lines verbatim.

**Conclusion:** both (a) and (b) are flagged. AJ-1 is reported without the CRA-4
"inconclusive" fallback. Every version of the scripts used, and their outputs, is preserved
under the scratch directory and reproduced in this report.

---

## AJ-1: satisfiability sweep

**Verdict: BREAKS** on one predicate — **AD-1 (d2) (i)**, the admitting branch. Per ADR-1's
own text this is the ONE predicate for which *"the pre-declared alternative of AD-1
applies"* rather than making the whole draft not-approvable-as-written; this review states
the finding and the alternative the draft itself names, and makes no approval
recommendation. Every other predicate swept either HOLDS (generally as a feasibility
observation, never a pass) or is READING-DEPENDENT as stated below.

### Predicate table

| id | world | expected failures / missing predecessors | satisfiable | witness (labelled after-the-stop where it is) | reading-dependent |
| --- | --- | --- | --- | --- | --- |
| DV-1..DV-17 (VA-4) | delivered r4 code, static+toy dynamic | none specific to admitdev's difference | yes | note §8 (table), §8.1 — all PASS, before the stop except DV-17 (after; labelled) | no |
| DV-18(a)/(b)/(e) — RF-4/RB-5(c)/RL-6/RG-3(d) | scratch dev world per command | R-7 gate not run; REG-1 NOT_EVALUABLE; R-8 predecessors missing; 3 RG-3(d) items — all EXPECTED | yes, under the RG-3(d) development reading | note §10.3 table — completed_valid, frozen checker exit 0, exactly 3 REG-1 items, 0 evidenced children without read-back, 19/8 (controls; independently cross-checked, see below), 7 (anchor-identity), 2+all (controls-a1); §11 substitution tables, 0 "not OK" | **yes** — satisfiable only under RG-3(d)'s development reading; unsatisfiable under the literal RF-4(c) it replaces (= AJ-0(b)) |
| **AD-1 (d1) refusal branch** | 2 development-copy edits of DV-18(a) world | both copies EXPECTED to refuse | **yes** | note §10.4 (attempt 3); **independently verified against raw bundle**, see below | no |
| **AD-1 (d2) admitting branch** | RK-4(e)/D-19 coherent copies | (i) explicitly requires NO refusal for every gate image | **NO — UNSATISFIABLE** | none found; card-suggested witness (i)(5) is a refusal-differential test, not an admission test | no |
| RH-5(d) order rule | 2 scratch processes, run first | n/a | yes | note §10.1 — (f)(xiv)/(xv) ran 05:41:04Z–05:41:12Z, first in the DV-18 window | no |
| toy-G2 SSF "expected failure" (D-5) | DV-7 toy-prime world | none enumerated in RF-4(b) for a toy package's own solve failure | yes, as observed (reproducible over 2 stages) | note O-2, §8.1 | **yes** — see below |
| RK-4(e)(1)-(18),(23) coherent-copy verdicts | RK-4(e)/D-19 coherent copies | varies per item | yes, except the admitting requirement folded into (d2) | note §10.7 — items (1)-(18),(23) all as required; only (11)/(12) are PASS-class, both non-gate-image child-end classifications | no |
| remaining extended DV-18 (RF-6/RG-7/RH-6/RI-3/RJ-5/RJ-4(c)/RJ-6/RK-4(c,d)/RL-6(f,g)) | scratch + in-place-altered objects | varies per item (32+ sub-items) | yes | note §10.1-10.2, §10.5-10.7, §11-12 — reported as a group (see Deviation DEV-4 below); LKA-7 closure scan and CX-A control independently spot-checked | no |

### The break: AD-1 (d2) (i)

**Predicate** (`v2_addendum_admitdev.yaml` lines 267–285): on the coherent copy set of
readbackclose RK-4(e)(5), in which *"every gate image G1..G4 (and, for an addendum
package, the controls_a1 image) and every package the later package requires or reads has
a copy whose r4 checker exits 0 and whose REG-1 record is recorded PASS"*: (i) the
wrapper's preflight of the later package **ADMITS** (no RB-4/RL-4/RK-3/RF-3 refusal).

**Derivation.** `reg1()` computes ONE result per plan copy: it looks up
`cand = RUNS/g1_id(P)`, where `g1_id(P)` is the PLAN's designated **real production** G1 id
(e.g. `RUN-GFPN-3e27a0` for the r4 plan), and returns `NOT_EVALUABLE` unless that exact id
has a `raw-result.json` on disk. In every development world of this zero-run lineage
(`maximum_runs 0` is BINDING; R4S-12: no repaired package exists under `runs/` during any
development check; no r4 or r5 package has ever been written there), that exact production
id never exists on disk — so `reg1()` is unconditionally `NOT_EVALUABLE` for the **whole
plan copy**, for every package built from it, including a "coherent copy of G1 itself". RG-3
(d) — which admitdev's own `changes.unchanged` list explicitly keeps "its words and reach" —
states categorically that a development package's expected checker items are exactly the
three REG-1-derived FAILING items, "because REG-1 is NOT_EVALUABLE where G1 does not exist";
this is not narrowed for RK-4(e) coherent copies (RK-4(e)/D-19 recomputes only the
manifest's `solver_events` block and `child_readback_accounting` — it does not, and by its
own words cannot, fabricate a real production G1 package at the plan's fixed production id).
Since `r3_check_run.main()` (line 400) returns nonzero exit whenever `errs` is non-empty,
**"the r4 checker exits 0 AND whose REG-1 record is recorded PASS" can never hold for any
gate image in any development world under this lineage.**

**Witness search.** The r4 note's DV-18(i) table (§10.7, items (1)–(18), (23)) — the only
place RK-4(e) coherent copies are exercised — contains no item demonstrating "checker exits
0 AND REG-1 recorded PASS" on any gate-image copy. Item (5), which the card names as the
candidate witness, is: *"a failing F-4 copy does not refuse the build package, a failing G1
copy does"* — a **refusal-differential** test, not an admission test. Independently
verified against the raw bundle record (`dv18/dv18-summary.json`, key `"(i) copies".items
["(5)"]`):
```
"(5) a failing F-4 copy does not refuse the next package (build); a failing G1 copy (required, read) does"
expectation: "no refusal naming F-4; a refusal naming G1"
observed: both sides are FAIL records (F-4's own verdict is FAIL; its failure just does not propagate)
```
No item in the table shows an ADMITTING (i)-branch outcome. **The card's suggested witness
confirms the gap rather than filling it.**

**The draft's own pre-declared alternative.** admitdev anticipates this exact outcome:

> *"PRE-DECLARED ALTERNATIVE (fixed here, before any review): if the review finds (d2)
> unsatisfiable in every development world the texts permit (ADR-1), the approving act may
> approve with (d2) DELETED, on condition that its decision and the r5 stage card declare
> residual RDL-1: 'RB-4's and RL-4's admitting branch on a real gate set is first exercised
> at the r5 gate; a wrongful refusal there is fail-closed, an impediment for a Coordinator
> decision, never evidence'. (d1) is never deleted."* (lines 300–307)

Per ADR-1: *"A predicate named unsatisfiable makes the draft NOT APPROVABLE AS WRITTEN,
except (d2), for which the pre-declared alternative of AD-1 applies."* **This review states
the finding only. Applying ADR-1 / the alternative is the approving act's decision, not
this review's (CRA-6: no approval recommendation).**

### AD-1 (d1) — the refusal branch — independently verified, satisfiable and discriminating

`v2_addendum_admitdev.yaml` lines 240–266. Independently verified against
`dv18/dv18-summary.json` key `"(d)"` (sha256
`c41c79823444b71b195608ed7e5e0bbe95678c6f48e44511c76780f3103d8424`, checked against
`MEMBERS.sha256`):

| copy | frozen_checker_exit | r4 checker exit | items | RB-4(b) refuses? |
| --- | --- | --- | --- | --- |
| `original` (i) | 0 | 1 | exactly the 3 REG-1 items | yes, naming the (a) package |
| `readback_list_emptied` (ii) | 1 | 1 | the read-back line **plus** the 3 REG-1 items | yes, naming the (a) package |

**Discriminant confirmed**: the line `"no child RLIMIT_AS read-back recorded"` is the FIRST
bullet of copy (ii)'s frozen-checker output and is **absent** from copy (i)'s output —
exactly as AD-1(d1)'s DISCRIMINANT clause requires.

### Toy-G2 SSF "expected failure" (D-5) — reading-dependent

`implementation-v2-r4.md` D-5 (lines 622–624): the toy G2 package at p′=1039 persistently
produces the SSF signature on every attempt, in **both** the r3 and r4 stages; the Executor
declares its "did not pass" refusal EXPECTED. VA-4's own words for DV-7 ("the checker on
every toy package") do not state that a toy package's own completion status must PASS, nor
does RF-4(b)'s enumerated EXPECTED PREFLIGHT REFUSALS list (R-7 gate packages; R-7 REG-1
NOT_EVALUABLE; R-8; the RB-4/RL-4/RK-3/RF-3 admission; the R-6 analogue) name "a toy gate
package's persistent SSF failure". Under a reading limiting "expected" strictly to that
enumerated list, D-5 falls outside it — an Executor accommodation established by repeated
practice across two stages rather than a numbered, textually-authorized exception. Under a
reading that "the checker runs on every toy package" (not "every toy package's own solve
PASSES"), D-5 is within DV-7 as worded. **Not a break** (this predicate predates admitdev
and is unaffected by AD-1..AD-5's difference); reported per the card's own attention item.
The cheapest discriminating check: whether VA-4's "no development check is re-run to obtain
a pass" implies the FIRST occurrence of this refusal (in r3) should have STOPped the stage —
in which case its recurrence in r4, never promoted to a numbered rule between the two
stages, is an uncorrected precedent rather than a satisfied predicate.

### Cross-check: RB-5(c)'s "19 capped children / 8 SC-4 rows"

```
$ ls experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956/child/*.meta.json | wc -l
11
$ ls experiments/EXP-GFPN-05ff43/runs/RUN-GFPN-bfe956/solver/ | grep -c '\.ms\.out$\|\.ms\.log$'
16
```
11 builders + 8 solves (16 files = 8×2) = **19**, matching RB-5(c) exactly.

### Fail-closed findings

| id | text | cost |
| --- | --- | --- |
| FCF-1 | DV-18(d) attempts 1 and 2 were harness faults (D-12): attempt 1's plan copy did not make the (a) package the G4 image; attempt 2's copy also rewrote the id map. Both preserved. | two harness-construction iterations; no repository/package write |
| FCF-2 | DV-18(b) attempt 1: harness looked for plan kind "anchor_identity" (real kind "anchor"); stopped before any launch. | one harness-construction iteration |
| FCF-3 | A wrapper-recorded outcome (RF-3(b)) or infrastructure-stop outcome (RG-2) stops the dependent chain for a Coordinator decision, never evidence (confirmed in raw `(i)(15)` record). | an impediment, not a re-run |

### Deviation: DV-1..DV-17 and one group of extended DV-18 items reported as feasibility-witness blocks

DV-1..DV-17 are untouched by AD-1..AD-5's difference (admitdev's own `unchanged` list names
them); they are reported as a block rather than individually re-derived, since the joint
(AJ-1) concerns admitdev's difference. One group of 32+ extended DV-18 sub-items
(RF-6/RG-7/RH-6/RI-3/RJ-5/RJ-4(c)/RJ-6/RK-4(c,d)/RL-6(f,g)) was reported from the r4 note's
own table rather than independently re-derived item by item, given the depth already spent
on the (d1)/(d2) pair and the AJ-0/AJ-3 derivations (the weakest evidentiary tier this
review used for any predicate — see Deviations below). Two representative points were
independently spot-checked: the LKA-7 closure scan (`r4_recorder.py` lines 447, 475 read as
text — see AJ-3) and the CX-A discriminating control's gap-vs-verdict-level distinction
(cross-read from `dv18-summary.json`'s `"in_place"` block during AJ-0/AJ-1 extraction).

---

## AJ-2: discrimination

**Verdict: HOLDS.**

**Definitions.** W-IGNORE: a wrapper whose RB-4(b) admits whenever RB-4(a) holds, whatever
the checker's exit status. W-STRICT: a wrapper that refuses every later package.

**From the texts:** W-IGNORE fails AD-1(d1)(ii) (it would ADMIT the F-4 package on the
readback-emptied copy despite the checker's failure, where (d1)(ii) requires a refusal) and
AD-1(d2)(ii) (it would ADMIT despite one gate image's checker failing on the emptied
read-back list, where (d2)(ii) also requires a refusal naming that image) — because
W-IGNORE's rule never reads the checker's exit status at all. W-STRICT fails AD-1(d2)(i)
**as worded** (it never admits anything, so it cannot satisfy (d2)(i)'s admission
requirement), independent of whether (d2)(i)'s premise is ever reachable — a wrapper is
judged against the stated requirement, not against whether that requirement's premise can
occur.

**Delivered-code cross-check** (read as text, no import). `r4_run_wrapper.py`
`r7_gate_packages` (lines 210–226) implements RB-4 as two independent ANDed conditions:
```python
if r.get("run_status") != "completed_valid" or r.get("gate_pass") is not True:
    ref.append(...)                                          # RB-4 (a)
v = checker_verdict(g)
if v["exit_status"] != 0 or v["verdict"] != "PASS":
    ref.append("R-7 (RB-4 (b)) the r4 checker on gate package %s: exit %s verdict %s; stop %s" ...)  # RB-4 (b)
```
This confirms the **delivered** code is neither W-IGNORE nor W-STRICT — it genuinely reads
the checker's exit status and verdict — grounding the discrimination premise in real code
behaviour, not only in the amendment's prose.

**Other wrong wrapper.** A wrapper reading ONLY the frozen checker's exit (ignoring the
r4-specific REG-1 items) would see `frozen_checker_exit=0` on the (d1)(i) original copy
(confirmed above) and so would **admit** there — but (d1)(i) is part of "THE REFUSAL BRANCH"
and requires a refusal. This alternate wrong wrapper fails (d1)(i) itself; it does not pass
both (d1) and (d2). No other-wrong-wrapper candidate passes both.

---

## AJ-3: neutrality

**Verdict: HOLDS.**

| rule | scope |
| --- | --- |
| AD-1 | development worlds only (scratch, never a package); explicitly never a gate package, result, or comparison basis |
| AD-2 | stage conduct after a STOP condition (procedural; no package verdict logic) |
| AD-3 | paths, id minting, binding-hash count, ceiling count (administrative; no verdict logic) |
| AD-4 | one inference-block metadata key, content unchanged from the frozen v2/r3 wrapper ("That key selects no provider, backend, endpoint or model identifier") |
| AD-5 | (a) note disclosure, report-only, "exit statuses unchanged"; (b) a NEW restriction (no outer guard unless declared) that can only REMOVE a class of interference, not add one |

**RFR-1/RFR-2 applied to the difference:** RFR-1 (no fail-open) — searched for a package
that should FAIL being admitted/PASS instead: none found (AD-1's outcomes are all explicit
non-package development observations; AD-2/AD-3/AD-4 touch no verdict-computing path,
cross-checked for AD-4 against the delivered `r4_run_wrapper.py`'s `inference_block()`,
whose key content is unchanged). RFR-2 (no planned-basis refusal) — searched for a
planned-basis outcome receiving FAIL by design under the difference: none found. Both name
nothing new.

### O-1: can a child that execs be reached by the ESRCH path?

**Answer: NO.**

`v2_solver.py`'s `_run_child_locked` (lines 175–236, read as text): the CHILD reaches
`os.execve`/`os.execv` only after `os.read(go_r, 1)` unblocks; the PARENT writes the go byte
only **after** it has already read the child's `"OK ..."` report to completion (a blocking
read loop) and optionally opened the hardware perf counter. childend RGL-1
(`v2_addendum_childend.yaml`) states: *"the after-fork-in-parent callback runs in the
parent after fork() returns and before os.fork() returns"* — CPython guarantees the RG-1
callback (which opens the software task-clock counter targeted at the ESRCH-vulnerable
window) completes **before any** of the parent's post-fork code, strictly before the parent
could reach the point of sending the go byte. Any child that reaches the go-byte wait (a
precondition for exec) is therefore guaranteed to already have the callback's counter
opened. The ESRCH race is confined to children terminating via `os._exit(97)` (setrlimit
failure) or `os._exit(98)` (hard-limit mismatch, line ~199–201) — **both before the go-byte
wait**, i.e. before the child's fate depends on the parent at all. Corroboration: the r4
note's D-9 deviation records that the DV-18(f)(xx) stand-in for a returncode-98 exit needed
an **artificial 1.5s delay** specifically *"so that the parent writes its go byte first"* —
confirming that without deliberate delay this pre-go-byte path genuinely can race the
callback, while an exec-bound child cannot. Note O-1 itself records the ESRCH path was
observed only in (f)(ix) (pre-go-byte `os.open` failure) and object O29b's gp child (also
pre-go-byte), never in an exec case.

**Consequence for AJ-3:** a planned, legitimate exec outcome cannot FAIL via the ESRCH/
`undetermined` route as a side effect of RG-1's timing; RG-1 (unchanged by AD-1..AD-5)
introduces no fail-open or planned-basis-refusal risk on this axis.

### LKA-7(b): does the RL-5 read-back load lie within "the RL-1 installation"?

**Answer: YES.**

`r4_recorder.py` (read as text): line 447 (`orig = v2_solver_module.run_child`, inside
`install()`) is the capture load; line 475 (`attr = getattr(v2_solver_module, "run_child",
None)`, inside `readback()`) is the RL-5 read-back load. Both `install` and `readback` are
functions defined in `r4_recorder.py`, the file that implements RL-1 end to end — "the RL-1
installation" as the r4 note's own §12 table names it. No other load of the frozen
`run_child` object exists in the delivered r4 tree (the note's LKA-7 closure scan lists
exactly these two loads, both in `r4_recorder.py`). LKA-7(b) holds.

**Conclusion:** no production predicate, verdict, admission, computed/recorded value,
frozen byte, argv, or envelope changes under AD-1..AD-5. HOLDS.

---

## AJ-4: re-issue consistency

**Verdict: HOLDS**, with one item count-verified but not exhaustively pairwise-verified
(disclosed below).

| check | claim | result |
| --- | --- | --- |
| eighteen hashes | 17 `bound_hashes` + admitdev's own `addendum_sha256` | PASS — all 17 verified byte for byte above; the 18th is admitdev's own hash, verified in (a) |
| 204 retired ids | union of `bea197` R-8 (124) + `1ce186` R-5 (38) + `minted-run-ids.txt` (42, from the file) | PASS (count); duplicate-freedom PARTIALLY verified (see below) |
| 6 existing packages | RUN-GFPN-ac4487, -3377f1, -f6a21a, -902222, -f5412a, -bfe956 | PASS — all six directories confirmed to exist |
| 48 over twelve plans | 6 existing + 42 reserved = 48 | PASS (structural/arithmetic; 8→10→12 plan-count progression consistent with the amendment lineage) |
| ten forbidden task ids | RB-6(d)'s eight + AD-3(d)'s two | PASS — matches this card's own CRA-8 list of exactly ten ids |

```
$ wc -l experiments/EXP-GFPN-05ff43/implementation-v2-r4/minted-run-ids.txt
42
$ sort -u experiments/EXP-GFPN-05ff43/implementation-v2-r4/minted-run-ids.txt | wc -l
42
```
`DEC-20260924-bea197` line 933: *"124 retired in all"*. `DEC-20260924-1ce186` line 1004:
*"38 added; 162 in all (R-5)"*. 124+38=162, +42=204. **Arithmetic PASS.**

**Disclosed scope limit:** duplicate-freedom of the full 204-id set was NOT independently
re-derived by extracting and pairwise-comparing all individual ids from the two decision
files' R-8/R-5 blocks (both files exceed 1000 lines and do not carry the id lists as a
single grep-able block within this review's budget). The reviewer instead relies on the
id-minting process's own `--check` step (42/42, 0 occurrences against all prior sets, per
`implementation-v2-r4.md` §0, 04:01Z–04:02Z) and DV-6's exhaustive 217-id sweep (162 retired
+ 42 frozen + 42 r3 + v1 ids, each refused with an id-class reason).

---

## Deviations

- **DEV-1.** DP-5's "54 run directories" required `-mindepth 1`; a naive `find ... -type d`
  returns 55 (it also matches `runs/` itself). Methodological note, not a finding.
- **DEV-2.** `DEC-20260924-e52eec` (2244 lines) was not read in full; only lines 1–815
  (containing VA-4, CRA-9's normative content) plus the `bound_hashes` block were read.
- **DEV-3.** AJ-4's retired-id duplicate-freedom check is count-verified, not
  pairwise-verified from primary text (see AJ-4 above). No working-context compaction
  occurred during this review (CRA-5's recovery rule was not exercised).
- **DEV-4.** One block of 32+ extended DV-18 sub-items was reported as a feasibility-witness
  group rather than independently re-derived item by item.
- **DEV-5.** Per CRA-7, the vendor-service word the AD-4 inference-block key names is never
  written in this report; referred to only as "the AD-4 key" throughout. No automated
  word-list self-check script was written; the reviewer manually avoided the word and
  re-read this file before writing it to confirm.

---

## Red team report

```yaml
red_team_report:
  id: TASK-20260925-5842cf
  task_id: TASK-20260925-5842cf
  claim_under_review: >-
    DRAFT AMD-EXP-GFPN-05ff43-20260925-admitdev: that AD-1's replacement of readbackcover
    RB-5(d) makes every development predicate of the successor r5 stage satisfiable by a
    correctly-delivered layer, that AD-1 discriminates W-IGNORE and W-STRICT wrong
    wrappers, and that AD-1..AD-5 change no production predicate or computed value.
  objections:
    - AD-1(d2)(i) (the admitting branch) is UNSATISFIABLE in every development world the
      texts permit, for the same structural reason that already made RB-5(d) literal and
      RF-4(c) first-worded unsatisfiable — a break the draft's own text anticipated with a
      pre-declared alternative, but a break nonetheless; ADR-1 treats every OTHER
      unsatisfiable predicate as fatal to approval-as-written.
    - The toy-G2 SSF "expected failure" designation (D-5), reproduced identically across
      the r3 and r4 stages, rests on Executor judgment rather than a numbered rule in
      RF-4(b)'s enumerated expected-refusal list.
    - One block of 32+ extended DV-18 sub-items was reported as a feasibility-witness group
      rather than independently re-derived item by item — the weakest evidentiary tier
      this review used for any predicate.
  required_controls:
    - Before any r5 stage relies on (d2), the approving act should record whether it is
      applying the pre-declared alternative (delete (d2), adopt RDL-1) or asserting a
      different satisfiability derivation than this report's.
    - A future review with more budget should independently re-derive the CX-A/CX-B
      discriminating controls and the RH-6(i)(19)-(20) count-gap items from raw bundle
      records, the way this review did for (d1)/(d2) and the AJ-0 mechanism.
  counterexample_or_mutation: >-
    The known-answer control (AJ-0) is the counterexample-search method applied to two
    already-known-broken predicates; it flags both correctly. The (d2) finding was
    produced by applying the SAME method, unprompted, to a THIRD predicate (AD-1's own
    new text) and finding it fails by the identical mechanism.
  baseline_comparison: null
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges: []
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    Under CRA-1..CRA-9 static reading only: AD-1(d1)'s refusal branch is satisfiable and
    discriminating, independently confirmed against primary bundle evidence; AD-1(d2)'s
    admitting branch is unsatisfiable as literally worded, a finding the draft's own text
    already anticipated and pre-answered; AD-2 through AD-5 are neutral on every
    production predicate this review checked; the draft's discrimination and
    reissue-consistency claims hold on independent re-derivation. This is an observation
    about the draft's text and the preserved r4 record, not a statement about D,
    H-GFPN-9a29be, or HEUR-GFPN-DFLAT.
  next_concrete_action: >-
    The Coordinator's approving act applies ADR-5, ADR-0, ADR-1, ADR-2, ADR-3, ADR-4 in
    order to this report and the draft; ADR-1's own text already names the disposition for
    an unsatisfiable (d2): apply the pre-declared alternative or record a different
    derivation.
  artifact_paths:
    - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/review-report.yaml
    - coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260925-5842cf/review-report.md
```

---

## Review attestation

- **Joints owned:** AJ-0, AJ-1, AJ-2, AJ-3, AJ-4 (single reviewer).
- **Sibling reports:** `TASK-20260924-d897a6` and `TASK-20260924-1ecb7d` were read as
  INPUTS (per the card), not as sibling reports of this round.
- **`blind_from` files not opened:** `DEC-20260925-8b2bf7.yaml`, `CORR-20260925-ee6929.yaml`,
  `TASK-20260925-5ad812.yaml`, `TASK-20260925-3bd499.yaml` (handoff), `KN-TECH-c9dcd5.md`,
  `KN-TECH-d45927.md`, `KN-TECH-fe7faf.md`, `ledger/goals/GOAL-GFPN-380702/goal.yaml`.
- **Paths read:** see `review-report.yaml`'s `review_attestation.paths_read` for the full
  list; principal sources were `v2_addendum_admitdev.yaml` (full), the fourteen other
  incorporated amendment files (readbackcover, childend, failclosed, readbackclose,
  readbackfull, gapattr, attcount, launchkind, and the earlier five), `DEC-20260924-daf670`
  (`bound_hashes` block), `DEC-20260924-e52eec` (lines 1–815), `CORR-20260924-19154c`
  (full), `TASK-20260924-d91a96.yaml` (R4S-7..R4S-13), `implementation-v2-r4.md` (full, 761
  lines), targeted reads of `r4_recorder.py`, `r4_run_wrapper.py`, `v2_solver.py`,
  `r3_run_wrapper.py`, `r3_check_run.py`, three members of the preserved DV-18 bundle
  (member-hash-verified against `MEMBERS.sha256`), and the archive/preservation receipts.
- **Commands (exact argv):** `sha256sum` over each hash-bound file; `git rev-parse HEAD`;
  `git branch --show-current`; `git status --short`; `git log --oneline -5`; `git log
  --oneline -1 origin/main`; `find experiments/EXP-GFPN-05ff43/runs -mindepth 1 -maxdepth 1
  -type d | wc -l`; `find experiments/EXP-GFPN-05ff43 -maxdepth 1 -iname '*r5*'`;
  `python3 -B <scratch>/verify_f0b9f0.py` (script reproduced above, written to a scratch
  file and run by path); `tar -tzf .../stage-r4-dv-evidence.tar.gz`; `tar -xzf
  .../stage-r4-dv-evidence.tar.gz -C <scratch> <three explicit member paths>`; `sha256sum`
  over the extracted members, compared against `MEMBERS.sha256`; targeted `grep -n` over
  amendment/decision files; `ls`/`find` over `RUN-GFPN-bfe956/`. No `python3 -c` or heredoc
  program was used; every script was written to a scratch file first. `GIT_OPTIONAL_LOCKS=0`
  for every git child.
- **Budget:** the review completed within the 43200s advisory checkpoint; no joint was cut
  short by budget.
- **Verdicts summary:** AJ-0 holds; AJ-1 breaks (one predicate, `AD-1(d2)(i)`; the draft's
  own pre-declared alternative applies); AJ-2 holds; AJ-3 holds; AJ-4 holds.

## Inference

```yaml
inference:
  requested_policy: review-adversarial
  resolved_model_id: null
  resolved_model_note: "none supplied by the dispatching session; none invented"
  fallback_used: false
  degraded_allowed: false
  bedrock_used: false
```

Observations only. No approval recommendation.
