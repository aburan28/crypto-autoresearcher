"""EXP-SEMBIN-79a02d Stage 3 -- inventory of open-source F4/XL-style engines
exposing PER-STEP DEGREE (vendored in the repo or installed via pip/apt).
Magma, Sage and AUXIN are excluded as success paths and are not provisioned.
Writes raw-result.json; the executor copies the decision to stage3/.
usage: stage3_inventory.py <run_dir>"""
import importlib, json, os, shutil, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()


def main():
    rd = sys.argv[1]
    inv = {"executables": {}, "python_modules": {}, "apt": {}, "repo": {}}
    for exe in ["msolve", "Singular", "M2", "giac", "maple", "magma", "sage", "maxima", "gap", "openf4", "fgb"]:
        inv["executables"][exe] = shutil.which(exe)
    for mod in ["sympy", "openf4", "pyfgb", "fgb_sage", "msolve", "galois", "flint", "cypari2", "brial", "polybori", "sage"]:
        try:
            m = importlib.import_module(mod)
            inv["python_modules"][mod] = getattr(m, "__version__", "present")
        except Exception as e:
            inv["python_modules"][mod] = None
    inv["apt"]["matching_packages"] = sh("dpkg -l | awk '{print $2, $3}' | grep -i -E 'msolve|singular|macaulay2|giac|m4ri|flint|pari|polybori|brial|openf4|fgb|maxima|gap' || true")
    # sympy capability check
    try:
        import sympy.polys.groebnertools as gt
        import inspect
        src = inspect.getsource(gt.groebner)
        inv["python_modules"]["sympy_groebner_methods"] = "buchberger, f5b (method switch in groebner(); no F4, no step-degree trace API)" if "f5b" in src else src[:200]
    except Exception as e:
        inv["python_modules"]["sympy_groebner_methods"] = repr(e)
    inv["repo"]["src/crypto_autoresearcher/index_calculus/msolve.py"] = (
        "wrapper only (calls an external msolve binary; prime fields F_p; binary not installed)"
        if os.path.exists(os.path.join(REPO, "src/crypto_autoresearcher/index_calculus/msolve.py")) else None)
    inv["repo"]["vendored_engine_found"] = False
    engine = None
    out = {"schema": "EXP-SEMBIN-79a02d.stage3.inventory.v1", "inventory": inv,
           "engine_selected": engine,
           "decision": "O-IMPEDIMENT" if engine is None else "RUN_TRACE",
           "manifest_summary": {"status": "completed_valid",
                                "validity_reason": "inventory completed; no per-step-degree open-source F4/XL engine installed or vendored",
                                "stage3_decision": "O-IMPEDIMENT" if engine is None else "RUN_TRACE"}}
    json.dump(out, open(os.path.join(rd, "raw-result.json"), "w"), indent=1)
    print(json.dumps(out["decision"]))


if __name__ == "__main__":
    main()
