# BATCH-028 approval determination for EXP-SMTH-4403c4

Written 2026-08-02 by the Coordinator, AFTER the measurement ran. That ordering
is the defect this document records; it is not repaired by being documented.

## The defect, stated plainly, and it is mine

`experiments/EXP-SMTH-4403c4/specification.yaml` carries `status:
frozen_pending_approval` and `approved_by: null`. AGENTS.md reserves experiment
approval to the Coordinator, and no approval was recorded before execution.

The executor did not sneak past a gate. It executed on the authority the
contract itself names -- `execution_authorized_by: dispatch_card
TASK-20260802-6a39f8` -- and then flagged the gap in its own report as D1,
stating that without a Coordinator determination the run is not
evidence-eligible and that it could not cure that itself. That is exactly right,
and it is the second time in this session a producer has caught a Coordinator
defect I introduced.

THE ROOT CAUSE IS THE DISPATCH CARD I WROTE. The BATCH-028 queue made
TASK-20260802-80f5e9 freeze a contract and TASK-20260802-6a39f8 execute it, with
no task between them that approves it and no gate requiring approval. I built a
lifecycle with the approval step missing and then authorized execution through
it.

## What the missing approval does and does not put at risk

APPROVAL PROTECTS TWO DISTINCT THINGS, and they are not in the same condition
here.

1. INTEGRITY -- that the contract was fixed before any datum could influence it.
   THIS IS INTACT AND IS INDEPENDENTLY VERIFIABLE WITHOUT TRUSTING ANYONE'S
   ASSERTION:
   - the contract's sha256 `664e37a3...62eb6f` was recorded in
     `freeze_receipt.json` by a task that produced no datum, and recomputed to
     the same value by the executing task before its first datum;
   - `null_calibration.json` was written at 21:27:22Z and hashed, and the first
     treatment integer was constructed after the PHASE2_START stamp at
     21:27:48Z -- the null demonstrably preceded the treatment;
   - the Coordinator independently recomputed the contract hash and it matches.
   None of that depends on an approval record existing.

2. JUDGEMENT -- that the Coordinator considered the design worth running, that
   its scope is right, and that its rules can answer the question. THIS WAS NOT
   DONE BEFORE EXECUTION AND CANNOT NOW BE DONE PROSPECTIVELY. Any assessment I
   write today is retrospective and is labelled so below.

## Retrospective design determination, labelled as retrospective

Having read the frozen contract, I judge the design sound and correctly scoped:
it decides limb (a) of HEUR-DS-1 only, demotes the Dickman rho model to a
zero-decision-weight diagnostic, measures its null at the actual X, excludes the
diagonal by construction rather than by filter, and declares its own unpowered
regime in advance with a distinct verdict so a thin not-reject cannot be read as
a pass. I would have approved it prospectively.

THAT SENTENCE IS WORTH EXACTLY AS MUCH AS ITS TIMING ALLOWS, WHICH IS LESS THAN
A PROSPECTIVE APPROVAL. I am stating a counterfactual about what I would have
done, after seeing that the results came back clean, and a reader should
discount it accordingly. I am not backdating an approval and the contract's
`approved_by` field is NOT edited -- it is frozen, and editing it would be both
an immutability violation and a falsification of the record.

## Disposition: NOT decided here

I am NOT unilaterally ruling this run evidence-eligible. Doing so would put the
Coordinator who created the defect in sole judgement of whether the defect
matters, on a package whose results are already known to favour the campaign.

The question goes to the independent validator and red team as a named item:
GIVEN that the pre-registration integrity is independently verifiable from the
hash chain and the phase ordering, and GIVEN that no prospective approval
exists, is this run admissible as evidence, and at what standing? The ledger
archive TASK-20260802-268ec9 rules on eligibility only after both have answered,
and a reviewer finding it inadmissible is a legitimate outcome that would leave
OPEN-BATCH023-A open.

## Second contract defect, recorded: D2

The contract directs the executor to read
`experiments/EXP-SMTH-002/results/feasibility_report.json`, WHICH DOES NOT
EXIST. The executor did not improvise silently: it substituted the measured
throughput from EXP-SMTH-002's actual run manifest and its own budget probe, and
recorded the substitution. Correct handling. The contract is frozen, so this is
not repaired in place; a successor contract must fix the reference.

## Binding on the next batch

Every future batch that freezes a contract carries an explicit Coordinator
APPROVAL TASK between the freeze and the execution, and the execution card's
completion gate requires a non-null `approved_by`. A queue whose lifecycle omits
approval is a defect in the queue, not a licence to skip it.
