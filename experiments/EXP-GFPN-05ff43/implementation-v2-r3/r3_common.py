#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r3 and 2-a1-r3 -- shared context of the r3 REPAIR LAYER.

Authority (DEC-20260924-e52eec VA-2 order): DEC-20260924-e52eec VA-1..VA-12; AMD-EXP-GFPN-05ff43-20260924-valueclose;
consumercover, launchcover and healthresolve as valueclose incorporates them (never approved); DEC-20260924-15a77a
SC-1..SC-11 re-pointed; seedresolve; solverevent as seedresolve incorporates it; paristack with DEC-20260923-80e280
RC-1..RC-13. Written by the r3 successor stage (TASK-20260924-ed17fe). Started from implementation-v2-r2/r2_common.py
(see implementation-v2-r3.md, file table).

ADDITIVE ONLY. This module never imports a v2 or v2-a1 module, and no r3 file imports an r1, r2 or v1 module. It holds:
  * paths, identifiers and the NINE bound amendment hashes (VA-1; R-1);
  * the PS-1 fix, branch P-A (configure BEFORE any v2 / v2-a1 import; RC-2 (c));
  * the RC-2 read-backs and pari-stack.json;
  * the RC-3 redirection read-back helper;
  * the SE-6 PYTHONHASHSEED read-back of the driver process (DV-13);
  * the forbidden-task-id guards of VA-7 (a), each a separate function that reads no site value (VA-8 (b)).
