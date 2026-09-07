# Independence check — BATCH-e15a65

- **Task**: TASK-20260907-175a4a (Coordinator) · **Goal / question / batch**: GOAL-ECRANK-002 / RQ-ECRANK-27dcc5 / BATCH-e15a65
- **Frozen plan**: `ledger/decisions/DEC-20260907-9953c0.yaml`, `review_plan.plan_id: REVIEW-PLAN-BATCH-e15a65`, `blindness.mutual: true`, `blindness.lifted_for: []`, `procedure_deviations: []` at freeze
- **Purpose**: record how far this round actually rested on the independence it claims, and preserve every disclosed deviation by name rather than smoothing it. The plan's own `procedure_deviations_note` puts this duty here: *"A review protocol that is silently deviated from is worth less than one that was never declared, because it still reads as rigorous."*
- **Authority**: a draft record. It changes no status and asserts no attestation that was not obtained.

---

## 1. The tool result, and exactly whose result it is

**I did not run the tool.** Under this runtime the Coordinator subagent holds no command-execution tool. The orchestrating session ran it and reported the result, which is recorded here as reported and attributed to that session:

```text
python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260907-46731e.yaml \
  --reports coordination/goals/GOAL-ECRANK-002/batches/BATCH-e15a65/tasks/
```

**Reported result: PASS — 2 reports; every joint owned and attested; blindness respected; controls declared.**

Also reported by the orchestrating session and relied on here:

- `tools/research_dispatch.py … --claims refs` renders a valid plan with `TASK-20260907-175a4a` the single Ready Task and all gates passing.
- Both reviewer tasks are `completed` in the queue with their claims released, and both reports are committed.

**Three honest qualifications on that PASS, stated rather than assumed away.**

1. **It was run against a binding copy, not the authoritative block.** `--plan` names `ledger/handoffs/TASK-20260907-46731e.yaml`. `DEC-20260907-9953c0.review_plan.binding_copies` declares the two handoff copies as copies and the decision block as authoritative, and its `binding_copies_note` says a copy that abbreviates a joint it does not own "points here and adds nothing". The Red Team handoff is therefore the copy that abbreviates **J1–J4**. So the check exercised the joint-ownership graph as written in a copy whose J1–J4 entries are abbreviations.
2. **Plan-copy equivalence was verified — by one of the reviewers, on its own binding.** The Validator read the authoritative decision **last of everything**, solely to compare it field by field against the copy embedded in its own handoff, and reports them identical on every binding field (`claim_under_review`, `coordinator_prior`, `blindness`, `blind_rederivation.{quantity, parameters, blind_from, blindness_limits}`, `procedure_deviations`, and the `attack_plan`/`breaking_artifact` of J2, J3, J4), with two benign divergences: the handoff copy adds a strict-superset clause to J1's attack plan (the explicit ban on `seed*1000 + index` derived seeds, which it then checked and reports clean), and the decision copy adds one explanatory sentence to `read_order_requirement`. That is a careful check, and it is **self-reported by the party bound**. No independent agent verified copy equivalence for the Red Team handoff.
3. **Nothing in the tool's PASS can see content.** It checks the *shape* of the round — owned joints, attestations, declared sources, non-intersecting `blind_from`. It cannot see whether a verdict was revised after a disclosure, and §3.1 turns on exactly that.

## 2. What the round's independence actually consisted of

