#!/usr/bin/env python3
"""Run one proves-too-much variant of the producer's gfpn_audit.py, unchanged in
its decision logic (see make_variants.py), with all output under this scratch
directory.  Never touches experiments/ and never goes through run_wrapper.py.

usage: run_object.py VARIANT [EXTRA_ECM_DIR ...]

Harness inputs (the only things set here):
  * the module global REPO is pointed at the repository root, because the copy
    sits outside experiments/EXP-GFPN-726eb2/implementation/ and REPO is
    computed from __file__ (gfpn_audit.py line 46); it is only used to open the
    frozen source texts under inputs/;
  * --ecm-log-dir is a scratch directory holding byte-identical copies of the
    12 GMP-ECM logs the producer's runs consumed (runs/RUN-GFPN-3bbef2/
    certificates/ecm/), plus, for object A only, the genuine GMP-ECM logs made
    by scratch invocation #1 (prep/prep.py);
  * --out is a scratch directory; --rigidity-budget-seconds 14400 as in the
    producer's command.txt.
"""
import importlib.util, os, shutil, sys, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.dirname(HERE)
REPO = "/home/user/crypto-autoresearcher"
ORIG_ECM = os.path.join(REPO, "experiments/EXP-GFPN-726eb2/runs/RUN-GFPN-3bbef2/certificates/ecm")

def main():
    name = sys.argv[1]
    extra = sys.argv[2:]
    vdir = os.path.join(SCR, "variants", name)
    curve = open(os.path.join(vdir, "curve_flag.txt")).read().strip()
    odir = os.path.join(SCR, "objects", name)
    out = os.path.join(odir, "out")
    assert not os.path.exists(out), f"refusing to overwrite {out}"
    hints = os.path.join(odir, "ecm_hints")
    os.makedirs(hints)
    for fn in sorted(os.listdir(ORIG_ECM)):
        shutil.copyfile(os.path.join(ORIG_ECM, fn), os.path.join(hints, fn))
    for d in extra:
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".out"):
                shutil.copyfile(os.path.join(d, fn), os.path.join(hints, fn))
    os.makedirs(out)
    sys.path.insert(0, vdir)
    spec = importlib.util.spec_from_file_location("gfpn_audit", os.path.join(vdir, "gfpn_audit.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO = REPO
    sys.argv = ["gfpn_audit.py", "--curve", curve, "--rigidity-budget-seconds", "14400",
                "--ecm-log-dir", hints, "--out", out]
    t0 = time.time()
    rc = mod.main()
    meta = {"variant": name, "curve_flag": curve, "rc": rc, "wall_seconds": round(time.time() - t0, 1),
            "argv": sys.argv, "ecm_hint_files": sorted(os.listdir(hints)), "gfpn_arith_module": mod.__dict__.get("__file__")}
    json.dump(meta, open(os.path.join(odir, "harness-meta.json"), "w"), indent=2)
    return rc

if __name__ == "__main__":
    sys.exit(main())