"""
import datetime
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(EXP_DIR, "..", ".."))
V2_DIR = os.path.join(EXP_DIR, "implementation-v2")
A1_DIR = os.path.join(EXP_DIR, "implementation-v2-a1")
RUNS_DIR = os.path.join(EXP_DIR, "runs")

EXPERIMENT_ID = "EXP-GFPN-05ff43"
HYPOTHESIS_ID = "H-GFPN-9a29be"
HEURISTIC_ID = "HEUR-GFPN-DFLAT"

# ----------------------------------------------------------------------------- bound protocol (VA-1; R-1: NINE hashes)
AMD = os.path.join(EXP_DIR, "amendments")
V2_AMENDMENT_ID = "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii"
V2_AMENDMENT_PATH = os.path.join(AMD, "v1_to_v2_reanchor_and_arm_iii.yaml")
V2_AMENDMENT_SHA256 = "e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3"
V2_APPROVAL = "DEC-20260923-e788a1"
A1_ADDENDUM_ID = "AMD-EXP-GFPN-05ff43-20260923-rung31"
A1_ADDENDUM_PATH = os.path.join(AMD, "v2_addendum_rung31.yaml")
A1_ADDENDUM_SHA256 = "2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c"
A1_APPROVAL = "DEC-20260923-8b2dbf"
PARISTACK_ID = "AMD-EXP-GFPN-05ff43-20260923-paristack"
PARISTACK_PATH = os.path.join(AMD, "v2_addendum_paristack.yaml")
PARISTACK_SHA256 = "856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7"
PARISTACK_APPROVAL = "DEC-20260923-80e280"
PARISTACK_CONDITIONS = ["RC-%d" % i for i in range(1, 14)]
SEEDRESOLVE_ID = "AMD-EXP-GFPN-05ff43-20260924-seedresolve"
SEEDRESOLVE_PATH = os.path.join(AMD, "v2_addendum_seedresolve.yaml")
SEEDRESOLVE_SHA256 = "dc714a446a22a99fd6762196d4e6ad1b8c9e7eb3920d64cf26036f95ecadee81"
SEEDRESOLVE_APPROVAL = "DEC-20260924-15a77a"
SEEDRESOLVE_CONDITIONS = ["SC-%d" % i for i in range(1, 12)]
SEEDRESOLVE_CORRECTION = "CORR-20260924-36ce25"
NEVER_APPROVED = "incorporated by reference, never approved"
SOLVEREVENT_ID = "AMD-EXP-GFPN-05ff43-20260923-solverevent"
SOLVEREVENT_PATH = os.path.join(AMD, "v2_addendum_solverevent.yaml")
SOLVEREVENT_SHA256 = "011d4b2c11f99d696281ccfdd4d65ece4fefcc6ae71de3de813049bbeb2d9b7f"
HEALTHRESOLVE_ID = "AMD-EXP-GFPN-05ff43-20260924-healthresolve"
HEALTHRESOLVE_PATH = os.path.join(AMD, "v2_addendum_healthresolve.yaml")
HEALTHRESOLVE_SHA256 = "ccb55334c542c809b8526e54a2985627a44c435e5ca68a14ef5f6a779291a70d"
LAUNCHCOVER_ID = "AMD-EXP-GFPN-05ff43-20260924-launchcover"
LAUNCHCOVER_PATH = os.path.join(AMD, "v2_addendum_launchcover.yaml")
LAUNCHCOVER_SHA256 = "c27ffe5c15d13d1c1137bdba11944ac53f0e91c79d8f460a5d2b18066ca5f447"
CONSUMERCOVER_ID = "AMD-EXP-GFPN-05ff43-20260924-consumercover"
CONSUMERCOVER_PATH = os.path.join(AMD, "v2_addendum_consumercover.yaml")
CONSUMERCOVER_SHA256 = "a900d757980b379c301393d51bde008847f5280fd0b6ac237ae1f67efce4eee0"
VALUECLOSE_ID = "AMD-EXP-GFPN-05ff43-20260924-valueclose"
VALUECLOSE_PATH = os.path.join(AMD, "v2_addendum_valueclose.yaml")
VALUECLOSE_SHA256 = "877c5b898921812cd4da2c35a905a423ecd77bdbe204c73e902b459829e8e4f1"
VALUECLOSE_APPROVAL = "DEC-20260924-e52eec"
VALUECLOSE_CONDITIONS = ["VA-%d" % i for i in range(1, 13)]
CORRECTIONS = ["CORR-20260924-36ce25", "CORR-20260924-5b83a1", "CORR-20260924-432f43", "CORR-20260924-e78b7a",
               "CORR-20260924-838ff2", "CORR-20260924-27a4b6"]
BOUND_HASHES = ((V2_AMENDMENT_PATH, V2_AMENDMENT_SHA256), (A1_ADDENDUM_PATH, A1_ADDENDUM_SHA256),
                (PARISTACK_PATH, PARISTACK_SHA256), (SEEDRESOLVE_PATH, SEEDRESOLVE_SHA256),
                (SOLVEREVENT_PATH, SOLVEREVENT_SHA256), (HEALTHRESOLVE_PATH, HEALTHRESOLVE_SHA256),
                (LAUNCHCOVER_PATH, LAUNCHCOVER_SHA256), (CONSUMERCOVER_PATH, CONSUMERCOVER_SHA256),
                (VALUECLOSE_PATH, VALUECLOSE_SHA256))

PROTOCOL_V2_R3 = "2-r3"
PROTOCOL_A1_R3 = "2-a1-r3"

# ----------------------------------------------------------------------------- SE-2 with SF-1..SF-3, HR-1..HR-8 (declared values)
K = 5                        # SF-3: at most K + 1 = 6 attempts per wrapped call, further bounded by the SF-2 (c) / HR-6 cap
SPACING_S = 2.0              # SF-2 (a); SC-11 (d)
RENAME_SUFFIX = ".ssf-attempt%d"   # SC-11 (a), appended to the full file name
RESOLVE_CAP_RULE = ("SF-2 (c) with SC-11 (c), (e) and, at the health site, HR-6: attempt 2 always starts on an SSF attempt 1 "
                    "(subject to K); attempt k + 1 (k >= 2) starts only if the summed wall seconds of attempts 2..k (each: recorded "
                    "end UTC minus recorded start UTC) are below the timeout of that wrapped call -- at v2_driver.solve the timeout_s "
                    "argument actually passed to that call, at a1_health.run_system the value a1_health.DEV_TIMEOUT_S read at call "
                    "time (the timeout the frozen run_system passes to run_child); otherwise the recorded result is attempt k's and "
                    "solver-events.json records resolve_cap_reached")
REG1_D_BRANCH = "d-parsed"   # SF-4
SITE_S1 = "v2_driver.solve"
SITE_S2 = "a1_health.run_system"
SITE_S3 = "v2_driver.solve/callgrind"
DV17_R = 10                  # CG-5 (d); CC-8 (b)

# ----------------------------------------------------------------------------- plans
PLAN_V2 = os.path.join(EXP_DIR, "trial-plan-v2.json")                 # frozen, read-only
PLAN_A1 = os.path.join(EXP_DIR, "trial-plan-v2-a1.json")              # frozen, read-only
PLAN_V2_SHA256 = "16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16"
PLAN_A1_SHA256 = "2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6"
PLAN_V2_R1 = os.path.join(EXP_DIR, "trial-plan-v2-r1.json")           # stage-R1 output, read-only (ids retired)
PLAN_A1_R1 = os.path.join(EXP_DIR, "trial-plan-v2-a1-r1.json")
PLAN_V2_R2 = os.path.join(EXP_DIR, "trial-plan-v2-r2.json")           # stage-r2 output, read-only (ids retired)
PLAN_A1_R2 = os.path.join(EXP_DIR, "trial-plan-v2-a1-r2.json")
PLAN_V2_R3 = os.path.join(EXP_DIR, "trial-plan-v2-r3.json")
PLAN_A1_R3 = os.path.join(EXP_DIR, "trial-plan-v2-a1-r3.json")
LADDER_PATH = os.path.join(EXP_DIR, "implementation", "ladder.json")  # v1, frozen, read-only

# ----------------------------------------------------------------------------- task ids
TASK_STAGE = "TASK-20260924-ed17fe"       # this r3 successor stage (development notes only)
TASK_RUNS_V2 = "TASK-20260924-4351ac"     # every repaired v2 manifest (R2'')
TASK_RUNS_A1 = "TASK-20260924-b3e690"     # every repaired addendum manifest (R2b'')
ARCHIVE_TASK = "TASK-20260924-f1fb0e"     # the two-phase archive of this stage (phase A) and of R2'' (phase B)
# Never a task id on any r3 artifact (R-13 list of HR-10; VA-7). Held as guard constants only; split so that the full
# strings do not occur in this file.
FORBIDDEN_TASK_IDS = tuple(["TASK-20260923-" + t for t in ("cd932c", "6c7f55", "3aa31e", "292052")]
                           + ["TASK-20260924-" + t for t in ("946010", "9490b1")])

# ----------------------------------------------------------------------------- receipts and phase-A commits
ARCHIVES = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives")
RECEIPT_V2_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "snapshot-receipt.json")
RECEIPT_V2_PHASE_B = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "post-run-receipt.json")
RECEIPT_A1_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-4ff597", "snapshot-receipt.json")
RECEIPT_R3_PHASE_A = os.path.join(ARCHIVES, ARCHIVE_TASK, "snapshot-receipt.json")
RECEIPT_R3_PHASE_B = os.path.join(ARCHIVES, ARCHIVE_TASK, "post-run-receipt.json")
PHASE_A_COMMIT_0FA03F = "fb4597b2014b44a0c9528d48d3ab9997b46f038c"   # CORR-20260923-fb1be8 XD-1; literal (PS-5)
PHASE_A_COMMIT_4FF597 = "36c3b0d2e05878a8df1209b5048f8ce14515c27f"   # literal (PS-5), addendum packages

V2_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2", "experiments/EXP-GFPN-05ff43/implementation-v2.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2.json"]
A1_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2-a1", "experiments/EXP-GFPN-05ff43/implementation-v2-a1.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json"]
R3_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2-r3", "experiments/EXP-GFPN-05ff43/implementation-v2-r3.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2-r3.json", "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r3.json"]

# ----------------------------------------------------------------------------- ids (PS-3 retirement; SC-10; DEC-20260924-bea197 R-8)
USED_V2 = ["RUN-GFPN-ac4487", "RUN-GFPN-3377f1"]                          # kept as records, never re-run
RETIRED_V2_UNUSED = [  # paristack PS-3 retirement, verbatim order (29)
    "RUN-GFPN-76420e", "RUN-GFPN-b231c1", "RUN-GFPN-a07776", "RUN-GFPN-1ad09b", "RUN-GFPN-0c7483", "RUN-GFPN-4abae0", "RUN-GFPN-9e4212",
    "RUN-GFPN-bbbbe3", "RUN-GFPN-a521dd", "RUN-GFPN-a07b6d", "RUN-GFPN-dc1d4e", "RUN-GFPN-b9207c", "RUN-GFPN-aa56bd", "RUN-GFPN-e5b90d",
    "RUN-GFPN-d2f759", "RUN-GFPN-745cad", "RUN-GFPN-aeff00", "RUN-GFPN-3db273", "RUN-GFPN-3be8a4", "RUN-GFPN-00e64b", "RUN-GFPN-c5294d",
    "RUN-GFPN-36cad2", "RUN-GFPN-11d2ad", "RUN-GFPN-fc5d58", "RUN-GFPN-8f86cc", "RUN-GFPN-e26e4b", "RUN-GFPN-9da048", "RUN-GFPN-59320d",
    "RUN-GFPN-1596f6"]
RETIRED_A1_UNUSED = ["RUN-GFPN-0d91bf", "RUN-GFPN-8c772a", "RUN-GFPN-569fd7", "RUN-GFPN-086463", "RUN-GFPN-bab146",
                     "RUN-GFPN-7dd55d", "RUN-GFPN-47aa51", "RUN-GFPN-3a70f1", "RUN-GFPN-ae4918", "RUN-GFPN-8cfac3",
                     "RUN-GFPN-6a7f35"]
# The 42 r1 ids (DEC-20260923-582d6b R-4), in r1 minting order.
RETIRED_R1 = [
    "RUN-GFPN-a61a10", "RUN-GFPN-30d3ee", "RUN-GFPN-b0993b", "RUN-GFPN-3e521f", "RUN-GFPN-4fc824", "RUN-GFPN-27c136", "RUN-GFPN-fc29b6",
    "RUN-GFPN-072f55", "RUN-GFPN-a6ac23", "RUN-GFPN-d48e01", "RUN-GFPN-9696d7", "RUN-GFPN-d6468a", "RUN-GFPN-98d454", "RUN-GFPN-bda7a9",
    "RUN-GFPN-1bcead", "RUN-GFPN-b76390", "RUN-GFPN-aad5a9", "RUN-GFPN-286cdb", "RUN-GFPN-4e37c2", "RUN-GFPN-5cb274", "RUN-GFPN-1626b4",
    "RUN-GFPN-2d52fc", "RUN-GFPN-f917a8", "RUN-GFPN-5fc8d7", "RUN-GFPN-8b0643", "RUN-GFPN-e2a2a5", "RUN-GFPN-3e568b", "RUN-GFPN-25adbd",
    "RUN-GFPN-a3773d", "RUN-GFPN-cb9dff", "RUN-GFPN-3868df", "RUN-GFPN-14cfa2", "RUN-GFPN-dd64d4", "RUN-GFPN-097656", "RUN-GFPN-8fd922",
    "RUN-GFPN-a901d9", "RUN-GFPN-6435b2", "RUN-GFPN-f7733e", "RUN-GFPN-3a1c9f", "RUN-GFPN-c8870b", "RUN-GFPN-8e4d7d", "RUN-GFPN-51e56b"]
# The 42 r2 ids (DEC-20260924-bea197 R-8), in r2 minting order.
RETIRED_R2 = [
    "RUN-GFPN-a09162", "RUN-GFPN-0dca26", "RUN-GFPN-b69444", "RUN-GFPN-22ee49", "RUN-GFPN-bf833b", "RUN-GFPN-4bafcf", "RUN-GFPN-93607c",
    "RUN-GFPN-3a01f3", "RUN-GFPN-4ea41a", "RUN-GFPN-b9059b", "RUN-GFPN-bebfc0", "RUN-GFPN-48c73f", "RUN-GFPN-724745", "RUN-GFPN-477ae1",
    "RUN-GFPN-479e05", "RUN-GFPN-c3fb79", "RUN-GFPN-ecefab", "RUN-GFPN-4189b4", "RUN-GFPN-ff8c15", "RUN-GFPN-6c464c", "RUN-GFPN-0bb551",
    "RUN-GFPN-f78382", "RUN-GFPN-f4302b", "RUN-GFPN-beac9f", "RUN-GFPN-d9f68f", "RUN-GFPN-c8be8b", "RUN-GFPN-2f3442", "RUN-GFPN-9e266d",
    "RUN-GFPN-c3062b", "RUN-GFPN-cfe871", "RUN-GFPN-c8c1f8", "RUN-GFPN-599b87", "RUN-GFPN-af4935", "RUN-GFPN-ad6372", "RUN-GFPN-b0bfca",
    "RUN-GFPN-a11a01", "RUN-GFPN-585023", "RUN-GFPN-411471", "RUN-GFPN-09fbad", "RUN-GFPN-20faaa", "RUN-GFPN-dc7e11", "RUN-GFPN-0fa6cd"]
RETIRED_82 = RETIRED_V2_UNUSED + RETIRED_A1_UNUSED + RETIRED_R1            # DEC-20260924-15a77a SC-10
RETIRED_ALL = RETIRED_82 + RETIRED_R2                                     # 124

# ----------------------------------------------------------------------------- REG-1 (PS-4 read with SE-4 and SF-4; CG-4)
REG1_REFERENCE_RUN = "RUN-GFPN-ac4487"
REG1_EXCLUSION_LIST = os.path.join(HERE, "reg1-exclusion-list.json")    # byte-identical copy of X1..X17 (DV-8)
REG1_EXCLUSION_SHA256 = "4122bcb06c1c1bdd7613ef20fa62d09207916badf7786ad3c314a04094a99f2c"

# ----------------------------------------------------------------------------- envelope (AC-1; RC-10; VA-10)
CAP_BYTES = 10737418240
DRIVER_RSS_LIMIT = 1073741824
MAX_PACKAGES_SHARED = 48
DRIVER_PYTHONHASHSEED = "0"  # SE-6; CORR-20260923-111265

# ----------------------------------------------------------------------------- PS-1: the fix
PS1_BRANCH = "P-A"
PARISIZE = 67108864            # 64 MiB (paristack PS-1 P-A; RC-2: no other value)
PARISIZEMAX = 536870912        # 512 MiB = half of driver_rss_limit_bytes
VMHWM_BOUND = 805306368        # 768 MiB (PS-1 rule_for_the_values; DV-2)
PARI_API = ("h = cypari2.Pari(); h.allocatemem(67108864, 536870912, silent=True)  "
            "[cypari2 2.2.0 Pari.allocatemem(s, sizemax) -> set_pari_stack_size -> libpari paristack_setsize]")
# RC-2 (b): EXIT read-back semantics of default(parisize), established by THIS stage's semantics probe on the delivered
# configuration code (implementation-v2-r3.md). "requested": default(parisize) reports the configured size after growth.
PARISIZE_EXIT_SEMANTICS = "requested"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical_json(obj):
    """RC-4 (c) canonical form: sort_keys, separators (',', ':'), ensure_ascii false."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def receipt_paths(receipt):
    ps = receipt.get("path_sha256") or {}
    if isinstance(ps, list):
        return {x["path"]: x["sha256"] for x in ps}
    return dict(ps)