- **Two mutually blind reviewers, disjoint joints, one owner each.** J1–J4 to `TASK-20260907-d47eb0` (Validator), J5–J7 plus the `proves_too_much` control to `TASK-20260907-46731e` (Red Team). No joint has two owners; no joint has none. Each report states, unprompted, that it returns **no whole-claim verdict** because it cannot see the other joints by construction — which is the behaviour the plan's design intends and the one most easily violated.
- **Both ran `review-adversarial` at xhigh in fresh independent sessions**, `fallback_used: false`, `degraded_allowed: false`, Bedrock guard negative. Neither tier was downgraded and neither report changed any status.
- **Both bound to the same snapshot**, `03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad`, and both verified the binding independently — the Validator by recomputing the receipt's 60 `path_sha256` (60/60) and by `git diff --stat 03c6e3181..HEAD` being empty; the Red Team by the same empty diff, checked twice.
- **Disjoint write scopes**, two files each under their own task directory; neither committed anything.
- **The plan's two structural controls were both run**: the `proves_too_much` control against all three declared objects with the declared failure signature (Red Team), and the `blind_rederivation` with a declared read order (Validator).
- **The declared `blind_from` set held.** `source/**` and `implementation.md` were never opened by the Validator. Two contacts are disclosed precisely: a directory walk returning eight `.py` **names**, and SHA-256 digests of those eight files compared against `run.code.source_sha256` (8/8), performed **after** the blind Part A was already written to disk. A digest carries no implementation content, and the check is the artifact-binding duty `agents/validator.md` responsibility 1 imposes.
- **The round produced a genuinely overturned Coordinator prior** — item (8), the one the plan named as the one it would most like overturned — and a factual correction to item (9) from **both** reviewers independently. A round that only confirms a recorded prior and a round that can overturn it look identical afterwards; this one overturned it, which is evidence that the independence was operative and not decorative.

## 3. The disclosed deviations, preserved and named

Four are recorded. The plan froze `procedure_deviations: []`, so all four are recorded here for the first time, as the plan requires. None is a violation of the blindness contract as written; each is a place where the round is weaker than the plan's design intends, and each is stated with what it could and could not have contaminated.

### PDR-1 — Incidental sibling exposure: each reviewer's final repo-wide `git status` surfaced the other's FILENAMES

**What happened.** Both reviewers ran a repository-wide `git status` at the end of their tasks — a completion-gate obligation, to confirm they had written nothing outside their write scope and had committed nothing. Because both task directories were untracked, the listing printed the sibling's paths.

- The **Validator** saw two names: `.../TASK-20260907-46731e/redteam-report.md` and `.../review_attestation.yaml`. Its attestation records this under `incidental_sibling_exposure` with `occurred: true`, `disclosed_rather_than_absorbed: true`, and states both deliverables were already written and all four verdicts already fixed; both files were absent from the tree throughout the analysis.
- The **Red Team** saw one name: `.../TASK-20260907-d47eb0/validation-report.md`, after `redteam-report.md` "was already written". Its attestation records this under `read_sibling_reports_attestation` with the reason: *"an attestation that says 'did not list' must be literally true, and a whole-repository status listing is a listing."*

**What it could NOT have contaminated.** Any content. Neither file was opened, read, diffed, grepped, hashed or inferred from; no byte of either entered the other session. `read_sibling_reports: false` is honestly false in both attestations, and the exposure is post-hoc in both — the Validator's after both deliverables were written, the Red Team's after its report was written.

**What it could in principle have contaminated.** Two things, both about the *existence* of the sibling rather than its content: (i) knowledge that the other reviewer had finished, which could create pressure either to conform or to differentiate; and (ii) an opportunity to revise a verdict already written to disk. A filename is not a finding, and neither exposure carried a verdict, a number, or a direction. But note the asymmetry the Validator itself points out: because the sibling files were present at its final check and absent throughout its analysis, it learned that the Red Team **finished first**. That is a scheduling fact, it confers no authority, and it did not reach either report — and it is exactly the sort of thing that must be written down rather than judged harmless by the party who saw it.

**The limit I state plainly.** Whether a file was revised between being written and being committed is **not independently detectable from the tree**. The claim that no verdict changed after the exposure rests on the two attestations alone. I accept it: both reviewers volunteered the exposure unprompted when neither had to, which is the behaviour of agents disclosing rather than managing, and their reports contradict each other's framing in one place (§C.4 of `composition.md`) and correct the same Coordinator prior from different premises in another — neither of which is what convergence under contamination looks like. **`blindness.lifted_for` stays `[]`; this was not a lift, and nothing in this round is treated as jointly reviewed.**

**Structural remedy for the successor**, so this does not recur as a matter of luck: give the completion-gate scope check a path filter (`git status --porcelain -- <own write_scope>`) rather than a repository-wide listing. A reviewer should not have to choose between verifying its write scope and preserving its blindness.

### PDR-2 — The J4 re-derivation was implementation-blind but NOT value-blind, and the Validator flagged it itself

