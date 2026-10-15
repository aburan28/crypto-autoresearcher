"""Bounded pairing/paired-element instrument. Importing performs no experiment.

Only run_experiment executes the frozen F43 study. The helper routines also admit
small, non-study software fixtures. Exact arithmetic is deliberately unoptimized;
counts are primitive calls/attempts, not a single claimed work or complexity unit.
"""
from __future__ import annotations

import argparse
from collections import Counter as Bag
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import resource
import sys
import time

try:
    from tools.lattice_ic_core import (Counter, Curve, Field, encode_point,
                                      factorize, is_prime, rank_mod,
                                      select_prime_subgroup, write_artifacts)
except ModuleNotFoundError:
    from lattice_ic_core import (Counter, Curve, Field, encode_point, factorize,
                                 is_prime, rank_mod, select_prime_subgroup,
                                 write_artifacts)


FIXTURE = {"p": 43, "A": 1, "B": 0, "target_A": -4, "target_B": 0,
           "r": 11, "quadratic": [1, 0], "basis_change_quadratic": [2, -2],
           "isogeny_degree": 2, "targets": "all a=0..r-1; Q=aP",
           "box_ab": 16, "smooth_prime_bound": 13,
           "large_k_gate": {"q": 2, "r": 101, "maximum_extension_degree": 2},
           "special_ideal": {"ell": 5, "s": 2, "basis": [[5, 0], [2, 1]],
                             "primitive_pair_subpanel": True}}
PANELS = ("admission", "pairings", "field_bases", "baselines", "relations",
          "descent", "special_ideal", "controls")
CONTROLS = ("identity", "degenerate", "annihilator", "large_k", "relabeling",
            "power_permutation", "norm_only", "missing_unit", "bad_projection")
CASE_STATUSES = ("measured", "zero_yield", "inadmissible", "bounded_instrument_stop", "invalid")


def resource_usage(scope):
    """Actual process high-water RSS; never interpreted as incremental arm RSS."""
    native = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    _require(sys.platform.startswith("linux") or sys.platform == "darwin",
             "ru_maxrss units unsupported on this platform")
    scale = 1 if sys.platform == "darwin" else 1024
    return {"peak_rss_bytes": int(native*scale), "native_peak_rss": native,
            "native_unit": "bytes" if scale == 1 else "KiB", "platform": sys.platform,
            "scope": scope+"; RUSAGE_SELF lifetime high-water includes imports and prior phases; excludes child processes; not incremental or per-arm"}


def _check_resource_usage(record):
    _require(record["platform"].startswith("linux") or record["platform"] == "darwin", "unsupported RSS units")
    scale = 1 if record["platform"] == "darwin" else 1024
    _require(record["native_unit"] == ("bytes" if scale == 1 else "KiB")
             and isinstance(record["peak_rss_bytes"], int) and record["peak_rss_bytes"] > 0
             and record["peak_rss_bytes"] == int(record["native_peak_rss"]*scale)
             and "RUSAGE_SELF lifetime high-water" in record["scope"], "bad resource measurement")


def _arm_cost(counter, wall, cpu, dependencies):
    return {"wall_seconds": time.monotonic()-wall, "cpu_seconds": time.process_time()-cpu,
            "counter": counter.snapshot(),
            "cache_policy": "fresh Field/Curve/Counter per arm (Curve only for pairing); no cache inherited from admission or another arm; base pairing warms only this arm's deterministic point cache, then all targets use it",
            "dependencies": dependencies,
            "scope": "one cold arm, including its setup and all declared targets; no heterogeneous count total; component phases are sequential and leaf-exclusive"}


def pairing_arm(p, quadratic, A, B, r, P, S, arm):
    """Fresh, separately measured direct/transported/reused-power arms.

    Public admission witnesses are inputs; their construction is a separately
    named cold-start dependency. Reused powers pay for their own direct Miller
    images; they never borrow the direct arm's populated cache or outputs.
    """
    _require(arm in ("direct", "transported", "reused_power"), "unknown pairing arm")
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("setup"):
        f = Field(p, quadratic, counter=counter)
        c = Curve(f, A, B)
        left, right = _point(c, P), _point(c, S)
        _require(c.mul(r, left) is None and c.mul(r, right) is None, "arm torsion")
        group = [c.mul(a, left) for a in range(r)]
        eval_curve, eval_left, eval_right, eval_group = c, left, right, group
    if arm == "transported":
        with counter.phase("map_construction_and_evaluation"):
            eval_curve = Curve(f, -4*A, 0)
            eval_left, eval_right = isogeny(c, eval_curve, left), isogeny(c, eval_curve, right)
            eval_group = [isogeny(c, eval_curve, point) for point in group]
    with counter.phase("base_pairing"):
        base, base_certificate = weil_pairing(eval_curve, eval_left, eval_right, r)
    images, certificates = [], []
    with counter.phase("target_pairings"):
        for point in eval_group:
            value, certificate = weil_pairing(eval_curve, point, eval_right, r)
            images.append(value)
            certificates.append(certificate)
    direct_dependency = None
    if arm == "reused_power":
        direct_dependency = {"g": list(base), "images": [list(h) for h in images],
                             "g_certificate": base_certificate, "certificates": certificates}
        with counter.phase("degree_two_powers"):
            base = f.pow(base, 2)
            images = [f.pow(value, 2) for value in images]
    return {"arm": arm, "P": encode_point(c, left), "S": encode_point(c, right),
            "G": [encode_point(c, point) for point in group],
            "evaluation_P": encode_point(eval_curve, eval_left),
            "evaluation_S": encode_point(eval_curve, eval_right),
            "evaluation_G": [encode_point(eval_curve, point) for point in eval_group],
            "g": list(base), "images": [list(value) for value in images],
            "g_certificate": base_certificate, "certificates": certificates,
            "direct_dependency": direct_dependency,
            "cost": _arm_cost(counter, wall, cpu, ["admission public P,S,r; charged separately in every cold-start component list"])}


def baseline_arm(p, quadratic, g, targets, r, method):
    """Fresh field/counter for each basis and each DLP baseline algorithm."""
    _require(method in ("exhaustive", "bsgs"), "unknown DLP baseline")
    counter, wall, cpu = Counter(), time.monotonic(), time.process_time()
    with counter.phase("setup"):
        f = Field(p, quadratic, counter=counter)
        base, images = f.coerce(g), [f.coerce(h) for h in targets]
        _require(base != f.one and f.pow(base, r) == f.one, "baseline base order")
    records = []
    with counter.phase("solve"):
        for image in images:
            if method == "exhaustive":
                logs, details = exhaustive_dlp(f, base, image, r), None
            else:
                logs, details = bsgs_dlp(f, base, image, r)
            records.append({"h": list(image), "logs": logs, "details": details})
    return {"method": method, "records": records,
            "cost": _arm_cost(counter, wall, cpu, ["actual pairing images supplied as DLP input; their acquisition and any basis conversion are separate cold-start components"])}


def _check_arm_cost(cost, expected_phases):
    _require(cost["wall_seconds"] >= 0 and cost["cpu_seconds"] >= 0
             and cost["dependencies"] and "fresh Field/Curve/Counter" in cost["cache_policy"], "bad cold arm scope")
    counter = cost["counter"]
    _require(set(counter["phases"]) == set(expected_phases), "missing/extra arm cost components")
    counts = Bag()
    for phase in counter["phases"].values():
        _require(phase["calls"] == 1 and 0 <= phase["wall_seconds"] <= cost["wall_seconds"]
                 and 0 <= phase["cpu_seconds"] <= cost["cpu_seconds"], "bad arm phase timing")
        _require(all(isinstance(n, int) and n >= 0 for n in phase["operations"].values()), "bad arm operation counts")
        counts.update(phase["operations"])
    _require(dict(counts) == counter["operations"], "arm work not exactly leaf allocated")
    _require(sum(x["wall_seconds"] for x in counter["phases"].values()) <= cost["wall_seconds"]
             and sum(x["cpu_seconds"] for x in counter["phases"].values()) <= cost["cpu_seconds"], "arm phases overlap")


