#!/usr/bin/env python3
"""EXP-YIELD-003 driver - fresh-master-seed re-execution of the EXP-YIELD-002
repaired-null arm at the 48 declared tuples, plus the RC-21B high-precision
block and the known-answer integrity arm.

TASK-20260729-035, GOAL-ECDLP-001, BATCH-013.

THE CONTRACT IN FORCE is the COMMITTED BLOB
experiments/EXP-YIELD-003/specification.yaml at commit
de6fbb752f9f0b9ce28fda91b15a88593861dfcc, read together with the FIFTEEN
PRE-DISPATCH CONDITIONS PDC-1 .. PDC-15 recorded verbatim in
coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/TASK-20260729-034/
snapshot_commit_receipt.json.

D-1 PROPHYLAXIS.  The frozen specification reads `status: review_required` with
`approved_by: null` BY DESIGN.  THAT NULL IS NOT EVIDENCE OF NON-APPROVAL.  The
APPROVAL DETERMINATION is recorded in the TASK-20260729-034 snapshot commit
receipt: "APPROVED, CONDITIONAL ON PDC-1 THROUGH PDC-15 BEING RECORDED VERBATIM
IN THIS RECEIPT", condition_satisfied true, authorized_to_execute true, verdict
source RT-20260729-033 PASS with zero blocking objections.

THERE IS NO SUCCESS CRITERION AND NO FALSIFICATION CRITERION.  The mean, the
standard deviation and the standard error of z_sem over the 48 declared tuples
are OBSERVATIONS FEEDING NO CRITERION.  This driver evaluates NO criterion,
declares NO branch, and does NOT apply the resume condition.  Disposition
belongs to TASK-20260729-037, TASK-20260729-038 and DEC-20260729-003 (ST-4).

THE CONTRACT IS NOT THRESHOLD-FREE AND NO RECORD THIS DRIVER WRITES SAYS IT IS.
It carries one pre-registered three-way disposition rule - the resume condition
carried verbatim from DEC-20260729-002 NA-1 - which this run package records and
does not apply.

ZERO CURVE ARITHMETIC.  No elliptic-curve point addition, no doubling, no scalar
multiplication, no curve-order computation, no curve or generator selection, no
discrete-logarithm table, no factor base, no sum set, no census, no summation
polynomial, no Groebner basis, no polynomial system solve.  This is a
balls-in-bins simulation over the integer residue range {0, ..., N-1} on
integers QUOTED from committed, hash-bound files.

PROVENANCE, STATED HONESTLY (task card constraint).  The authoring session DID
READ experiments/EXP-YIELD-002/driver/repaired_null.py before writing this file,
because EXP-YIELD-003 is a declared REPLICATION of that arm.  What was reused is
recorded in REUSE_FROM_EXP_YIELD_002 below and in every manifest.  The session
did NOT read and this file does not import
experiments/EXP-YIELD-001/driver/yield_census.py; that file was never opened.

Permitted dependencies: the Python standard library and numpy, and nothing else.
Nothing under harness/, tools/ or orchestration/ is imported, executed or read.

Usage:
    python3 experiments/EXP-YIELD-003/driver/replicate_repaired_null.py --run RUN-YIELD-003-KNOWNANSWER
    python3 experiments/EXP-YIELD-003/driver/replicate_repaired_null.py --run RUN-YIELD-003-REPLICATE-REPAIRED
    python3 experiments/EXP-YIELD-003/driver/replicate_repaired_null.py --run RUN-YIELD-003-HIGHPREC
    python3 experiments/EXP-YIELD-003/driver/replicate_repaired_null.py --summary
    python3 experiments/EXP-YIELD-003/driver/replicate_repaired_null.py --pp1-child   (PP-1 sub-block; writes NO file)
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import platform
import resource
import struct
import subprocess
import sys
import time

import numpy as np

# --------------------------------------------------------------------------
# 0.  Identity and contract constants.  Every value below is QUOTED from a
#     committed file or from the committed TASK-20260729-034 receipt.
# --------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-YIELD-003"
TASK_ID = "TASK-20260729-035"
GOAL_ID = "GOAL-ECDLP-001"
BATCH_ID = "BATCH-013"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

CONTRACT_IN_FORCE = {
    "path": "experiments/EXP-YIELD-003/specification.yaml",
    "commit": "de6fbb752f9f0b9ce28fda91b15a88593861dfcc",
    "status_in_the_frozen_file": "review_required",
    "approved_by_in_the_frozen_file": None,
    "d1_prophylaxis_note": (
        "THE NULL approved_by IS BY DESIGN AND MUST NOT BE READ AS EVIDENCE OF "
        "NON-APPROVAL.  The approval determination lives in "
        "coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/"
        "TASK-20260729-034/snapshot_commit_receipt.json, APPROVAL_DETERMINATION: "
        "'APPROVED, CONDITIONAL ON PDC-1 THROUGH PDC-15 BEING RECORDED VERBATIM "
        "IN THIS RECEIPT', condition_satisfied true, authorized_to_execute true, "
        "verdict source RT-20260729-033 PASS, fifteen numbered objections, ZERO "
        "blocking."
    ),
    "pre_execution_review": (
        "coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/reviews/"
        "TASK-20260729-033/contract_review.yaml, REV-20260729-033, verdict PASS."
    ),
    "pre_dispatch_conditions_source": (
        "coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/archives/"
        "TASK-20260729-034/snapshot_commit_receipt.json, field "
        "PRE_DISPATCH_CONDITIONS_VERBATIM.  The fifteen texts are embedded in "
        "this driver as constants; the driver does NOT read the receipt at run "
        "time, because IV-6 fires on reading any file not named in `inputs`."
    ),
}

# inputs.files_read of the frozen contract.  AN INPUT THAT IS NOT HASH-BOUND IS
# NOT AN INPUT.  A mismatch fires IV-1 and is never repaired in flight.
IN_1_PATH = "experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json"
IN_1_SHA256 = "040207f85a3444a3377cdf5c86175fb70de6e47280f91c09a516f7a65d2125cd"
IN_2_PATH = "experiments/EXP-YIELD-001/results/summary.json"
IN_2_SHA256 = "2287b277b6f6ce842230ca13bf1217a8ba34cc6da1d2d362123502810f7b2aeb"
IN_3_PATH = "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/results.json"
IN_3_SHA256 = "73bb3ae1a8b1b9fffa4b1f83e76b12738efbbacb5a60631781b4cad3a61dcaf8"
IV2_EXTRA_FILES = [
    ("experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-ASRECORDED/results.json",
     "c486194da88732a6bd2a5fb146e42a0d76807d7069e21beaad7fa4706ae556c1"),
    ("experiments/EXP-YIELD-002/runs/RUN-YIELD-002-KNOWNANSWER/results.json",
     "d99b8833c70293bac2f1a52e9c13ce2b30e3a9d2aa3cd7235ebeb27d68793799"),
]
IN_1_2_BOUND_COMMIT = "2fb2bb7a111d999859612e52990eea7dc6bbac1a"
IN_3_BOUND_COMMIT = "c7189f80225bad0d0d2aa28cbbbb11e672d30dd6"

# replication.seeds of the frozen contract.
MASTER_SEEDS = {
    "REPLICATE-REPAIRED": 130301,
    "KNOWNANSWER": 130401,
    "HIGHPREC-REPAIRED": 130501,
    "HIGHPREC-ASRECORDED": 130501,
}
# THE CLOSED ENUMERATED ARM-LABEL SET (the DEV-4 repair).  IV-2d fires on any
# label outside these four strings.
ARM_LABELS_CLOSED_SET = ["REPLICATE-REPAIRED", "KNOWNANSWER",
                         "HIGHPREC-REPAIRED", "HIGHPREC-ASRECORDED"]

RUN_IDS = {
    "KNOWNANSWER": "RUN-YIELD-003-KNOWNANSWER",
    "REPLICATE-REPAIRED": "RUN-YIELD-003-REPLICATE-REPAIRED",
    "HIGHPREC": "RUN-YIELD-003-HIGHPREC",
}
ARM_ORDER_ST_2 = ["RUN-YIELD-003-KNOWNANSWER", "RUN-YIELD-003-REPLICATE-REPAIRED",
                  "RUN-YIELD-003-HIGHPREC"]

INV4_FAILING_TUPLES = ["T-18-3-B16", "T-16-3-B16", "T-18-3-B24", "T-18-3-B28"]
MERGED_TUPLE = "T-12-3-B22"

# The six m = 2 block tuples the contract NAMES as the consequence of the RC-21B
# rule.  THE RULE GOVERNS OVER THE NAMES IF THEY EVER DISAGREE; the driver
# applies the rule and reports the comparison.
RC_21B_NAMED_SIX = ["T-18-2-B34", "T-18-2-B44", "T-18-2-B58",
                    "T-14-2-B118", "T-16-2-B246", "T-12-2-B62"]

HIGHPREC_REPLICATES = 10000
IV1_TOLERANCE = 1e-9          # IV-1 / KA-8, absolute
KA_SIGMA_TOLERANCE = 4.000    # KA-3, KA-4, KA-6
PER_RUN_WALL_CLOCK_SECONDS = 600  # ST-1
MAXIMUM_MEMORY_GB = 4             # ST-1
CLAIM_TIER = "toy"

COMMITTED_EXP_YIELD_002_Z_SEM_MEAN = 0.36102368504276455  # QUOTED, feeds nothing.

# --------------------------------------------------------------------------
# 1.  Sentences carried into every record.  PDC-2 SPLITS THE CONSTRAINED
#     SENTENCE AND THE SPLIT IS OBEYED HERE.
# --------------------------------------------------------------------------

CONSTRAINED_SENTENCE_PROHIBITION = (
    "NO RECORD MAY SAY THE REPAIRED NULL LANDS ON P_pred.  This prohibition "
    "binds every record this contract produces, without qualification, and it "
    "is obeyed by this driver and by every file it writes."
)
CONSTRAINED_SENTENCE_ASSERTION_SCOPE_PDC_2 = (
    "PDC-2.  The ASSERTION half of the constrained sentence - that the null "
    "lands at or slightly above P_pred by an amount larger than the declared "
    "second-order biases account for, and unexplained - IS SCOPED TO THE "
    "COMMITTED EXP-YIELD-002 REALISATION ONLY and MAY NOT be asserted of "
    "EXP-YIELD-003's own realised data by this run record, by the results "
    "summary, by any review, by EV-ECDLP-010 or by DEC-20260729-003.  This "
    "package therefore asserts it of NOTHING it measured."
)
ADMISSION_AND_CEILING = (
    "CARRIED VERBATIM AND BINDING.  EXP-YIELD-003 IS NOT AN EXPONENT-DECIDING "
    "SCREEN AND IS NOT EVEN AN INSTRUMENT CONTROL ON A CONTROL.  IT IS A "
    "REPLICATION OF AN INSTRUMENT CONTROL ON A CONTROL.  IT MOVES NO EXPONENT "
    "AND CANNOT MOVE ONE.  ITS CLAIM TIER IS CAPPED AT TOY.  It CAN MEET NO "
    "COMPLETION CRITERION OF GOAL-ECDLP-001 UNDER ANY OUTCOME.  It changes no "
    "hypothesis status.  It COMPUTES NO OCCUPANCY-NORMALISED EFFICIENCY E AND "
    "NO YIELD RATIO R.  IT DOES NOT UN-FIRE INV-4 AND DOES NOT RE-DISPOSE IT.  "
    "It DECLARES INV-5 NEITHER FIRED NOR NOT FIRED.  IT TOUCHES NO COST MODEL.  "
    "A TIMEOUT, CRASH, RESOURCE EXHAUSTION OR IMPLEMENTATION FAILURE IS "
    "INFRASTRUCTURE SIGNAL AND IS NEVER A NEGATIVE MATHEMATICAL RESULT about "
    "P_pred, about the shift, about the diagnostic, about the occupancy null, "
    "about decomposition yield or about anything else.  NON-EXECUTION IS NEVER "
    "RECORDED AS A RESULT."
)
ST_4_NO_INTERPRETATION = (
    "ST-4 OBSERVED.  This run package contains OBSERVATIONS ONLY.  It states no "
    "disposition of the resume condition, writes no evidence or decision "
    "record, touches no hypothesis status, does not re-dispose INV-4, does not "
    "adjudicate INV-5, says nothing about decomposition yield, and DOES NOT "
    "DESCRIBE THIS REPLICATION AS A FRESH-PLATFORM REPLICATION.  Interpretation "
    "belongs to TASK-20260729-037, TASK-20260729-038 and DEC-20260729-003."
)
NO_SUCCESS_CRITERION_STATEMENT = (
    "NO SUCCESS CRITERION AND NO FALSIFICATION CRITERION EXIST IN THIS "
    "CONTRACT, AND THAT IS THE DESIGN - acceptance limits on the INSTRUMENT "
    "(the seven invalidation rules), none on the MEASURAND.  THE CONTRACT IS "
    "NEVERTHELESS NOT THRESHOLD-FREE AND NO RECORD MAY CALL IT THRESHOLD-FREE: "
    "it carries ONE pre-registered three-way disposition rule, the resume "
    "condition carried verbatim from DEC-20260729-002 NA-1, which this run "
    "package RECORDS and DOES NOT APPLY."
)
RESUME_CONDITION_VERBATIM = (
    "If the replicated mean is within about 0.14 SEM of zero, the shift is "
    "recorded as chance and closed. If it reproduces above about +0.25 SEM, the "
    "driver, the numpy build and the platform become the objects of the next "
    "control. NO CONCLUSION ABOUT THE PROCESS IS DRAWN FROM IT EITHER WAY, and "
    "no conclusion about decomposition yield is drawn from it in any case."
)
RESUME_CONDITION_NOT_APPLIED_HERE = (
    "RECORDED, NOT APPLIED.  This driver does not evaluate the resume "
    "condition, does not compare any realised number against 0.14 or 0.25, and "
    "declares no branch.  The unassigned region - above about +0.14 and at most "
    "about +0.25, and everything below about -0.14 - is RECORDED AS "
    "INCONCLUSIVE ON THE SHIFT by the contract and is never assimilated to the "
    "nearer named branch; that disposition belongs to DEC-20260729-003."
)
BND_1_2_3_4 = {
    "BND-1": (
        "WITH A FRESH MASTER SEED ON THE SAME DRIVER, THE SAME BUILD AND THE "
        "SAME PLATFORM, THIS REPLICATION SEPARATES CHANCE FROM A "
        "SEED-INDEPENDENT DETERMINISTIC PROPERTY OF THE DRIVER-BUILD-PLATFORM "
        "COMBINATION, AND IT SEPARATES NONE OF THOSE THREE FROM EACH OTHER."
    ),
    "BND-2": (
        "IT NEVER SEPARATES ANY OF THE THREE FROM THE PROCESS, because the "
        "process is identical in both run sets.  A reproduction is evidence "
        "about THIS INSTRUMENT and never about the balls-in-bins process, never "
        "about P_pred, and never about decomposition yield."
    ),
    "BND-3": (
        "NO RECORD MAY DESCRIBE THIS AS A FRESH-PLATFORM REPLICATION, BECAUSE "
        "THE PLATFORM DOES NOT CHANGE.  A different OPERATING SYSTEM and a "
        "different MACHINE ARCHITECTURE are unavailable on this host."
    ),
    "BND-4": (
        "DETERMINISM OF THE RECORDED PIPELINE IS NOT PORTABILITY.  No record "
        "may read PP-1, under any case, as a portability result or as a "
        "cross-version determinism result."
    ),
}
PDC_15_DIFFERENCE_COLUMN_PROHIBITION = (
    "PDC-15, SYMMETRIC AND BINDING.  NO RECORD MAY QUOTE ANY HIGH-PRECISION "
    "REPAIRED-MINUS-AS-RECORDED DIFFERENCE COLUMN AS A CONFIRMATION OF T, AND "
    "NO RECORD MAY QUOTE IT AS A DISCONFIRMATION OF T.  The exact expectation "
    "of that difference under the specified process is "
    "(|S_(m-2)|/N)[(N-1)(1-2/N)^(C_red/2) + (1-1/N)^(C_red/2)], which agrees "
    "with T to better than 3.2e-5 at every one of the ten block tuples, SO THAT "
    "AGREEMENT IS ARITHMETIC AND NOT EVIDENCE."
)
PDC_9_RECOMPUTABILITY_NOTE = (
    "PDC-9 / RC-33-L.  The deviation of the repaired leg from the exact "
    "analytic mean, IN STANDARD-ERROR UNITS - the quantity RT-20260729-021 "
    "RT21-6 used as its discriminating control - IS RECOMPUTABLE from the "
    "fields this record already carries: the per-leg mean, sd and standard "
    "error at 10000 replicates (OM-8) and N, C_red and |S_(m-2)| (OM-9), "
    "through E[distinct] = N - (1 - s/N)[(N-1)(1-2/N)^(C_red/2) + "
    "(1-1/N)^(C_red/2)].  NO SUCH QUANTITY IS COMPUTED HERE AND NO THRESHOLD IS "
    "APPLIED; the statement exists so that a later record that pre-registers "
    "its reading knows the quantity is available.  `The block feeds nothing` is "
    "a statement about EXP-YIELD-003 and NOT a statement that these archived "
    "numbers are uninterpretable by any future record."
)
REUSE_FROM_EXP_YIELD_002 = {
    "did_the_authoring_session_read_the_EXP_YIELD_002_driver": True,
    "file_read": "experiments/EXP-YIELD-002/driver/repaired_null.py",
    "why_reading_it_is_permitted": (
        "The TASK-20260729-035 queue entry permits it explicitly: EXP-YIELD-003 "
        "is a declared REPLICATION of that arm and pretending otherwise would be "
        "theatre.  The file is NOT imported and NOT executed by this driver; "
        "only the authoring session read it."
    ),
    "what_was_reused": [
        "The SHAPE of draw_replicates - one boolean occupancy array of length N "
        "cleared per replicate, one rng.choice(N, size=s, replace=False, "
        "shuffle=True) pre-mark call, one rng.integers(0, N, size=C_red//2, "
        "dtype=numpy.int64) throw call, marking g and (N-g) mod N, counting with "
        "numpy.count_nonzero.  The call sequence itself is MANDATED WORD FOR "
        "WORD by the EXP-YIELD-003 contract clause "
        "the_named_calls_and_the_stream_order_carried_from_C_3d_and_C_19c, so it "
        "is not a free choice in either file.",
        "The SHAPE of the seed derivation helpers (SHA-256 of a pipe-joined "
        "ASCII payload, low 64 bits little-endian unsigned).  The payload field "
        "order is mandated by the EXP-YIELD-003 contract clause "
        "seed_derivation_binding and knownanswer_seed_derivation.",
        "The SHAPE of the utility helpers sha256_file, git_state, the in-process "
        "stdout/stderr Tee, and the environment block field list.",
        "The DEV-1 deviation pattern - folding command.txt, environment.json and "
        "stderr.log into the manifest because the declared artifact set admits "
        "no separate files for them.",
    ],
    "what_was_NOT_reused": [
        "No number, no seed, no tuple set and no result was copied.  Every "
        "parameter is read from the hash-bound inputs at run time.",
        "The EXP-YIELD-002 criteria CR-1 .. CR-4, its power curve, its "
        "conditional budget block, its phi-equivalent block and its mandated C-20 "
        "sentence are NOT carried: EXP-YIELD-003 has no criterion and RT21-1 "
        "forbids reproducing the C-20 power sentence.",
    ],
    "experiments_EXP_YIELD_001_driver": (
        "experiments/EXP-YIELD-001/driver/yield_census.py WAS NOT READ, NOT "
        "OPENED, NOT IMPORTED AND NOT EXECUTED by the authoring session or by "
        "this driver.  RECORDED AS THE TASK CARD REQUIRES.  THIS IS NOT A "
        "DISCHARGE OF RC-F AND NO DISCHARGE IS CLAIMED."
    ),
}

# The fifteen pre-dispatch conditions, COPIED PROGRAMMATICALLY from the committed
# TASK-20260729-034 snapshot_commit_receipt.json field
# PRE_DISPATCH_CONDITIONS_VERBATIM by the executing session, never retyped, and
# embedded here as a constant so that this driver does not READ that receipt at
# run time (IV-6 fires on reading any file not named in `inputs`).
PRE_DISPATCH_CONDITIONS_VERBATIM = json.loads(r'''
{
"binding_statement": "EVERY CONDITION BELOW MUST APPEAR VERBATIM IN THE TASK-20260729-034 SNAPSHOT COMMIT RECEIPT BEFORE TASK-20260729-035 IS DISPATCHED. D-2 is this program's worked example of what a late recording costs: a condition recorded after the fact is not a condition. None of these conditions changes a seed, a replicate count, a tuple set, a block membership, a denominator reading, a tolerance or an invalidation-rule value, so none is a protocol amendment and none consumes the RC-13 one-cycle cap.",
"conditions": [
{
"id": "PDC-1",
"text": "IV-6's clause `applies any threshold to any quantity of this contract` is scoped to the observation quantities OM-1 through OM-9 and to any quantity derived from them, and does not reach the tolerances that invalidation rules IV-1 and IV-3 themselves mandate; the driver's application of the 1e-9 absolute tolerances of IV-1 and KA-8 and of the 4.000-sigma tolerances of KA-3, KA-4 and KA-6 is required execution of those rules and does not fire IV-6."
},
{
"id": "PDC-2",
"text": "The clause named `the_constrained_sentence_binding_every_record_this_contract_produces` is read in two parts: its prohibition, that no record may say the repaired null lands ON P_pred, binds every record this contract produces without qualification; its assertion, that the null lands at or slightly above P_pred by an amount larger than the declared second-order biases account for and unexplained, is scoped to the committed EXP-YIELD-002 realisation only and may not be asserted of EXP-YIELD-003's own realised data by any run record, results summary, review, EV-ECDLP-010 or DEC-20260729-003."
},
{
"id": "PDC-3",
"text": "Observation feasibility table section 6's sentence naming T-18-2-B82 at lambda 0.01284643 as the nearest non-selected lambda neighbour from below is superseded and corrected: the rank-4 tuple, and therefore the nearest non-selected neighbour from below, is T-16-2-B38 at lambda 0.01100056; T-18-2-B82 is rank 5. The RC-21B rule and the six selected block tuples are unaffected and are independently confirmed correct."
},
{
"id": "PDC-4",
"text": "DEFER-BATCH013-001's cost statement `of order twenty-four times the committed EXP-YIELD-002 high-precision block` is superseded and corrected to of order twelve times when counted in tuple-legs, the committed block being four tuples in two legs, and of order six times when counted in the byte-clear unit the contract's own budget note uses; no other part of DEFER-BATCH013-001 is changed and it remains deferred."
},
{
"id": "PDC-5",
"text": "The sem_001 column discrepancy in the committed BATCH-012 criterion feasibility table is recorded as hand-arithmetic error and not as presentation-level rounding; it is present at all eleven 30-replicate rows and at none of the thirty-seven 100-replicate rows, and its largest instance is 3.929e-3 absolute at T-18-3-B82, where the table prints 31.725983 and the authoritative value from the committed BATCH-011 results is 31.7299120391; the committed machine records are correct at all 48 rows to 0.0 absolute, no criterion and no quantity of EXP-YIELD-003 consumes the column, and the committed artifact is superseded rather than edited."
},
{
"id": "PDC-6",
"text": "The clause `no_criterion_may_be_added_later` prohibits the attachment of any NEW threshold, acceptance region, band, window, decision rule or pass-or-fail reading, and does not prohibit DEC-20260729-003 from applying the resume condition carried verbatim from DEC-20260729-002 NA-1, which pre-exists this contract and is the only disposition DEC-20260729-003 is authorised to take on the primary observation."
},
{
"id": "PDC-7",
"text": "Observation OM-7 is retained and is not struck; no disposition of the resume condition may be taken on the mean of delta_z, which is identically the replicated 48-tuple z_sem mean minus 0.36102368504276455 and therefore carries no information the primary observation does not, and the resume condition is evaluated on the primary observation OM-5's mean and on no other quantity."
},
{
"id": "PDC-8",
"text": "PP-1's outcome is classified on STREAM EQUALITY and not on numpy version equality alone: the Executor records whether the PP-1 48-tuple z_sem vector is bit-identical to the primary arm's, records both numpy version strings, and records that a different numpy version producing an identical stream is a fourth case that the contract's three-case statement does not enumerate; under no case may PP-1 be read as a portability result, as a cross-version determinism result or as a separation of the driver from the build, and if PP-1 yields a second fresh-stream 48-tuple mean that mean is reported as a separately labelled observation and is never pooled with, averaged into, substituted for, or compared against the resume-condition thresholds."
},
{
"id": "PDC-9",
"text": "The statement that the high-precision block feeds nothing is a statement about EXP-YIELD-003 and is not a statement that the block's archived numbers are uninterpretable by any future record; a later record that pre-registers its reading before looking at them may read them, and the deviation of the repaired leg from the exact analytic mean in standard-error units - the quantity RT-20260729-021 RT21-6 used as its discriminating control - is recomputable from the fields OM-8 and OM-9 already require."
},
{
"id": "PDC-10",
"text": "The tail-check counts of absolute z_sem above 1, 2 and 3 are reported beside expectations computed under the contract's own stated null for z_sem, which is a Student-t mixture of 37 tuples at 99 degrees of freedom and 11 at 29 degrees of freedom giving expected counts of 15.412, 2.389 and 0.187 over 48 draws, and if the standard-normal figures 15.231, 2.184 and 0.130 are reported they are labelled as computed under a reference distribution that is not the stated null."
},
{
"id": "PDC-11",
"text": "PRED-ID EXTENDED is applied to every count this contract and its records state and not only to counts of tuples; in particular the figure 105 is recorded as the number of DISTINCT derived seeds in the three committed EXP-YIELD-002 run results.json files, which record 109 seed fields, the four repeats being the four INV-4-failing tuples printed twice inside RUN-YIELD-002-NULL-REPAIRED, and the IV-2c scope is recorded as covering all 98 derived seeds IN-1 records, being 49 for the antipodal arm and 49 for the independent-throw contrast arm, rather than the antipodal arm alone."
},
{
"id": "PDC-12",
"text": "The standard error of the 48-tuple z_sem mean under the independent-stream design is recorded as 0.1466905 rather than 0.146691, and the two standardised resume-condition edges as 0.9543904 and 1.7042686 rather than 0.954389 and 1.704194; all three corrections are in the sixth decimal place, none changes any statement in which the figures bear weight, and the branch probabilities derived from them are independently confirmed correct."
},
{
"id": "PDC-13",
"text": "PP-1's second interpreter is invoked as a subprocess running the single declared driver file and returns its numbers to the parent process without writing any file inside the repository; if a temporary file is unavoidable it is created outside the repository, its exact path is recorded in the manifest, and it is removed before the run ends, so that the committed artifact set remains exactly the eleven declared files and IV-6 does not fire on a twelfth."
},
{
"id": "PDC-14",
"text": "The unit convention of the resume condition is recorded explicitly: `about 0.14 SEM` and `about +0.25 SEM` are 0.14 and 0.25 in the units of the z_sem statistic itself, being the same usage as RT-20260729-021's `+0.0264 SEM on average` and DEC-20260729-002 NA-1's `at most 0.0895 SEM`, and are not multiples of the 0.1466905 standard error of the 48-tuple mean; under the alternative reading the pre-committed inconclusive region would have probability about 0.49 rather than 0.2957 under a centred replication."
},
{
"id": "PDC-15",
"text": "The prohibition on the high-precision difference column is symmetric: no record may quote any high-precision repaired-minus-as-recorded difference column as a confirmation of T and no record may quote it as a disconfirmation of T, and any record that reports the column states that its exact expectation under the specified process is (|S_(m-2)|/N)[(N-1)(1-2/N)^(C_red/2) + (1-1/N)^(C_red/2)], which agrees with T to better than 3.2e-5 at every one of the ten block tuples, so that agreement is arithmetic and not evidence."
}
]
}
''')

PDC_COMPLIANCE = {
    "PDC-1": (
        "OBEYED AND LOAD-BEARING.  IV-6's threshold clause is scoped to the "
        "observation quantities OM-1..OM-9 and quantities derived from them, and "
        "does NOT reach the tolerances IV-1 and IV-3 themselves mandate.  This "
        "driver therefore applies the 1e-9 absolute tolerances of IV-1 and KA-8 "
        "and the 4.000-sigma tolerances of KA-3, KA-4 and KA-6 as REQUIRED "
        "EXECUTION of those rules.  IV-6 DOES NOT FIRE on them.  Without PDC-1 "
        "this run would have stopped under ST-3 before the first draw, because "
        "IV-1 and IV-3 mandate 192 tolerance tests that IV-6 read literally "
        "forbids."
    ),
    "PDC-2": "OBEYED.  See CONSTRAINED_SENTENCE_PROHIBITION and CONSTRAINED_SENTENCE_ASSERTION_SCOPE_PDC_2.",
    "PDC-3": (
        "CARRIED.  The corrected nearest non-selected lambda neighbour from "
        "below is T-16-2-B38 at lambda 0.01100056 (rank 4); T-18-2-B82 at "
        "0.01284643 is rank 5.  The driver RE-APPLIES the RC-21B rule to IN-1 "
        "and reports the realised ranks, so the correction is checkable rather "
        "than quoted."
    ),
    "PDC-4": (
        "CARRIED, NOT CONSUMED.  DEFER-BATCH013-001's cost multiple is of order "
        "TWELVE times the committed high-precision block counted in tuple-legs, "
        "and of order SIX times counted in byte-clears, not twenty-four.  "
        "Nothing in this run consumes that figure."
    ),
    "PDC-5": (
        "CARRIED, NOT CONSUMED.  The sem_001 column discrepancy in the committed "
        "BATCH-012 criterion feasibility table is HAND-ARITHMETIC ERROR at all "
        "eleven 30-replicate rows, largest 3.929e-3 absolute at T-18-3-B82.  NO "
        "QUANTITY OF THIS RUN CONSUMES THAT COLUMN."
    ),
    "PDC-6": (
        "CARRIED.  The prohibition on adding a criterion later forbids NEW "
        "thresholds and does not forbid DEC-20260729-003 from applying the "
        "carried resume condition.  THIS RUN PACKAGE APPLIES NOTHING."
    ),
    "PDC-7": (
        "OBEYED.  OM-7 is retained and is not struck.  NO DISPOSITION IS TAKEN "
        "ON THE MEAN OF delta_z, which is identically the replicated 48-tuple "
        "z_sem mean minus 0.36102368504276455 and carries no information the "
        "primary observation does not.  The identity is stated beside the number "
        "so it cannot be used as a differently named route to the disposition."
    ),
    "PDC-8": (
        "OBEYED.  PP-1 is classified on STREAM EQUALITY, not on numpy version "
        "equality: the driver records whether the PP-1 48-tuple z_sem vector is "
        "BIT-IDENTICAL to the primary arm's, records both numpy version strings, "
        "and records that a different numpy version producing an identical "
        "stream is a FOURTH CASE the contract's three-case statement does not "
        "enumerate.  PP-1 is read as NO portability result, NO cross-version "
        "determinism result and NO separation of the driver from the build.  A "
        "second fresh-stream 48-tuple mean is reported as a separately labelled "
        "observation and is NEVER pooled with, averaged into, substituted for, "
        "or compared against the resume-condition thresholds."
    ),
    "PDC-9": "OBEYED.  See PDC_9_RECOMPUTABILITY_NOTE in the high-precision block.",
    "PDC-10": (
        "OBEYED.  The tail-check counts are reported beside expectations "
        "computed under THE CONTRACT'S OWN STATED NULL for z_sem - a Student-t "
        "mixture of 37 tuples at 99 degrees of freedom and 11 at 29 - which the "
        "driver evaluates from the regularized incomplete beta function and "
        "cross-checks against PDC-10's quoted 15.412, 2.389 and 0.187.  The "
        "standard-normal figures are also reported and are LABELLED as computed "
        "under a reference distribution that is NOT the stated null."
    ),
    "PDC-11": (
        "OBEYED.  PRED-ID EXTENDED is applied to every count this package "
        "states.  105 is recorded as the number of DISTINCT derived seeds in the "
        "three committed EXP-YIELD-002 run results.json files, which record 109 "
        "seed FIELDS, the four repeats being the four INV-4-failing tuples "
        "printed twice inside RUN-YIELD-002-NULL-REPAIRED.  IV-2c's scope is "
        "recorded as ALL 98 derived seeds IN-1 records - 49 antipodal and 49 "
        "independent-throw contrast - and not the antipodal arm alone.  Both "
        "pool sizes are MEASURED by enumeration here, not asserted."
    ),
    "PDC-12": (
        "CARRIED AS A PRE-DATA REFERENCE MAGNITUDE AND APPLIED TO NOTHING.  The "
        "standard error of the 48-tuple z_sem mean under the independent-stream "
        "design is 0.1466905; the two standardised resume-condition edges are "
        "0.9543904 and 1.7042686.  No realised number of this run is compared "
        "against any of the three."
    ),
    "PDC-13": (
        "OBEYED.  PP-1's second interpreter is invoked as a SUBPROCESS running "
        "this single declared driver file with --pp1-child, and returns its "
        "numbers to the parent process ON STDOUT.  NO FILE IS WRITTEN inside the "
        "repository by the child and no temporary file is created anywhere, so "
        "the committed artifact set stays exactly the eleven declared files and "
        "IV-6 does not fire on a twelfth."
    ),
    "PDC-14": (
        "RECORDED.  `about 0.14 SEM` and `about +0.25 SEM` are 0.14 and 0.25 IN "
        "THE UNITS OF THE z_sem STATISTIC ITSELF - the same usage as "
        "RT-20260729-021's `+0.0264 SEM on average` and DEC-20260729-002 NA-1's "
        "`at most 0.0895 SEM` - and are NOT multiples of the 0.1466905 standard "
        "error of the 48-tuple mean.  This run package applies neither reading."
    ),
    "PDC-15": "OBEYED.  See PDC_15_DIFFERENCE_COLUMN_PROHIBITION in the high-precision block.",
}

# --------------------------------------------------------------------------
# 2.  Small utilities.
# --------------------------------------------------------------------------


class Tee(object):
    """In-process tee of stdout and stderr into the run's stdout.log (DEV-1)."""

    def __init__(self, stream, handle):
        self._stream = stream
        self._handle = handle

    def write(self, data):
        self._stream.write(data)
        self._handle.write(data)

    def flush(self):
        self._stream.flush()
        self._handle.flush()

    def isatty(self):
        return False