**What happened.** The Validator raised this in section A.1 of its report, **before** opening anything, as a weakening the plan did not anticipate: *"The mandatory readings themselves quote the answer."* The handoff it is required to read first embeds the frozen plan, whose `coordinator_prior` item (8) and J4 `attack_plan` both quote *"the recorded 15 at 100, 22 at 1000, 28 at 10000, feasible_tuples 20 and feasibility_fraction 0.002"*; the second Coordinator prior repeats `{100: 15, 1000: 22, 10000: 28}` and `feasibility_fraction: 0.002`. The plan had declared a *different* weakening — a read order in place of true blindness for the producer's raw records (`blind_rederivation.read_order_requirement`) — and had not noticed that its own text leaks the target values.

**What it could NOT have contaminated.**

- **The negative finding itself.** J4's result is that `N_6(H)` is **not derivable** from the frozen contract. Knowing the target values makes reverse-engineering a matching convention *easier*, not harder; the reviewer nonetheless failed across **375** conventions (3 pool orderings × 5 stdlib generators × 25 burn-in offsets) to reproduce even the b-tuple at `b_index 579`. Value leakage cannot manufacture a failure to reproduce, so the finding is if anything strengthened by it.
- **The seven definitional gaps G1–G7**, which are statements about what the contract text does and does not define.
- **The committed falsified prediction.** The Validator committed a stream (first tuple `(0,1,4,−7,−1,−2)`, sha256 `b1e62603e999…fafeda`) before opening anything and recorded its falsification, 0/28 agreement.

**What it DID contaminate, stated precisely rather than at the convenient level.** Any reading of J4's agreements as *blind* agreement about the values.

