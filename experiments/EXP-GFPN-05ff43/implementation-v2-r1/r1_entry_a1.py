#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-a1-r1 -- ENTRY POINT for v2-a1 driver commands (addendum PS-2 (a)).

usage (launched only by r1_run_wrapper.py, which sets GFPN_RUN_DIR):
    python3 -B r1_entry_a1.py <v2-a1 driver_args from trial-plan-v2-a1-r1.json>

Order (PS-1; RC-2; RC-3 (b), (d)):
  1. PS-1 P-A: configure the process-wide PARI stack BEFORE any v2 or v2-a1 module is imported.
  2. import a1_common (it imports no v2 module at module level) and set, BEFORE importing a1_driver (whose
     line 30 calls a1_common.redirect_v2() at import):
       PLAN_A1_PATH -> trial-plan-v2-a1-r1.json, V2_PLAN_PATH -> trial-plan-v2-r1.json,
       RECEIPT_V2_PHASE_B -> the TASK-20260923-b53550 phase-B receipt, V2_GATE_PACKAGES -> the four r1 gate ids,
       TASK_ID_RUNS -> TASK-20260923-292052, PROTOCOL_VERSION -> "2-a1-r1".
     import a1_driver (redirect_v2 then sets v2_common.PLAN_PATH to the redirected PLAN_A1_PATH).
     AFTER importing a1_driver: v2_common.TASK_ID -> TASK-20260923-292052 (redirect_v2's default task_id is
     bound at definition, a1_common.py line 90). v2_common.PLAN_PATH is NEVER set to trial-plan-v2-r1.json here.
  3. after all imports, immediately before dispatch: RC-3 (d) read-back of every redirected attribute and the
     RC-2 (a) start read-back; exit 2 before any command unless each equals its r1 value.
  4. dispatch: the UNCHANGED a1_driver.main().
  5. at exit: RC-2 (b) exit read-back -> pari-stack.json.
No v2 or v2-a1 function is replaced (P-A).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_common as R                                    # noqa: E402  (imports no v2 / v2-a1 module)

ENTRY = "r1_entry_a1"


def r1_gate_ids():
    """The four r1 gate ids: the images of the four v2 gate packages, read from the r1 v2 plan."""
    return tuple(R.load_json(R.PLAN_V2_R1)["gate"]["blocking_packages"])


def main():
    stack = R.PariStack()
    stack.configure()                                    # step 1
    run_dir = os.environ.get("GFPN_RUN_DIR")
    if not run_dir:
        print("REFUSING: GFPN_RUN_DIR not set: launch through r1_run_wrapper.py", file=sys.stderr)
        return 2
    gate_ids = r1_gate_ids()
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC                               # step 2
    AC.PLAN_A1_PATH = R.PLAN_A1_R1
    AC.V2_PLAN_PATH = R.PLAN_V2_R1
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R1_PHASE_B
    AC.V2_GATE_PACKAGES = gate_ids
    AC.TASK_ID_RUNS = R.TASK_R2B
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R1
    import a1_driver as DR                               # calls AC.redirect_v2() at import
    import v2_common as C
    C.TASK_ID = R.TASK_R2B                               # after a1_driver (RC-3 (b))
    expected = {"a1_common.PLAN_A1_PATH": R.PLAN_A1_R1, "a1_common.V2_PLAN_PATH": R.PLAN_V2_R1,
                "a1_common.RECEIPT_V2_PHASE_B": R.RECEIPT_R1_PHASE_B, "a1_common.V2_GATE_PACKAGES": gate_ids,
                "a1_common.TASK_ID_RUNS": R.TASK_R2B, "a1_common.PROTOCOL_VERSION": R.PROTOCOL_A1_R1,
                "v2_common.PLAN_PATH": R.PLAN_A1_R1, "v2_common.TASK_ID": R.TASK_R2B}
    redir, reasons = R.check_redirections(expected)      # step 3
    if DR.C is not C:
        reasons.append("RC-3 (d) a1_driver.C is not the v2_common module object")
    if list(gate_ids) != list(R.load_json(R.PLAN_A1_R1)["gate"]["v2_blocking_packages"]):
        reasons.append("RC-3 (d) the r1 gate ids of trial-plan-v2-r1.json differ from trial-plan-v2-a1-r1.json gate.v2_blocking_packages")
    reasons += stack.start_readback()
    if reasons:
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, "refused_before_any_command", reasons,
                                {"argv": sys.argv[1:]})
        for r in reasons:
            print("REFUSING (no command run): " + r, file=sys.stderr)
        return 2
    status, exc = "command_returned", None
    try:
        DR.main()                                        # step 4
    except SystemExit as e:
        status = "command_exited_%s" % (e.code,)
        exc = e
    except BaseException as e:                           # noqa: BLE001
        status = "command_raised_%s" % type(e).__name__
        exc = e
    finally:
        ex = stack.exit_readback()                       # step 5
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, status, [], {"argv": sys.argv[1:],
                                "exit_readback_pass": ex["pass_"]})
    if exc is not None:
        raise exc
    return 0


if __name__ == "__main__":
    sys.exit(main())
