# Independence check — pfdr-battery-20260904 composition (TASK-20260904-e6b4dd)

Gate G0 of TASK-20260904-e6b4dd requires the five
`tools/check_review_independence.py` invocations "with their verbatim output".

## THIS SESSION DID NOT RUN THE TOOL, AND NO OUTPUT IS REPRODUCED HERE

The Coordinator subagent executing TASK-20260904-e6b4dd holds Read, Grep, Glob,
Write, Edit and SendMessage only. It has **no shell and no interpreter**. It
therefore could not execute `tools/check_review_independence.py`, and AGENTS.md
rule 5 forbids reproducing output it did not obtain. Nothing below is the
tool's output, and nothing below may be cited as the tool's PASS.

What is recorded instead is a **manual re-performance of every check the tool
performs**, read off the five committed `review_plan` blocks and the ten
committed `review_attestation` blocks. That is weaker than the tool in exactly
one respect — a human reading can miss a string mismatch the tool would
catch — and stronger in one respect, noted at the end, where the tool's own
leak check is structurally unable to fire on one report.

The orchestrating session must run the five commands below before this round's
records are treated as verified, and must record their verbatim output.

```sh
python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260904-2bb29d.yaml \
  --reports coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-2bb29d \
            coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-6681da

python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260904-4c0d7d.yaml \
  --reports coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-4c0d7d \
            coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97

python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260904-642cf5.yaml \
  --reports coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-642cf5 \
            coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-ed0e8f

python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260904-a7eead.yaml \
  --reports coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-a7eead \
            coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3

python3 tools/check_review_independence.py \
  --plan ledger/handoffs/TASK-20260904-42b33a.yaml \
  --reports coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-42b33a \
            coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5
```

**The orchestrating Coordinator session states that it ran all five commands
itself, before dispatching this composition task, and that all five PASS with**
`10 report(s), every joint owned and attested, blindness respected, controls
declared` **against plans TASK-20260904-2bb29d, -4c0d7d, -642cf5, -a7eead and
-42b33a.** That result is recorded here as the **orchestrating Coordinator
session's**, attributed to it and not to this subagent, which did not execute
the tool and did not observe its output. The manual re-performance below is an
independent second reading of the same property, not a restatement of that
PASS.

## Manual re-performance, check by check

The tool checks seven things (its module docstring plus `check()`):
(1) `coordinator_prior` non-empty; (2) every joint has exactly one owner;
(3) each owner filed an attestation claiming that joint verbatim in
`joints_owned`; (4) each attestation's `verdict` is `holds|breaks|inconclusive`;
(5) no reviewer read sibling reports unless `blindness.lifted_for` names it;
(6) `proves_too_much.objects` non-empty with a non-empty `failure_signature`;
(7) when `blind_rederivation.required`, the re-deriver's `sources_read` does not
intersect `blind_from`, and `blind_from_respected` is explicitly `true`.

### (1) coordinator_prior

Non-empty and substantial in all five plans (2bb29d l.191-236; 4c0d7d
l.188-226; 642cf5 l.209-251; a7eead l.213-246; 42b33a l.232-292). Each names a
DECISION I EXPECT, which is what makes the confirmed/refined/overturned
comparison in each `review-analysis.md` possible.

### (2)-(4) joint ownership, attestation and verdict

| plan | joints | owners (each exactly once) | attested verbatim | verdicts |
| --- | --- | --- | --- | --- |
| 2bb29d (c04716) | V1-V3, R1-R4 (7) | V1-V3 → 2bb29d; R1-R4 → 6681da | yes, both | `holds` / `breaks` |
| 4c0d7d (fd901a) | V1-V4, R1-R4 (8) | V1-V4 → 4c0d7d; R1-R4 → 8c5f97 | yes, both | `holds` / `breaks` |
| 642cf5 (5726af) | V1-V4, R0-R4 (9) | V1-V4 → 642cf5; R0-R4 → ed0e8f | yes, both | `holds` / `breaks` |
| a7eead (20ee58) | V1-V4, R0-R4 (9) | V1-V4 → a7eead; R0-R4 → 0d66e3 | yes, both | `holds` / `holds` |
| 42b33a (cbdefb) | V1-V4, R0-R5 (10) | V1-V4 → 42b33a; R0-R5 → 3a2ff5 | yes, both | `breaks` / `breaks` |

No joint has two owners; no joint is unowned; every `assigned_to` filed a
report; every `joints_owned` list reproduces its plan's joint strings verbatim
(the reports say so explicitly — ed0e8f's `joints_owned_note` records "copied
verbatim from review_plan.joints"). All ten verdicts are in the tool's
vocabulary. Every `attack_plan` is non-empty.

Two notes that are NOT independence defects and are recorded so a reader does
not mistake them for one:

- 6681da's aggregate verdict is `breaks` while its per-joint results are
  R1 breaks, R2 breaks, **R3 holds**, R4 breaks. 8c5f97's is `breaks` with
  R1 holds, R2 breaks, R3 holds, R4 breaks. ed0e8f's is `breaks` with R0 holds
  and R1-R4 breaking at least one clause each. 42b33a's is `breaks` with
  V1 holds, **V2 breaks**, V3 holds, V4 holds. 3a2ff5's is `breaks` with only
  R1 breaking. An aggregate `breaks` is not a whole-experiment verdict; the
  composition is joint by joint.
- 42b33a's own `verdict` field inside `validation_report` reads `incomplete`
  while its `review_attestation.verdict` reads `breaks`. The tool reads the
  attestation, which is in vocabulary. The two are consistent in substance: the
  receipt is incomplete because joint V2 breaks.

### (5) blindness

All five plans set `blindness.mutual: true`, `lifted_for: []`,
`rationale: null`. All ten attestations set `read_sibling_reports: false`. The
tool's condition therefore does not fire anywhere.

Every one of the ten reports additionally discloses incidental exposure to
sibling **paths** — directory names from an `ls` or `git status`, and in three
cases a commit subject line naming another task's outcome (6681da saw
d3249e14's subject for 42b33a; 3a2ff5 saw a subject for 8c5f97; 0d66e3 saw
sibling directory names). In every case the report states that no sibling file
was opened and that its own findings predate the command that printed the name.
These disclosures are what a truthful attestation looks like; they are not
lifted blindness and the tool would not flag them, because the tool reads
`read_sibling_reports`, not prose.

