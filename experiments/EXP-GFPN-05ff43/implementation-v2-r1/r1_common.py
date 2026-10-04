#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r1 and 2-a1-r1 -- shared context of the REPAIR LAYER.

Authority: AMD-EXP-GFPN-05ff43-20260923-paristack (sha256 856fdc1d...c7) read with DEC-20260923-80e280
(conditions RC-1..RC-13). Written by stage R1 (TASK-20260923-a681f9).

ADDITIVE ONLY (addendum PS-2; card R1-1). This module never imports a v2 or v2-a1 module. It holds:
  * paths, identifiers and bound hashes;
  * the PS-1 fix, branch P-A: configure_pari() sets cypari2's process-wide PARI stack to
    parisize 67108864 / parisizemax 536870912 BEFORE any v2 or v2-a1 module is imported (RC-2 (c));
  * the RC-2 read-backs (start: two fresh cypari2.Pari() handles in sequence; exit: through the retained
    handle, with VmHWM / VmRSS) and pari-stack.json;
  * the RC-3 redirection read-back helper.
No function, class or computation of v2 or v2-a1 is replaced (P-A).
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

# ----------------------------------------------------------------------------- bound protocol (RC-1; R-1)
REPAIR_ID = "AMD-EXP-GFPN-05ff43-20260923-paristack"
REPAIR_PATH = os.path.join(EXP_DIR, "amendments", "v2_addendum_paristack.yaml")
REPAIR_SHA256 = "856fdc1d7b71da0cd9073634066dcb2a9a66d69cd10adf4ff5a738f2618390c7"
REPAIR_APPROVAL = "DEC-20260923-80e280"
REPAIR_CONDITIONS = ["RC-%d" % i for i in range(1, 14)]
V2_AMENDMENT_ID = "AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii"
V2_AMENDMENT_PATH = os.path.join(EXP_DIR, "amendments", "v1_to_v2_reanchor_and_arm_iii.yaml")
V2_AMENDMENT_SHA256 = "e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3"
V2_APPROVAL = "DEC-20260923-e788a1"
A1_ADDENDUM_ID = "AMD-EXP-GFPN-05ff43-20260923-rung31"
A1_ADDENDUM_PATH = os.path.join(EXP_DIR, "amendments", "v2_addendum_rung31.yaml")
A1_ADDENDUM_SHA256 = "2c5e052468e37111023dd116706149fb05d691e7188e26ae1e2c069bad792d0c"
A1_APPROVAL = "DEC-20260923-8b2dbf"
BOUND_HASHES = ((V2_AMENDMENT_PATH, V2_AMENDMENT_SHA256), (A1_ADDENDUM_PATH, A1_ADDENDUM_SHA256), (REPAIR_PATH, REPAIR_SHA256))

PROTOCOL_V2_R1 = "2-r1"
PROTOCOL_A1_R1 = "2-a1-r1"

# ----------------------------------------------------------------------------- plans
PLAN_V2 = os.path.join(EXP_DIR, "trial-plan-v2.json")                 # frozen, read-only
PLAN_A1 = os.path.join(EXP_DIR, "trial-plan-v2-a1.json")              # frozen, read-only
PLAN_V2_SHA256 = "16f33e39b58277734f52b4b3c7353a9878ff6703a638a561541adb8f57e44e16"
PLAN_A1_SHA256 = "2a788720bebc2a3848c1c1100aaa31f6c8a196030e668c3e3eb71d0cea255ac6"
PLAN_V2_R1 = os.path.join(EXP_DIR, "trial-plan-v2-r1.json")
PLAN_A1_R1 = os.path.join(EXP_DIR, "trial-plan-v2-a1-r1.json")
LADDER_PATH = os.path.join(EXP_DIR, "implementation", "ladder.json")  # v1, frozen, read-only

# ----------------------------------------------------------------------------- task ids
TASK_R1 = "TASK-20260923-a681f9"          # this stage (development notes only)
TASK_R2 = "TASK-20260923-3aa31e"          # every repaired v2 manifest
TASK_R2B = "TASK-20260923-292052"         # every repaired addendum manifest
ARCHIVE_TASK = "TASK-20260923-b53550"     # the two-phase repair archive
# Never a task id on any r1 artifact (addendum amends_fields; RC-3 (f)). Held as a guard only.
FORBIDDEN_TASK_IDS = ("TASK-20260923-" + "cd932c", "TASK-20260923-" + "6c7f55")

