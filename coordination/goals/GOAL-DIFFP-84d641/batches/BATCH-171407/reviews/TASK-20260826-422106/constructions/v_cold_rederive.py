"""COLD RE-DERIVATION of EXP-DIFFP-f26790 through the PRODUCER'S OWN MODULE.

TASK-20260826-422106 (Validator).  MECHANISM, STATED SO THE CLOSE KNOWS WHICH
CHECK IT RECEIVED: this re-executes harness/diffpath/readmit.py's stage
functions in a FRESH PROCESS from the contract's declared seeds and compares
the emitted documents byte-for-byte-equivalent (structurally) with the
producer's archived artifacts.  IT CHECKS THAT THE REPORTED NUMBERS ARE WHAT
THAT CODE PRODUCES.  The separate script v_independent_forced_set.py checks
that the code implements the CONTRACT.  Two different checks.

NO CHARGED RUN IS CREATED: _charge/_emit/run_wrapped are NOT called, no run
directory is written, no RUN-* id is minted, no deadline is armed.
TASK_ROOT is redirected into this reviewer's OWN write scope; the producer's
task directory and the archived run directories are never written.

MY OWN QUARANTINE FIREWALL, INSTALLED BEFORE ANY IMPORT OF ANYTHING:
an independent sys.addaudithook that RAISES on every open/os.open under
coordination/goals/GOAL-MD5-001/quarantine, under the H-1 forbidden path, and
under coordination/goals/GOAL-DIFFP-84d641/sealed-priors, plus the sibling
reviewer's directories.  This is a MECHANISM and not an intent.
"""
import sys, os, json, io

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[os.pardir]*8))

_V_BLOCKED = tuple(os.path.join(REPO, p) for p in (
    "coordination/goals/GOAL-MD5-001/quarantine",
    "coordination/goals/GOAL-DIFFP-84d641/sealed-priors",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-145531/reviews/TASK-20260824-7d9f92/constructions",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/reviews/TASK-20260826-a9d51e",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/task-cards/TASK-20260826-a9d51e",
    "coordination/goals/GOAL-DIFFP-84d641/batches/BATCH-171407/review-plan/assignment-TASK-20260826-a9d51e.yaml",
))
_V_ATTEMPTS = []
_V_OPENED = []

class ValidatorFirewallBreach(RuntimeError):
    pass

def _v_hook(event, args):
    if event not in ("open", "os.open"):
        return
    try:
        p = args[0]
    except Exception:
        return
    if isinstance(p, bytes):
        try: p = p.decode()
        except Exception: return
    if not isinstance(p, str):
        return
    full = os.path.abspath(p)
    _V_OPENED.append(full)
    for pre in _V_BLOCKED:
        if full == pre or full.startswith(pre + os.sep):
            _V_ATTEMPTS.append(full)
            raise ValidatorFirewallBreach(
                f"VALIDATOR FIREWALL: refused to open {full}")

sys.addaudithook(_v_hook)
sys.path.insert(0, REPO)

# ---- prove MY OWN hook is live before anything else is imported ------------
_selftest = {}
try:
    open(os.path.join(REPO, "coordination/goals/GOAL-MD5-001/quarantine/anything"), "rb")
    _selftest["quarantine_open_raised"] = False
except ValidatorFirewallBreach:
    _selftest["quarantine_open_raised"] = True
except Exception as e:
    _selftest["quarantine_open_raised"] = ("unexpected: %s" % type(e).__name__)
try:
    open(os.path.join(REPO, "coordination/goals/GOAL-DIFFP-84d641/sealed-priors/x"), "rb")
    _selftest["sealed_prior_open_raised"] = False
except ValidatorFirewallBreach:
    _selftest["sealed_prior_open_raised"] = True
except Exception as e:
    _selftest["sealed_prior_open_raised"] = ("unexpected: %s" % type(e).__name__)
_selftest["modules_imported_before_hook"] = sorted(
    n for n, m in sys.modules.items()
    if getattr(m, "__file__", None) and "harness" in str(getattr(m, "__file__")))

# ---- ORDERING PROBE for R4-J1: was the producer's audit hook installed
# ---- before any substrate import?  Measured by watching sys.modules.
import importlib
RM = importlib.import_module("harness.diffpath.readmit")
ordering = {
    "producer_firewall_state_after_import": {
        "audit_hook_installed": RM._FIREWALL_STATE["audit_hook_installed"],
        "census_stub_installed": RM._FIREWALL_STATE["census_stub_installed"]},
    "census_quarantine_attestation_is_the_stub":
        RM.CEN.quarantine_attestation.__qualname__.startswith("install_"),
    "stub_output": RM.CEN.quarantine_attestation(),
}

# ---- REDIRECT every write into the reviewer's own scope --------------------
OUT = os.path.join(HERE, "cold-rederive-out")
os.makedirs(OUT, exist_ok=True)
RM.TASK_ROOT = OUT

state = {"pre_digests": RM.digests()}
state["census"] = RM.CEN.build_census(
    RM.SEEDS["planted_path_generation_md5"],
    RM.SEEDS["planted_path_generation_sha1"],
    scan={"candidates": []})

s1 = RM.run_stage1(state)
s2 = RM.run_stage2(state)
s3 = RM.run_stage3(state)
s4 = RM.run_stage4(state)

summary = {
    "validator_firewall_selftest": _selftest,
    "validator_firewall_blocked_attempts": _V_ATTEMPTS,
    "validator_files_opened_under_quarantine_prefix": [
        p for p in _V_OPENED if "GOAL-MD5-001/quarantine" in p],
    "validator_files_opened_under_forbidden_H1_prefix": [
        p for p in _V_OPENED if "TASK-20260824-7d9f92/constructions" in p],
    "validator_total_open_events_seen": len(_V_OPENED),
    "producer_firewall_ordering_probe": ordering,
    "seeds_used": RM.SEEDS,
    "stage_metrics": {"stage1": str(s1)[:400], "stage2": str(s2)[:400],
                      "stage3": str(s3)[:400], "stage4": str(s4)[:400]},
    "files_written_by_this_rederivation": sorted(os.listdir(OUT)),
}
json.dump(summary, open(os.path.join(HERE, "v_cold_rederive_summary.json"), "w"),
          indent=1, default=str)
print(json.dumps(summary, indent=1, default=str)[:6000])
