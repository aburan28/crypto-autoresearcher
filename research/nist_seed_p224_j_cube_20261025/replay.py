#!/usr/bin/env python3
"""Replay the archived j/3-division observation; requires Python 3 and PARI/GP."""
import argparse
import copy
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check_input(row):
    p, b, n = (row[k] for k in ("p", "b", "n"))
    if not all(type(x) is int for x in (p, b, n)) or not (0 < b < p and n > 3):
        raise ValueError("invalid integer parameters")
    identity = row["identity"]
    if (int(identity["field"]["characteristic"]),
        int(identity["curve"]["a6"]),
        int(identity["curve"]["subgroup_order"])) != (p, b, n):
        raise ValueError("exact curve identity differs from p,b,n")
    if int(identity["curve"]["a4"]) % p != p - 3:
        raise ValueError("expected fixed a=-3 model")
    state = (row["timestamp"] << 16) | 0x330E
    seed = bytearray()
    for i in range(20 * row["ordinal"]):
        state = (0x5DEECE66D * state + 11) & ((1 << 48) - 1)
        if i >= 20 * (row["ordinal"] - 1):
            seed.append(state >> 40)
    if seed.hex() != row["seed"]:
        raise ValueError("seed does not match timestamp and ordinal")
    bits = p.bit_length()
    v = (bits - 1) // 160
    w = bits - 160 * v - 1
    c = int.from_bytes(hashlib.sha1(seed).digest(), "big") & ((1 << w) - 1)
    z = int.from_bytes(seed, "big")
    for i in range(1, v + 1):
        part = ((z + i) % (1 << 160)).to_bytes(20, "big")
        c = (c << 160) | int.from_bytes(hashlib.sha1(part).digest(), "big")
    if (c * b * b + 27) % p:
        raise ValueError("seed-derived coefficient relation failed")
    delta = -16 * (-108 + 27 * b * b) % p
    if not delta:
        raise ValueError("singular curve")
    j = 6912 * pow(4 - b * b, -1, p) % p
    if j != 6912 * c * pow(4 * c + 27, -1, p) % p:
        raise ValueError("j formulas disagree")
    return j


def replay(inputs, gp):
    names = [r["name"] for r in inputs]
    if len(inputs) != 21 or len(set(names)) != 21:
        raise ValueError("expected the complete 21-curve comparison")
    if sum(r["published"] for r in inputs) != 10:
        raise ValueError("expected ten published controls")
    js = [check_input(row) for row in inputs]
    commands = []
    for row in inputs:
        p, b, n = (row[k] for k in ("p", "b", "n"))
        commands.append(
            f"E=ellinit([-3,{b}],{p});v=elldivpol(E,3);f=factor(v);"
            "print(lift(E.j));"
            "print(vector(matsize(f)[1],i,[poldegree(f[i,1]),f[i,2]]));"
            f"print([isprime({p}),isprime({n}),"
            "prod(i=1,matsize(f)[1],f[i,1]^f[i,2])*pollead(v)==v]);"
        )
    result = subprocess.run([gp, "-q", "-f"], input="\n".join(commands) + "\n",
                            text=True, capture_output=True, timeout=120)
    if result.returncode or "***" in result.stderr:
        raise RuntimeError(f"PARI failed: {result.stderr}")
    lines = result.stdout.splitlines()
    if len(lines) != 3 * len(inputs):
        raise ValueError("incomplete PARI output")
    observations = []
    for i, (row, j) in enumerate(zip(inputs, js)):
        native_j = int(lines[3 * i])
        factors = json.loads(lines[3 * i + 1])
        if json.loads(lines[3 * i + 2]) != [1, 1, 1]:
            raise ValueError("prime or factor-product check failed")
        if native_j != j or sum(d * e for d, e in factors) != 4:
            raise ValueError("native invariant or division degree mismatch")
        if any(e != 1 for d, e in factors):
            raise ValueError("non-squarefree division polynomial")
        observations.append(dict(
            name=row["name"], curve_uid=row["identity"]["curve_uid"],
            published=row["published"], field_bits=row["p"].bit_length(),
            ordinal=row["ordinal"], j=j,
            j_cube=pow(j, (row["p"] - 1) // math.gcd(3, row["p"] - 1), row["p"]) == 1,
            three_division_factor_degrees=sorted(d for d, e in factors)))
    return observations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gp", default=shutil.which("gp"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.gp:
        parser.error("PARI/GP is required; install it or provide --gp")
    inputs = json.loads((HERE / "inputs.json").read_text())["curves"]
    observed = replay(inputs, args.gp)
    expected = json.loads((HERE / "observations.json").read_text())["curves"]
    if observed != expected:
        raise ValueError("replay differs from the archived observations")
    # Falsification controls: exact coefficient and seed binding must reject tampering.
    for key in ("b", "ordinal"):
        bad = copy.deepcopy(inputs[0])
        bad[key] += 1
        try:
            check_input(bad)
        except ValueError:
            continue
        raise ValueError(f"tampering control was accepted: {key}")
    receipt = dict(status="pass", curves=21, published=10, omitted=11,
                   exact_input_and_seed_checks=21, native_j_checks=21,
                   division_factor_product_checks=21, tampering_controls=2,
                   historical_selector_identified=False)
    text = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