def proc_status():
    """VmHWM / VmRSS / VmPeak / VmSize of this process, bytes."""
    out = {}
    with open("/proc/self/status") as fh:
        for line in fh:
            k = line.split(":", 1)[0]
            if k in ("VmHWM", "VmRSS", "VmPeak", "VmSize"):
                out[k + "_bytes"] = int(line.split()[1]) * 1024
    return out


def v2_or_a1_modules_loaded():
    return sorted(m for m in sys.modules if m.startswith(("v2_", "a1_")))


def hashseed_readback():
    """SE-6 / DV-13: the PYTHONHASHSEED condition of THIS (driver) process, read back inside it."""
    return {"PYTHONHASHSEED_env": os.environ.get("PYTHONHASHSEED"),
            "sys_flags_hash_randomization": sys.flags.hash_randomization,
            "hash_of_probe_string": hash("r3-hashseed-probe"),
            "pid": os.getpid(), "at": now()}


# ----------------------------------------------------------------------------- VA-7 (a) guards (read no site value)
def forbidden_ids_in_text(txt):
    """The forbidden task ids (R-13 list) that occur in txt. Used ONLY on text that carries no site value: plan text,
    r3 constants and redirected attribute values, and the pari-stack.json serialization (VA-7 (a), (b))."""
    return [f for f in FORBIDDEN_TASK_IDS if f in txt]