class InputIntegrityError(Exception):
    """IV-1 INPUT INTEGRITY."""


class AmbiguityStop(Exception):
    """ST-3 STOP AND REPORT."""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_state():
    def run(args):
        try:
            return subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True,
                                  check=True).stdout.strip()
        except Exception as exc:  # pragma: no cover - infrastructure path
            return "UNAVAILABLE: %r" % (exc,)

    porcelain = run(["git", "status", "--porcelain"])
    entries = [ln for ln in porcelain.splitlines() if ln.strip()]
    codes = {}
    for ln in entries:
        codes[ln[:2]] = codes.get(ln[:2], 0) + 1
    return {
        "commit": run(["git", "rev-parse", "HEAD"]),
        "branch": run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": bool(entries),
        "dirty_entry_count": len(entries),
        "dirty_entries_by_status_code": codes,
        "dirty_entries_first_64": entries[:64],
        "porcelain_sha256": hashlib.sha256(porcelain.encode("utf-8")).hexdigest(),
        "worktree": REPO_ROOT,
    }


def environment_block(driver_sha256, rlimit_status):
    """THE SIX REQUIRED STRINGS, RECORDED BEFORE THE FIRST DRAW (IV-7)."""
    return {
        "recorded_before_the_first_draw": True,
        "sys_version": sys.version,
        "sys_executable": sys.executable,
        "platform_platform": platform.platform(),
        "platform_machine": platform.machine(),
        "platform_processor": platform.processor(),
        "numpy___version__": np.__version__,
        "numpy_version_exact_string": np.__version__,
        "cpu_count": os.cpu_count(),
        "dependency_versions": {"numpy": np.__version__, "python": platform.python_version()},
        "numpy_pin_note": (
            "THE EXACT numpy.__version__ STRING GOVERNS AND THE PIN IS "
            "LOAD-BEARING.  numpy does not guarantee bit-identical Generator "
            "output across versions, and shuffle=True and shuffle=False return "
            "the same SET of pre-marked bins but leave the generator in "
            "DIFFERENT STATES, so the following rng.integers call differs.  ONE "
            "numpy version is used across all three arms, all 48 tuples, all ten "
            "block tuples and all eight known-answer cases.  PP-1's second "
            "interpreter build is EXPRESSLY OUTSIDE that single-version scope "
            "(IV-7) and records its own six environment strings separately."
        ),
        "committed_reference_environment_quoted": {
            "source": ("QUOTED from the committed EXP-YIELD-002 manifest at "
                       "c7189f80225bad0d0d2aa28cbbbb11e672d30dd6"),
            "python_version_begins": "3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22)",
            "platform": "macOS-26.6-arm64-arm-64bit-Mach-O",
            "machine": "arm64",
            "processor": "arm",
            "numpy": "2.4.0",
        },
        "driver_path": "experiments/EXP-YIELD-003/driver/replicate_repaired_null.py",
        "driver_sha256": driver_sha256,
        "rlimit_as_status": rlimit_status,
        "files_this_driver_opens": [
            "the five hash-bound input files named in inputs (IN-1, IN-2, IN-3 "
            "and the two EXP-YIELD-002 results files read only for IV-2)",
            "this driver file itself, to record its own SHA-256",
            "the three artifact files of the run it is executing, for writing",
        ],
        "randomness_sources": [
            "numpy.random.default_rng(seed) [PCG64] - the ONLY source of "
            "randomness in this package.  One generator per tuple per arm label, "
            "seeded by the contract's SHA-256 derivation, recorded beside every "
            "number it produced.",
            "No other source of randomness is used.  Set iteration order, dict "
            "order and hash randomisation enter no reported number.",
        ],
    }


def inference_block():
    """Recorded honestly.  Nothing here is probe-verified and nothing is claimed."""
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source": (
            "TASK-20260729-035 dispatch_queue.json handoff.inference.policy, verbatim."
        ),
        "adapter_invoked": False,
        "adapter_not_invoked_reason": (
            "DELIBERATE AND LITERAL.  The EXP-YIELD-003 contract's "
            "instrument_independence.forbidden_imports clause forbids this "
            "driver from importing OR EXECUTING anything under orchestration/, "
            "and IV-6 fires on invoking a forbidden module.  "
            "`python3 -m orchestration.adapter resolve` and `doctor --probe` "
            "were therefore NOT run by this driver.  NO ADAPTER RESULT IS "
            "CLAIMED AND NONE IS FABRICATED."
        ),
        "backend_env_AUTORESEARCH_BACKEND": os.environ.get("AUTORESEARCH_BACKEND"),
        "policy_env_AUTORESEARCH_POLICY": os.environ.get("AUTORESEARCH_POLICY"),
        "resolved_runtime_model_id": "claude-opus-5",
        "resolved_model_id_source": (
            "Self-reported by the Claude Code runtime session executing "
            "TASK-20260729-035.  NOT probe-verified."
        ),
        "model_verified": False,
        "fallback_used": False,
        "fallback_allowed": False,
        "degraded_allowed": False,
        "degraded_requirements": [],
        "reasoning_effort": None,
        "independent_session_required": False,
        "policy_binding_mismatch_disclosed": (
            "DISCLOSED, NEVER SUBSTITUTED (INT-BATCH013-D).  The handoff requests "
            "policy `executor-implementation`.  CLAUDE.md's model policy note "
            "records that Claude Code cannot resolve "
            "orchestration/model-policies.yaml identifiers; subagent frontmatter "
            "supports only Claude models and all subagents run at "
            "`model: inherit`.  The adapter is known to resolve the executor role "
            "to a different model than the executing session reports.  This "
            "session was not launched with a resolved policy environment and "
            "reports itself as claude-opus-5.  This is a process-level per-role "
            "model-selection gap, NOT a backend fallback, and it is recorded "
            "rather than resolved by the Executor.  Model independence is "
            "neither available nor claimed and no session in BATCH-013 may be "
            "counted toward a completion_quorum attestation."
        ),
    }


# --------------------------------------------------------------------------
# 3.  Exact arithmetic on DETERMINED quantities.
# --------------------------------------------------------------------------


def tuple_label(k, m, B):
    return "T-%d-%d-B%d" % (k, m, B)


def occupancy_prediction(N, C_red, s):
    """P_pred = N(1 - exp(-lambda)) + |S_(m-2)| exp(-lambda), lambda = C_red/N."""
    lam = C_red / N
    e = math.exp(-lam)
    return N * (1.0 - e) + s * e


def exact_process_mean(N, C_red, s):
    """E[distinct] = N - (1 - s/N)[(N-1) A + C], A = (1-2/N)^(C_red/2),
    C = (1-1/N)^(C_red/2).  Evaluated in log space.  DETERMINED."""
    half = C_red // 2
    A = math.exp(half * math.log1p(-2.0 / N))
    Cc = math.exp(half * math.log1p(-1.0 / N))
    return N - (1.0 - s / N) * ((N - 1) * A + Cc)


def exact_difference_expectation(N, C_red, s):
    """PDC-15.  The exact expectation of the repaired-minus-as-recorded
    difference: (s/N)[(N-1)(1-2/N)^(C_red/2) + (1-1/N)^(C_red/2)].  DETERMINED."""
    half = C_red // 2
    A = math.exp(half * math.log1p(-2.0 / N))
    Cc = math.exp(half * math.log1p(-1.0 / N))
    return (s / N) * ((N - 1) * A + Cc)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Lentz)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-16:
            break
    return h


