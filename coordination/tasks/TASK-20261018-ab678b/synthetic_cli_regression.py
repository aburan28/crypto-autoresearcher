#!/usr/bin/env python3
"""Actual subprocess CLI regression; synthetic fixture only, no ECDLP cell.

The frozen envelope is copied byte for byte into an isolated disposable Git
checkout. Two tiny unrelated C++ programs replace scientific routes in that
fixture. Launch/environment/command documents are explicitly synthetic test
provenance, not a native supervisor admission or production run receipt.
The Coordinator permits Git initialization/commit ONLY in this disposable
fixture; no Git mutation is made in the shared research repository.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[3]
TASK = Path(__file__).resolve().parent
HELPER = Path("coordination/tasks/TASK-20261018-1cb336/envelope.py")
ARTIFACTS = ["raw-result.json", "primary-output.json", "native-primary.json",
             "independent-check.json", "certificate.yaml", "manifest.yaml"]
OBSERVED_PREFIX = ["env", "GIT_CONFIG_COUNT=1", "GIT_CONFIG_KEY_0=core.preloadIndex",
                   "GIT_CONFIG_VALUE_0=false"]
CPP_A = r'''#include <cstdio>
#include <cstring>
int main(int n,char**v) {
 if(n==2 && std::strcmp(v[1],"--self-test")==0) {
  std::puts("{\"synthetic_control\":true,\"frozen_worksheet_executed\":false}"); return 0;
 }
 int fixture=2+5;
 std::printf("{\"synthetic_only\":true,\"fixture_value\":%d}\n",fixture);
}
'''
CPP_B = r'''#include <iostream>
#include <string>
int main(int n,char**v) {
 if(n==2 && std::string(v[1])=="--self-test") {
  std::cout << "{\"synthetic_control\":true,\"frozen_worksheet_executed\":false}\n";
 } else {
  int fixture=9-2;
  std::cout << "{\"fixture_value\":" << fixture << ",\"synthetic_only\":true}\n";
 }
}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def call(argv, cwd, *, ceiling=False):
    def limits():
        resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    start = time.monotonic()
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                            timeout=120, preexec_fn=limits if ceiling else None)
    return {"argv": argv, "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr,
            "wall_seconds": time.monotonic()-start,
            "address_space_cap_bytes": 1024**3 if ceiling else None}


def run(output):
    output.mkdir()  # exclusive, including failed synthetic attempts
    original_hash = sha(ROOT/HELPER)
    original_failure_command = json.loads((ROOT/"experiments/EXP-ECDLP-95f69f/runs/RUN-ECDLP-f67842/command.txt").read_text())
    assert original_failure_command[:4] == OBSERVED_PREFIX
    compiler = json.loads((ROOT/"experiments/EXP-ECDLP-95f69f/implementation/config.json").read_text())["compiler"]
    receipt = {"schema": "synthetic-cli-conformance.v1", "synthetic_only": True,
               "scientific_trials": 0, "frozen_worksheet_cells": 0,
               "production_supervisor_admission_claimed": False,
               "helper_source": str(HELPER), "helper_sha256": original_hash,
               "helper_monkeypatched": False, "fixture_cpp_a": CPP_A, "fixture_cpp_b": CPP_B,
               "source_failure_prefix": OBSERVED_PREFIX, "steps": []}
    with tempfile.TemporaryDirectory(prefix="worksheet-synthetic-cli-") as temporary:
        fixture = Path(temporary)
        target = fixture/HELPER
        target.parent.mkdir(parents=True)
        shutil.copy2(ROOT/HELPER, target)
        assert sha(target) == original_hash
        exp = "SYNTHETIC-CLI-ONLY"
        impl = Path("experiments")/exp/"implementation"
        spec = Path("experiments")/exp/"specification.json"
        config_path = impl/"config.json"
        for name, text in (("route_a.cpp", CPP_A), ("route_b.cpp", CPP_B)):
            path = fixture/impl/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        write(fixture/spec, {"synthetic_only": True, "not_a_scientific_specification": True})
        write(fixture/impl/"bindings.json", {"synthetic_only": True, "scope": "CLI fixture, not ECDLP"})
        config = {"experiment_id": exp, "specification": str(spec), "seed": None,
                  "source_dependencies": [str(spec), str(impl/"bindings.json"),
                                          str(impl/"route_a.cpp"), str(impl/"route_b.cpp")],
                  "routes": {"a": str(impl/"route_a.cpp"), "b": str(impl/"route_b.cpp")},
                  "compiler": compiler, "curve_id": None, "bindings": str(impl/"bindings.json"),
                  "scope": "SYNTHETIC CLI FIXTURE ONLY; no cryptographic arithmetic or scientific trial",
                  "controls": [{"field": "synthetic_only", "value": True},
                               {"field": "fixture_value", "value": 7}],
                  "predictions": [{"field": "fixture_value", "value": 8}],
                  "prediction_scope": "Intentionally false synthetic predicate, no scientific hypothesis"}
        write(fixture/config_path, config)
        # Real Git commands and a real commit, exclusively in the disposable
        # fixture. No env override, fake Git executable or shared-index writes.
        for command in (["git", "init", "-q"], ["git", "add", "."],
                        ["git", "-c", "user.name=Synthetic CLI Fixture",
                         "-c", "user.email=fixture@example.invalid", "commit", "-qm",
                         "synthetic fixture only; no scientific result"]):
            record = call(command, fixture)
            receipt["steps"].append(record)
            assert record["returncode"] == 0, record
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=fixture, text=True).strip()
        sources = {str(path): sha(fixture/path) for path in [HELPER, config_path, *map(Path, config["source_dependencies"])]}
        trials = []
        plan_path = Path("synthetic-plan.json")
        for shape in ("direct", "observed-env-prefix"):
            command = [sys.executable, str(HELPER), "run", "--plan", str(plan_path),
                       "--out", "{run_dir}", "--route", "a"]
            if shape != "direct":
                command = [*OBSERVED_PREFIX, *command]
            trials.append({"id": shape, "run_id": "SYNTHETIC-"+shape,
                           "argv": command,
                           "check_argv": [sys.executable, str(HELPER), "check", "--plan", str(plan_path),
                                          "--out", "{run_dir}", "--route", "a"],
                           "artifacts": ARTIFACTS, "memory_mb": 1024, "watchdog_seconds": 120,
                           "finite_worksheet": {"route": "a", "implementation": str(config_path), "input_seed": None}})
        plan = {"schema": "crypto.autoresearch.trial_plan.v1", "frozen": True,
                "experiment_id": exp, "specification": str(spec),
                "specification_sha256": sha(fixture/spec), "source_sha256": sources,
                "synthetic_only": True, "trials": trials}
        write(fixture/plan_path, plan)
        for trial in trials:
            directory = fixture/"experiments"/exp/"runs"/trial["run_id"]
            directory.mkdir(parents=True)
            expanded = lambda argv: [x.replace("{run_dir}", str(directory)) for x in argv]
            # Explicit synthetic provenance. This does not impersonate the
            # native research supervisor or supply a production claim.
            launch = {"plan_sha256": sha(fixture/plan_path), "trial_id": trial["id"],
                      "run_id": trial["run_id"], "started_at": datetime.now(timezone.utc).isoformat(),
                      "authority": {"commit": commit, "synthetic_fixture_only": True},
                      "argv": expanded(trial["argv"]), "check_argv": expanded(trial["check_argv"]),
                      "synthetic_provenance_not_production": True}
            write(directory/"launch.json", launch)
            write(directory/"environment.json", {"source_sha256": sources,
                  "specification_sha256": plan["specification_sha256"], "commit": commit,
                  "synthetic_provenance_not_production": True})
            (directory/"command.txt").write_text(json.dumps(launch["argv"])+"\n")
            record = call(launch["argv"], fixture, ceiling=True)
            receipt["steps"].append({"case": trial["id"], "phase": "primary", **record})
            if trial["id"] == "direct":
                assert record["returncode"] == 0, record
                checked = call(launch["check_argv"], fixture, ceiling=True)
                receipt["steps"].append({"case": "direct", "phase": "independent-check", **checked})
                assert checked["returncode"] == 0, checked
                manifest = json.loads((directory/"manifest.yaml").read_text())["run"]
                assert manifest["result"]["valid"] is True
                assert manifest["result"]["metrics"]["prediction_match"] is False
                assert manifest["result"]["metrics"]["observations"] == {"fixture_value": 7, "synthetic_only": True}
                assert all((directory/name).is_file() for name in ARTIFACTS)
            else:
                assert record["returncode"] == 1, record
                assert record["stderr"].strip() == "current invocation differs from the actual supervisor command", record
                assert not any((directory/name).exists() for name in ARTIFACTS)
        # Preserve actual fixture commands/logs/artifacts, explicitly outside
        # every production experiment directory, with no object database.
        with tarfile.open(output/"synthetic-fixture-evidence.tar.gz", "w:gz") as archive:
            for path in sorted(fixture.rglob("*")):
                if path.is_file() and ".git" not in path.relative_to(fixture).parts:
                    archive.add(path, arcname="synthetic-fixture-only/"+path.relative_to(fixture).as_posix())
        receipt["temporary_fixture_commit"] = commit
        receipt["fixture_archive_sha256"] = sha(output/"synthetic-fixture-evidence.tar.gz")
        receipt["direct_primary_and_independent_check_pass"] = True
        receipt["observed_env_prefix_refused_before_native_compilation"] = True
    assert sha(ROOT/HELPER) == original_hash
    receipt["original_helper_unchanged"] = True
    receipt["passed"] = True
    write(output/"receipt.json", receipt)
    print(json.dumps({"synthetic_only": True, "passed": True,
                      "scientific_trials": 0, "helper_sha256": original_hash,
                      "receipt_sha256": sha(output/"receipt.json")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    destination = Path(arguments.output).resolve()
    if not destination.is_relative_to(TASK):
        raise ValueError("write only in the source-preparation handoff scope")
    run(destination)
