"""Persistent JSONL workers; frozen inputs; charged failures and verification."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import selectors
import signal
import subprocess
import sys
import time

from .certificate import Rank, certify, terms, vanishes


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def validate(manifest):
    if manifest.get("schema") != 1:
        raise ValueError("expected manifest schema 1")
    ring = manifest["ring"]
    n = ring["nvars"]
    if (type(n) is not int or not 1 <= n <= 12 or ring.get("field") != "GF(2)"
            or ring.get("order") != "degrevlex"
            or ring.get("quotient") != "x_i^2+x_i"
            or ring.get("variables") != [f"x{i}" for i in range(n)]):
        raise ValueError("requires frozen Boolean ring, 1..12 variables, x0 > x1 > ...")
    if not isinstance(manifest.get("encoding"), str) or not manifest["encoding"]:
        raise ValueError("encoding identity required")
    if type(manifest.get("threads", 1)) is not int or not 1 <= manifest.get("threads", 1) <= 64:
        raise ValueError("threads must be in 1..64")
    watchdog = manifest["watchdog_seconds"]
    if type(watchdog) not in (int, float) or not math.isfinite(watchdog) or watchdog <= 0:
        raise ValueError("positive finite per-request watchdog required")
    instances = manifest["instances"]
    backends = manifest["backends"]
    if not instances or not backends:
        raise ValueError("instances and backends must be nonempty")
    for items in (instances, backends):
        ids = [item["id"] for item in items]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("identities must be unique nonempty strings")
    for instance in instances:
        terms(instance["equations"], n)
        blocks = instance.get("blocks")
        if blocks is not None and (not isinstance(blocks, list) or not blocks
                or any(type(k) is not int or k < 1 for k in blocks) or sum(blocks) != n):
            raise ValueError("blocks must be positive lengths covering all variables")
    for backend in backends:
        command = backend["command"]
        if not isinstance(command, list) or not command or any(
                not isinstance(x, str) or not x for x in command):
            raise ValueError("worker command must be a nonempty argv list")
        if backend.get("mode") not in ("cold", "warm", "learn_apply"):
            raise ValueError("backend mode must be cold, warm, or learn_apply")
        if not backend.get("provenance"):
            raise ValueError("backend version/source provenance required")
    relation = manifest.get("relation_verifier")
    if relation is not None:
        Rank(relation["modulus"], relation["width"])
        if (not isinstance(relation.get("command"), list) or not relation["command"]
                or any(not isinstance(x, str) or not x for x in relation["command"])
                or not relation.get("provenance")):
            raise ValueError("independent verifier command and provenance required")
    curve = manifest.get("witness_verifier")
    if curve is not None and (not isinstance(curve.get("command"), list)
            or not curve["command"] or any(not isinstance(x, str) or not x
            for x in curve["command"]) or not curve.get("provenance")):
        raise ValueError("independent curve witness verifier command and provenance required")
    return manifest


class Worker:
    """A local, trusted worker (not a sandbox). Unix process-group watchdog."""

    def __init__(self, command, directory, number, watchdog, threads=1):
        self.watchdog = watchdog
        self.stderr = (directory / f"worker-{number}.stderr").open("xb")
        self.raw = (directory / f"worker-{number}.stdout").open("xb")
        self.requests = (directory / f"worker-{number}.requests.jsonl").open("x")
        self.process = None
        self.peak_rss = None
        try:
            environment = dict(os.environ)
            for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                             "JULIA_NUM_THREADS"):
                environment[variable] = str(threads)
            environment["PYTHONHASHSEED"] = "0"
            self.process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=self.stderr,
                                            start_new_session=True, bufsize=0, env=environment)
            os.set_blocking(self.process.stdout.fileno(), False)
        except BaseException:
            self.close()
            raise

    def sample_rss(self):
        # VmHWM is the worker process high-water mark, NOT a process-tree peak.
        try:
            for line in Path(f"/proc/{self.process.pid}/status").read_text().splitlines():
                if line.startswith("VmHWM:"):
                    value = int(line.split()[1]) * 1024
                    self.peak_rss = max(self.peak_rss or 0, value)
        except (OSError, ValueError):
            pass

    def request(self, payload):
        request = (encoded(payload) + "\n").encode()
        # Both directions are nonblocking and bounded. Workers that never read
        # stdin, never terminate a line, or flood stdout hit the same watchdog.
        if len(request) > 1_048_576:
            raise ValueError("request exceeds one MiB")
        self.requests.write(request.decode())
        self.requests.flush()
        os.set_blocking(self.process.stdin.fileno(), False)
        deadline = time.monotonic() + self.watchdog
        sent, buffer = 0, b""
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdin, selectors.EVENT_WRITE)
            selector.register(self.process.stdout, selectors.EVENT_READ)
            while True:
                self.sample_rss()
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("worker request watchdog expired; outcome unknown")
                for key, _ in selector.select(min(.05, remaining)):
                    if key.fileobj is self.process.stdin:
                        sent += os.write(self.process.stdin.fileno(), request[sent:])
                        if sent == len(request):
                            selector.unregister(self.process.stdin)
                    else:
                        chunk = os.read(self.process.stdout.fileno(), 65536)
                        if not chunk:
                            raise RuntimeError("worker exited before a complete response")
                        self.raw.write(chunk)
                        self.raw.flush()
                        buffer += chunk
                        if len(buffer) > 1_048_576:
                            raise ValueError("response exceeds one MiB")
                        if b"\n" in buffer:
                            line, rest = buffer.split(b"\n", 1)
                            if rest.strip():
                                raise ValueError("multiple responses to one request")
                            response = json.loads(line)
                            encoded(response)  # Reject NaN/Infinity before journaling.
                            if (not isinstance(response, dict)
                                    or response.get("request_id") != payload["request_id"]):
                                raise ValueError("response request identity mismatch")
                            self.sample_rss()
                            return response

    def close(self):
        if self.process is not None:
            # Kill the process group even if the parent exited leaving children.
            try:
                os.killpg(self.process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            self.process.wait()
            self.process.stdin.close()
            self.process.stdout.close()
        self.stderr.close()
        self.raw.close()
        self.requests.close()


def run_backend(manifest, backend, directory):
    directory.mkdir()
    started = time.perf_counter()
    parent_cpu_started = time.process_time()
    children_started = resource.getrusage(resource.RUSAGE_CHILDREN)
    events = []
    worker, verifier, curve_worker = None, None, None
    trace = None
    serial = 0
    peak_rss = None
    phases = {}
    results = []
    relation = manifest.get("relation_verifier")
    curve = manifest.get("witness_verifier")
    rank = Rank(relation["modulus"], relation["width"]) if relation else None
    relation_complete = True
    certified_applies = 0
    journal = (directory / "events.jsonl").open("x")

    def record(event):
        events.append(event)
        journal.write(encoded(event) + "\n")
        journal.flush()
        os.fsync(journal.fileno())

    def launch(command):
        nonlocal serial
        serial += 1
        return Worker(command, directory, serial, manifest["watchdog_seconds"],
                      manifest.get("threads", 1))

    def call(operation, instance, active, command, extra=None):
        nonlocal peak_rss
        begin = time.perf_counter()
        payload = {"schema": 1, "request_id": len(events), "operation": operation,
                   "ring": manifest["ring"], "encoding": manifest["encoding"],
                   "instance": instance, **(extra or {})}
        try:
            if active is None:
                active = launch(command)
            response = active.request(payload)
            status = response.get("status")
            if status not in ("ok", "incompatible", "unavailable", "error", "unknown"):
                raise ValueError("invalid worker status")
        except (OSError, ValueError, RuntimeError, TimeoutError) as error:
            status = ("timeout" if isinstance(error, TimeoutError) else
                      "unavailable" if isinstance(error, FileNotFoundError) else "error")
            response = {"status": status, "error": str(error)}
            if active is not None:
                active.close()
                if active.peak_rss is not None:
                    peak_rss = max(peak_rss or 0, active.peak_rss)
            active = None
        duration = time.perf_counter() - begin
        phases[operation] = phases.get(operation, 0) + duration
        if active is not None and active.peak_rss is not None:
            peak_rss = max(peak_rss or 0, active.peak_rss)
        record({"operation": operation, "instance_id": instance["id"],
                "seconds": duration, "status": status, "response": response})
        return response, active

    def check(instance, response):
        if response.get("status") != "ok":
            return None
        begin = time.perf_counter()
        try:
            n = manifest["ring"]["nvars"]
            if "basis_terms" in response:
                certificate = certify(n, instance["equations"], response["basis_terms"],
                                      blocks=response.get("basis_blocks"))
                if response.get("basis_blocks") not in (None, instance.get("blocks")):
                    certificate = {"verified": False, "reason": "basis block order differs from instance"}
            else:
                solutions = response["solutions"]
                if (not isinstance(solutions, list) or not solutions
                        or any(type(a) is not int or not 0 <= a < (1 << n) for a in solutions)
                        or len(solutions) != len(set(solutions))):
                    raise ValueError("solutions must be distinct in-range assignment masks")
                original = terms(instance["equations"], n)
                valid = all(vanishes(original, a) for a in solutions)
                certificate = {"verified": valid, "method": "direct-input-equation-replay",
                               "complete": False, "root_count": None,
                               "solutions": solutions if valid else None}
        except (KeyError, TypeError, ValueError) as error:
            certificate = {"verified": False, "error": str(error)}
        duration = time.perf_counter() - begin
        phases["basis_verification"] = phases.get("basis_verification", 0) + duration
        record({"operation": "basis_verification", "instance_id": instance["id"],
                "seconds": duration, "certificate": certificate})
        return certificate if certificate["verified"] else None

    try:
        for index, instance in enumerate(manifest["instances"]):
            if backend["mode"] == "cold" and worker is not None:
                worker.close()
                worker = None
            operation = ("learn" if index == 0 else "apply") if (
                backend["mode"] == "learn_apply" and (index == 0 or trace is not None)
            ) else "solve"
            response, worker = call(operation, instance, worker, backend["command"],
                                    {"trace_id": trace} if operation == "apply" else None)
            certificate = check(instance, response)
            if operation == "apply" and certificate is not None:
                certified_applies += 1
            if operation == "learn" and certificate and isinstance(response.get("trace_id"), str):
                trace = response["trace_id"] or None
            if operation in ("learn", "apply") and certificate is None:
                # Never reuse suspect state; fallback costs include restart.
                if worker is not None:
                    worker.close()
                    worker = None
                trace = None
                response, worker = call("fallback", instance, worker, backend["command"],
                                        {"operation": "solve"})
                certificate = check(instance, response)
            result = {"instance_id": instance["id"], "input_sha256": digest(instance),
                      "status": ("verified" if certificate and certificate["root_count"] is not None
                                 else "verified_witness" if certificate else "unknown"),
                      "root_count": certificate["root_count"] if certificate else None,
                      "relation_rank_increment": None}
            if curve is not None:
                result["curve_witness"] = "unknown"
                if certificate and certificate["solutions"] is not None:
                    reply, curve_worker = call("verify_witnesses", instance, curve_worker,
                                               curve["command"],
                                               {"solutions": certificate["solutions"]})
                    try:
                        candidates = certificate["solutions"]
                        confirmed = reply["verified_solutions"]
                        if (reply.get("status") != "ok" or not isinstance(confirmed, list)
                                or any(type(a) is not int or a not in candidates for a in confirmed)
                                or len(confirmed) != len(set(confirmed))):
                            raise ValueError("invalid curve witness verification")
                        result["curve_witness"] = "verified" if confirmed else "none"
                        result["curve_verified_solutions"] = confirmed
                    except (KeyError, TypeError, ValueError):
                        result["curve_witness"] = "unknown"
            if rank is not None and certificate is None:
                relation_complete = False
            if certificate and rank is not None:
                reply, verifier = call("verify_relations", instance, verifier,
                                       relation["command"], {"solutions": certificate["solutions"]})
                begin = time.perf_counter()
                try:
                    if reply.get("status") != "ok":
                        raise ValueError("independent relation verifier did not complete")
                    result["relation_rank_increment"] = rank.add(reply["vectors"])
                except (KeyError, ValueError, TypeError):
                    relation_complete = False
                    result["relation_verification"] = "unknown"
                duration = time.perf_counter() - begin
                phases["relation_rank"] = phases.get("relation_rank", 0) + duration
                record({"operation": "relation_rank", "instance_id": instance["id"],
                        "seconds": duration, "increment": result["relation_rank_increment"]})
            results.append(result)
    finally:
        for active in (worker, verifier, curve_worker):
            if active is not None:
                active.close()
        journal.close()
    total = time.perf_counter() - started
    children_finished = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (time.process_time() - parent_cpu_started
           + children_finished.ru_utime + children_finished.ru_stime
           - children_started.ru_utime - children_started.ru_stime)
    verified = sum(row["status"] == "verified" for row in results)
    witnesses = sum(row["status"] == "verified_witness" for row in results)
    metrics = [event.get("response", {}).get("metrics", {}) for event in events]
    metrics = [m for m in metrics if isinstance(m, dict)]
    # Preserve progress from workers killed at a watchdog or matrix budget.
    # Stderr is an archived append-only stream, and its markers are advisory
    # solver telemetry rather than correctness certificates.
    for stderr_path in sorted(directory.glob("worker-*.stderr")):
        for line in stderr_path.read_text(errors="replace").splitlines():
            if line.startswith("GROEBNER_TELEMETRY "):
                try:
                    report = json.loads(line[len("GROEBNER_TELEMETRY "):])
                    if isinstance(report, dict):
                        metrics.append(report)
                except ValueError:
                    pass

    def maximum(name):
        values = [m[name] for m in metrics if type(m.get(name)) is int and m[name] >= 0]
        return max(values) if values else None

    summary = {"schema": 1, "scope": "bounded-Boolean-solver-stage",
               "manifest_sha256": digest(manifest), "backend": backend,
               "candidate_id": None, "full_dlp_speedup": None,
               "timing_boundary": "backend launch through worker cleanup, including verification and journal IO",
               "excluded_costs": ["environment provisioning", "upstream instance generation/encoding",
                                  "downstream DLP stages", "final summary serialization"],
               "total_wall_seconds": total, "phase_seconds": phases,
               "parent_and_reaped_children_cpu_seconds": cpu,
               "unattributed_wall_seconds": total - sum(phases.values()),
               "verified_instances": verified, "attempted_instances": len(results),
               "verified_witness_instances": witnesses,
               "verified_curve_witness_instances": (
                   sum(row.get("curve_witness") == "verified" for row in results)
                   if curve is not None else None),
               "verified_witness_instances_per_total_second": witnesses / total,
               "trace_apply_attempts": sum(e["operation"] == "apply" for e in events),
               "certified_trace_applies": certified_applies,
               "fallback_attempts": sum(e["operation"] == "fallback" for e in events),
               "verified_instances_per_total_second": verified / total,
               "verified_relation_rank": len(rank.pivots) if rank is not None else None,
               "relation_verification_complete": relation_complete if rank is not None else None,
               "verified_rank_per_total_second": len(rank.pivots) / total if rank is not None else None,
               "peak_worker_process_rss_bytes": peak_rss,
               "backend_reported_highest_degree": maximum("highest_degree"),
               "backend_reported_largest_matrix_rows": maximum("largest_matrix_rows"),
               "backend_reported_largest_matrix_columns": maximum("largest_matrix_columns"),
               "results": results}
    (directory / "summary.json").write_text(encoded(summary) + "\n")
    return summary


def run(manifest, output):
    validate(manifest)
    output = Path(output)
    # Exclusive directory creation: old evidence is never overwritten.
    output.mkdir(parents=True, exist_ok=False)
    (output / "manifest.json").write_text(encoded(manifest) + "\n")
    source = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(Path(__file__).parent.iterdir()) if p.is_file()}
    (output / "host.json").write_text(encoded({"python": sys.version,
        "platform": platform.platform(), "source_sha256": source,
        "manifest_sha256": digest(manifest), "cwd": str(Path.cwd()),
        "started_unix_seconds": time.time()}) + "\n")
    summaries = [run_backend(manifest, backend, output / f"backend-{i}")
                 for i, backend in enumerate(manifest["backends"])]
    (output / "comparison.json").write_text(encoded(summaries) + "\n")
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for result in run(json.loads(args.manifest.read_text()), args.output):
        print(encoded({k: result[k] for k in ("backend", "verified_instances",
            "attempted_instances", "total_wall_seconds", "verified_rank_per_total_second")}))


if __name__ == "__main__":
    main()