def verify_pairing_arm(record, p, quadratic, A, B, r, P, S):
    """Replay arm certificates without trusting cross-arm equality or booleans."""
    f = Field(p, quadratic)
    c = Curve(f, A, B)
    left, right = _point(c, P), _point(c, S)
    group = [c.mul(a, left) for a in range(r)]
    arm = record["arm"]
    _require(arm in ("direct", "transported", "reused_power"), "unknown arm")
    _require(record["P"] == P and record["S"] == S
             and record["G"] == [encode_point(c, point) for point in group], "arm source witnesses")
    phases = {"setup", "base_pairing", "target_pairings"}
    ec, ep, es, eg = c, left, right, group
    if arm == "transported":
        phases.add("map_construction_and_evaluation")
        ec = Curve(f, -4*A, 0)
        ep, es = isogeny(c, ec, left), isogeny(c, ec, right)
        eg = [isogeny(c, ec, point) for point in group]
    _require(record["evaluation_P"] == encode_point(ec, ep)
             and record["evaluation_S"] == encode_point(ec, es)
             and record["evaluation_G"] == [encode_point(ec, point) for point in eg], "arm evaluated map witnesses")
    if arm == "reused_power":
        phases.add("degree_two_powers")
        raw = record["direct_dependency"]
        _require(raw is not None and raw["g_certificate"] == record["g_certificate"]
                 and raw["certificates"] == record["certificates"], "missing direct power dependency")
    else:
        _require(record["direct_dependency"] is None, "spurious dependency")
        raw = record
    _require(len(raw["images"]) == len(raw["certificates"]) == r, "arm target coverage")
    verify_weil(ec, ep, es, r, raw["g"], raw["g_certificate"])
    _require(f.coerce(raw["g"]) != f.one, "degenerate arm base")
    for point, image, certificate in zip(eg, raw["images"], raw["certificates"]):
        verify_weil(ec, point, es, r, image, certificate)
    if arm == "reused_power":
        _require(record["g"] == list(f.pow(raw["g"], 2))
                 and record["images"] == [list(f.pow(image, 2)) for image in raw["images"]], "unpaid or bad reused powers")
    _check_arm_cost(record["cost"], phases)
    counts = record["cost"]["counter"]["operations"]
    attempts = len(raw["g_certificate"]["attempts"])+sum(len(x["attempts"]) for x in raw["certificates"])
    _require(counts.get("weil.shift_attempt") == attempts and counts.get("curve.enumeration") == 1,
             "arm shift/cold enumeration costs inconsistent with witnesses")
    if arm == "reused_power":
        _require(record["cost"]["counter"]["phases"]["degree_two_powers"]["operations"].get("field.pow") == r+1,
                 "missing power cost")


def verify_baseline_arm(record, p, quadratic, g, images, r):
    _check_arm_cost(record["cost"], {"setup", "solve"})
    f, method = Field(p, quadratic), record["method"]
    _require(method in ("exhaustive", "bsgs") and len(record["records"]) == len(images), "baseline arm coverage")
    for image, witness in zip(images, record["records"]):
        hits = [a for a in range(r) if f.pow(g, a) == f.coerce(image)]
        _require(witness["h"] == list(image) and witness["logs"] == hits, "baseline arm log witness")
        if method == "exhaustive":
            _require(witness["details"] is None, "spurious exhaustive BSGS witness")
        else:
            m = math.isqrt(r-1)+1
            _require(witness["details"] == {"m": m, "baby_entries": m, "giant_steps": m+1}, "BSGS arm work witness")
    counts = record["cost"]["counter"]["operations"]
    if method == "exhaustive":
        _require(counts.get("baseline.exhaustive_comparison") == len(images)*r, "unpaid exhaustive comparisons")
    else:
        m = math.isqrt(r-1)+1
        _require(counts.get("baseline.bsgs_baby") == len(images)*m
                 and counts.get("baseline.bsgs_giant") == len(images)*(m+1), "unpaid BSGS work")


def _require(test, message):
    if not test:
        raise ValueError(message)


def _point(c, encoded):
    if encoded is None:
        return None
    result = tuple(c.field.coerce(x) for x in encoded)
    _require(c.is_on_curve(result) and encoded == encode_point(c, result),
             "off-curve or noncanonical point certificate")
    return result


def _line_quotient(c, left, right, at):
    """Miller g_left,right(at), including vertical and identity branches."""
    f = c.field
    if at is None:
        raise ZeroDivisionError("evaluation at O")
    if left is None or right is None:
        return f.one
    x, y = at
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and f.add(y1, y2) == f.zero:
        return f.sub(x, x1)
    slope = (f.mul(f.add(f.mul(3, f.mul(x1, x1)), c.A), f.inv(f.mul(2, y1)))
             if left == right else f.mul(f.sub(y2, y1), f.inv(f.sub(x2, x1))))
    line = f.sub(f.sub(y, y1), f.mul(slope, f.sub(x, x1)))
    summed = c.add(left, right)
    return line if summed is None else f.mul(line, f.inv(f.sub(x, summed[0])))


def miller(c, point, n, at):
    """Actual binary Miller recurrence, with poles exposed rather than patched."""
    _require(n > 0, "positive Miller integer required")
    _require(c.is_on_curve(point) and c.is_on_curve(at), "Miller point admission")
    c.counter.inc("miller.call")
    if point is None:
        return c.field.one
    f, running, value = c.field, point, c.field.one
    for bit in bin(n)[3:]:
        c.counter.inc("miller.double_step")
        value = f.mul(f.mul(value, value), _line_quotient(c, running, running, at))
        running = c.add(running, running)
        if bit == "1":
            c.counter.inc("miller.add_step")
            value = f.mul(value, _line_quotient(c, running, point, at))
            running = c.add(running, point)
    return value


def _weil_at_shift(c, p, q, r, shift):
    f = c.field
    places = (c.add(q, shift), shift, c.neg(shift), c.add(p, c.neg(shift)))
    values = [miller(c, p, r, places[0]), miller(c, p, r, places[1]),
              miller(c, q, r, places[2]), miller(c, q, r, places[3])]
    if any(x == f.zero for x in values):
        raise ZeroDivisionError("Miller zero in disjoint-divisor evaluation")
    value = f.mul(f.mul(values[0], f.inv(values[1])),
                  f.mul(values[2], f.inv(values[3])))
    return value, values


def weil_pairing(c, p, q, r):
    """Disjoint divisors: fP(Q+T)/fP(T) * fQ(-T)/fQ(P-T).

    T is the first successful O-first lex point. Every failed evaluation is
    charged and retained; no random auxiliary point or inferred normalization.
    """
    _require(is_prime(r) and c.mul(r, p) is None and c.mul(r, q) is None,
             "Weil inputs must be r-torsion")
    if p is None or q is None:
        return c.field.one, {"identity_argument": True, "attempts": []}
    attempts = []
    for shift in c.points():
        c.counter.inc("weil.shift_attempt")
        try:
            value, values = _weil_at_shift(c, p, q, r, shift)
        except ZeroDivisionError as error:
            attempts.append({"T": encode_point(c, shift), "pole": str(error)})
            continue
        attempts.append({"T": encode_point(c, shift), "values": [list(x) for x in values]})
        _require(c.field.pow(value, r) == c.field.one, "Weil value outside mu_r")
        return value, {"identity_argument": False, "attempts": attempts}
    raise ArithmeticError("no disjoint Miller evaluation shift exists in enumerated field")


def verify_weil(c, p, q, r, image, certificate):
    """Check the recorded Miller evaluations and every earlier pole explicitly."""
    f = c.field
    original_image, image = image, f.coerce(image)
    _require(list(original_image) == list(image), "noncanonical pairing image")
    _require(c.mul(r, p) is None and c.mul(r, q) is None, "bad torsion input")
    if p is None or q is None:
        _require(certificate == {"identity_argument": True, "attempts": []}
                 and image == f.one, "bad identity pairing")
        return
    attempts = certificate["attempts"]
    _require(certificate["identity_argument"] is False and attempts, "missing shifts")
    shifts = c.points()
    _require(len(attempts) <= len(shifts), "excess shift attempts")
    for i, attempt in enumerate(attempts):
        shift = _point(c, attempt["T"])
        _require(shift == shifts[i], "auxiliary shifts not canonical exhaustive prefix")
        try:
            value, values = _weil_at_shift(c, p, q, r, shift)
        except ZeroDivisionError as error:
            _require(i < len(attempts)-1 and attempt == {
                "T": encode_point(c, shift), "pole": str(error)}, "bad pole witness")
        else:
            _require(i == len(attempts)-1 and attempt == {
                "T": encode_point(c, shift), "values": [list(x) for x in values]}
                and value == image and f.pow(value, r) == f.one, "bad Miller witness")