The round-closure receipt records that several final reports were physically
swept into commits whose subject lines name a different task, by a broad
`git add -A coordination/reviews/`. That is an archiving artifact of a shared
worktree, disclosed by the reviewers themselves (6681da `worktree_events`,
8c5f97 `worktree_disclosure`, ed0e8f `worktree_disclosure`, 3a2ff5
`sibling_material_encountered` item 4). It bears on which commit holds which
bytes, not on independence. **The archiving session must re-stage and re-hash
the final working-tree content of all ten directories rather than rely on the
WIP snapshots**, as 6681da and ed0e8f both explicitly request.

### (6) proves-too-much

Present with non-empty `objects` and a non-empty `failure_signature` in all
five plans, and assigned to the red team in all five. All five red teams ran it
and reported per-object outcomes. Three of the five found the failure signature
present on at least one object:

- 6681da: fired on 3 of 4 objects (direct presentation under the bounded slice;
  m ∈ {3,4,5} with D_0 below the generator degree; D_0 = 2). Did not fire at
  m = 2, where the object is right.
- 8c5f97: fired on p = 2, on p = 3, on the positive control, and produced a
  PARTIAL SURVIVAL on the Wilson inclusion map W_{1,3} at p = 3 under the
  record's own entry-content operationalization.
- ed0e8f: absent on the three planned objects, present as designed on one added
  object (a non-tensor top form that re-produces d_ff = 5 with fall_dim 2).
- 0d66e3: fired on all three objects, and its generator-count extension is the
  load-bearing finding of that experiment.
- 3a2ff5: absent on objects 1-3, present as designed on object 4 (the s = 1
  saturated systems).

### (7) blind re-derivation

| plan | required | assigned_to | `blind_from_respected` | leak by inspection |
| --- | --- | --- | --- | --- |
| 2bb29d | false | null | `null` (correct; not a re-derivation task) | n/a |
| 4c0d7d | false | null | `null` (correct) | n/a |
| 642cf5 | true | TASK-20260904-642cf5 | `true` | none |
| a7eead | true | TASK-20260904-a7eead | `true` | none |
| 42b33a | true | TASK-20260904-42b33a | `true` | none by inspection; see the tooling note |

- **642cf5.** `sources_read` is a flat list containing no `blind_from` path. The
  blind_from paths (`runs/*/raw-result.json`, `runs/*/stdout.log`,
  `run_pfdr_5726af.py`) appear under a separate key,
  `paths_hashed_or_size_measured_without_reading`, with an explicit note that
  only match/MISMATCH and a byte count were printed. Phase boundary
  2026-09-04T02:15:12Z, `rederivation.yaml` sha256
  `2e96f2dc…e0c53` recorded at the boundary and unchanged at report time.
- **a7eead.** Same construction; the blind_from paths are under
  `hashed_not_opened` with the same rationale, stated as "listing them would
  report a blindness breach that did not happen, and omitting them silently
  would hide that the hashes were checked at all". Phase A read set was
  narrower than the plan permitted: no manifest was opened at all before the
  boundary. `rederivation.yaml` sha256 `c8bfc433…1be4ca`, written
  02:16:46Z.
- **42b33a.** Blind_from paths are under `hashed_but_not_opened`. Phase boundary
  02:34:03Z, `rederivation.yaml` sha256 `04a55734…1bc0c`.

**TOOLING NOTE, recorded because it changes what the PASS means.**
TASK-20260904-42b33a's attestation records `sources_read` as a **mapping**
(`phase_A:` / `phase_B:` lists) rather than as a flat list. `check()` does
`[str(p).strip() for p in (attestation.get("sources_read") or [])]`, and
iterating a mapping yields its KEYS, so for that one report the mechanical
leak check compares the plan's `blind_from` paths against the two strings
`phase_A` and `phase_B` and cannot match. The check does not crash and does
not warn; it silently has nothing to compare. For TASK-20260904-42b33a the
blind-ordering property therefore rests on the attestation, the phase-boundary
log and the hash of `rederivation.yaml`, and **not** on the mechanical check —
the same class of silent-pass defect recorded as PD-2 of DEC-20260901-e24d15.
This Coordinator performed the comparison by hand instead and found no
`blind_from` path in either phase list.

## Outcome for gate G0

Every check the tool performs is satisfied on all five plans by manual
re-performance, and the orchestrating Coordinator session independently reports
a PASS from the tool itself on all five. **No strength cap is applied and no
`procedure_deviations` superseding note is required on independence grounds.**
Two items travel with the round's records instead of being absorbed:

1. The five tool invocations were not executed by THIS session and their output
   is not reproduced anywhere in this file. The PASS recorded above is the
   orchestrating session's and is attributed to it.
2. The mechanical blind_from leak check is inert on TASK-20260904-42b33a for
   the structural reason above, so the PASS on that plan does not include a
   leak check. This Coordinator performed that comparison by hand and found no
   `blind_from` path in either phase list.

Recorded by the Coordinator subagent under TASK-20260904-e6b4dd, 2026-09-04.
