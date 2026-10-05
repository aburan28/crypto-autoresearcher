"""00 -- CONSTRUCTION-FIDELITY CHECK of TASK-20261002-a8bbd8.

Verifies the adapted generator (code/01_generator.py) reproduces the archived
replica rows EXACTLY before any new rung is generated: same seeds, same N rule,
same encodings, same pair counting, same row fields, same mode semantics. Runs
a handful of ARCHIVED instances (m4 b12, m5 b12, m4 b24; on-mode) through the
adapted generator into out/fidelity/ (a SEPARATE file -- nothing here ever
enters out/replica_rows.jsonl, which holds only the new 26..32 rows), then
compares every row field-by-field against the archived rows (all fields except
"seconds", which is wall-clock, not construction).

NO import or execution of anything under src/crypto_autoresearcher: the
generator is the task's own adapted copy of the red team's self-contained
replica (RF-4: imports only heapq/json/math/os/sys/time/numpy); this check
shells out to it exactly as the generation driver does.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TASK = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(os.path.dirname(TASK)))
ARCH = os.path.join(WT, "coordination/review/pfdr-twfloor-20261001/reviews/"
                    "TASK-20260929-575e80/attacks/out/ptm5_results.jsonl")
PY = sys.executable
GEN = os.path.join(HERE, "01_generator.py")
FID = os.path.join(TASK, "out", "fidelity")
os.makedirs(FID, exist_ok=True)

CASES = [("m4_b12", 4, 12, 0, 6),   # m = 4 path (h = 2 table)
         ("m5_b12", 5, 12, 0, 6),   # m = 5 path (h = 3 table, level-3 decode)
         ("m4_b24", 4, 24, 0, 3)]   # a larger archived rung


def strip_seconds(rec):
    rec = dict(rec)
    rec.pop("seconds", None)
    return rec


def deep_eq(a, b, path="$"):
    if type(a) is not type(b):
        return [f"{path}: type {type(a).__name__} != {type(b).__name__}"]
    if isinstance(a, dict):
        errs = []
        for k in sorted(set(a) | set(b)):
            if k not in a:
                errs.append(f"{path}.{k}: missing in generated")
            elif k not in b:
                errs.append(f"{path}.{k}: missing in archived")
            else:
                errs.extend(deep_eq(a[k], b[k], f"{path}.{k}"))
        return errs
    if isinstance(a, list):
        if len(a) != len(b):
            return [f"{path}: len {len(a)} != {len(b)}"]
        return [e for i, (x, y) in enumerate(zip(a, b))
                for e in deep_eq(x, y, f"{path}[{i}]")]
    return [] if a == b else [f"{path}: {a!r} != {b!r}"]


def main():
    arch = [json.loads(l) for l in open(ARCH)]
    idx = {(r["m"], r["N"], r["inst"], r["mode"]): r for r in arch}
    out = {"task": "TASK-20261002-a8bbd8", "purpose": "verify the adapted "
           "generator reproduces the archived replica construction exactly "
           "(same seeds/N rule/encodings/pair counting/row fields/mode "
           "semantics) before generating the new rungs; the generated rows "
           "here are fidelity probes only -- they never enter "
           "out/replica_rows.jsonl and never enter the analysis",
           "compared_fields": "every row field except 'seconds' (wall-clock)",
           "cases": {}}
    ok_all = True
    for tag, m, bits, lo, hi in CASES:
        path = os.path.join(FID, f"{tag}.jsonl")
        if os.path.exists(path):
            os.remove(path)
        cmd = [PY, GEN, path, str(m), str(bits), str(lo), str(hi)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            out["cases"][tag] = {"generator_exit": r.returncode,
                                 "stderr_tail": r.stderr[-2000:]}
            ok_all = False
            continue
        gen = [json.loads(l) for l in open(path)]
        case = {"generator_cmd": cmd, "n_generated": len(gen), "mismatches": []}
        for g in gen:
            a = idx.get((g["m"], g["N"], g["inst"], g["mode"]))
            if a is None:
                case["mismatches"].append(
                    {"row": (g["m"], g["N"], g["inst"], g["mode"]),
                     "error": "no archived row with this key"})
                continue
            errs = deep_eq(strip_seconds(g), strip_seconds(a))
            if errs:
                case["mismatches"].append(
                    {"row": (g["m"], g["N"], g["inst"], g["mode"]),
                     "fields": errs[:20]})
        case["exact_match"] = not case["mismatches"]
        ok_all &= case["exact_match"]
        out["cases"][tag] = case
        print(f"{tag}: n={case['n_generated']} exact_match={case['exact_match']}")
        for mm in case["mismatches"][:3]:
            print("  MISMATCH", json.dumps(mm)[:400])
    out["all_exact_match"] = ok_all
    dest = os.path.join(TASK, "out", "fidelity_check.json")
    json.dump(out, open(dest, "w"), indent=1, sort_keys=True)
    print("all_exact_match:", ok_all)
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