def reg_incomplete_beta(a, b, x):
    """I_x(a, b), the regularized incomplete beta function.  DETERMINED."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta + b * math.log1p(-x) + a * math.log(x)) * _betacf(b, a, 1.0 - x) / b


def student_t_two_sided_tail(t, df):
    """P(|T_df| > t) = I_{df/(df+t^2)}(df/2, 1/2).  DETERMINED."""
    return reg_incomplete_beta(df / 2.0, 0.5, df / (df + t * t))


def normal_two_sided_tail(x):
    """P(|Z| > x) for a standard normal.  DETERMINED."""
    return math.erfc(x / math.sqrt(2.0))


# --------------------------------------------------------------------------
# 4.  Inputs.  IV-1 INPUT INTEGRITY.
# --------------------------------------------------------------------------


def _walk_seeds(obj, out, path="$"):
    """Enumerate every integer recorded under a key named `seed` or
    `derived_seed`.  Used to MEASURE the IV-2b and IV-2c comparison pools by
    enumeration rather than to assert their size (PDC-11)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("seed", "derived_seed") and isinstance(v, int) and not isinstance(v, bool):
                out.append((path + "." + k, v))
            else:
                _walk_seeds(v, out, path + "." + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_seeds(v, out, path + "[%d]" % i)


def load_inputs():
    """Verify the five hash-bound files, build the 48 declared tuples, run IV-1."""
    findings = {"IV_1_checks": [], "IV_1_fired": False}
    hashes = {}
    for name, rel, pinned, commit in [
        ("IN-1", IN_1_PATH, IN_1_SHA256, IN_1_2_BOUND_COMMIT),
        ("IN-2", IN_2_PATH, IN_2_SHA256, IN_1_2_BOUND_COMMIT),
        ("IN-3", IN_3_PATH, IN_3_SHA256, IN_3_BOUND_COMMIT),
    ]:
        got = sha256_file(os.path.join(REPO_ROOT, rel))
        hashes[name] = {"path": rel, "bound_commit": commit, "sha256_pinned": pinned,
                        "sha256_as_read": got, "match": got == pinned}
    for i, (rel, pinned) in enumerate(IV2_EXTRA_FILES):
        got = sha256_file(os.path.join(REPO_ROOT, rel))
        hashes["IV-2-EXTRA-%d" % (i + 1)] = {
            "path": rel, "bound_commit": IN_3_BOUND_COMMIT, "sha256_pinned": pinned,
            "sha256_as_read": got, "match": got == pinned,
            "role": "READ FOR ITS DERIVED SEEDS ONLY (IV-2b).  Supplies no parameter."}
    findings["input_files"] = hashes
    bad = [k for k, v in hashes.items() if not v["match"]]
    findings["IV_1_checks"].append({
        "check": "SHA-256 of every hash-bound input file equals the pinned value",
        "files_checked": len(hashes), "mismatched_files": bad, "ok": not bad})
    if bad:
        findings["IV_1_fired"] = True
        raise InputIntegrityError(
            "IV-1: hash mismatch at %s.  A MISMATCH IS AN INVALIDATION, NOT A "
            "REPAIR OPPORTUNITY." % ", ".join(bad))

    with open(os.path.join(REPO_ROOT, IN_1_PATH)) as fh:
        in1 = json.load(fh)
    with open(os.path.join(REPO_ROOT, IN_2_PATH)) as fh:
        in2 = json.load(fh)
    with open(os.path.join(REPO_ROOT, IN_3_PATH)) as fh:
        in3 = json.load(fh)

    cells = in1["cells"]
    findings["IV_1_checks"].append({"check": "IN-1 cells array carries exactly 49 entries",
                                    "value": len(cells), "ok": len(cells) == 49})
    n_eval = in2["realised_evaluable_set"]["n_evaluable_on_measured_B"]
    n_eval_den = in2["out_of_band"]["n_eval_denominator"]
    findings["IV_1_checks"].append({"check": "IN-2 n_evaluable_on_measured_B == 49",
                                    "value": n_eval, "ok": n_eval == 49})
    findings["IV_1_checks"].append({"check": "IN-2 n_eval_denominator == 49 (cross-check only)",
                                    "value": n_eval_den, "ok": n_eval_den == 49})

    # RC-C de-duplication on measured B within each (k, m) column.  The
    # FIRST-LISTED occurrence in IN-1's cells array is the binding reference.
    order, index, merged = [], {}, []
    for idx, c in enumerate(cells):
        key = (c["k"], c["m"], c["B"])
        if key in index:
            merged.append({"tuple": tuple_label(*key),
                           "binding_reference_cell_index": index[key],
                           "binding_reference_beta": cells[index[key]]["beta"],
                           "second_occurrence_cell_index": idx,
                           "second_occurrence_beta": c["beta"],
                           "note": ("MERGED UNDER RC-C.  The tuple is DRAWN ONCE, not "
                                    "twice, which is what de-duplication means, and its "
                                    "seed string uses round(beta x 1000) of the "
                                    "FIRST-LISTED occurrence.")})
            continue
        index[key] = idx
        order.append(key)
    findings["merged_cells"] = merged
    findings["IV_1_checks"].append({
        "check": "RC-C de-duplication on measured B within (k, m) columns yields exactly 48 tuples",
        "value": len(order), "ok": len(order) == 48})

    tuples = []
    worst = {"lambda": 0.0, "exp_minus_lambda": 0.0, "T": 0.0, "P_pred": 0.0}
    z002 = {}
    for row in in3["repaired_arm"]["rows"]:
        z002[row["tuple"]] = row
    for key in order:
        c = cells[index[key]]
        k, m, B = key
        N, C_red = c["N"], c["C_red"]
        s = c["P_pred_decomposition"]["S_m_minus_2_used"]
        lbl = tuple_label(k, m, B)
        if C_red % 2 != 0:
            findings["IV_1_fired"] = True
            raise InputIntegrityError("IV-1: odd C_red at %s; NO THROW IS PERFORMED" % lbl)
        lam, e = C_red / N, math.exp(-C_red / N)
        T = s * e
        P = occupancy_prediction(N, C_red, s)
        worst["lambda"] = max(worst["lambda"], abs(lam - c["lambda_C_red_over_N"]))
        worst["exp_minus_lambda"] = max(
            worst["exp_minus_lambda"], abs(e - c["P_pred_decomposition"]["exp_minus_lambda"]))
        worst["T"] = max(worst["T"], abs(T - c["P_pred_decomposition"]["S_m_minus_2_term"]))
        worst["P_pred"] = max(worst["P_pred"], abs(P - c["P_pred"]))
        sched = 100 if C_red <= 10 ** 4 else (30 if C_red <= 10 ** 6 else 10)
        tuples.append({
            "tuple": lbl, "k": k, "p": c["p"], "N": N, "beta": c["beta"], "m": m,
            "L": c["L"], "B": B, "C_red": C_red, "C_red_is_even": c["C_red_is_even"],
            "s_S_m_minus_2": s, "n_rep": sched,
            "n_rep_source": "THE C-14 SCHEDULE, NOT RAISED.  DETERMINED from C_red.",
            "n_rep_quoted_in_IN_1": c["replicates"],
            "n_rep_matches_IN_1": sched == c["replicates"],
            "lambda": lam, "lambda_quoted": c["lambda_C_red_over_N"],
            "exp_minus_lambda": e,
            "exp_minus_lambda_quoted": c["P_pred_decomposition"]["exp_minus_lambda"],
            "T": T, "T_quoted": c["P_pred_decomposition"]["S_m_minus_2_term"],
            "P_pred": c["P_pred"], "P_pred_recomputed": P,
            "mu_001": c["antipodal"]["mean"], "s_001": c["antipodal"]["sd"],
            "is_INV_4_failing_tuple": lbl in INV4_FAILING_TUPLES,
            "source_cell_index_in_IN_1": index[key],
            "z_sem_002_QUOTED": z002[lbl]["z_sem"],
            "z_sd_002_QUOTED": z002[lbl]["z_sd"],
            "seed_002_QUOTED": z002[lbl]["derived_seed"],
        })
    findings["IV_1_checks"].append({
        "check": ("driver-recomputed lambda, exp(-lambda), T and P_pred agree with the "
                  "QUOTED values to 1e-9 absolute at all 48 tuples (192 tolerance tests; "
                  "REQUIRED EXECUTION OF IV-1 UNDER PDC-1, IV-6 DOES NOT FIRE)"),
        "max_abs_diff": worst, "tolerance": IV1_TOLERANCE,
        "tolerance_tests_performed": 4 * len(tuples),
        "ok": max(worst.values()) <= IV1_TOLERANCE})
    findings["IV_1_checks"].append({
        "check": "every declared tuple's C-14 replicate count equals the count IN-1 records",
        "mismatched_tuples": [t["tuple"] for t in tuples if not t["n_rep_matches_IN_1"]],
        "ok": all(t["n_rep_matches_IN_1"] for t in tuples)})
    for chk in findings["IV_1_checks"]:
        if not chk.get("ok", True):
            findings["IV_1_fired"] = True
    if findings["IV_1_fired"]:
        raise InputIntegrityError("IV-1 FIRED: %s" % json.dumps(findings["IV_1_checks"]))

    findings["replicate_schedule_realised"] = {
        "n_100": sum(1 for t in tuples if t["n_rep"] == 100),
        "n_100_is_a_COUNT_members": [t["tuple"] for t in tuples if t["n_rep"] == 100],
        "n_30": sum(1 for t in tuples if t["n_rep"] == 30),
        "n_30_is_a_COUNT_members": [t["tuple"] for t in tuples if t["n_rep"] == 30],
        "n_10": sum(1 for t in tuples if t["n_rep"] == 10),
        "n_10_note": ("THE 10-REPLICATE TIER IS UNREACHABLE ON THIS SET: the largest "
                      "declared C_red is 91922 at T-18-3-B82, below the 10^6 boundary."),
        "max_C_red": max(t["C_red"] for t in tuples),
    }
    findings["arity_split"] = {
        "m_2_is_a_COUNT": sum(1 for t in tuples if t["m"] == 2),
        "m_2_members": [t["tuple"] for t in tuples if t["m"] == 2],
        "m_3_is_a_COUNT": sum(1 for t in tuples if t["m"] == 3),
        "m_3_members": [t["tuple"] for t in tuples if t["m"] == 3],
    }
    findings["IV_1_verdict"] = "IV-1 DID NOT FIRE.  All five hash-bound inputs verify."
    return tuples, findings, in3


def committed_seed_pools():
    """MEASURED BY ENUMERATION, NOT ASSERTED (PDC-11)."""
    pool_002, fields_002 = [], []
    for rel in [IN_3_PATH] + [p for p, _ in IV2_EXTRA_FILES]:
        with open(os.path.join(REPO_ROOT, rel)) as fh:
            doc = json.load(fh)
        out = []
        _walk_seeds(doc, out)
        fields_002.extend([(rel, p, v) for p, v in out])
        pool_002.extend(v for _, v in out)
    with open(os.path.join(REPO_ROOT, IN_1_PATH)) as fh:
        in1 = json.load(fh)
    out1 = []
    _walk_seeds(in1, out1)
    return {
        "EXP_YIELD_002_seed_fields_is_a_COUNT": len(fields_002),
        "EXP_YIELD_002_distinct_seeds_is_a_COUNT": len(set(pool_002)),
        "EXP_YIELD_002_pool_note": (
            "PDC-11.  105 IS THE NUMBER OF DISTINCT DERIVED SEEDS in the three "
            "committed EXP-YIELD-002 run results.json files, which record 109 "
            "seed FIELDS; the four repeats are the four INV-4-failing tuples "
            "printed twice inside RUN-YIELD-002-NULL-REPAIRED, once in `rows` and "
            "once in `INV_4_failing_tuples_reported_separately`.  Both figures "
            "here are MEASURED by enumeration."),
        "IN_1_seed_fields_is_a_COUNT": len(out1),
        "IN_1_distinct_seeds_is_a_COUNT": len(set(v for _, v in out1)),
        "IN_1_pool_note": (
            "PDC-11.  IV-2c's scope is ALL derived seeds IN-1 records - 49 for "
            "the antipodal arm and 49 for the independent-throw contrast arm - "
            "and NOT the antipodal arm alone."),
        "residual_disclosed": (
            "IV-2b and IV-2c compare against the seeds recorded in files this "
            "contract reads and hash-binds.  THEY DO NOT COVER EVERY BATCH-011 "
            "DERIVED SEED, because the other BATCH-011 run records are outside "
            "this contract's permitted inputs.  What covers those instead is the "
            "DECLARED MASTER-SEED BLOCK DISJOINTNESS, which is a DESIGN FACT and "
            "NOT A PROOF about derived seeds, the derivation being a SHA-256 "
            "digest.  The residual is disclosed rather than claimed away."),
        "_pool_002": set(pool_002),
        "_pool_in1": set(v for _, v in out1),
    }


# --------------------------------------------------------------------------
# 5.  Seed derivation (contract clause seed_derivation_binding) and IV-2.
# --------------------------------------------------------------------------


def derive_tuple_seed(master, arm_label, k, beta, m, B, C_red):
    """LOW 64 BITS, unsigned little-endian, of the SHA-256 digest of the ASCII
    string joined by the single character `|` with no whitespace, in this exact
    order: master seed, arm label, k, round(beta x 1000), m, B, C_red."""
    payload = "|".join([str(master), arm_label, str(k), str(int(round(beta * 1000))),
                        str(m), str(B), str(C_red)])
    return payload, int.from_bytes(hashlib.sha256(payload.encode("ascii")).digest()[:8],
                                   "little", signed=False)


def derive_ka_seed(master, case_label, N, s, C_red):
    """master | KNOWNANSWER | case label | N | s | C_red, same digest rule."""
    payload = "|".join([str(master), "KNOWNANSWER", case_label, str(N), str(s), str(C_red)])
    return payload, int.from_bytes(hashlib.sha256(payload.encode("ascii")).digest()[:8],
                                   "little", signed=False)


KA_SEED_PARAMS = [("KA-1", 11, 3, 0), ("KA-2", 11, 11, 8), ("KA-3", 11, 3, 8),
                  ("KA-4", 11, 3, 0), ("KA-6", 11, 0, 2)]


def select_block_tuples(tuples):
    """RC-21B.  Apply the pre-registered deterministic rule to IN-1 and report
    the comparison against the six names the contract states.  THE RULE GOVERNS
    OVER THE NAMES IF THEY EVER DISAGREE."""
    m2 = [t for t in tuples if t["m"] == 2]
    ordered = sorted(range(len(m2)), key=lambda i: (m2[i]["lambda_quoted"], i))
    ranked = [m2[i] for i in ordered]
    six = [ranked[0]["tuple"], ranked[1]["tuple"], ranked[2]["tuple"],
           ranked[-3]["tuple"], ranked[-2]["tuple"], ranked[-1]["tuple"]]
    record = {
        "rule": ("Order the 29 declared m = 2 tuples by lambda = C_red/N ASCENDING, "
                 "lambda QUOTED from IN-1 as lambda_C_red_over_N.  The selected six "
                 "are THE THREE WITH THE SMALLEST LAMBDA AND THE THREE WITH THE "
                 "LARGEST LAMBDA.  Ties would break by order of first appearance in "
                 "IN-1's cells array."),
        "m_2_count_is_a_COUNT": len(m2),
        "ascending_lambda_ranks_1_to_6": [
            {"rank": i + 1, "tuple": ranked[i]["tuple"], "lambda_quoted": ranked[i]["lambda_quoted"]}
            for i in range(6)],
        "descending_lambda_ranks_1_to_3_from_the_top": [
            {"rank_from_top": i + 1, "tuple": ranked[-1 - i]["tuple"],
             "lambda_quoted": ranked[-1 - i]["lambda_quoted"]} for i in range(3)],
        "selected_six_by_the_rule": six,
        "six_named_in_the_contract": RC_21B_NAMED_SIX,
        "rule_and_names_agree_as_sets": sorted(six) == sorted(RC_21B_NAMED_SIX),
        "ties_arose": False,
        "PDC_3_nearest_non_selected_neighbour_from_below": {
            "corrected_name": ranked[3]["tuple"],
            "lambda_quoted": ranked[3]["lambda_quoted"],
            "rank": 4,
            "superseded_name_in_the_feasibility_table": "T-18-2-B82",
            "superseded_name_realised_rank": 1 + [r["tuple"] for r in ranked].index("T-18-2-B82"),
            "note": ("PDC-3 CONFIRMED BY RE-APPLICATION OF THE RULE.  The RC-21B rule "
                     "and the six selected block tuples are unaffected."),
        },
        "block_membership": {
            "the_four_m_3_tuples_carried_from_EXP_YIELD_002": INV4_FAILING_TUPLES,
            "the_six_m_2_tuples_selected_by_the_rule": six,
            "ten_is_a_COUNT_members": INV4_FAILING_TUPLES + six,
        },
    }
    by_label = {t["tuple"]: t for t in tuples}
    block = [by_label[l] for l in INV4_FAILING_TUPLES + six]
    return block, record


def all_experiment_seeds(tuples, block):
    """Derive EVERY seed of EXP-YIELD-003 and run the four IV-2 checks."""
    seeds = []
    for t in tuples:
        payload, seed = derive_tuple_seed(MASTER_SEEDS["REPLICATE-REPAIRED"],
                                          "REPLICATE-REPAIRED", t["k"], t["beta"],
                                          t["m"], t["B"], t["C_red"])
        seeds.append({"scope": "RUN-YIELD-003-REPLICATE-REPAIRED", "arm_label": "REPLICATE-REPAIRED",
                      "key": t["tuple"], "seed_string": payload, "derived_seed": seed})
    for case, N, s, C_red in KA_SEED_PARAMS:
        payload, seed = derive_ka_seed(MASTER_SEEDS["KNOWNANSWER"], case, N, s, C_red)
        seeds.append({"scope": "RUN-YIELD-003-KNOWNANSWER", "arm_label": "KNOWNANSWER",
                      "key": case, "seed_string": payload, "derived_seed": seed})
    for label in ("HIGHPREC-REPAIRED", "HIGHPREC-ASRECORDED"):
        for t in block:
            payload, seed = derive_tuple_seed(MASTER_SEEDS[label], label, t["k"], t["beta"],
                                              t["m"], t["B"], t["C_red"])
            seeds.append({"scope": "RUN-YIELD-003-HIGHPREC", "arm_label": label,
                          "key": t["tuple"], "seed_string": payload, "derived_seed": seed})

    pools = committed_seed_pools()
    values = [s["derived_seed"] for s in seeds]
    strings = [s["seed_string"] for s in seeds]
    dup_values = sorted({v for v in values if values.count(v) > 1})
    dup_strings = sorted({v for v in strings if strings.count(v) > 1})
    hit_002 = sorted(set(values) & pools["_pool_002"])
    hit_in1 = sorted(set(values) & pools["_pool_in1"])
    bad_labels = sorted({s["arm_label"] for s in seeds
                         if s["arm_label"] not in ARM_LABELS_CLOSED_SET})
    by_key = {}
    for s in seeds:
        if s["scope"] == "RUN-YIELD-003-HIGHPREC":
            by_key.setdefault(s["key"], []).append(s)
    leg_collisions = sorted(k for k, v in by_key.items()
                            if len({x["seed_string"] for x in v}) != 2
                            or len({x["derived_seed"] for x in v}) != 2)
    dev4 = [{"tuple": k,
             "HIGHPREC-REPAIRED_seed_string": [x for x in v if x["arm_label"] == "HIGHPREC-REPAIRED"][0]["seed_string"],
             "HIGHPREC-REPAIRED_derived_seed": [x for x in v if x["arm_label"] == "HIGHPREC-REPAIRED"][0]["derived_seed"],
             "HIGHPREC-ASRECORDED_seed_string": [x for x in v if x["arm_label"] == "HIGHPREC-ASRECORDED"][0]["seed_string"],
             "HIGHPREC-ASRECORDED_derived_seed": [x for x in v if x["arm_label"] == "HIGHPREC-ASRECORDED"][0]["derived_seed"],
             "seed_strings_differ": len({x["seed_string"] for x in v}) == 2,
             "derived_seeds_differ": len({x["derived_seed"] for x in v}) == 2}
            for k, v in by_key.items()]

    checks = {
        "seed_derivation_rule": (
            "The LOW 64 BITS, as an unsigned little-endian integer, of the "
            "SHA-256 digest of the ASCII string joined by the single character "
            "`|` with no whitespace: master seed, arm label, k, "
            "round(beta x 1000), m, B, C_red for a tuple; master seed, "
            "KNOWNANSWER, case label, N, s, C_red for a known-answer case.  "
            "RE-DERIVABLE BY A THIRD PARTY FROM THE CONTRACT TEXT ALONE."),
        "total_derived_seeds_is_a_COUNT": len(seeds),
        "master_seeds": {"REPLICATE-REPAIRED": 130301, "KNOWNANSWER": 130401,
                         "HIGHPREC-REPAIRED": 130501, "HIGHPREC-ASRECORDED": 130501},
        "master_seed_block_disjointness_declared": (
            "THE THREE MASTER SEEDS 130301, 130401 AND 130501 ARE FRESH and are "
            "declared disjoint from EXP-YIELD-002's four master seeds 120201, "
            "120301, 120401 and 120501 and from BATCH-011's block 110200 to "
            "110799 inclusive.  The three values are pairwise distinct.  THIS IS "
            "A DESIGN FACT ABOUT MASTER SEEDS AND IS NOT A PROOF ABOUT DERIVED "
            "SEEDS."),
        "IV_2a_two_EXP_YIELD_003_seeds_coincide": bool(dup_values),
        "IV_2a_duplicate_values": dup_values,
        "IV_2a_duplicate_seed_strings": dup_strings,
        "IV_2b_collision_with_committed_EXP_YIELD_002_seeds": hit_002,
        "IV_2c_collision_with_IN_1_seeds": hit_in1,
        "IV_2d_labels_outside_the_closed_set": bad_labels,
        "IV_2d_closed_arm_label_set": ARM_LABELS_CLOSED_SET,
        "IV_2d_high_precision_legs_sharing_a_seed_string": leg_collisions,
        "DEV_4_repair_verified_before_any_draw": dev4,
        "DEV_4_repair_verdict": (
            "THE TWO HIGH-PRECISION LEGS DERIVE DIFFERENT SEED STRINGS AND "
            "DIFFERENT SEEDS AT EVERY ONE OF THE TEN BLOCK TUPLES."
            if not leg_collisions else
            "IV-2d FIRED: the two legs share a seed string at %s" % ", ".join(leg_collisions)),
        "comparison_pools": {k: v for k, v in pools.items() if not k.startswith("_")},
    }
    fired = []
    if dup_values or dup_strings:
        fired.append("IV-2a")
    if hit_002:
        fired.append("IV-2b")
    if hit_in1:
        fired.append("IV-2c")
    if bad_labels or leg_collisions:
        fired.append("IV-2d")
    checks["IV_2_fired"] = bool(fired)
    checks["IV_2_sub_rules_that_fired"] = fired
    checks["IV_2_verdict"] = ("IV-2 DID NOT FIRE." if not fired else
                              "IV-2 FIRED at %s.  THE RUN STOPS AND REPORTS AND IS NOT "
                              "EVIDENCE." % ", ".join(fired))
    return seeds, checks


# --------------------------------------------------------------------------
# 6.  The two processes.  P-REPAIRED and P-ASRECORDED.
# --------------------------------------------------------------------------


def draw_replicates(rng, N, C_red, s, n_rep, pre_mark):
    """P-REPAIRED (pre_mark True) or P-ASRECORDED (pre_mark False).

    STEP 1, PRE-MARK.  Choose s DISTINCT bins UNIFORMLY AT RANDOM WITHOUT
    REPLACEMENT from all N bins and mark them.  The identity bin 0 IS ELIGIBLE.
    Exactly one call rng.choice(N, size=s, replace=False, shuffle=True), OMITTED
    ENTIRELY when s = 0 and omitted entirely in any P-ASRECORDED leg.

    STEP 2, THROW.  Exactly one call rng.integers(0, N, size=C_red // 2,
    dtype=numpy.int64), consumed in index order, each entry g marking bin g and
    bin (N - g) mod N.  A throw with g = 0 marks bin 0 only and is not
    corrected, not rejected and not resampled.

    STEP 3, COUNT.  The number of distinct marked bins.

    ORDER IS BINDING: step 1 strictly precedes step 2 within a replicate, and
    replicates consume the one per-tuple generator SEQUENTIALLY without
    re-seeding.
    """
    n_throw = C_red // 2
    occ = np.zeros(N, dtype=bool)
    out = np.empty(n_rep, dtype=np.int64)
    variates = 0
    do_pre_mark = bool(pre_mark) and s > 0
    for rep in range(n_rep):
        occ[:] = False
        if do_pre_mark:
            idx = rng.choice(N, size=s, replace=False, shuffle=True)
            occ[idx] = True
            variates += s
        g = rng.integers(0, N, size=n_throw, dtype=np.int64)
        variates += n_throw
        occ[g] = True
        occ[(N - g) % N] = True
        out[rep] = np.count_nonzero(occ)
    return out, variates


def stream_position_probe(seed):
    """RC-33-M, THE OPTIONAL TIGHTENING, ADOPTED.  The first three RAW 64-bit
    integers the PCG64 bit generator returns after seeding, taken from a
    SEPARATE generator instance so that the arm's own stream is untouched."""
    probe = np.random.default_rng(seed)
    return [int(x) for x in probe.bit_generator.random_raw(3)]


# --------------------------------------------------------------------------
# 7.  Arm 1: RUN-YIELD-003-KNOWNANSWER.  IV-3, cases KA-1 .. KA-8.
# --------------------------------------------------------------------------


def arm_knownanswer(tuples, deadline):
    master = MASTER_SEEDS["KNOWNANSWER"]
    cases, fired = [], []
    variates_total = 0

    payload, seed = derive_ka_seed(master, "KA-1", 11, 3, 0)
    counts, v = draw_replicates(np.random.default_rng(seed), 11, 0, 3, 1000, True)
    variates_total += v
    bad = int(np.count_nonzero(counts != 3))
    cases.append({"case": "KA-1", "label": "SAMPLED",
                  "description": ("ZERO THROWS.  N = 11, s = 3, C_red = 0, 1000 replicates.  "
                                  "Exact target distinct = 3 in EVERY replicate."),
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 0, "replicates": 1000,
                  "target": 3, "tolerance": "ZERO", "admissible_interval": [3, 3],
                  "half_band": 0.0, "replicates_off_target_is_a_COUNT": bad,
                  "min": int(counts.min()), "max": int(counts.max()), "passes": bad == 0})
    if bad:
        fired.append("KA-1")

    payload, seed = derive_ka_seed(master, "KA-2", 11, 11, 8)
    counts, v = draw_replicates(np.random.default_rng(seed), 11, 8, 11, 1000, True)
    variates_total += v
    bad = int(np.count_nonzero(counts != 11))
    cases.append({"case": "KA-2", "label": "SAMPLED",
                  "description": ("FULL PRE-MARKING.  N = 11, s = 11, C_red = 8, 1000 "
                                  "replicates.  Exact target distinct = 11 in EVERY replicate."),
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 11, "C_red": 8, "replicates": 1000,
                  "target": 11, "tolerance": "ZERO", "admissible_interval": [11, 11],
                  "half_band": 0.0, "replicates_off_target_is_a_COUNT": bad,
                  "min": int(counts.min()), "max": int(counts.max()), "passes": bad == 0})
    if bad:
        fired.append("KA-2")

    payload, seed = derive_ka_seed(master, "KA-3", 11, 3, 8)
    n = 10 ** 6
    counts, v = draw_replicates(np.random.default_rng(seed), 11, 8, 3, n, True)
    variates_total += v
    target = exact_process_mean(11, 8, 3)
    mean, sd = float(counts.mean()), float(counts.std(ddof=1))
    band = KA_SIGMA_TOLERANCE * sd / math.sqrt(n)
    diff = abs(mean - target)
    cases.append({"case": "KA-3", "label": "SAMPLED",
                  "description": ("EXACT EXPECTATION.  N = 11, s = 3, C_red = 8, hence 4 "
                                  "throws, 10^6 replicates.  Target computed by the driver "
                                  "from the closed form E = N - (1 - s/N)[(N-1)(1 - 2/N)^"
                                  "(C_red/2) + (1 - 1/N)^(C_red/2)]; NO DECIMAL IS "
                                  "HARD-CODED."),
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 8, "replicates": n,
                  "target_from_closed_form": target, "target_label": "DETERMINED",
                  "empirical_mean": mean, "empirical_sd_ddof_1": sd,
                  "tolerance": "4.000 x empirical sd / sqrt(10^6)",
                  "half_band": band,
                  "admissible_interval": [target - band, target + band],
                  "abs_difference": diff, "passes": diff <= band})
    if diff > band:
        fired.append("KA-3")

    # KA-4 and KA-5 share one stream.
    payload, seed = derive_ka_seed(master, "KA-4", 11, 3, 0)
    rng = np.random.default_rng(seed)
    n = 10 ** 6
    bin_counts = np.zeros(11, dtype=np.int64)
    occ = np.zeros(11, dtype=bool)
    ka5_bad = 0
    for _ in range(n):
        occ[:] = False
        idx = rng.choice(11, size=3, replace=False, shuffle=True)
        occ[idx] = True
        rng.integers(0, 11, size=0, dtype=np.int64)  # step 2 with C_red // 2 == 0
        bin_counts += occ
        if int(np.count_nonzero(occ)) != 3:
            ka5_bad += 1
    variates_total += 3 * n
    freqs = (bin_counts / n).tolist()
    band = KA_SIGMA_TOLERANCE * math.sqrt((3.0 / 11.0) * (8.0 / 11.0) / n)
    worst = max(abs(f - 3.0 / 11.0) for f in freqs)
    cases.append({"case": "KA-4", "label": "SAMPLED",
                  "description": ("PRE-MARKING UNIFORMITY.  N = 11, s = 3, C_red = 0, 10^6 "
                                  "pre-markings.  For EACH of the 11 bins the empirical "
                                  "marginal frequency must satisfy |frequency - 3/11| <= "
                                  "4.000 sqrt((3/11)(8/11)/10^6)."),
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 0, "pre_markings": n,
                  "target_frequency": 3.0 / 11.0, "half_band": band,
                  "half_band_quoted_in_the_contract": 0.00178145,
                  "admissible_interval": [3.0 / 11.0 - band, 3.0 / 11.0 + band],
                  "empirical_frequencies": freqs, "worst_abs_deviation": worst,
                  "passes": worst <= band})
    if worst > band:
        fired.append("KA-4")
    cases.append({"case": "KA-5", "label": "SAMPLED",
                  "description": ("PRE-MARKING WITHOUT REPLACEMENT AND COUNTED ONCE.  In "
                                  "the SAME 10^6 pre-markings of KA-4 the number of "
                                  "distinct marked bins must equal 3 in EVERY pre-marking."),
                  "stream": "REUSES THE KA-4 STREAM.  Takes no draw of its own.",
                  "seed_string": None, "derived_seed": None,
                  "N": 11, "s": 3, "C_red": 0, "pre_markings": n, "target": 3,
                  "tolerance": "ZERO", "admissible_interval": [3, 3], "half_band": 0.0,
                  "pre_markings_off_target_is_a_COUNT": ka5_bad, "passes": ka5_bad == 0})
    if ka5_bad:
        fired.append("KA-5")

    # KA-6 and KA-7 share one stream.  s = 0, so STEP 1 IS OMITTED ENTIRELY.
    payload, seed = derive_ka_seed(master, "KA-6", 11, 0, 2)
    rng = np.random.default_rng(seed)
    n = 10 ** 6
    n_one = ka6_bad = ka7_bad = 0
    for _ in range(n):
        g = rng.integers(0, 11, size=1, dtype=np.int64)
        gv = int(g[0])
        marked = set()
        marked.add(gv)
        marked.add((11 - gv) % 11)
        d = len(marked)
        if gv == 0:
            if d != 1:
                ka6_bad += 1
        elif d != 2:
            ka6_bad += 1
        if d == 1:
            n_one += 1
        if marked != {gv, (11 - gv) % 11}:
            ka7_bad += 1
    variates_total += n
    freq_one = n_one / n
    band6 = KA_SIGMA_TOLERANCE * math.sqrt((1.0 / 11.0) * (10.0 / 11.0) / n)
    dev = abs(freq_one - 1.0 / 11.0)
    cases.append({"case": "KA-6", "label": "SAMPLED",
                  "description": ("IDENTITY-BIN ACCOUNTING.  N = 11, s = 0, C_red = 2, "
                                  "hence one throw, 10^6 replicates.  STEP 1 IS OMITTED "
                                  "ENTIRELY BECAUSE s = 0.  distinct must be 1 whenever "
                                  "g = 0 and 2 otherwise, ZERO TOLERANCE on that "
                                  "implication; and |frequency(distinct = 1) - 1/11| <= "
                                  "4.000 sqrt((1/11)(10/11)/10^6)."),
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 0, "C_red": 2, "replicates": n,
                  "step_1_omitted_because_s_is_zero": True,
                  "implication_violations_is_a_COUNT": ka6_bad,
                  "implication_tolerance": "ZERO",
                  "empirical_frequency_distinct_1": freq_one,
                  "target_frequency": 1.0 / 11.0, "half_band": band6,
                  "half_band_quoted_in_the_contract": 0.00114993,
                  "admissible_interval": [1.0 / 11.0 - band6, 1.0 / 11.0 + band6],
                  "abs_deviation": dev, "passes": ka6_bad == 0 and dev <= band6})
    if ka6_bad or dev > band6:
        fired.append("KA-6")
    cases.append({"case": "KA-7", "label": "SAMPLED",
                  "description": ("ANTIPODAL PAIRING.  In the SAME 10^6 replicates of KA-6 "
                                  "the marked bin set must equal exactly {g, (11 - g) mod "
                                  "11} in EVERY replicate."),
                  "stream": "REUSES THE KA-6 STREAM.  Takes no draw of its own.",
                  "seed_string": None, "derived_seed": None,
                  "N": 11, "s": 0, "C_red": 2, "replicates": n, "tolerance": "ZERO",
                  "admissible_interval": "exact set equality", "half_band": 0.0,
                  "violations_is_a_COUNT": ka7_bad, "passes": ka7_bad == 0})
    if ka7_bad:
        fired.append("KA-7")

    # KA-8.  DETERMINED, consumes no random number.
    rows, worst8 = [], 0.0
    by_label = {t["tuple"]: t for t in tuples}
    for lbl in INV4_FAILING_TUPLES:
        t = by_label[lbl]
        recomputed = occupancy_prediction(t["N"], t["C_red"], t["s_S_m_minus_2"])
        d = abs(recomputed - t["P_pred"])
        worst8 = max(worst8, d)
        rows.append({"tuple": lbl, "N": t["N"], "C_red": t["C_red"],
                     "s_S_m_minus_2": t["s_S_m_minus_2"], "P_pred_QUOTED": t["P_pred"],
                     "P_pred_recomputed": recomputed, "abs_difference": d,
                     "label": "DETERMINED"})
    cases.append({"case": "KA-8", "label": "DETERMINED",
                  "description": ("P_pred REPRODUCTION AGAINST THE COMMITTED PACKAGE at "
                                  "the four INV-4-failing tuples, by exact "
                                  "double-precision arithmetic from the QUOTED N, C_red "
                                  "and |S_(m-2)|, requiring agreement to 1e-9 absolute at "
                                  "all four.  `four` IS A COUNT and its members are named "
                                  "in the rows below."),
                  "stream": "DETERMINED.  Consumes no random number.",
                  "seed_string": None, "derived_seed": None,
                  "tolerance": IV1_TOLERANCE, "half_band": IV1_TOLERANCE,
                  "admissible_interval": "|recomputed - QUOTED| <= 1e-9",
                  "rows": rows, "max_abs_difference": worst8, "passes": worst8 <= IV1_TOLERANCE})
    if worst8 > IV1_TOLERANCE:
        fired.append("KA-8")

    return {
        "arm": "CTRL-003-KNOWNANSWER",
        "run_id": RUN_IDS["KNOWNANSWER"],
        "feeds": "IV-3 ONLY.  It is an integrity check on the run and not a criterion.",
        "master_seed": master,
        "generators_seeded_for": ["KA-1", "KA-2", "KA-3", "KA-4", "KA-6"],
        "generators_not_seeded": {"KA-5": "reuses the KA-4 stream",
                                  "KA-7": "reuses the KA-6 stream",
                                  "KA-8": "DETERMINED, takes none"},
        "PDC_1_note": (
            "The tolerances applied in KA-3, KA-4, KA-6 and KA-8 are REQUIRED "
            "EXECUTION of IV-3 and do not fire IV-6 (PDC-1)."),
        "cases": cases,
        "IV_3_fired": bool(fired),
        "IV_3_cases_that_fired": fired,
        "IV_3_verdict": ("IV-3 DID NOT FIRE.  No known-answer case mismatched beyond its "
                         "stated tolerance."
                         if not fired else
                         "IV-3 FIRED at %s.  THE ENTIRE RUN SET IS INVALID and is never "
                         "evidence about P_pred, about the shift or about anything else."
                         % ", ".join(fired)),
        "total_random_variates_requested": variates_total,
        "cases_not_reached": [],
    }


# --------------------------------------------------------------------------
# 8.  Arm 2: RUN-YIELD-003-REPLICATE-REPAIRED.  The primary arm.
# --------------------------------------------------------------------------


def measure_tuple(t, arm_label, master, pre_mark, n_rep):
    payload, seed = derive_tuple_seed(master, arm_label, t["k"], t["beta"], t["m"],
                                      t["B"], t["C_red"])
    rng = np.random.default_rng(seed)
    t0 = time.monotonic()
    counts, variates = draw_replicates(rng, t["N"], t["C_red"], t["s_S_m_minus_2"],
                                       n_rep, pre_mark)
    elapsed = time.monotonic() - t0
    mean = float(counts.mean())
    sd = float(counts.std(ddof=1))
    sem = sd / math.sqrt(n_rep)
    return {
        "tuple": t["tuple"], "arm_label": arm_label, "seed_string": payload,
        "derived_seed": seed, "n_rep": n_rep, "label_n_rep": "DETERMINED",
        "process": "P-REPAIRED" if pre_mark else "P-ASRECORDED",
        "mean": mean, "sd_ddof_1": sd, "sem": sem,
        "relative_sd": sd / mean if mean else None,
        "min": int(counts.min()), "max": int(counts.max()),
        "label_mean": "SAMPLED", "label_sd": "SAMPLED", "label_sem": "SAMPLED",
        "throws_per_replicate": t["C_red"] // 2,
        "random_variates_requested": variates,
        "elapsed_seconds": elapsed, "label_elapsed": "MEASURED",
    }


def arm_primary(tuples, deadline, log):
    master = MASTER_SEEDS["REPLICATE-REPAIRED"]
    rows, not_reached, variates_total = [], [], 0
    for t in tuples:
        if time.monotonic() > deadline:
            not_reached = [x["tuple"] for x in tuples[len(rows):]]
            log("ST-1 CAP REACHED before %s.  STOPPING AND REPORTING." % t["tuple"])
            break
        r = measure_tuple(t, "REPLICATE-REPAIRED", master, True, t["n_rep"])
        variates_total += r["random_variates_requested"]
        mu, sd, sem = r["mean"], r["sd_ddof_1"], r["sem"]
        z_sem = (mu - t["P_pred"]) / sem
        z_sd = (mu - t["P_pred"]) / sd
        delta = mu - t["P_pred"]
        r.update({
            "k": t["k"], "m": t["m"], "B": t["B"], "beta": t["beta"], "N": t["N"],
            "C_red": t["C_red"], "s_S_m_minus_2": t["s_S_m_minus_2"],
            "P_pred_QUOTED": t["P_pred"], "label_P_pred": "QUOTED",
            "lambda": t["lambda"], "exp_minus_lambda": t["exp_minus_lambda"],
            "T": t["T"], "label_lambda_exp_T": "DETERMINED",
            "mu_001_QUOTED": t["mu_001"], "s_001_QUOTED": t["s_001"],
            "label_mu_001": "QUOTED (SAMPLED in origin)",
            "label_s_001": "QUOTED (SAMPLED in origin)",
            "is_INV_4_failing_tuple": t["is_INV_4_failing_tuple"],
            "z_sem": z_sem, "z_sd": z_sd, "abs_z_sem": abs(z_sem), "abs_z_sd": abs(z_sd),
            "label_z_sem": "SAMPLED", "label_z_sd": "SAMPLED",
            "denominator_reading_primary_OM_3": {
                "reading": "standard error of the mean, sem_rep = s_rep/sqrt(n_rep)",
                "denominator": sem, "n_rep_that_produced_it": t["n_rep"],
                "statistic": z_sem, "label": "SAMPLED"},
            "denominator_reading_secondary_OM_4": {
                "reading": "literal single-replicate standard deviation s_rep, ddof n_rep - 1",
                "denominator": sd, "n_rep_that_produced_it": t["n_rep"],
                "statistic": z_sd, "label": "SAMPLED"},
            "mean_minus_P_pred": delta,
            "sign_of_mean_minus_P_pred_OM_6": ("negative" if delta < 0 else
                                               ("positive" if delta > 0 else "zero")),
            "z_sem_002_QUOTED": t["z_sem_002_QUOTED"],
            "delta_z_OM_7": z_sem - t["z_sem_002_QUOTED"],
            "label_delta_z": "SAMPLED (this run) minus QUOTED (committed EXP-YIELD-002)",
            "seed_002_QUOTED": t["seed_002_QUOTED"],
            "seed_differs_from_the_committed_EXP_YIELD_002_seed":
                t["seed_002_QUOTED"] != r["derived_seed"],
            "identity_bin_treatment": (
                "Bin 0 is the IDENTITY BIN.  It IS ELIGIBLE to be pre-marked and is "
                "chosen with probability s/N like every other bin.  A throw with g = 0 "
                "marks bin 0 only, because (N - 0) mod N = 0, so that throw covers ONE "
                "bin rather than two; it is not corrected, not rejected and not "
                "resampled."),
        })
        rows.append(r)
        log("  %-13s n_rep=%3d mean=%.6f sd=%.6f z_sem=%+.6f z_sd=%+.6f"
            % (r["tuple"], r["n_rep"], mu, sd, z_sem, z_sd))
    return rows, not_reached, variates_total


def aggregate_primary(rows, tuples):
    """OM-5, OM-6, OM-7 and the tail checks.  OBSERVATIONS FEEDING NO CRITERION."""
    n = len(rows)
    complete = n == 48
    z = [r["z_sem"] for r in rows]
    zsd = [r["z_sd"] for r in rows]
    dz = [r["delta_z_OM_7"] for r in rows]

    def triple(v):
        k = len(v)
        mean = sum(v) / k
        var = sum((x - mean) ** 2 for x in v) / (k - 1)
        sd = math.sqrt(var)
        return {"count_is_a_COUNT": k, "mean": mean, "sample_sd_ddof_1": sd,
                "standard_error": sd / math.sqrt(k), "min": min(v), "max": max(v),
                "label": "SAMPLED"}

    om5 = triple(z)
    om5.update({
        "id": "OM-5",
        "definition": ("THE PRIMARY OBSERVATION - the arithmetic mean of the 48 z_sem "
                       "values, their sample standard deviation with denominator 47, and "
                       "that standard deviation divided by sqrt(48).  ALL THREE ARE "
                       "SAMPLED MAGNITUDES."),
        "it_feeds_no_criterion": (
            "NO THRESHOLD IS APPLIED TO ANY OF THE THREE NUMBERS by this driver, by "
            "this run record or by the results summary.  The package reports them, "
            "reports the full sorted z_sem vector, and stops."),
        "computed_over_all_48_declared_tuples": complete,
        "IV_5_note": (
            "OM-5 IS NOT COMPUTED AT ALL unless all 48 tuples were measured; a mean "
            "over fewer than 48 is a different quantity, is reported under a different "
            "name, and its member set is enumerated."),
        "sorted_z_sem_vector_verbatim": sorted(z),
        "z_sem_by_tuple_in_IN_1_order": [{"tuple": r["tuple"], "z_sem": r["z_sem"]} for r in rows],
        "largest_abs_z_sem_is_a_MAGNITUDE": max(abs(x) for x in z),
        "largest_abs_z_sem_attained_at_tuple": max(rows, key=lambda r: abs(r["z_sem"]))["tuple"],
    })
    if not complete:
        om5["id"] = "PARTIAL - NOT OM-5"
        om5["definition"] = ("A MEAN OVER FEWER THAN 48 TUPLES IS A DIFFERENT QUANTITY "
                            "AND IS NOT OM-5.  Its member set is enumerated in "
                            "member_set_enumerated.")
        om5["member_set_enumerated"] = [r["tuple"] for r in rows]

    neg = [r["tuple"] for r in rows if r["mean_minus_P_pred"] < 0]
    pos = [r["tuple"] for r in rows if r["mean_minus_P_pred"] > 0]
    zero = [r["tuple"] for r in rows if r["mean_minus_P_pred"] == 0]
    om6 = {
        "id": "OM-6", "label": "SAMPLED",
        "n_neg_is_a_COUNT": len(neg),
        "n_neg_members_named": neg,
        "n_pos_is_a_COUNT": len(pos), "n_pos_members_named": pos,
        "n_zero_is_a_COUNT": len(zero), "n_zero_members_named": zero,
        "note": ("PRED-ID EXTENDED.  n_neg IS A COUNT and the tuples it counts are named "
                 "immediately beside it.  NO WINDOW, THRESHOLD OR AGGREGATE-SIGN "
                 "CRITERION OF THE CR-4 KIND EXISTS IN THIS CONTRACT and none may be "
                 "applied to n_neg by any later record."),
    }

    om7 = triple(dz)
    om7.update({
        "id": "OM-7", "label": "SAMPLED",
        "definition": ("delta_z per tuple, this run's z_sem minus the committed "
                       "EXP-YIELD-002 repaired-arm z_sem QUOTED from IN-3 at the same "
                       "tuple label, with its 48-tuple mean, sd and standard error."),
        "sorted_delta_z_vector_verbatim": sorted(dz),
        "delta_z_by_tuple": [{"tuple": r["tuple"], "delta_z": r["delta_z_OM_7"]} for r in rows],
        "PDC_7_no_disposition_may_be_taken_on_this_mean": (
            "THE MEAN OF delta_z IS IDENTICALLY THE REPLICATED 48-TUPLE z_sem MEAN "
            "MINUS 0.36102368504276455 and therefore carries NO INFORMATION THE PRIMARY "
            "OBSERVATION DOES NOT.  NO DISPOSITION OF THE RESUME CONDITION MAY BE TAKEN "
            "ON IT, and the resume condition is evaluated - elsewhere, not here - on "
            "OM-5's mean and on no other quantity."),
        "the_identity_shown": {
            "mean_delta_z": sum(dz) / len(dz),
            "mean_z_sem_minus_committed_mean": (sum(z) / len(z)) - COMMITTED_EXP_YIELD_002_Z_SEM_MEAN,
            "committed_EXP_YIELD_002_z_sem_mean_QUOTED": COMMITTED_EXP_YIELD_002_Z_SEM_MEAN,
            "abs_difference_between_the_two_routes": abs(
                (sum(dz) / len(dz)) - ((sum(z) / len(z)) - COMMITTED_EXP_YIELD_002_Z_SEM_MEAN)),
            "note": ("The two routes agree to floating-point rounding, which is what the "
                     "identity asserts.  NO THRESHOLD IS APPLIED TO THE DIFFERENCE."),
        },
        "independence_by_construction": (
            "The two draws are independent by construction: the master seeds differ "
            "(130301 against 120201) and the arm labels differ (REPLICATE-REPAIRED "
            "against REPAIRED), so no two seed strings coincide."),
    })

    counts = {}
    for c in (1, 2, 3):
        k = sum(1 for x in z if abs(x) > c)
        n100 = sum(1 for r in rows if r["n_rep"] == 100)
        n30 = sum(1 for r in rows if r["n_rep"] == 30)
        t_exp = n100 * student_t_two_sided_tail(float(c), 99) + n30 * student_t_two_sided_tail(float(c), 29)
        z_exp = len(z) * normal_two_sided_tail(float(c))
        counts["abs_z_sem_above_%d" % c] = {
            "realised_count_is_a_COUNT": k,
            "realised_members_named": [r["tuple"] for r in rows if abs(r["z_sem"]) > c],
            "expected_count_under_the_contracts_own_stated_null": t_exp,
            "expected_count_under_the_contracts_own_stated_null_note": (
                "STUDENT-t MIXTURE of %d tuples at 99 degrees of freedom and %d at 29, "
                "evaluated here from the regularized incomplete beta function.  THIS IS "
                "THE STATED NULL." % (n100, n30)),
            "expected_count_quoted_in_PDC_10": {1: 15.412, 2: 2.389, 3: 0.187}[c],
            "expected_count_under_the_standard_normal": z_exp,
            "expected_count_under_the_standard_normal_LABEL": (
                "COMPUTED UNDER A REFERENCE DISTRIBUTION THAT IS NOT THE STATED NULL "
                "(PDC-10).  The standard normal is systematically too thin in the tail - "
                "by about 44 per cent at the 3-sigma count - so a reader comparing "
                "realised counts against it would see an apparent tail excess that is an "
                "artefact of the wrong reference."),
        }
    tail = {
        "note": ("OBSERVATIONS.  NO TEST IS PERFORMED, NOTHING FIRES, NO p-VALUE IS "
                 "COMPUTED.  Every reported count states that it is a count and names "
                 "its members.  The thresholds 1, 2 and 3 are the contract's own "
                 "MANDATED REPORTING RULE in tail_checks, executed as written; they are "
                 "not a criterion and, on the PDC-1 reading, applying a threshold the "
                 "contract itself mandates as a reporting rule is required execution of "
                 "that clause rather than an IV-6 threshold application.  SEE THE "
                 "DECLARED AMBIGUITY NOTE AMB-2."),
        "z_sem": counts,
        "z_sd_distribution_reported_in_the_same_shape": {
            "count_is_a_COUNT": len(zsd), "mean": sum(zsd) / len(zsd),
            "sample_sd_ddof_1": math.sqrt(sum((x - sum(zsd) / len(zsd)) ** 2 for x in zsd) / (len(zsd) - 1)),
            "min": min(zsd), "max": max(zsd), "sorted_vector_verbatim": sorted(zsd),
            "largest_abs_z_sd_is_a_MAGNITUDE": max(abs(x) for x in zsd),
            "largest_abs_z_sd_attained_at_tuple": max(rows, key=lambda r: abs(r["z_sd"]))["tuple"],
            "label": "SAMPLED",
        },
    }

    inv4 = [{"tuple": r["tuple"], "mean": r["mean"], "sd_ddof_1": r["sd_ddof_1"],
             "sem": r["sem"], "z_sem": r["z_sem"], "z_sd": r["z_sd"],
             "P_pred_QUOTED": r["P_pred_QUOTED"], "delta_z_OM_7": r["delta_z_OM_7"],
             "label": "SAMPLED"}
            for r in rows if r["is_INV_4_failing_tuple"]]
    return {
        "OM_5_primary_observation": om5,
        "OM_6_signs": om6,
        "OM_7_delta_z": om7,
        "tail_checks": tail,
        "INV_4_failing_tuples_reported_separately": {
            "members_named": INV4_FAILING_TUPLES,
            "four_is_a_COUNT": len(INV4_FAILING_TUPLES),
            "note": ("Reporting these four separately is a REPORTING requirement and "
                     "confers no criterion, no threshold and no separate disposition.  IT "
                     "DOES NOT RE-OPEN, RE-DISPOSE OR UN-FIRE INV-4, which fired at 4 of "
                     "the 49 criterion-evaluable cells of the BATCH-011 package and "
                     "stands untouched."),
            "rows": inv4,
        },
    }


# --------------------------------------------------------------------------
# 9.  PP-1.  The interpreter-build attempt, a SUB-BLOCK of the primary run.
# --------------------------------------------------------------------------

PP1_CANDIDATE_INTERPRETERS = [
    "/Library/Frameworks/Python.framework/Versions/3.13/bin/python3",
    "/opt/homebrew/bin/python3.13",
    "/opt/homebrew/bin/python3.14",
    "/opt/homebrew/bin/python3.11",
    "/usr/bin/python3",
    "python3.12",
]


def pp1_enumerate_builds():
    """Record for each interpreter build on the host its exact sys.version and
    sys.executable and whether numpy imports there and at which exact version."""
    found = []
    seen = set()
    for cand in PP1_CANDIDATE_INTERPRETERS:
        path = cand
        if not os.path.isabs(cand):
            try:
                path = subprocess.run(["/usr/bin/which", cand], capture_output=True,
                                      text=True).stdout.strip()
            except Exception:
                path = ""
            if not path:
                found.append({"candidate": cand, "resolved_path": None,
                              "available": False, "failure": "not found on PATH"})
                continue
        if not os.path.exists(path):
            found.append({"candidate": cand, "resolved_path": path, "available": False,
                          "failure": "path does not exist"})
            continue
        code = ("import sys, platform, json;"
                "d={'sys_version': sys.version, 'sys_executable': sys.executable,"
                "'platform_platform': platform.platform(), 'platform_machine': platform.machine(),"
                "'platform_processor': platform.processor()};"
                "\ntry:\n import numpy; d['numpy___version__']=numpy.__version__;"
                " d['numpy_importable']=True\nexcept Exception as e:\n"
                " d['numpy___version__']=None; d['numpy_importable']=False;"
                " d['numpy_import_failure']=repr(e)\nprint(json.dumps(d))")
        try:
            proc = subprocess.run([path, "-c", code], capture_output=True, text=True, timeout=120)
            info = json.loads(proc.stdout.strip().splitlines()[-1])
            info.update({"candidate": cand, "resolved_path": path, "available": True})
        except Exception as exc:
            info = {"candidate": cand, "resolved_path": path, "available": False,
                    "failure": "probe failed: %r" % (exc,)}
        key = info.get("sys_executable") or path
        if key in seen:
            info["duplicate_of_an_already_listed_build"] = True
        seen.add(key)
        found.append(info)
    return found


def pp1_run_child(interpreter, driver_path, timeout_s):
    cmd = [interpreter, driver_path, "--pp1-child"]
    t0 = time.monotonic()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s,
                              cwd=REPO_ROOT)
    except Exception as exc:
        return {"command": " ".join(cmd), "obtained": False,
                "failure": "subprocess failed: %r" % (exc,),
                "elapsed_seconds": time.monotonic() - t0}
    if proc.returncode != 0:
        return {"command": " ".join(cmd), "obtained": False,
                "returncode": proc.returncode,
                "failure": "non-zero exit; stderr tail: %s" % proc.stderr.strip()[-2000:],
                "elapsed_seconds": time.monotonic() - t0}
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as exc:
        return {"command": " ".join(cmd), "obtained": False,
                "failure": "child stdout did not parse as JSON: %r" % (exc,),
                "elapsed_seconds": time.monotonic() - t0}
    payload.update({"command": " ".join(cmd), "obtained": True,
                    "elapsed_seconds": time.monotonic() - t0})
    return payload


