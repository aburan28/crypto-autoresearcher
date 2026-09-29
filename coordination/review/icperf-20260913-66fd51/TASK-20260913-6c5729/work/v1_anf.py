"""V1 steps (2)-(4): parse the shipped WDSat ANF myself, evaluate every
equation at the recorded WDSat assignment, decode the first 3l bits under both
bit-order conventions, evaluate f3, and compute the four traces.

ANF format taken from inputs/TRIMOSKA-WDSAT-2024/upstream/README.md
("Input forms / ANF"): each line is `x <terms> 0`; a term is a bare variable
index (degree 1), `T` (the constant), or `.d v1..vd` (a degree-d monomial).
Both possible satisfaction conventions (XOR of terms = 1, XOR of terms = 0)
are evaluated, so the file itself decides which one holds.
"""

from __future__ import annotations

import json
import os

from valgf import GF2n, BinaryCurve, INF, f3_summation, parse_info

BENCH = "/workspace/inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks"
RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
OUT = os.path.dirname(os.path.abspath(__file__))


def parse_anf(path):
    eqs = []
    nvars = neqs = None
    with open(path) as fh:
        for raw in fh:
            ln = raw.strip()
            if not ln:
                continue
            if ln.startswith("p "):
                parts = ln.split()
                nvars, neqs = int(parts[2]), int(parts[3])
                continue
            toks = ln.split()
            assert toks[0] == "x", toks[0]
            assert toks[-1] == "0", toks[-1]
            toks = toks[1:-1]
            terms = []
            i = 0
            while i < len(toks):
                t = toks[i]
                if t == "T":
                    terms.append(("T",))
                    i += 1
                elif t.startswith("."):
                    d = int(t[1:])
                    mono = tuple(int(v) for v in toks[i + 1:i + 1 + d])
                    assert len(mono) == d
                    terms.append(mono)
                    i += 1 + d
                else:
                    terms.append((int(t),))
                    i += 1
            eqs.append(terms)
    return {"nvars": nvars, "neqs_declared": neqs, "equations": eqs}


def eval_eq(terms, assign):
    v = 0
    for t in terms:
        if t == ("T",):
            v ^= 1
        else:
            p = 1
            for idx in t:
                p &= assign[idx]
            v ^= p
    return v


def evaluate(path, assignment_str):
    anf = parse_anf(path)
    n = anf["nvars"]
    assert len(assignment_str) == n, (path, len(assignment_str), n)
    assign = [0] * (n + 1)
    for i, c in enumerate(assignment_str):
        assign[i + 1] = 1 if c == "1" else 0
    vals = [eval_eq(t, assign) for t in anf["equations"]]
    return {
        "nvars": n,
        "n_equations": len(anf["equations"]),
        "n_equations_declared": anf["neqs_declared"],
        "n_eq_xor_equals_1": sum(vals),
        "n_eq_xor_equals_0": len(vals) - sum(vals),
        "max_degree": max(max(len(t) for t in eq) if eq else 0 for eq in anf["equations"]),
        "vals": vals,
    }


def row_lookup(instance, engine, config):
    for ln in open(os.path.join(RUN, "results.jsonl")):
        r = json.loads(ln)
        if (r.get("instance") == instance and r.get("engine") == engine
                and r.get("config") == config):
            return r
    return None


