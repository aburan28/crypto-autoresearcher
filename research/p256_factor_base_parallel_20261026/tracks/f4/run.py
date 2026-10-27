"""F4 frozen second-pass panel. Import and --help execute no panel."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STUDY = HERE.parents[1]
OLD = REPO / "research/p256_factor_base_parallel_20261025"
TASK = "TASK-20261026-b71abe"
ARMS = [("natural", "candidate"), ("natural-order-aa", "control_aa"),
        ("positive", "control_positive"), ("negative", "control_negative")]
METRICS = ["cases_recorded", "fully_rational", "eligible_rows", "outside_rank",
           "kernel_dimension", "cancelled_rank", "controls_passed", "controls_total",
           "sparse_reductions", "witness_dag_nodes", "expanded_witness_terms",
           "max_pivot_nonzeros", "mismatches"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if len(payload.encode()) > 60000:
        payload = json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n"
    if len(payload.encode()) > 60000:
        raise ValueError("Split the certificate before the 60KB publication guard: " + str(path))
    with path.open("x") as handle:
        handle.write(payload)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def now():
    return datetime.now(timezone.utc).isoformat()


def source_observation(protocol):
    commits = {arm["instrument"]["commit"] for arm in protocol["arms"]}
    if len(commits) != 1 or None in commits:
        raise ValueError("Root must pin the implementation commit before execution")
    pinned = next(iter(commits))
    paths = [HERE/name for name in ["run.py", "sparse.py", "independent.py",
                                     "analysis.py", "export.py"]]
    paths += [OLD/"tracks/f4/divisor.py", OLD/"baseline/parameters.py",
              OLD/"tracks/f4/receipts/check-04/coefficient_m4.json",
              STUDY/"runtime/checkpoint_gate.py"]
    source_hashes = {}
    for path in paths:
        rel = str(path.relative_to(REPO))
        committed = subprocess.check_output(["git", "show", pinned+":"+rel], cwd=REPO)
        actual = path.read_bytes()
        if actual != committed:
            raise ValueError("Selected source/input differs from pinned commit: " + rel)
        source_hashes[rel] = hashlib.sha256(actual).hexdigest()
    analysis_sha = protocol["analysis_plan"]["script"]["sha256"]
    if analysis_sha != digest(HERE/"analysis.py"):
        raise ValueError("Frozen analysis hash mismatch")
    binary = Path(sys.executable).resolve()
    interpreter_sha = digest(binary)
    if any(a["instrument"]["binary_sha256"] != interpreter_sha for a in protocol["arms"]):
        raise ValueError("Actual Python executable differs from the frozen instrument")
    return {"verified_implementation_commit": pinned,
            "runtime_head": subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                       cwd=REPO, text=True).strip(),
            "runtime_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"],
                                                            cwd=REPO, text=True)),
            "selected_source_matches_pinned_commit": True,
            "source_sha256": source_hashes,
            "interpreter": str(binary), "interpreter_sha256": interpreter_sha,
            "entrypoint_sha256": digest(HERE/"run.py")}


def slope(seed, anchor, sample, p):
    rejected = []
    for retry in range(1024):
        message = f"P256-F4-pass2-slope-v1|{seed}|{anchor}|{sample}|{retry}".encode()
        hashed = hashlib.sha256(message).hexdigest()
        value = int(hashed, 16)
        if value < p:
            return value, {"hash": hashed, "hash_rejections": rejected,
                           "retry": retry, "domain": "P256-F4-pass2-slope-v1"}
        rejected.append({"hash": hashed, "integer": value})
    raise RuntimeError("Hash rejection guard exhausted; no replacement seed")


def store_graph(directory, label, certificate, checked, case_ids):
    target = directory/"graphs"/label
    target.mkdir(parents=True, exist_ok=False)
    dag = certificate.pop("dag")
    witnesses = certificate.pop("witnesses")
    outputs = certificate.pop("cancelled_rows")
    quotients = certificate.pop("outside_integer_lift_quotients")
    parts = []
    for start in range(0, len(dag), 128):
        path = target/f"dag-{start//128:03d}.json"
        write_json(path, {"first_node": start, "nodes": dag[start:start+128]})
        parts.append({"path": path.name, "sha256": digest(path), "nodes": len(dag[start:start+128])})
    witness_paths = []
    for index, (witness, output, quotient) in enumerate(zip(witnesses, outputs, quotients)):
        path = target/f"witness-{index:03d}.json"
        write_json(path, {"coefficients_mod_r": witness, "base_row": output,
                          "outside_integer_lift_quotients": quotient})
        witness_paths.append({"path": path.name, "sha256": digest(path)})
    certificate.update(dag_parts=parts, witness_files=witness_paths,
                       case_ids=case_ids, independent=checked)
    write_json(target/"certificate.json", certificate)
    # Restore runtime objects; only their serialized custody is sharded.
    certificate.update(dag=dag, witnesses=witnesses, cancelled_rows=outputs,
                       outside_integer_lift_quotients=quotients)


def graph(dp, independent, sparse, directory, label, cases, base, points,
          expected_kernel=None, expected_rank=None, matrix_only=False):
    rows = [case["row"] for case in cases]
    certificate = sparse.reduce_rows(rows, base, dp.r)
    checked = independent.check_graph(rows, base, certificate, dp.r,
                                     None if matrix_only else points,
                                     None if matrix_only else (dp.p, dp.a, dp.r))
    if expected_kernel is not None:
        assert checked["kernel_dimension"] == expected_kernel
    if expected_rank is not None:
        assert checked["cancelled_rank"] == expected_rank
    store_graph(directory, label, certificate, checked, [case["id"] for case in cases])
    return certificate, checked


def metrics():
    return {key: 0 for key in METRICS}


def apply_graph_metrics(values, certificate, checked):
    for key in ["outside_rank", "kernel_dimension", "cancelled_rank"]:
        values[key] += checked[key]
    for source, target in [("reductions", "sparse_reductions"),
                           ("dag_nodes", "witness_dag_nodes"),
                           ("expanded_witness_terms", "expanded_witness_terms")]:
        values[target] += certificate["stats"][source]
    values["max_pivot_nonzeros"] = max(values["max_pivot_nonzeros"],
                                         certificate["stats"]["max_pivot_nonzeros"])


def execute(out, seed, protocol, observation, gate):
    dp = load(OLD/"tracks/f4/divisor.py", "f4_first_pass_read_only")
    independent = load(HERE/"independent.py", "f4_separate_consumer")
    sparse = load(HERE/"sparse.py", "f4_streaming_reducer")
    points, point_cache = {}, {}
    calls = {"public_scalar_multiplication_calls": 0, "producer_factorization_calls": 0,
             "independent_divisor_checks": 0}

    def point(k):
        if k not in point_cache:
            calls["public_scalar_multiplication_calls"] += 1
            point_cache[k] = dp.mul(k)
        P = point_cache[k]
        points[str(P[0])] = (P[0], min(P[1], dp.p-P[1]))
        return P

    base = {str(point(k)[0]) for k in range(1, 17)}
    write_json(out/"curve-and-base.json", {"p": dp.p, "a": dp.a, "b": dp.b,
              "r": dp.r, "h": 1, "G": dp.G,
              "base_inverse_orbits": sorted(base), "base_scalars": list(range(1, 17)),
              "anchor_scalars": list(range(1, 9)),
              "order_scope": "Published prime order and cofactor are assumptions, not new point-count certificates."})
    row_records, arm_details, completed = [], {}, {}
    counter_checkpoint = {key: 0 for key in calls}

    def consume(case):
        calls["independent_divisor_checks"] += 1
        return independent.check_divisor(case, dp.p, dp.a, dp.b, dp.r)

    def finish(arm, role, values, detail, start, before, started):
        usage = resource.getrusage(resource.RUSAGE_SELF)
        record = {"run_id": f"F4-{out.name}-{arm}", "arm": arm, "role": role,
                  "instance_id": "0", "seed": seed, "replicate": 0, "warmup": False,
                  "status": "failed" if values["mismatches"] else "succeeded",
                  "verification": "refuted" if values["mismatches"] else "verified",
                  "started_at": started, "finished_at": now(),
                  "wall_seconds": time.perf_counter()-start, "wall_valid": False,
                  "cpu_user_seconds": usage.ru_utime-before.ru_utime,
                  "cpu_sys_seconds": usage.ru_stime-before.ru_stime,
                  "max_rss_bytes": usage.ru_maxrss*1024,
                  "native_counters": {key: value-counter_checkpoint[key]
                                      for key, value in calls.items()},
                  "native_counters_cumulative": dict(calls), **values}
        counter_checkpoint.update(calls)
        row_records.append(record)
        arm_details[arm] = detail
        write_json(out/f"arm-{arm}.json", {"row": record, "details": detail})
        with (out/"rows.jsonl").open("a") as handle:
            handle.write(json.dumps(record, separators=(",", ":"))+"\n")

    natural, invalid = [], []
    start, before, started = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF), now()
    values = metrics()
    for anchor in range(1, 9):
        P = point(anchor)
        for index in range(16):
            case_id = f"anchor-{anchor:02d}-draw-{index:02d}"
            try:
                t, sample = slope(seed, anchor, index, dp.p)
                calls["producer_factorization_calls"] += 1
                case = dp.divisor(([-P[1]-t*P[0], t], [1]))
                case.update(id=case_id, declared_anchors=[list(P)], sample=sample,
                            anchor_scalar=anchor, draw=index, slope=t,
                            provenance="fixed hash-derived anchored section; no planted residual zeros")
                points.update(consume(case))
                assert case["pole_order"] == 3
                case["verification"] = "verified"
                values["fully_rational"] += case["fully_rational"]
                if case["fully_rational"]:
                    assert sum(key not in base for key in case["row"]) <= 2
                    natural.append(case)
                write_json(out/"natural"/(case_id+".json"), case)
            except Exception as error:
                failure = {"id": case_id, "anchor_scalar": anchor, "draw": index,
                           "verification": "error", "exception": repr(error),
                           "traceback": traceback.format_exc()}
                invalid.append(failure)
                write_json(out/"natural"/(case_id+".failure.json"), failure)
                values["mismatches"] += 1
            values["cases_recorded"] += 1
    values["eligible_rows"] = len(natural)
    try:
        certificate, checked = graph(dp, independent, sparse, out, "natural", natural, base, points)
        apply_graph_metrics(values, certificate, checked)
        completed["natural"] = checked
    except Exception as error:
        values["mismatches"] += 1
        write_json(out/"natural-graph.failure.json", {"exception": repr(error), "traceback": traceback.format_exc()})
    finish("natural", "candidate", values, {"unique_generated_functions": 128,
           "graph_case_ids": [c["id"] for c in natural], "failed_cases": invalid,
           "accounting": "Shared base construction is charged to this arm's scalar-call count. Arm clocks begin after that setup and are diagnostic, not complete cost metrics. Inner group/field operations are not priced."}, start, before, started)

    start, before, started = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF), now()
    values = metrics()
    values.update(cases_recorded=128, fully_rational=len(natural), eligible_rows=len(natural),
                  mismatches=len(invalid))
    try:
        certificate, checked = graph(dp, independent, sparse, out, "natural-reversed", list(reversed(natural)), base, points)
        apply_graph_metrics(values, certificate, checked)
        for key in ["outside_rank", "kernel_dimension", "cancelled_rank"]:
            assert checked[key] == completed["natural"][key]
    except Exception as error:
        values["mismatches"] += 1
        write_json(out/"aa.failure.json", {"exception": repr(error), "traceback": traceback.format_exc()})
    finish("natural-order-aa", "control_aa", values, {"unique_generated_functions": 0,
           "same_128_raw_cases": True, "nuisance": "reversed graph input order; no resampling"}, start, before, started)

    def actual_cases(label, pairs):
        cases = []
        for i, (left, right) in enumerate(pairs):
            P, Q = point(left), point(right)
            calls["producer_factorization_calls"] += 1
            case = dp.divisor(dp.line(P, Q))
            case.update(id=f"{label}-{i:02d}", declared_anchors=[list(P), list(Q)],
                        provenance="deliberately constructed split graph control",
                        input_scalars=[left, right])
            points.update(consume(case))
            assert case["fully_rational"]
            write_json(out/"controls"/label/(case["id"]+".json"), case)
            cases.append(case)
        return cases

    start, before, started = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF), now()
    values, positive_records, first_cycle = metrics(), [], None
    specifications = []
    for length in [4, 8, 16]:
        vertices = list(range(100, 100+length))
        pairs = [(vertices[i], -vertices[(i+1) % length]) for i in range(length)]
        specifications.append((f"balanced-{length}", pairs, set(base), False, 1, 1))
    triangle_a, triangle_b = [(100, 101), (101, 103), (103, 100)], [(1000, 1001), (1001, 1003), (1003, 1000)]
    paired_base = {str(point(i+j)[0]) for i, j in triangle_a+triangle_b}
    paired_base.add(str(point(900)[0]))
    specifications.append(("paired-unbalanced", triangle_a+triangle_b+[(100, -1000)], paired_base, False, 1, 1))
    abstract = [
        ("weighted-parallel", [{"u": 1, "v": 2, "b0": 1},
                               {"u": 3, "v": 4, "b1": 1},
                               {"u": 5, "v": 6, "b2": 1}], {"b0", "b1", "b2"}, 1, 1),
        ("weighted-unary", [{"u": 2, "b0": 1}, {"u": 3, "b1": 1}], {"b0", "b1"}, 1, 1),
        ("zero-outside", [{"b0": 1}], {"b0"}, 1, 1)]
    for label, pairs, control_base, matrix_only, kernel, final_rank in specifications:
        values["cases_recorded"] += 1
        values["controls_total"] += 1
        try:
            cases = actual_cases(label, pairs)
            certificate, checked = graph(dp, independent, sparse, out, label, cases, control_base, points,
                                         kernel, final_rank, matrix_only)
            if first_cycle is None:
                first_cycle = (cases, control_base, certificate)
            apply_graph_metrics(values, certificate, checked)
            values["eligible_rows"] += len(cases)
            values["fully_rational"] += len(cases)
            values["controls_passed"] += 1
            positive_records.append({"id": label, "matrix_only": False, **checked})
        except Exception as error:
            values["mismatches"] += 1
            write_json(out/"controls"/(label+".failure.json"), {"exception": repr(error), "traceback": traceback.format_exc()})
    for label, rows, control_base, kernel, final_rank in abstract:
        values["cases_recorded"] += 1
        values["controls_total"] += 1
        try:
            cases = [{"id": f"{label}-{i}", "row": row} for i, row in enumerate(rows)]
            write_json(out/"controls"/(label+".inputs.json"), {"cases": cases, "scope": "abstract linear-algebra control over the actual subgroup field; no curve divisor claim"})
            certificate, checked = graph(dp, independent, sparse, out, label, cases, control_base, points,
                                         kernel, final_rank, matrix_only=True)
            apply_graph_metrics(values, certificate, checked)
            values["eligible_rows"] += len(cases)
            values["controls_passed"] += 1
            positive_records.append({"id": label, "matrix_only": True, **checked})
        except Exception as error:
            values["mismatches"] += 1
            write_json(out/"controls"/(label+".failure.json"), {"exception": repr(error), "traceback": traceback.format_exc()})
    finish("positive", "control_positive", values, {"control_families": positive_records,
           "natural_sampling_claim": False}, start, before, started)

    start, before, started = time.perf_counter(), resource.getrusage(resource.RUSAGE_SELF), now()
    values, negative_records = metrics(), []

    def refusal(label, operation, payload):
        values["cases_recorded"] += 1
        values["controls_total"] += 1
        write_json(out/"corruptions"/(label+".json"), payload)
        try:
            operation()
        except (AssertionError, ValueError) as error:
            values["controls_passed"] += 1
            negative_records.append({"id": label, "rejected": True, "error": repr(error)})
        else:
            values["mismatches"] += 1
            negative_records.append({"id": label, "rejected": False})

    try:
        cases = actual_cases("lone-unbalanced", triangle_a)
        triangle_base = {str(point(i+j)[0]) for i, j in triangle_a}
        certificate, checked = graph(dp, independent, sparse, out, "lone-unbalanced", cases, triangle_base, points, 0, 0)
        apply_graph_metrics(values, certificate, checked)
        values["cases_recorded"] += 1
        values["controls_total"] += 1
        values["controls_passed"] += 1
        values["eligible_rows"] += len(cases)
        values["fully_rational"] += len(cases)
        negative_records.append({"id": "lone-unbalanced", "no_cancellation": True, **checked})
    except Exception as error:
        values["mismatches"] += 1
        write_json(out/"controls/lone-unbalanced.failure.json", {"exception": repr(error), "traceback": traceback.format_exc()})
    try:
        cases, control_base, original = first_cycle
        bad = json.loads(json.dumps(original))
        witness = {int(i): c for i, c in bad["witnesses"][0].items()}
        witness[0] = (witness.get(0, 0)+1) % dp.r
        bad["witnesses"][0] = witness
        refusal("wrong-cancellation", lambda: independent.check_graph(
            [case["row"] for case in cases], control_base, bad, dp.r, points, (dp.p, dp.a, dp.r)),
            {"coefficients_mod_r": witness, "input_cases": [case["id"] for case in cases]})
        bad_case = json.loads(json.dumps(cases[0]))
        key = next(iter(bad_case["row"]))
        bad_case["row"][key] *= -1
        refusal("flipped-signed-row", lambda: consume(bad_case), bad_case)
        old_case = json.loads((OLD/"tracks/f4/receipts/check-04/coefficient_m4.json").read_text())
        consume(old_case)
        bad_case = json.loads(json.dumps(old_case))
        bad_case["norm_factors"] = [q for q in bad_case["norm_factors"] if q["degree"] == 1]
        refusal("omitted-nonrational-factor", lambda: consume(bad_case), bad_case)
    except Exception as error:
        values["mismatches"] += 1
        write_json(out/"negative-prerequisite.failure.json", {"exception": repr(error), "traceback": traceback.format_exc()})
    finish("negative", "control_negative", values, {"controls": negative_records,
           "retained_old_nonsplit_input": "20261025/tracks/f4/receipts/check-04/coefficient_m4.json"}, start, before, started)
    write_json(out/"result.json", {"schema": "p256-f4-pass2-result/v1", "task": TASK,
               "status": "completed_with_failures" if any(r["mismatches"] for r in row_records) else "completed_exact_panel",
               "unique_natural_functions": 128, "natural_eligible": len(natural),
               "arm_rows": [{key: row[key] for key in ["arm", "status"]+METRICS} for row in row_records],
               "native_counters": calls, "source": observation,
               "scope": "Exact fixed-input arithmetic and finite conditional observations; no speed, general-yield or end-to-end ECDLP claim.",
               "scientific_state_transition": False, "model_verified": False})
    return row_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--protocol", type=Path, default=HERE/"protocol.json")
    parser.add_argument("--release", type=Path, default=HERE/"phase-b-release.json")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    if protocol["freeze"]["status"] != "frozen":
        raise SystemExit("Refusing an unfrozen protocol")
    if args.seed != protocol["extensions"]["panel_seed"]:
        raise SystemExit("Seed differs from the prospective panel")
    if args.out.exists():
        raise SystemExit("Fresh output directory required")
    observation = source_observation(protocol)
    helper = load(STUDY/"runtime/checkpoint_gate.py", "f4_canonical_checkpoint_gate")
    gate = helper.require_gate(REPO, args.release, protocol, TASK)
    args.out.mkdir(parents=True, exist_ok=False)
    write_json(args.out/"checkpoint-gate.json", gate)
    cpu_model = next((line.split(":", 1)[1].strip() for line in Path("/proc/cpuinfo").read_text().splitlines()
                      if line.startswith("model name")), None)
    memory = next((int(line.split()[1])*1024 for line in Path("/proc/meminfo").read_text().splitlines()
                   if line.startswith("MemTotal:")), None)
    environment = {"observed_utc": now(), "source": observation,
                   "python": sys.version, "host": platform.node(),
                   "cpu_model": cpu_model, "logical_cpus": os.cpu_count(),
                   "memory_bytes": memory, "kernel": platform.release(),
                   "hypervisor": None, "isolation_tier_max": "L0",
                   "isolation_blockers": ["shared virtual host; clocks diagnostic only"],
                   "threads": 1, "command": [sys.executable]+sys.argv,
                   "protocol_sha256": protocol["freeze"]["protocol_sha256"]}
    write_json(args.out/"environment.json", environment)
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    try:
        rows = execute(args.out, args.seed, protocol, observation, gate)
        analysis = load(HERE/"analysis.py", "f4_frozen_analysis")
        analysis.analyze(args.out, args.out/"analysis")
        exporter = load(HERE/"export.py", "f4_frozen_exporter")
        exporter.export_run(args.out, args.protocol, args.out/"export.json")
    except BaseException as error:
        write_json(args.out/"process.failure.json", {"exception": repr(error), "traceback": traceback.format_exc(),
                   "status": "not_completed", "mathematical_empty_set": False})
        raise
    print(json.dumps({"out": str(args.out), "arm_rows": len(rows),
                      "failed_arms": sum(row["status"] != "succeeded" for row in rows)}))
    return int(any(row["status"] != "succeeded" for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
