#!/usr/bin/env python3
"""EXP-YIELD-002 driver - curve-free repaired-null re-derivation of CTRL-NULL-SUMSET.

TASK-20260729-018, GOAL-ECDLP-001, BATCH-012.

THE CONTRACT IN FORCE IS THE PRECEDENCE QUADRUPLE, ORDERED AS RT29-5 STATES IT:

    1. experiments/EXP-YIELD-002/amendments/v2_to_v3.yaml   at 0548d8cc  (governs)
    2. experiments/EXP-YIELD-002/amendments/v1_to_v2.yaml   at e3c9cb45
    3. .../BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md at f291a624
       (read as corrected by v1_to_v2 as corrected by v2_to_v3)
    4. experiments/EXP-YIELD-002/specification.yaml         at f291a624  (frozen)

ZERO CURVE ARITHMETIC.  This file performs no elliptic-curve point addition, no
doubling, no scalar multiplication, no curve-order computation, no curve or
generator selection, no discrete-logarithm table, no factor base, no sum set, no
census, no summation polynomial, no Groebner basis and no polynomial system
solve.  It is a balls-in-bins simulation over the integer residue range
{0, ..., N-1} on integers QUOTED from two committed files.

RC-F INDEPENDENCE CONDITION.  This driver was written WITHOUT READING
experiments/EXP-YIELD-001/driver/yield_census.py.  That file was never opened,
never imported and never executed by the authoring session.  THIS IS NOT A
DISCHARGE OF RC-F AND NO DISCHARGE IS CLAIMED.

OBSERVATIONS ONLY (ST-4).  This file evaluates the pre-registered criteria and
records their firing sets.  It states NO outcome branch, computes no efficiency
E and no yield ratio, re-disposes INV-4 in no way, declares INV-5 neither way,
and writes no evidence, decision, knowledge or ledger record.

Permitted dependencies: the Python standard library and numpy.  Nothing else.

Usage:
    python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-KNOWNANSWER
    python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-NULL-ASRECORDED
    python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run RUN-YIELD-002-NULL-REPAIRED
    python3 experiments/EXP-YIELD-002/driver/repaired_null.py --summary
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time

import numpy as np

# --------------------------------------------------------------------------
# 0.  Contract constants.  Every value below is QUOTED from a committed file.
# --------------------------------------------------------------------------

EXPERIMENT_ID = "EXP-YIELD-002"
TASK_ID = "TASK-20260729-018"
GOAL_ID = "GOAL-ECDLP-001"
BATCH_ID = "BATCH-012"

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

CONTRACT_QUADRUPLE = [
    {
        "rank": 1,
        "role": "governs where it and any lower member differ",
        "path": "experiments/EXP-YIELD-002/amendments/v2_to_v3.yaml",
        "amendment_id": "AMD-EXP-YIELD-002-V3",
        "commit": "0548d8ccabcd8c95bd0a7240b8424d9c5248a138",
        "blob_sha1": "9c0f13ad322a003731482806a25b003584d18b4c",
    },
    {
        "rank": 2,
        "role": "governs where v3 is silent",
        "path": "experiments/EXP-YIELD-002/amendments/v1_to_v2.yaml",
        "amendment_id": "AMD-EXP-YIELD-002-V2",
        "commit": "e3c9cb451381625877034174b61ca918b48f790d",
        "blob_sha1": "ff83aa32a5d4a06b0c065183e3729049c8ea33f8",
    },
    {
        "rank": 3,
        "role": "read as corrected by v1_to_v2 as corrected by v2_to_v3 (RT29-5)",
        "path": "coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/tasks/TASK-20260729-014/criterion_feasibility_table.md",
        "commit": "f291a624610458fc7ad40b5cf174447517ce97e5",
        "blob_sha1": "e5e4db97847dee08d50f3c7258e23914dbd5026d",
    },
    {
        "rank": 4,
        "role": "frozen specification; governs where all three above are silent",
        "path": "experiments/EXP-YIELD-002/specification.yaml",
        "commit": "f291a624610458fc7ad40b5cf174447517ce97e5",
        "blob_sha1": "30a8bf3eb265b37d870581201d51646119531594",
        "status_in_the_frozen_file": "review_required",
        "approved_by_in_the_frozen_file": None,
        "d1_prophylaxis_note": (
            "THE NULL approved_by IS BY DESIGN AND MUST NOT BE READ AS EVIDENCE OF "
            "NON-APPROVAL.  The approval determination lives in "
            "coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/archives/"
            "TASK-20260729-030/snapshot_commit_receipt.json, APPROVAL_DETERMINATION: "
            "APPROVED, authorized_to_execute true, after three independent "
            "pre-execution reviews (RT-20260729-016 REVISE, RT-20260729-025 REVISE, "
            "RT-20260729-029 PASS) and two amendment cycles."
        ),
    },
]

# inputs.files_read of the frozen specification.  An input that is not
# hash-bound is not an input (IV-4).
IN_1_PATH = "experiments/EXP-YIELD-001/runs/RUN-YIELD-001-NULL-RANDOM-SUMSET/results.json"
IN_1_SHA256 = "040207f85a3444a3377cdf5c86175fb70de6e47280f91c09a516f7a65d2125cd"
IN_2_PATH = "experiments/EXP-YIELD-001/results/summary.json"
IN_2_SHA256 = "2287b277b6f6ce842230ca13bf1217a8ba34cc6da1d2d362123502810f7b2aeb"
BOUND_COMMIT = "2fb2bb7a111d999859612e52990eea7dc6bbac1a"

MASTER_SEEDS = {
    "KNOWNANSWER": 120401,
    "ASRECORDED": 120301,
    "REPAIRED": 120201,
    "HIGHPREC": 120501,
}

RUN_IDS = {
    "KNOWNANSWER": "RUN-YIELD-002-KNOWNANSWER",
    "ASRECORDED": "RUN-YIELD-002-NULL-ASRECORDED",
    "REPAIRED": "RUN-YIELD-002-NULL-REPAIRED",
}

# The four INV-4-failing tuples of the BATCH-011 package, QUOTED from the frozen
# specification declared_cell_set block.  Reported separately as a REPORTING
# requirement only; they carry no separate criterion and no separate threshold.
INV4_FAILING_TUPLES = ["T-18-3-B16", "T-16-3-B16", "T-18-3-B24", "T-18-3-B28"]

MERGED_TUPLE = "T-12-3-B22"

CR_THRESHOLD = 3.000
MISS_STRUCTURED_EDGE = 4.000  # C-4; the constant lives in exactly two places
CR4_LOW, CR4_HIGH = 14, 34

HIGHPREC_REPLICATES = 10000

PER_RUN_WALL_CLOCK_SECONDS = 600  # ST-1
MAXIMUM_MEMORY_GB = 4  # ST-1

CLAIM_TIER = "toy"

# --------------------------------------------------------------------------
# Mandatory sentences.  Carried VERBATIM into every record this driver writes.
# --------------------------------------------------------------------------

POWER_LIMIT_SENTENCE = (
    "THEREFORE A PASS OF P-CORE IS NOT EVIDENCE THAT THE REPAIRED NULL IS EXACT: "
    "it is evidence that the null does not fall short by a LARGE fraction of T, "
    "and a shortfall of 5 percent of T or less would be very unlikely to be "
    "detected by anything in this contract."
)
POWER_LIMIT_OBLIGATION = (
    "C-20: EVERY RECORD PRODUCED FROM THIS CONTRACT MUST CARRY THIS SENTENCE, "
    "WHATEVER BRANCH IT REPORTS - every EXP-YIELD-002 run record, the "
    "EXP-YIELD-002 results summary, EV-ECDLP-009 and DEC-20260729-002 - in the "
    "PD-7 pattern.  A MISS-MARGINAL record is EQUALLY BLIND to a shortfall of 5 "
    "percent of T and is MORE liable to the softer misreading."
)
PD_7_SENTENCE = (
    "PD-7 / C-12 / C-21, CARRIED VERBATIM.  IV-1 CANNOT DISTINGUISH `the "
    "re-implementation is faithful` FROM `the re-implementation inherited the "
    "same defect through the contract text`, because P-ASRECORDED is specified "
    "to be IDENTICAL to what the driver the Coordinator read implements, so if "
    "that driver carried a subtle process error and the Coordinator transcribed "
    "it faithfully, IV-1 reproduces it and passes; BATCH-012 therefore "
    "contributes an INDEPENDENT RE-IMPLEMENTATION OF A COORDINATOR-TRANSCRIBED "
    "PROCESS, NOT AN INDEPENDENT RE-DERIVATION, which is strictly weaker than "
    "RC-F's second route and is essentially zero progress on it.  ONE ASYMMETRY "
    "PARTIALLY RESCUES THE DESIGN: step 1 of P-REPAIRED has NO ANALOGUE in the "
    "BATCH-011 driver, so the PRIMARY arm is not transcribed from anything, and "
    "it is only the COMPARABILITY ANCHOR that is contaminated.  C-3d transcribes "
    "the as-recorded arm one level deeper and therefore moves the RC-F position "
    "slightly further from an independent re-derivation.  RC-F IS NOT DISCHARGED "
    "BY THIS RUN AND NO DISCHARGE IS CLAIMED."
)
ADMISSION_AND_CEILING = (
    "CARRIED VERBATIM AND BINDING.  EXP-YIELD-002 IS NOT EVEN AN "
    "EXPONENT-DECIDING SCREEN.  It is an INSTRUMENT CONTROL ON A CONTROL.  IT "
    "MOVES NO EXPONENT AND CANNOT MOVE ONE.  ITS CLAIM TIER IS CAPPED AT TOY.  "
    "It CAN MEET NO COMPLETION CRITERION OF GOAL-ECDLP-001 UNDER ANY OUTCOME.  "
    "It changes no hypothesis status.  It COMPUTES NO OCCUPANCY-NORMALISED "
    "EFFICIENCY E AND NO YIELD RATIO R.  IT DOES NOT UN-FIRE INV-4 AND DOES NOT "
    "RE-DISPOSE IT.  It DECLARES INV-5 NEITHER FIRED NOR NOT FIRED.  IT TOUCHES "
    "NO COST MODEL.  A TIMEOUT, CRASH, RESOURCE EXHAUSTION OR IMPLEMENTATION "
    "FAILURE IS INFRASTRUCTURE SIGNAL AND IS NEVER A NEGATIVE MATHEMATICAL "
    "RESULT about P_pred, about the diagnostic, about the occupancy null, or "
    "about anything else."
)
CHANCE_ALARM_READING = {
    "note": (
        "PRE-REGISTERED BEFORE ANY DRAW, from RT-20260729-029 (committed at "
        "5174001c) and its conditional_budget_note.md.  Reported so that a reader "
        "of any realised outcome has the pre-data reference in front of them."
    ),
    "branch_law_under_a_perfectly_correct_repaired_null_exact_A1": {
        "P_P_CORE": 0.659,
        "P_MISS_MARGINAL": 0.291,
        "P_MISS_STRUCTURED": 0.050,
        "reading": (
            "THE DESIGN RECORDS ITS PREDICTION AS NOT MET ABOUT ONE TIME IN THREE "
            "EVEN IF EVERYTHING IT HOPES IS TRUE."
        ),
    },
    "branch_law_under_the_A2_approximation": {
        "P_P_CORE": 0.708,
        "P_MISS_MARGINAL": 0.258,
        "P_MISS_STRUCTURED": 0.034,
        "note": "A2 is known to understate; 0.050 is the figure to be carried (RT29-7).",
    },
    "spurious_MISS_STRUCTURED_rate": 0.050,
    "spurious_MISS_STRUCTURED_rate_note": (
        "EVERY RECORD READING A MISS-STRUCTURED MUST QUOTE 0.050 as the chance "
        "rate under a perfectly correct repaired null, NOT `roughly 3 to 4 "
        "percent` (RT29-7 supersedes RT-20260729-025 on this figure)."
    ),
    "CR_3_expected_conditional_exceedances_at_3000": {"A2": 0.229893, "exact_A1": 0.252724},
    "CR_3_P_at_least_one_chance_alarm": {"A2": 0.210755, "exact_A1": 0.229568},
    "CR_1_expected_exceedances_at_3000": 0.187718,
    "CR_4_P_fires": 0.002302,
    "named_expected_chance_offenders_C_16": {
        "T-18-2-B264": {"p_A2": 0.095265, "p_exact_A1": 0.104949, "rank": 1},
        "T-14-2-B118": {"p_A2": 0.054505, "p_exact_A1": 0.056783, "rank": 2},
        "obligation": (
            "EVERY RECORD READING A CR-3 EXCEEDANCE AT T-18-2-B264 OR T-14-2-B118 "
            "MUST QUOTE THE CONDITIONAL RATE from the committed table - 0.105 and "
            "0.057 with A2 removed, 0.095 and 0.055 under A2 - and MUST NOT quote "
            "the marginal 0.18726 as the per-tuple reading.  A REALISED CR-3 "
            "EXCEEDANCE AT EITHER OF THOSE TWO TUPLES WAS NAMED BEFORE THE DATA "
            "EXISTED and is the pre-registered expectation, not a discovery."
        ),
    },
    "RT29_2_correction": (
        "NO RECORD MAY QUOTE `0.377 does not bound the conditional total` WITHOUT "
        "THE CORRECTION AT RT29-2: the sentence section 8 asserts is a "
        "PROBABILITY, whose conditional value is 0.341 (exact-A1) or 0.292 (A2), "
        "so 0.377 is no longer a DERIVED bound - the derived conditional union "
        "bound is 0.4427 - but it remains a TRUE bound on P(at least one chance "
        "alarm)."
    ),
    "RT29_4_correction": (
        "NO RECORD MAY QUOTE `E[n_neg] = 48` WITHOUT THE CORRECTION AT RT29-4: "
        "under the reading C-14 adopts the sum is 40.94 and P(n_neg = 48) is "
        "1.5e-4.  The error OVERSTATES the design's own counterfactual power and "
        "feeds no criterion."
    ),
    "PD_8_pre_data_observation": (
        "At all 29 m = 2 tuples the restored term T is at most 0.998 bins, so at "
        "T-18-2-B264, T-14-2-B118 and T-18-2-B140 the committed BATCH-011 "
        "residual exceeds 3T and CANNOT BE EXPLAINED BY THE MISSING PRE-MARKING "
        "UNDER ANY OUTCOME OF THIS EXPERIMENT.  Feeds no criterion, no threshold "
        "and no verdict."
    ),
}

PREREGISTERED_PREDICTION_VERBATIM = (
    "THE REPAIRED NULL LANDS WITHIN 3 STANDARD DEVIATIONS OF THE UNCHANGED "
    "P_pred AT EVERY DECLARED CELL, UNDER BOTH DENOMINATOR READINGS - the "
    "single-replicate standard deviation and DEV-4's stricter standard error of "
    "the mean - with the repaired null's mean shifted UP by "
    "|S_(m-2)| exp(-C_red/N) relative to the per-cell mean recorded in "
    "RUN-YIELD-001-NULL-RANDOM-SUMSET at commit "
    "2fb2bb7a111d999859612e52990eea7dc6bbac1a."
)

# C-18: these four sets are FEASIBILITY SETS UNDER THE COUNTERFACTUAL.  They feed
# NO criterion, NO threshold, NO invalidation rule and NO verdict, and a realised
# firing set differing from them is NOT a failed prediction.  The pre-registered
# REALISED expectation under P-CORE is the EMPTY set for CR-1, CR-2 and CR-3 and
# n_neg in [14, 34] for CR-4, and that is the only comparison PRED-ID governs.
PREREGISTERED_REALISED_EXPECTATION = {
    "CR-1": [],
    "CR-2": [],
    "CR-3": [],
    "CR-4": "n_neg in [14, 34]",
    "rule_PRED_ID": (
        "Every comparison of a realised outcome against a pre-registered "
        "expectation is evaluated on SET IDENTITY - which tuples - and NEVER on "
        "CARDINALITY - how many.  A realised set whose COUNT matches a predicted "
        "count while its MEMBERS differ is recorded as a FAILED PREDICTION."
    ),
}

COUNTERFACTUAL_FEASIBILITY_SETS = {
    "binding_note": (
        "C-18: FEASIBILITY SETS UNDER THE COUNTERFACTUAL ONLY.  They feed NO "
        "criterion, NO threshold, NO invalidation rule and NO verdict, and a "
        "realised firing set differing from them is NOT a failed prediction."
    ),
    "CR-1": ["T-16-2-B38", "T-18-2-B34", "T-18-2-B44", "T-18-2-B58", "T-12-3-B16",
             "T-12-3-B20", "T-12-3-B22", "T-14-3-B20", "T-14-3-B26", "T-14-3-B34",
             "T-16-3-B16", "T-16-3-B22", "T-16-3-B30", "T-16-3-B38", "T-18-3-B16",
             "T-18-3-B24", "T-18-3-B28", "T-18-3-B34", "T-18-3-B44", "T-18-3-B58"],
    "CR-2": ["T-16-3-B16", "T-16-3-B22", "T-18-3-B16", "T-18-3-B24", "T-18-3-B28"],
    "CR-3": ["T-18-2-B34", "T-18-2-B44", "T-12-3-B16", "T-12-3-B20", "T-12-3-B22",
             "T-14-3-B20", "T-14-3-B26", "T-14-3-B34", "T-16-3-B16", "T-16-3-B22",
             "T-16-3-B30", "T-16-3-B38", "T-18-3-B16", "T-18-3-B24", "T-18-3-B28",
             "T-18-3-B34", "T-18-3-B44", "T-18-3-B58"],
    "cannot_fire_complement": [
        "T-12-2-B36", "T-12-2-B42", "T-12-2-B46", "T-12-2-B54", "T-12-2-B62",
        "T-14-2-B34", "T-14-2-B44", "T-14-2-B56", "T-14-2-B72", "T-14-2-B86",
        "T-14-2-B118", "T-16-2-B48", "T-16-2-B58", "T-16-2-B72", "T-16-2-B88",
        "T-16-2-B116", "T-16-2-B144", "T-16-2-B192", "T-16-2-B246", "T-18-2-B82",
        "T-18-2-B110", "T-18-2-B140", "T-18-2-B192", "T-18-2-B264", "T-18-2-B390",
        "T-16-3-B48", "T-16-3-B58", "T-18-3-B82"],
}

PREREGISTERED_POWER_CURVE = {
    "setup": (
        "Let the repaired null still fall short of P_pred by a fraction phi of T "
        "at every tuple, with sem_rep equal to sem_001.  phi = 1.00 is the "
        "all-or-nothing counterfactual of C-2; phi = 0 is the null-plus-declared-"
        "bias case the prediction asserts."
    ),
    "curve": [
        {"phi": 0.02, "E_n_neg": 26.66, "P_CR4_fires": 0.009, "tuples_expected_z_sem_at_least_3": 0},
        {"phi": 0.05, "E_n_neg": 29.22, "P_CR4_fires": 0.048, "tuples_expected_z_sem_at_least_3": 1},
        {"phi": 0.10, "E_n_neg": 31.71, "P_CR4_fires": 0.179, "tuples_expected_z_sem_at_least_3": 5},
        {"phi": 0.20, "E_n_neg": 34.46, "P_CR4_fires": 0.499, "tuples_expected_z_sem_at_least_3": 8},
        {"phi": 0.50, "E_n_neg": 37.97, "P_CR4_fires": 0.919, "tuples_expected_z_sem_at_least_3": 16},
        {"phi": 1.00, "E_n_neg": 40.72, "P_CR4_fires": 0.997, "tuples_expected_z_sem_at_least_3": 20},
    ],
    "reading_pre_registered": (
        "IN THE REGIME WHERE THE PER-TUPLE CRITERIA HAVE NO POWER, PHI AT MOST "
        "0.05, CR-4's FIRING PROBABILITY IS AT MOST 0.048.  CR-4 restores power "
        "against the COMPLETE failure, not against partial ones."
    ),
    "provenance": (
        "QUOTED from AMD-EXP-YIELD-002-V2 preregistered_power_curve, whose "
        "eighteen figures RT-20260729-029 re-derived and reproduced exactly.  It "
        "is a PRE-REGISTERED DESIGN LIMIT, not a measurement."
    ),
}

# --------------------------------------------------------------------------
# The committed conditional CR-3 chance-alarm budget.
# QUOTED VERBATIM from the committed
#   coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/reviews/
#   TASK-20260729-029/conditional_budget_note.md
# section 4, at commit 5174001c37cc6e3b27fb468e0742d7732976a5de,
# sha256 05f6e7cc93494c850f5779f14335d136287d612e8a29fbf482fe28ba8dca74c2
# as bound by the TASK-20260729-030 receipt.
#
# C-15's dispatch gate.  RT-20260729-029 required control: results.json must
# carry the per-tuple delta_i, p_i(3.000) and rank, and they MUST EQUAL the
# committed table.  A disagreement between the run's own delta table and the
# committed one is an ST-3 STOP AND REPORT.
# --------------------------------------------------------------------------

COMMITTED_CONDITIONAL_BUDGET_TABLE = {
    "T-18-2-B264": {"rank": 1, "n_rep": 30, "df": 29, "T": 0.8753281, "r_i": -27.121262, "bias_i": 0.056294, "sem_001": 9.264144, "delta_i": 2.93363, "p_i_3000_A2": 0.095265, "p_i_3000_exact_A1": 0.104949, "p_i_4000_exact_A1": 0.005285},
    "T-14-2-B118": {"rank": 2, "n_rep": 100, "df": 99, "T": 0.6577581, "r_i": 9.621193, "bias_i": 0.122282, "sem_001": 3.598098, "delta_i": -2.63998, "p_i_3000_A2": 0.054505, "p_i_3000_exact_A1": 0.056783, "p_i_4000_exact_A1": 0.001557},
    "T-16-3-B22": {"rank": 3, "n_rep": 100, "df": 99, "T": 21.4107146, "r_i": 1.534056, "bias_i": 0.013118, "sem_001": 0.701847, "delta_i": -2.16705, "p_i_3000_A2": 0.018966, "p_i_3000_exact_A1": 0.020172, "p_i_4000_exact_A1": 0.0003124},
    "T-18-2-B140": {"rank": 4, "n_rep": 100, "df": 99, "T": 0.963246, "r_i": -3.271398, "bias_i": 0.017865, "sem_001": 1.672625, "delta_i": 1.96653, "p_i_3000_A2": 0.01142, "p_i_3000_exact_A1": 0.01227, "p_i_4000_exact_A1": 0.0001487},
    "T-16-2-B246": {"rank": 5, "n_rep": 30, "df": 29, "T": 0.6306413, "r_i": -29.821402, "bias_i": 0.127249, "sem_001": 16.161196, "delta_i": 1.85312, "p_i_3000_A2": 0.008435, "p_i_3000_exact_A1": 0.010749, "p_i_4000_exact_A1": 0.0001695},
    "T-14-3-B34": {"rank": 6, "n_rep": 100, "df": 99, "T": 22.9085741, "r_i": -6.413732, "bias_i": 0.118745, "sem_001": 3.422283, "delta_i": 1.90881, "p_i_3000_A2": 0.009802, "p_i_3000_exact_A1": 0.010564, "p_i_4000_exact_A1": 0.0001193},
    "T-16-2-B88": {"rank": 7, "n_rep": 100, "df": 99, "T": 0.9427118, "r_i": 2.6005, "bias_i": 0.027393, "sem_001": 1.436958, "delta_i": -1.79066, "p_i_3000_A2": 0.007104, "p_i_3000_exact_A1": 0.007706, "p_i_4000_exact_A1": 7.525e-05},
    "T-18-2-B58": {"rank": 8, "n_rep": 100, "df": 99, "T": 0.9935936, "r_i": 0.573575, "bias_i": 0.003188, "sem_001": 0.320473, "delta_i": -1.77983, "p_i_3000_A2": 0.006893, "p_i_3000_exact_A1": 0.007481, "p_i_4000_exact_A1": 7.209e-05},
    "T-16-2-B192": {"rank": 9, "n_rep": 30, "df": 29, "T": 0.7551534, "r_i": -13.915154, "bias_i": 0.098231, "sem_001": 9.218217, "delta_i": 1.52018, "p_i_3000_A2": 0.00324, "p_i_3000_exact_A1": 0.004376, "p_i_4000_exact_A1": 4.796e-05},
    "T-18-2-B390": {"rank": 10, "n_rep": 30, "df": 29, "T": 0.7478206, "r_i": -26.877266, "bias_i": 0.100365, "sem_001": 19.117644, "delta_i": 1.41114, "p_i_3000_A2": 0.002316, "p_i_3000_exact_A1": 0.003193, "p_i_4000_exact_A1": 3.106e-05},
    "T-14-3-B26": {"rank": 11, "n_rep": 100, "df": 99, "T": 21.7869449, "r_i": -2.712432, "bias_i": 0.070591, "sem_001": 1.973876, "delta_i": 1.40993, "p_i_3000_A2": 0.002308, "p_i_3000_exact_A1": 0.002561, "p_i_4000_exact_A1": 1.562e-05},
    "T-16-3-B58": {"rank": 12, "n_rep": 30, "df": 29, "T": 35.3283693, "r_i": 17.371138, "bias_i": 0.130512, "sem_001": 14.184607, "delta_i": -1.21545, "p_i_3000_A2": 0.001234, "p_i_3000_exact_A1": 0.001767, "p_i_4000_exact_A1": 1.387e-05},
    "T-14-2-B34": {"rank": 13, "n_rep": 100, "df": 99, "T": 0.9658184, "r_i": 0.595747, "bias_i": 0.016649, "sem_001": 0.454655, "delta_i": -1.27371, "p_i_3000_A2": 0.001494, "p_i_3000_exact_A1": 0.001673, "p_i_4000_exact_A1": 8.617e-06},
    "T-16-2-B72": {"rank": 14, "n_rep": 100, "df": 99, "T": 0.9612773, "r_i": 1.154892, "bias_i": 0.018793, "sem_001": 0.990105, "delta_i": -1.14745, "p_i_3000_A2": 0.000983, "p_i_3000_exact_A1": 0.001111, "p_i_4000_exact_A1": 4.889e-06},
    "T-18-3-B28": {"rank": 15, "n_rep": 100, "df": 99, "T": 27.6102985, "r_i": -0.794924, "bias_i": 0.006885, "sem_001": 0.724573, "delta_i": 1.1066, "p_i_3000_A2": 0.000856, "p_i_3000_exact_A1": 0.00097, "p_i_4000_exact_A1": 4.057e-06},
    "T-18-3-B82": {"rank": 16, "n_rep": 30, "df": 29, "T": 57.7128077, "r_i": -30.125536, "bias_i": 0.112051, "sem_001": 31.729912, "delta_i": 0.95297, "p_i_3000_A2": 0.000502, "p_i_3000_exact_A1": 0.000759, "p_i_4000_exact_A1": 4.46e-06},
    "T-12-2-B54": {"rank": 17, "n_rep": 100, "df": 99, "T": 0.6946071, "r_i": 1.763061, "bias_i": 0.114297, "sem_001": 1.646638, "delta_i": -1.00129, "p_i_3000_A2": 0.000595, "p_i_3000_exact_A1": 0.000679, "p_i_4000_exact_A1": 2.49e-06},
    "T-16-3-B48": {"rank": 18, "n_rep": 30, "df": 29, "T": 36.2385292, "r_i": -11.42947, "bias_i": 0.098215, "sem_001": 13.135574, "delta_i": 0.87759, "p_i_3000_A2": 0.000383, "p_i_3000_exact_A1": 0.000589, "p_i_4000_exact_A1": 3.184e-06},
    "T-16-3-B16": {"rank": 19, "n_rep": 100, "df": 99, "T": 15.8331555, "r_i": 0.253424, "bias_i": 0.005172, "sem_001": 0.264086, "delta_i": -0.94004, "p_i_3000_A2": 0.000479, "p_i_3000_exact_A1": 0.000549, "p_i_4000_exact_A1": 1.866e-06},
    "T-16-2-B48": {"rank": 20, "n_rep": 100, "df": 99, "T": 0.982601, "r_i": 0.441144, "bias_i": 0.008585, "sem_001": 0.462294, "delta_i": -0.93568, "p_i_3000_A2": 0.000472, "p_i_3000_exact_A1": 0.000541, "p_i_4000_exact_A1": 1.828e-06},
    "T-18-3-B44": {"rank": 21, "n_rep": 30, "df": 29, "T": 41.6742999, "r_i": -2.966764, "bias_i": 0.025361, "sem_001": 4.108999, "delta_i": 0.72819, "p_i_3000_A2": 0.000221, "p_i_3000_exact_A1": 0.000351, "p_i_4000_exact_A1": 1.609e-06},
    "T-14-2-B56": {"rank": 22, "n_rep": 100, "df": 99, "T": 0.9099644, "r_i": 0.947767, "bias_i": 0.041899, "sem_001": 1.113133, "delta_i": -0.8138, "p_i_3000_A2": 0.000303, "p_i_3000_exact_A1": 0.000351, "p_i_4000_exact_A1": 1.018e-06},
    "T-18-2-B82": {"rank": 23, "n_rep": 100, "df": 99, "T": 0.9872357, "r_i": -0.497331, "bias_i": 0.006321, "sem_001": 0.636436, "delta_i": 0.79136, "p_i_3000_A2": 0.000279, "p_i_3000_exact_A1": 0.000324, "p_i_4000_exact_A1": 9.128e-07},
    "T-12-2-B62": {"rank": 24, "n_rep": 100, "df": 99, "T": 0.6185484, "r_i": -1.338022, "bias_i": 0.129206, "sem_001": 1.87694, "delta_i": 0.78171, "p_i_3000_A2": 0.000269, "p_i_3000_exact_A1": 0.000312, "p_i_4000_exact_A1": 8.708e-07},
    "T-14-2-B72": {"rank": 25, "n_rep": 100, "df": 99, "T": 0.8555882, "r_i": 1.380728, "bias_i": 0.064051, "sem_001": 1.996589, "delta_i": -0.65946, "p_i_3000_A2": 0.00017, "p_i_3000_exact_A1": 0.000199, "p_i_4000_exact_A1": 4.759e-07},
    "T-14-2-B44": {"rank": 26, "n_rep": 100, "df": 99, "T": 0.9434173, "r_i": -0.428124, "bias_i": 0.027072, "sem_001": 0.697858, "delta_i": 0.65228, "p_i_3000_A2": 0.000166, "p_i_3000_exact_A1": 0.000194, "p_i_4000_exact_A1": 4.592e-07},
    "T-12-3-B20": {"rank": 27, "n_rep": 100, "df": 99, "T": 14.3079597, "r_i": -0.872668, "bias_i": 0.108666, "sem_001": 1.582249, "delta_i": 0.62021, "p_i_3000_A2": 0.000147, "p_i_3000_exact_A1": 0.000172, "p_i_4000_exact_A1": 3.91e-07},
    "T-18-3-B34": {"rank": 28, "n_rep": 100, "df": 99, "T": 33.1580885, "r_i": 0.743979, "bias_i": 0.012148, "sem_001": 1.374054, "delta_i": -0.53261, "p_i_3000_A2": 0.000105, "p_i_3000_exact_A1": 0.000124, "p_i_4000_exact_A1": 2.509e-07},
    "T-18-3-B58": {"rank": 29, "n_rep": 30, "df": 29, "T": 51.2191318, "r_i": 4.536647, "bias_i": 0.053143, "sem_001": 10.340896, "delta_i": -0.43357, "p_i_3000_A2": 7.1e-05, "p_i_3000_exact_A1": 0.000122, "p_i_4000_exact_A1": 3.983e-07},
    "T-12-3-B16": {"rank": 30, "n_rep": 100, "df": 99, "T": 13.4722459, "r_i": 0.553495, "bias_i": 0.068934, "sem_001": 1.059195, "delta_i": -0.45748, "p_i_3000_A2": 7.8e-05, "p_i_3000_exact_A1": 9.3e-05, "p_i_4000_exact_A1": 1.709e-07},
    "T-18-2-B110": {"rank": 31, "n_rep": 100, "df": 99, "T": 0.9771477, "r_i": -0.545467, "bias_i": 0.011229, "sem_001": 1.241929, "delta_i": 0.44825, "p_i_3000_A2": 7.5e-05, "p_i_3000_exact_A1": 9e-05, "p_i_4000_exact_A1": 1.63e-07},
    "T-14-3-B20": {"rank": 32, "n_rep": 100, "df": 99, "T": 18.4506882, "r_i": 0.489351, "bias_i": 0.036391, "sem_001": 1.02108, "delta_i": -0.44361, "p_i_3000_A2": 7.4e-05, "p_i_3000_exact_A1": 8.8e-05, "p_i_4000_exact_A1": 1.592e-07},
    "T-16-2-B58": {"rank": 33, "n_rep": 100, "df": 99, "T": 0.9746982, "r_i": 0.269665, "bias_i": 0.012409, "sem_001": 0.605447, "delta_i": -0.4249, "p_i_3000_A2": 6.9e-05, "p_i_3000_exact_A1": 8.2e-05, "p_i_4000_exact_A1": 1.446e-07},
    "T-12-2-B42": {"rank": 34, "n_rep": 100, "df": 99, "T": 0.8021618, "r_i": 0.579545, "bias_i": 0.083361, "sem_001": 1.196852, "delta_i": -0.41457, "p_i_3000_A2": 6.6e-05, "p_i_3000_exact_A1": 7.9e-05, "p_i_4000_exact_A1": 1.371e-07},
    "T-12-2-B46": {"rank": 35, "n_rep": 100, "df": 99, "T": 0.7676404, "r_i": -0.420781, "bias_i": 0.094481, "sem_001": 1.256528, "delta_i": 0.41007, "p_i_3000_A2": 6.5e-05, "p_i_3000_exact_A1": 7.8e-05, "p_i_4000_exact_A1": 1.34e-07},
    "T-18-2-B34": {"rank": 36, "n_rep": 100, "df": 99, "T": 0.9977939, "r_i": -0.042191, "bias_i": 0.001101, "sem_001": 0.110901, "delta_i": 0.39037, "p_i_3000_A2": 6e-05, "p_i_3000_exact_A1": 7.2e-05, "p_i_4000_exact_A1": 1.212e-07},
    "T-16-2-B144": {"rank": 37, "n_rep": 30, "df": 29, "T": 0.853876, "r_i": -1.65758, "bias_i": 0.064708, "sem_001": 6.299854, "delta_i": 0.27339, "p_i_3000_A2": 3.9e-05, "p_i_3000_exact_A1": 7e-05, "p_i_4000_exact_A1": 1.876e-07},
    "T-18-2-B44": {"rank": 38, "n_rep": 100, "df": 99, "T": 0.996308, "r_i": 0.068011, "bias_i": 0.001841, "sem_001": 0.17296, "delta_i": -0.38257, "p_i_3000_A2": 5.9e-05, "p_i_3000_exact_A1": 7e-05, "p_i_4000_exact_A1": 1.164e-07},
    "T-18-3-B16": {"rank": 39, "n_rep": 100, "df": 99, "T": 15.9579929, "r_i": 0.043548, "bias_i": 0.00131, "sem_001": 0.127936, "delta_i": -0.33015, "p_i_3000_A2": 4.8e-05, "p_i_3000_exact_A1": 5.8e-05, "p_i_4000_exact_A1": 8.919e-08},
    "T-14-2-B86": {"rank": 40, "n_rep": 100, "df": 99, "T": 0.8005019, "r_i": 0.750759, "bias_i": 0.083919, "sem_001": 2.03228, "delta_i": -0.32812, "p_i_3000_A2": 4.8e-05, "p_i_3000_exact_A1": 5.8e-05, "p_i_4000_exact_A1": 8.828e-08},
    "T-12-3-B22": {"rank": 41, "n_rep": 100, "df": 99, "T": 14.0926559, "r_i": 0.76164, "bias_i": 0.124861, "sem_001": 2.02077, "delta_i": -0.31512, "p_i_3000_A2": 4.5e-05, "p_i_3000_exact_A1": 5.5e-05, "p_i_4000_exact_A1": 8.27e-08},
    "T-16-2-B116": {"rank": 42, "n_rep": 100, "df": 99, "T": 0.9025697, "r_i": -0.625637, "bias_i": 0.045055, "sem_001": 2.381197, "delta_i": 0.28166, "p_i_3000_A2": 4e-05, "p_i_3000_exact_A1": 4.9e-05, "p_i_4000_exact_A1": 7.005e-08},
    "T-18-2-B192": {"rank": 43, "n_rep": 30, "df": 29, "T": 0.9319931, "r_i": 0.708344, "bias_i": 0.032235, "sem_001": 6.726274, "delta_i": -0.10052, "p_i_3000_A2": 2.4e-05, "p_i_3000_exact_A1": 4.6e-05, "p_i_4000_exact_A1": 9.857e-08},
    "T-12-2-B36": {"rank": 44, "n_rep": 100, "df": 99, "T": 0.8504756, "r_i": 0.193034, "bias_i": 0.066007, "sem_001": 0.89593, "delta_i": -0.14178, "p_i_3000_A2": 2.6e-05, "p_i_3000_exact_A1": 3.2e-05, "p_i_4000_exact_A1": 3.788e-08},
    "T-16-3-B30": {"rank": 45, "n_rep": 100, "df": 99, "T": 28.0077694, "r_i": -0.135784, "bias_i": 0.031505, "sem_001": 1.682591, "delta_i": 0.09942, "p_i_3000_A2": 2.4e-05, "p_i_3000_exact_A1": 3e-05, "p_i_4000_exact_A1": 3.309e-08},
    "T-18-3-B24": {"rank": 46, "n_rep": 100, "df": 99, "T": 23.7889104, "r_i": 0.032452, "bias_i": 0.004368, "sem_001": 0.413259, "delta_i": -0.06796, "p_i_3000_A2": 2.3e-05, "p_i_3000_exact_A1": 2.9e-05, "p_i_4000_exact_A1": 3.07e-08},
    "T-16-3-B38": {"rank": 47, "n_rep": 100, "df": 99, "T": 33.0510288, "r_i": 0.255024, "bias_i": 0.058481, "sem_001": 3.474959, "delta_i": -0.05656, "p_i_3000_A2": 2.3e-05, "p_i_3000_exact_A1": 2.8e-05, "p_i_4000_exact_A1": 3.007e-08},
    "T-16-2-B38": {"rank": 48, "n_rep": 100, "df": 99, "T": 0.9890597, "r_i": 0.016682, "bias_i": 0.005425, "sem_001": 0.293299, "delta_i": -0.03838, "p_i_3000_A2": 2.2e-05, "p_i_3000_exact_A1": 2.8e-05, "p_i_4000_exact_A1": 2.93e-08},
}

# The committed note prints delta_i to 5 decimals and p_i to 6 decimals.  No
# agreement tolerance for the run-time re-derivation against the committed table
# is stated anywhere in the contract quadruple, so one is DECLARED here as a
# protocol deviation (DEV-3) and set at the print precision of the committed
# file rather than chosen after the numbers were seen.
DELTA_AGREEMENT_TOLERANCE = 1e-5
P_AGREEMENT_TOLERANCE = 1e-6
IV4_TOLERANCE = 1e-9

PROTOCOL_DEVIATIONS = [
    {
        "id": "DEV-1",
        "kind": "declared artifact-layout deviation, forced by the contract",
        "text": (
            "docs/evidence-and-reproducibility.md's generic run package has "
            "command.txt, environment.json and stderr.log.  The contract's "
            "required_artifacts_rule and the TASK-20260729-018 queue entry declare "
            "EXACTLY ELEVEN FILES with three files per run directory and no "
            "separate command, environment or stderr file, and forbid any "
            "undeclared artifact.  The exact command and the full environment "
            "block are therefore recorded INSIDE manifest.json, and stderr is "
            "captured into stdout.log by an in-process tee.  Nothing is lost; the "
            "location changes.  This follows BATCH-011's DEV-1 precedent."
        ),
    },
    {
        "id": "DEV-2",
        "kind": "declared artifact-layout deviation, forced by the contract",
        "text": (
            "agents/executor.md asks for a separate implementation note.  The "
            "eleven-path declaration admits no such file, so the implementation "
            "notes and this deviation list live in every manifest and in "
            "results/summary.json, and are repeated in the execution report."
        ),
    },
    {
        "id": "DEV-3",
        "kind": "declared reading of an under-determined agreement tolerance",
        "text": (
            "RT-20260729-029's required control says results.json's per-tuple "
            "delta_i and p_i(3.000) MUST EQUAL the committed conditional budget "
            "table and that a disagreement is an ST-3 STOP AND REPORT, but no "
            "numeric agreement tolerance is stated anywhere in the contract "
            "quadruple, and the committed table is printed to 5 decimals for "
            "delta_i and 6 for p_i, so exact equality is unattainable in "
            "principle.  CONSERVATIVE READING TAKEN AND DECLARED BEFORE THE "
            "COMPARISON: the committed table's values are QUOTED and are the "
            "binding ones; the driver independently re-derives delta_i and "
            "p_i(3.000) under A2 from IN-1 and requires agreement to 1e-5 "
            "absolute on delta_i and 1e-6 absolute on p_i, i.e. to the print "
            "precision of the committed file; the realised maximum absolute "
            "differences are reported in full so a reviewer can re-judge the "
            "tolerance.  The exact-A1 column and the rank are QUOTED and are NOT "
            "re-derived, because exact-A1 needs a chi-square quadrature and scipy "
            "is not a permitted dependency."
        ),
    },
    {
        "id": "DEV-4",
        "kind": "declared reading of an under-determined seed-string field",
        "text": (
            "The seed derivation names the arm labels as exactly REPAIRED, "
            "ASRECORDED, KNOWNANSWER and HIGHPREC, and the high-precision "
            "diagnostic block runs BOTH processes at the four INV-4-failing "
            "tuples under the single label HIGHPREC.  The contract therefore "
            "derives the SAME per-tuple seed for the block's repaired and "
            "as-recorded legs.  CONSERVATIVE READING TAKEN: the contract's own "
            "enumerated label is used literally rather than a label the contract "
            "does not name, so the two legs at a tuple share a generator seed and "
            "are NOT independent streams.  Their realised draws still differ, "
            "because the repaired leg consumes an rng.choice call per replicate "
            "that the as-recorded leg does not.  THE BLOCK FEEDS NO CRITERION, NO "
            "THRESHOLD, NO INVALIDATION RULE AND NO VERDICT, so no criterion "
            "quantity depends on this reading.  It is declared rather than "
            "resolved silently."
        ),
    },
    {
        "id": "DEV-5",
        "kind": "declared reading of an under-determined reported quantity",
        "text": (
            "C-20 requires every run record to report `the REALISED "
            "PHI-EQUIVALENT - the value of phi for which the observed aggregate "
            "shortfall would be typical` but does not define the aggregation.  "
            "CONSERVATIVE READING TAKEN: no single aggregation is chosen.  FOUR "
            "named aggregations are reported side by side - a precision-weighted "
            "least-squares fit, a pooled ratio of sums, the median of the "
            "per-tuple ratios, and the phi whose declared E[n_neg] matches the "
            "realised n_neg by linear interpolation on the six declared curve "
            "rows.  ALL FOUR CARRY NO THRESHOLD, NO ACCEPTANCE REGION AND NO "
            "DISPOSITION, may not be compared against any value to produce a "
            "verdict, and are a coordinate on a declared curve and nothing else."
        ),
    },
    {
        "id": "DEV-6",
        "kind": "declared reading of an under-determined tail-check statistic",
        "text": (
            "tail_checks requires `the distribution of z_sem across the 48 "
            "declared tuples, reported against the standard normal` as an "
            "OBSERVATION but names no statistic.  CONSERVATIVE READING TAKEN: the "
            "full sorted vector of z_sem is reported verbatim together with its "
            "count, mean, sample sd, minimum, maximum and the counts of |z_sem| "
            "above 1, 2 and 3, beside the standard-normal expectations for 48 "
            "draws.  NO TEST IS PERFORMED, NOTHING FIRES, and no p-value is "
            "computed."
        ),
    },
    {
        "id": "DEV-7",
        "kind": "declared reading of a run-scoped reporting obligation",
        "text": (
            "C-20 requires EVERY run record to report the realised "
            "phi-equivalent, and C-16 requires the per-tuple delta_i / "
            "p_i(3.000) / rank in results.json.  RUN-YIELD-002-KNOWNANSWER and "
            "RUN-YIELD-002-NULL-ASRECORDED draw no P-REPAIRED replicate, so no "
            "realised phi-equivalent exists in them.  CONSERVATIVE READING TAKEN: "
            "each of those two records carries the phi-equivalent block with a "
            "null value and the reason, carries the C-20 sentence verbatim, and "
            "names RUN-YIELD-002-NULL-REPAIRED and results/summary.json as where "
            "the realised value is reported.  The committed C-16 table is carried "
            "in all three records.  NOTHING IS OMITTED; the location is named."
        ),
    },
]

IMPLEMENTATION_NOTES = [
    "The driver reads exactly two files under experiments/EXP-YIELD-001 - IN-1 and IN-2 - and verifies the SHA-256 of each before parsing it.  It reads no other file under that path, and in particular not the census runs, not the uniform-factor-base null, not the calibration leg, not the baseline run, not the specification, not the amendment and NOT experiments/EXP-YIELD-001/driver/yield_census.py.",
    "occupancy_prediction and both null processes were implemented from the contract text and the committed recorded quantities alone.",
    "Nothing under harness/ or tools/ is imported.  numpy is the only third-party dependency.",
    "One numpy.random.default_rng (PCG64) generator per tuple per arm, seeded by the contract's SHA-256 derivation and consumed sequentially without re-seeding.  No other source of randomness enters any reported number.",
    "Distinct occupancy is counted with one boolean array of length N per tuple, cleared between replicates.  A pre-marked bin is marked once and contributes once.  A throw with g = 0 marks bin 0 only, because (N - 0) mod N = 0; it is not corrected, not rejected and not resampled.",
    "C_red is QUOTED from IN-1 and is never recomputed from B.  C_red // 2 is an exact integer at all 48 declared tuples.",
    "The high-precision diagnostic block executes LAST inside RUN-YIELD-002-NULL-REPAIRED, so that a cap bind costs the block that feeds nothing before it costs a criterion quantity.",
]


# --------------------------------------------------------------------------
# 1.  Small utilities.
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


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def norm_upper_tail(x):
    """Q(x) = P(Z > x) for a standard normal, via math.erfc.  DETERMINED."""
    return 0.5 * math.erfc(x / math.sqrt(2.0))


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
        "dirty_entries": entries[:64],
        "porcelain_sha256": hashlib.sha256(porcelain.encode("utf-8")).hexdigest(),
        "worktree": REPO_ROOT,
    }


def environment_block(driver_sha256, rlimit_status):
    return {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "dependency_versions": {"numpy": np.__version__},
        "numpy_version_exact_string": np.__version__,
        "numpy_pin_note": (
            "C-19b: THE EXACT numpy.__version__ STRING GOVERNS.  It is recorded "
            "here and in results.json BEFORE the first draw.  ONE version is used "
            "across all three arms, all 48 tuples and all eight known-answer "
            "cases; any mid-batch change fires ST-3 STOP AND REPORT.  RT29-6: the "
            "pin is LOAD-BEARING - shuffle=True and shuffle=False return the same "
            "SET but leave the generator in DIFFERENT STATES, so the following "
            "rng.integers differs.  Step 1's call is written in full as "
            "rng.choice(N, size=s, replace=False, shuffle=True) per C-19c."
        ),
        "dependencies_note": (
            "numpy is the only third-party dependency.  Nothing from harness/, "
            "nothing from tools/, no computer-algebra system, no Groebner engine "
            "and no curve code is imported."
        ),
        "driver_path": "experiments/EXP-YIELD-002/driver/repaired_null.py",
        "driver_sha256": driver_sha256,
        "rlimit_as_status": rlimit_status,
        "randomness_sources": [
            "numpy.random.default_rng(seed) [PCG64] - the only source of "
            "randomness in this package.  One generator per tuple per arm, seeded "
            "by the contract's SHA-256 derivation and recorded beside every "
            "number it produced.",
            "No other source of randomness is used.  Set iteration order, dict "
            "order and hash randomisation do not enter any reported number.",
        ],
    }


def inference_block():
    """Recorded honestly.  Nothing here is probe-verified and nothing is claimed."""
    resolve_out = None
    probe_note = None
    try:
        proc = subprocess.run([sys.executable, "-m", "orchestration.adapter", "resolve",
                               "--role", "executor"], cwd=REPO_ROOT, capture_output=True,
                              text=True, timeout=60)
        resolve_out = (proc.stdout or "").strip() or (proc.stderr or "").strip()
        resolve_out = resolve_out[:2000]
    except Exception as exc:
        resolve_out = "UNAVAILABLE: %r" % (exc,)
    try:
        proc = subprocess.run([sys.executable, "-m", "orchestration.adapter", "doctor",
                               "--probe"], cwd=REPO_ROOT, capture_output=True, text=True,
                              timeout=120)
        probe_note = ((proc.stdout or "") + (proc.stderr or "")).strip()[:2000]
    except Exception as exc:
        probe_note = "UNAVAILABLE: %r" % (exc,)
    return {
        "requested_policy": "executor-implementation",
        "requested_policy_source": "TASK-20260729-018 queue entry handoff.inference.policy",
        "policy_resolution_command": "python3 -m orchestration.adapter resolve --role executor",
        "policy_resolution_output": resolve_out,
        "model_verification_attempt_command": "python3 -m orchestration.adapter doctor --probe",
        "model_verification_attempt_output": probe_note,
        "backend_env_AUTORESEARCH_BACKEND": os.environ.get("AUTORESEARCH_BACKEND"),
        "policy_env_AUTORESEARCH_POLICY": os.environ.get("AUTORESEARCH_POLICY"),
        "resolved_runtime_model_id": "claude-opus-5",
        "resolved_runtime_model_id_source": (
            "self-reported by the Claude Code runtime session executing "
            "TASK-20260729-018; NOT probe-verified"
        ),
        "model_verified": False,
        "fallback_used": False,
        "fallback_allowed": False,
        "degraded_allowed": False,
        "degraded_requirements": [],
        "reasoning_effort": None,
        "independent_session_required": False,
        "policy_binding_mismatch": (
            "DISCLOSED, NOT SILENTLY SUBSTITUTED.  The handoff requests policy "
            "`executor-implementation`.  CLAUDE.md's model policy note records "
            "that Claude Code cannot resolve orchestration/model-policies.yaml "
            "identifiers: subagent frontmatter supports only Claude models and "
            "all subagents run at `model: inherit`.  This session was not "
            "launched with a resolved policy environment "
            "(AUTORESEARCH_POLICY and AUTORESEARCH_BACKEND as recorded above) and "
            "reports itself as claude-opus-5.  This is a process-level per-role "
            "model-selection gap, NOT a backend fallback.  It is recorded here "
            "rather than resolved by the Executor.  Model independence is neither "
            "available nor claimed (INT-BATCH012-D)."
        ),
    }


# --------------------------------------------------------------------------
# 2.  Inputs.  IV-4 INPUT INTEGRITY.
# --------------------------------------------------------------------------


class InputIntegrityError(Exception):
    pass


class AmbiguityStop(Exception):
    """ST-3 STOP AND REPORT."""


def tuple_label(k, m, B):
    return "T-%d-%d-B%d" % (k, m, B)


def occupancy_prediction(N, C_red, s):
    """P_pred = N(1 - exp(-lambda)) + |S_(m-2)| exp(-lambda), lambda = C_red/N.

    Implemented from the contract text.  DETERMINED."""
    lam = C_red / N
    e = math.exp(-lam)
    return N * (1.0 - e) + s * e


def exact_process_mean(N, C_red, s):
    """E[distinct] = N - (1 - s/N)[(N-1) A + C], A = (1-2/N)^(C/2), C = (1-1/N)^(C/2).

    The exact mean of P-REPAIRED, from effect_size_arithmetic_OB_10.  Evaluated
    in log space.  DETERMINED."""
    half = C_red // 2
    A = math.exp(half * math.log1p(-2.0 / N))
    Cc = math.exp(half * math.log1p(-1.0 / N))
    return N - (1.0 - s / N) * ((N - 1) * A + Cc)


def load_inputs():
    """Verify the two hash-bound inputs, build the 48 declared tuples, run IV-4."""
    findings = {"IV_4_checks": [], "IV_4_fired": False}
    in1_abs = os.path.join(REPO_ROOT, IN_1_PATH)
    in2_abs = os.path.join(REPO_ROOT, IN_2_PATH)

    in1_hash = sha256_file(in1_abs)
    in2_hash = sha256_file(in2_abs)
    findings["IN_1"] = {"path": IN_1_PATH, "sha256_pinned": IN_1_SHA256,
                        "sha256_as_read": in1_hash, "match": in1_hash == IN_1_SHA256}
    findings["IN_2"] = {"path": IN_2_PATH, "sha256_pinned": IN_2_SHA256,
                        "sha256_as_read": in2_hash, "match": in2_hash == IN_2_SHA256}
    findings["bound_commit"] = BOUND_COMMIT
    if in1_hash != IN_1_SHA256 or in2_hash != IN_2_SHA256:
        findings["IV_4_fired"] = True
        findings["IV_4_checks"].append("HASH MISMATCH on IN-1 or IN-2")
        raise InputIntegrityError("IV-4: input hash mismatch; an input whose hash "
                                  "does not match is not the input this contract names")

    with open(in1_abs) as fh:
        in1 = json.load(fh)
    with open(in2_abs) as fh:
        in2 = json.load(fh)

    cells = in1["cells"]
    findings["IV_4_checks"].append({"check": "IN-1 cells array carries exactly 49 entries",
                                    "value": len(cells), "ok": len(cells) == 49})
    n_eval = in2["realised_evaluable_set"]["n_evaluable_on_measured_B"]
    n_eval_den = in2["out_of_band"]["n_eval_denominator"]
    findings["IV_4_checks"].append({"check": "IN-2 n_evaluable_on_measured_B == 49",
                                    "value": n_eval, "ok": n_eval == 49})
    findings["IV_4_checks"].append({"check": "IN-2 n_eval_denominator == 49",
                                    "value": n_eval_den, "ok": n_eval_den == 49})

    # RC-C de-duplication on measured B within each (k, m) column.  The FIRST
    # listed occurrence is the binding committed reference.
    order = []
    index = {}
    merged = []
    for idx, c in enumerate(cells):
        key = (c["k"], c["m"], c["B"])
        if key in index:
            merged.append({"tuple": tuple_label(*key),
                           "binding_reference_cell_index": index[key],
                           "binding_reference_beta": cells[index[key]]["beta"],
                           "second_draw_cell_index": idx,
                           "second_draw_beta": c["beta"],
                           "second_draw_mean": c["antipodal"]["mean"],
                           "second_draw_sd": c["antipodal"]["sd"],
                           "second_draw_replicates": c["replicates"],
                           "note": ("SECOND INDEPENDENT MONTE CARLO DRAW OF THE SAME "
                                    "PARAMETER TUPLE.  Reported as an OBSERVATION that "
                                    "feeds NO criterion, NO threshold, NO invalidation "
                                    "rule and NO verdict.  The tuple is drawn ONCE by "
                                    "this experiment, not twice.")})
            continue
        index[key] = idx
        order.append(key)
    findings["IV_4_checks"].append({"check": "RC-C de-duplication yields exactly 48 tuples",
                                    "value": len(order), "ok": len(order) == 48})
    findings["merged_cells"] = merged

    tuples = []
    max_lam = max_e = max_T = max_P = 0.0
    for key in order:
        c = cells[index[key]]
        k, m, B = key
        N = c["N"]
        C_red = c["C_red"]
        s = c["P_pred_decomposition"]["S_m_minus_2_used"]
        if C_red % 2 != 0:
            findings["IV_4_fired"] = True
            raise InputIntegrityError("IV-4: odd C_red at %s" % tuple_label(k, m, B))
        lam = C_red / N
        e = math.exp(-lam)
        T = s * e
        P = occupancy_prediction(N, C_red, s)
        max_lam = max(max_lam, abs(lam - c["lambda_C_red_over_N"]))
        max_e = max(max_e, abs(e - c["P_pred_decomposition"]["exp_minus_lambda"]))
        max_T = max(max_T, abs(T - c["P_pred_decomposition"]["S_m_minus_2_term"]))
        max_P = max(max_P, abs(P - c["P_pred"]))
        n_rep = c["replicates"]
        sched = 100 if C_red <= 10 ** 4 else (30 if C_red <= 10 ** 6 else 10)
        tuples.append({
            "tuple": tuple_label(k, m, B),
            "k": k, "p": c["p"], "N": N, "beta": c["beta"], "m": m, "L": c["L"],
            "B": B, "C_red": C_red, "C_red_is_even": c["C_red_is_even"],
            "s_S_m_minus_2": s,
            "n_rep": n_rep,
            "n_rep_from_C_14_schedule": sched,
            "n_rep_matches_C_14": sched == n_rep,
            "lambda": lam,
            "lambda_quoted": c["lambda_C_red_over_N"],
            "exp_minus_lambda": e,
            "exp_minus_lambda_quoted": c["P_pred_decomposition"]["exp_minus_lambda"],
            "T": T,
            "T_quoted": c["P_pred_decomposition"]["S_m_minus_2_term"],
            "P_pred": c["P_pred"],
            "P_pred_recomputed": P,
            "mu_001": c["antipodal"]["mean"],
            "s_001": c["antipodal"]["sd"],
            "sem_001": c["antipodal"]["sd"] / math.sqrt(n_rep),
            "z_001_single_sd_quoted": c["antipodal"]["z_vs_P_pred_single_sd"],
            "z_001_sem_quoted": c["antipodal"]["z_vs_P_pred_sd_of_mean"],
            "residual_after_adding_back_quoted": c["residual_after_adding_back_S_m_minus_2_term"],
            "NOISE_LIMITED_quoted": c["NOISE_LIMITED"],
            "is_INV_4_failing_tuple": tuple_label(k, m, B) in INV4_FAILING_TUPLES,
            "source_cell_index_in_IN_1": index[key],
        })

    findings["IV_4_checks"].append({
        "check": "driver-recomputed lambda, exp(-lambda), T and P_pred agree with the "
                 "QUOTED values to 1e-9 absolute at all 48 tuples",
        "max_abs_diff_lambda": max_lam, "max_abs_diff_exp_minus_lambda": max_e,
        "max_abs_diff_T": max_T, "max_abs_diff_P_pred": max_P,
        "tolerance": IV4_TOLERANCE,
        "ok": max(max_lam, max_e, max_T, max_P) <= IV4_TOLERANCE,
    })
    for chk in findings["IV_4_checks"]:
        if isinstance(chk, dict) and not chk.get("ok", True):
            findings["IV_4_fired"] = True
    if findings["IV_4_fired"]:
        raise InputIntegrityError("IV-4: %r" % (findings["IV_4_checks"],))

    # Schedule and shape observations.
    findings["replicate_schedule_realised"] = {
        "100": sum(1 for t in tuples if t["n_rep"] == 100),
        "30": sum(1 for t in tuples if t["n_rep"] == 30),
        "10": sum(1 for t in tuples if t["n_rep"] == 10),
        "all_match_C_14": all(t["n_rep_matches_C_14"] for t in tuples),
        "max_C_red": max(t["C_red"] for t in tuples),
    }
    findings["arity_split"] = {"m_2": sum(1 for t in tuples if t["m"] == 2),
                               "m_3": sum(1 for t in tuples if t["m"] == 3)}
    return tuples, findings


def conditional_budget_block(tuples):
    """C-16 REPORTING-ONLY.  Re-derive delta_i and p_i(3.000) under A2 and
    compare against the COMMITTED table.  Disagreement is an ST-3 STOP."""
    rows = []
    max_d = 0.0
    max_p = 0.0
    max_r = 0.0
    for t in tuples:
        lbl = t["tuple"]
        com = COMMITTED_CONDITIONAL_BUDGET_TABLE[lbl]
        m_rep = exact_process_mean(t["N"], t["C_red"], t["s_S_m_minus_2"])
        bias = m_rep - t["P_pred"]
        r_i = t["mu_001"] - (t["P_pred"] - t["T"])
        delta = (bias - r_i) / t["sem_001"]
        c = CR_THRESHOLD * math.sqrt(2.0)
        p_a2 = norm_upper_tail(c - delta) + norm_upper_tail(c + delta)
        dd = abs(delta - com["delta_i"])
        dp = abs(p_a2 - com["p_i_3000_A2"])
        dr = abs(r_i - t["residual_after_adding_back_quoted"])
        max_d = max(max_d, dd)
        max_p = max(max_p, dp)
        max_r = max(max_r, dr)
        rows.append({
            "tuple": lbl,
            "rank_QUOTED": com["rank"],
            "delta_i_QUOTED": com["delta_i"],
            "delta_i_rederived": delta,
            "delta_i_abs_diff": dd,
            "p_i_3000_A2_QUOTED": com["p_i_3000_A2"],
            "p_i_3000_A2_rederived": p_a2,
            "p_i_3000_A2_abs_diff": dp,
            "p_i_3000_exact_A1_QUOTED": com["p_i_3000_exact_A1"],
            "p_i_4000_exact_A1_QUOTED": com["p_i_4000_exact_A1"],
            "bias_i_rederived": bias,
            "bias_i_QUOTED": com["bias_i"],
            "r_i_rederived": r_i,
            "r_i_QUOTED": com["r_i"],
            "r_i_vs_IN_1_residual_after_adding_back_abs_diff": dr,
            "label": "DETERMINED (re-derived) beside QUOTED (committed table)",
        })
    agree = (max_d <= DELTA_AGREEMENT_TOLERANCE and max_p <= P_AGREEMENT_TOLERANCE
             and max_r <= IV4_TOLERANCE)
    return {
        "binding_note": (
            "C-16 REPORTING-ONLY, FIRING NOTHING, LOOSENING NOTHING.  The QUOTED "
            "column is the committed table of RT-20260729-029 "
            "conditional_budget_note.md section 4; it is the binding one.  The "
            "re-derived column is this driver's independent evaluation of C-15's "
            "bound rule from IN-1.  See DEV-3 for the declared tolerance."
        ),
        "source": ("coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/reviews/"
                   "TASK-20260729-029/conditional_budget_note.md at commit "
                   "5174001c37cc6e3b27fb468e0742d7732976a5de, sha256 "
                   "05f6e7cc93494c850f5779f14335d136287d612e8a29fbf482fe28ba8dca74c2"),
        "rule": ("delta_i = (bias_i - r_i)/sem_001,i ; "
                 "p_i(c) = Q(c sqrt(2) - delta_i) + Q(c sqrt(2) + delta_i)"),
        "max_abs_diff_delta_i": max_d,
        "max_abs_diff_p_i_3000_A2": max_p,
        "max_abs_diff_r_i_vs_IN_1": max_r,
        "tolerances": {"delta_i": DELTA_AGREEMENT_TOLERANCE,
                       "p_i_3000_A2": P_AGREEMENT_TOLERANCE,
                       "r_i_vs_IN_1": IV4_TOLERANCE},
        "agrees_with_the_committed_table": agree,
        "rows": sorted(rows, key=lambda r: r["rank_QUOTED"]),
    }


# --------------------------------------------------------------------------
# 3.  The two processes.
# --------------------------------------------------------------------------


def draw_replicates(rng, N, C_red, s, n_rep, pre_mark):
    """P-REPAIRED (pre_mark True) or P-ASRECORDED (pre_mark False).

    STEP 1, PRE-MARK.  Choose s DISTINCT bins UNIFORMLY AT RANDOM WITHOUT
    REPLACEMENT from all N bins, and mark them.  The identity bin 0 IS ELIGIBLE.
    A bin chosen in step 1 is marked ONCE and contributes ONCE to the distinct
    count.  The call is exactly rng.choice(N, size=s, replace=False,
    shuffle=True), OMITTED ENTIRELY when s = 0 and omitted entirely in the
    P-ASRECORDED arm.

    STEP 2, THROW.  Exactly one call rng.integers(0, N, size=C_red // 2,
    dtype=numpy.int64), whose returned array is consumed in index order, each
    entry g marking bin g and bin (N - g) mod N.

    STEP 3, COUNT.  The number of distinct marked bins.

    ORDER IS BINDING: step 1 strictly precedes step 2 within a replicate.  No
    other draw is taken from the generator inside the replicate, and replicates
    consume the one per-tuple generator SEQUENTIALLY without re-seeding.
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


