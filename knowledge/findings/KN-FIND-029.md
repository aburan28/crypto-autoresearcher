---
id: KN-FIND-029
type: internal_finding
title: Five false-green escapes across three repairs of one mutation control; coverage
  escapes are closable by construction, evasion escapes are not closable by an
  in-process instrument
tags:
- mutation-testing
- false-green
- coverage-escape
- observability
- trusting-trust
- harness-integrity
- instrument-design
- experiment-design
- methodology
- controls-before-belief
- scoped-negative
- aes
- toy-scale
confidence: reported
internal_refs:
- EV-AES-003
- DEC-20260731-026
- EV-AES-002
- DEC-20260731-025
- EV-AES-001
- DEC-20260731-011
- RQ-AES-001
- TASK-20260801-802
- TASK-20260801-804
- TASK-20260731-705
proof_status: derivation
proof_refs:
- coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-802/mutation_control_v3.py
- coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-802/repair_receipt_v3.json
- coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-802/repair_report_er6.md
- coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-804/er6_closeout_review.md
- coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-804/validation_report.yaml
- coordination/goals/GOAL-AES-001/batches/BATCH-002/tasks/TASK-20260731-705/harness_repair_review.md
added: 2026-08-01
superseded_by: null
---

## Why this entry exists

A **false green** is the dangerous direction of instrument failure: a mutation
control returns `verdict: pass` on a module that is demonstrably wrong. This
program built one such control, repaired it three times, and each repair
produced the next instance of its own failure class. The count is **five escapes
across three repairs**, two of them produced by an independent session in one
sitting with no privileged knowledge, and two of them live in the instrument as
committed.

The entry exists because the pattern is **not specific to AES** and not specific
to this campaign. Any campaign in this program that builds a mutation control to
certify a measurement faces the same design choice, and the error is one a
reader who has not made it yet would plausibly make: treating "we closed the
escape we found" as progress toward "no fault escapes".

Produced under `GOAL-AES-001` (question `RQ-AES-001`), in BATCH-002 and
BATCH-003, and promoted by `DEC-20260731-026` on `EV-AES-003`. The goal ID is
named in prose rather than in `internal_refs` because `GOAL-*` records are not
registered in the validator's ledger ID index (`tools/validate_ledger.py`,
`LEDGER_DIRS`).

**This entry contains no claim about AES.** See "Non-claims" below, which is
load-bearing rather than boilerplate.

## The instrument

`mutation_control_v2.py` / `mutation_control_v3.py`: a mutation control that
(a) computes reference ciphertexts in the parent process, (b) writes each mutant
into a scratch directory, (c) executes it in a subprocess through a shared
runner script that imports it under the fixed module name `mutant_under_test`,
handing the runner the module path, a tasks JSON and an output path on
`sys.argv`, and (d) scores a mutant `detected` iff
`comparisons_executed > 0 AND divergences > 0`. Tasks are an **enumerated grid**
over (key length x final_mix_columns x round count).

## The five escapes

Each is an existence demonstration, reproducible from recorded commands. Every
faulted module was independently confirmed wrong by direct ciphertext comparison
**before** the control was run.

| id | found by | route | outcome |
|---|---|---|---|
| **ER-6** | BATCH-002 validator (TASK-20260731-705) | coverage: `build_tasks()` generated `final_mix_columns=True` only for 16-byte keys | full green on a module wrong for `fmc=True` with 24/32-byte keys |
| **ER-7** | BATCH-003 producer (TASK-20260801-802) | evasion: the module reads its own `__name__ == "mutant_under_test"` and hides | full green |
| **ER-8** | BATCH-003 producer | evasion across the process boundary: the first mutant rewrites the **shared runner** it is handed on `sys.argv[0]`, so later mutants are stripped of their fault before `exec_module` | full green; detected only because v3 added a runner-integrity digest, and **not prevented** |
| **V-804-4** | BATCH-003 validator (TASK-20260801-804) | coverage: a fault confined to `(fmc=True AND r = Nr)` — `build_tasks()` sets `final_mix_columns=False` on **every** full-round task, so the cell is **empty by construction** | full green on a module wrong in 3 cells at 4/4 vectors each |
| **V-804-5** | BATCH-003 validator | evasion: a cloak keyed on `os.path.basename(sys.argv[0]) == 'mutant_runner.py'` rather than on `__name__` | full green on a module wrong in 4 cells |

