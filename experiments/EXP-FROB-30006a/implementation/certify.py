#!/usr/bin/env python3
"""Drive the independent certifier (pdp_enum.c) for one instance directory, and
optionally cross-check it against a brute-force pure-Python evaluation of the
summation polynomial over all of V^m (small cells only).

  certify.py INSTANCE_DIR [--enum-bin PATH] [--python-reference] [--limit K]

Writes INSTANCE_DIR/enum_params.txt and INSTANCE_DIR/certificate.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gf2n import GF2n, semaev_s3, semaev_s4  # noqa: E402


def write_params(inst: dict, path: Path) -> None:
    lines = [f"n {inst['n']}", f"modulus {inst['field']['modulus_hex']}", f"a {inst['curve']['a']}",
             f"m {inst['m']}", f"l {inst['l']}", f"xr {inst['target']['R_x_hex']}"]
    lines += [f"basis {h}" for h in inst["V"]["basis_rref_hex"]]
    lines += [f"pcheck {h}" for h in inst["V_parity_check_rows_hex"]]
    path.write_text("\n".join(lines) + "\n")


def python_reference(inst: dict) -> dict:
    F = GF2n(inst["n"], int(inst["field"]["modulus_hex"], 16))
    V = [int(h, 16) for h in inst["V"]["basis_rref_hex"]]
    xr = int(inst["target"]["R_x_hex"], 16)
    m, l = inst["m"], inst["l"]
    elems = []
    for c in range(1 << l):
        v = 0
        for k in range(l):
            if (c >> k) & 1:
                v ^= V[k]
        elems.append(v)
    t0 = time.monotonic()
    count = 0
    first = None
    if m == 2:
        for i, x1 in enumerate(elems):
            for x2 in elems[i:]:
                if semaev_s3(F, x1, x2, xr) == 0:
                    count += 1
                    first = first or [hex(x1), hex(x2)]
    else:
        for i, x1 in enumerate(elems):
            for j in range(i, len(elems)):
                x2 = elems[j]
                for k in range(j, len(elems)):
                    if semaev_s4(F, x1, x2, elems[k], xr) == 0:
                        count += 1
                        first = first or [hex(x1), hex(x2), hex(elems[k])]
    return {"tool": "certify.py python_reference (direct evaluation of S_{m+1} over unordered tuples of V)",
            "verdict": "SAT" if count else "UNSAT", "n_zero_tuples_unordered": count, "first": first,
            "elapsed_s": round(time.monotonic() - t0, 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instance_dir")
    ap.add_argument("--enum-bin", default=str(HERE / "bin" / "pdp_enum"))
    ap.add_argument("--python-reference", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    d = Path(a.instance_dir)
    inst = json.loads((d / "instance.json").read_text())
    params = d / "enum_params.txt"
    write_params(inst, params)
    argv = [a.enum_bin, str(params)]
    if a.limit is not None:
        argv += ["--limit", str(a.limit)]
    t0 = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True)
    wall = time.monotonic() - t0
    cert = {"schema": "EXP-FROB-30006a.certificate.v1", "argv": argv, "returncode": p.returncode,
            "stderr": p.stderr[-2000:], "wall_s": round(wall, 3),
            "enum_bin_sha256": hashlib.sha256(Path(a.enum_bin).read_bytes()).hexdigest(),
            "enum_source_sha256": hashlib.sha256((HERE / "pdp_enum.c").read_bytes()).hexdigest(),
            "params_sha256": hashlib.sha256(params.read_bytes()).hexdigest(),
            "instance_anf_sha256": inst["anf"]["sha256"], "result": None, "python_reference": None}
    if p.returncode == 0:
        cert["result"] = json.loads(p.stdout)
    else:
        cert["stdout"] = p.stdout[-2000:]
    if a.python_reference:
        cert["python_reference"] = python_reference(inst)
        if cert["result"]:
            cert["reference_agrees"] = cert["python_reference"]["verdict"] == cert["result"]["verdict"]
    cert["certificate_kind"] = ("exhaustive_enumeration_unsat" if cert["result"] and cert["result"]["verdict"] == "UNSAT" and cert["result"]["complete"]
                                else ("decomposition_witness" if cert["result"] and cert["result"]["verdict"] == "SAT" else "none"))
    (d / "certificate.json").write_text(json.dumps(cert, indent=1))
    print(json.dumps({k: cert.get(k) for k in ("returncode", "wall_s", "certificate_kind", "reference_agrees")}),
          (cert["result"] or {}).get("verdict"), (cert["result"] or {}).get("n_algebraic_witnesses"))
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
