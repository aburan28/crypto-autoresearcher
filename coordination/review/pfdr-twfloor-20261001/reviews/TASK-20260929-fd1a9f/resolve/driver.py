"""Thin capture driver for the F1 bounded recomputation (TASK-20260929-fd1a9f, VF-4).

usage: PYTHONPATH=<detached worktree>/src python driver.py <captures.jsonl> census <census flags...>

Imports the ARCHIVED engine from the detached worktree at 66d6eab71 (asserted),
wraps the solver entry point the census path calls
(crypto_autoresearcher.index_calculus.__main__.solve_index_calculus, called by
_census_instance), records each call's inputs and outputs, and returns the
solver's result object UNCHANGED. No engine file is modified; the census path
runs exactly as `python -m crypto_autoresearcher.index_calculus census ...`
(main(argv) of the archived __main__.py). The capture is used only to CHECK
solves with the disjoint module ec_check.py; nothing here checks anything.
"""
import json
import os
import sys

WT = "/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-twfloor-66d6eab71"


def main():
    cap_path, argv = sys.argv[1], sys.argv[2:]
    import crypto_autoresearcher.index_calculus.__main__ as M  # archived CLI module
    import crypto_autoresearcher.index_calculus.solver as S
    for mod in (M, S):
        if not os.path.realpath(mod.__file__).startswith(os.path.realpath(WT) + "/src/"):
            raise SystemExit(f"engine module resolved outside the detached worktree: {mod.__file__}")
    orig = M.solve_index_calculus
    if orig is not S.solve_index_calculus:
        raise SystemExit("__main__.solve_index_calculus is not solver.solve_index_calculus")
    fh = open(cap_path, "w")
    seq = [0]

    def wrapped(E, P, Q, *args, **kw):
        ic = orig(E, P, Q, *args, **kw)
        try:
            fb = kw.get("factor_base")
            rec = {"seq": seq[0], "p": E.p, "a": E.a, "b": E.b, "N": E.order,
                   "P": list(P) if P is not None else None, "Q": list(Q) if Q is not None else None,
                   "m": kw.get("m"), "seed": kw.get("seed"), "harvest": kw.get("harvest"),
                   "target_label": kw.get("target_label"), "attempt_budget": kw.get("attempt_budget"),
                   "max_attempts": kw.get("max_attempts"),
                   "fb_kind": getattr(fb, "kind", None),
                   "fb_params": {k: v for k, v in (getattr(fb, "params", {}) or {}).items()},
                   "fb_points": [list(pt) for pt in fb.points] if fb is not None else None,
                   "k_solver": ic.k, "verified_flag": ic.verified,
                   "terminated_by": (ic.harvest or {}).get("terminated_by"),
                   "attempts": ic.attempts, "relations": ic.relations, "rank": ic.rank,
                   "s3_solves": ic.s3_solves}
        except Exception as exc:  # capture must never alter the run
            rec = {"seq": seq[0], "capture_error": repr(exc)}
        fh.write(json.dumps(rec, default=str) + "\n")
        fh.flush()
        seq[0] += 1
        return ic

    M.solve_index_calculus = wrapped
    try:
        rc = M.main(argv)
    finally:
        fh.close()
    sys.exit(rc)


if __name__ == "__main__":
    main()
