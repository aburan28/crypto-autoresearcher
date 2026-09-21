# EXP-STR-004 CTRL-2: independent Sage re-verification of base-row decomposition
# certificates. Invoked ONLY through the `sage` binary — never as a Python import.
# Does NOT import, call, or replicate harness/toycurve.py.
#
# Usage:
#   sage experiments/EXP-STR-004/driver/verify_certificates.sage \
#       <certificates.json> <output.json>
#
# Input JSON schema:
#   {
#     "sage_version_string_expected": "<verbatim sage --version string>",
#     "certificates": [
#       {
#         "id": "<run_id>:base:<index>",
#         "run_id": "RUN-STR-004-...",
#         "base_row_index": <int>,
#         "kind": "decomposition",
#         "statement": {
#           "target": [x, y],
#           "summands": [[x, y], ...],
#           "curve": {"p": p, "a": a, "b": b}
#         }
#       },
#       ...
#     ]
#   }
#
# Output JSON schema:
#   {
#     "sage_version_string": "<this sage's version>",
#     "verifier": "sage-EllipticCurve-independent",
#     "n_input": <int>,
#     "n_checked": <int>,
#     "n_pass": <int>,
#     "n_fail": <int>,
#     "results": [{"id": ..., "run_id": ..., "base_row_index": ..., "ok": bool, "reason": str}, ...]
#   }

import json
import sys

if len(sys.argv) != 3:
    print("usage: sage verify_certificates.sage <certificates.json> <output.json>", file=sys.stderr)
    sys.exit(2)

in_path = sys.argv[1]
out_path = sys.argv[2]

with open(in_path, "r") as fh:
    payload = json.load(fh)

# SageMath version string (same family as `sage --version`)
try:
    sage_version_string = "SageMath version %s, Release Date: %s" % (
        sage.version.version, sage.version.date())
except Exception:
    sage_version_string = str(version())

expected = payload.get("sage_version_string_expected")
certs = payload.get("certificates", [])
results = []
n_pass = 0
n_fail = 0

for c in certs:
    cid = c.get("id")
    run_id = c.get("run_id")
    bidx = c.get("base_row_index")
    kind = c.get("kind")
    if kind != "decomposition":
        results.append({
            "id": cid, "run_id": run_id, "base_row_index": int(bidx) if bidx is not None else None,
            "ok": False, "reason": "unsupported_kind:%s" % kind,
        })
        n_fail += 1
        continue
    st = c.get("statement") or {}
    curve = st.get("curve") or {}
    try:
        p = Integer(curve["p"])
        a = Integer(curve["a"])
        b = Integer(curve["b"])
        E = EllipticCurve(GF(p), [a, b])
        target = E(Integer(st["target"][0]), Integer(st["target"][1]))
        acc = E(0)
        for s in st["summands"]:
            pt = E(Integer(s[0]), Integer(s[1]))
            acc = acc + pt
        ok = bool(acc == target)
        reason = "summands_sum_to_target" if ok else "sum_mismatch"
    except Exception as exc:
        ok = False
        reason = "exception:%s" % type(exc).__name__
    results.append({
        "id": cid,
        "run_id": run_id,
        "base_row_index": int(bidx) if bidx is not None else None,
        "ok": bool(ok),
        "reason": str(reason),
    })
    if ok:
        n_pass += 1
    else:
        n_fail += 1

# Coerce every scalar to a JSON-native Python type. Sage Integer/Boolean are
# not json-serializable (json.dump truncates mid-object and exits nonzero).
out = {
    "sage_version_string": str(sage_version_string),
    "sage_version_string_expected": expected,
    "sage_version_matches_expected": (
        bool(sage_version_string == expected) if expected else None
    ),
    "verifier": "sage-EllipticCurve-independent",
    "imports_harness_toycurve": False,
    "n_input": int(len(certs)),
    "n_checked": int(len(results)),
    "n_pass": int(n_pass),
    "n_fail": int(n_fail),
    "results": results,
}

with open(out_path, "w") as fh:
    json.dump(out, fh, indent=2, sort_keys=True)
    fh.write("\n")

print("checked=%d pass=%d fail=%d" % (int(len(results)), int(n_pass), int(n_fail)))
# Use os._exit: Sage's wrapper sometimes turns a clean sys.exit(0) into
# process exit 1, which the driver must not treat as certificate failure.
import os
os._exit(0 if int(n_fail) == 0 else 1)