- The `≤ 2 rational roots per tuple` ceiling (from the contract's own "single univariate quadratic" engine description) is **blind**.
- Its instantiation — *"28 ≤ 40, and at least 8 of the 20 feasible tuples must contribute two"* — uses the leaked 28 and 20 as inputs. So P-b's celebrated exact landing (the record shows **exactly** 8 tuples with two instances, 12 with one) is a check that the record is **internally coherent with a blind structural fact**, not a blind reproduction of the value 28.
- P-a (`20/10⁴ = 0.002`) and P-c (`15 ≤ 22 ≤ 28`) are arithmetic identities on leaked values; P-d's decade ratios likewise. All four remain useful, and none is blind agreement on the count.

The Validator says the same in its own words — *"I flag it rather than letting the round read as more independent than it was. This is a defect in the plan, not in the producer."* — and it is right on both counts. **Remedy for the successor**: a plan that requires a blind re-derivation must not quote the value in any mandatory reading; the target belongs in a sealed companion the Coordinator holds, not in the handoff.

### PDR-3 — `EXP-ECRANK-76a70d/` was outside the Red Team's read scope, so the predecessor non-transfer argument is made from one record

**What happened.** The Red Team discloses this under `sources_outside_scope_deliberately_not_read`: the predecessor experiment directory was outside its enumerated read scope and was not opened. Its answer to the earlier prior's proves-too-much requirement — *"a reading that proves too much about the predecessor is a defective reading"* — is therefore made from `ledger/evidence/EV-ECRANK-8b35bb.yaml` alone.

**What it could NOT have contaminated.** Everything the Red Team actually computed. J5, J6, J7, C-A, C-B, C-C and C-D are all read or derived from `experiments/EXP-ECRANK-73275e/` committed bytes at the snapshot plus the frozen contract; none of them depends on the predecessor package. The non-transfer argument's positive content is also independent of it, resting on two theorems tied to n = 6 and the all-ones pattern: (T1) is n-specific and the predecessor's known-false control ran at n = 8 and n = 10 (`EV-ECRANK-8b35bb certificate_refs` lists `kf-n8-b00..b19` and `kf-n10-b00..b19` and **no `kf-n6-*`**); (T2) concerns `construct.solve_n6`, which did not exist in the predecessor's draw route.

**What it leaves open, and I do not close it.** The conditional the Red Team states so it can be checked rather than assumed: *if* the predecessor's controls were also built on an object its counted path cannot produce, the same objection reaches it. That has **not been tested against the predecessor's own bytes**. The evidence visible from here points the other way — 1161/1161 plant recovery with a log-log slope 0.905 inside the frozen window is a control that plainly discriminated — but that is read off the successor's evidence record, not off the predecessor's runs. `EV-ECRANK-8b35bb` is untouched by this batch, and asking the question of it is next action **N5** in the closing decision.

**One related gap that is NOT scope-limited and does transfer.** `EV-ECRANK-8b35bb boundaries` already records that the multi-class certificate path "was exercised by NO certified instance anywhere in this experiment — all 58 certificates are single-class". Here 28 of 28 are 3-class and no control exercises the multi-class path at any n. So *"the multi-class certification path has never been controlled in this program"* is a two-experiment fact established from records both reviewers could see, not an artifact of PDR-3.

### PDR-4 — The plan's own designated strongest refutation artifact was not computable, and a substitute was used

**What happened.** J7's `attack_plan` ranks as item (i) — and the plan calls it *"the strongest refutation artifact this result admits"* — re-verifying the exhibited points of one recorded R3 instance against its Weierstrass equation in exact `Fraction` arithmetic and checking non-torsion by Mazur. The Red Team reports it is **not computable from the committed bytes**: `construct_arm` records only `{verdict, aggregate_total, n_classes, class_keys}` per instance (`construct.py:406–411`), so **no a-invariants and no curve points are persisted in any R3 artifact**. It ranked item (i) fourth on its own list, substituted C-B (full structural re-verification of all 28 from the raw ingredients `b`, `d_pattern`, `r`, `s`) plus C-C and C-D, ran three items, and stated exactly what a successor would need: persist `ainv_d` and the exhibited image points per class plus the Mazur witnesses, a small change at `construct.py:406–411`.

**What this means for the round.** The plan asked for the strongest refutation artifact and got the strongest **available** one. Under `docs/claims-and-verification.md` the R3 record carries **no re-verifiable solution certificate** — that is a finding about the package, not a shortfall by the reviewer. It is why `proof_status` on the composed evidence is `derivation` and not `certificate`, and why the successor design requirement above is ranked second in the closing decision.

## 4. Composed judgement on the round's independence

**The round rested on real independence, and it is weaker than the plan intended in two specific, disclosed places.**

Operative: seven joints, one owner each, no shared joint; two fresh xhigh sessions; one snapshot verified independently by both; disjoint write scopes; both structural controls run; `blind_from` held with two disclosed content-free contacts; and — the strongest single indicator — the round **overturned** the Coordinator prior the plan flagged as most wanting overturning, factually corrected a second from both sides independently, and produced two reviewers who disagree in framing on the R7 n = 6 question while agreeing on its operative consequence. That pattern is not what correlated reviews produce.

Weaker than intended: the J4 re-derivation was value-leaked by the plan's own mandatory text (PDR-2), so its agreements are internal-coherence checks rather than blind reproductions; and the predecessor non-transfer argument rests on one summary record (PDR-3). The two filename exposures (PDR-1) are disclosed, post-hoc, content-free, and rest on attestation for the no-revision claim.

**No lift is recorded and none occurred.** `blindness.lifted_for` remains `[]`; nothing here is treated as jointly reviewed; each verdict remains attributed to its single owner throughout `composition.md`.

**What this round does not license.** It is two reviews with three disclosed blindness deviations on a toy-scale run set whose primary positive control never evaluated. It is not a replication, not an independent second execution of the mechanism, and not a `review-breakthrough` round. It supports `inconclusive` with a specified repair; it supports no promotion, and IMP-2 and the UNPROMOTED C1-closure candidate of `DEC-20260905-7adca0` are untouched by it.

## 5. Carried into the record

- `composition.md` §C.4 states which reading the frozen text supports on the one framing difference.
- The closing decision draft carries PDR-1 … PDR-4 in its `procedure_deviations` block, since the frozen plan's own list was empty at freeze and departures are never quietly absorbed.
- The two structural remedies — a path-filtered completion-gate scope check, and keeping target values out of mandatory reviewer readings — are recorded as next actions owned by the Coordinator for the next review plan, not as findings about this one.