def z_vector_digest(z):
    return hashlib.sha256(struct.pack("<%dd" % len(z), *z)).hexdigest()


# --------------------------------------------------------------------------
# 10.  Arm 3: RUN-YIELD-003-HIGHPREC.  IT FEEDS NOTHING.
# --------------------------------------------------------------------------


def arm_highprec(block, deadline, log):
    rows, not_reached, variates_total = [], [], 0
    for t in block:
        if time.monotonic() > deadline:
            not_reached = [x["tuple"] for x in block[len(rows):]]
            log("ST-1 CAP REACHED before %s.  STOPPING AND REPORTING." % t["tuple"])
            break
        rep = measure_tuple(t, "HIGHPREC-REPAIRED", MASTER_SEEDS["HIGHPREC-REPAIRED"],
                            True, HIGHPREC_REPLICATES)
        asr = measure_tuple(t, "HIGHPREC-ASRECORDED", MASTER_SEEDS["HIGHPREC-ASRECORDED"],
                            False, HIGHPREC_REPLICATES)
        variates_total += rep["random_variates_requested"] + asr["random_variates_requested"]
        diff = rep["mean"] - asr["mean"]
        se_diff = math.sqrt(rep["sem"] ** 2 + asr["sem"] ** 2)
        exp_diff = exact_difference_expectation(t["N"], t["C_red"], t["s_S_m_minus_2"])
        rows.append({
            "tuple": t["tuple"], "k": t["k"], "m": t["m"], "B": t["B"], "N": t["N"],
            "C_red": t["C_red"], "s_S_m_minus_2": t["s_S_m_minus_2"],
            "P_pred_QUOTED": t["P_pred"], "T": t["T"], "lambda": t["lambda"],
            "label_OM_9": "DETERMINED (each also QUOTED from IN-1 and cross-checked to 1e-9)",
            "replicates_per_leg": HIGHPREC_REPLICATES,
            "is_INV_4_failing_tuple": t["is_INV_4_failing_tuple"],
            "block_membership_reason": ("carried from the EXP-YIELD-002 block (INV-4-failing, m = 3)"
                                        if t["is_INV_4_failing_tuple"] else
                                        "selected by the RC-21B lambda-extremes rule (m = 2)"),
            "leg_HIGHPREC_REPAIRED": rep,
            "leg_HIGHPREC_ASRECORDED": asr,
            "repaired_minus_asrecorded_difference": diff,
            "standard_error_of_the_difference": se_diff,
            "standard_error_basis": ("computed under the INDEPENDENCE THE DEV-4 REPAIR "
                                     "RESTORES: the two legs have different seed strings "
                                     "and therefore independent streams, so the variances "
                                     "add."),
            "label_difference": "SAMPLED",
            "exact_expectation_of_the_difference_DETERMINED": exp_diff,
            "T_DETERMINED": t["T"],
            "abs_exact_expectation_minus_T": abs(exp_diff - t["T"]),
        })
        log("  %-13s repaired=%.6f asrecorded=%.6f diff=%+.6f se_diff=%.6f"
            % (t["tuple"], rep["mean"], asr["mean"], diff, se_diff))
    return rows, not_reached, variates_total