def isogeny(c, target, point):
    """Degree-two map for y²=x³+a*x, with kernel O,(0,0)."""
    _require(c.B == c.field.zero, "degree-two map requires B=0")
    if point is None or point[0] == c.field.zero:
        return None
    f, (x, y) = c.field, point
    image = (f.add(x, f.mul(c.A, f.inv(x))),
             f.mul(y, f.sub(1, f.mul(c.A, f.inv(f.mul(x, x))))))
    _require(target.is_on_curve(image), "isogeny image off target")
    c.counter.inc("isogeny.affine_evaluation")
    return image


def convert_basis(element, source, target, direction="u_to_v"):
    _require(source.p == target.p and source.degree == target.degree == 2,
             "quadratic basis conversion required")
    a, b = source.coerce(element)
    source.counter.inc("basis.conversion")
    return target.coerce((a-b, b) if direction == "u_to_v" else (a+b, b))


def exhaustive_dlp(f, g, h, r):
    value, hits = f.one, []
    for a in range(r):
        f.counter.inc("baseline.exhaustive_comparison")
        if value == h:
            hits.append(a)
        value = f.mul(value, g)
    return hits


def bsgs_dlp(f, g, h, r):
    m, value, babies = math.isqrt(r-1)+1, f.one, {}
    for j in range(m):
        f.counter.inc("baseline.bsgs_baby")
        babies.setdefault(value, j)
        value = f.mul(value, g)
    stride, value = f.pow(g, -m), h
    hits = []
    for i in range(m+1):
        f.counter.inc("baseline.bsgs_giant")
        if value in babies:
            a = i*m+babies[value]
            if a < r and f.pow(g, a) == h:
                hits.append(a)
        value = f.mul(value, stride)
    return sorted(set(hits)), {"m": m, "baby_entries": len(babies), "giant_steps": m+1}


