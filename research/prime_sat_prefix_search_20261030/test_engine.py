#!/usr/bin/env python3
"""The four admitted synthetic families; no EC input generation or benchmark."""
import argparse
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))


def suite():
    import engine
    import check
    import driver
    limits = {"degree": 2, "rows": 256, "pc_calls": 512, "native_conflicts_per_call": 20000,
              "native_decisions_per_call": 20000, "outer_calls": 9}
    cases = [
        ("positive", 2, 2, [{3: 1, 0: 4}], [], None, [3], [0, 1, 2]),
        ("negative", 2, 2, [{3: 1}], [], None, [0, 1, 2], [0, 1, 2]),
        ("empty", 2, 2, [{0: 1}], [], None, [], [0, 1, 2]),
        ("fiber", 3, 1, [{1: 1}], [[-2, -3]], 3, [0], [0, 1, 3]),
    ]
    assertions, transcripts, worker_records = [], {}, {}
    def demand(name, value):
        assertions.append({"name": name, "passed": bool(value)})
        if not value:
            raise AssertionError(name)
    for name, n, m, polys, domain, bound, expected, schedule in cases:
        for strategy in engine.STRATEGIES:
            inp = {"p": 5, "n": n, "projected_bits": m, "polynomials": polys,
                   "domain": domain, "prefix_depths": schedule, "expected_models": expected}
            if bound is not None:
                inp["aux_bound"] = bound
            job = {"id": name + "-" + strategy, "cell_id": name, "input": inp,
                   "encoding": "synthetic", "strategy": strategy, "limits": limits}
            with tempfile.TemporaryDirectory(prefix="psearch-software-") as directory:
                output = Path(directory)
                row = driver.bounded_arm(job, output, 5)
                demand(job["id"] + "/worker", row["worker"]["returncode"] == 0)
                answer = json.loads((output / row["transcript"]["artifact"]).read_text())
                partial = json.loads((output / "transcripts" / (job["id"] + ".partial.json")).read_text())
                demand(job["id"] + "/durable_partial", partial == answer)
                worker_records[job["id"]] = {"row": row,
                    "stdout": (output / row["worker"]["stdout"]["artifact"]).read_text(),
                    "stderr": (output / row["worker"]["stderr"]["artifact"]).read_text()}
            checked = engine.adapter.verify_transcript(5, n, m, polys, domain, answer, aux_bound=bound)
            key = name + "/" + strategy
            demand(key + "/complete", answer["status"] == "complete" and checked["projected_model_set_complete"])
            demand(key + "/models", checked["projected_models"] == expected)
            check.counters_check(answer, n, limits)
            demand(key + "/counters", True)
            transcripts[key] = answer
            if name == "positive" and strategy != "model_only":
                demand(key + "/early", any(x["trigger"] == "partial" and x["depth"] == 1 and
                                            x["prefix"] == 0 and x["assigned_count"] < n for x in answer["learned"]))
            if name == "negative":
                demand(key + "/no_false_prefix", all(x["depth"] == n for x in answer["learned"]))
            if name == "empty":
                demand(key + "/empty_clause", any(x["clause"] == [] for x in answer["learned"]))
            print(json.dumps({"case": key, "status": "passed"}), flush=True)
    prop = engine.PrefixPropagator(engine.legacy.CountedRing(3, 5), [{1: 1}], 1, limits,
                                   "model_only", [0, 1, 3])
    prop.on_assignment(-1, fixed=True)
    prop.on_new_level()
    prop.on_assignment(2)
    prop.on_new_level()
    prop.on_assignment(-3)
    prop.on_backtrack(1)
    demand("backtrack/one", set(prop.assignments) == {0, 1})
    prop.on_backtrack(0)
    demand("backtrack/fixed", prop.assignments == {0: (0, 0, True)})
    demand("queue/no_clause", prop.has_clause() is False)
    try:
        prop._reject(0)
    except AssertionError:
        demand("reject/no_clause", True)
    else:
        demand("reject/no_clause", False)
    # Direct callback test, no additional native solver instance.
    capped = engine.PrefixPropagator(engine.legacy.CountedRing(2, 5), [{3: 1}], 2,
                                     {**limits, "pc_calls": 0}, "partial_prefix", [0, 1, 2])
    demand("budget/false_model", capped.check_model([1, 2]) is False)
    demand("budget/fallback", capped.events["pc_calls"] == 0 and capped.events["leaf_fallbacks"] == 1)
    demand("budget/real_clause", capped.has_clause() and capped.add_clause() == [-1, -2])
    censored = {"status": "censored", "models": [0], "learned": []}
    result = engine.adapter.verify_transcript(5, 2, 0, [], [], censored)
    demand("censored/closed_cover", result["cover_complete"] and not result["projected_model_set_complete"])
    mutations = check.mutation_controls()
    for name, result in mutations.items():
        demand("mutation/" + name, result["rejected"])
    print(json.dumps({"assertions": assertions, "transcripts": transcripts, "worker_records": worker_records,
                     "environment": engine.environment()},
                     sort_keys=True), flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--child", action="store_true")
    args = parser.parse_args()
    if args.child:
        return suite()
    if not args.receipt:
        parser.error("--receipt required")
    prior = json.loads(args.receipt.read_text()) if args.receipt.exists() else {
        "schema": "prime-prefix-search-software-integrity/v1", "attempts": [], "scientific_runs": 0}
    if len(prior["attempts"]) >= 4:
        raise ValueError("four software invocations already used")
    paths = [HERE / name for name in ("engine.py", "driver.py", "check.py", "test_engine.py", "README.md")]
    frozen = json.loads((ROOT / "coordination/prime_sat_prefix_search_20261030/source-inputs.json").read_text())["sources_sha256"]
    for name, digest in frozen.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest:
            raise ValueError("frozen source mismatch before suite: " + name)
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), "--child"]
    attempt = {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "argv": argv,
               "parent_argv": [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:]],
               "reason": "Initial native solver controls" if not prior["attempts"] else
                         "Validate durable subprocess path and strengthened offline/censor accounting on the same fixed controls",
               "sources": {str(p.relative_to(ROOT)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                                       "text": p.read_text()} for p in paths},
               "frozen_sources": frozen}
    try:
        completed = subprocess.run(argv, text=True, capture_output=True, timeout=60,
                                   env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        attempt.update(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
        attempt.update(returncode=None, timeout=True, stdout=text(error.stdout), stderr=text(error.stderr))
    attempt["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    attempt["frozen_sources_unchanged"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h
                                             for p, h in frozen.items())
    attempt["local_sources_unchanged"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == data["sha256"]
                                            for p, data in attempt["sources"].items())
    prior["attempts"].append(attempt)
    prior["valid"] = attempt["returncode"] == 0 and attempt["frozen_sources_unchanged"] and attempt["local_sources_unchanged"]
    from driver import write
    write(args.receipt, prior)
    print(json.dumps({"attempt": len(prior["attempts"]), "returncode": attempt["returncode"],
                      "valid": prior["valid"], "receipt": str(args.receipt)}))
    print(attempt["stdout"][-1500:])
    print(attempt["stderr"])
    return 0 if prior["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
