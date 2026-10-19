"""Frozen bounded engineering controls for TASK-20261017-68782f.

Invoke once with the direct pinned Sage binary, under the task-specific SSD
DOT_SAGE and TMPDIR. This script parses archived public systems but never
passes them to ``backend.solve_request``.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import pathlib
import platform
import random
import resource
import shutil
import subprocess
import sys
import time
import traceback


def _supervise() -> int:
    """One Sage child; conservative live guard below frozen 8 GiB ceilings."""
    import psutil

    own_dir = pathlib.Path(__file__).resolve().parent
    own_repo = own_dir.parent.parent
    scratch = pathlib.Path("/Volumes/SSD990-2/crypto/.scratch/icperf_prime_wide_backend_TASK-20261017-68782f")
    sage = "/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage"
    command = [sage, "-python", str(pathlib.Path(__file__).resolve()), "--controls"]
    stdout_path = own_dir / "test-stdout.log"
    stderr_path = own_dir / "test-stderr.log"
    validation_path = own_dir / "validation.json"
    vectors_path = own_dir / "vectors.json"
    prior_validation = json.loads(validation_path.read_text()) if validation_path.exists() else None
    prior_vectors = json.loads(vectors_path.read_text()) if vectors_path.exists() else None
    try:
        # psutil.children uses a host process-list query on macOS. Check it
        # before launching Sage so a sandbox denial cannot strand a child.
        psutil.Process(os.getpid()).children(recursive=True)
    except (psutil.Error, PermissionError) as exc:
        failure = {"schema":"icperf-prime-wide-backend-validation-v1",
                   "task_id":"TASK-20261017-68782f", "overall":"censored",
                   "classification":"infrastructure_error", "controls":{},
                   "full_width_systems_solved":0,"natural_systems_solved":0,
                   "anomaly":{"stage":"initial_process_visibility", "type":type(exc).__name__,
                              "detail":str(exc)}}
        (own_dir / "validation.json").write_text(json.dumps(failure,indent=2,sort_keys=True)+"\n")
        return 75
    started = time.monotonic()
    peak_rss = 0
    minimum_free = shutil.disk_usage(scratch).free
    maximum_scratch = 0
    stop_reason = None
    last_disk_check = 0.0
    attempt = 2 + stdout_path.read_bytes().count(b"=== attempt") if stdout_path.exists() else 2
    if attempt > 6:
        raise RuntimeError("bounded supervisor retry count exhausted")
    def scratch_bytes() -> int:
        total = 0
        for entry in scratch.rglob("*"):
            try:
                if entry.is_file():
                    total += entry.stat().st_size
            except FileNotFoundError:
                # Sage can remove a temp file between enumeration and stat.
                continue
        return total

    with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
        marker = f"\n=== attempt {attempt}: supervised Sage controls ===\n".encode()
        stdout.write(marker)
        stderr.write(marker)
        stdout.flush(); stderr.flush()
        child = subprocess.Popen(command, cwd=own_repo, env=os.environ.copy(),
                                 stdout=stdout, stderr=stderr)
        try:
            process = psutil.Process(child.pid)
        except (psutil.Error, PermissionError) as exc:
            child.terminate()
            child.wait(timeout=15)
            stop_reason = f"process_setup_unavailable:{type(exc).__name__}"
            process = None
        while process is not None and child.poll() is None:
            now = time.monotonic()
            try:
                family = [process] + process.children(recursive=True)
                rss = 0
                for member in family:
                    try:
                        state = member.status()
                        if state == psutil.STATUS_ZOMBIE:
                            if member.pid == child.pid and child.poll() is None:
                                raise RuntimeError("unreaped Sage root is zombie but poll is pending")
                            continue
                        rss += member.memory_info().rss
                    except (psutil.ZombieProcess, psutil.NoSuchProcess):
                        # Confirm the disappearing member has ceased to run.
                        # An unobservable live Sage root is a fail-closed stop.
                        if member.pid == child.pid and child.poll() is None:
                            raise
                        continue
                if child.poll() is not None:
                    break
                peak_rss = max(peak_rss, rss)
                if rss >= 6 * 2**30:
                    stop_reason = "rss_guard_at_6_gib_before_8_gib_ceiling"
            except (psutil.Error, PermissionError, RuntimeError) as exc:
                if child.poll() is not None:
                    break
                stop_reason = f"rss_monitor_unavailable:{type(exc).__name__}"
            if now - last_disk_check >= 1.0:
                try:
                    free = shutil.disk_usage(scratch).free
                    used = scratch_bytes()
                    minimum_free = min(minimum_free, free)
                    maximum_scratch = max(maximum_scratch, used)
                    if free < 8 * 2**30 or used > 8 * 2**30:
                        stop_reason = "disk_guard_8_gib"
                except Exception as exc:
                    stop_reason = f"disk_monitor_unavailable:{type(exc).__name__}:{exc}"
                last_disk_check = now
            if now - started >= 14400:
                stop_reason = "four_hour_watchdog"
            if stop_reason:
                try:
                    family = [process] + process.children(recursive=True)
                except (psutil.Error, PermissionError):
                    family = [process]
                for member in reversed(family):
                    try:
                        member.terminate()
                    except psutil.Error:
                        pass
                try:
                    child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    try:
                        family = [process] + process.children(recursive=True)
                    except (psutil.Error, PermissionError):
                        family = [process]
                    for member in reversed(family):
                        try:
                            member.kill()
                        except psutil.Error:
                            pass
                    child.wait()
                break
            time.sleep(0.05)
        exit_code = child.wait()
    supervisor = {"attempt":attempt, "initial_visibility_checked":True,
                  "rss_poll_seconds": 0.05, "disk_poll_seconds": 1.0,
                  "rss_termination_threshold_bytes": 6 * 2**30,
                  "frozen_rss_ceiling_bytes": 8 * 2**30,
                  "frozen_scratch_ceiling_bytes": 8 * 2**30,
                  "frozen_continuing_free_floor_bytes": 8 * 2**30,
                  "peak_observed_process_tree_rss_bytes": peak_rss,
                  "minimum_observed_free_bytes": minimum_free,
                  "maximum_observed_scratch_bytes": maximum_scratch,
                  "elapsed_seconds": time.monotonic()-started,
                  "stop_reason": stop_reason, "child_exit_code": exit_code,
                  "first_attempt_before_controls": "ulimit -v refused with invalid argument; raw stderr retained at start of test-stderr.log"}
    if validation_path.exists():
        validation = json.loads(validation_path.read_text())
    else:
        validation = {"schema":"icperf-prime-wide-backend-validation-v1",
                      "task_id":"TASK-20261017-68782f", "overall":"incomplete",
                      "controls":{}, "full_width_systems_solved":0,"natural_systems_solved":0}
    validation["supervisor"] = supervisor
    validation["precontrol_attempts"] = [{"attempt":1,"stage":"resource_limit_setup",
                                          "status":"infrastructure_error",
                                          "stderr":"research/icperf_prime_wide_backend_retry_20261017/command.txt:ulimit:6: setrlimit failed: invalid argument",
                                          "controls_attempted":0},
                                         {"attempt":2,"stage":"supervisor_setup",
                                          "status":"infrastructure_error",
                                          "stderr":"PermissionError: [Errno 1] Operation not permitted (originated from sysctl() malloc 1/3)",
                                          "control_output_observed":0},
                                         {"attempt":3,"stage":"supervisor_runtime",
                                          "status":"infrastructure_error",
                                          "detail":"psutil saw a Sage launcher zombie during the process-list race; the supervisor terminated and reaped it",
                                          "control_output_observed":0}]
    if prior_validation and prior_validation.get("supervisor",{}).get("attempt"):
        past = list(prior_validation.get("prior_attempts", []))
        older = dict(prior_validation)
        older.pop("prior_attempts", None)
        past.append({"attempt":prior_validation["supervisor"]["attempt"],
                     "classification":"implementation_error" if prior_validation.get("anomaly",{}).get("class")=="ValueError" else prior_validation.get("classification"),
                     "validation":older})
        validation["prior_attempts"] = past
        if prior_vectors is not None and vectors_path.exists():
            current_vectors = json.loads(vectors_path.read_text())
            old_vectors = dict(prior_vectors)
            old_vectors.pop("prior_attempts", None)
            current_vectors["prior_attempts"] = list(prior_vectors.get("prior_attempts", [])) + [
                {"attempt":prior_validation["supervisor"]["attempt"], "vectors":old_vectors}]
            vectors_path.write_text(json.dumps(current_vectors,indent=2,sort_keys=True)+"\n")
    if stop_reason:
        validation["overall"] = "censored"
        validation["classification"] = ("resource_exhaustion" if stop_reason.startswith(("rss_guard", "disk_guard", "four_hour"))
                                        else "infrastructure_error")
    validation_path.write_text(json.dumps(validation,indent=2,sort_keys=True)+"\n")
    environment_path = own_dir / "environment.json"
    if environment_path.exists():
        environment = json.loads(environment_path.read_text())
        environment["supervisor"] = supervisor
        environment_path.write_text(json.dumps(environment,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"supervisor":supervisor,"overall":validation["overall"]},sort_keys=True),flush=True)
    return 75 if stop_reason else exit_code


if __name__ == "__main__" and "--supervise" in sys.argv:
    sys.exit(_supervise())

from sage.all import EllipticCurve, GF, PolynomialRing

import backend
import independent_check as check


ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent.parent
SCRATCH = pathlib.Path("/Volumes/SSD990-2/crypto/.scratch/icperf_prime_wide_backend_TASK-20261017-68782f")
DOT_SAGE = SCRATCH / "sage"
TMPDIR = SCRATCH / "tmp"
SAGE_EXE = pathlib.Path("/Volumes/SSD990/cryptanalysis/third_party/sage-binary/sage")
P63 = 9223372021248595841
EXPECTED_SAGE_SHA = "b190e6cec5027031be752260d9b21a8e23f11a313cc620e5dcd1be28390643c1"
INPUTS = [
    "research/icperf_prime_475_target_systems_20261017/systems.json.gz",
    "research/icperf_prime_475_target_systems_20261017/sage_replay.json",
    "research/icperf_prime_475_controls_20261017/controls.json",
    "research/icperf_prime_coset_896_20261017/scan.json",
    "research/icperf_prime_fixtures_20261017/n63_seed20261017.json",
    "src/crypto_autoresearcher/index_calculus/msolve.py",
    "tests/test_index_calculus_fp.py",
    "ledger/proposals/IDEA-20261017-9cf4b9.yaml",
    "ledger/decisions/DEC-20261017-40cd49.yaml",
]


def digest(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, data) -> None:
    (ROOT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _bytes_under(path: pathlib.Path) -> int:
    return sum(entry.stat().st_size for entry in path.rglob("*") if entry.is_file())


def _rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value if platform.system() == "Darwin" else value * 1024


def resource_check(stage: str, samples: list[dict]) -> None:
    free = shutil.disk_usage(SCRATCH).free
    used = _bytes_under(SCRATCH)
    rss = _rss_bytes()
    row = {"stage": stage, "free_bytes": free, "scratch_bytes": used,
           "peak_rss_bytes": rss, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    samples.append(row)
    print(json.dumps({"resource": row}, sort_keys=True), flush=True)
    if free < 8 * 2**30 or used > 8 * 2**30 or rss > 8 * 2**30:
        raise RuntimeError(f"resource_limit_at_{stage}")


def precheck() -> tuple[dict, dict]:
    if pathlib.Path(os.environ.get("DOT_SAGE", "")).resolve() != DOT_SAGE:
        raise RuntimeError("DOT_SAGE mismatch")
    if pathlib.Path(os.environ.get("TMPDIR", "")).resolve() != TMPDIR:
        raise RuntimeError("TMPDIR mismatch")
    resolved_root = SCRATCH.resolve()
    for path in (SCRATCH, DOT_SAGE, TMPDIR):
        if not path.is_dir() or path.stat().st_mode & 0o777 != 0o700:
            raise RuntimeError(f"scratch path missing or mode mismatch: {path}")
    for path in (DOT_SAGE, TMPDIR):
        if not str(path.resolve()).startswith(str(resolved_root) + os.sep):
            raise RuntimeError("scratch path escapes task root")
        probe = path / ".engineering-probe"
        probe.write_bytes(b"prime63-exact\n")
        if probe.read_bytes() != b"prime63-exact\n":
            raise RuntimeError("scratch probe read mismatch")
        probe.unlink()
    if DOT_SAGE.stat().st_dev != TMPDIR.stat().st_dev:
        raise RuntimeError("DOT_SAGE and TMPDIR on different devices")
    free = shutil.disk_usage(SCRATCH).free
    if free < 16 * 2**30:
        raise RuntimeError("less than 16 GiB free before controls")
    sage_sha = digest(SAGE_EXE)
    if sage_sha != EXPECTED_SAGE_SHA:
        raise RuntimeError("Sage executable digest mismatch")
    input_shas = {path: digest(REPO / path) for path in INPUTS}
    manifest = {"schema": "icperf-prime-wide-backend-inputs-v1",
                "task_id": "TASK-20261017-68782f",
                "inputs_sha256": input_shas,
                "backend_sha256": digest(ROOT / "backend.py"),
                "independent_check_sha256": digest(ROOT / "independent_check.py"),
                "test_source_sha256": digest(ROOT / "test_backend.py"),
                "sage_executable_sha256": sage_sha}
    version = subprocess.check_output([str(SAGE_EXE), "--version"], text=True).strip()
    environment = {"schema": "icperf-prime-wide-backend-environment-v1",
                   "task_id": "TASK-20261017-68782f",
                   "command": "zsh -f research/icperf_prime_wide_backend_retry_20261017/command.txt",
                   "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
                   "git_status_at_start": subprocess.check_output(["git", "status", "--short"], cwd=REPO, text=True),
                   "python_version": platform.python_version(), "platform": platform.platform(),
                   "sage_version": version, "sage_executable": str(SAGE_EXE),
                   "sage_executable_sha256": sage_sha, "dot_sage": str(DOT_SAGE),
                   "tmpdir": str(TMPDIR), "scratch_root": str(SCRATCH),
                   "scratch_directory_mode": "0700", "free_bytes_before_controls": free,
                   "published_claim": "coordination/goals/GOAL-ICPERF-e6b6a4/batches/BATCH-25c5e3/claims/TASK-20261017-68782f.1.claim.json",
                   "published_claim_seen_on_ref": True,
                   "process_limit": "8 GiB virtual address and post-control RSS checks",
                   "scratch_limit_bytes": 8 * 2**30,
                   "continuing_free_floor_bytes": 8 * 2**30,
                   "watchdog_seconds": 14400}
    return manifest, environment


def terms(poly) -> list[dict]:
    return [{"coefficient": str(int(c)),
             "powers": [[i, int(e)] for i, e in enumerate(exps) if e]}
            for exps, c in poly.dict().items() if c]


def synthetic_ideals() -> list[tuple[str, dict, str, list[tuple[int, int]]]]:
    p = P63
    one = {"p": str(p), "variables": ["x", "y"], "equations": [
        [{"coefficient": "1", "powers": [[0, 1]]}, {"coefficient": str(p-11), "powers": []}],
        [{"coefficient": "1", "powers": [[1, 1]]}, {"coefficient": str(p-13), "powers": []}]]}
    two = {"p": str(p), "variables": ["x", "y"], "equations": [
        [{"coefficient": "1", "powers": [[0, 2]]}, {"coefficient": str(p-3), "powers": [[0, 1]]},
         {"coefficient": "2", "powers": []}],
        [{"coefficient": "1", "powers": [[1, 1]]}, {"coefficient": str(p-7), "powers": []}]]}
    inconsistent = {"p": str(p), "variables": ["x", "y"], "equations": [
        [{"coefficient": "1", "powers": [[0, 1]]}, {"coefficient": str(p-1), "powers": []}],
        [{"coefficient": "1", "powers": [[0, 1]]}, {"coefficient": str(p-2), "powers": []}]]}
    positive = {"p": str(p), "variables": ["x", "y"], "equations": [
        [{"coefficient": "1", "powers": [[0, 1]]}, {"coefficient": str(p-1), "powers": []}]]}
    return [("one_root", one, "ok", [(11, 13)]),
            ("two_roots", two, "ok", [(1, 7), (2, 7)]),
            ("inconsistent", inconsistent, "certified_no_solution", []),
            ("positive_dimensional", positive, "unsupported", [])]


def regression_m2() -> dict:
    p, a, b = 1019, 2, 3
    E = check.curve(p, a, b)
    base = []
    for x in range(p):
        candidates = check.lift_points(E, x)
        if candidates:
            base.append(candidates[0])
        if len(base) == 8:
            break
    target = base[0] + base[1]
    if target.is_zero():
        raise AssertionError("regression target at infinity")
    xR = int(target[0])
    k = GF(p)
    ring = PolynomialRing(k, names=("x1", "x2"))
    x1, x2 = ring.gens()
    member1 = ring.one()
    member2 = ring.one()
    for point in base:
        member1 *= x1 - int(point[0])
        member2 *= x2 - int(point[0])
    s3 = (x1-x2)**2*xR**2 - 2*((x1+x2)*(x1*x2+a)+2*b)*xR + (x1*x2-a)**2 - 4*b*(x1+x2)
    request = {"p": str(p), "variables": ["x1", "x2"],
               "equations": [terms(member1), terms(member2), terms(s3)]}
    result = backend.solve_request(request)
    got = sorted(tuple(int(root["variables"][name]) for name in ("x1", "x2"))
                 for root in result.get("roots", []))
    xs = [int(point[0]) for point in base]
    expected = sorted((u, v) for u, v in itertools.product(xs, repeat=2)
                      if xR in check.geometric_s3_roots(E, u, v))
    target_xy = (int(target[0]), int(target[1]))
    lifts = [check.verify_signed_sum(E, list(pair), target_xy, allowed_x=set(xs))
             for pair in got]
    passed = result["status"] == "ok" and got == expected and all(row["accepted"] for row in lifts)
    return {"status": "pass" if passed else "failed", "p": str(p), "a": a, "b": b,
            "base_x": xs, "target": list(target_xy), "expected_roots": expected,
            "backend_roots": got, "signed_checks": lifts, "backend_result": result}


def run() -> int:
    started = time.monotonic()
    samples = []
    controls = {}
    vectors = {"schema": "icperf-prime-wide-backend-vectors-v1", "seed": 20261017,
               "field_identities": [], "s3_valid": [], "s3_altered": [],
               "synthetic_ideals": [], "m2_regression": None, "signed_rejections": []}
    validation = {"schema": "icperf-prime-wide-backend-validation-v1",
                  "task_id": "TASK-20261017-68782f", "overall": "incomplete",
                  "controls": controls, "resource_samples": samples,
                  "full_width_systems_solved": 0, "natural_systems_solved": 0,
                  "classification": "engineering_controls_only"}
    try:
        manifest, environment = precheck()
        write_json("input_manifest.json", manifest)
        write_json("environment.json", environment)
        resource_check("pre_controls", samples)
        archive = backend.parse_archive(REPO / INPUTS[0])
        controls["archive_parse_21"] = {"status": "pass" if archive["systems_parsed"] == 21 else "failed",
                                        "systems_parsed": archive["systems_parsed"],
                                        "systems_solved": archive["systems_solved"]}
        vectors["archive_parse"] = archive
        print(json.dumps({"control": "archive_parse_21", "result": controls["archive_parse_21"]}, sort_keys=True), flush=True)
        resource_check("archive_parse_21", samples)

        curve_data = backend.load_json(REPO / INPUTS[4])["curve"]
        p, a, b = (int(curve_data[key]) for key in ("p", "a", "b"))
        assert p == P63
        E = check.curve(p, a, b)
        witness = backend.load_json(REPO / INPUTS[4])["witness"]
        P = E([int(witness[0]), int(witness[1])])
        assert not P.is_zero()
        rng = random.Random(20261017)
        K = GF(p)
        for i in range(64):
            x, y, z = (rng.randrange(1, p) for _ in range(3))
            observed = [int(K(x)+K(y)), int(K(x)*K(y)), int(K(x)/K(y)), int(K(x)**5),
                        int((K(x)+K(y))*K(z))]
            expected = [(x+y)%p, (x*y)%p, x*pow(y,-1,p)%p, pow(x,5,p), (x+y)*z%p]
            vectors["field_identities"].append({"index": i, "inputs": [str(x),str(y),str(z)],
                                                 "observed": [str(q) for q in observed],
                                                 "expected": [str(q) for q in expected],
                                                 "pass": observed == expected})
        field_pass = sum(row["pass"] for row in vectors["field_identities"])
        controls["field_identities_64"] = {"status": "pass" if field_pass == 64 else "failed",
                                           "passed": field_pass, "count": 64}
        print(json.dumps({"control": "field_identities_64", "result": controls["field_identities_64"]}, sort_keys=True), flush=True)
        resource_check("field_identities_64", samples)

        for i in range(16):
            s, t = rng.randrange(1, 2**20), rng.randrange(1, 2**20)
            Q, R = int(s)*P, int(t)*P
            U = Q + R
            if U.is_zero() or int(Q[1]) == 0:
                raise AssertionError("degenerate fixed-seed S3 control")
            x1, x2, x3 = int(Q[0]), int(R[0]), int(U[0])
            observed = backend.s3_value(p,a,b,x1,x2,x3)
            geometric = x3 in check.geometric_s3_roots(E,x1,x2)
            signed = check.verify_signed_sum(E,[x1,x2],(x3,int(U[1])),
                                             required_y=[int(Q[1]),int(R[1])])
            good = observed == 0 and geometric and signed["accepted"]
            vectors["s3_valid"].append({"index":i,"scalars":[s,t],
                                        "xs":[str(x1),str(x2),str(x3)],
                                        "ys":[str(int(Q[1])),str(int(R[1])),str(int(U[1]))],
                                        "s3":str(observed),"geometric":geometric,
                                        "signed":signed,"pass":good})
            changed = (x3+1) % p
            while changed in check.geometric_s3_roots(E,x1,x2):
                changed = (changed+1) % p
            bad_value = backend.s3_value(p,a,b,x1,x2,changed)
            bad_geom = changed in check.geometric_s3_roots(E,x1,x2)
            vectors["s3_altered"].append({"index":i,"xs":[str(x1),str(x2),str(changed)],
                                          "s3":str(bad_value),"geometric":bad_geom,
                                          "pass":bad_value != 0 and not bad_geom})
            if i == 0:
                wrong = check.verify_signed_sum(E,[x1,x2],(x3,int(U[1])),
                                                required_y=[(-int(Q[1]))%p,int(R[1])])
                vectors["signed_rejections"].append({"kind":"wrong_sign","result":wrong,
                                                       "pass":not wrong["accepted"]})
                changed_root = check.verify_signed_sum(E,[x1,(x2+1)%p],(x3,int(U[1])),
                                                       allowed_x={x1,x2})
                vectors["signed_rejections"].append({"kind":"altered_root","result":changed_root,
                                                       "pass":not changed_root["accepted"]})
                changed_target = check.verify_signed_sum(E,[x1,x2],(x3,(-int(U[1]))%p),
                                                         required_y=[int(Q[1]),int(R[1])])
                vectors["signed_rejections"].append({"kind":"target_mismatch","result":changed_target,
                                                       "pass":not changed_target["accepted"]})
        for name, key in (("s3_valid_16","s3_valid"),("s3_altered_16","s3_altered")):
            passed = sum(row["pass"] for row in vectors[key])
            controls[name] = {"status":"pass" if passed == 16 else "failed", "passed":passed,"count":16}
            print(json.dumps({"control":name,"result":controls[name]},sort_keys=True),flush=True)
            resource_check(name,samples)

        scan = backend.load_scan_metadata(REPO / INPUTS[3])
        assert int(scan["curve"]["p"]) == p
        selected = next(row for row in scan["attempts"] if row["base_parameters"]["seed"] == scan["selected_seed"])
        parameters = selected["base_parameters"]
        d, g, zeta = (backend.exact_int(parameters[key], key) for key in ("d","coset","zeta"))
        coset_value = pow(g,d,p)
        nonlifting = next(x for j in range(d) if not check.lift_points(E,(x:=g*pow(zeta,j,p)%p)))
        rejection = check.verify_signed_sum(E,[nonlifting],(int(P[0]),int(P[1])),
                                            coset=(d,coset_value))
        vectors["signed_rejections"].append({"kind":"nonlifting_coset_root",
                                               "x":str(nonlifting),"coset_check":pow(nonlifting,d,p)==coset_value,
                                               "result":rejection,
                                               "pass":pow(nonlifting,d,p)==coset_value and rejection["reason"]=="nonlifting_x"})
        rejects_ok = all(row["pass"] for row in vectors["signed_rejections"])
        controls["signed_rejections_4"] = {"status":"pass" if rejects_ok else "failed",
                                            "passed":sum(row["pass"] for row in vectors["signed_rejections"]),"count":4}
        print(json.dumps({"control":"signed_rejections_4","result":controls["signed_rejections_4"]},sort_keys=True),flush=True)
        resource_check("signed_rejections_4",samples)

        for label, request, expected_status, expected_roots in synthetic_ideals():
            result = backend.solve_request(request)
            roots = sorted(tuple(int(row["variables"][name]) for name in ("x","y"))
                           for row in result.get("roots",[]))
            passed = result["status"] == expected_status and roots == expected_roots
            if label == "positive_dimensional":
                passed &= result.get("reason") == "positive_dimension" and result.get("dimension",0)>0
            if label == "inconsistent":
                passed &= result.get("certificate") == "Groebner basis contains 1"
            row = {"label":label,"request":request,"result":result,"roots":roots,
                   "expected_status":expected_status,"expected_roots":expected_roots,"pass":passed}
            vectors["synthetic_ideals"].append(row)
            controls[label] = {"status":"pass" if passed else "failed",
                               "backend_status":result["status"],"root_count":len(roots)}
            print(json.dumps({"control":label,"result":controls[label]},sort_keys=True),flush=True)
            resource_check(label,samples)

        m2 = regression_m2()
        vectors["m2_regression"] = m2
        controls["small_m2_enumeration"] = {"status":m2["status"],
                                             "expected_count":len(m2["expected_roots"]),
                                             "backend_count":len(m2["backend_roots"])}
        print(json.dumps({"control":"small_m2_enumeration","result":controls["small_m2_enumeration"]},sort_keys=True),flush=True)
        resource_check("small_m2_enumeration",samples)
        validation["overall"] = "pass" if all(row["status"]=="pass" for row in controls.values()) else "failed"
    except Exception as exc:
        validation["overall"] = "censored" if str(exc).startswith("resource_limit") else "failed"
        validation["anomaly"] = {"class":type(exc).__name__,"detail":str(exc),
                                 "traceback":traceback.format_exc()}
        print(json.dumps({"anomaly":validation["anomaly"]},sort_keys=True),file=sys.stderr,flush=True)
    finally:
        validation["elapsed_seconds"] = time.monotonic()-started
        write_json("vectors.json",vectors)
        write_json("validation.json",validation)
    return 0 if validation["overall"]=="pass" else 1


if __name__ == "__main__":
    sys.exit(run())
