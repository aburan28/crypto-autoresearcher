# TASK-20260824-7d9f92 -- BLIND RE-DERIVATION, WRITTEN BEFORE READING THE PRODUCER PACKAGE

Written at the UTC timestamp recorded in red-team-report.yaml
`independent_derivation_before_reading.written_at`, BEFORE any file under
coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/tasks/TASK-20260824-68ba87
was opened, and without ever opening harness/diffpath/depgraph.py or
tests/test_diffpath_depgraph.py.

MECHANISM: my own re-implementation of the contract's declared rule
(constructions/rt3_rederive.py and constructions/rt3_objects.py), importing only the
COMMITTED modules adjudicator.py, equivalence.py, primitives.py, pathobj.py and
controlpower.py. NOT the producer's module.

## Derived strict key components (from ADJ.serialize under STRICT = {E1,E3,E4,E5})
md5 : primitive, length, message_difference, step_delta, block_index          (5)
sha1: primitive, length, message_difference, step_delta, block_index,
      in_linearized_code                                                      (6)
in_linearized_code IS NOT IN THE MD5 KEY AT ALL.

## Constructibility under my CTL-WF (declared in rt3_rederive.wf_reject_reasons)
CONSTRUCTIBLE      : d_message_difference, d_step_delta, d_block_index
NOT CONSTRUCTIBLE  : d_primitive (length/word-count inconsistency, 16/16 rejected)
                     d_length (step_delta arity != length, 32/32 rejected)
                     d_in_linearized_code (flag != recomputed, 8/8 rejected on
                       sha1; 0 constructed on md5 -- the component is not in the
                       md5 key) == null family (e)

## My cell partition of the full 6x6 matrix
per-primitive cells total                 : 72   (36 family-by-row x 2 primitives)
excluded not_constructible                : 36
excluded diagonal                         :  6
excluded forced_by_the_graph (row deleting
  in_linearized_code, retained
  message_difference determines it)       :  6
ADJUDICATED                               : 24   (= 12 family-by-row pairs x 2)

## MY DIFFERING-CELL COUNT
differing cells, honest vs O-E, over the 24 adjudicated per-primitive cells: 0
  equivalently 0 of the 12 adjudicated family-by-row pairs.
honest verdict distribution over the 24 adjudicated cells: DETECTED 0 / NOT DETECTED 24.

## Same counting rule, other instruments (24 adjudicated cells)
honest vs honest          : 0
honest vs O-E             : 0
honest vs always_non_member: 0
honest vs always_member   : 24

## The count WITHOUT the forced_by_the_graph exclusion
cells 30, differing honest vs O-E: 1
the single differing cell: (d_message_difference, row deleting in_linearized_code,
sha1): honest NOT DETECTED, O-E DETECTED.

## My answer to R3-J6/J13, formed before reading the producer's framing
The diagonal exclusion RELOCATES the restatement question rather than answering it,
and the per-primitive split is the finding: on sha1 the excluded diagonal cell
(d_message_difference, delete message_difference) measures NOT DETECTED under the
honest instrument, so the contract's diagonal THEOREM is false there.

CENSUS COMPLETENESS beside every figure above: readable 0 / quarantined_not_read 1 /
acquisition_gap 8, never summed; shadow_planted 16 carried separately. Claim ceiling
`analyzed`. Nothing above is a statement about MD5 or SHA-1.