class QuadraticRing:
    """Z[z]/(z²+c1*z+c0), exact coefficient pairs and element division."""
    def __init__(self, c0, c1, name, counter=None):
        self.c0, self.c1, self.name = c0, c1, name
        self.counter = counter if counter is not None else Counter()

    def mul(self, x, y):
        self.counter.inc("ring.mul")
        a, b = x
        c, d = y
        return a*c-self.c0*b*d, a*d+b*c-self.c1*b*d

    def norm(self, x):
        self.counter.inc("ring.norm")
        a, b = x
        return a*a-self.c1*a*b+self.c0*b*b

    def divide(self, x, y):
        self.counter.inc("ring.exact_division_attempt")
        a, b = y
        norm = self.norm(y)
        if not norm:
            raise ZeroDivisionError("zero ring divisor")
        numerator = self.mul(x, (a-self.c1*b, -b))
        return tuple(v//norm for v in numerator) if all(v % norm == 0 for v in numerator) else None

    def evaluate(self, x, f, root):
        self.counter.inc("ring.field_evaluation")
        return f.add(x[0], f.mul(x[1], root))


def prime_generators(ring, bound, coefficient_bound):
    """All norm-ell elements in fixed box; inert integer generators separately."""
    generators, primes = [], [x for x in range(2, bound+1) if is_prime(x)]
    for a in range(-coefficient_bound, coefficient_bound+1):
        for b in range(-coefficient_bound, coefficient_bound+1):
            ring.counter.inc("ring.generator_candidate")
            norm = ring.norm((a, b))
            if norm in primes:
                generators.append({"element": [a, b], "norm": norm,
                                   "rational_prime": norm, "type": "norm_prime"})
    inert = []
    for ell in primes:
        roots = [x for x in range(ell) if (x*x+ring.c1*x+ring.c0) % ell == 0]
        ring.counter.inc("ring.inert_root_trial", ell)
        if not roots:
            generators.append({"element": [ell, 0], "norm": ell*ell,
                               "rational_prime": ell, "type": "inert_integer"})
            inert.append(ell)
    generators.sort(key=lambda g: (g["norm"], g["element"]))
    return generators, inert


def factor_element(ring, element, generators, units):
    _require(tuple(element) != (0, 0), "zero cannot be smoothly factored")
    remainder, factors = tuple(element), []
    for index, generator in enumerate(generators):
        exponent = 0
        while True:
            quotient = ring.divide(remainder, generator["element"])
            if quotient is None:
                break
            remainder, exponent = quotient, exponent+1
        if exponent:
            factors.append([index, exponent])
    accepted = remainder in [tuple(u) for u in units]
    return {"element": list(element), "norm": ring.norm(element), "factors": factors,
            "remainder": list(remainder), "unit": list(remainder) if accepted else None,
            "accepted": accepted}


def verify_factorization(ring, cert, generators, units, f=None, root=None, exponent=None):
    """Multiply actual elements, validate units and each projected factor."""
    element = tuple(cert["element"])
    _require(element != (0, 0) and cert["norm"] == ring.norm(element), "bad ring norm")
    _require(cert["accepted"] == (tuple(cert["remainder"]) in [tuple(u) for u in units]),
             "false factorization acceptance")
    _require(cert["unit"] == (cert["remainder"] if cert["accepted"] else None), "missing/bad unit")
    product, previous = tuple(cert["remainder"]), -1
    for index, power in cert["factors"]:
        _require(isinstance(power, int) and power > 0 and previous < index < len(generators),
                 "bad generator index/power/order")
        previous = index
        for _ in range(power):
            product = ring.mul(product, generators[index]["element"])
    _require(product == element, "ring ELEMENT identity failed")
    if f is not None:
        value = ring.evaluate(element, f, root)
        _require(cert["evaluation"] == list(value), "bad element evaluation")
        projected = None if value == f.zero else f.pow(value, exponent)
        _require(cert["projected"] == (None if projected is None else list(projected)),
                 "bad element projection")
        if cert["accepted"] and projected is not None:
            product = f.pow(ring.evaluate(cert["unit"], f, root), exponent)
            for index, power in cert["factors"]:
                image = f.pow(ring.evaluate(generators[index]["element"], f, root), exponent)
                _require(image == f.coerce(generators[index]["projected"]), "bad projected factor")
                product = f.mul(product, f.pow(image, power))
            _require(product == projected, "projected element identity failed")
    return True


def solve_relative(rows, n, r, counter=None):
    """Homogeneous rows plus column zero anchored to 1; never takes true logs."""
    if n == 0:
        return {"rank": 0, "augmented_rank": 0, "consistent": True,
                "unique": False, "solution": None, "pivots": []}
    matrix = [[x % r for x in row]+[0] for row in rows]
    matrix.append([1]+[0]*(n-1)+[1])
    pivot_row, pivots = 0, []
    for column in range(n):
        pivot = next((i for i in range(pivot_row, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        inverse = pow(matrix[pivot_row][column], -1, r)
        matrix[pivot_row] = [x*inverse % r for x in matrix[pivot_row]]
        for i in range(len(matrix)):
            if i == pivot_row:
                continue
            coefficient = matrix[i][column]
            matrix[i] = [(x-coefficient*y) % r for x, y in zip(matrix[i], matrix[pivot_row])]
            if counter:
                counter.inc("relations.modular_row_elimination")
        pivots.append(column)
        pivot_row += 1
    consistent = all(any(row[:n]) or row[-1] == 0 for row in matrix)
    unique = consistent and len(pivots) == n
    solution = [0]*n if unique else None
    if unique:
        for i, col in enumerate(pivots):
            solution[col] = matrix[i][-1]
    return {"rank": rank_mod(rows, r), "augmented_rank": len(pivots),
            "consistent": consistent, "unique": unique, "solution": solution,
            "pivots": pivots}


def _project_factorization(ring, cert, generators, units, f, root, exponent):
    value = ring.evaluate(cert["element"], f, root)
    cert["evaluation"] = list(value)
    cert["projected"] = None if value == f.zero else list(f.pow(value, exponent))
    verify_factorization(ring, cert, generators, units, f, root, exponent)


def _row_for_pair(pair, columns, fields, f, exponent):
    indices = {tuple(x): i for i, x in enumerate(columns)}
    row = [0]*len(columns)
    for sign, cert, data in zip((1, -1), pair["factorizations"], fields):
        ring, root, generators, units = data
        image = f.pow(ring.evaluate(cert["unit"], f, root), exponent)
        if image != f.one:
            row[indices[image]] += sign
        for index, power in cert["factors"]:
            image = tuple(generators[index]["projected"])
            if image != f.one:
                row[indices[image]] += sign*power
    return row


def paired_relations(f, r, box=16, prime_bound=13):
    """Actual paired elements; no pairing/DLP/planted scalar is an input."""
    _require(f.p == 43 and f.quadratic == (1, 0) and r == 11,
             "frozen paired-ring evaluation is specific to p43,r11")
    exponent, u = (f.order-1)//r, f.coerce((0, 1))
    fields, descriptions = [], []
    for c0, c1, name, coefficient_bound, root, units in (
            (1, 0, "Z[i]", 13, u, [[1, 0], [-1, 0], [0, 1], [0, -1]]),
            (3, -1, "Z[w]", 26, f.mul(f.add(u, 2), f.inv(4)), [[1, 0], [-1, 0]])):
        ring = QuadraticRing(c0, c1, name, f.counter)
        _require(f.add(f.add(f.mul(root, root), f.mul(c1, root)), c0) == f.zero,
                 "ring evaluation root invalid")
        generators, inert = prime_generators(ring, prime_bound, coefficient_bound)
        for generator in generators:
            value = ring.evaluate(generator["element"], f, root)
            _require(value != f.zero, "characteristic prime generator must be excluded")
            generator["projected"] = list(f.pow(value, exponent))
        fields.append((ring, root, generators, units))
        descriptions.append({"name": name, "polynomial": [c0, c1, 1],
                             "coefficient_bound": coefficient_bound, "root": list(root),
                             "units": units, "generators": generators, "inert": inert})
    pairs, images = [], set()
    # Preserve columns not reached by the bounded relation search: deleting
    # them could hide rank deficiency. Units are explicit potential columns.
    for ring, root, generators, units in fields:
        images.update(tuple(g["projected"]) for g in generators
                      if tuple(g["projected"]) != f.one)
        images.update(image for unit in units
                      if (image := f.pow(ring.evaluate(unit, f, root), exponent)) != f.one)
    for a in range(-box, box+1):
        for b in range(-box, box+1):
            if a == b == 0:
                continue
            f.counter.inc("relations.box_candidate")
            certs = []
            for element, (ring, root, generators, units) in zip(((a, -b), (a+2*b, -4*b)), fields):
                cert = factor_element(ring, element, generators, units)
                _project_factorization(ring, cert, generators, units, f, root, exponent)
                cert["norm_smooth"] = all(p <= prime_bound for p in factorize(cert["norm"]))
                certs.append(cert)
            _require(certs[0]["evaluation"] == certs[1]["evaluation"], "paired evaluations disagree")
            accepted = all(c["accepted"] and c["projected"] is not None for c in certs)
            pair = {"ab": [a, b], "factorizations": certs, "accepted": accepted}
            pairs.append(pair)
    columns = [list(x) for x in sorted(images)]
    rows, pair_indices = [], []
    for i, pair in enumerate(pairs):
        if pair["accepted"]:
            rows.append(_row_for_pair(pair, columns, fields, f, exponent))
            pair_indices.append(i)
    solution = solve_relative(rows, len(columns), r, f.counter)
    return {"projection_exponent": exponent, "fields": descriptions, "pairs": pairs,
            "columns": columns, "rows": rows, "row_pair_indices": pair_indices,
            "solve": solution, "anchor": columns[0] if columns else None,
            "box": box, "prime_bound": prime_bound}


def individual_descent(f, r, relations, g, targets):
    """Entire fixed box searched separately per image, using smooth identities."""
    solution = relations["solve"]["solution"]
    columns = {tuple(x): i for i, x in enumerate(relations["columns"])}
    first = relations["fields"][0]
    ring = QuadraticRing(1, 0, "Z[i]", f.counter)
    descents = []
    for image in [g]+list(targets):
        matches = []
        for i, pair in enumerate(relations["pairs"]):
            f.counter.inc("descent.box_candidate")
            cert = pair["factorizations"][0]
            # A descent needs one ring identity, not a paired relation.
            if cert["accepted"] and cert["projected"] == list(image):
                matches.append(i)
        relative_log = None
        chosen = matches[0] if matches else None
        if chosen is not None and solution is not None:
            cert = relations["pairs"][chosen]["factorizations"][0]
            unit = f.pow(ring.evaluate(cert["unit"], f, f.coerce(first["root"])),
                         relations["projection_exponent"])
            value = 0 if unit == f.one else solution[columns[unit]]
            for index, power in cert["factors"]:
                projected = tuple(first["generators"][index]["projected"])
                if projected != f.one:
                    value += power*solution[columns[projected]]
            relative_log = value % r
        descents.append({"image": list(image), "matching_pair_indices": matches,
                         "chosen_pair_index": chosen, "relative_log": relative_log,
                         "candidates_tested": len(relations["pairs"])})
    denominator = descents[0]["relative_log"]
    recovered = []
    for image, descent in zip(targets, descents[1:]):
        if image == f.one:
            recovered.append({"scalar": 0, "status": "identity_log_zero", "verified": True})
        elif denominator is None or denominator == 0 or descent["relative_log"] is None:
            recovered.append({"scalar": None, "status": "incomplete_rank_or_descent", "verified": False})
        else:
            scalar = descent["relative_log"]*pow(denominator, -1, r) % r
            verified = f.pow(g, scalar) == image
            _require(verified, "relation recovery verification failed")
            recovered.append({"scalar": scalar, "status": "recovered", "verified": verified})
    return {"descents": descents, "recovered": recovered,
            "normalizing_log_g": denominator,
            "truth_log_input": False}


def special_ideal(box, counter):
    ring = QuadraticRing(1, 0, "Z[i]", counter)
    cells = []
    for a in range(-box, box+1):
        for b in range(-box, box+1):
            counter.inc("ideal.box_candidate")
            member = (a-2*b) % 5 == 0
            quotient = ring.divide((a, -b), (2, -1))
            _require(member == (quotient is not None), "good-root ideal membership disagreement")
            if member:
                _require(ring.norm((a, -b)) % 5 == 0, "ideal norm divisibility")
            cells.append({"ab": [a, b], "member": member, "primitive": math.gcd(a, b) == 1,
                          "basis_coordinates": [(a-2*b)//5, b] if member else None,
                          "norm": ring.norm((a, -b)),
                          "element_quotient": list(quotient) if quotient is not None else None})
    return {"ring": "Z[i]", "basis": [[5, 0], [2, 1]], "determinant": 5,
            "good_root": 2, "prime_element": [2, -1], "cells": cells,
            "members": sum(c["member"] for c in cells),
            "primitive_members": sum(c["member"] and c["primitive"] for c in cells)}


def _independent_prime_points(p, A, B):
    # Literal equation enumeration independent of core's square-root table.
    return [None]+[((x,), (y,)) for x in range(p) for y in range(p)
                   if (y*y-x*x*x-A*x-B) % p == 0]


def _case(panel, observables, certificates, inputs=None, status="measured", limits=None):
    _require(status in CASE_STATUSES, "case status outside shared schema")
    return {"id": panel, "panel": panel, "status": status,
            "inputs": inputs or {}, "observables": observables,
            "certificates": certificates, "work": {"allocation": panel}, "limits": limits or []}


def run_experiment(seed=1729):
    """Execute all frozen panels. Never called by the software test suite."""
    counter, cases = Counter(), []
    with counter.phase("shared_setup"):
        prime = Field(43, counter=counter)
        source, target = Curve(prime, 1, 0), Curve(prime, -4, 0)
        f = Field(43, (1, 0), counter=counter)
        c, cp = Curve(f, 1, 0), Curve(f, -4, 0)
    with counter.phase("admission"):
        source_points, target_points = source.points(), target.points()
        _require(source_points == _independent_prime_points(43, 1, 0), "source count oracle")
        _require(target_points == _independent_prime_points(43, -4, 0), "target count oracle")
        counter.inc("admission.independent_equation_trial", 2*43*43)
        admitted = select_prime_subgroup(source, r=11)
        _require(admitted["admitted"], "frozen subgroup admission failed")
        p = tuple(f.coerce(x[0]) for x in admitted["P"])
        u = f.coerce((0, 1))
        s = (f.neg(p[0]), f.mul(u, p[1]))
        gpoints = [c.mul(a, p) for a in range(11)]
        _require(c.is_on_curve(s) and c.mul(11, s) is None and s not in gpoints,
                 "distortion order/independence")
        images = [isogeny(source, target, point) for point in source_points]
        residuals = []
        for i, left in enumerate(source_points):
            for j, right in enumerate(source_points):
                counter.inc("admission.map_pair_test")
                if isogeny(source, target, source.add(left, right)) != target.add(images[i], images[j]):
                    residuals.append([i, j])
        _require(not residuals, "map homomorphism failure")
        admission_cert = {"source_points": [encode_point(source, x) for x in source_points],
                          "target_points": [encode_point(target, x) for x in target_points],
                          "source_order": len(source_points), "target_order": len(target_points),
                          "source_factorization": {str(k): v for k, v in factorize(len(source_points)).items()},
                          "target_factorization": {str(k): v for k, v in factorize(len(target_points)).items()},
                          "P": encode_point(c, p), "S": encode_point(c, s),
                          "G": [encode_point(c, x) for x in gpoints],
                          "map_images": [encode_point(target, x) for x in images],
                          "map_pair_tests": len(source_points)**2, "residuals": residuals,
                          "kernel": [encode_point(source, x) for x in source_points if isogeny(source, target, x) is None]}
        cases.append(_case("admission", {"admitted": True, "r": 11}, admission_cert))
    with counter.phase("pairings"):
        arms = {name: pairing_arm(43, (1, 0), 1, 0, 11,
                                 encode_point(c, p), encode_point(c, s), name)
                for name in ("direct", "transported", "reused_power")}
        direct, transported, reused = [arms[name] for name in ("direct", "transported", "reused_power")]
        g, gcert = f.coerce(direct["g"]), direct["g_certificate"]
        gp, gpcert = f.coerce(transported["g"]), transported["g_certificate"]
        _require(g != f.one and f.pow(g, 11) == f.one and gp == f.pow(g, 2), "nondegeneracy/covariance")
        targets, pair_records = [], []
        for a, q in enumerate(gpoints):
            h, hc = f.coerce(direct["images"][a]), direct["certificates"][a]
            qp = isogeny(c, cp, q)
            hp, hpc = f.coerce(transported["images"][a]), transported["certificates"][a]
            _require(h == f.pow(g, a) and hp == f.pow(gp, a) and hp == f.pow(h, 2), "target covariance")
            _require(reused["images"][a] == list(hp), "reused-power independent arm mismatch")
            targets.append(h)
            pair_records.append({"a": a, "Q": encode_point(c, q), "phiQ": encode_point(cp, qp),
                                 "h": list(h), "phi_h": list(hp), "h_certificate": hc,
                                 "phi_h_certificate": hpc, "reused_power": reused["images"][a],
                                 "zero_target": a == 0})
        cases.append(_case("pairings", {"nontrivial_target_images": sum(h != f.one for h in targets),
                                       "covariance_failures": 0},
                           {"g": list(g), "phi_g": list(gp), "g_certificate": gcert,
                            "phi_g_certificate": gpcert, "targets": pair_records, "arms": arms}))
    with counter.phase("basis_conversion"):
        vfield = Field(43, (2, -2), counter=counter)
        conversion = []
        for element in f.elements():
            converted = convert_basis(element, f, vfield)
            _require(convert_basis(converted, vfield, f, "v_to_u") == element, "basis roundtrip")
            conversion.append([list(element), list(converted)])
        vp, vs = [tuple(convert_basis(x, f, vfield) for x in point) for point in (p, s)]
        converted_g, converted_gp = convert_basis(g, f, vfield), convert_basis(gp, f, vfield)
        converted_targets = [convert_basis(h, f, vfield) for h in targets]
    with counter.phase("field_bases"):
        vc, vcp = Curve(vfield, 1, 0), Curve(vfield, -4, 0)
        vg, vgc = weil_pairing(vc, vp, vs, 11)
        vgp, vgpc = weil_pairing(vcp, isogeny(vc, vcp, vp), isogeny(vc, vcp, vs), 11)
        vtargets = []
        for q, h in zip(gpoints, targets):
            vq = None if q is None else tuple(convert_basis(x, f, vfield) for x in q)
            vh, vhc = weil_pairing(vc, vq, vs, 11)
            vphi_h, vphi_hc = weil_pairing(vcp, isogeny(vc, vcp, vq),
                                          isogeny(vc, vcp, vs), 11)
            _require(vh == convert_basis(h, f, vfield), "basis pairing disagreement")
            _require(vphi_h == vfield.pow(vh, 2), "basis target covariance")
            vtargets.append({"Q": encode_point(vc, vq), "h": list(vh), "certificate": vhc,
                             "phi_h": list(vphi_h), "phi_certificate": vphi_hc})
        _require(vg == convert_basis(g, f, vfield) and vgp == convert_basis(gp, f, vfield), "basis base disagreement")
        cases.append(_case("field_bases", {"converted_elements": len(conversion)},
                           {"conversion": conversion, "P": encode_point(vc, vp), "S": encode_point(vc, vs),
                            "g": list(vg), "phi_g": list(vgp), "g_certificate": vgc,
                            "phi_g_certificate": vgpc, "targets": vtargets,
                            "converted_pairing_inputs": {"g": list(converted_g), "phi_g": list(converted_gp),
                                                         "images": [list(h) for h in converted_targets]}}))
    baseline_records, baseline_arms = [], {}
    for label, quadratic, base, hs in (("u", (1, 0), g, targets),
                                      ("v", (2, -2), converted_g, converted_targets)):
        for method in ("exhaustive", "bsgs"):
            baseline_arms[label+"_"+method] = baseline_arm(43, quadratic, base, hs, 11, method)
        for a, h in enumerate(hs):
            exhaustive = baseline_arms[label+"_exhaustive"]["records"][a]["logs"]
            bsgs = baseline_arms[label+"_bsgs"]["records"][a]["logs"]
            witness = baseline_arms[label+"_bsgs"]["records"][a]["details"]
            _require(exhaustive == bsgs == [a], "DLP baseline discrepancy")
            baseline_records.append({"basis": label, "a": a, "h": list(h),
                                     "exhaustive": exhaustive, "bsgs": bsgs, "bsgs_work": witness})
    cases.append(_case("baselines", {"targets_per_basis": 11},
                       {"records": baseline_records, "arms": baseline_arms}))
    with counter.phase("relations"):
        relations = paired_relations(f, 11)
        cases.append(_case("relations", {"accepted": sum(p["accepted"] for p in relations["pairs"]),
                                        "columns": len(relations["columns"]), "solve": relations["solve"],
                                        "completeness": "unique_relative_logs" if relations["solve"]["unique"] else "incomplete_rank"}, relations,
                           limits=[] if relations["solve"]["unique"] else ["Incomplete modular rank; no relative-log completion supplied."]))
    with counter.phase("descent"):
        descent = individual_descent(f, 11, relations, g, targets)
        recovered_count = sum(x["status"] == "recovered" for x in descent["recovered"])
        complete = all(x["verified"] for x in descent["recovered"])
        cases.append(_case("descent", {"recovered_nonzero": recovered_count,
                                      "completeness": "complete_coverage" if complete else "incomplete_coverage"},
                           descent, status="measured" if recovered_count else "zero_yield",
                           limits=[] if complete else ["Incomplete rank or individual descent coverage; no baseline logs supplied."]))
    with counter.phase("special_ideal"):
        ideal = special_ideal(16, counter)
        cases.append(_case("special_ideal", {"members": ideal["members"], "primitive_members": ideal["primitive_members"]}, ideal))
    with counter.phase("controls"):
        controls = _make_controls(seed, c, cp, p, s, g, targets, gpoints, relations)
        cases.append(_case("controls", {"all_retained": True}, controls,
                           status="invalid" if controls["relabeling"]["compatible"] else "measured",
                           limits=["Unexpected compatible random labeling; control invalid."] if controls["relabeling"]["compatible"] else []))
    return {"schema_version": 1, "direction": "pairing", "seed": seed,
            "parameters": FIXTURE, "cases": cases,
            "checks": {"runtime_assertions": "completed; not independent review",
                       "random_relabeling_control_valid": not controls["relabeling"]["compatible"]},
            "limitations": ["Only frozen tiny-field scope; no NFS or ECDLP complexity claim.",
                            "Baseline truth and planted scalars never enter paired relation solving.",
                            "Incomplete rank and descent coverage remain explicit.",
                            "A successful internal checker is not independent review."],
            "work_accounting": {"counter": counter.snapshot(),
                                "resource": resource_usage("trial through result assembly before artifact serialization"),
                                "arm_accounting": {
                                    "pairing_cost_paths": {name: "cases.pairings.certificates.arms."+name+".cost" for name in arms},
                                    "baseline_cost_paths": {name: "cases.baselines.certificates.arms."+name+".cost" for name in baseline_arms},
                                    "basis_conversion_component": "counter.phases.basis_conversion (sequential with field_bases validation)",
                                    "cold_start_components": {name: ["counter.phases.shared_setup", "counter.phases.admission", "pairing_arms."+name+".cost"] for name in arms},
                                    "baseline_acquisition_components": {label+"_"+method: ["counter.phases.shared_setup", "counter.phases.admission", "pairing_arms.direct.cost"]+
                                        (["counter.phases.basis_conversion"] if label == "v" else [])+["baseline_arms."+label+"_"+method+".cost"]
                                        for label in ("u", "v") for method in ("exhaustive", "bsgs")},
                                    "interpretation": "Components are references, not summed totals. Each pairing cold start pays its own fresh setup plus the shared admission dependency. Reused-power arm pays its own direct base/target pairings before powers. Baseline solver arms start from obtained public images; acquisition and basis conversion are named separately. Parent pairings phase is an inclusive diagnostic and excludes child-arm primitive counts; never add it to child-arm times. No per-arm or end-to-end advantage claimed."},
                                "convention": "Named primitive calls and attempts; arithmetic layers overlap. Main counter excludes separately recorded fresh-arm counters. Phase allocations are leaf-exclusive, phase times inclusive; never sum layers or inclusive times.",
                                "unpriced_work": ["Python allocation/serialization and comparisons except explicitly counted comparisons", "checker replay wall/CPU and lifetime RSS reported separately on --check stdout, not trial counters"]},
            "instrument_scope": {"protocol": "prospective-protocols.json/pairing", "full_panels": list(PANELS),
                                 "scientific_claim": False, "development_only_without_supervisor": True}}


def _make_controls(seed, c, cp, p, s, g, targets, group, relations):
    f, r = c.field, 11
    identity, identity_cert = weil_pairing(c, p, s, r)
    degenerate, degenerate_cert = weil_pairing(c, p, p, r)
    _require(identity == g and degenerate == f.one, "identity/degenerate control")
    permutation = list(range(r))
    random.Random(seed).shuffle(permutation)
    # Retain the actual seeded permutation even if it accidentally respects the law.
    failures = [[a, b] for a in range(r) for b in range(r)
                if permutation[(a+b) % r] != (permutation[a]+permutation[b]) % r]
    c.counter.inc("controls.relabel_pair_test", r*r)
    identity_failures = []
    identity_images = list(group)
    for a in range(r):
        for b in range(r):
            c.counter.inc("controls.identity_pair_test")
            if identity_images[(a+b) % r] != c.add(identity_images[a], identity_images[b]):
                identity_failures.append([a, b])
    _require(not identity_failures and len(set(identity_images)) == r, "identity map control")
    order = next(k for k in range(1, 101) if pow(2, k, 101) == 1)
    killed = [encode_point(c, c.mul(r, q)) for q in group]
    power = [list(f.pow(h, 2)) for h in targets]
    _require(len(set(map(tuple, power))) == r, "power map not permutation")
    # Construct controlled corruptions of genuine exact element identities.
    ring = QuadraticRing(1, 0, "Z[i]", c.counter)
    d = relations["fields"][0]
    unit_example = factor_element(ring, (-1, 0), d["generators"], d["units"])
    bad_unit = json.loads(json.dumps(unit_example))
    bad_unit["unit"] = None
    rejected_unit = False
    try:
        verify_factorization(ring, bad_unit, d["generators"], d["units"])
    except ValueError:
        rejected_unit = True
    norm_only = {"element": [3, 4], "norm": 25, "factors": [],
                 "remainder": [1, 0], "unit": [1, 0], "accepted": True}
    rejected_norm = False
    try:
        verify_factorization(ring, norm_only, d["generators"], d["units"])
    except ValueError:
        rejected_norm = True
    chosen = next(p["factorizations"][0] for p in relations["pairs"]
                  if p["factorizations"][0]["accepted"] and p["factorizations"][0]["factors"]
                  and p["factorizations"][0]["projected"] is not None)
    corrupted = json.loads(json.dumps(d["generators"]))
    index = chosen["factors"][0][0]
    corrupted[index]["projected"] = list(f.mul(tuple(corrupted[index]["projected"]), g))
    rejected_projection = False
    try:
        verify_factorization(ring, chosen, corrupted, d["units"], f,
                             f.coerce(d["root"]), relations["projection_exponent"])
    except ValueError:
        rejected_projection = True
    _require(rejected_unit and rejected_norm and rejected_projection, "adverse identity control failed")
    return {"identity": {"image": list(identity), "certificate": identity_cert,
                          "map_images": [encode_point(c, q) for q in identity_images],
                          "failure_pairs": identity_failures, "injective": True},
            "degenerate": {"image": list(degenerate), "certificate": degenerate_cert, "accepted_nondegenerate": False},
            "annihilator": {"images": killed, "injective": False},
            "large_k": {"q": 2, "r": 101, "k": order, "maximum_extension_degree": 2,
                        "admitted_curve": False, "admitted": order <= 2},
            "relabeling": {"permutation": permutation, "failure_pairs": failures,
                           "compatible": not failures,
                           "status": "expected_incompatibility" if failures else "unexpected_compatible_labeling"},
            "power_permutation": {"images": power, "exponents": [(2*a) % r for a in range(r)],
                                  "histogram_before": [1]*r, "histogram_after": [1]*r,
                                  "selected_target_advantage_claimed": False},
            "norm_only": {"bad_certificate": norm_only, "rejected": rejected_norm},
            "missing_unit": {"valid_certificate": unit_example, "bad_certificate": bad_unit,
                             "rejected": rejected_unit},
            "bad_projection": {"factorization": chosen, "generator_index": index,
                               "corrupted_projected": corrupted[index]["projected"], "rejected": rejected_projection}}


def _verify_relations(relations, f, r):
    _require(relations["box"] == 16 and relations["prime_bound"] == 13
             and relations["projection_exponent"] == 168, "wrong relation schedule")
    fields = []
    for d, expected in zip(relations["fields"], ((1, 0, "Z[i]", 13), (3, -1, "Z[w]", 26))):
        c0, c1, name, bound = expected
        ring = QuadraticRing(c0, c1, name)
        _require(d["name"] == name and d["polynomial"] == [c0, c1, 1]
                 and d["coefficient_bound"] == bound, "wrong ring parameters")
        units = [[1, 0], [-1, 0], [0, 1], [0, -1]] if c0 == 1 else [[1, 0], [-1, 0]]
        _require(d["units"] == units, "wrong unit group")
        root = f.coerce(d["root"])
        expected_root = f.coerce((0, 1)) if c0 == 1 else f.mul(f.add((0, 1), 2), f.inv(4))
        _require(root == expected_root, "wrong explicit ring evaluation")
        expected_generators, inert = prime_generators(ring, 13, bound)
        _require(d["inert"] == inert and len(d["generators"]) == len(expected_generators), "generator coverage")
        for actual, gen in zip(d["generators"], expected_generators):
            projected = f.pow(ring.evaluate(gen["element"], f, root), 168)
            _require(actual == {**gen, "projected": list(projected)}, "bad prime-element generator")
            _require(ring.norm(gen["element"]) == gen["norm"] and gen["rational_prime"] != f.p,
                     "generator norm/characteristic")
        fields.append((ring, root, d["generators"], units))
    _require(len(relations["fields"]) == 2, "missing/extra rings")
    schedule = [[a, b] for a in range(-16, 17) for b in range(-16, 17) if a or b]
    _require([p["ab"] for p in relations["pairs"]] == schedule, "deleted/altered box cells")
    images, accepted = set(), []
    for ring, root, generators, units in fields:
        images.update(tuple(g["projected"]) for g in generators
                      if tuple(g["projected"]) != f.one)
        images.update(image for unit in units
                      if (image := f.pow(ring.evaluate(unit, f, root), 168)) != f.one)
    for i, pair in enumerate(relations["pairs"]):
        a, b = pair["ab"]
        _require(len(pair["factorizations"]) == 2, "missing ring certificate")
        for cert, element, (ring, root, generators, units) in zip(
                pair["factorizations"], ((a, -b), (a+2*b, -4*b)), fields):
            _require(cert["element"] == list(element), "altered paired element")
            verify_factorization(ring, cert, generators, units, f, root, 168)
            # Recheck deterministic division schedule as well as exact identity.
            expected = factor_element(ring, element, generators, units)
            _require(all(cert[k] == value for k, value in expected.items()), "noncanonical element division")
            _require(cert["norm_smooth"] == all(p <= 13 for p in factorize(cert["norm"])), "norm smooth flag")
        certs = pair["factorizations"]
        _require(certs[0]["evaluation"] == certs[1]["evaluation"], "paired field values differ")
        good = all(c["accepted"] and c["projected"] is not None for c in certs)
        _require(pair["accepted"] == good, "false paired acceptance")
        if good:
            accepted.append(i)
    _require(relations["columns"] == [list(x) for x in sorted(images)], "factorbase image deduplication")
    _require(relations["row_pair_indices"] == accepted, "relation coverage")
    expected_rows = [_row_for_pair(relations["pairs"][i], relations["columns"], fields, f, 168) for i in accepted]
    _require(relations["rows"] == expected_rows, "row not induced by exact identity")
    for row in expected_rows:
        product = f.one
        for image, power in zip(relations["columns"], row):
            product = f.mul(product, f.pow(image, power))
        _require(product == f.one, "homogeneous field relation fails")
    n, solution = len(relations["columns"]), relations["solve"]
    _require(solution == solve_relative(expected_rows, n, r), "incorrect modular rank/solve")
    _require(relations["anchor"] == (relations["columns"][0] if n else None), "anchor order")
    if solution["solution"] is not None:
        logs = solution["solution"]
        _require(logs[0] == 1 and all(sum(a*b for a, b in zip(row, logs)) % r == 0 for row in expected_rows),
                 "relative-log residual")
        _require(rank_mod(expected_rows+[[1]+[0]*(n-1)], r) == n, "unproved unique solution")
        anchor = tuple(relations["anchor"])
        _require(all(f.pow(anchor, value) == tuple(image) for image, value in zip(relations["columns"], logs)),
                 "relative logs fail independent exponentiation")


def check_result(result):
    """Substantive exact coverage/certificate validation; raises on corruption."""
    _require(result["schema_version"] == 1 and result["direction"] == "pairing", "wrong envelope")
    _require(result["parameters"] == FIXTURE, "wrong source parameters")
    _require([x["id"] for x in result["cases"]] == list(PANELS), "missing/extra/reordered panels")
    _require(result["instrument_scope"]["full_panels"] == list(PANELS)
             and result["instrument_scope"]["scientific_claim"] is False, "wrong instrument scope")
    for case in result["cases"]:
        _require(set(("id", "panel", "status", "inputs", "observables", "certificates", "work", "limits")) <= set(case)
                 and case["panel"] == case["id"] and case["work"] == {"allocation": case["id"]}
                 and case["status"] in CASE_STATUSES, "case schema/status")
    cases = {c["id"]: c for c in result["cases"]}
    _require(set(cases["controls"]["certificates"]) == set(CONTROLS), "deleted/extra controls")
    prime, f = Field(43), Field(43, (1, 0))
    source, target, c, cp = Curve(prime, 1, 0), Curve(prime, -4, 0), Curve(f, 1, 0), Curve(f, -4, 0)
    ad = cases["admission"]["certificates"]
    source_points, target_points = source.points(), target.points()
    _require(source_points == _independent_prime_points(43, 1, 0)
             and target_points == _independent_prime_points(43, -4, 0), "independent curve count")
    for name, points, curve in (("source", source_points, source), ("target", target_points, target)):
        _require(ad[name+"_points"] == [encode_point(curve, x) for x in points]
                 and ad[name+"_order"] == len(points)
                 and ad[name+"_factorization"] == {str(k): v for k, v in factorize(len(points)).items()}, "curve census certificate")
    p, s = _point(c, ad["P"]), _point(c, ad["S"])
    canonical = select_prime_subgroup(source, r=11)
    _require(p == tuple(f.coerce(x[0]) for x in canonical["P"]), "noncanonical P")
    group = [c.mul(a, p) for a in range(11)]
    _require(ad["G"] == [encode_point(c, q) for q in group] and len(set(group)) == 11,
             "bad G certificate")
    _require(s == (f.neg(p[0]), f.mul((0, 1), p[1])) and s not in group and c.mul(11, s) is None,
             "bad distortion witness")
    images = [isogeny(source, target, q) for q in source_points]
    _require(ad["map_images"] == [encode_point(target, q) for q in images]
             and ad["kernel"] == [encode_point(source, q) for q in source_points if isogeny(source, target, q) is None]
             and ad["map_pair_tests"] == len(source_points)**2 and ad["residuals"] == [], "bad map coverage")
    for i, left in enumerate(source_points):
        for j, right in enumerate(source_points):
            _require(isogeny(source, target, source.add(left, right)) == target.add(images[i], images[j]), "map homomorphism")
    _require(cases["admission"]["observables"] == {"admitted": True, "r": 11}, "admission summary")
    pp, sp = isogeny(c, cp, p), isogeny(c, cp, s)
    pair = cases["pairings"]["certificates"]
    g, gp = f.coerce(pair["g"]), f.coerce(pair["phi_g"])
    _require(set(pair["arms"]) == {"direct", "transported", "reused_power"}, "missing pairing cost arms")
    for name, arm in pair["arms"].items():
        _require(arm["arm"] == name, "wrong pairing arm name")
        verify_pairing_arm(arm, 43, (1, 0), 1, 0, 11, ad["P"], ad["S"])
    _require(pair["arms"]["direct"]["g"] == pair["g"]
             and pair["arms"]["transported"]["g"] == pair["phi_g"]
             and pair["arms"]["reused_power"]["g"] == pair["phi_g"], "arm base alignment")
    verify_weil(c, p, s, 11, g, pair["g_certificate"])
    verify_weil(cp, pp, sp, 11, gp, pair["phi_g_certificate"])
    _require(g != f.one and f.pow(g, 11) == f.one and gp == f.pow(g, 2), "base covariance/nondegeneracy")
    _require([x["a"] for x in pair["targets"]] == list(range(11)), "target coverage")
    targets = []
    for a, record in enumerate(pair["targets"]):
        q, h, hp = group[a], f.coerce(record["h"]), f.coerce(record["phi_h"])
        _require(record["Q"] == encode_point(c, q) and record["phiQ"] == encode_point(cp, isogeny(c, cp, q)), "bad Q/map Q")
        verify_weil(c, q, s, 11, h, record["h_certificate"])
        verify_weil(cp, isogeny(c, cp, q), sp, 11, hp, record["phi_h_certificate"])
        _require(h == f.pow(g, a) and hp == f.pow(gp, a) and hp == f.pow(h, 2)
                 and record["reused_power"] == list(hp) and record["zero_target"] == (a == 0), "target covariance/truth")
        _require(pair["arms"]["direct"]["images"][a] == list(h)
                 and pair["arms"]["transported"]["images"][a] == list(hp)
                 and pair["arms"]["reused_power"]["images"][a] == list(hp), "arm target alignment")
        targets.append(h)
    _require(cases["pairings"]["observables"] == {"nontrivial_target_images": 10, "covariance_failures": 0}, "pair summary")
    vb = cases["field_bases"]["certificates"]
    vf = Field(43, (2, -2))
    vc, vcp = Curve(vf, 1, 0), Curve(vf, -4, 0)
    expected_conversion = [[list(x), list(vf.coerce((x[0]-x[1], x[1])))] for x in f.elements()]
    _require(vb["conversion"] == expected_conversion, "incomplete/wrong basis conversion")
    vp, vs = [tuple(vf.coerce((x[0]-x[1], x[1])) for x in point) for point in (p, s)]
    _require(vb["P"] == encode_point(vc, vp) and vb["S"] == encode_point(vc, vs), "basis points")
    for key, curve, left, right, expected in (("g", vc, vp, vs, g),
            ("phi_g", vcp, isogeny(vc, vcp, vp), isogeny(vc, vcp, vs), gp)):
        _require(vb[key] == list(vf.coerce((expected[0]-expected[1], expected[1]))), "basis base")
        verify_weil(curve, left, right, 11, vb[key], vb[key+"_certificate"])
    _require(len(vb["targets"]) == 11 and cases["field_bases"]["observables"] == {"converted_elements": 43**2}, "basis target coverage")
    _require(vb["converted_pairing_inputs"] == {"g": vb["g"], "phi_g": vb["phi_g"],
             "images": [x["h"] for x in vb["targets"]]}, "basis acquisition alignment")
    for q, h, record in zip(group, targets, vb["targets"]):
        vq = None if q is None else tuple(vf.coerce((x[0]-x[1], x[1])) for x in q)
        _require(record["Q"] == encode_point(vc, vq) and record["h"] == list(vf.coerce((h[0]-h[1], h[1]))), "basis target")
        verify_weil(vc, vq, vs, 11, record["h"], record["certificate"])
        verify_weil(vcp, isogeny(vc, vcp, vq), isogeny(vc, vcp, vs),
                    11, record["phi_h"], record["phi_certificate"])
        _require(vf.coerce(record["phi_h"]) == vf.pow(record["h"], 2), "basis target covariance")
    records = cases["baselines"]["certificates"]["records"]
    baseline_arms = cases["baselines"]["certificates"]["arms"]
    _require(set(baseline_arms) == {label+"_"+method for label in ("u", "v") for method in ("exhaustive", "bsgs")}, "baseline arm coverage")
    for label in ("u", "v"):
        for method in ("exhaustive", "bsgs"):
            base, images, quadratic = (g, targets, (1, 0)) if label == "u" else (
                vf.coerce(vb["g"]), [vf.coerce(x["h"]) for x in vb["targets"]], (2, -2))
            arm = baseline_arms[label+"_"+method]
            _require(arm["method"] == method, "baseline method mismatch")
            verify_baseline_arm(arm, 43, quadratic, base, images, 11)
    _require([(x["basis"], x["a"]) for x in records] == [(label, a) for label in ("u", "v") for a in range(11)], "baseline coverage")
    for record in records:
        ff, base = (f, g) if record["basis"] == "u" else (vf, vf.coerce(vb["g"]))
        a, h = record["a"], ff.coerce(record["h"])
        _require(h == ff.pow(base, a) and record["exhaustive"] == record["bsgs"] == [a]
                 and record["bsgs_work"] == {"m": 4, "baby_entries": 4, "giant_steps": 5}, "baseline log certificate")
    _require(cases["baselines"]["observables"] == {"targets_per_basis": 11}, "baseline summary")
    relations = cases["relations"]["certificates"]
    _verify_relations(relations, f, 11)
    _require(cases["relations"]["observables"] == {"accepted": sum(p["accepted"] for p in relations["pairs"]),
             "columns": len(relations["columns"]), "solve": relations["solve"],
             "completeness": "unique_relative_logs" if relations["solve"]["unique"] else "incomplete_rank"}, "relation summary")
    descent = cases["descent"]["certificates"]
    _require(descent == individual_descent(f, 11, relations, g, targets), "bad descent search/normalization")
    for a, recovered in enumerate(descent["recovered"]):
        if recovered["scalar"] is not None:
            _require(recovered["scalar"] == a and f.pow(g, a) == targets[a], "bad recovered scalar")
    recovered_count = sum(x["status"] == "recovered" for x in descent["recovered"])
    complete = all(x["verified"] for x in descent["recovered"])
    _require(cases["descent"]["observables"] == {"recovered_nonzero": recovered_count,
             "completeness": "complete_coverage" if complete else "incomplete_coverage"}, "descent summary")
    ideal = cases["special_ideal"]["certificates"]
    _require(ideal == special_ideal(16, Counter()), "incomplete/bad ideal census")
    ring = QuadraticRing(1, 0, "Z[i]")
    for cell in ideal["cells"]:
        if cell["member"]:
            a, b = cell["ab"]
            z, y = cell["basis_coordinates"]
            _require((5*z+2*y, y) == (a, b)
                     and ring.mul(cell["element_quotient"], (2, -1)) == (a, -b), "ideal lattice/element witness")
    _require(cases["special_ideal"]["observables"] == {"members": ideal["members"], "primitive_members": ideal["primitive_members"]}, "ideal summary")
    controls = cases["controls"]["certificates"]
    _require(set(controls) == set(CONTROLS), "deleted/extra controls")
    expected = _make_controls(result["seed"], c, cp, p, s, g, targets, group, relations)
    _require(controls == expected and cases["controls"]["observables"] == {"all_retained": True}, "bad control witnesses")
    # Make acceptance/status fields derived, not arbitrary prose.
    for name in PANELS:
        expected_status = "measured"
        if name == "descent" and not recovered_count:
            expected_status = "zero_yield"
        if name == "controls" and controls["relabeling"]["compatible"]:
            expected_status = "invalid"
        _require(cases[name]["status"] == expected_status, "false case status")
    _require(cases["relations"]["limits"] == ([] if relations["solve"]["unique"] else ["Incomplete modular rank; no relative-log completion supplied."])
             and cases["descent"]["limits"] == ([] if complete else ["Incomplete rank or individual descent coverage; no baseline logs supplied."]), "deleted incompleteness limits")
    work = result["work_accounting"]
    _check_resource_usage(work["resource"])
    accounting = work["arm_accounting"]
    _require(accounting["pairing_cost_paths"] == {name: "cases.pairings.certificates.arms."+name+".cost" for name in pair["arms"]}
             and accounting["baseline_cost_paths"] == {name: "cases.baselines.certificates.arms."+name+".cost" for name in baseline_arms}, "missing cost references")
    _require(accounting["cold_start_components"] == {name: ["counter.phases.shared_setup", "counter.phases.admission", "pairing_arms."+name+".cost"] for name in pair["arms"]}, "unpaid admission dependency")
    _require(accounting["baseline_acquisition_components"] == {label+"_"+method: ["counter.phases.shared_setup", "counter.phases.admission", "pairing_arms.direct.cost"]+
             (["counter.phases.basis_conversion"] if label == "v" else [])+["baseline_arms."+label+"_"+method+".cost"]
             for label in ("u", "v") for method in ("exhaustive", "bsgs")}, "unpaid baseline acquisition/conversion")
    _require(accounting["basis_conversion_component"] == "counter.phases.basis_conversion (sequential with field_bases validation)"
             and "No per-arm or end-to-end advantage claimed" in accounting["interpretation"], "cost comparison scope")
    _require(work["convention"] and work["unpriced_work"] and result["limitations"] and result["checks"], "missing accounting/limits")
    _require(result["checks"]["random_relabeling_control_valid"] ==
             (not controls["relabeling"]["compatible"]), "false random-label control validity")
    snapshot = work["counter"]
    _require(all(isinstance(n, int) and n >= 0 for n in snapshot["operations"].values()), "bad work count")
    phases = snapshot["phases"]
    _require((set(PANELS)-{"baselines"}) | {"basis_conversion", "shared_setup"} <= set(phases), "missing paid phases")
    _require(phases["basis_conversion"]["operations"] == {"basis.conversion": 2*43**2+4+2+11}, "unpaid full basis-conversion component")
    totals = Bag()
    for phase in phases.values():
        _require(phase["calls"] > 0 and phase["wall_seconds"] >= 0 and phase["cpu_seconds"] >= 0, "bad phase cost")
        _require(all(isinstance(n, int) and n >= 0 for n in phase["operations"].values()), "bad phase work")
        totals.update(phase["operations"])
    _require(all(n <= snapshot["operations"].get(k, -1) for k, n in totals.items()), "double allocated phase work")
    _require(snapshot["operations"].get("relations.box_candidate") == 33**2-1
             and snapshot["operations"].get("descent.box_candidate") == 12*(33**2-1)
             and snapshot["operations"].get("ideal.box_candidate") == 33**2
             and snapshot["operations"].get("admission.map_pair_test") == len(source_points)**2,
             "wrong scheduled work counts")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if args.check:
        _require(args.output_dir is None, "--check cannot write output")
        check_wall, check_cpu = time.monotonic(), time.process_time()
        check_result(json.loads(args.check.read_text()))
        print(json.dumps({"certificate_valid": True, "independent_review": False,
                          "checker_wall_seconds": time.monotonic()-check_wall,
                          "checker_cpu_seconds": time.process_time()-check_cpu,
                          "resource": resource_usage("separate checker through certificate replay"),
                          "scope": "separate certificate replay; excluded from trial counters"}, sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir is required for execution")
    started, wall, cpu = datetime.now(timezone.utc).isoformat(), time.monotonic(), time.process_time()
    result = run_experiment(args.seed)
    # The supervisor invokes --check separately. This avoids silently charging
    # a complete checker replay as construction time in the canonical writer.
    write_artifacts(result, args.output_dir, args.seed, started, wall, cpu)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, ArithmeticError, TypeError) as error:
        print(f"pairing instrument/check failure: {error}", file=sys.stderr)
        raise SystemExit(1)