ER-6 was the H-3 failure shape recurring **inside the repair for H-3**. V-804-4
is ER-6's shape recurring inside the repair for ER-6, on the adjacent axis of
the *same two-factor table*. V-804-5 is ER-7's shape recurring immediately after
ER-7 was named, through a different channel.

**Strongest channel identified and deliberately NOT run:** a mutant that reads
`sys.argv[2]` — the tasks JSON the runner is handed — and disables its fault on
exactly the `(key, plaintext, rounds, fmc)` tuples that will be compared. That
defeats **any finite task set**, including a corrected one, and no widening of
coverage addresses it. Named, not demonstrated.

## The structural reason, and the three-part decomposition

The reason the class keeps producing instances is **structural, not inductive**:

1. Each repair closes **one cell** of an open-ended product of axes
   (`key length x fmc x round regime x direction x r>Nr x components x
   key/plaintext value space`) or **one channel** of an open-ended observation
   set (`__name__`, `argv[0]`, `argv[2]`, environment, `/proc/<ppid>/cmdline`,
   cwd, module search path, the writable runner file). Enumeration against an
   open-ended set does not converge.
2. The adversary model is **strictly stronger than the instrument**. The mutant
   is an ordinary child process holding the harness's own inputs on its command
   line, so any test that runs the object under a *distinguishable* condition
   can be evaded by an object that reads the condition — and each added check is
   itself observable. This is the standard trusting-trust / observer-dependence
   shape.
3. The empirical pattern matches: a defect class whose next instance is cheap to
   find after each repair is not being exhausted.

The useful decomposition is into **three** kinds of property, not one:

- **Closed properties of the scoring core are meetable and were met.** "The only
  route to `detected: true` is `comparisons_executed > 0 AND divergences > 0`,
  and every error path returns `detected: false` with
  `infrastructure_outcome: true`" is a closed property of one function,
  verifiable by inspection over a finite code path. Eleven independently
  authored injection shapes across two batches failed to move it.
- **Coverage escapes are closable BY CONSTRUCTION, not by enumeration.** Derive
  the task set from the module's **own declared parameter domain** rather than
  from a hard-coded grid, so that "cell not generated" is impossible by
  construction. Enumerating one more axis after each escape is the method that
  produced ER-6 and V-804-4.
- **Evasion escapes are not closable at all by an in-process instrument against
  an adversarial module.** Running the comparison under conditions
  *indistinguishable from ordinary use* (ordinary module name, ordinary `argv`,
  ordinary cwd, no harness-shaped paths) removes the cheap tells and is worth
  doing, but an object able to read anything about its environment can in
  principle be made evasive. The honest handling is to **declare the evasion
  class out of the threat model**, on a stated ground — e.g. that the module
  under test is committed, readable and non-adversarial — and to write that
  declaration into any certificate that relies on the instrument.

## Practice rules this yields

1. **A green states the covered cells, or it states nothing.** Write the
   coverage boundary into the machine-readable receipt, computed by the control
   from the task set it actually generated, not inferred from the loop that
   generates it. A boundary that is not written down will be assumed wider than
   it is.
2. **Prove a repair by executing it, never by reading the new task set.** The
   ER-6 close-out was accepted because an independently authored fault, confirmed
   real by ciphertext comparison, was detected through an **executed comparison
   that diverged** (212 executed, 24 divergent) and through no exception path.
3. **Check the widened control is not vacuous.** A task set that fires on
   everything makes its own detections meaningless. The semantics-preserving
   no-op mutant must score `detected: false` **after a nonzero number of
   executed comparisons**.