def main():
    out = {}

    # --- calibration: an S instance whose answer the run verified ----------
    calib = []
    for inst in ("n19l6-1-S", "n17l6-1-S", "n15l5-1-S", "n19l6-2-S"):
        row = row_lookup(inst, "wdsat", "default")
        anfpath = os.path.join(BENCH, f"X{inst}.anf")
        ev = evaluate(anfpath, row["assignment"])
        info = parse_info(os.path.join(BENCH, f"INFO{inst}.dimacs"))
        l = info["l"]
        core = row["assignment"][: 3 * l]
        calib.append({
            "instance": inst,
            "assignment_len": len(row["assignment"]),
            "n_eq": ev["n_equations"],
            "n_eq_xor_equals_1": ev["n_eq_xor_equals_1"],
            "n_eq_xor_equals_0": ev["n_eq_xor_equals_0"],
            "max_monomial_degree": ev["max_degree"],
            "first_3l_bits": [core[i * l:(i + 1) * l] for i in range(3)],
            "shipped_certificate": info["cert_raw"],
            "verification_recorded": row.get("verification"),
        })
    out["calibration_S_instances"] = calib

    # --- the target: n19l6-19-U -------------------------------------------
    inst = "n19l6-19-U"
    info = parse_info(os.path.join(BENCH, f"INFO{inst}.dimacs"))
    n, l = info["n"], info["l"]
    F = GF2n(n, info["modulus_bits"])
    E = BinaryCurve(F, 1, 1)
    anfpath = os.path.join(BENCH, f"X{inst}.anf")

    per_config = []
    for cfg in ("default", "core_order", "symmetry", "gauss_elim"):
        row = row_lookup(inst, "wdsat", cfg)
        ev = evaluate(anfpath, row["assignment"])
        per_config.append({
            "config": cfg,
            "assignment": row["assignment"],
            "assignment_len": len(row["assignment"]),
            "n_equations": ev["n_equations"],
            "n_eq_xor_equals_1": ev["n_eq_xor_equals_1"],
            "n_eq_xor_equals_0": ev["n_eq_xor_equals_0"],
            "unsatisfied_under_xor_eq_1": ev["n_eq_xor_equals_0"],
            "unsatisfied_under_xor_eq_0": ev["n_eq_xor_equals_1"],
            "recorded_x_bits": row["verification"]["x_bits"],
            "recorded_why": row["verification"]["why"],
        })
    out["wdsat_rows_n19l6_19_U"] = per_config

    # --- decode the first 3l bits under both conventions -------------------
    assignment = per_config[0]["assignment"]
    core_bits = [assignment[i * l:(i + 1) * l] for i in range(3)]
    xr_lsb = F.from_bits_lsb_first(info["xr_bits"])
    xr_msb = F.from_bits_msb_first(info["xr_bits"])
    conv_table = []
    for convname, conv, xr in (("lsb_first", F.from_bits_lsb_first, xr_lsb),
                               ("msb_first", F.from_bits_msb_first, xr_msb)):
        xs = [conv(b) for b in core_bits]
        f3 = f3_summation(F, xs[0], xs[1], xs[2], xr)
        conv_table.append({
            "convention": convname,
            "core_bits": core_bits,
            "x_hex": [hex(v) for v in xs],
            "xr_hex": hex(xr),
            "f3_hex": hex(f3),
            "f3_is_zero": f3 == 0,
            "x_on_curve": [bool(E.is_x_coord(v)) for v in xs],
            "xr_on_curve": bool(E.is_x_coord(xr)),
            "trace_x": [F.trace(F.add(F.add(v, 1), F.inv(F.mul(v, v)))) if v else 0 for v in xs],
            "trace_xr": F.trace(F.add(F.add(xr, 1), F.inv(F.mul(xr, xr)))) if xr else 0,
            "x_in_subspace_V": [bool(v < (1 << l)) for v in xs],
        })
    out["convention_table_n19l6_19_U"] = conv_table

    # --- is it a twist decomposition? -------------------------------------
    # The quadratic twist of y^2+xy=x^3+a x^2+b is y^2+xy=x^3+(a+g)x^2+b for
    # any g with Tr(g)=1; with a=1 and n odd, Tr(1)=1, so the twist is
    # y^2+xy = x^3 + b (a'=0).  x is a twist x-coordinate iff
    # Tr(x + a' + b/x^2) = 0, i.e. exactly the complement of the E test.
    tw = BinaryCurve(F, 0, 1)
    best = conv_table[0]
    xs = [F.from_bits_lsb_first(b) for b in core_bits]
    twist_info = {
        "twist_curve": "y^2 + x*y = x^3 + 1  (a'=0, b=1); Tr(1)=1 for odd n so a'=a+1 is a valid twist",
        "x_on_twist_lsb": [bool(tw.is_x_coord(v)) for v in xs],
        "xr_on_twist_lsb": bool(tw.is_x_coord(xr_lsb)),
        "x_on_twist_msb": [bool(tw.is_x_coord(F.from_bits_msb_first(b))) for b in core_bits],
        "xr_on_twist_msb": bool(tw.is_x_coord(xr_msb)),
    }
    # If all four are twist x-coordinates, check the decomposition on the twist.
    for convname, conv, xr in (("lsb_first", F.from_bits_lsb_first, xr_lsb),
                               ("msb_first", F.from_bits_msb_first, xr_msb)):
        pts = [tw.points_with_x(conv(b)) for b in core_bits]
        if any(len(p) == 0 for p in pts) or not tw.is_x_coord(xr):
            twist_info[f"decomposition_on_twist_{convname}"] = "not all four on the twist"
            continue
        hits = []
        for i, P1 in enumerate(pts[0]):
            for j, P2 in enumerate(pts[1]):
                for k, P3 in enumerate(pts[2]):
                    S = tw.add(tw.add(P1, P2), P3)
                    if S is not INF and S[0] == xr:
                        hits.append((i, j, k))
        twist_info[f"decomposition_on_twist_{convname}"] = {
            "combinations_tried": 8, "matches": len(hits), "match_indices": hits}
    out["twist_analysis"] = twist_info

    # --- exhaustive check: is ANY (x1,x2,x3) in V^3 an E-decomposition of
    #     this x_R?  l=6 -> 64^3 = 262144 triples, trivial. --------------
    V = list(range(1 << l))
    onE = [v for v in V if E.is_x_coord(v)]
    ontw = [v for v in V if tw.is_x_coord(v)]
    out["subspace_stats"] = {
        "l": l, "|V|": len(V),
        "x_in_V_on_E": len(onE), "x_in_V_on_twist": len(ontw),
        "xr_lsb_on_E": bool(E.is_x_coord(xr_lsb)),
        "xr_lsb_on_twist": bool(tw.is_x_coord(xr_lsb)),
    }

    def all_decompositions(curve, xr):
        pts = {}
        for v in V:
            p = curve.points_with_x(v)
            if p:
                pts[v] = p
        sols = []
        keys = sorted(pts)
        for a in keys:
            for b in keys:
                if b < a:
                    continue
                for c in keys:
                    if c < b:
                        continue
                    for P1 in pts[a]:
                        for P2 in pts[b]:
                            for P3 in pts[c]:
                                S = curve.add(curve.add(P1, P2), P3)
                                if S is not INF and S[0] == xr:
                                    sols.append((hex(a), hex(b), hex(c)))
                                    break
                            else:
                                continue
                            break
                        else:
                            continue
                        break
        return sorted(set(sols))

    out["exhaustive_E_decompositions_of_xr_lsb"] = all_decompositions(E, xr_lsb)
    out["exhaustive_twist_decompositions_of_xr_lsb"] = all_decompositions(tw, xr_lsb)

    with open(os.path.join(OUT, "v1_anf.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)

    # ---- console ----------------------------------------------------------
    print("== calibration (S instances, run-verified answers) ==")
    for c in calib:
        print(f"  {c['instance']}: |assign|={c['assignment_len']} eqs={c['n_eq']} "
              f"XOR=1 on {c['n_eq_xor_equals_1']}, XOR=0 on {c['n_eq_xor_equals_0']}; "
              f"core={c['first_3l_bits']} shipped={c['shipped_certificate']}")
    print("== n19l6-19-U WDSat rows ==")
    for c in per_config:
        print(f"  {c['config']}: |assign|={c['assignment_len']} eqs={c['n_equations']} "
              f"XOR=1 on {c['n_eq_xor_equals_1']}, XOR=0 on {c['n_eq_xor_equals_0']}")
    print("== two-convention table ==")
    for c in conv_table:
        print(f"  {c['convention']}: x={c['x_hex']} xr={c['xr_hex']} f3={c['f3_hex']} "
              f"zero={c['f3_is_zero']} onE={c['x_on_curve']} xr_onE={c['xr_on_curve']} "
              f"traces={c['trace_x']} tr(xr)={c['trace_xr']}")
    print("== twist ==")
    print(" ", json.dumps(twist_info, sort_keys=True))
    print("== subspace ==", json.dumps(out["subspace_stats"], sort_keys=True))
    print("E-decompositions of x_R in V^3:", len(out["exhaustive_E_decompositions_of_xr_lsb"]),
          out["exhaustive_E_decompositions_of_xr_lsb"][:10])
    print("twist-decompositions of x_R in V^3:",
          len(out["exhaustive_twist_decompositions_of_xr_lsb"]),
          out["exhaustive_twist_decompositions_of_xr_lsb"][:10])


if __name__ == "__main__":
    main()