# --------------------------------------------------------------------------
# 11.  Manifest, artifacts, and the run driver.
# --------------------------------------------------------------------------

PROTOCOL_DEVIATIONS_COMMON = [
    {
        "id": "DEV-1",
        "carried_from": "BATCH-011 and BATCH-012, same content, same reason",
        "what": ("The declared artifact set for this run is exactly manifest.json, "
                 "results.json and stdout.log.  IT ADMITS NO SEPARATE command.txt, "
                 "environment.json OR stderr.log, which the reproduction-package layout "
                 "in docs/evidence-and-reproducibility.md otherwise requires."),
        "how_it_is_handled": ("The exact command, the full environment block and the "
                              "stderr location are FOLDED INTO manifest.json, and stderr "
                              "is tee'd in-process into stdout.log so no output is lost."),
        "effect_size": ("NONE on any measured quantity.  It is a file-layout deviation "
                        "only; every field the layout requires is present, in a different "
                        "file."),
        "conservative_reading": ("A reader looking for command.txt will not find it.  The "
                                 "deviation is declared here and in every manifest so that "
                                 "the absence is a recorded choice and not a gap."),
    },
]


def common_manifest(run_id, command, git, env, inf, started_iso, ended_iso, elapsed,
                    rusage_before, rusage_after, terminal_status, validity_status,
                    validity_reason, iv_fired, iv_evaluated, deviations, extra):
    man = {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": None,
        "hypothesis_id_note": (
            "NULL AND DELIBERATELY SO.  EXP-YIELD-003 TESTS NO HYPOTHESIS and moves "
            "none.  H-YIELD-001 stays `specified` under every outcome; H-IC-001, "
            "H-STR-002 and H-SUBRES-001 stay `weakened`; H-ENDO-001 stays `approved`; "
            "H-GGM-001 stays `specified`; H-FCP-001 stays `analyzed`.  No hypothesis "
            "record is read, written, created or cited as moved by this run."),
        "heuristic_under_test": None,
        "heuristic_under_test_note": (
            "NULL.  HEUR-1, the counting heuristic B^m/(m! p), is NOT tested, NOT "
            "validated, NOT weakened and is not a measured quantity anywhere."),
        "task_id": TASK_ID, "goal_id": GOAL_ID, "batch_id": BATCH_ID,
        "contract_in_force": CONTRACT_IN_FORCE,
        "pre_dispatch_conditions": {
            "source": CONTRACT_IN_FORCE["pre_dispatch_conditions_source"],
            "count_is_a_COUNT": 15,
            "ids": ["PDC-%d" % i for i in range(1, 16)],
            "compliance": PDC_COMPLIANCE,
        },
        "command": command,
        "command_note": ("THE EXACT COMMAND AS INVOKED.  DEV-1: there is no separate "
                         "command.txt in the declared artifact set, so it is recorded "
                         "here."),
        "invocation_cwd": os.getcwd(),
        "git": git,
        "environment": env,
        "environment_note": ("DEV-1: there is no separate environment.json in the "
                             "declared artifact set, so the full environment block is "
                             "recorded here and in results.json, BEFORE THE FIRST DRAW "
                             "(IV-7)."),
        "inference": inf,
        "budget": {
            "wall_clock_seconds_per_run_ST_1": PER_RUN_WALL_CLOCK_SECONDS,
            "maximum_memory_gb_ST_1": MAXIMUM_MEMORY_GB,
            "maximum_runs": 3,
            "task_card_wall_clock_seconds": 1800,
        },
        "resource_measurements": {
            "elapsed_wall_clock_seconds": elapsed,
            "label_elapsed": "MEASURED",
            "ru_maxrss_bytes_self": rusage_after.ru_maxrss,
            "ru_maxrss_bytes_self_note": ("macOS reports ru_maxrss in BYTES.  MEASURED."),
            "ru_utime_seconds": rusage_after.ru_utime - rusage_before.ru_utime,
            "ru_stime_seconds": rusage_after.ru_stime - rusage_before.ru_stime,
            "peak_memory_gb_measured": rusage_after.ru_maxrss / float(1024 ** 3),
            "within_the_4_gb_cap": rusage_after.ru_maxrss / float(1024 ** 3) <= MAXIMUM_MEMORY_GB,
        },
        "stdout_location": "experiments/EXP-YIELD-003/runs/%s/stdout.log" % run_id,
        "stderr_location": ("experiments/EXP-YIELD-003/runs/%s/stdout.log - DEV-1: stderr "
                            "is tee'd in-process into stdout.log because the declared "
                            "artifact set has no stderr.log" % run_id),
        "raw_results_location": "experiments/EXP-YIELD-003/runs/%s/results.json" % run_id,
        "timestamps": {"started_utc": started_iso, "ended_utc": ended_iso,
                       "precision": "second"},
        "terminal_status": terminal_status,
        "validity_status": validity_status,
        "validity_reason": validity_reason,
        "invalidation_rules_fired": iv_fired,
        "invalidation_rules_evaluated": iv_evaluated,
        "certificate": {
            "kind": "none",
            "why": ("PURE MEASUREMENT RUN.  No discrete logarithm is solved, no "
                    "factor-base relation is claimed, no counterexample is produced and "
                    "no curve operation is performed, so docs/claims-and-verification.md "
                    "requires no solution certificate.  BND-6: a counterexample "
                    "certificate is NOT APPLICABLE to a replication and is recorded as "
                    "not applicable rather than as satisfied.  The evidence this run can "
                    "produce is EMPIRICAL_ONLY."),
            "independent_reverification": ("NOT APPLICABLE - there is no certificate to "
                                           "re-verify.  What IS re-verified independently "
                                           "of the sampling code is the input integrity "
                                           "(IV-1 SHA-256 pins), the seed derivation "
                                           "(IV-2, re-derivable by a third party from the "
                                           "contract text), and the simulator itself "
                                           "against exactly computable expectations "
                                           "(IV-3, run FIRST under ST-2)."),
        },
        "claim_tier": CLAIM_TIER,
        "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
        "no_success_criterion_statement": NO_SUCCESS_CRITERION_STATEMENT,
        "resume_condition_carried_verbatim": RESUME_CONDITION_VERBATIM,
        "resume_condition_not_applied_here": RESUME_CONDITION_NOT_APPLIED_HERE,
        "ST_4_no_interpretation": ST_4_NO_INTERPRETATION,
        "constrained_sentence_prohibition_PDC_2": CONSTRAINED_SENTENCE_PROHIBITION,
        "constrained_sentence_assertion_scope_PDC_2": CONSTRAINED_SENTENCE_ASSERTION_SCOPE_PDC_2,
        "boundaries": BND_1_2_3_4,
        "instrument_independence_attested": {
            "zero_curve_arithmetic": (
                "ATTESTED.  No elliptic-curve point addition, doubling, scalar "
                "multiplication, curve-order computation, curve or generator selection, "
                "discrete-logarithm table, factor base, sum set, census, summation "
                "polynomial, Groebner basis or polynomial system solve was performed.  "
                "The run is a balls-in-bins simulation over the integer residue range."),
            "forbidden_imports": (
                "ATTESTED.  Nothing under harness/, tools/ or orchestration/ was "
                "imported, executed or read; experiments/EXP-YIELD-001/driver/"
                "yield_census.py was never opened; experiments/EXP-YIELD-002/driver/"
                "repaired_null.py was read by the authoring session and is NOT imported "
                "or executed here.  The only third-party dependency is numpy."),
            "provenance_of_the_driver": REUSE_FROM_EXP_YIELD_002,
            "no_E_no_R": ("ATTESTED.  No occupancy-normalised efficiency E and no yield "
                          "ratio R is computed, quoted or reported, and the value 0.85 "
                          "appears nowhere."),
            "RC_F": ("RC-F IS UNDISCHARGED.  This run makes no progress on it and NO "
                     "DISCHARGE IS CLAIMED."),
            "RC_B": "RC-B IS OPEN and is untouched: this contract specifies zero curve compute.",
        },
        "scale_relevance": {
            "tier": "toy",
            "scoped_to": ("the 48 declared parameter tuples; the four tested field sizes "
                          "k in {12, 14, 16, 18} and their quoted group orders 4001, "
                          "16619, 65633 and 261707; the frozen beta grid as realised in "
                          "the source package; arities m in {2, 3}; the one prime-order "
                          "curve per size of the source package; THIS simulator, THIS "
                          "driver, THIS numpy build, THIS interpreter build, THIS "
                          "platform and THIS budget; and the occupancy CONTROL OBJECT "
                          "alone."),
            "not_a_cryptanalytic_result": (
                "NOTHING MEASURED HERE IS EVIDENCE ABOUT CRYPTOGRAPHIC-SIZE CURVES IN "
                "EITHER DIRECTION.  This is not a cryptanalytic result, not an attack, "
                "not an attack improvement, not an exponent result, not a closure and "
                "not an impossibility claim."),
        },
        "protocol_deviations": deviations,
        "required_artifacts_this_run": [
            "experiments/EXP-YIELD-003/runs/%s/manifest.json" % run_id,
            "experiments/EXP-YIELD-003/runs/%s/results.json" % run_id,
            "experiments/EXP-YIELD-003/runs/%s/stdout.log" % run_id,
        ],
        "eleven_declared_artifact_paths": ELEVEN_DECLARED_PATHS,
        "no_commit_made": ("NO COMMIT WAS MADE BY THIS RUN.  TASK-20260729-036 commits "
                           "these artifacts and nothing else does."),
    }
    man.update(extra)
    return man


