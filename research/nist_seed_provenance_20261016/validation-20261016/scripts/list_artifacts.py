#!/usr/bin/env python3
"""Print every file under validation-20261016/ (except validation_report.yaml, which cannot
carry its own hash) as YAML artifact_paths entries with SHA-256 and size."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, sha256_file

base = "research/nist_seed_provenance_20261016/validation-20261016"
for dp, dn, fn in sorted(os.walk(ROOT)):
    dn.sort()
    for f in sorted(fn):
        full = os.path.join(dp, f)
        rel = os.path.relpath(full, ROOT)
        if rel == "validation_report.yaml":
            continue
        print(f"    - path: {base}/{rel}\n      sha256: {sha256_file(full)}\n      bytes: {os.path.getsize(full)}")
