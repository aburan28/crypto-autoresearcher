#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-r1 -- ENTRY POINT for v2 driver commands (addendum PS-2 (a)).

usage (launched only by r1_run_wrapper.py, which sets GFPN_RUN_DIR):
    python3 -B r1_entry_v2.py <v2 driver_args from trial-plan-v2-r1.json>

Order (PS-1; RC-2; RC-3 (a), (d)):
  1. PS-1 P-A: configure cypari2's process-wide PARI stack (parisize 67108864, parisizemax 536870912) BEFORE
     any v2 module is imported.
  2. import v2_common; set v2_common.PLAN_PATH -> trial-plan-v2-r1.json and v2_common.TASK_ID ->
     TASK-20260923-3aa31e; THEN import v2_driver.
  3. after all imports, immediately before dispatch: RC-3 (d) redirection read-back and RC-2 (a) start
     read-back (two fresh cypari2.Pari() handles). Unless every value equals its r1 value, exit 2 before any
     command runs (the refusal is recorded in pari-stack.json; never a result).
  4. dispatch: the UNCHANGED v2_driver.main() on this process's argv.
  5. at exit, normal or by exception: RC-2 (b) exit read-back, VmHWM / VmRSS -> pari-stack.json.
No v2 function is replaced (P-A).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r1_common as R                                    # noqa: E402  (imports no v2 module)

ENTRY = "r1_entry_v2"


def main():
    stack = R.PariStack()
    stack.configure()                                    # step 1: before any v2 import
    run_dir = os.environ.get("GFPN_RUN_DIR")
    if not run_dir:
        print("REFUSING: GFPN_RUN_DIR not set: launch through r1_run_wrapper.py", file=sys.stderr)
        return 2
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C                                # step 2
    C.PLAN_PATH = R.PLAN_V2_R1
    C.TASK_ID = R.TASK_R2
    import v2_driver as D                                # noqa: F401  (after the redirection)
    expected = {"v2_common.PLAN_PATH": R.PLAN_V2_R1, "v2_common.TASK_ID": R.TASK_R2}
    redir, reasons = R.check_redirections(expected)      # step 3
    reasons += stack.start_readback()
    if reasons:
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, "refused_before_any_command", reasons,
                                {"argv": sys.argv[1:]})
        for r in reasons:
            print("REFUSING (no command run): " + r, file=sys.stderr)
        return 2
    status, exc = "command_returned", None
    try:
        D.main()                                         # step 4 (argparse reads sys.argv[1:])
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
