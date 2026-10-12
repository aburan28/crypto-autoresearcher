#!/usr/bin/env python3
"""w5_worker.py LIB SYSJSON D CAP_GIB [ROWS_OUT]  -- run ONE closure with ONE library in a fresh process; print one JSON line.
Counts batches from the library's own verbose line on stderr (CLOSURE_VERBOSE=1 is set here). SCRATCH, TASK-20261004-7d2fb6."""
import sys, os, json, io, re, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vclos
lib, sysjson, D, cap = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
rows_out = sys.argv[5] if len(sys.argv) > 5 else None
s = json.load(open(sysjson))
os.environ["CLOSURE_VERBOSE"] = "1"
c = vclos.Clos(lib)
# capture the C library's stderr by redirecting fd 2 to a temp file
import tempfile
tf = tempfile.TemporaryFile(mode="w+b")
saved = os.dup(2); os.dup2(tf.fileno(), 2)
try:
    r = c.run(s["N"], D, s["equations"], mem_cap_gb=cap, want_rows=bool(rows_out))
finally:
    os.dup2(saved, 2); os.close(saved)
tf.seek(0); err = tf.read().decode(errors="replace")
batches = len(re.findall(r"^\[closure D=\d+ it=\d+\] batch", err, re.M))
out = {k: v for k, v in r.items() if k not in ("rows", "lm")}
out["batches"] = batches
out["lib"] = os.path.basename(lib); out["cap_gib"] = cap
out["lm_by_deg"] = r.get("by_deg")
out["stderr_other"] = [l for l in err.splitlines() if not l.startswith("[closure D=")][:5]
if rows_out and "rows" in r:
    vclos.write_rows_bin(r["rows"], rows_out)
if "lm" in r:
    out["lm_list_sha"] = None
    with open(sysjson + ".lm_last", "w") as fh: fh.write("\n".join(map(str, r["lm"])))
print(json.dumps(out))
