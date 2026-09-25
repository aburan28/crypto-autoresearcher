#!/usr/bin/env python3
"""EXP-GFPN-05ff43 protocols 2-r5 / 2-a1-r5 -- the PARAMETRISATION ACCOUNTING of DEC-20260924-15a77a SC-3 (DV-15)
and SC-4 (the r5 checker), re-pointed to both wrapped sites by DEC-20260924-e52eec VA-3 (and to r5 by DEC-20260924-daf670 LKA-3 and DEC-20260925-fc8dbb), with the frozen v2_solver
imported read-only and NO solver child. Started from implementation-v2-r4/r4_accounting.py (unchanged logic; module names re-pointed to r5; that r4 file itself started from implementation-v2-r3/r3_accounting.py, per implementation-v2-r4.md).

For an msolve output that v2_solver.parse_msolve_param reads as param, with w the eliminating polynomial and den the
denominator exactly as v2_solver.rational_solutions reads them (v2_solver.py lines 444-445):
  n_roots    = number of distinct roots of w in F_p, as w.roots() returns them (line 453);
  n_den_zero = roots r with den(r) = 0 (lines 455-457);
  n_arity    = roots skipped for arity (lines 466-468);
  n_points   = len(sols) returned by v2_solver.rational_solutions;
  n_distinct = number of distinct tuples among sols.
INVARIANT for an output the frozen classifier calls ok: n_den_zero = 0, n_arity = 0, n_distinct = n_points = n_roots.
The per-root loop below mirrors rational_solutions (lines 453-469) only to COUNT the skips; its point list is asserted
equal to what the frozen rational_solutions returns, so the counts are the frozen function's.
A violation is RECORDED, never acted on (SC-4); in the r5 stage it is a STOP (SC-3).
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r5_common as R                                    # noqa: E402

EXTRA_VAR_LINE = "Adding a linear form with an extra variable"


def _v2():
    if R.V2_DIR not in sys.path:
        sys.path.insert(0, R.V2_DIR)
    import v2_solver as V                                # read-only import; launches nothing here
    return V


def ms_header(ms_path):
    """(names, p) from an msolve input file's first two lines (write_msolve_input, v2_arms.py lines 692-708)."""
    with open(ms_path) as fh:
        names = fh.readline().strip().split(",")
        p = int(fh.readline().strip())
    return names, p


def nvars_p(out_path, ms_path=None, log_path=None, payload=None):
    """Input variable count and characteristic. Source preference: the retained .ms header; otherwise the msolve
    output header (char, varnames) minus msolve's added variable when the log records it. The source is returned."""
    if ms_path and os.path.exists(ms_path):
        names, p = ms_header(ms_path)
        return len(names), p, "input .ms header"
    added = False
    if log_path and os.path.exists(log_path):
        added = EXTRA_VAR_LINE in open(log_path, errors="replace").read()
    n = len(payload["varnames"]) - (1 if added else 0)
    return n, int(payload["char"]), "msolve output header%s" % (" minus the added linear-form variable (log)" if added else "")


def accounting(out_path, ms_path=None, log_path=None, nvars=None, p=None):
    import flint
    V = _v2()
    kind, payload = V.parse_msolve_param(out_path)
    rec = {"output_sha256": R.sha256_file(out_path) if os.path.exists(out_path) else None, "parse_kind": kind}
    if kind != "param":
        rec["applicable"] = False
        return rec
    if nvars is None or p is None:
        nvars, p, src = nvars_p(out_path, ms_path, log_path, payload)
    else:
        src = "given"
    rec.update(applicable=True, p=p, nvars=nvars, nvars_p_source=src)
    w = flint.nmod_poly(payload["elim"][1], p)
    den = flint.nmod_poly(payload["den"][1], p)
    roots = w.roots()
    n_den_zero = n_arity = 0
    pts = []
    for r, _mult in roots:
        r = int(r)
        dn = int(den(r))
        if dn == 0:
            n_den_zero += 1
            continue
        vals = []
        for entry in payload["params"]:
            polyc = entry[0]
            cst = int(entry[1]) if len(entry) > 1 else 1
            v = flint.nmod_poly(polyc[1], p)
            vals.append((-int(v(r)) * pow(cst * dn, -1, p)) % p)
        if len(vals) == nvars - 1:
            vals.append(r % p)
        if len(vals) != nvars:
            n_arity += 1
            continue
        pts.append(vals)
    sols, sinfo = V.rational_solutions(payload, p, nvars)
    rec["mirror_equals_frozen_rational_solutions"] = [list(map(int, s)) for s in sols] == pts
    rec.update(n_roots=len(roots), n_den_zero=n_den_zero, n_arity=n_arity, n_points=len(sols),
               n_distinct=len({tuple(int(x) for x in s) for s in sols}), elim_degree=sinfo.get("elim_degree"),
               elim_squarefree=sinfo.get("elim_squarefree"), header_degree=payload.get("degree"))
    rec["invariant_holds"] = (rec["n_den_zero"] == 0 and rec["n_arity"] == 0
                              and rec["n_distinct"] == rec["n_points"] == rec["n_roots"])
    return rec