def forbidden_ids_in_values(values):
    """VA-7 (a): r3 constants and redirected attribute values EQUAL to (or containing) a forbidden id."""
    bad = []
    for v in values:
        for x in (v if isinstance(v, (list, tuple)) else [v]):
            if isinstance(x, str) and forbidden_ids_in_text(x):
                bad.append(x)
    return bad


def r3_constant_values():
    """Every r3 task-id constant and every value an entry redirects an attribute to (VA-7 (a))."""
    return [TASK_STAGE, TASK_RUNS_V2, TASK_RUNS_A1, ARCHIVE_TASK, PROTOCOL_V2_R3, PROTOCOL_A1_R3,
            PLAN_V2_R3, PLAN_A1_R3, RECEIPT_R3_PHASE_A, RECEIPT_R3_PHASE_B]


# ----------------------------------------------------------------------------- the seven repair amendments (VA-1)
REPAIR_KEYS = ("paristack", "seedresolve", "solverevent", "healthresolve", "launchcover", "consumercover", "valueclose")


def repair_amendments():
    """The seven repair amendments with their standing (VA-1)."""
    return {
        "paristack": {"id": PARISTACK_ID, "sha256": PARISTACK_SHA256, "approval_decision": PARISTACK_APPROVAL,
                      "conditions": PARISTACK_CONDITIONS},
        "seedresolve": {"id": SEEDRESOLVE_ID, "sha256": SEEDRESOLVE_SHA256, "approval_decision": SEEDRESOLVE_APPROVAL,
                        "conditions": SEEDRESOLVE_CONDITIONS, "correction": SEEDRESOLVE_CORRECTION},
        "solverevent": {"id": SOLVEREVENT_ID, "sha256": SOLVEREVENT_SHA256, "standing": NEVER_APPROVED},
        "healthresolve": {"id": HEALTHRESOLVE_ID, "sha256": HEALTHRESOLVE_SHA256, "standing": NEVER_APPROVED},
        "launchcover": {"id": LAUNCHCOVER_ID, "sha256": LAUNCHCOVER_SHA256, "standing": NEVER_APPROVED},
        "consumercover": {"id": CONSUMERCOVER_ID, "sha256": CONSUMERCOVER_SHA256, "standing": NEVER_APPROVED},
        "valueclose": {"id": VALUECLOSE_ID, "sha256": VALUECLOSE_SHA256, "approval_decision": VALUECLOSE_APPROVAL,
                       "conditions": VALUECLOSE_CONDITIONS}}


