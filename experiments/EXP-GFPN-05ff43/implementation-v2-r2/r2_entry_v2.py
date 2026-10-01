#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-r2 -- ENTRY POINT for v2 driver commands (paristack PS-2 (a); solverevent SE-3;
seedresolve SF-7; card ST-2, ST-3). Started from implementation-v2-r1/r1_entry_v2.py.

usage (launched only by r2_run_wrapper.py, which sets GFPN_RUN_DIR and PYTHONHASHSEED="0"):
    python3 -B r2_entry_v2.py <v2 driver_args from trial-plan-v2-r2.json>

Order:
  1. PS-1 P-A: configure cypari2's process-wide PARI stack (parisize 67108864, parisizemax 536870912) BEFORE any v2
     module is imported (RC-2 (c)).
  2. import v2_common; set v2_common.PLAN_PATH -> trial-plan-v2-r2.json and v2_common.TASK_ID ->
     TASK-20260924-946010 (RC-3 (a) re-pointed; ST-3 (a)); THEN import v2_driver.
  3. SE-3: replace v2_driver.solve by the r2 re-solve wrapper (r2_resolve), which calls the ORIGINAL function.
  4. after all imports, immediately before dispatch: RC-3 (d) redirection read-back, the SE-3 replacement read-back,
     the SE-6 PYTHONHASHSEED read-back and the RC-2 (a) start read-back. Unless every redirection and the
     replacement read back as required and the PARI read-backs are exact, exit 2 before any command runs (recorded in
     pari-stack.json; never a result).
  5. dispatch: the UNCHANGED v2_driver.main() on this process's argv.
  6. at exit, normal or by exception: RC-2 (b) exit read-back, VmHWM / VmRSS -> pari-stack.json.
The only function replaced is v2_driver.solve (SE-3). v2_common.curve_order_pari is not replaced (P-A).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r2_common as R                                    # noqa: E402  (imports no v2 module)
import r2_resolve as RS                                  # noqa: E402  (imports no v2 module)

ENTRY = "r2_entry_v2"


def main():
    stack = R.PariStack()
    stack.configure()                                    # step 1: before any v2 import
    run_dir = os.environ.get("GFPN_RUN_DIR")
    if not run_dir:
        print("REFUSING: GFPN_RUN_DIR not set: launch through r2_run_wrapper.py", file=sys.stderr)
        return 2
    sys.path.insert(0, R.V2_DIR)
    import v2_common as C                                # step 2
    C.PLAN_PATH = R.PLAN_V2_R2
    C.TASK_ID = R.TASK_RUNS_V2
    import v2_driver as D                                # after the redirection
    RS.install(D, run_dir)                               # step 3 (SE-3)
    expected = {"v2_common.PLAN_PATH": R.PLAN_V2_R2, "v2_common.TASK_ID": R.TASK_RUNS_V2}
    redir, reasons = R.check_redirections(expected)      # step 4
    se3, se3_reasons = RS.readback(D)
    redir["v2_driver.solve (SE-3 replacement)"] = dict(se3, equal=not se3_reasons)
    reasons += se3_reasons
    hs = R.hashseed_readback()
    reasons += stack.start_readback()
    extra = {"argv": sys.argv[1:], "python_hash_seed_driver_readback": hs}
    if reasons:
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, "refused_before_any_command", reasons, extra)
        for r in reasons:
            print("REFUSING (no command run): " + r, file=sys.stderr)
        return 2
    RS.begin()                                           # initial solver-events.json, only after every read-back passed
    status, exc = "command_returned", None
    try:
        D.main()                                         # step 5 (argparse reads sys.argv[1:])
    except SystemExit as e:
        status = "command_exited_%s" % (e.code,)
        exc = e
    except BaseException as e:                           # noqa: BLE001
        status = "command_raised_%s" % type(e).__name__
        exc = e
    finally:
        ex = stack.exit_readback()                       # step 6
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, status, [], dict(extra, exit_readback_pass=ex["pass_"]))
    if exc is not None:
        raise exc
    return 0


if __name__ == "__main__":
    sys.exit(main())