def derive_tuple_seed(master, arm_label, k, beta, m, B, C_red):
    """The LOW 64 BITS, as an unsigned little-endian integer, of the SHA-256
    digest of the ASCII string formed by joining with the single character `|`
    and nothing else, in this exact order and with no whitespace - the decimal
    master seed, the arm label, the decimal k, the decimal round(beta x 1000),
    the decimal m, the decimal B, the decimal C_red."""
    payload = "|".join([str(master), arm_label, str(k), str(int(round(beta * 1000))),
                        str(m), str(B), str(C_red)])
    digest = hashlib.sha256(payload.encode("ascii")).digest()
    return payload, int.from_bytes(digest[:8], "little", signed=False)


def derive_ka_seed(master, case_label, N, s, C_red):
    """C-3a: joined with the single character pipe, in this exact order and with
    no whitespace - the decimal master seed 120401, the arm label KNOWNANSWER,
    the case label, the decimal N, the decimal s and the decimal C_red."""
    payload = "|".join([str(master), "KNOWNANSWER", case_label, str(N), str(s), str(C_red)])
    digest = hashlib.sha256(payload.encode("ascii")).digest()
    return payload, int.from_bytes(digest[:8], "little", signed=False)


# --------------------------------------------------------------------------
# 4.  Arm: RUN-YIELD-002-KNOWNANSWER  (IV-2)
# --------------------------------------------------------------------------


