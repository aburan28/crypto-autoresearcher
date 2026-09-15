"""V1 step (2), second half: evaluate the CryptoMiniSat model recorded in the
run log against the UPSTREAM CNF-XOR file the row actually read, with the
validator's own parser.

CNF-XOR semantics (WDSat README "Input forms / CNF-XOR" and the standard
CryptoMiniSat convention): a plain clause is a disjunction of literals; a line
beginning `x` is an XOR clause that is satisfied when the XOR of its literals
is TRUE, a negated literal contributing (1 xor value).
"""
from __future__ import annotations

import json
import os
import re

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
OUT = os.path.dirname(os.path.abspath(__file__))


def read_model(logpath):
    lits = []
    for ln in open(logpath):
        if ln.startswith("v "):
            lits += [int(t) for t in ln.split()[1:]]
    assert lits[-1] == 0
    lits = lits[:-1]
    n = max(abs(v) for v in lits)
    assign = [None] * (n + 1)
    for v in lits:
        assign[abs(v)] = 1 if v > 0 else 0
    return assign, n


def read_cnfxor(path):
    ors, xors = [], []
    nvars = nclauses = None
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln.startswith("c"):
            continue
        if ln.startswith("p "):
            p = ln.split()
            nvars, nclauses = int(p[2]), int(p[3])
            continue
        if ln.startswith("x"):
            toks = [int(t) for t in ln[1:].split()]
            assert toks[-1] == 0
            xors.append(toks[:-1])
        else:
            toks = [int(t) for t in ln.split()]
            assert toks[-1] == 0
            ors.append(toks[:-1])
    return nvars, nclauses, ors, xors


def main():
    inst = "n19l6-19-U"
    assign, nmodel = read_model(os.path.join(RUN, f"logs/cms_xor_{inst}.out"))
    nvars, nclauses, ors, xors = read_cnfxor(os.path.join(BENCH, f"X{inst}.dimacs"))

    def lit(v):
        a = assign[abs(v)]
        return a if v > 0 else 1 - a

    bad_or = sum(1 for c in ors if not any(lit(v) for v in c))
    bad_xor_true = sum(1 for c in xors if (sum(lit(v) for v in c) % 2) != 1)
    bad_xor_false = sum(1 for c in xors if (sum(lit(v) for v in c) % 2) != 0)

    core = "".join(str(assign[i]) for i in range(1, 19))
    out = {
        "instance": inst,
        "dimacs_header": {"nvars": nvars, "nclauses": nclauses},
        "model_vars_recorded": nmodel,
        "n_or_clauses": len(ors),
        "n_xor_clauses": len(xors),
        "unsatisfied_or_clauses": bad_or,
        "unsatisfied_xor_under_xor_eq_1": bad_xor_true,
        "unsatisfied_xor_under_xor_eq_0": bad_xor_false,
        "first_18_model_bits": core,
        "first_18_as_three_l6_chunks": [core[0:6], core[6:12], core[12:18]],
        "recorded_assignment_core_bits": None,
    }
    for ln in open(os.path.join(RUN, "results.jsonl")):
        r = json.loads(ln)
        if r.get("instance") == inst and r.get("engine") == "cryptominisat5":
            out["recorded_assignment_core_bits"] = r.get("assignment_core_bits")
            out["recorded_x_bits"] = r["verification"]["x_bits"]
    with open(os.path.join(OUT, "v1_cms.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
