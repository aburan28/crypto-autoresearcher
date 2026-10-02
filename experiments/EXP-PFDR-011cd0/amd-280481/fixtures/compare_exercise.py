"""Compare the retargeted exercise log with fixtures/exercise-log-after-D7.json step by step,
after normalising timestamps and paths (A-3 fixture_exercise (1)).  Fields compared: step label,
exit code, expected exit, check result, expectation_met; stdout/stderr tails reported beside."""
import json, re, sys
old_p, new_p, out_p = sys.argv[1:4]
o, n = json.load(open(old_p)), json.load(open(new_p))
TS = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?(\+00:00|Z)?")
def norm(x, fx):
    s = json.dumps(x, sort_keys=True)
    s = s.replace(fx, "<FX>").replace("experiments/EXP-PFDR-011cd0/amd-280481/analyze_relcensus.py",
                                      "experiments/EXP-PFDR-011cd0/analyze_relcensus.py")
    s = TS.sub("<TS>", s)
    s = re.sub(r"RUN-[A-Za-z0-9-]+-(\d{8}T\d{6}Z)", "<STAMP>", s)
    s = re.sub(r"\d+\.\d+ ?s\b", "<SEC>", s)
    return s
rows = []
for i, (a, b) in enumerate(zip(o["steps"], n["steps"]), 1):
    f = {k: norm(a.get(k), o["fx"]) == norm(b.get(k), n["fx"]) for k in ("step", "exit_code", "expected_exit", "check", "expectation_met")}
    t = {k: norm(a.get(k), o["fx"]) == norm(b.get(k), n["fx"]) for k in ("stdout_tail", "stderr_tail")}
    rows.append({"step": i, "label": b["step"], "result_fields_equal": f, "results_identical": all(f.values()),
                 "tails_equal_after_normalisation": t,
                 **({} if all(f.values()) else {"old": {k: a.get(k) for k in ("exit_code", "check", "expectation_met")},
                                                 "new": {k: b.get(k) for k in ("exit_code", "check", "expectation_met")}})})
res = {"what": "A-3 fixture exercise (1): retargeted 38 steps vs exercise-log-after-D7.json",
       "old_log": old_p, "new_log": new_p, "steps_old": len(o["steps"]), "steps_new": len(n["steps"]),
       "identical_steps": sum(r["results_identical"] for r in rows),
       "differing_steps": [r["step"] for r in rows if not r["results_identical"]],
       "tail_differences": [r["step"] for r in rows if not all(r["tails_equal_after_normalisation"].values())],
       "steps": rows}
json.dump(res, open(out_p, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("steps_old", "steps_new", "identical_steps", "differing_steps", "tail_differences")}))
