#!/usr/bin/env python3
"""Read-only local CLI/registry probe. It never creates a Job or a service."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess


def probe(image=None, mcp_binary=None):
    record = {"schema": "classical.ecdlp.endpoint-reuse.local-readiness/v1",
              "recorded_at": datetime.now(timezone.utc).isoformat(), "ready": False,
              "scope": "the local CLI route only; not a scientific approval or isolated measurement",
              "mutations": [], "blockers": [], "checks": {}}
    if not image or re.fullmatch(r"[^\s]+@sha256:[0-9a-f]{64}", image) is None:
        record["blockers"].append("No actual published candidate image digest was supplied.")
    executable = mcp_binary or shutil.which("isolab-eks-mcp")
    if not executable or not Path(executable).is_file():
        record["blockers"].append("No actual local isolab-eks-mcp executable/connection is configured.")
    docker = shutil.which("docker")
    if not docker:
        record["blockers"].append("No registry manifest inspector is available.")
    if record["blockers"]:
        return record
    try:
        catalog_call = subprocess.run([executable, "tools"], capture_output=True, text=True, timeout=30, check=True)
        catalog = json.loads(catalog_call.stdout)
        names = {x["name"] for x in catalog["tools"]}
        if not {"isolab_k8s_run", "isolab_k8s_overview", "isolab_k8s_status", "isolab_k8s_results"} <= names:
            raise ValueError("the actual server lacks the generic Job contract")
        overview_call = subprocess.run([executable, "call", "isolab_k8s_overview", "{}"], capture_output=True, text=True, timeout=55, check=True)
        overview = json.loads(overview_call.stdout)
        # A real server may wrap tool results; retain it rather than inferring access.
        record["checks"]["overview_returned"] = True
        record["checks"]["overview"] = overview
        if overview.get("namespace") != "isolab" or overview.get("node_pool") != "cpu-spot":
            raise ValueError("the live response did not establish the expected lab/pool")
        registry = subprocess.run([docker, "manifest", "inspect", image], capture_output=True, text=True, timeout=30)
        record["checks"]["registry_manifest_returncode"] = registry.returncode
        if registry.returncode:
            raise ValueError("the digest-pinned image could not be read through existing registry authorization")
        json.loads(registry.stdout)
        record["checks"]["image_manifest_read"] = True
        record["ready"] = True
    except Exception as error:
        record["blockers"].append(str(error) if isinstance(error, ValueError) else type(error).__name__)
    return record


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image")
    p.add_argument("--mcp-binary")
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    if a.out.exists():
        p.error("fresh observation path required")
    result = probe(a.image, a.mcp_binary)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ready"] else 2)


if __name__ == "__main__":
    main()