ELEVEN_DECLARED_PATHS = [
    "experiments/EXP-YIELD-003/driver/replicate_repaired_null.py",
    "experiments/EXP-YIELD-003/results/summary.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-REPLICATE-REPAIRED/manifest.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-REPLICATE-REPAIRED/results.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-REPLICATE-REPAIRED/stdout.log",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-HIGHPREC/manifest.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-HIGHPREC/results.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-HIGHPREC/stdout.log",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-KNOWNANSWER/manifest.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-KNOWNANSWER/results.json",
    "experiments/EXP-YIELD-003/runs/RUN-YIELD-003-KNOWNANSWER/stdout.log",
]


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False)
        fh.write("\n")


# --------------------------------------------------------------------------
# 12.  Declared ambiguities.  ST-3 requires them to be reported, never applied
#      silently.
# --------------------------------------------------------------------------

DECLARED_AMBIGUITIES = [
    {
        "id": "AMB-1",
        "clause": "IV-6 SCOPE BREACH versus IV-1 and IV-3",
        "the_collision": (
            "IV-6 invalidates a run that `applies any threshold to any quantity of this "
            "contract`, while IV-1 mandates a 1e-9 absolute tolerance on four recomputed "
            "quantities at each of the 48 tuples - 192 tolerance tests - and IV-3 "
            "mandates 4.000-sigma tolerances at KA-3, KA-4 and KA-6 and a 1e-9 tolerance "
            "at KA-8.  READ LITERALLY THE TWO RULES INVALIDATE EACH OTHER and a literal "
            "Executor stops under ST-3 before the first draw."),
        "how_it_was_resolved": (
            "BY PDC-1, RECORDED VERBATIM IN THE TASK-20260729-034 RECEIPT BEFORE "
            "DISPATCH.  IV-6's threshold clause is scoped to the observation quantities "
            "OM-1 through OM-9 and quantities derived from them, and does not reach the "
            "tolerances IV-1 and IV-3 themselves mandate.  Applying those tolerances is "
            "REQUIRED EXECUTION of those rules and does not fire IV-6."),
        "status": "RESOLVED BY A PRE-DISPATCH CONDITION.  NOT resolved by the Executor.",
    },
    {
        "id": "AMB-2",
        "clause": "IV-6 versus the contract's own MANDATED tail-check counts and OM-6 sign count",
        "the_collision": (
            "The contract's tail_checks clause MANDATES reporting the counts of |z_sem| "
            "above 1, above 2 and above 3, and OM-6 MANDATES the count of tuples with a "
            "strictly negative sign.  Each is literally an application of a threshold to "
            "a quantity derived from OM-3 or OM-1, which IV-6 read literally forbids."),
        "how_it_was_resolved": (
            "BY THE SAME STRUCTURE PDC-1 SETTLES, APPLIED TO A CLAUSE OF IDENTICAL SHAPE "
            "AND RECORDED RATHER THAN APPLIED SILENTLY.  A threshold the contract itself "
            "MANDATES AS A REPORTING RULE is required execution of that clause, exactly "
            "as IV-1's and IV-3's mandated tolerances are.  The contract states of these "
            "counts that NO TEST IS PERFORMED, NOTHING FIRES and NO p-VALUE IS COMPUTED, "
            "so no criterion is created by computing them.  REFUSING to compute them "
            "would breach the tail_checks and OM-6 clauses.  THE EXECUTOR RECORDS THIS "
            "READING AS ITS OWN AND FLAGS IT FOR THE REVIEWER; it is not covered by the "
            "letter of PDC-1, which names only IV-1, KA-8, KA-3, KA-4 and KA-6."),
        "status": ("DECLARED.  If a reviewer rules the other way, the affected quantities "
                   "are the tail-check counts and n_neg, and NOTHING ELSE IN THE PACKAGE "
                   "DEPENDS ON THEM - the primary observation OM-5 is a mean, a standard "
                   "deviation and a standard error, computed without any threshold."),
    },
    {
        "id": "AMB-3",
        "clause": "PP_1_the_interpreter_build_attempt.the_procedure",
        "the_collision": (
            "The clause fires `IF AND ONLY IF a build different from the primary one has "
            "an importable numpy` and then says to re-execute the primary arm `UNDER "
            "THAT BUILD`, in the SINGULAR.  THIS HOST OFFERS MORE THAN ONE QUALIFYING "
            "BUILD, and the contract does not say which one to use."),
        "how_it_was_resolved": (
            "BY RUNNING EVERY QUALIFYING BUILD AND LABELLING EACH SEPARATELY, rather "
            "than by silently choosing one.  Running a superset satisfies the clause's "
            "requirement and removes the unrecorded choice.  Each PP-1 leg is reported "
            "as its own separately labelled observation, none is pooled with, averaged "
            "into or substituted for the primary observation, and none is compared "
            "against the resume-condition thresholds (PDC-8).  DECLARED AS DEVIATION "
            "DEV-6."),
        "status": "DECLARED AS A PROTOCOL DEVIATION WITH ITS EFFECT SIZE.",
    },
]


# --------------------------------------------------------------------------
# 13.  PP-1 child mode.  WRITES NO FILE (PDC-13).
# --------------------------------------------------------------------------


def pp1_child():
    """Re-execute the primary 48-tuple arm under this interpreter build, under
    the SAME master seed 130301 and the SAME arm label REPLICATE-REPAIRED, and
    return the numbers to the parent ON STDOUT.  NO FILE IS WRITTEN."""
    env = environment_block("not-computed-in-child", "not-set-in-child")
    t0 = time.monotonic()
    tuples, findings, _ = load_inputs()
    rows = []
    for t in tuples:
        r = measure_tuple(t, "REPLICATE-REPAIRED", MASTER_SEEDS["REPLICATE-REPAIRED"],
                          True, t["n_rep"])
        z_sem = (r["mean"] - t["P_pred"]) / r["sem"]
        rows.append({"tuple": t["tuple"], "mean": r["mean"], "sd_ddof_1": r["sd_ddof_1"],
                     "sem": r["sem"], "z_sem": z_sem, "derived_seed": r["derived_seed"],
                     "seed_string": r["seed_string"]})
    z = [r["z_sem"] for r in rows]
    mean = sum(z) / len(z)
    sd = math.sqrt(sum((x - mean) ** 2 for x in z) / (len(z) - 1))
    payload = {
        "pp1_child": True,
        "environment": {k: env[k] for k in ("sys_version", "sys_executable",
                                            "platform_platform", "platform_machine",
                                            "platform_processor", "numpy___version__")},
        "environment_recorded_before_the_first_draw": True,
        "input_integrity_verified": {k: v["match"] for k, v in findings["input_files"].items()},
        "tuples_measured_is_a_COUNT": len(rows),
        "rows": rows,
        "z_sem_mean": mean, "z_sem_sample_sd_ddof_1": sd,
        "z_sem_standard_error": sd / math.sqrt(len(z)),
        "z_sem_vector_sha256": z_vector_digest(z),
        "mean_vector_sha256": hashlib.sha256(
            struct.pack("<%dd" % len(rows), *[r["mean"] for r in rows])).hexdigest(),
        "elapsed_seconds": time.monotonic() - t0,
        "wrote_no_file": True,
    }
    sys.stdout.write(json.dumps(payload) + "\n")
    return 0


# --------------------------------------------------------------------------
# 14.  The run driver.
# --------------------------------------------------------------------------