# ----------------------------------------------------------------------------- receipts and phase-A commits
ARCHIVES = os.path.join(REPO, "coordination", "goals", "GOAL-GFPN-380702", "archives")
RECEIPT_V2_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "snapshot-receipt.json")
RECEIPT_V2_PHASE_B = os.path.join(ARCHIVES, "TASK-20260923-0fa03f", "post-run-receipt.json")
RECEIPT_A1_PHASE_A = os.path.join(ARCHIVES, "TASK-20260923-4ff597", "snapshot-receipt.json")
RECEIPT_R1_PHASE_A = os.path.join(ARCHIVES, ARCHIVE_TASK, "snapshot-receipt.json")
RECEIPT_R1_PHASE_B = os.path.join(ARCHIVES, ARCHIVE_TASK, "post-run-receipt.json")
PHASE_A_COMMIT_0FA03F = "fb4597b2014b44a0c9528d48d3ab9997b46f038c"   # CORR-20260923-fb1be8 XD-1; literal (PS-5)
PHASE_A_COMMIT_4FF597 = "36c3b0d2e05878a8df1209b5048f8ce14515c27f"   # literal (PS-5), addendum packages

V2_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2", "experiments/EXP-GFPN-05ff43/implementation-v2.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2.json"]
A1_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2-a1", "experiments/EXP-GFPN-05ff43/implementation-v2-a1.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1.json"]
R1_PATHS_REL = ["experiments/EXP-GFPN-05ff43/implementation-v2-r1", "experiments/EXP-GFPN-05ff43/implementation-v2-r1.md",
                "experiments/EXP-GFPN-05ff43/trial-plan-v2-r1.json", "experiments/EXP-GFPN-05ff43/trial-plan-v2-a1-r1.json"]

# ----------------------------------------------------------------------------- REG-1 (PS-4)
REG1_REFERENCE_RUN = "RUN-GFPN-ac4487"
REG1_EXCLUSION_LIST = os.path.join(HERE, "reg1-exclusion-list.json")

# ----------------------------------------------------------------------------- envelope (AC-1; RC-10)
CAP_BYTES = 10737418240
DRIVER_RSS_LIMIT = 1073741824
MAX_PACKAGES_SHARED = 48

# ----------------------------------------------------------------------------- PS-1: the fix
PS1_BRANCH = "P-A"
PARISIZE = 67108864            # 64 MiB (addendum PS-1 P-A; RC-2: no other value)
PARISIZEMAX = 536870912        # 512 MiB = half of driver_rss_limit_bytes
VMHWM_BOUND = 805306368        # 768 MiB (PS-1 rule_for_the_values; DV-2)
PARI_API = ("h = cypari2.Pari(); h.allocatemem(67108864, 536870912, silent=True)  "
            "[cypari2 2.2.0 Pari.allocatemem(s, sizemax) -> set_pari_stack_size -> libpari paristack_setsize]")
# RC-2 (b): EXIT read-back semantics of default(parisize), established by DV-2 on this host (see
# implementation-v2-r1.md "RC-2 read-back semantics"). "requested": default(parisize) reports the configured
# (requested) size even after the stack grew, so the exit read-back must equal PARISIZE exactly.
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
                    "authority": "%s PS-1 P-A with %s RC-2" % (REPAIR_ID, REPAIR_APPROVAL)}
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
    Returns (record, reasons). The record holds the r1 values only (old values are listed in
    implementation-v2-r1.md; a forbidden task id is never written into a run artifact)."""
    rec, reasons = {}, []
    for key, want in expected.items():
        mod, attr = key.rsplit(".", 1)
        m = sys.modules.get(mod)
        got = getattr(m, attr, "<module %s not loaded>" % mod) if m is not None else "<module %s not loaded>" % mod
        if isinstance(got, tuple):
            got = list(got)
        w = list(want) if isinstance(want, tuple) else want
        ok = got == w
        rec[key] = {"expected_r1_value": w, "read_back": got if ok else "<differs; not recorded>", "equal": ok}
        if not ok:
            reasons.append("RC-3 (d) redirection read-back %s does not equal its r1 value" % key)
    return rec, reasons


def write_pari_stack_json(run_dir, stack, redirections, entry, status, reasons, extra=None):
    obj = {"schema": "crypto.autoresearch.gfpn05.r1.pari_stack.v1", "experiment_id": EXPERIMENT_ID,
           "entry": entry, "status": status, "refusal_reasons": reasons, "pari_stack": stack.rec,
           "redirections": redirections, "written_at": now()}
    if extra:
        obj.update(extra)
    txt = json.dumps(obj, indent=1, default=str)
    for f in FORBIDDEN_TASK_IDS:
        if f in txt:
            raise RuntimeError("refusing to write a forbidden task id into pari-stack.json")
    with open(os.path.join(run_dir, "pari-stack.json"), "w") as fh:
        fh.write(txt)
    return obj
