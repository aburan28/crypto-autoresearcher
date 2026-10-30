#!/usr/bin/env python3
"""Emit the sources_read YAML block from sources_sha256.txt (crypto paths,
relative to the crypto checkout) and a fixed list of autoresearcher docs."""
import re
import sys

d = sys.argv[1]
HOW = [
    (r"PROTOCOL(_AMENDMENT_1)?\.md$", "read in full before any producer output (the statement)", "blind"),
    (r"/specs/c24\.json$", "read in full; all six normalised and compared by receipt_checks/inline spec diff", "blind"),
    (r"/specs/.*\.json$", "parsed (normalised spec diff: only curve, base sizes, label differ)", "blind"),
    (r"records\.jsonl$", "parsed by own scripts rederive.py, controls.py, multiplicity.py, receipt_checks.py", "blind"),
    (r"r24/session\.json$", "read in full; parsed by receipt_checks.py", "blind"),
    (r"session\.json$", "parsed by receipt_checks.py (planned/written/status/sha/commit)", "blind"),
    (r"plan\.json$", "sha256 only (equals session.json plan_sha256)", "blind"),
    (r"sessions/.*/spec\.json$", "sha256 (equals specs/<s>.json) and parsed for isolation_required", "blind"),
    (r"ecbench/compare\.rs$", "read lines 1-490 (compare, match_pairs, ratio_with_interval); read-only, not built", "blind"),
    (r"ecbench/stats\.rs$", "read in full (Resampler, quantile, bootstrap); read-only", "blind"),
    (r"ecbench/band\.rs$", "read in full (unpriced_counts, priced_gae, band, ranks); read-only", "blind"),
    (r"ecbench/canonical\.rs$", "read lines 117-123 (splitmix64)", "blind"),
    (r"ecbench/record\.rs$", "read lines 361-373 (counts)", "blind"),
    (r"ecbench/methods\.rs$", "read lines 580-600 (expected_s) and 1898-1990 (PRICED_NATIVE)", "blind"),
    (r"bin/ecbench\.rs$", "read lines 220-280, 1070-1160, 1630-1805 (CLI defaults, compare, band_cmd, table)", "blind"),
    (r"^AGENTS\.md$", "crypto AGENTS.md sec 5a (691-724) and sec 10 (1088-1159)", "blind"),
    (r"analysis/summary\.json$", "after blind seal; diffed by compare_summary.py", "after_seal"),
    (r"analysis/", "after blind seal; diffed by compare_producer.py", "after_seal"),
    (r"scripts/summary\.(jq|sh)$", "after blind seal; read in full, not executed", "after_seal"),
    (r"scripts/plots\.py$", "after blind seal; read in full, not executed", "after_seal"),
    (r"README\.md$", "after blind seal; read in full; numbers checked by check_prose.py", "after_seal"),
    (r"REPORT\.typ$", "after blind seal; read in full; numbers checked by check_prose.py", "after_seal"),
    (r"REPORT\.pdf$", "after blind seal; pdftotext -layout (text equals REPORT.typ)", "after_seal"),
    (r"figures/.*\.svg$", "after blind seal; data decoded by decode_figures.py", "after_seal"),
]
out = ["sources_read:"]
for line in open(f"{d}/sources_sha256.txt"):
    sha, path = line.split()
    how, phase = next(((h, p) for rx, h, p in HOW if re.search(rx, path)), ("read", "?"))
    out.append(f"  - {{path: 'crypto:{path}', sha256: {sha}, phase: {phase}, how: '{how}'}}")
out.append("  - {path: 'crypto:research/ic_planner_validation_20261020/sessions/*/comparisons/*.json (42 files)', "
           "sha256: 'per file in scripts/readers/stats/sources_comparisons_sha256.txt', phase: after_seal, "
           "how: 'after blind seal; diffed by compare_producer.py'}")
out.append("  - {path: 'crypto:benchmarks/20261020-ic-planner-validation/{REPORT.pdf,*.svg}', sha256: 'identical to the research/ copies (85f40e8c..., d15452fa..., 0003c109..., a8efe167...)', phase: after_seal, how: 'sha256 only'}")
out.append("  - {path: 'crypto: git metadata (log, merge-base, diff --name-only, show --stat 68bae680b)', sha256: 'n/a', phase: blind, how: 'read-only git; output scripts/readers/stats/git_checks.txt'}")
for p, sha, how in (
    ("docs/agent-runtime-core.md", "720f372d63c45c5154c4be1f03e36dde349b9cc0bc64b68481ed7e8a28356606", "read in full"),
    ("agents/validator.md", "33947db8c7cc8663ac79f1eff4b183e75d0546915feb23e77654cd03a249c9d2", "read in full"),
    ("docs/sheriff.md", "16fc9ca487b64122403de02128005ebc8f8ae75798a454118de796e06aa4f54c", "lines 1-100, 278-364 (B5, B6), 436-505 (B9, B10)"),
    ("AGENTS.md", "e3cf5d3ac17eb5c600879273af8f327957cd0ea0058df02bb11ebd214342c709", "sections Review architecture (359-371) and Curve identity and measured bounds (523-538)"),
    ("research/sheriff/SHF-20261021-477d51/prior.md", "a747919fb12c79f8f46145d9c51a143f12bf82c9c8a81ab8d4e8f4fda5a6d61e", "first 40 lines (the case prior; no producer numbers)"),
):
    out.append(f"  - {{path: 'crypto-autoresearcher:{p}', sha256: {sha}, phase: blind, how: '{how}'}}")
open(sys.argv[2], "w").write("\n".join(out) + "\n")
print("wrote", sys.argv[2], len(out) - 1, "entries")