def execute_run(arm_key):
    run_id = RUN_IDS[arm_key]
    run_dir = os.path.join(REPO_ROOT, "experiments", "EXP-YIELD-003", "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    stdout_path = os.path.join(run_dir, "stdout.log")

    rlimit_status = None
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (MAXIMUM_MEMORY_GB * 1024 ** 3, hard))
        rlimit_status = "RLIMIT_AS set to %d bytes" % (MAXIMUM_MEMORY_GB * 1024 ** 3)
    except Exception as exc:
        rlimit_status = ("RLIMIT_AS could not be set on this host (%r); the %d GB cap is "
                         "ENFORCED BY MEASUREMENT (ru_maxrss recorded and compared against "
                         "the cap in the manifest) and by the design's peak footprint of "
                         "one boolean array of length at most 261707 plus the parsed input "
                         "documents." % (exc, MAXIMUM_MEMORY_GB))

    rusage_before = resource.getrusage(resource.RUSAGE_SELF)
    started_iso = utc_now()
    t_start = time.monotonic()
    deadline = t_start + PER_RUN_WALL_CLOCK_SECONDS

    handle = open(stdout_path, "w")
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout = Tee(real_out, handle)
    sys.stderr = Tee(real_err, handle)

    def log(msg):
        print(msg)
        sys.stdout.flush()

    terminal_status = "failed_implementation"
    validity_status = "invalid"
    validity_reason = "the run did not reach its own terminal block"
    iv_fired, iv_evaluated = [], {}
    results = {}
    deviations = list(PROTOCOL_DEVIATIONS_COMMON)
    extra_manifest = {}

    driver_sha = sha256_file(os.path.abspath(__file__))
    env = environment_block(driver_sha, rlimit_status)
    git = git_state()
    inf = inference_block()
    command = " ".join([sys.executable,
                        "experiments/EXP-YIELD-003/driver/replicate_repaired_null.py",
                        "--run", run_id])

    try:
        log("=" * 78)
        log("EXP-YIELD-003  %s" % run_id)
        log("TASK-20260729-035  GOAL-ECDLP-001  BATCH-013")
        log("=" * 78)
        log("CONTRACT IN FORCE: experiments/EXP-YIELD-003/specification.yaml at de6fbb75")
        log("APPROVAL: recorded in the TASK-20260729-034 snapshot receipt as APPROVED,")
        log("  conditional on PDC-1 .. PDC-15 recorded verbatim.  The frozen file's")
        log("  `status: review_required` and `approved_by: null` are D-1 PROPHYLAXIS and")
        log("  ARE NOT EVIDENCE OF NON-APPROVAL.")
        log("")
        log(NO_SUCCESS_CRITERION_STATEMENT)
        log("")
        log(ST_4_NO_INTERPRETATION)
        log("")
        log("--- ENVIRONMENT, RECORDED BEFORE THE FIRST DRAW (IV-7) ---")
        for key in ("sys_version", "sys_executable", "platform_platform",
                    "platform_machine", "platform_processor", "numpy___version__"):
            log("  %-22s %s" % (key, env[key]))
        log("  committed reference environment (QUOTED, EXP-YIELD-002 manifest at c7189f80):")
        log("    python 3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22), "
            "macOS-26.6-arm64-arm-64bit-Mach-O, arm64, arm, numpy 2.4.0")
        log("  THE PLATFORM CANNOT VARY: a genuinely different OPERATING SYSTEM and a")
        log("  genuinely different MACHINE ARCHITECTURE are NOT AVAILABLE - this harness")
        log("  runs on ONE macOS arm64 machine.  NO RECORD PRODUCED BY THIS BATCH MAY")
        log("  DESCRIBE THIS EXPERIMENT AS A FRESH-PLATFORM REPLICATION.")
        log("")
        log("--- GIT STATE ---")
        log("  commit %s  branch %s  dirty %s (%d entries)"
            % (git["commit"], git["branch"], git["dirty"], git["dirty_entry_count"]))
        log("")

        log("--- IV-1 INPUT INTEGRITY ---")
        tuples, findings, in3 = load_inputs()
        for k, v in findings["input_files"].items():
            log("  %-14s sha256 match=%s  %s" % (k, v["match"], v["path"]))
        log("  %s" % findings["IV_1_verdict"])
        log("  48 declared tuples built by RC-C de-duplication; 37 at 100 replicates, "
            "11 at 30 (COUNTS; members named in results.json).")
        iv_evaluated["IV-1"] = findings["IV_1_verdict"]

        log("")
        log("--- RC-21B BLOCK SELECTION, RULE RE-APPLIED TO IN-1 ---")
        block, block_record = select_block_tuples(tuples)
        log("  selected six m = 2 tuples by the rule: %s"
            % ", ".join(block_record["selected_six_by_the_rule"]))
        log("  rule and the contract's six names agree as sets: %s"
            % block_record["rule_and_names_agree_as_sets"])
        log("  PDC-3: nearest non-selected lambda neighbour from below is %s at %.8f (rank 4);"
            % (block_record["PDC_3_nearest_non_selected_neighbour_from_below"]["corrected_name"],
               block_record["PDC_3_nearest_non_selected_neighbour_from_below"]["lambda_quoted"]))
        log("         T-18-2-B82 is rank %d."
            % block_record["PDC_3_nearest_non_selected_neighbour_from_below"]["superseded_name_realised_rank"])
        if not block_record["rule_and_names_agree_as_sets"]:
            raise AmbiguityStop(
                "ST-3: the RC-21B rule and the six names in the contract disagree.  THE "
                "RULE GOVERNS, and the disagreement is a defect in the contract to be "
                "reported rather than repaired in flight.")

        log("")
        log("--- IV-2 SEED INTEGRITY AND COLLISION, BEFORE ANY DRAW ---")
        seeds, seed_checks = all_experiment_seeds(tuples, block)
        log("  %d derived seeds of EXP-YIELD-003 (a COUNT: 48 primary + 5 known-answer + "
            "20 high-precision legs)" % seed_checks["total_derived_seeds_is_a_COUNT"])
        log("  comparison pools MEASURED BY ENUMERATION: %d EXP-YIELD-002 seed fields, "
            "%d distinct; %d IN-1 seeds, %d distinct"
            % (seed_checks["comparison_pools"]["EXP_YIELD_002_seed_fields_is_a_COUNT"],
               seed_checks["comparison_pools"]["EXP_YIELD_002_distinct_seeds_is_a_COUNT"],
               seed_checks["comparison_pools"]["IN_1_seed_fields_is_a_COUNT"],
               seed_checks["comparison_pools"]["IN_1_distinct_seeds_is_a_COUNT"]))
        log("  %s" % seed_checks["IV_2_verdict"])
        log("  DEV-4 REPAIR: %s" % seed_checks["DEV_4_repair_verdict"])
        iv_evaluated["IV-2"] = seed_checks["IV_2_verdict"]
        if seed_checks["IV_2_fired"]:
            iv_fired.append("IV-2")
            raise AmbiguityStop("IV-2 FIRED BEFORE ANY DRAW: %s" % seed_checks["IV_2_verdict"])

        base = {
            "schema": "crypto.autoresearch.run_results.v1",
            "run_id": run_id, "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID,
            "goal_id": GOAL_ID, "batch_id": BATCH_ID,
            "contract_in_force": CONTRACT_IN_FORCE,
            "claim_tier": CLAIM_TIER,
            "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
            "no_success_criterion_statement": NO_SUCCESS_CRITERION_STATEMENT,
            "resume_condition_carried_verbatim": RESUME_CONDITION_VERBATIM,
            "resume_condition_not_applied_here": RESUME_CONDITION_NOT_APPLIED_HERE,
            "ST_4_no_interpretation": ST_4_NO_INTERPRETATION,
            "constrained_sentence_prohibition_PDC_2": CONSTRAINED_SENTENCE_PROHIBITION,
            "constrained_sentence_assertion_scope_PDC_2": CONSTRAINED_SENTENCE_ASSERTION_SCOPE_PDC_2,
            "boundaries": BND_1_2_3_4,
            "environment": env,
            "environment_recorded_before_the_first_draw": True,
            "platform_cannot_vary": (
                "STATED PLAINLY RATHER THAN LEFT TO BE INFERRED FROM AN ABSENT FIELD.  A "
                "genuinely different OPERATING SYSTEM and a genuinely different MACHINE "
                "ARCHITECTURE ARE NOT AVAILABLE: this harness runs on ONE macOS arm64 "
                "machine.  NO RECORD PRODUCED BY THIS BATCH MAY DESCRIBE THIS EXPERIMENT "
                "AS A FRESH-PLATFORM REPLICATION."),
            "input_integrity_IV_1": findings,
            "seed_integrity_IV_2": seed_checks,
            "all_derived_seeds_of_EXP_YIELD_003": seeds,
            "RC_21B_block_selection": block_record,
            "declared_ambiguities": DECLARED_AMBIGUITIES,
            "pre_dispatch_condition_compliance": PDC_COMPLIANCE,
            "timestamps": {"started_utc": started_iso},
        }

        if arm_key == "KNOWNANSWER":
            log("")
            log("--- ARM 1 of 3 (ST-2 order): KNOWN-ANSWER CASES KA-1 .. KA-8 ---")
            ka = arm_knownanswer(tuples, deadline)
            log("  %s" % ka["IV_3_verdict"])
            for c in ka["cases"]:
                log("  %-5s passes=%s" % (c["case"], c["passes"]))
            iv_evaluated["IV-3"] = ka["IV_3_verdict"]
            if ka["IV_3_fired"]:
                iv_fired.append("IV-3")
            base["known_answer_arm"] = ka
            base["total_random_variates_requested"] = ka["total_random_variates_requested"]
            not_reached = []
            terminal_status = "completed_invalid" if ka["IV_3_fired"] else "completed_valid"
            validity_status = "invalid" if ka["IV_3_fired"] else "valid"
            validity_reason = ka["IV_3_verdict"]

        elif arm_key == "REPLICATE-REPAIRED":
            log("")
            log("--- ARM 2 of 3 (ST-2 order): THE PRIMARY ARM, 48 TUPLES, P-REPAIRED ---")
            log("  master seed 130301, arm label REPLICATE-REPAIRED, C-14 schedule NOT RAISED")
            rows, not_reached, variates = arm_primary(tuples, deadline, log)
            base["primary_arm"] = {
                "arm": "CTRL-003-REPLICATE-REPAIRED", "run_id": run_id,
                "process": "P-REPAIRED",
                "master_seed": MASTER_SEEDS["REPLICATE-REPAIRED"],
                "arm_label": "REPLICATE-REPAIRED",
                "feeds": ("NO CRITERION.  It produces the primary OBSERVATION OM-5 and the "
                          "secondary observations OM-6 and OM-7, all of which feed nothing."),
                "rows": rows,
                "tuples_measured_is_a_COUNT": len(rows),
                "tuples_not_reached_named_IV_5": not_reached,
                "IV_5_verdict": ("IV-5 DID NOT FIRE.  All 48 declared tuples were measured."
                                 if not not_reached else
                                 "IV-5: the run did not reach %d declared tuples, NAMED HERE: %s"
                                 % (len(not_reached), ", ".join(not_reached))),
                "total_random_variates_requested": variates,
                "stream_position_probe_RC_33_M": {
                    "note": ("RC-33-M, THE OPTIONAL TIGHTENING, ADOPTED.  The first three "
                             "RAW 64-bit integers the per-tuple PCG64 bit generator returns "
                             "after seeding, taken from a SEPARATE generator instance so "
                             "the arm's own stream is untouched.  It pins the stream "
                             "position that the contract's named-calls clause makes "
                             "load-bearing, and detects a step-order defect that no "
                             "known-answer case can see.  NO THRESHOLD IS APPLIED."),
                    "tuple": rows[0]["tuple"] if rows else None,
                    "derived_seed": rows[0]["derived_seed"] if rows else None,
                    "first_three_raw_uint64":
                        stream_position_probe(rows[0]["derived_seed"]) if rows else None,
                },
            }
            if not_reached:
                iv_fired.append("IV-5")
            iv_evaluated["IV-5"] = base["primary_arm"]["IV_5_verdict"]
            base["total_random_variates_requested"] = variates
            if len(rows) == 48:
                agg = aggregate_primary(rows, tuples)
                base["observations"] = agg
                log("")
                log("--- OM-5 THE PRIMARY OBSERVATION.  IT FEEDS NO CRITERION. ---")
                log("  count (a COUNT)         48")
                log("  mean   z_sem            %.10f" % agg["OM_5_primary_observation"]["mean"])
                log("  sample sd (ddof 47)     %.10f"
                    % agg["OM_5_primary_observation"]["sample_sd_ddof_1"])
                log("  standard error          %.10f"
                    % agg["OM_5_primary_observation"]["standard_error"])
                log("  THESE ARE MAGNITUDES.  NO THRESHOLD IS APPLIED TO THEM HERE, NO")
                log("  BRANCH IS DECLARED AND THE RESUME CONDITION IS NOT APPLIED (ST-4).")
                log("  n_neg (a COUNT)         %d" % agg["OM_6_signs"]["n_neg_is_a_COUNT"])
                log("  n_neg members: %s" % ", ".join(agg["OM_6_signs"]["n_neg_members_named"]))
            else:
                log("")
                log("OM-5 IS NOT COMPUTED: fewer than 48 tuples were measured (IV-5).")
                base["observations"] = {
                    "OM_5_primary_observation": None,
                    "why": ("IV-5.  The primary observation OM-5 IS NOT COMPUTED AT ALL "
                            "unless all 48 tuples were measured.  The tuples not reached "
                            "are named in primary_arm.tuples_not_reached_named_IV_5."),
                }

            # ---- PP-1, a declared SUB-BLOCK of this run ----------------------
            log("")
            log("--- PP-1 INTERPRETER-BUILD ATTEMPT (a declared SUB-BLOCK, not a fourth run) ---")
            builds = pp1_enumerate_builds()
            for b in builds:
                log("  %-52s available=%s numpy=%s"
                    % (b.get("resolved_path") or b.get("candidate"), b.get("available"),
                       b.get("numpy___version__") if b.get("available") else b.get("failure")))
            primary_exe = os.path.realpath(sys.executable)
            qualifying = []
            for b in builds:
                if not b.get("available") or not b.get("numpy_importable"):
                    continue
                if os.path.realpath(b["sys_executable"]) == primary_exe:
                    continue
                if any(os.path.realpath(q["sys_executable"]) == os.path.realpath(b["sys_executable"])
                       for q in qualifying):
                    continue
                qualifying.append(b)
            legs = []
            if len(rows) == 48:
                z_primary = [r["z_sem"] for r in rows]
                mu_primary = [r["mean"] for r in rows]
                primary_digest = z_vector_digest(z_primary)
                primary_mu_digest = hashlib.sha256(
                    struct.pack("<48d", *mu_primary)).hexdigest()
            else:
                z_primary, primary_digest, primary_mu_digest = None, None, None
            for i, b in enumerate(qualifying):
                if time.monotonic() > deadline:
                    legs.append({"leg": "PP-1-%s" % chr(65 + i), "obtained": False,
                                 "failure": "ST-1 cap reached before this leg was attempted",
                                 "interpreter": b["sys_executable"]})
                    continue
                log("  running PP-1 leg %s under %s (numpy %s)"
                    % (chr(65 + i), b["sys_executable"], b["numpy___version__"]))
                child = pp1_run_child(b["sys_executable"], os.path.abspath(__file__),
                                      max(30.0, deadline - time.monotonic()))
                leg = {"leg": "PP-1-%s" % chr(65 + i), "interpreter": b["sys_executable"]}
                leg.update(child)
                if child.get("obtained") and z_primary is not None:
                    child_z = [r["z_sem"] for r in child["rows"]]
                    differing = [child["rows"][j]["tuple"] for j in range(len(child_z))
                                 if child_z[j] != z_primary[j]]
                    leg["stream_equality_PDC_8"] = {
                        "z_sem_vector_bit_identical_to_the_primary_arm":
                            child["z_sem_vector_sha256"] == primary_digest,
                        "mean_vector_bit_identical_to_the_primary_arm":
                            child["mean_vector_sha256"] == primary_mu_digest,
                        "primary_arm_z_sem_vector_sha256": primary_digest,
                        "pp1_z_sem_vector_sha256": child["z_sem_vector_sha256"],
                        "tuples_whose_z_sem_differs_is_a_COUNT": len(differing),
                        "tuples_whose_z_sem_differs_named": differing,
                        "numpy_version_primary_arm": env["numpy___version__"],
                        "numpy_version_pp1": child["environment"]["numpy___version__"],
                        "numpy_versions_equal":
                            child["environment"]["numpy___version__"] == env["numpy___version__"],
                        "declared_case": None,
                        "second_fresh_stream_mean_if_any": None,
                    }
                    se = leg["stream_equality_PDC_8"]
                    if se["numpy_versions_equal"] and se["z_sem_vector_bit_identical_to_the_primary_arm"]:
                        se["declared_case"] = (
                            "CASE ONE OF THE CONTRACT'S THREE-CASE STATEMENT - the second "
                            "build carries THE SAME numpy version and the stream is "
                            "IDENTICAL.  This is what a correct pipeline produces by "
                            "construction for the random stream; PP-1 here tests ONLY that "
                            "the interpreter build does not change the arithmetic, and it "
                            "CANNOT separate a driver property from a build property.  It "
                            "is NOT a portability result and NOT a cross-version "
                            "determinism result (BND-4).  The `by construction` half is "
                            "exact for the stream and empirical for the float64 "
                            "reductions, the same numpy version built for a different "
                            "CPython being a different binary.")
                    elif se["numpy_versions_equal"]:
                        se["declared_case"] = (
                            "CASE ONE WITH A DIFFERENCE - same numpy version, DIFFERENT "
                            "numbers.  THE CONTRACT STATES IN ADVANCE THAT A DIFFERENCE IN "
                            "CASE ONE WOULD BE A FINDING ABOUT THE PIPELINE, and it is "
                            "reported as one.")
                    elif se["z_sem_vector_bit_identical_to_the_primary_arm"]:
                        se["declared_case"] = (
                            "THE FOURTH CASE - DIFFERENT numpy VERSION, IDENTICAL STREAM - "
                            "WHICH THE CONTRACT'S THREE-CASE STATEMENT DOES NOT ENUMERATE "
                            "(PDC-8, OBJ-8).  Classification is on STREAM EQUALITY and not "
                            "on version equality.  A reader applying the stated taxonomy "
                            "would misclassify this as case two, `confounds build with "
                            "stream`, when in fact NOTHING VARIED in the numbers.  UNDER NO "
                            "CASE MAY THIS BE READ AS A PORTABILITY RESULT, AS A "
                            "CROSS-VERSION DETERMINISM RESULT OR AS A SEPARATION OF THE "
                            "DRIVER FROM THE BUILD.")
                    else:
                        se["declared_case"] = (
                            "CASE TWO - DIFFERENT numpy VERSION AND A DIFFERENT STREAM.  "
                            "PP-1 is therefore a SECOND FRESH-STREAM DRAW that also happens "
                            "to be under a different build, so it CONFOUNDS BUILD WITH "
                            "STREAM and cannot attribute any difference to either.")
                        se["second_fresh_stream_mean_if_any"] = {
                            "z_sem_mean": child["z_sem_mean"],
                            "z_sem_sample_sd_ddof_1": child["z_sem_sample_sd_ddof_1"],
                            "z_sem_standard_error": child["z_sem_standard_error"],
                            "label": "SAMPLED - A SEPARATELY LABELLED OBSERVATION",
                            "PDC_8_fence": ("THIS MEAN IS NEVER POOLED WITH, AVERAGED INTO, "
                                            "SUBSTITUTED FOR, OR COMPARED AGAINST THE "
                                            "RESUME-CONDITION THRESHOLDS.  It is not OM-5."),
                        }
                legs.append(leg)
                log("    obtained=%s" % leg.get("obtained"))
            base["PP_1_interpreter_build_attempt"] = {
                "it_is_not_a_fourth_run": (
                    "PP-1 IS A DECLARED SUB-BLOCK OF RUN-YIELD-003-REPLICATE-REPAIRED.  It "
                    "creates no fourth run identifier, no fourth run directory and no "
                    "additional artifact path.  It feeds no criterion and is never pooled "
                    "with, averaged into or substituted for the primary observation OM-5."),
                "mechanics_PDC_13": (
                    "The second interpreter is invoked as a SUBPROCESS running this single "
                    "declared driver file with --pp1-child and returns its numbers ON "
                    "STDOUT.  NO FILE IS WRITTEN inside the repository and no temporary "
                    "file is created anywhere, so the artifact set stays at eleven."),
                "primary_interpreter": {"sys_version": env["sys_version"],
                                        "sys_executable": env["sys_executable"],
                                        "numpy___version__": env["numpy___version__"]},
                "builds_enumerated_on_this_host": builds,
                "qualifying_second_builds_is_a_COUNT": len(qualifying),
                "qualifying_second_builds_named": [b["sys_executable"] for b in qualifying],
                "legs": legs,
                "what_was_obtained_and_what_was_not": {
                    "obtained": [l["leg"] for l in legs if l.get("obtained")],
                    "not_obtained": [{"leg": l["leg"], "interpreter": l.get("interpreter"),
                                      "failure": l.get("failure")}
                                     for l in legs if not l.get("obtained")],
                    "builds_without_an_importable_numpy": [
                        {"interpreter": b.get("resolved_path"),
                         "sys_version": b.get("sys_version"),
                         "numpy_import_failure": b.get("numpy_import_failure")}
                        for b in builds if b.get("available") and not b.get("numpy_importable")],
                    "builds_not_present_on_this_host": [
                        {"candidate": b["candidate"], "failure": b.get("failure")}
                        for b in builds if not b.get("available")],
                },
                "what_could_not_be_obtained_stated_plainly": (
                    "A GENUINELY DIFFERENT OPERATING SYSTEM AND A GENUINELY DIFFERENT "
                    "MACHINE ARCHITECTURE COULD NOT BE OBTAINED, because this harness runs "
                    "on ONE macOS arm64 machine.  THAT IS SAID PLAINLY HERE RATHER THAN "
                    "LEFT TO BE INFERRED.  What was looked for is enumerated in "
                    "builds_enumerated_on_this_host: every python3.x interpreter on PATH "
                    "and at the two framework prefixes, with its exact sys.version, its "
                    "exact sys.executable and whether numpy imports there and at which "
                    "exact version."),
                "IV_7_scope_note": (
                    "IV-7's single-numpy-version rule has scope THE THREE ARMS AND ONLY THE "
                    "THREE ARMS.  PP-1's re-execution under a second build is EXPRESSLY "
                    "OUTSIDE it and records its own six environment strings; a numpy "
                    "version difference between the three arms and PP-1 DOES NOT FIRE "
                    "IV-7."),
                "BND_3_and_BND_4": [BND_1_2_3_4["BND-3"], BND_1_2_3_4["BND-4"]],
            }
            terminal_status = "cancelled_by_budget" if not_reached else "completed_valid"
            validity_status = "valid"
            validity_reason = (
                "IV-1 did not fire, IV-2 did not fire, IV-6 did not fire and IV-7 did not "
                "fire; all 48 declared tuples were measured."
                if not not_reached else
                "PARTIAL RESULT WITH A NAMED GAP (IV-5).  The tuples not reached are named "
                "individually.  A TIMEOUT IS INFRASTRUCTURE SIGNAL AND IS NEVER A NEGATIVE "
                "MATHEMATICAL RESULT.")

        elif arm_key == "HIGHPREC":
            log("")
            log("--- ARM 3 of 3 (ST-2 order): THE HIGH-PRECISION BLOCK.  IT FEEDS NOTHING. ---")
            log("  master seed 130501, arm labels HIGHPREC-REPAIRED and HIGHPREC-ASRECORDED,")
            log("  10 block tuples (a COUNT), both legs, %d replicates per leg per tuple."
                % HIGHPREC_REPLICATES)
            rows, not_reached, variates = arm_highprec(block, deadline, log)
            base["high_precision_block"] = {
                "arm": "CTRL-003-HIGHPREC", "run_id": run_id,
                "feeds": ("NOTHING.  THIS BLOCK FEEDS NO CRITERION, NO THRESHOLD, NO "
                          "INVALIDATION RULE AND NO VERDICT.  Its numbers may not be "
                          "substituted for, averaged with, pooled with, or compared against "
                          "any other quantity of this contract to produce a disposition."),
                "master_seed": 130501,
                "arm_labels": ["HIGHPREC-REPAIRED", "HIGHPREC-ASRECORDED"],
                "replicates_per_leg_per_tuple": HIGHPREC_REPLICATES,
                "block_membership": block_record["block_membership"],
                "twenty_seeded_streams_is_a_COUNT": 2 * len(block),
                "rows": rows,
                "tuples_measured_is_a_COUNT": len(rows),
                "tuples_not_reached_named_IV_5": not_reached,
                "IV_5_verdict": ("IV-5 DID NOT FIRE.  All 10 block tuples were measured."
                                 if not not_reached else
                                 "IV-5: the run did not reach %d block tuples, NAMED HERE: %s"
                                 % (len(not_reached), ", ".join(not_reached))),
                "total_random_variates_requested": variates,
                "difference_column_prohibition_PDC_15": PDC_15_DIFFERENCE_COLUMN_PROHIBITION,
                "recomputability_note_PDC_9_RC_33_L": PDC_9_RECOMPUTABILITY_NOTE,
                "max_abs_exact_expectation_minus_T_over_the_block_is_a_MAGNITUDE":
                    (max(r["abs_exact_expectation_minus_T"] for r in rows) if rows else None),
            }
            if not_reached:
                iv_fired.append("IV-5")
            iv_evaluated["IV-5"] = base["high_precision_block"]["IV_5_verdict"]
            base["total_random_variates_requested"] = variates
            terminal_status = "cancelled_by_budget" if not_reached else "completed_valid"
            validity_status = "valid"
            validity_reason = (
                "IV-1 did not fire, IV-2 did not fire, IV-6 did not fire and IV-7 did not "
                "fire; both legs were measured at all 10 block tuples."
                if not not_reached else
                "PARTIAL RESULT WITH A NAMED GAP (IV-5).  A TIMEOUT IS INFRASTRUCTURE "
                "SIGNAL AND IS NEVER A NEGATIVE MATHEMATICAL RESULT.")

        iv_evaluated.setdefault("IV-3", (
            "NOT EVALUATED IN THIS RUN.  IV-3 is evaluated in RUN-YIELD-003-KNOWNANSWER, "
            "which executes FIRST under ST-2 so that a simulator defect is caught before "
            "any observation quantity is produced."))
        iv_evaluated.setdefault("IV-5", "IV-5 DID NOT FIRE.")
        iv_evaluated["IV-4"] = (
            "IV-4 DID NOT FIRE.  No timeout, crash, resource exhaustion, budget "
            "cancellation or implementation failure occurred in this run."
            if terminal_status == "completed_valid" else
            "IV-4: the run terminated as %s.  THIS IS INFRASTRUCTURE SIGNAL AND IS NEVER A "
            "NEGATIVE MATHEMATICAL RESULT about P_pred, about the shift, about the "
            "diagnostic, about the occupancy null, about decomposition yield or about "
            "anything else." % terminal_status)
        iv_evaluated["IV-6"] = (
            "IV-6 DID NOT FIRE.  No forbidden module was imported or invoked, no "
            "elliptic-curve operation was computed, no occupancy-normalised efficiency E "
            "and no yield ratio R was computed or reported, no file outside `inputs` was "
            "read, no file outside the eleven declared artifacts was written, and NO "
            "THRESHOLD WAS APPLIED TO ANY OBSERVATION QUANTITY OM-1 THROUGH OM-9 OR TO "
            "ANY QUANTITY DERIVED FROM THEM.  The tolerances applied under IV-1 and IV-3 "
            "are REQUIRED EXECUTION OF THOSE RULES AND DO NOT FIRE IV-6 (PDC-1).  See the "
            "declared ambiguities AMB-1 and AMB-2.")
        iv_evaluated["IV-7"] = (
            "IV-7 DID NOT FIRE.  All six required environment strings were recorded in "
            "this manifest and in results.json BEFORE THE FIRST DRAW of this run; one "
            "numpy version (%s) is used throughout this arm; PP-1's separate environment "
            "block is EXPRESSLY OUTSIDE the single-version scope." % env["numpy___version__"])

    except InputIntegrityError as exc:
        iv_fired.append("IV-1")
        terminal_status = "completed_invalid"
        validity_status = "invalid"
        validity_reason = ("IV-1 INPUT INTEGRITY FIRED.  THE RUN STOPPED AND REPORTED, "
                           "PERFORMED NO FURTHER THROW, AND IS NOT EVIDENCE.  %s" % exc)
        log("STOP AND REPORT: %s" % validity_reason)
    except AmbiguityStop as exc:
        terminal_status = "completed_invalid"
        validity_status = "invalid"
        validity_reason = "ST-3 STOP AND REPORT: %s" % exc
        log("STOP AND REPORT: %s" % validity_reason)
    except MemoryError as exc:
        iv_fired.append("IV-4")
        terminal_status = "resource_exhaustion"
        validity_status = "invalid"
        validity_reason = ("RESOURCE EXHAUSTION: %r.  THIS IS INFRASTRUCTURE SIGNAL AND IS "
                           "NEVER A NEGATIVE MATHEMATICAL RESULT." % (exc,))
        log("STOP AND REPORT: %s" % validity_reason)
    except Exception as exc:  # pragma: no cover
        iv_fired.append("IV-4")
        terminal_status = "failed_implementation"
        validity_status = "invalid"
        validity_reason = ("IMPLEMENTATION FAILURE: %r.  THIS IS INFRASTRUCTURE SIGNAL AND "
                           "IS NEVER A NEGATIVE MATHEMATICAL RESULT." % (exc,))
        import traceback
        log("STOP AND REPORT: %s" % validity_reason)
        log(traceback.format_exc())

    ended_iso = utc_now()
    elapsed = time.monotonic() - t_start
    rusage_after = resource.getrusage(resource.RUSAGE_SELF)

    if arm_key == "REPLICATE-REPAIRED":
        deviations = deviations + [
            {
                "id": "DEV-5",
                "what": ("THE THREE ARMS WERE EXECUTED ON A DIFFERENT INTERPRETER BUILD "
                         "FROM THE COMMITTED EXP-YIELD-002 RUN, which used python 3.13.1 "
                         "with numpy 2.4.0.  The contract NAMES NO VERSION, because the "
                         "authoring session had no shell; the TASK-20260729-035 card "
                         "directs execution on the most genuinely different interpreter "
                         "build available on this host, which is what was done."),
                "effect_size": ("The random stream is a function of the numpy version and "
                                "the seed.  The seed changed by design; whether the numpy "
                                "version change also changed the stream is MEASURED by the "
                                "PP-1 legs and reported there.  This is a DECLARED "
                                "EXECUTION CHOICE within the contract's silence, not a "
                                "departure from any clause."),
                "conservative_reading": ("A reader must not treat any agreement or "
                                         "disagreement with the committed run as a "
                                         "seed-only contrast: the build differs too.  "
                                         "BND-1 already limits what the seed contrast buys, "
                                         "and this widens rather than narrows what is "
                                         "confounded."),
            },
            {
                "id": "DEV-6",
                "what": ("PP-1 WAS EXECUTED AGAINST EVERY QUALIFYING SECOND BUILD ON THE "
                         "HOST RATHER THAN THE SINGULAR `THAT BUILD` THE CONTRACT NAMES.  "
                         "See declared ambiguity AMB-3."),
                "effect_size": ("NONE on any quantity of the contract.  Each PP-1 leg is a "
                                "separately labelled observation feeding nothing; none is "
                                "pooled with, averaged into or substituted for OM-5, and "
                                "none is compared against the resume-condition "
                                "thresholds."),
                "conservative_reading": ("Running a superset of what the clause requires "
                                         "removes an unrecorded choice at the cost of extra "
                                         "compute.  A reviewer who reads the clause as "
                                         "permitting exactly one leg may disregard the "
                                         "additional legs; the first leg alone satisfies "
                                         "the clause."),
            },
            {
                "id": "DEV-7",
                "what": ("THE OPTIONAL TIGHTENING RC-33-M WAS ADOPTED: the first three raw "
                         "64-bit integers of one named tuple's per-tuple generator are "
                         "recorded beside its derived seed, taken from a SEPARATE generator "
                         "instance."),
                "effect_size": ("NONE.  The arm's own stream is untouched, because the "
                                "probe uses its own generator instance seeded with the same "
                                "value.  It adds three reported integers and no threshold."),
                "conservative_reading": ("It pins the stream position that the contract's "
                                         "named-calls clause makes load-bearing and detects "
                                         "a step-order defect no known-answer case can see.  "
                                         "The reviewer raised it as optional and did not "
                                         "impose it."),
            },
        ]
    deviations = deviations + [
        {
            "id": "DEV-8",
            "what": ("THE ORCHESTRATION ADAPTER WAS NOT INVOKED to resolve the model policy "
                     "or to probe model identity, because the contract forbids this driver "
                     "from importing or EXECUTING anything under orchestration/ and IV-6 "
                     "fires on invoking a forbidden module.  The committed EXP-YIELD-002 "
                     "driver did invoke it; this driver does not."),
            "effect_size": ("NONE on any measured quantity.  The consequence is that "
                            "resolved_model_id is SELF-REPORTED and model_verified is "
                            "false, which is what the inference block records.  NO ADAPTER "
                            "RESULT IS CLAIMED AND NONE IS FABRICATED."),
            "conservative_reading": ("The known policy binding mismatch INT-BATCH013-D is "
                                     "therefore DISCLOSED and not probed.  It is not "
                                     "substituted."),
        },
    ]

    results.update(base)
    results.update({
        "terminal_status": terminal_status,
        "validity_status": validity_status,
        "validity_reason": validity_reason,
        "invalidation_rules_fired": iv_fired,
        "invalidation_rules_evaluated": iv_evaluated,
        "protocol_deviations": deviations,
        "declared_ambiguities": DECLARED_AMBIGUITIES,
        "elapsed_seconds": elapsed,
        "timestamps": {"started_utc": started_iso, "ended_utc": ended_iso,
                       "precision": "second"},
    })
    write_json(os.path.join(run_dir, "results.json"), results)

    manifest = common_manifest(
        run_id, command, git, env, inf, started_iso, ended_iso, elapsed,
        rusage_before, rusage_after, terminal_status, validity_status, validity_reason,
        iv_fired, iv_evaluated, deviations,
        extra={
            "input_parameters": {
                "input_files": results.get("input_integrity_IV_1", {}).get("input_files"),
                "declared_tuple_count_is_a_COUNT": 48,
                "declared_tuple_members_named_in":
                    "results.json input_integrity_IV_1.arity_split and the arm rows",
                "replicate_schedule":
                    results.get("input_integrity_IV_1", {}).get("replicate_schedule_realised"),
            },
            "seeds": {
                "master_seeds": MASTER_SEEDS,
                "derivation_rule": results.get("seed_integrity_IV_2", {}).get("seed_derivation_rule"),
                "all_derived_seeds": results.get("all_derived_seeds_of_EXP_YIELD_003"),
                "IV_2_checks": {k: v for k, v in results.get("seed_integrity_IV_2", {}).items()
                                if k != "comparison_pools"},
            },
            "declared_ambiguities": DECLARED_AMBIGUITIES,
            "PP_1_disclosure": results.get("PP_1_interpreter_build_attempt", {
                "applies_to_this_run": False,
                "note": ("PP-1 IS A DECLARED SUB-BLOCK OF RUN-YIELD-003-REPLICATE-REPAIRED "
                         "ONLY.  It is not a fourth run and it does not apply to this arm.  "
                         "Its full disclosure, including what was obtained and what was "
                         "not, is in that run's manifest and results.json."),
                "platform_could_not_vary": (
                    "A GENUINELY DIFFERENT OPERATING SYSTEM AND A GENUINELY DIFFERENT "
                    "MACHINE ARCHITECTURE ARE NOT AVAILABLE ON THIS HOST, which runs one "
                    "macOS arm64 machine.  STATED PLAINLY IN EVERY MANIFEST.  NO RECORD "
                    "MAY DESCRIBE THIS EXPERIMENT AS A FRESH-PLATFORM REPLICATION."),
            }),
        })
    write_json(os.path.join(run_dir, "manifest.json"), manifest)

    log("")
    log("terminal_status  %s" % terminal_status)
    log("validity_status  %s" % validity_status)
    log("elapsed_seconds  %.3f" % elapsed)
    log("peak rss bytes   %d" % rusage_after.ru_maxrss)
    log("artifacts written: manifest.json, results.json, stdout.log")
    log("NO COMMIT WAS MADE.")

    sys.stdout = real_out
    sys.stderr = real_err
    handle.close()
    return 0 if validity_status == "valid" else 1


