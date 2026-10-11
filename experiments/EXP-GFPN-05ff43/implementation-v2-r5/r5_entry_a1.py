#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocol 2-a1-r5 -- ENTRY POINT for v2-a1 driver commands (paristack PS-2 (a); solverevent SE-3;
healthresolve HR-3; readbackfull RL-1, RL-5; card R5S-1, R5S-2, R5S-3). Started from implementation-v2-r4/r4_entry_a1.py (see implementation-v2-r5.md); that r4 file itself started from implementation-v2-r3/r3_entry_a1.py.

usage (launched only by r5_run_wrapper.py, which sets GFPN_RUN_DIR and PYTHONHASHSEED="0"):
    python3 -B r5_entry_a1.py <v2-a1 driver_args from trial-plan-v2-a1-r5.json>

Order (R5S-2; DEC-20260924-daf670 LKA-3):
  1. PS-1 P-A: configure the process-wide PARI stack BEFORE any v2 or v2-a1 module is imported.
  2. import a1_common (it imports no v2 module at module level) and set, BEFORE importing a1_driver (whose line 30
     calls a1_common.redirect_v2() at import):
       PLAN_A1_PATH -> trial-plan-v2-a1-r5.json, V2_PLAN_PATH -> trial-plan-v2-r5.json,
       RECEIPT_V2_PHASE_B -> coordination/goals/GOAL-GFPN-380702/archives/TASK-20260925-0ed1be/post-run-receipt.json,
       V2_GATE_PACKAGES -> the four r5 gate ids, TASK_ID_RUNS -> TASK-20260925-23c435, PROTOCOL_VERSION -> "2-a1-r5".
     import a1_driver (redirect_v2 then sets v2_common.PLAN_PATH to the redirected PLAN_A1_PATH).
     AFTER importing a1_driver: v2_common.TASK_ID -> TASK-20260925-23c435. v2_common.PLAN_PATH is NEVER set to
     trial-plan-v2-r5.json here.
  3. SE-3: after `import a1_driver`, replace v2_driver.solve (a1_driver's D) by the r5 re-solve wrapper.
     HR-3: after `import a1_driver` (which imports a1_health at its line 38), replace a1_health.run_system by the r5
     health wrapper. RL-1: then replace v2_solver.run_child by the r5 launch recorder.
  4. after all imports, immediately before dispatch: RC-3 (d) read-back of every redirected attribute, the SE-3, HR-3
     and RL-5 read-backs, the SE-6 PYTHONHASHSEED read-back and the RC-2 (a) start read-back; exit 2 before any
     command unless each is as required.
  5. dispatch: the UNCHANGED a1_driver.main().
  6. at exit: RC-2 (b) exit read-back -> pari-stack.json.
The functions replaced here are v2_driver.solve (SE-3), a1_health.run_system (HR-3) and v2_solver.run_child (RL-1);
nothing else. The RG-1 callback is a registration, not a replacement.
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402  (imports no v2 / v2-a1 module)
import r5_resolve as RS                                  # noqa: E402  (imports no v2 / v2-a1 module)
import r5_recorder as REC                                # noqa: E402  (imports no v2 / v2-a1 module)

ENTRY = "r5_entry_a1"
SE3_KEY = "v2_driver.solve (SE-3 replacement)"
HR3_KEY = "a1_health.run_system (HR-3 replacement)"
RL1_KEY = "v2_solver.run_child (RL-1 launch recorder; RL-5 install read-back)"


def r5_gate_ids():
    """The four r5 gate ids: the images of the four v2 gate packages, read from the r5 v2 plan."""
    return tuple(R.load_json(R.PLAN_V2_R5)["gate"]["blocking_packages"])


def main():
    stack = R.PariStack()
    stack.configure()                                    # step 1
    run_dir = os.environ.get("GFPN_RUN_DIR")
    if not run_dir:
        print("REFUSING: GFPN_RUN_DIR not set: launch through r5_run_wrapper.py", file=sys.stderr)
        return 2
    gate_ids = r5_gate_ids()
    sys.path.insert(0, R.V2_DIR)
    sys.path.insert(0, R.A1_DIR)
    import a1_common as AC                               # step 2
    AC.PLAN_A1_PATH = R.PLAN_A1_R5
    AC.V2_PLAN_PATH = R.PLAN_V2_R5
    AC.RECEIPT_V2_PHASE_B = R.RECEIPT_R5_PHASE_B
    AC.V2_GATE_PACKAGES = gate_ids
    AC.TASK_ID_RUNS = R.TASK_RUNS_A1
    AC.PROTOCOL_VERSION = R.PROTOCOL_A1_R5
    import a1_driver as DR                               # calls AC.redirect_v2() at import; imports a1_health
    import v2_common as C
    C.TASK_ID = R.TASK_RUNS_A1                           # after a1_driver (RC-3 (b))
    import v2_driver as D
    import a1_health as H
    import a1_pari as P
    import v2_solver as V
    RS.install(D, run_dir)                               # step 3 (SE-3), after `import a1_driver`
    RS.install_health(H, run_dir)                        # step 3 (HR-3), after `import a1_driver`
    REC.install(V, run_dir)                              # step 3 (RL-1), after SE-3 and HR-3
    expected = {"a1_common.PLAN_A1_PATH": R.PLAN_A1_R5, "a1_common.V2_PLAN_PATH": R.PLAN_V2_R5,
                "a1_common.RECEIPT_V2_PHASE_B": R.RECEIPT_R5_PHASE_B, "a1_common.V2_GATE_PACKAGES": gate_ids,
                "a1_common.TASK_ID_RUNS": R.TASK_RUNS_A1, "a1_common.PROTOCOL_VERSION": R.PROTOCOL_A1_R5,
                "v2_common.PLAN_PATH": R.PLAN_A1_R5, "v2_common.TASK_ID": R.TASK_RUNS_A1}
    redir, reasons = R.check_redirections(expected)      # step 4
    if DR.C is not C:
        reasons.append("RC-3 (d) a1_driver.C is not the v2_common module object")
    if DR.D is not D:
        reasons.append("SE-3 read-back: a1_driver.D is not the v2_driver module object")
    if list(gate_ids) != list(R.load_json(R.PLAN_A1_R5)["gate"]["v2_blocking_packages"]):
        reasons.append("RC-3 (d) the r5 gate ids of trial-plan-v2-r5.json differ from trial-plan-v2-a1-r5.json gate.v2_blocking_packages")
    se3, se3_reasons = RS.readback(D)
    redir[SE3_KEY] = dict(se3, equal=not se3_reasons)
    reasons += se3_reasons
    hr3, hr3_reasons = RS.readback_health(H, DR)
    redir[HR3_KEY] = dict(hr3, equal=not hr3_reasons)
    reasons += hr3_reasons
    rl1, rl1_reasons = REC.readback(V, users=(D, H, P))
    redir[RL1_KEY] = dict(rl1, equal=not rl1_reasons)
    reasons += rl1_reasons
    hs = R.hashseed_readback()
    reasons += stack.start_readback()
    extra = {"argv": sys.argv[1:], "python_hash_seed_driver_readback": hs, "cap_env_readback": R.cap_env_readback()}
    if reasons:
        R.write_pari_stack_json(run_dir, stack, redir, ENTRY, "refused_before_any_command", reasons, extra)
        for r in reasons:
            print("REFUSING (no command run): " + r, file=sys.stderr)
        return 2
    RS.begin()                                           # initial solver-events.json, only after every read-back passed
    status, exc = "command_returned", None
    try:
        DR.main()                                        # step 5
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
