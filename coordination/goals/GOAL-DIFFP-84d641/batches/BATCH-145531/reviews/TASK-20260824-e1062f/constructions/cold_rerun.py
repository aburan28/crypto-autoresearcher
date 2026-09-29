"""COLD RE-RUN of EXP-DIFFP-04082e's deterministic outputs, TASK-20260824-e1062f.

NOT A CHARGED RUN.  It calls the committed module's pure stage functions
directly and never main()/_emit()/_charge(), so it creates NO run directory, NO
RUN-* id, NO manifest and NO armed deadline, and it consumes no ceiling.
TASK_ROOT is redirected into THIS REVIEW'S OWN constructions/coldrun/ so that
not one byte of the producer's task directory or of the archived run
directories is written.
"""
import json, os, sys, time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../../.."))
sys.path.insert(0, REPO)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "coldrun")
os.makedirs(OUT, exist_ok=True)

from harness.diffpath import depgraph as D          # noqa: E402
from harness.diffpath import census as CEN          # noqa: E402

assert D.TASK_ROOT != OUT
D.TASK_ROOT = OUT                                   # redirect every _write_json
t0 = time.monotonic()
D.install_quarantine_firewall()
state = {"pre_digests": D.digests()}
state["census"] = CEN.build_census(
    D.SEEDS["planted_path_generation_md5"],
    D.SEEDS["planted_path_generation_sha1"],
    scan={"candidates": []})
stages = []
for name, fn in (("run_graph", D.run_graph), ("run_partition", D.run_partition),
                 ("run_offdiagonal", D.run_offdiagonal),
                 ("run_null_object", D.run_null_object), ("run_rc1", D.run_rc1)):
    t = time.monotonic()
    res, _raw = fn(state)
    stages.append({"stage": name, "seconds": round(time.monotonic() - t, 3),
                   "metrics": res.metrics, "seed": res.seed,
                   "stdout": res.stdout})
post = D.digests()
json.dump({"stages": stages,
           "frozen_comparison": D.compare_digests(state["pre_digests"], post),
           "total_seconds": round(time.monotonic() - t0, 3)},
          open(os.path.join(OUT, "cold-metrics.json"), "w"), indent=1, default=str)
print(json.dumps({s["stage"]: s["metrics"] for s in stages}, indent=1, default=str))
print("TOTAL_SECONDS", round(time.monotonic() - t0, 3))