4. **Confirm an injected fault with multiple random vectors, never one
   structured vector.** A structured key/plaintext can whiten to a constant
   state, on which AES MixColumns is the identity (`02^03^01^01 = 01`), hiding a
   real fault completely. This was hit in practice.
5. **Confirm faults through a runner that imports under the module's ordinary
   name.** Any confirmation sharing the control's import name is blind to the
   ER-7 class by construction.
6. **A null control must isolate the property it names.** The adjacent lesson
   from the same batch (`EV-AES-003` A-10): a redesigned falsification gate
   discriminated, yet an equally admissible *sibling* null — the same selection
   rule applied to the other proper subgroup — negated the same named ingredient
   and read identically to the target. Build the sibling null before believing
   the label. This is the sharpened form of KN-FIND-028's rule that a null built
   by negating a *sufficient* hypothesis is not automatically discriminating.
7. **Absence of evidence is not evidence of absence.** The ER-8-restore
   conjecture (tamper the shared runner, then restore its bytes at exit to defeat
   the integrity digest) is **unresolved**: the probe was confounded, and a
   matching post-run digest is consistent both with "the tamper never landed" and
   with "the tamper landed and was perfectly reverted".

## Reproduction

```
python3 coordination/goals/GOAL-AES-001/batches/BATCH-003/tasks/TASK-20260801-802/mutation_control_v3.py \
    --module <faulted copy of aes_reduced.py> --repo-root <repo> --out receipt.json
```

Fault injections for ER-6, ER-7 and ER-8 are selectable in the committed control
via `--fault-injection`; the v2 coverage width is reproducible behind
`--fmc-coverage legacy`, which returns the ER-6 false green from the same
artifact. V-804-4 and V-804-5 were written by the validator in its own text and
are transcribed verbatim in `er6_closeout_review.md` sections 5 and 6.1. All
seeds are recorded in `repair_receipt_v3.json`; the control is deterministic
across invocations (`determinism_rerun_digest_matches: true`).

## Non-claims — read this before citing

- **No claim about AES of any kind, at any round count.** Nothing here is a
  distinguisher, a key recovery, a complexity claim or a barrier statement. A
  mutation control is an instrument; facts about it are reproducibility facts
  about that instrument and about nothing else.
- **No fault in the module under test was found by anyone.** Every fault
  discussed here was deliberately injected in order to test the instrument.
  Nothing here says `aes_reduced.py` is wrong.
- **The five instances are established; the generalisation is a reasoned
  judgement.** "H-3 is not meetable by enumeration with an instrument of this
  design" is supported by five measured escapes from two independent sessions
  and by the structural argument above. It is **not a proof of impossibility**,
  and it is not a statement about mutation testing in general beyond the
  instrument and threat model described here. `confidence: reported` refers to
  exactly this split.
- **Not a retroactive invalidation of anything.** No scored mutant in BATCH-002
  or BATCH-003 exercised any evasion route — the mutants are committed, readable,
  and contain neither construction — so every scored observation stands exactly
  as recorded. What narrows is the inference a reader may draw *from* a green,
  not the green.
- **The three-part decomposition is a design recommendation, not an enacted
  protocol change.** `DEC-20260731-011`'s certification condition stands
  undischarged as written; restating it requires
  `protocol-amendment-GOAL-AES-001-004`, prospective and never retroactive.
- **`proof_status: derivation`**, copied from `EV-AES-003` and never exceeding
  it: reproducible empirical demonstrations plus a checkable written argument.
  Not machine-checked proof.
- **Independence is in SESSION and not in MODEL.** Under inference-amendment
  `0137a051` every producer, the validator and the Coordinator resolve to the
  same model, so the agreement between them is correlated. No goal-closure
  attestation rests on any of this work.
- **No literature was consulted and no novelty is claimed.** The
  observer-dependence shape is elementary and the honest expectation is that it
  is well known. No primary source is reachable under this campaign's network
  policy, so novelty is **unresolvable** in this environment.
