#!/usr/bin/env python3
"""Independent Legendre/norm point recount and rational-Euclidean screen checker.

This module never imports the producer or original pilot. Fp2 characters are
Legendre symbols of norms in Fp, rather than producer square-multiplicity tables.
--self-test checks small software fixtures and never executes the fixed panel.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import platform
import resource
import sys
import time

import sympy as sp

EXP = "EXP-ECDLP-da4ba3"
PRIMES = [11, 13, 17, 19, 23, 31, 43, 59]


def legendre(x, p):
    z = pow(x % p, (p-1)//2, p)
    return -1 if z == p-1 else z


def recount(p, a, b, degree, reverse=False):
    """Count D via (1+chi(f(x)))(1+chi(h(x))) at each x, plus 2."""
    d = None if degree == 1 else next(z for z in range(1, p) if legendre(z, p) == -1)
    if degree not in (1, 2):
        raise ValueError("unsupported extension degree")
    q = p**degree
    ne, nh, nd = 1, 1, 2
    indices = range(q-1, -1, -1) if reverse else range(q)
    for index in indices:
        if degree == 1:
            f, h = (index**3+7) % p, ((index-a)*(index-b)) % p
            ce, ch, cz = legendre(f, p), legendre(f*h, p), legendre(h, p)
        else:
            # Index is v*p+u: a different traversal/encoding implementation.
            u, v = index % p, index // p
            fu = (u**3+3*d*u*v*v+7) % p
            fv = (3*u*u*v+d*v**3) % p
            hu = ((u-a)*(u-b)+d*v*v) % p
            hv = ((2*u-a-b)*v) % p
            nf = (fu*fu-d*fv*fv) % p
            n_h = (hu*hu-d*hv*hv) % p
            ce, ch, cz = legendre(nf, p), legendre(nf*n_h, p), legendre(n_h, p)
        ne += 1+ce
        nh += 1+ch
        nd += (1+ce)*(1+cz)
    return {"degree": degree, "q": q, "nonresidue": d, "N_E": ne, "N_H": nh, "N_D": nd,
            "field_polynomial": [1, 0, -d] if d is not None else None,
            "infinity_points": {"E": 1, "H": 1, "D": 2}}


def trim(poly):
    poly = [Fraction(c) for c in poly]
    while len(poly) > 1 and poly[0] == 0:
        poly.pop(0)
    return poly


def multiply(a, b):
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] += x*y
    return trim(out)


def rational_gcd(a, b):
    a, b = trim(a), trim(b)
    while any(b):
        remainder = a[:]
        while any(remainder) and len(remainder) >= len(b):
            scale = remainder[0]/b[0]
            for j, coefficient in enumerate(b):
                remainder[j] -= scale*coefficient
            remainder = trim(remainder)
        a, b = b, remainder
    return [int(c/a[0]) if (c/a[0]).denominator == 1 else str(c/a[0]) for c in a]


def is_reciprocal(poly, p):
    degree = len(poly)-1
    if degree <= 0 or degree % 2 or poly[0] != 1:
        return False
    # Reverse coefficients through the functional equation.
    return [Fraction(c)*Fraction(p)**(degree//2-i) for i, c in enumerate(poly)] == list(reversed(poly))


def classification(p, fe, fh):
    if not is_reciprocal(fe, p) or not is_reciprocal(fh, p):
        return "malformed"
    return "shared" if len(rational_gcd(fe, fh)) > 1 else "coprime"


def expected_catalogue(p):
    pairs, events = [], []
    rank = 0
    for a in range(p):
        for b in range(a+1, p):
            bad = [x for x in [a, b] if (x*x*x+7) % p == 0]
            event = {"event": "candidate_pair", "p": p, "a": a, "b": b,
                     "lexicographic_rank": rank, "accepted": len(bad) == 0,
                     "reason": "f_root_at_cover_branch" if bad else "eligible",
                     "f_root_branches": bad}
            rank += 1
            if not bad:
                event.update(panel="primary" if len(pairs) < 8 else "companion", eligible_index=len(pairs))
                pairs.append((a, b))
            events.append(event)
            if len(pairs) == 16:
                return pairs, events
    raise ValueError("fixed catalogue has fewer than 16 eligible pairs")


def synthetic(p):
    return [{"id": name, "p": p, "F_E": [1, -1, p], "F_H": h, "expected": expected}
            for name, h, expected in [
                ("shared", [1, -2, 2*p+1, -2*p, p*p], "shared"),
                ("coprime", [1, 0, 2*p, 0, p*p], "coprime"),
                ("sign_malformed_reciprocal", [1, -2, 2*p+1, 2*p, p*p], "malformed")]]


def verify_cell(cell, check):
    p, a, b = (cell[k] for k in ("p", "a", "b"))
    observed, backwards = cell["counts"], cell["reverse_counts"]
    check(len(observed) == 2 and len(backwards) == 2, "both field degrees in both enumeration arms")
    checked = []
    for degree in (1, 2):
        reference = recount(p, a, b, degree)
        reverse_reference = recount(p, a, b, degree, True)
        checked.append(reference)
        check(reference == reverse_reference, f"independent reverse recount degree={degree}")
        for arm, rows in (("forward", observed), ("reverse", backwards)):
            r = rows[degree-1]
            check(all(r.get(k) == value for k, value in reference.items()),
                  f"independent recount {arm} degree={degree}")
            check(r["N_D"] == r["N_E"]+r["N_H"]-r["q"]-1, f"decomposition identity {arm} degree={degree}")
            check(r.get("operation_vector") == {"field_additions": 3*p**degree,
                  "field_multiplications": 5*p**degree, "square_table_lookups": 4*p**degree,
                  "affine_x_visits": p**degree}, f"operation accounting {arm} degree={degree}")
    te, th = p+1-checked[0]["N_E"], p+1-checked[0]["N_H"]
    se, sh = p*p+1-checked[1]["N_E"], p*p+1-checked[1]["N_H"]
    check(se == te*te-2*p, "elliptic second trace")
    check((th*th-sh) % 2 == 0, "integral genus-two reciprocal coefficient")
    fe, fh = [1, -te, p], [1, -th, (th*th-sh)//2, -p*th, p*p]
    for arm in ("screen", "reverse_screen"):
        s = cell[arm]
        expected = {"F_E": fe, "F_H": fh, "gcd_over_Q": rational_gcd(fe, fh),
                    "gcd_over_Q_degree": len(rational_gcd(fe, fh))-1,
                    "F_D_candidate": multiply(fe, fh), "reciprocal_valid": True,
                    "classification": classification(p, fe, fh), "t_E": te, "s_E2": se,
                    "t_H": th, "s_H2": sh, "E_order": checked[0]["N_E"], "H_order": sum(fh),
                    "source_type": "supersingular_control" if te % p == 0 else "ordinary_toy",
                    "full_genus3_frobenius_independent_check": False}
        check(all(s.get(k) == v for k, v in expected.items()), f"rational polynomial screen {arm}")
        product = [1]
        for factor in s["F_H_irreducible_factors"]:
            coeff, mult = factor["coefficients"], factor["multiplicity"]
            check(isinstance(mult, int) and mult > 0, f"factor multiplicity {arm}")
            check(sp.Poly.from_list(coeff, sp.Symbol("T"), domain=sp.QQ).is_irreducible, f"rational factor irreducibility {arm}")
            for _ in range(mult):
                product = multiply(product, coeff)
        check(product == fh, f"factor reconstruction {arm}")
    check(cell.get("aa_exact") is True and observed == backwards and cell["screen"] == cell["reverse_screen"], "producer transported-enumeration A/A")
    check(cell.get("sample_role") == ("calibration" if (p, a, b) == (43, 0, 1) else "holdout"), "calibration/holdout provenance")
    check(cell.get("subgroup_uid") is None and cell.get("factor_base_uid") is None, "no unconstructed subgroup or factor base")


def verify(result, config_bytes):
    failures, checks = [], Counter()
    def check(condition, label):
        checks[label] += 1
        if not condition:
            failures.append({"check": label, "cell": current[0]})
    current = ["envelope"]
    cfg = json.loads(config_bytes)
    check(cfg.get("experiment_id") == EXP and cfg.get("primes") == PRIMES and cfg.get("covers_per_prime") == 8
          and cfg.get("extension_degrees") == [1, 2] and cfg.get("f_coefficients_descending") == [1, 0, 0, 7], "frozen config")
    check(result.get("schema") == "prym-geometry-result/v2" and result.get("experiment_id") == EXP, "result identity")
    check(result.get("config_sha256") == sha256(config_bytes).hexdigest(), "config hash")
    check(result.get("complete") is True and result.get("errors") == [], "complete census without producer errors")
    check(result.get("measurement_scope") == "point_counts_Fp_Fp2_only" and result.get("full_genus3_frobenius_independent_check") is False
          and result.get("jacobian_maps_checked") is False, "bounded verification scope")
    expected, inspected = {"primary": [], "companion": []}, []
    for p in PRIMES:
        pairs, events = expected_catalogue(p)
        inspected.extend(events)
        for index, (a, b) in enumerate(pairs):
            expected["primary" if index < 8 else "companion"].append((p, a, b))
    check(result.get("candidate_pairs") == inspected, "complete candidate/reject stream")
    rows_checked = 0
    for panel in ("primary", "companion"):
        rows = result.get(f"{panel}_rows", [])
        check([(r.get("p"), r.get("a"), r.get("b")) for r in rows] == expected[panel], f"exact {panel} fixed panel")
        for cell in rows:
            current[0] = {k: cell.get(k) for k in ("p", "a", "b", "panel")}
            try:
                check(cell.get("panel") == panel, "panel label")
                verify_cell(cell, check)
                rows_checked += 1
            except Exception as exc:
                failures.append({"check": "cell checker exception", "cell": current[0], "detail": f"{type(exc).__name__}: {exc}"})
    controls = result.get("synthetic_controls", [])
    current[0] = "synthetic controls"
    supplied = [s for p in PRIMES for s in synthetic(p)]
    check([{k: c.get(k) for k in ("id", "p", "F_E", "F_H", "expected")} for c in controls] == supplied, "exact supplied synthetic controls")
    for c in controls:
        try:
            s, p, fe, fh = c["observed"], c["p"], c["F_E"], c["F_H"]
            check(s.get("classification") == c["expected"] == classification(p, fe, fh), f"synthetic classification {p}/{c['id']}")
            check(s.get("gcd_over_Q") == rational_gcd(fe, fh) and s.get("gcd_over_Q_degree") == len(rational_gcd(fe, fh))-1,
                  f"synthetic rational gcd {p}/{c['id']}")
            check(s.get("reciprocal_valid") == (is_reciprocal(fe, p) and is_reciprocal(fh, p)), f"synthetic reciprocity {p}/{c['id']}")
        except Exception as exc:
            failures.append({"check": "synthetic checker exception", "detail": f"{type(exc).__name__}: {exc}"})
    return {"schema": "prym-geometry-verification/v2", "experiment_id": EXP,
            "status": "passed" if not failures else "failed", "independent_recount": True,
            "arithmetic_method": "Euler/Legendre over Fp; norm-to-Fp characters over Fp2; rational Euclidean gcd",
            "producer_imported": False, "rows_checked": rows_checked, "primary_expected": 64, "companion_expected": 64,
            "synthetic_expected": 24, "checks": dict(checks), "failed_checks": failures,
            "full_genus3_frobenius_independent_check": False, "jacobian_maps_checked": False,
            "execution_authority_granted": False}


def render_reports(directory, raw, verification):
    """Render recorded values only. A human must inspect PDF before archive."""
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing, Line, String
    from reportlab.pdfgen import canvas
    from xml.sax.saxutils import escape
    points = []
    for panel in ("primary", "companion"):
        for p in PRIMES:
            selected = [r for r in raw.get(f"{panel}_rows", []) if r["p"] == p]
            points.append({"p": p, "panel": panel, "n": len(selected),
                           "shared_count": sum(r["screen"]["gcd_over_Q_degree"] > 0 for r in selected)})
    source = {"run_id": directory.name, "source": "raw-result.json", "metric": "count of nonzero rational gcd degree",
              "uncertainty": "exact finite census; no sampling interval", "points": points}
    write_json(directory/"graph-source.json", source)
    drawing = Drawing(520, 220)
    drawing.add(String(8, 204, f"{directory.name}: recorded overlap counts; actual n shown", fontSize=9))
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="300" viewBox="0 0 520 220">',
           '<rect width="520" height="220" fill="white"/>',
           f'<text x="8" y="16" font-size="9">{escape(directory.name)}: recorded overlap counts; actual n shown</text>']
    colors = {"primary": "#2456a6", "companion": "#bd5125"}
    for i, point in enumerate(points):
        x, height = 28+(i % 8)*60+(16 if point["panel"] == "companion" else 0), point["shared_count"]*16
        color = colors[point["panel"]]
        from reportlab.lib.colors import HexColor
        drawing.add(Line(x, 40, x, 40+height, strokeColor=HexColor(color), strokeWidth=10))
        drawing.add(String(x-4, 25, str(point["p"]), fontSize=7))
        drawing.add(String(x-7, 16, f"n={point['n']}", fontSize=6))
        drawing.add(String(x-4, 46+height, str(point["shared_count"]), fontSize=7))
        svg.append(f'<line x1="{x}" y1="180" x2="{x}" y2="{180-height}" stroke="{color}" stroke-width="10"/>')
        svg.append(f'<text x="{x-4}" y="195" font-size="7">{point["p"]}</text><text x="{x-7}" y="204" font-size="6">n={point["n"]}</text><text x="{x-4}" y="{174-height}" font-size="7">{point["shared_count"]}</text>')
    drawing.add(String(8, 8, "p on x axis; overlap count 0..8; blue=primary, orange=companion", fontSize=8))
    svg.append('<text x="8" y="212" font-size="8">p; overlap count 0..8; blue=primary, orange=companion; exact census</text></svg>')
    (directory/"graph.svg").write_text("\n".join(svg)+"\n")
    text = (f"# {EXP} / {directory.name}\n\nObservations only; no scientific verdict or ECDLP claim.\n\n"
            f"Independent check: {verification['status']}; rows checked: {verification['rows_checked']}; "
            f"failed checks: {len(verification['failed_checks'])}.\n\n"
            f"Producer wall seconds (measured): {raw.get('wall_seconds')}; CPU seconds (measured): {raw.get('cpu_seconds')}; "
            f"producer peak RSS bytes (measured): {raw.get('peak_rss_bytes')}.\n\n"
            "The exact primary 64 cells, next-64 structural companions, forward/reverse counts, candidate rejects, "
            "synthetic controls and operation vectors are in raw-result.json. Checker costs are separate in verification.json. "
            "Source revision, command, dependencies, seeds and field definitions are in manifest.yaml and environment.json.\n\n"
            "Fp/Fp2 certify two D traces only. F_D_candidate is inferred from geometry; no complete independent genus-three "
            "Frobenius verification, Jacobian map, subgroup action or recovery. Previously seen F43 (0,1) is calibration.\n\n"
            "![Exact recorded gcd overlaps](graph.svg)\n\nPDF inspection is required before archiving; it is not asserted by this renderer.\n")
    (directory/"report.md").write_text(text)
    pdf = canvas.Canvas(str(directory/"report.pdf"), pagesize=(612, 792))
    lines = [f"{EXP} / {directory.name}", "Observations only; no scientific verdict or ECDLP claim.",
             f"Independent check: {verification['status']}; rows={verification['rows_checked']}; failures={len(verification['failed_checks'])}",
             "Inputs, commands, versions, resources: manifest.yaml / environment.json.",
             "Exact records: raw-result.json; independent recount: verification.json.",
             "Both fixed panels and both enumeration orders; synthetic screen controls.",
             "Fp/Fp2 give two D traces; F_D_candidate is inferred from geometry.",
             "No independently complete genus-three Frobenius polynomial or maps.",
             "No subgroup action, ECDLP recovery, speedup or security conclusion.",
             "F43 (0,1) is calibration. No canonical research graph changes.",
             "Human PDF inspection is required before archive."]
    for i, line in enumerate(lines):
        pdf.setFont("Helvetica", 10)
        pdf.drawString(36, 752-20*i, line)
    renderPDF.draw(drawing, pdf, 40, 260)
    pdf.save()


def write_json(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write("\n")


def self_test():
    # Exhaustive brute solutions for p=5 validates the independent norm formula.
    for degree in (1, 2):
        p, a, b, d = 5, 0, 1, 2
        elems = [(u, v) for u in range(p) for v in range(p if degree == 2 else 1)]
        def mul(x, y):
            return ((x[0]*y[0]+d*x[1]*y[1]) % p, (x[0]*y[1]+x[1]*y[0]) % p)
        ne, nh, nd = 1, 1, 2
        for x in elems:
            cube = mul(mul(x, x), x)
            f = ((cube[0]+7) % p, cube[1])
            h = mul(((x[0]-a) % p, x[1]), ((x[0]-b) % p, x[1]))
            y_roots = sum(mul(y, y) == f for y in elems)
            z_roots = sum(mul(z, z) == h for z in elems)
            ne += y_roots
            nd += y_roots*z_roots
            nh += sum(mul(y, y) == mul(f, h) for y in elems)
        counted = recount(p, a, b, degree)
        assert [counted[k] for k in ("N_E", "N_H", "N_D")] == [ne, nh, nd]
        assert counted == recount(p, a, b, degree, True)
    for c in synthetic(5):
        assert classification(5, c["F_E"], c["F_H"]) == c["expected"]
    assert rational_gcd([1, -1, 5], [1, -2, 11, -10, 25]) == [1, -1, 5]
    assert rational_gcd([1, -1, 5], [1, 0, 10, 0, 25]) == [1]
    assert not is_reciprocal([1, -2, 11, 10, 25], 5)
    return {"software_checks": "passed", "scientific_panel_executed": False,
            "fixtures": "exhaustive F5/F25 roots; forward/reverse; shared/coprime/malformed polynomial controls"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps(self_test(), sort_keys=True))
        return 0
    if args.config is None or args.run_dir is None:
        parser.error("--config and --run-dir are required for independent verification")
    directory = args.run_dir
    start, cpu = time.perf_counter(), time.process_time()
    raw_path = directory/"raw-result.json"
    raw = json.loads(raw_path.read_text())
    verification = verify(raw, args.config.read_bytes())
    verification.update(raw_result_sha256=sha256(raw_path.read_bytes()).hexdigest(),
                        checker_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                        finished_at=datetime.now(timezone.utc).isoformat(),
                        wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu,
                        peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == "darwin" else 1024),
                        python=platform.python_version())
    write_json(directory/"verification.json", verification)
    with (directory/"events.jsonl").open("a") as stream:
        for failed in verification["failed_checks"]:
            stream.write(json.dumps({"event": "independent_check_failure", **failed}, sort_keys=True)+"\n")
        stream.write(json.dumps({"event": "independent_checker_terminal", "status": verification["status"]}, sort_keys=True)+"\n")
    render_reports(directory, raw, verification)
    print(json.dumps({"status": verification["status"], "rows_checked": verification["rows_checked"],
                      "failed_checks": len(verification["failed_checks"])}))
    return 0 if verification["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