# ----------------------------------------------------------------------------- PS-1 P-A configuration and RC-2 read-backs
class PariStack:
    """Configures the process-wide PARI stack (P-A) and performs the RC-2 read-backs.

    configure() MUST run before the first import of any v2 or v2-a1 module (RC-2 (c)); it records whether it did.
    start_readback(): after all imports, immediately before dispatch: a FRESH cypari2.Pari() handle (as
    v2_common.py line 253 constructs one), default(parisize) and default(parisizemax); then a SECOND fresh
    handle and both again. Every reading must equal the configured values exactly (RC-2 (a)).
    exit_readback(): through the RETAINED second handle (constructing a new handle would itself re-size the
    stack), plus VmHWM / VmRSS (RC-2 (b); PS-1 read_back)."""

    def __init__(self):
        self.rec = {"branch": PS1_BRANCH, "configured": {"parisize": PARISIZE, "parisizemax": PARISIZEMAX},
                    "api": PARI_API, "exit_parisize_semantics": PARISIZE_EXIT_SEMANTICS,
                    "authority": "%s PS-1 P-A with %s RC-2 (re-pointed to r3 by %s VA-3)" % (PARISTACK_ID, PARISTACK_APPROVAL, VALUECLOSE_APPROVAL)}
        self.handle = None

    def configure(self):
        before = v2_or_a1_modules_loaded()
        self.rec["v2_or_a1_modules_loaded_before_configuring"] = before
        self.rec["configured_before_first_v2_or_a1_import"] = not before
        self.rec["cypari2_imported_before_configuring"] = "cypari2" in sys.modules
        import cypari2
        h = cypari2.Pari()
        h.allocatemem(PARISIZE, PARISIZEMAX, silent=True)
        self.rec["configured_at"] = now()
        self.rec["versions"] = versions()
        return self.rec

    @staticmethod
    def _read(h):
        return {"parisize": int(h.default("parisize")), "parisizemax": int(h.default("parisizemax")),
                "stacksize_current": int(h.stacksize()), "stacksizemax_current": int(h.stacksizemax())}

    def start_readback(self):
        import cypari2
        h1 = cypari2.Pari()
        r1 = self._read(h1)
        h2 = cypari2.Pari()
        r2 = self._read(h2)
        self.handle = h2
        reasons = []
        for i, r in ((1, r1), (2, r2)):
            if r["parisize"] != PARISIZE or r["parisizemax"] != PARISIZEMAX:
                reasons.append("RC-2 (a) start read-back through fresh handle %d: parisize %s parisizemax %s != configured %s / %s"
                               % (i, r["parisize"], r["parisizemax"], PARISIZE, PARISIZEMAX))
        self.rec["start_readback"] = {"fresh_handle_1": r1, "fresh_handle_2": r2, "at": now(), "pass": not reasons,
                                      "proc_status": proc_status()}
        return reasons

    def exit_readback(self):
        h = self.handle
        if h is None:
            import cypari2
            h = cypari2.Pari()
            how = "fresh handle (no retained handle: start read-back did not run)"
        else:
            how = "retained second start handle (no re-construction)"
        r = self._read(h)
        ok_max = r["parisizemax"] == PARISIZEMAX
        if PARISIZE_EXIT_SEMANTICS == "requested":
            ok_size = r["parisize"] == PARISIZE
        else:
            ok_size = PARISIZE <= r["parisize"] <= PARISIZEMAX
        ps = proc_status()
        self.rec["exit_readback"] = dict(r, read_through=how, at=now(), proc_status=ps, pass_parisizemax_exact=ok_max,
                                         pass_parisize=ok_size, parisize_rule=PARISIZE_EXIT_SEMANTICS,
                                         vmhwm_at_most_768MiB=ps.get("VmHWM_bytes", 0) <= VMHWM_BOUND,
                                         pass_=ok_max and ok_size)
        return self.rec["exit_readback"]