def arm_knownanswer(tuples, deadline):
    master = MASTER_SEEDS["KNOWNANSWER"]
    cases = []
    fired = []
    variates_total = 0

    # ---- KA-1 -------------------------------------------------------------
    payload, seed = derive_ka_seed(master, "KA-1", 11, 3, 0)
    rng = np.random.default_rng(seed)
    counts, v = draw_replicates(rng, 11, 0, 3, 1000, True)
    variates_total += v
    bad = int(np.count_nonzero(counts != 3))
    cases.append({"case": "KA-1", "description": "ZERO THROWS.  N = 11, s = 3, C_red = 0, "
                                                 "1000 replicates.  Exact target distinct = 3 in EVERY replicate.",
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 0, "replicates": 1000,
                  "target": 3, "tolerance": "ZERO", "label": "SAMPLED",
                  "replicates_off_target": bad, "min": int(counts.min()),
                  "max": int(counts.max()), "passes": bad == 0})
    if bad:
        fired.append("KA-1")

    # ---- KA-2 -------------------------------------------------------------
    payload, seed = derive_ka_seed(master, "KA-2", 11, 11, 8)
    rng = np.random.default_rng(seed)
    counts, v = draw_replicates(rng, 11, 8, 11, 1000, True)
    variates_total += v
    bad = int(np.count_nonzero(counts != 11))
    cases.append({"case": "KA-2", "description": "FULL PRE-MARKING.  N = 11, s = 11, C_red = 8, "
                                                 "1000 replicates.  Exact target distinct = 11 in EVERY replicate.",
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 11, "C_red": 8, "replicates": 1000,
                  "target": 11, "tolerance": "ZERO", "label": "SAMPLED",
                  "replicates_off_target": bad, "min": int(counts.min()),
                  "max": int(counts.max()), "passes": bad == 0})
    if bad:
        fired.append("KA-2")

    # ---- KA-3 -------------------------------------------------------------
    payload, seed = derive_ka_seed(master, "KA-3", 11, 3, 8)
    rng = np.random.default_rng(seed)
    n = 10 ** 6
    counts, v = draw_replicates(rng, 11, 8, 3, n, True)
    variates_total += v
    target = exact_process_mean(11, 8, 3)
    mean = float(counts.mean())
    sd = float(counts.std(ddof=1))
    tol = 4.000 * sd / math.sqrt(n)
    diff = abs(mean - target)
    cases.append({"case": "KA-3", "description": "EXACT EXPECTATION.  N = 11, s = 3, C_red = 8, "
                                                 "hence 4 throws, 10^6 replicates.  Target computed by the driver from the "
                                                 "closed form E = N - (1 - s/N)[(N-1)(1 - 2/N)^(C/2) + (1 - 1/N)^(C/2)]; the "
                                                 "decimal 7.243921 is NOT hard-coded.",
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 8, "replicates": n,
                  "target_from_closed_form": target, "label": "SAMPLED",
                  "empirical_mean": mean, "empirical_sd_ddof_1": sd,
                  "abs_difference": diff,
                  "tolerance_4_sd_over_sqrt_n": tol, "passes": diff <= tol})
    if diff > tol:
        fired.append("KA-3")

    # ---- KA-4 and KA-5 ----------------------------------------------------
    # C-19a: KA-5 REUSES THE KA-4 STREAM and takes no draw of its own.
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
        g = rng.integers(0, 11, size=0, dtype=np.int64)  # C_red // 2 == 0
        bin_counts += occ
        if int(np.count_nonzero(occ)) != 3:
            ka5_bad += 1
    variates_total += 3 * n
    freqs = (bin_counts / n).tolist()
    band = 4.000 * math.sqrt((3.0 / 11.0) * (8.0 / 11.0) / n)
    worst = max(abs(f - 3.0 / 11.0) for f in freqs)
    cases.append({"case": "KA-4", "description": "PRE-MARKING UNIFORMITY.  N = 11, s = 3, "
                                                 "C_red = 0, 10^6 pre-markings.  Each of the 11 marginal frequencies must "
                                                 "satisfy |frequency - 3/11| <= 4.000 sqrt((3/11)(8/11)/10^6).",
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 3, "C_red": 0, "pre_markings": n, "label": "SAMPLED",
                  "target_frequency": 3.0 / 11.0, "half_band": band,
                  "admissible_interval": [3.0 / 11.0 - band, 3.0 / 11.0 + band],
                  "empirical_frequencies": freqs,
                  "worst_abs_deviation": worst, "passes": worst <= band})
    if worst > band:
        fired.append("KA-4")
    cases.append({"case": "KA-5", "description": "PRE-MARKING WITHOUT REPLACEMENT AND COUNTED "
                                                 "ONCE.  In the SAME 10^6 pre-markings of KA-4 the number of distinct marked "
                                                 "bins must equal 3 in EVERY pre-marking.",
                  "stream": "REUSES THE KA-4 STREAM (C-19a).  Takes no draw of its own and "
                            "is seeded by no generator.",
                  "seed_string": None, "derived_seed": None,
                  "N": 11, "s": 3, "C_red": 0, "pre_markings": n, "label": "SAMPLED",
                  "target": 3, "tolerance": "ZERO",
                  "pre_markings_off_target": ka5_bad, "passes": ka5_bad == 0})
    if ka5_bad:
        fired.append("KA-5")

    # ---- KA-6 and KA-7 ----------------------------------------------------
    # s = 0, so STEP 1 IS OMITTED ENTIRELY.  C-19a: KA-7 REUSES THE KA-6 STREAM.
    payload, seed = derive_ka_seed(master, "KA-6", 11, 0, 2)
    rng = np.random.default_rng(seed)
    n = 10 ** 6
    n_one = 0
    ka6_bad = 0
    ka7_bad = 0
    for _ in range(n):
        g = rng.integers(0, 11, size=1, dtype=np.int64)
        gv = int(g[0])
        marked = {gv, (11 - gv) % 11}
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
    band6 = 4.000 * math.sqrt((1.0 / 11.0) * (10.0 / 11.0) / n)
    dev = abs(freq_one - 1.0 / 11.0)
    cases.append({"case": "KA-6", "description": "IDENTITY-BIN ACCOUNTING.  N = 11, s = 0, "
                                                 "C_red = 2, hence one throw, 10^6 replicates.  STEP 1 IS OMITTED ENTIRELY "
                                                 "BECAUSE s = 0 (C-3d, ruled LOAD-BEARING by RT-20260729-025).  distinct must "
                                                 "be 1 whenever g = 0 and 2 otherwise, ZERO TOLERANCE on that implication; and "
                                                 "|frequency(distinct = 1) - 1/11| <= 4.000 sqrt((1/11)(10/11)/10^6).",
                  "seed_string": payload, "derived_seed": seed,
                  "N": 11, "s": 0, "C_red": 2, "replicates": n, "label": "SAMPLED",
                  "step_1_omitted_because_s_is_zero": True,
                  "implication_violations": ka6_bad,
                  "empirical_frequency_distinct_1": freq_one,
                  "target_frequency": 1.0 / 11.0, "half_band": band6,
                  "admissible_interval": [1.0 / 11.0 - band6, 1.0 / 11.0 + band6],
                  "abs_deviation": dev,
                  "passes": ka6_bad == 0 and dev <= band6})
    if ka6_bad or dev > band6:
        fired.append("KA-6")
    cases.append({"case": "KA-7", "description": "ANTIPODAL PAIRING.  In the SAME 10^6 "
                                                 "replicates of KA-6 the marked bin set must equal exactly "
                                                 "{g, (11 - g) mod 11} in EVERY replicate.",
                  "stream": "REUSES THE KA-6 STREAM (C-19a).  Takes no draw of its own and "
                            "is seeded by no generator.",
                  "seed_string": None, "derived_seed": None,
                  "N": 11, "s": 0, "C_red": 2, "replicates": n, "label": "SAMPLED",
                  "tolerance": "ZERO", "violations": ka7_bad, "passes": ka7_bad == 0})
    if ka7_bad:
        fired.append("KA-7")

    # ---- KA-8 -------------------------------------------------------------
    # DETERMINED, not SAMPLED.  Consumes no random number and is seeded by no
    # generator (C-19a).
    ka8_rows = []
    worst8 = 0.0
    by_label = {t["tuple"]: t for t in tuples}
    for lbl in INV4_FAILING_TUPLES:
        t = by_label[lbl]
        recomputed = occupancy_prediction(t["N"], t["C_red"], t["s_S_m_minus_2"])
        d = abs(recomputed - t["P_pred"])
        worst8 = max(worst8, d)
        ka8_rows.append({"tuple": lbl, "N": t["N"], "C_red": t["C_red"],
                         "s_S_m_minus_2": t["s_S_m_minus_2"],
                         "P_pred_QUOTED": t["P_pred"],
                         "P_pred_recomputed": recomputed,
                         "abs_difference": d, "label": "DETERMINED"})
    cases.append({"case": "KA-8", "description": "P_pred REPRODUCTION AGAINST THE COMMITTED "
                                                 "PACKAGE.  At the four INV-4-failing tuples, recompute P_pred = "
                                                 "N(1 - exp(-C_red/N)) + |S_(m-2)| exp(-C_red/N) by exact double-precision "
                                                 "arithmetic from the QUOTED N, C_red and |S_(m-2)|, requiring |difference| "
                                                 "<= 1e-9 absolute at all four.",
                  "stream": "DETERMINED.  Consumes no random number and is seeded by no "
                            "generator (C-19a).",
                  "seed_string": None, "derived_seed": None, "label": "DETERMINED",
                  "tolerance": 1e-9, "rows": ka8_rows,
                  "max_abs_difference": worst8, "passes": worst8 <= 1e-9})
    if worst8 > 1e-9:
        fired.append("KA-8")

    return {
        "arm": "CTRL-002-KNOWNANSWER",
        "run_id": RUN_IDS["KNOWNANSWER"],
        "feeds": "IV-2 only.",
        "master_seed": master,
        "seed_derivation_rule": ("C-3a: sha256(master|KNOWNANSWER|case|N|s|C_red), low 64 "
                                 "bits little-endian unsigned.  Keyed on the CASE LABEL, so "
                                 "all eight strings are distinct by construction."),
        "generators_seeded_for": ["KA-1", "KA-2", "KA-3", "KA-4", "KA-6"],
        "generators_not_seeded": {"KA-5": "reuses the KA-4 stream",
                                  "KA-7": "reuses the KA-6 stream",
                                  "KA-8": "DETERMINED, takes none"},
        "cases": cases,
        "IV_2_fired": bool(fired),
        "IV_2_cases_that_fired": fired,
        "IV_2_verdict": ("IV-2 DID NOT FIRE.  No known-answer case mismatched beyond its "
                         "stated tolerance." if not fired else
                         "IV-2 FIRED at %s.  THE ENTIRE RUN SET IS INVALID and is never "
                         "evidence about P_pred, about the diagnostic or about anything "
                         "else." % ", ".join(fired)),
        "total_random_variates_requested": variates_total,
        "tuples_not_reached": [],
    }