# --------------------------------------------------------------------------
# 15.  summary.json.  DERIVED from the three results.json files.  NO NUMBER IN
#      IT IS HAND-ENTERED.
# --------------------------------------------------------------------------


def build_summary():
    src = {}
    for key, run_id in RUN_IDS.items():
        path = os.path.join(REPO_ROOT, "experiments", "EXP-YIELD-003", "runs", run_id,
                            "results.json")
        with open(path) as fh:
            src[key] = json.load(fh)
        src[key]["_sha256"] = sha256_file(path)
        src[key]["_path"] = "experiments/EXP-YIELD-003/runs/%s/results.json" % run_id

    ka = src["KNOWNANSWER"].get("known_answer_arm", {})
    prim = src["REPLICATE-REPAIRED"].get("primary_arm", {})
    obs = src["REPLICATE-REPAIRED"].get("observations", {})
    hp = src["HIGHPREC"].get("high_precision_block", {})

    tol_cases = []
    for c in ka.get("cases", []):
        tol_cases.append({"case": c["case"], "label": c.get("label"),
                          "tolerance": c.get("tolerance"), "half_band": c.get("half_band"),
                          "admissible_interval": c.get("admissible_interval"),
                          "passes": c.get("passes"),
                          "NARROW_1_repair": ("The admissible interval and the numeric "
                                              "half-band are recorded per case in "
                                              "results.json AND in summary.json, repairing "
                                              "prospectively the cosmetic omission NARROW-1 "
                                              "recorded in the committed EXP-YIELD-002 "
                                              "condensed summary projection.")})

    summary = {
        "schema": "crypto.autoresearch.results_summary.v1",
        "experiment_id": EXPERIMENT_ID, "task_id": TASK_ID, "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "derived_note": ("DERIVED BY THE DRIVER FROM THE THREE results.json FILES AND "
                         "REPRODUCIBLE FROM THEM.  NO NUMBER IN THIS FILE IS HAND-ENTERED."),
        "source_results_files": {k: {"path": v["_path"], "sha256": v["_sha256"],
                                     "terminal_status": v["terminal_status"],
                                     "validity_status": v["validity_status"]}
                                 for k, v in src.items()},
        "contract_in_force": CONTRACT_IN_FORCE,
        "pre_dispatch_conditions_verbatim": PRE_DISPATCH_CONDITIONS_VERBATIM,
        "pre_dispatch_condition_compliance": PDC_COMPLIANCE,
        "claim_tier": CLAIM_TIER,
        "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
        "no_success_criterion_statement": NO_SUCCESS_CRITERION_STATEMENT,
        "resume_condition_carried_verbatim": RESUME_CONDITION_VERBATIM,
        "resume_condition_not_applied_here": RESUME_CONDITION_NOT_APPLIED_HERE,
        "unit_convention_PDC_14": PDC_COMPLIANCE["PDC-14"],
        "pre_data_reference_magnitudes_PDC_12": {
            "standard_error_of_the_48_tuple_z_sem_mean_under_the_independent_stream_design": 0.1466905,
            "standardised_resume_condition_edges": [0.9543904, 1.7042686],
            "these_are_MAGNITUDES": True,
            "status": ("QUOTED FROM PDC-12 AS PRE-DATA REFERENCE MAGNITUDES AND APPLIED TO "
                       "NOTHING.  NO REALISED NUMBER OF THIS RUN IS COMPARED AGAINST ANY OF "
                       "THE THREE BY THIS PACKAGE."),
            "the_design_is_poorly_powered_for_its_own_question": (
                "STATED PRE-DATA BY THE CONTRACT AND CARRIED HERE.  The two "
                "resume-condition thresholds sit at about 0.95 and about 1.70 of that "
                "standard error, so THIS DESIGN CANNOT SEPARATE ITS OWN TWO RESUME "
                "BRANCHES SHARPLY, and the unassigned interval between them is a real "
                "region this measurement lands in with non-negligible probability - about "
                "0.296 under a centred replication and about 0.159 under an exactly "
                "reproducing shift.  A REPLICATED MEAN IN EITHER UNASSIGNED REGION IS "
                "RECORDED AS INCONCLUSIVE ON THE SHIFT AND IS NEVER ASSIGNED TO THE NEARER "
                "NAMED BRANCH."),
        },
        "ST_4_no_interpretation": ST_4_NO_INTERPRETATION,
        "constrained_sentence_prohibition_PDC_2": CONSTRAINED_SENTENCE_PROHIBITION,
        "constrained_sentence_assertion_scope_PDC_2": CONSTRAINED_SENTENCE_ASSERTION_SCOPE_PDC_2,
        "boundaries": BND_1_2_3_4,
        "environment_of_the_three_arms": {
            k: {s: v["environment"][s] for s in
                ("sys_version", "sys_executable", "platform_platform", "platform_machine",
                 "platform_processor", "numpy___version__")}
            for k, v in src.items()},
        "one_numpy_version_across_the_three_arms": len({
            v["environment"]["numpy___version__"] for v in src.values()}) == 1,
        "committed_reference_environment_quoted":
            src["REPLICATE-REPAIRED"]["environment"]["committed_reference_environment_quoted"],
        "platform_cannot_vary": src["REPLICATE-REPAIRED"]["platform_cannot_vary"],
        "input_integrity_IV_1": {
            "files": src["REPLICATE-REPAIRED"]["input_integrity_IV_1"]["input_files"],
            "verdict": src["REPLICATE-REPAIRED"]["input_integrity_IV_1"]["IV_1_verdict"],
            "replicate_schedule_realised":
                src["REPLICATE-REPAIRED"]["input_integrity_IV_1"]["replicate_schedule_realised"],
            "arity_split": src["REPLICATE-REPAIRED"]["input_integrity_IV_1"]["arity_split"],
            "merged_cells": src["REPLICATE-REPAIRED"]["input_integrity_IV_1"]["merged_cells"],
        },
        "seed_integrity_IV_2": src["REPLICATE-REPAIRED"]["seed_integrity_IV_2"],
        "RC_21B_block_selection": src["HIGHPREC"]["RC_21B_block_selection"],
        "known_answer_arm_IV_3": {
            "verdict": ka.get("IV_3_verdict"),
            "cases_that_fired": ka.get("IV_3_cases_that_fired"),
            "tolerances_and_admissible_intervals_per_case": tol_cases,
            "cases": [{k: v for k, v in c.items() if k != "empirical_frequencies"}
                      for c in ka.get("cases", [])],
        },
        "primary_observation_OM_5": obs.get("OM_5_primary_observation"),
        "secondary_observation_OM_6_signs": obs.get("OM_6_signs"),
        "secondary_observation_OM_7_delta_z": obs.get("OM_7_delta_z"),
        "tail_checks": obs.get("tail_checks"),
        "INV_4_failing_tuples_reported_separately":
            obs.get("INV_4_failing_tuples_reported_separately"),
        "per_tuple_rows_both_denominator_readings_RC_E": [
            {"tuple": r["tuple"], "k": r["k"], "m": r["m"], "B": r["B"], "N": r["N"],
             "C_red": r["C_red"], "s_S_m_minus_2": r["s_S_m_minus_2"], "n_rep": r["n_rep"],
             "seed_string": r["seed_string"], "derived_seed": r["derived_seed"],
             "mu_rep_OM_1": r["mean"], "s_rep_OM_2": r["sd_ddof_1"],
             "sem_rep_OM_2": r["sem"], "P_pred_QUOTED_OM_9": r["P_pred_QUOTED"],
             "lambda_OM_9": r["lambda"], "exp_minus_lambda_OM_9": r["exp_minus_lambda"],
             "T_OM_9": r["T"],
             "z_sem_OM_3": r["z_sem"], "z_sd_OM_4": r["z_sd"],
             "sign_OM_6": r["sign_of_mean_minus_P_pred_OM_6"],
             "delta_z_OM_7": r["delta_z_OM_7"],
             "label": "SAMPLED except P_pred, lambda, exp(-lambda), T and n_rep"}
            for r in prim.get("rows", [])],
        "per_tuple_rows_note": ("BOTH DENOMINATOR READINGS ARE REPORTED AT EVERY ONE OF THE "
                                "48 TUPLES AND NO TUPLE REPORTS ONLY ONE (RC-E).  Here both "
                                "are OBSERVATIONS and neither is a criterion."),
        "high_precision_block": {
            "feeds": hp.get("feeds"),
            "block_membership": hp.get("block_membership"),
            "replicates_per_leg_per_tuple": hp.get("replicates_per_leg_per_tuple"),
            "difference_column_prohibition_PDC_15": hp.get("difference_column_prohibition_PDC_15"),
            "recomputability_note_PDC_9_RC_33_L": hp.get("recomputability_note_PDC_9_RC_33_L"),
            "max_abs_exact_expectation_minus_T_over_the_block_is_a_MAGNITUDE":
                hp.get("max_abs_exact_expectation_minus_T_over_the_block_is_a_MAGNITUDE"),
            "rows": [{"tuple": r["tuple"], "N": r["N"], "C_red": r["C_red"],
                      "s_S_m_minus_2": r["s_S_m_minus_2"], "T_DETERMINED": r["T_DETERMINED"],
                      "P_pred_QUOTED": r["P_pred_QUOTED"],
                      "repaired_mean": r["leg_HIGHPREC_REPAIRED"]["mean"],
                      "repaired_sd": r["leg_HIGHPREC_REPAIRED"]["sd_ddof_1"],
                      "repaired_sem": r["leg_HIGHPREC_REPAIRED"]["sem"],
                      "repaired_seed_string": r["leg_HIGHPREC_REPAIRED"]["seed_string"],
                      "asrecorded_mean": r["leg_HIGHPREC_ASRECORDED"]["mean"],
                      "asrecorded_sd": r["leg_HIGHPREC_ASRECORDED"]["sd_ddof_1"],
                      "asrecorded_sem": r["leg_HIGHPREC_ASRECORDED"]["sem"],
                      "asrecorded_seed_string": r["leg_HIGHPREC_ASRECORDED"]["seed_string"],
                      "repaired_minus_asrecorded_difference": r["repaired_minus_asrecorded_difference"],
                      "standard_error_of_the_difference": r["standard_error_of_the_difference"],
                      "exact_expectation_of_the_difference_DETERMINED":
                          r["exact_expectation_of_the_difference_DETERMINED"],
                      "abs_exact_expectation_minus_T": r["abs_exact_expectation_minus_T"],
                      "label": "SAMPLED except T, P_pred and the exact expectation"}
                     for r in hp.get("rows", [])],
        },
        "PP_1_interpreter_build_attempt": src["REPLICATE-REPAIRED"].get(
            "PP_1_interpreter_build_attempt"),
        "invalidation_rules": {
            k: {"fired": v["invalidation_rules_fired"],
                "evaluated": v["invalidation_rules_evaluated"]}
            for k, v in src.items()},
        "coverage_IV_5": {
            "primary_arm_tuples_measured_is_a_COUNT": prim.get("tuples_measured_is_a_COUNT"),
            "primary_arm_tuples_not_reached_named": prim.get("tuples_not_reached_named_IV_5"),
            "high_precision_block_tuples_measured_is_a_COUNT": hp.get("tuples_measured_is_a_COUNT"),
            "high_precision_block_tuples_not_reached_named": hp.get("tuples_not_reached_named_IV_5"),
        },
        "protocol_deviations": {k: v["protocol_deviations"] for k, v in src.items()},
        "declared_ambiguities": DECLARED_AMBIGUITIES,
        "resource_measurements": {k: {"elapsed_seconds": v["elapsed_seconds"],
                                      "total_random_variates_requested":
                                          v.get("total_random_variates_requested")}
                                  for k, v in src.items()},
        "timestamps": {k: v["timestamps"] for k, v in src.items()},
        "run_order_ST_2": ARM_ORDER_ST_2,
        "eleven_declared_artifact_paths": ELEVEN_DECLARED_PATHS,
        "provenance_of_the_driver": REUSE_FROM_EXP_YIELD_002,
        "inference": inference_block(),
        "no_commit_made": ("NO COMMIT WAS MADE BY THIS PACKAGE.  TASK-20260729-036 commits "
                           "these artifacts and nothing else does."),
        "what_this_package_does_not_do": [
            "It states NO disposition of the resume condition and declares NO branch.",
            "It moves NO hypothesis status and creates NO evidence, decision or knowledge record.",
            "It does NOT un-fire INV-4 and does NOT re-dispose it; it declares INV-5 neither way.",
            "It computes NO occupancy-normalised efficiency E and NO yield ratio R.",
            "It touches NO cost model and produces NO operation-count comparison.",
            "It discharges NEITHER RC-F NOR RC-B and claims no progress on either.",
            "It is NOT a fresh-platform replication and no record may describe it as one.",
            "It is NOT a cryptanalytic result, an attack, an exponent result, a closure or "
            "an impossibility claim, and its claim tier is capped at toy.",
        ],
    }
    out = os.path.join(REPO_ROOT, "experiments", "EXP-YIELD-003", "results", "summary.json")
    write_json(out, summary)
    print("summary written: experiments/EXP-YIELD-003/results/summary.json")
    print("OM-5 mean %.10f  sd %.10f  se %.10f" % (
        summary["primary_observation_OM_5"]["mean"],
        summary["primary_observation_OM_5"]["sample_sd_ddof_1"],
        summary["primary_observation_OM_5"]["standard_error"]))
    return 0


def main():
    ap = argparse.ArgumentParser(description="EXP-YIELD-003 driver")
    ap.add_argument("--run", choices=list(RUN_IDS.values()))
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--pp1-child", action="store_true")
    args = ap.parse_args()
    if args.pp1_child:
        return pp1_child()
    if args.summary:
        return build_summary()
    if args.run:
        for key, rid in RUN_IDS.items():
            if rid == args.run:
                return execute_run(key)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