def versions():
    import importlib.metadata as md
    out = {"python": sys.version.split()[0]}
    try:
        out["cypari2"] = md.version("cypari2")
    except Exception as e:                               # noqa: BLE001
        out["cypari2"] = "ERROR %r" % (e,)
    try:
        import cypari2
        out["pari_library"] = str(cypari2.Pari.pari_version())
    except Exception as e:                               # noqa: BLE001
        out["pari_library"] = "ERROR %r" % (e,)
    return out


def check_redirections(expected):
    """RC-3 (d): read every redirected attribute back from its module. expected: {"module.ATTR": value}.
    Returns (record, reasons). The record holds the r3 values only (old values are listed in implementation-v2-r3.md).
    VA-7 (a): a redirected value equal to (or containing) a forbidden task id is refused."""
    rec, reasons = {}, []
    for key, want in expected.items():
        mod, attr = key.rsplit(".", 1)
        m = sys.modules.get(mod)
        got = getattr(m, attr, "<module %s not loaded>" % mod) if m is not None else "<module %s not loaded>" % mod
        if isinstance(got, tuple):
            got = list(got)
        w = list(want) if isinstance(want, tuple) else want
        ok = got == w
        rec[key] = {"expected_r3_value": w, "read_back": got if ok else "<differs; not recorded>", "equal": ok}
        if not ok:
            reasons.append("RC-3 (d) redirection read-back %s does not equal its r3 value" % key)
        if forbidden_ids_in_values([w]):
            reasons.append("VA-7 (a) the r3 value of redirected attribute %s carries a forbidden task id" % key)
    bad = forbidden_ids_in_values(r3_constant_values())
    if bad:
        reasons.append("VA-7 (a) an r3 constant carries a forbidden task id")
    return rec, reasons


def write_pari_stack_json(run_dir, stack, redirections, entry, status, reasons, extra=None):
    """pari-stack.json carries no site value (PARI read-backs, redirections, the hash-seed read-back)."""
    obj = {"schema": "crypto.autoresearch.gfpn05.r3.pari_stack.v1", "experiment_id": EXPERIMENT_ID,
           "entry": entry, "status": status, "refusal_reasons": reasons, "pari_stack": stack.rec,
           "redirections": redirections, "written_at": now()}
    if extra:
        obj.update(extra)
    txt = json.dumps(obj, indent=1, default=str)
    if forbidden_ids_in_text(txt):                        # VA-7 (a); a file with no site value
        raise RuntimeError("refusing to write a forbidden task id into pari-stack.json")
    with open(os.path.join(run_dir, "pari-stack.json"), "w") as fh:
        fh.write(txt)
    return obj