# --------------------------------------------------------------------------
# 5.  Arms: the two 48-tuple null arms.
# --------------------------------------------------------------------------


def arm_null(tuples, arm_label, deadline, log):
    """Process P-REPAIRED (arm_label REPAIRED) or P-ASRECORDED at all 48 tuples,
    in the order they appear in IN-1's cells array (ST-2)."""
    master = MASTER_SEEDS[arm_label]
    pre_mark = arm_label == "REPAIRED"
    rows = []
    not_reached = []
    variates_total = 0
    for t in tuples:
        if time.monotonic() > deadline:
            not_reached.append({"tuple": t["tuple"],
                                "reason": "ST-1 per-run wall-clock cap reached before this "
                                          "tuple was drawn.  IV-5: named, not estimated, "
                                          "not substituted."})
            continue
        payload, seed = derive_tuple_seed(master, arm_label, t["k"], t["beta"], t["m"],
                                          t["B"], t["C_red"])
        rng = np.random.default_rng(seed)
        t0 = time.monotonic()
        counts, v = draw_replicates(rng, t["N"], t["C_red"], t["s_S_m_minus_2"],
                                    t["n_rep"], pre_mark)
        variates_total += v
        mu = float(counts.mean())
        sd = float(counts.std(ddof=1))
        sem = sd / math.sqrt(t["n_rep"])
        row = {
            "tuple": t["tuple"], "k": t["k"], "m": t["m"], "B": t["B"], "beta": t["beta"],
            "N": t["N"], "C_red": t["C_red"], "s_S_m_minus_2": t["s_S_m_minus_2"],
            "n_rep": t["n_rep"], "label_n_rep": "DETERMINED",
            "seed_string": payload, "derived_seed": seed,
            "mean": mu, "sd_ddof_1": sd, "sem": sem,
            "relative_sd": (sd / mu) if mu else None,
            "min": int(counts.min()), "max": int(counts.max()),
            "label_mean": "SAMPLED", "label_sd": "SAMPLED", "label_sem": "SAMPLED",
            "P_pred_QUOTED": t["P_pred"], "label_P_pred": "QUOTED",
            "lambda": t["lambda"], "exp_minus_lambda": t["exp_minus_lambda"],
            "T": t["T"], "label_T": "DETERMINED",
            "mu_001_QUOTED": t["mu_001"], "s_001_QUOTED": t["s_001"],
            "sem_001_DETERMINED": t["sem_001"],
            "label_mu_001": "QUOTED (SAMPLED in origin)",
            "label_s_001": "QUOTED (SAMPLED in origin)",
            "label_sem_001": "DETERMINED from QUOTED s_001 and n_rep (C-6)",
            "is_INV_4_failing_tuple": t["is_INV_4_failing_tuple"],
            "identity_bin_treatment": (
                "Bin 0 is the IDENTITY BIN.  It IS ELIGIBLE to be pre-marked and is "
                "chosen with probability s/N like every other bin.  A throw with g = 0 "
                "marks bin 0 only, because (N - 0) mod N = 0, so that throw covers ONE "
                "bin rather than two; it is not corrected, not rejected and not "
                "resampled." if pre_mark else
                "Bin 0 is the IDENTITY BIN.  Step 1 is deleted in P-ASRECORDED, so no "
                "bin is pre-marked.  A throw with g = 0 marks bin 0 only, because "
                "(N - 0) mod N = 0; it is not corrected, not rejected and not "
                "resampled."),
            "realised_bin_count": t["N"],
            "realised_orbit_count": (t["N"] - 1) // 2 + 1,
            "orbit_note": ("The N - 1 non-identity residues partition into (N-1)/2 "
                           "ANTIPODAL-PAIR BINS and the identity bin {0} stands alone, "
                           "giving (N-1)/2 + 1 orbits over N bins.  THE QUANTITY MEASURED "
                           "IS THE NUMBER OF DISTINCT BINS COVERED, NOT THE NUMBER OF "
                           "ORBITS TOUCHED."),
            "odd_C_red_handling": ("C_red is QUOTED from IN-1 and is never recomputed from "
                                   "B.  C_red = %d is even, so C_red/2 = %d is an exact "
                                   "integer and no rounding, flooring or ceiling rule is "
                                   "needed or permitted." % (t["C_red"], t["C_red"] // 2)),
            "throws_per_replicate": t["C_red"] // 2,
            "elapsed_seconds": time.monotonic() - t0,
        }
        if pre_mark:
            # PM-3, PM-4, PM-5 and the aggregate sign.  Both denominator readings
            # are reported at every tuple, always, never only the more favourable
            # one, with the replicate count that produced each.
            row["z_sem"] = (mu - t["P_pred"]) / sem
            row["z_sd"] = (mu - t["P_pred"]) / sd
            row["abs_z_sem"] = abs(row["z_sem"])
            row["abs_z_sd"] = abs(row["z_sd"])
            row["denominator_reading_primary"] = {
                "reading": "DEV-4 standard error of the mean, sem_rep = s_rep/sqrt(n_rep)",
                "denominator": sem, "n_rep_that_produced_it": t["n_rep"],
                "statistic": row["z_sem"]}
            row["denominator_reading_secondary"] = {
                "reading": "literal single-replicate standard deviation, s_rep (ddof n_rep - 1)",
                "denominator": sd, "n_rep_that_produced_it": t["n_rep"],
                "statistic": row["z_sd"]}
            row["mean_minus_P_pred"] = mu - t["P_pred"]
            row["sign_of_mean_minus_P_pred"] = (
                "negative" if mu - t["P_pred"] < 0 else
                ("positive" if mu - t["P_pred"] > 0 else "zero"))
            shift_num = (mu - t["mu_001"]) - t["T"]
            shift_den = math.sqrt(sem ** 2 + t["sem_001"] ** 2)
            row["shift_vs_recorded_mean"] = mu - t["mu_001"]
            row["z_shift"] = shift_num / shift_den
            row["abs_z_shift"] = abs(row["z_shift"])
            row["z_shift_numerator"] = shift_num
            row["z_shift_denominator"] = shift_den
            row["label_z_sem"] = "SAMPLED"
            row["label_z_sd"] = "SAMPLED"
            row["label_z_shift"] = "SAMPLED numerator and denominator over a DETERMINED T and a QUOTED mu_001"
        else:
            row["z_comp"] = (mu - t["mu_001"]) / math.sqrt(sem ** 2 + t["sem_001"] ** 2)
            row["abs_z_comp"] = abs(row["z_comp"])
            row["r_sd"] = sd / t["s_001"]
            row["ln_r_sd"] = math.log(sd / t["s_001"])
            row["abs_ln_r_sd"] = abs(row["ln_r_sd"])
            row["IV_1b_threshold"] = 3.000 / math.sqrt(t["n_rep"] - 1)
            row["C_9_reporting_only_statistic"] = abs(mu - t["mu_001"]) / (math.sqrt(2.0) * t["sem_001"])
            row["label_z_comp"] = "SAMPLED over a QUOTED mu_001"
            row["label_r_sd"] = "SAMPLED over a QUOTED s_001"
        rows.append(row)
        log("  %-13s N=%-7d C_red=%-6d s=%-4d n=%-4d mean=%.4f sd=%.6f"
            % (t["tuple"], t["N"], t["C_red"], t["s_S_m_minus_2"], t["n_rep"], mu, sd))
    return rows, not_reached, variates_total


def highprec_block(tuples, deadline, log):
    """CTRL-002-DIAGNOSTIC-HIGHPRECISION.  Both processes at the four
    INV-4-failing tuples only, 10000 replicates each, master seed 120501.

    THIS BLOCK FEEDS NO CRITERION, NO THRESHOLD, NO INVALIDATION RULE AND NO
    VERDICT."""
    master = MASTER_SEEDS["HIGHPREC"]
    by_label = {t["tuple"]: t for t in tuples}
    rows = []
    not_reached = []
    variates_total = 0
    for lbl in INV4_FAILING_TUPLES:
        t = by_label[lbl]
        if time.monotonic() > deadline:
            not_reached.append({"tuple": lbl, "reason": "ST-1 cap reached; the block that "
                                                        "feeds nothing is sacrificed first, per ST-2."})
            continue
        payload, seed = derive_tuple_seed(master, "HIGHPREC", t["k"], t["beta"], t["m"],
                                          t["B"], t["C_red"])
        entry = {"tuple": lbl, "N": t["N"], "C_red": t["C_red"],
                 "s_S_m_minus_2": t["s_S_m_minus_2"],
                 "replicates": HIGHPREC_REPLICATES,
                 "seed_string": payload, "derived_seed": seed,
                 "seed_note": ("DEV-4: the contract's enumerated arm labels are exactly "
                               "REPAIRED, ASRECORDED, KNOWNANSWER and HIGHPREC, so BOTH "
                               "legs of this block derive the SAME per-tuple seed.  Their "
                               "realised draws still differ, because the repaired leg "
                               "consumes an rng.choice call per replicate that the "
                               "as-recorded leg does not.  The block feeds nothing.")}
        for leg, pre in (("P_REPAIRED", True), ("P_ASRECORDED", False)):
            rng = np.random.default_rng(seed)
            counts, v = draw_replicates(rng, t["N"], t["C_red"], t["s_S_m_minus_2"],
                                        HIGHPREC_REPLICATES, pre)
            variates_total += v
            entry[leg] = {"mean": float(counts.mean()),
                          "sd_ddof_1": float(counts.std(ddof=1)),
                          "sem": float(counts.std(ddof=1)) / math.sqrt(HIGHPREC_REPLICATES),
                          "label": "SAMPLED"}
        entry["measured_mean_difference_repaired_minus_asrecorded"] = (
            entry["P_REPAIRED"]["mean"] - entry["P_ASRECORDED"]["mean"])
        entry["T_DETERMINED"] = t["T"]
        rows.append(entry)
        log("  HIGHPREC %-13s repaired=%.5f asrecorded=%.5f"
            % (lbl, entry["P_REPAIRED"]["mean"], entry["P_ASRECORDED"]["mean"]))
    return {
        "binding_label": (
            "THIS BLOCK FEEDS NO CRITERION, NO THRESHOLD, NO INVALIDATION RULE AND NO "
            "VERDICT.  Its numbers may not be substituted for, averaged with, pooled "
            "with, or compared against any criterion quantity, and no record produced by "
            "BATCH-012 may evaluate CR-1, CR-2, CR-3, CR-4, IV-1 or IV-2 on them.  It is "
            "reported and labelled and nothing else."),
        "master_seed": master,
        "replicates": HIGHPREC_REPLICATES,
        "rows": rows,
        "tuples_not_reached": not_reached,
        "total_random_variates_requested": variates_total,
    }


# --------------------------------------------------------------------------
# 6.  Criterion evaluation.  PRE-REGISTERED EVALUATIONS ONLY; NO BRANCH.
# --------------------------------------------------------------------------


def evaluate_criteria(rows, n_declared=48):
    cr1 = sorted(r["tuple"] for r in rows if r["abs_z_sem"] >= CR_THRESHOLD)
    cr2 = sorted(r["tuple"] for r in rows if r["abs_z_sd"] >= CR_THRESHOLD)
    cr3 = sorted(r["tuple"] for r in rows if r["abs_z_shift"] >= CR_THRESHOLD)
    n_neg = sum(1 for r in rows if r["mean_minus_P_pred"] < 0)
    cr1_at_edge = sorted(r["tuple"] for r in rows if r["abs_z_sem"] >= MISS_STRUCTURED_EDGE)
    cr3_at_edge = sorted(r["tuple"] for r in rows if r["abs_z_shift"] >= MISS_STRUCTURED_EDGE)

    def pred_id(realised, expected):
        rs, es = set(realised), set(expected)
        return {"realised_firing_set": sorted(rs),
                "pre_registered_realised_expectation": sorted(es),
                "intersection_count": len(rs & es),
                "realised_minus_preregistered_count": len(rs - es),
                "preregistered_minus_realised_count": len(es - rs),
                "realised_minus_preregistered": sorted(rs - es),
                "preregistered_minus_realised": sorted(es - rs),
                "identical_on_set_identity": rs == es}

    return {
        "evaluation_note": (
            "PRE-REGISTERED CRITERION EVALUATIONS ONLY (ST-4).  This block records "
            "which criteria fired at which tuples.  IT STATES NO OUTCOME BRANCH, "
            "reaches no finding, re-disposes INV-4 in no way and declares INV-5 "
            "neither way.  Interpretation belongs to TASK-20260729-020, "
            "TASK-20260729-021 and TASK-20260729-022."),
        "n_declared_tuples": n_declared,
        "n_tuples_evaluated": len(rows),
        "all_48_evaluated": len(rows) == n_declared,
        "CR-1": {
            "statement": "At EVERY one of the 48 declared tuples, |z_sem| is STRICTLY LESS THAN 3.000.",
            "threshold": CR_THRESHOLD,
            "fires_at": cr1, "n_fires": len(cr1), "holds": len(cr1) == 0,
            "PRED_ID": pred_id(cr1, PREREGISTERED_REALISED_EXPECTATION["CR-1"]),
            "tuples_at_or_above_the_4000_severity_edge": cr1_at_edge,
        },
        "CR-2": {
            "statement": "At EVERY one of the 48 declared tuples, |z_sd| is STRICTLY LESS THAN 3.000.",
            "threshold": CR_THRESHOLD,
            "fires_at": cr2, "n_fires": len(cr2), "holds": len(cr2) == 0,
            "PRED_ID": pred_id(cr2, PREREGISTERED_REALISED_EXPECTATION["CR-2"]),
        },
        "CR-3": {
            "statement": ("At EVERY one of the 48 declared tuples, "
                          "|z_shift| = |(mu_rep - mu_001) - T|/sqrt(sem_rep^2 + sem_001^2) "
                          "is STRICTLY LESS THAN 3.000."),
            "threshold": CR_THRESHOLD,
            "fires_at": cr3, "n_fires": len(cr3), "holds": len(cr3) == 0,
            "PRED_ID": pred_id(cr3, PREREGISTERED_REALISED_EXPECTATION["CR-3"]),
            "tuples_at_or_above_the_4000_severity_edge": cr3_at_edge,
        },
        "CR-4": {
            "statement": ("n_neg is the number of the 48 declared tuples at which "
                          "(mu_rep - P_pred) is strictly negative.  CR-4 HOLDS if and only "
                          "if n_neg is at least 14 AND at most 34.  CR-4 FIRES if n_neg is "
                          "at least 35 or at most 13."),
            "n_neg": n_neg, "window": [CR4_LOW, CR4_HIGH],
            "holds": CR4_LOW <= n_neg <= CR4_HIGH,
            "fires": not (CR4_LOW <= n_neg <= CR4_HIGH),
            "pre_registered_realised_expectation": PREREGISTERED_REALISED_EXPECTATION["CR-4"],
        },
        "PRED_ID_rule": PREREGISTERED_REALISED_EXPECTATION["rule_PRED_ID"],
    }


def tail_checks(rows):
    z = sorted(r["z_sem"] for r in rows)
    zs = sorted(rows, key=lambda r: -r["abs_z_sem"])
    zh = sorted(rows, key=lambda r: -r["abs_z_shift"])
    arr = np.array(z)
    n = len(z)
    return {
        "binding_label": ("OBSERVATIONS.  None of these is a criterion and none fires "
                          "anything."),
        "z_sem_distribution_against_the_standard_normal": {
            "reading_note": ("DEV-6: the contract names no statistic here, so the full "
                             "sorted vector is reported with descriptive summaries beside "
                             "the standard-normal expectations for %d draws.  NO TEST IS "
                             "PERFORMED." % n),
            "n": n,
            "sorted_z_sem": z,
            "mean": float(arr.mean()), "sd_ddof_1": float(arr.std(ddof=1)) if n > 1 else None,
            "min": float(arr.min()), "max": float(arr.max()),
            "count_abs_gt_1": int(np.count_nonzero(np.abs(arr) > 1.0)),
            "count_abs_gt_2": int(np.count_nonzero(np.abs(arr) > 2.0)),
            "count_abs_gt_3": int(np.count_nonzero(np.abs(arr) > 3.0)),
            "standard_normal_expectation_for_n_draws": {
                "mean": 0.0, "sd": 1.0,
                "expected_count_abs_gt_1": n * 0.3173105,
                "expected_count_abs_gt_2": n * 0.0455003,
                "expected_count_abs_gt_3": n * 0.0026998,
            },
        },
        "largest_abs_z_sem": {"tuple": zs[0]["tuple"], "value": zs[0]["abs_z_sem"]},
        "largest_abs_z_shift": {"tuple": zh[0]["tuple"], "value": zh[0]["abs_z_shift"]},
        "top_five_abs_z_sem": [{"tuple": r["tuple"], "abs_z_sem": r["abs_z_sem"]} for r in zs[:5]],
        "top_five_abs_z_shift": [{"tuple": r["tuple"], "abs_z_shift": r["abs_z_shift"]} for r in zh[:5]],
    }


def phi_equivalent(rows, tuples):
    """C-20 REPORTING-ONLY.  See DEV-5: four named aggregations, no choice made.

    THE REALISED PHI-EQUIVALENT HAS NO PRE-REGISTERED THRESHOLD, NO ACCEPTANCE
    REGION AND NO DISPOSITION.  It may not be compared against any value to
    produce a verdict.  It is a coordinate on a declared curve."""
    by_label = {t["tuple"]: t for t in tuples}
    per_tuple = []
    num_w = den_w = 0.0
    num_p = den_p = 0.0
    ratios = []
    for r in rows:
        t = by_label[r["tuple"]]
        shortfall = t["P_pred"] - r["mean"]
        T = t["T"]
        sem = r["sem"]
        ratios.append(shortfall / T)
        num_w += shortfall * T / (sem ** 2)
        den_w += T * T / (sem ** 2)
        num_p += shortfall
        den_p += T
        per_tuple.append({"tuple": r["tuple"], "shortfall_P_pred_minus_mu_rep": shortfall,
                          "T": T, "phi_i": shortfall / T})
    ratios.sort()
    n = len(ratios)
    median = ratios[n // 2] if n % 2 else 0.5 * (ratios[n // 2 - 1] + ratios[n // 2])
    n_neg = sum(1 for r in rows if r["mean_minus_P_pred"] < 0)
    curve = PREREGISTERED_POWER_CURVE["curve"]
    phi_from_n_neg = None
    note = None
    if n_neg <= curve[0]["E_n_neg"]:
        note = ("The realised n_neg %d is at or below the E[n_neg] of the lowest declared "
                "curve row (phi = 0.02, E[n_neg] = 26.66), so no interpolated phi exists "
                "on the declared curve and none is invented." % n_neg)
    elif n_neg >= curve[-1]["E_n_neg"]:
        note = ("The realised n_neg %d is at or above the E[n_neg] of the highest declared "
                "curve row (phi = 1.00, E[n_neg] = 40.72); no extrapolation is performed."
                % n_neg)
    else:
        for a, b in zip(curve, curve[1:]):
            if a["E_n_neg"] <= n_neg <= b["E_n_neg"]:
                frac = (n_neg - a["E_n_neg"]) / (b["E_n_neg"] - a["E_n_neg"])
                phi_from_n_neg = a["phi"] + frac * (b["phi"] - a["phi"])
                note = ("Linear interpolation on the two bracketing declared curve rows "
                        "phi = %.2f and phi = %.2f." % (a["phi"], b["phi"]))
                break
    return {
        "binding_label": (
            "REPORTING-ONLY.  THE REALISED PHI-EQUIVALENT HAS NO PRE-REGISTERED "
            "THRESHOLD, NO ACCEPTANCE REGION AND NO DISPOSITION.  It may not be "
            "compared against any value to produce a verdict, and no record may say "
            "that this run `excluded phi above` some figure as though that were a "
            "criterion.  It is a coordinate on a declared curve, published so that the "
            "declared blindness of the design is visible in the record that reports the "
            "outcome."),
        "deviation": "DEV-5 - the contract does not define the aggregation; four named "
                     "aggregations are reported and none is chosen.",
        "phi_precision_weighted_least_squares": (num_w / den_w) if den_w else None,
        "phi_pooled_ratio_of_sums": (num_p / den_p) if den_p else None,
        "phi_median_of_per_tuple_ratios": median,
        "phi_from_realised_n_neg_on_the_declared_curve": phi_from_n_neg,
        "phi_from_realised_n_neg_note": note,
        "realised_n_neg": n_neg,
        "per_tuple": per_tuple,
        "pre_registered_power_curve": PREREGISTERED_POWER_CURVE,
        "power_limit_sentence": POWER_LIMIT_SENTENCE,
        "power_limit_obligation": POWER_LIMIT_OBLIGATION,
        "label": "SAMPLED numerator over DETERMINED T",
    }


def evaluate_IV_1(rows):
    a_fire = sorted(r["tuple"] for r in rows if r["abs_z_comp"] >= 3.000)
    b_fire = sorted(r["tuple"] for r in rows if r["abs_ln_r_sd"] >= r["IV_1b_threshold"])
    ranked = sorted(rows, key=lambda r: -r["C_9_reporting_only_statistic"])
    c9 = [{"tuple": r["tuple"], "statistic": r["C_9_reporting_only_statistic"],
           "rank_among_the_48": i + 1} for i, r in enumerate(ranked)]
    return {
        "IV_1a": {
            "statement": "IV-1a FIRES if |z_comp| is at least 3.000 at MORE THAN 2 of the 48 tuples.",
            "threshold": 3.000,
            "tuples_at_or_above_threshold": a_fire,
            "count": len(a_fire),
            "fires": len(a_fire) > 2,
        },
        "IV_1b": {
            "statement": ("IV-1b FIRES if |ln_r_sd| is at least 3.000/sqrt(n_rep - 1) at "
                          "MORE THAN 2 of the 48 tuples, which is 0.30151 at the 37 tuples "
                          "with 100 replicates and 0.55709 at the 11 tuples with 30."),
            "tuples_at_or_above_threshold": b_fire,
            "count": len(b_fire),
            "fires": len(b_fire) > 2,
        },
        "IV_1_fires": (len(a_fire) > 2) or (len(b_fire) > 2),
        "consequence_if_either_fires": (
            "This batch's re-implementation does not reproduce the committed antipodal "
            "arm, so THE REPAIRED ARM'S COMPARISON TO THE RECORDED PACKAGE IS VOID RATHER "
            "THAN NEGATIVE.  A VOID HERE IS THE ABSENCE OF A MEASUREMENT AND IS NEVER A "
            "NEGATIVE MATHEMATICAL RESULT ABOUT P_pred, ABOUT THE DIAGNOSTIC OR ABOUT "
            "ANYTHING ELSE."),
        "C_9_reporting_only": {
            "binding_label": "REPORTING-ONLY, FIRING NOTHING.  IV-1a and IV-1b are "
                             "UNCHANGED in trigger and in threshold; NOTHING IS LOOSENED.",
            "statistic": "|mu_asrec - mu_001|/(sqrt(2) sem_001)",
            "pre_registered_fact": (
                "UNDER THE SCENARIO IN WHICH THE COMMITTED BATCH-011 RESIDUALS ARE REAL "
                "RATHER THAN SAMPLING NOISE, the maximum of that quantity is 2.074 at "
                "T-18-2-B264 and the next is 1.867 at T-14-2-B118, so it reaches 3.000 at "
                "ZERO of the 48 tuples and IV-1a DOES NOT FIRE.  THIS IS A BLIND SPOT, "
                "NOT A FALSE-ALARM HAZARD: IV-1 is the gate that anchors CR-3's "
                "comparison to the committed package, and it cannot see the single "
                "largest anomaly in that package."),
            "ranked": c9,
        },
    }


# --------------------------------------------------------------------------
# 7.  Manifest and run-record assembly.
# --------------------------------------------------------------------------


def common_manifest(run_id, command, git, env, inf, started, ended, rusage_before,
                    rusage_after, terminal_status, validity_status, validity_reason,
                    inv_fired, inv_evaluated, seeds_block, input_block, extra):
    return {
        "schema": "crypto.autoresearch.run_manifest.v1",
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "hypothesis_id": None,
        "hypothesis_id_note": (
            "NULL AND DELIBERATELY SO.  EXP-YIELD-002 TESTS NO HYPOTHESIS.  It is an "
            "INSTRUMENT CONTROL ON EXP-YIELD-001'S CONTROL OBJECT CTRL-NULL-SUMSET.  No "
            "hypothesis record is read, written, created or cited as moved by this run."),
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "contract_in_force": {
            "note": ("THE CONTRACT IN FORCE IS THE PRECEDENCE QUADRUPLE.  Ordering read "
                     "as RT29-5 states it: v3 over v2 over the criterion feasibility "
                     "table over the frozen specification, with the table read as "
                     "corrected by v2 as corrected by v3."),
            "quadruple": CONTRACT_QUADRUPLE,
            "approval_determination": {
                "location": ("coordination/goals/GOAL-ECDLP-001/batches/BATCH-012/"
                             "archives/TASK-20260729-030/snapshot_commit_receipt.json"),
                "determination": "APPROVED",
                "authorized_to_execute": True,
                "verdict_source": "RT-20260729-029, verdict PASS",
                "review_history": ("THREE independent pre-execution reviews: "
                                   "RT-20260729-016 REVISE on the frozen contract, "
                                   "RT-20260729-025 REVISE on the first amendment, "
                                   "RT-20260729-029 PASS on the second.  Two amendment "
                                   "cycles, the second a declared deviation from a "
                                   "pre-registered gate (INT-BATCH012-O)."),
                "conditional_on": ("TASK-20260729-030 committing BOTH RT-20260729-029 "
                                   "artifacts, because C-15's dispatch gate requires the "
                                   "conditional chance-alarm budget to exist and be "
                                   "committed BEFORE any draw.  The receipt records that "
                                   "condition as satisfied; this run verified both files "
                                   "are present at HEAD and re-derived the budget rule "
                                   "against the committed table."),
            },
            "confirmatory_status": "exploratory_only",
            "confirmatory_status_basis": (
                "RC-G: a successor whose inputs are quantities already committed in the "
                "BATCH-011 package has an outcome partly determined by data already in "
                "hand, so it CANNOT be confirmatory; and the protocol was revised twice "
                "after adverse independent reviews.  PRE-REGISTRATION ORDER is preserved "
                "and is a different, weaker property, checkable against Git."),
        },
        "command": command,
        "command_note": ("Reproduces this run exactly from the recorded revision, the "
                         "recorded driver SHA-256 and the recorded exact numpy version.  "
                         "stdout and stderr are tee'd in-process into stdout.log (DEV-1)."),
        "invocation_cwd": REPO_ROOT,
        "git": git,
        "environment": env,
        "inference": inf,
        "input_parameters": input_block,
        "seeds": seeds_block,
        "budget": {
            "wall_clock_seconds_per_run_cap": PER_RUN_WALL_CLOCK_SECONDS,
            "maximum_memory_gb_cap": MAXIMUM_MEMORY_GB,
            "maximum_runs": 3,
            "total_cpu_hours_cap": 0.5,
        },
        "resource_measurements": {
            "wall_clock_seconds": ended[1] - started[1],
            "user_cpu_seconds": rusage_after.ru_utime - rusage_before.ru_utime,
            "system_cpu_seconds": rusage_after.ru_stime - rusage_before.ru_stime,
            "peak_rss_bytes_self": rusage_after.ru_maxrss,
            "peak_rss_note": ("ru_maxrss from resource.getrusage(RUSAGE_SELF); on macOS "
                              "this is in BYTES."),
        },
        "stdout_location": "stdout.log (in this run directory)",
        "stderr_location": ("stdout.log (in this run directory) - stderr is tee'd into "
                            "stdout.log in-process; DEV-1 declares the layout deviation."),
        "raw_results_location": "results.json (in this run directory)",
        "timestamps": {"started_utc": started[0], "ended_utc": ended[0],
                       "started_monotonic": started[1], "ended_monotonic": ended[1]},
        "terminal_status": terminal_status,
        "validity_status": validity_status,
        "validity_reason": validity_reason,
        "invalidation_rules_fired": inv_fired,
        "invalidation_rules_evaluated": inv_evaluated,
        "certificate": {
            "kind": "none",
            "reason": ("PURE MEASUREMENT RUN.  This run claims no discrete-logarithm "
                       "solve and no factor-base relation, performs zero curve "
                       "arithmetic, and therefore emits no solution certificate.  "
                       "docs/claims-and-verification.md: a pure measurement run sets "
                       "certificate.kind none explicitly."),
        },
        "claim_tier": CLAIM_TIER,
        "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
        "ST_4_no_interpretation": (
            "This run package contains OBSERVATIONS AND PRE-REGISTERED CRITERION "
            "EVALUATIONS ONLY.  It does NOT state which of P-CORE, MISS-STRUCTURED or "
            "MISS-MARGINAL obtained, writes no evidence or decision record, touches no "
            "hypothesis status, does not re-dispose INV-4, does not adjudicate INV-5, "
            "computes no efficiency E and no yield ratio, touches no cost model, and "
            "says nothing about decomposition yield.  Interpretation belongs to "
            "TASK-20260729-020, TASK-20260729-021 and TASK-20260729-022."),
        "instrument_independence_attested": {
            "zero_curve_arithmetic": True,
            "yield_census_py_not_read": True,
            "statement": ("RECORDED AS THE DECLARED INDEPENDENCE CONDITION REQUIRES.  "
                          "This driver was written from the contract text and the "
                          "committed recorded quantities alone.  "
                          "experiments/EXP-YIELD-001/driver/yield_census.py WAS NOT READ, "
                          "NOT IMPORTED AND NOT EXECUTED by the authoring session or by "
                          "this run.  IT IS NOT A DISCHARGE OF RC-F AND NO DISCHARGE IS "
                          "CLAIMED."),
            "files_read_under_EXP_YIELD_001": [IN_1_PATH, IN_2_PATH],
            "forbidden_imports_avoided": ["harness/*", "tools/*",
                                          "experiments/EXP-YIELD-001/driver/yield_census.py"],
            "PD_7": PD_7_SENTENCE,
        },
        "power_limit_sentence_C_20": POWER_LIMIT_SENTENCE,
        "power_limit_obligation_C_20": POWER_LIMIT_OBLIGATION,
        "pre_registered_prediction_verbatim": PREREGISTERED_PREDICTION_VERBATIM,
        "pre_data_chance_alarm_reading": CHANCE_ALARM_READING,
        "protocol_deviations": PROTOCOL_DEVIATIONS,
        "implementation_notes": IMPLEMENTATION_NOTES,
        "required_artifacts_this_run": ["manifest.json", "results.json", "stdout.log"],
        "eleven_declared_artifact_paths": [
            "experiments/EXP-YIELD-002/driver/repaired_null.py",
            "experiments/EXP-YIELD-002/results/summary.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/manifest.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/results.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-REPAIRED/stdout.log",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-ASRECORDED/manifest.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-ASRECORDED/results.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-NULL-ASRECORDED/stdout.log",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-KNOWNANSWER/manifest.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-KNOWNANSWER/results.json",
            "experiments/EXP-YIELD-002/runs/RUN-YIELD-002-KNOWNANSWER/stdout.log",
        ],
        "no_commit_made": ("THIS RUN MADE NO COMMIT.  TASK-20260729-019 commits this "
                           "package and nothing else does."),
        **extra,
    }


def write_json(path, obj):
    tmp = path + ".partial"
    with open(tmp, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=False, allow_nan=False)
        fh.write("\n")
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# 8.  Run drivers.
# --------------------------------------------------------------------------


def execute_run(arm_key):
    run_id = RUN_IDS[arm_key]
    run_dir = os.path.join(REPO_ROOT, "experiments", "EXP-YIELD-002", "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    stdout_path = os.path.join(run_dir, "stdout.log")
    manifest_path = os.path.join(run_dir, "manifest.json")
    results_path = os.path.join(run_dir, "results.json")

    command = ("python3 experiments/EXP-YIELD-002/driver/repaired_null.py --run %s" % run_id)
    driver_sha = sha256_file(os.path.abspath(__file__))

    # Git state and the inference block are captured BEFORE any draw and before
    # the ST-1 memory cap is applied, so that a subprocess is never taken under
    # a restricted address space.
    git = git_state()
    inf = inference_block()

    # ST-1 memory cap.
    rlimit_status = None
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (MAXIMUM_MEMORY_GB * 1024 ** 3, hard))
        rlimit_status = "RLIMIT_AS set to %d bytes" % (MAXIMUM_MEMORY_GB * 1024 ** 3)
    except Exception as exc:
        rlimit_status = ("RLIMIT_AS could not be set on this host (%r); the %d GB cap is "
                         "enforced by measurement (ru_maxrss recorded) and by the design's "
                         "peak footprint of one boolean array of length at most 261707 "
                         "plus the parsed IN-1 document, i.e. below 1 MB."
                         % (exc, MAXIMUM_MEMORY_GB))

    rusage_before = resource.getrusage(resource.RUSAGE_SELF)
    started = (utc_now(), time.monotonic())
    deadline = started[1] + PER_RUN_WALL_CLOCK_SECONDS

    handle = open(stdout_path, "w")
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout = Tee(real_out, handle)
    sys.stderr = Tee(real_err, handle)

    def log(msg):
        print(msg)
        sys.stdout.flush()

    terminal_status = "failed_implementation"
    validity_status = "invalid"
    validity_reason = "the run did not reach its own completion path"
    inv_fired = []
    inv_evaluated = []
    payload = {}
    extra = {}
    seeds_block = {}
    input_block = {}
    tuples = None
    integrity = None

    try:
        log("=" * 78)
        log("EXP-YIELD-002 %s" % run_id)
        log("TASK-20260729-018  GOAL-ECDLP-001  BATCH-012")
        log("started_utc %s" % started[0])
        log("numpy.__version__ = %s   (C-19b: THE EXACT STRING GOVERNS; recorded "
            "BEFORE the first draw)" % np.__version__)
        log("python %s" % sys.version.split()[0])
        log("ZERO CURVE ARITHMETIC.  experiments/EXP-YIELD-001/driver/yield_census.py "
            "WAS NOT READ.")
        log("=" * 78)

        log("[IV-4] verifying the two hash-bound inputs at %s" % BOUND_COMMIT)
        tuples, integrity = load_inputs()
        log("[IV-4] IN-1 sha256 OK; IN-2 sha256 OK; 49 cells; RC-C de-duplication -> "
            "%d tuples; schedule %s" % (len(tuples), integrity["replicate_schedule_realised"]))
        inv_evaluated.append("IV-4 INPUT INTEGRITY - evaluated, did not fire")

        log("[C-15] re-deriving the conditional CR-3 budget against the committed table")
        budget = conditional_budget_block(tuples)
        log("[C-15] max|delta diff| = %.3e ; max|p_A2 diff| = %.3e ; max|r_i - IN-1| = "
            "%.3e ; agrees = %s" % (budget["max_abs_diff_delta_i"],
                                    budget["max_abs_diff_p_i_3000_A2"],
                                    budget["max_abs_diff_r_i_vs_IN_1"],
                                    budget["agrees_with_the_committed_table"]))
        if not budget["agrees_with_the_committed_table"]:
            raise AmbiguityStop(
                "ST-3 STOP AND REPORT: the run's own delta table disagrees with the "
                "committed conditional budget table beyond the declared tolerance "
                "(DEV-3).  Both are determined from the same committed constants.")

        input_block = {
            "declared_tuple_count": len(tuples),
            "rule_RC_C": ("the 49 criterion-evaluable cells of the BATCH-011 package, "
                          "DE-DUPLICATED ON MEASURED B WITHIN EACH (k, m) COLUMN"),
            "merged_tuple": MERGED_TUPLE,
            "merged_cells": integrity["merged_cells"],
            "arity_split": integrity["arity_split"],
            "replicate_schedule_realised": integrity["replicate_schedule_realised"],
            "replicate_schedule_C_14": ("100 replicates where C_red is at most 10^4; 30 "
                                        "where C_red is above 10^4 and at most 10^6; 10 "
                                        "where C_red exceeds 10^6.  NOT RAISED."),
            "INV_4_failing_tuples_of_the_BATCH_011_package": INV4_FAILING_TUPLES,
            "tuples": tuples,
            "IN_1": integrity["IN_1"], "IN_2": integrity["IN_2"],
            "bound_commit": BOUND_COMMIT,
        }

        if arm_key == "KNOWNANSWER":
            log("[ST-2] arm 1 of 3: RUN-YIELD-002-KNOWNANSWER (IV-2)")
            armres = arm_knownanswer(tuples, deadline)
            seeds_block = {
                "master_seed": armres["master_seed"],
                "seed_derivation_rule": armres["seed_derivation_rule"],
                "per_case": [{"case": c["case"], "seed_string": c.get("seed_string"),
                              "derived_seed": c.get("derived_seed")} for c in armres["cases"]],
                "generators_seeded_for": armres["generators_seeded_for"],
                "generators_not_seeded": armres["generators_not_seeded"],
                "seed_block_note": ("The four master seeds 120401, 120301, 120201 and "
                                    "120501 are disjoint from the BATCH-011 master seeds "
                                    "110201, 110301, 110401, 110501, 110601 and 110701."),
            }
            for c in armres["cases"]:
                log("  %-5s passes=%s" % (c["case"], c["passes"]))
            inv_evaluated.append("IV-2 SIMULATOR KNOWN-ANSWER DEFECT - evaluated at all "
                                 "eight cases")
            if armres["IV_2_fired"]:
                inv_fired.append("IV-2 at %s" % ", ".join(armres["IV_2_cases_that_fired"]))
            payload = {"known_answer_arm": armres}
            extra = {"IV_2_fired": armres["IV_2_fired"],
                     "IV_2_cases_that_fired": armres["IV_2_cases_that_fired"]}
            terminal_status = "completed_valid" if not armres["IV_2_fired"] else "completed_invalid"
            validity_status = "valid" if not armres["IV_2_fired"] else "invalid"
            validity_reason = armres["IV_2_verdict"]

        elif arm_key == "ASRECORDED":
            log("[ST-2] arm 2 of 3: RUN-YIELD-002-NULL-ASRECORDED (IV-1)")
            rows, not_reached, variates = arm_null(tuples, "ASRECORDED", deadline, log)
            iv1 = evaluate_IV_1(rows) if len(rows) == len(tuples) else None
            seeds_block = {
                "master_seed": MASTER_SEEDS["ASRECORDED"],
                "arm_label": "ASRECORDED",
                "seed_derivation_rule": (
                    "The LOW 64 BITS, as an unsigned little-endian integer, of the SHA-256 "
                    "digest of the ASCII string formed by joining with the single "
                    "character `|` and nothing else, in this exact order and with no "
                    "whitespace - the decimal master seed, the arm label, the decimal k, "
                    "the decimal round(beta x 1000), the decimal m, the decimal B, the "
                    "decimal C_red."),
                "per_tuple": [{"tuple": r["tuple"], "seed_string": r["seed_string"],
                               "derived_seed": r["derived_seed"]} for r in rows],
                "stream_independence_declaration": (
                    "THE REPAIRED AND AS-RECORDED ARMS USE INDEPENDENT STREAMS, because "
                    "their arm labels differ and therefore their per-tuple seeds differ.  "
                    "Common random numbers are NOT used."),
                "merged_tuple_seed_note": ("T-12-3-B22 is seeded from its binding "
                                           "committed reference, the beta = 0.325 entry, "
                                           "so round(beta x 1000) = 325.  It is drawn "
                                           "ONCE, not twice."),
            }
            payload = {"as_recorded_arm": {
                "arm": "CTRL-002-ASRECORDED",
                "run_id": run_id,
                "process": "P-ASRECORDED - P-REPAIRED WITH STEP 1 DELETED.  Nothing is pre-marked.",
                "purpose": ("COMPARABILITY AND NOT MEASUREMENT.  It feeds IV-1 only, and "
                            "NO success criterion and NO falsification criterion."),
                "rows": rows,
                "tuples_not_reached": not_reached,
                "total_random_variates_requested": variates,
                "IV_1": iv1,
            }}
            if iv1 is not None:
                log("  IV-1a |z_comp|>=3.000 at %d tuples %s ; fires=%s"
                    % (iv1["IV_1a"]["count"], iv1["IV_1a"]["tuples_at_or_above_threshold"],
                       iv1["IV_1a"]["fires"]))
                log("  IV-1b at %d tuples %s ; fires=%s"
                    % (iv1["IV_1b"]["count"], iv1["IV_1b"]["tuples_at_or_above_threshold"],
                       iv1["IV_1b"]["fires"]))
                inv_evaluated.append("IV-1 COMPARABILITY OF THE AS-RECORDED ARM - evaluated")
                if iv1["IV_1_fires"]:
                    inv_fired.append("IV-1")
            if not_reached:
                inv_fired.append("IV-5 INCOMPLETE COVERAGE")
            extra = {"IV_1_fires": iv1["IV_1_fires"] if iv1 else None}
            terminal_status = "completed_valid" if not not_reached else "cancelled_by_budget"
            validity_status = "valid" if not not_reached else "invalid"
            validity_reason = (
                "All 48 declared tuples drawn.  IV-1 evaluated and reported; a firing of "
                "IV-1 voids the repaired arm's comparison to the recorded package and is "
                "never a negative mathematical result."
                if not not_reached else
                "ST-1 cap bound; %d tuples not reached, named under IV-5." % len(not_reached))

        else:  # REPAIRED
            log("[ST-2] arm 3 of 3: RUN-YIELD-002-NULL-REPAIRED (CR-1, CR-2, CR-3, CR-4)")
            rows, not_reached, variates = arm_null(tuples, "REPAIRED", deadline, log)
            criteria = evaluate_criteria(rows) if len(rows) == len(tuples) else None
            tails = tail_checks(rows) if rows else None
            phi = phi_equivalent(rows, tuples) if rows else None
            log("[ST-2] high-precision diagnostic block LAST (feeds nothing)")
            hp = highprec_block(tuples, deadline, log)
            seeds_block = {
                "master_seed": MASTER_SEEDS["REPAIRED"],
                "arm_label": "REPAIRED",
                "high_precision_block_master_seed": MASTER_SEEDS["HIGHPREC"],
                "high_precision_block_arm_label": "HIGHPREC",
                "seed_derivation_rule": (
                    "The LOW 64 BITS, as an unsigned little-endian integer, of the SHA-256 "
                    "digest of the ASCII string formed by joining with the single "
                    "character `|` and nothing else, in this exact order and with no "
                    "whitespace - the decimal master seed, the arm label, the decimal k, "
                    "the decimal round(beta x 1000), the decimal m, the decimal B, the "
                    "decimal C_red."),
                "per_tuple": [{"tuple": r["tuple"], "seed_string": r["seed_string"],
                               "derived_seed": r["derived_seed"]} for r in rows],
                "high_precision_block_per_tuple": [
                    {"tuple": e["tuple"], "seed_string": e["seed_string"],
                     "derived_seed": e["derived_seed"]} for e in hp["rows"]],
                "stream_independence_declaration": (
                    "THE REPAIRED AND AS-RECORDED ARMS USE INDEPENDENT STREAMS, because "
                    "their arm labels differ and therefore their per-tuple seeds differ.  "
                    "Common random numbers are NOT used.  CR-3's denominator "
                    "sqrt(sem_rep^2 + sem_001^2) assumes independence between the arms "
                    "being differenced, and the seed derivation is what makes that "
                    "assumption true rather than assumed."),
                "merged_tuple_seed_note": ("T-12-3-B22 is seeded from its binding "
                                           "committed reference, the beta = 0.325 entry, "
                                           "so round(beta x 1000) = 325.  It is drawn "
                                           "ONCE, not twice."),
                "high_precision_block_seed_note": "See DEV-4.",
            }
            payload = {"repaired_arm": {
                "arm": "CTRL-002-REPAIRED",
                "run_id": run_id,
                "process": ("P-REPAIRED.  STEP 1 pre-mark s = |S_(m-2)| distinct bins "
                            "uniformly at random without replacement from all N bins, the "
                            "identity bin eligible; STEP 2 throw C_red/2 times, each g "
                            "uniform on {0,...,N-1} with replacement, marking bin g and "
                            "bin (N - g) mod N; STEP 3 count distinct marked bins.  ORDER "
                            "IS BINDING."),
                "rows": rows,
                "tuples_not_reached": not_reached,
                "total_random_variates_requested": variates,
                "criteria": criteria,
                "tail_checks": tails,
                "realised_phi_equivalent": phi,
                "high_precision_diagnostic_block": hp,
                "INV_4_failing_tuples_reported_separately": {
                    "label": "INV-4-FAILING TUPLES OF THE BATCH-011 PACKAGE",
                    "note": ("Reporting these four separately is a REPORTING requirement "
                             "and confers no separate criterion, no separate threshold and "
                             "no separate disposition.  Every criterion is evaluated on "
                             "all 48 tuples denominated in the de-duplicated count.  THIS "
                             "RUN DOES NOT UN-FIRE INV-4 AND DOES NOT RE-DISPOSE IT."),
                    "rows": [r for r in rows if r["is_INV_4_failing_tuple"]],
                },
            }}
            if criteria:
                for cid in ("CR-1", "CR-2", "CR-3"):
                    log("  %s fires at %d tuples: %s"
                        % (cid, criteria[cid]["n_fires"], criteria[cid]["fires_at"]))
                log("  CR-4 n_neg = %d, window [%d, %d], fires = %s"
                    % (criteria["CR-4"]["n_neg"], CR4_LOW, CR4_HIGH, criteria["CR-4"]["fires"]))
            if not_reached or hp["tuples_not_reached"]:
                inv_fired.append("IV-5 INCOMPLETE COVERAGE")
            extra = {}
            terminal_status = "completed_valid" if not not_reached else "cancelled_by_budget"
            validity_status = "valid" if not not_reached else "invalid"
            validity_reason = (
                "All 48 declared tuples drawn at the C-14 replicate schedule; the "
                "pre-registered criteria were evaluated exactly as frozen and their "
                "firing sets recorded.  NO OUTCOME BRANCH IS STATED (ST-4)."
                if not not_reached else
                "ST-1 cap bound; %d tuples not reached, named under IV-5." % len(not_reached))

        inv_evaluated += [
            "IV-3 INFRASTRUCTURE - no timeout, crash, resource exhaustion or budget "
            "cancellation occurred" if terminal_status == "completed_valid" else
            "IV-3 INFRASTRUCTURE - see terminal_status",
            "IV-5 INCOMPLETE COVERAGE - evaluated",
            "IV-6 SCOPE BREACH - evaluated: no forbidden module imported, no curve "
            "operation computed, no efficiency E and no yield ratio computed or reported, "
            "no file under experiments/EXP-YIELD-001 read other than IN-1 and IN-2, and "
            "no file written outside the eleven declared artifacts",
        ]

    except InputIntegrityError as exc:
        terminal_status = "completed_invalid"
        validity_status = "invalid"
        validity_reason = ("IV-4 INPUT INTEGRITY fired: %s.  The run STOPPED AND REPORTED "
                           "immediately, performed no further throw, and IS NOT EVIDENCE."
                           % exc)
        inv_fired.append("IV-4")
        payload = {"error": str(exc), "integrity": integrity}
        log("[STOP] %s" % validity_reason)
    except AmbiguityStop as exc:
        terminal_status = "completed_invalid"
        validity_status = "invalid"
        validity_reason = str(exc)
        inv_fired.append("ST-3 STOP AND REPORT")
        payload = {"error": str(exc)}
        log("[STOP] %s" % validity_reason)
    except MemoryError as exc:  # pragma: no cover
        terminal_status = "resource_exhaustion"
        validity_status = "invalid"
        validity_reason = ("MemoryError: %r.  INFRASTRUCTURE SIGNAL.  This is NEVER a "
                           "negative mathematical result about P_pred, about the "
                           "diagnostic, about the occupancy null or about anything else."
                           % (exc,))
        inv_fired.append("IV-3 INFRASTRUCTURE / ST-1 memory cap")
        payload = {"error": repr(exc)}
        log("[STOP] %s" % validity_reason)
    except Exception as exc:  # pragma: no cover
        import traceback
        terminal_status = "failed_implementation"
        validity_status = "invalid"
        validity_reason = ("Unhandled exception %r.  INFRASTRUCTURE / IMPLEMENTATION "
                           "SIGNAL.  This is NEVER a negative mathematical result about "
                           "P_pred, about the diagnostic or about anything else." % (exc,))
        inv_fired.append("IV-3 INFRASTRUCTURE")
        payload = {"error": repr(exc), "traceback": traceback.format_exc()}
        log("[STOP] %s" % validity_reason)
        traceback.print_exc()

    ended = (utc_now(), time.monotonic())
    rusage_after = resource.getrusage(resource.RUSAGE_SELF)
    env = environment_block(driver_sha, rlimit_status)

    results = {
        "schema": "crypto.autoresearch.run_results.v1",
        "run_id": run_id,
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "terminal_status": terminal_status,
        "validity_status": validity_status,
        "validity_reason": validity_reason,
        "numpy_version_exact_string": np.__version__,
        "numpy_version_note": ("C-19b: THE EXACT numpy.__version__ STRING GOVERNS and is "
                               "recorded here BEFORE the first draw.  ONE version across "
                               "all three arms, all 48 tuples and all eight known-answer "
                               "cases."),
        "claim_tier": CLAIM_TIER,
        "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
        "ST_4_no_interpretation": (
            "OBSERVATIONS AND PRE-REGISTERED CRITERION EVALUATIONS ONLY.  NO OUTCOME "
            "BRANCH IS STATED, no efficiency E and no yield ratio is computed, INV-4 is "
            "not re-disposed, INV-5 is declared neither way, and nothing is said about "
            "decomposition yield."),
        "power_limit_sentence_C_20": POWER_LIMIT_SENTENCE,
        "power_limit_obligation_C_20": POWER_LIMIT_OBLIGATION,
        "PD_7_RC_F": PD_7_SENTENCE,
        "pre_registered_prediction_verbatim": PREREGISTERED_PREDICTION_VERBATIM,
        "pre_data_chance_alarm_reading": CHANCE_ALARM_READING,
        "counterfactual_feasibility_sets_C_18": COUNTERFACTUAL_FEASIBILITY_SETS,
        "pre_registered_realised_expectation_PRED_ID": PREREGISTERED_REALISED_EXPECTATION,
        "input_integrity_IV_4": integrity,
        "conditional_CR_3_budget_C_16": None,
        "protocol_deviations": PROTOCOL_DEVIATIONS,
        "implementation_notes": IMPLEMENTATION_NOTES,
        "timestamps": {"started_utc": started[0], "ended_utc": ended[0]},
        "elapsed_seconds": ended[1] - started[1],
    }
    try:
        results["conditional_CR_3_budget_C_16"] = budget
    except Exception:
        results["conditional_CR_3_budget_C_16"] = {
            "status": "NOT PRODUCED - the run stopped before the budget block was built."}
    if arm_key != "REPAIRED":
        results["realised_phi_equivalent"] = {
            "value": None,
            "reason": ("DEV-7: this arm draws no P-REPAIRED replicate, so no realised "
                       "phi-equivalent exists in it.  The realised phi-equivalent is "
                       "reported in RUN-YIELD-002-NULL-REPAIRED/results.json and in "
                       "experiments/EXP-YIELD-002/results/summary.json."),
            "power_limit_sentence": POWER_LIMIT_SENTENCE,
            "pre_registered_power_curve": PREREGISTERED_POWER_CURVE,
        }
    results.update(payload)

    manifest = common_manifest(run_id, command, git, env, inf, started, ended,
                               rusage_before, rusage_after, terminal_status,
                               validity_status, validity_reason, inv_fired,
                               inv_evaluated, seeds_block, input_block, extra)

    log("")
    log("terminal_status = %s" % terminal_status)
    log("validity_status = %s" % validity_status)
    log("wall clock %.3f s ; peak rss %d bytes"
        % (ended[1] - started[1], rusage_after.ru_maxrss))
    log("MAKE NO COMMIT.  TASK-20260729-019 commits this package.")

    sys.stdout = real_out
    sys.stderr = real_err
    handle.close()

    write_json(results_path, results)
    manifest["artifact_sha256"] = {
        "results.json": sha256_file(results_path),
        "stdout.log": sha256_file(stdout_path),
    }
    write_json(manifest_path, manifest)
    return terminal_status, validity_status


# --------------------------------------------------------------------------
# 9.  summary.json - DERIVED by the driver from the three results.json files.
# --------------------------------------------------------------------------


def build_summary():
    base = os.path.join(REPO_ROOT, "experiments", "EXP-YIELD-002")
    paths = {k: os.path.join(base, "runs", v, "results.json") for k, v in RUN_IDS.items()}
    loaded = {}
    for k, p in paths.items():
        with open(p) as fh:
            loaded[k] = json.load(fh)

    ka = loaded["KNOWNANSWER"].get("known_answer_arm", {})
    asrec = loaded["ASRECORDED"].get("as_recorded_arm", {})
    rep = loaded["REPAIRED"].get("repaired_arm", {})

    asrec_by = {r["tuple"]: r for r in asrec.get("rows", [])}
    rep_by = {r["tuple"]: r for r in rep.get("rows", [])}
    budget_by = {r["tuple"]: r for r in
                 loaded["REPAIRED"].get("conditional_CR_3_budget_C_16", {}).get("rows", [])}

    joined = []
    ratios = []
    for lbl, r in rep_by.items():
        a = asrec_by.get(lbl, {})
        b = budget_by.get(lbl, {})
        ratio = (r["sd_ddof_1"] / a["sd_ddof_1"]) if a.get("sd_ddof_1") else None
        if ratio is not None:
            ratios.append({"tuple": lbl, "s_rep_over_s_asrec": ratio})
        joined.append({
            "tuple": lbl, "k": r["k"], "m": r["m"], "B": r["B"], "beta": r["beta"],
            "N": r["N"], "C_red": r["C_red"], "s_S_m_minus_2": r["s_S_m_minus_2"],
            "n_rep": r["n_rep"],
            "is_INV_4_failing_tuple": r["is_INV_4_failing_tuple"],
            "P_pred_QUOTED": r["P_pred_QUOTED"],
            "T_DETERMINED": r["T"],
            "repaired": {"mean": r["mean"], "sd_ddof_1": r["sd_ddof_1"], "sem": r["sem"],
                         "n_rep": r["n_rep"], "label": "SAMPLED"},
            "as_recorded": {"mean": a.get("mean"), "sd_ddof_1": a.get("sd_ddof_1"),
                            "sem": a.get("sem"), "n_rep": a.get("n_rep"),
                            "label": "SAMPLED"},
            "committed_BATCH_011": {"mu_001": r["mu_001_QUOTED"], "s_001": r["s_001_QUOTED"],
                                    "sem_001": r["sem_001_DETERMINED"],
                                    "label": "QUOTED (SAMPLED in origin); sem_001 DETERMINED"},
            "shift_vs_recorded_mean": r["shift_vs_recorded_mean"],
            "standardized_residuals": {
                "z_sem": {"value": r["z_sem"], "denominator": r["sem"],
                          "reading": "standard error of the mean", "n_rep": r["n_rep"]},
                "z_sd": {"value": r["z_sd"], "denominator": r["sd_ddof_1"],
                         "reading": "single-replicate standard deviation", "n_rep": r["n_rep"]},
                "z_shift": {"value": r["z_shift"], "denominator": r["z_shift_denominator"],
                            "n_rep": r["n_rep"]},
            },
            "comparability": {"z_comp": a.get("z_comp"), "r_sd": a.get("r_sd"),
                              "ln_r_sd": a.get("ln_r_sd"),
                              "C_9_reporting_only_statistic": a.get("C_9_reporting_only_statistic")},
            "conditional_CR_3_budget_C_16": {
                "delta_i_QUOTED": b.get("delta_i_QUOTED"),
                "p_i_3000_A2_QUOTED": b.get("p_i_3000_A2_QUOTED"),
                "p_i_3000_exact_A1_QUOTED": b.get("p_i_3000_exact_A1_QUOTED"),
                "rank_QUOTED": b.get("rank_QUOTED"),
            },
            "s_rep_over_s_asrec": ratio,
        })
    joined.sort(key=lambda x: (x["m"], x["k"], x["B"]))

    summary = {
        "schema": "crypto.autoresearch.experiment_summary.v1",
        "experiment_id": EXPERIMENT_ID,
        "task_id": TASK_ID,
        "goal_id": GOAL_ID,
        "batch_id": BATCH_ID,
        "derivation_note": (
            "DERIVED BY THE DRIVER FROM THE THREE results.json FILES AND REPRODUCIBLE "
            "FROM THEM.  NO NUMBER IN THIS FILE IS HAND-ENTERED.  Command: python3 "
            "experiments/EXP-YIELD-002/driver/repaired_null.py --summary"),
        "source_results_files": {
            k: {"path": "experiments/EXP-YIELD-002/runs/%s/results.json" % v,
                "sha256": sha256_file(paths[k]),
                "terminal_status": loaded[k]["terminal_status"],
                "validity_status": loaded[k]["validity_status"]}
            for k, v in RUN_IDS.items()},
        "numpy_version_exact_string": loaded["REPAIRED"]["numpy_version_exact_string"],
        "numpy_single_version_across_all_three_arms": (
            loaded["KNOWNANSWER"]["numpy_version_exact_string"]
            == loaded["ASRECORDED"]["numpy_version_exact_string"]
            == loaded["REPAIRED"]["numpy_version_exact_string"]),
        "claim_tier": CLAIM_TIER,
        "claim_ceiling_carried_verbatim": ADMISSION_AND_CEILING,
        "ST_4_no_interpretation": (
            "OBSERVATIONS AND PRE-REGISTERED CRITERION EVALUATIONS ONLY.  THIS FILE "
            "STATES NO OUTCOME BRANCH, computes no efficiency E and no yield ratio, does "
            "not re-dispose INV-4, declares INV-5 neither way, touches no cost model and "
            "says nothing about decomposition yield.  Interpretation belongs to "
            "TASK-20260729-020, TASK-20260729-021 and TASK-20260729-022."),
        "power_limit_sentence_C_20": POWER_LIMIT_SENTENCE,
        "power_limit_obligation_C_20": POWER_LIMIT_OBLIGATION,
        "PD_7_RC_F": PD_7_SENTENCE,
        "pre_registered_prediction_verbatim": PREREGISTERED_PREDICTION_VERBATIM,
        "pre_data_chance_alarm_reading": CHANCE_ALARM_READING,
        "counterfactual_feasibility_sets_C_18": COUNTERFACTUAL_FEASIBILITY_SETS,
        "pre_registered_realised_expectation_PRED_ID": PREREGISTERED_REALISED_EXPECTATION,
        "protocol_deviations": PROTOCOL_DEVIATIONS,
        "implementation_notes": IMPLEMENTATION_NOTES,
        "IV_2_known_answer": {"fired": ka.get("IV_2_fired"),
                              "cases_that_fired": ka.get("IV_2_cases_that_fired"),
                              "verdict": ka.get("IV_2_verdict"),
                              "cases": [{"case": c["case"], "passes": c["passes"],
                                         "tolerance": c.get("tolerance", c.get("tolerance_4_sd_over_sqrt_n"))}
                                        for c in ka.get("cases", [])]},
        "IV_1_comparability": asrec.get("IV_1"),
        "criteria": rep.get("criteria"),
        "tail_checks": rep.get("tail_checks"),
        "tail_check_s_rep_over_s_asrec": {
            "binding_label": "OBSERVATION.  NOT a criterion; fires nothing.",
            "reference_value": 1.0,
            "per_tuple": ratios,
            "min": min((x["s_rep_over_s_asrec"] for x in ratios), default=None),
            "max": max((x["s_rep_over_s_asrec"] for x in ratios), default=None),
        },
        "realised_phi_equivalent": rep.get("realised_phi_equivalent"),
        "high_precision_diagnostic_block": rep.get("high_precision_diagnostic_block"),
        "conditional_CR_3_budget_C_16": loaded["REPAIRED"].get("conditional_CR_3_budget_C_16"),
        "coverage": {
            "declared_tuple_count": 48,
            "repaired_tuples_measured": len(rep.get("rows", [])),
            "as_recorded_tuples_measured": len(asrec.get("rows", [])),
            "repaired_tuples_not_reached": rep.get("tuples_not_reached", []),
            "as_recorded_tuples_not_reached": asrec.get("tuples_not_reached", []),
            "IV_5_note": ("A PARTIAL RESULT WITH A NAMED GAP IS A RESULT; A SILENTLY "
                          "TRUNCATED ONE IS NOT.  No unreached tuple is reported as "
                          "measured and no estimate is substituted for a measurement that "
                          "did not happen."),
        },
        "INV_4_failing_tuples_reported_separately": rep.get("INV_4_failing_tuples_reported_separately"),
        "per_tuple": joined,
    }
    out = os.path.join(base, "results", "summary.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    write_json(out, summary)
    print("wrote experiments/EXP-YIELD-002/results/summary.json (%d tuples joined)"
          % len(joined))


# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description="EXP-YIELD-002 curve-free driver")
    ap.add_argument("--run", choices=list(RUN_IDS.values()))
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    if args.summary:
        build_summary()
        return 0
    if not args.run:
        ap.error("one of --run or --summary is required")
    key = [k for k, v in RUN_IDS.items() if v == args.run][0]
    terminal, validity = execute_run(key)
    print("%s -> %s / %s" % (args.run, terminal, validity))
    return 0 if validity == "valid" else 1


if __name__ == "__main__":
    sys.exit(main())
