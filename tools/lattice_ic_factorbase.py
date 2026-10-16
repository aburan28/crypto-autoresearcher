"""Exact prospective auxiliary-coset pilot; no study computation at import.

The default study executes only via run_experiment()/CLI after external admission.
Software tests use explicit non-study parameters. Exhaustive enumeration is the
candidate algorithm here and is charged, never passed off as a free solver oracle.
"""
from __future__ import annotations

import argparse
from collections import Counter as Histogram
from contextlib import contextmanager
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import random
import resource
import sys
import time

try:
    from lattice_ic_core import (Counter, Curve, Field, encode_point, factorize,
                                  rank_mod, select_prime_subgroup, write_artifacts)
except ImportError:
    from tools.lattice_ic_core import (Counter, Curve, Field, encode_point, factorize,
                                       rank_mod, select_prime_subgroup, write_artifacts)

SCHEMA = "lattice_ic.factorbase.v1"
UNPRICED = ["Python allocation, hashing and loop overhead not given a primitive unit cost",
            "integer bit complexity not separately weighted; RSS is process highwater, not isolated phase allocation",
            "no cryptographic-scale discovery or polynomial-solver cost inferred"]


_CoreCounter = Counter


def _rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return int(value)
    if sys.platform.startswith("linux"):
        return int(value)*1024
    raise RuntimeError("unsupported native ru_maxrss units; instrument-stop")


class Counter(_CoreCounter):
    """Core-compatible local counter with observed process RSS at phase exits."""

    def __init__(self):
        super().__init__()
        self.phase_rss = {}

    @contextmanager
    def phase(self, name):
        before = _rss_bytes()
        try:
            with super().phase(name):
                yield self
        finally:
            after = _rss_bytes()
            record = self.phase_rss.setdefault(name, {"process_highwater_start_bytes": before,
                                                      "process_highwater_end_bytes": after})
            record["process_highwater_end_bytes"] = max(record["process_highwater_end_bytes"], after)

    def snapshot(self):
        return {**super().snapshot(), "phase_rss": dict(self.phase_rss),
                "process_peak_rss_bytes": _rss_bytes(),
                "rss_scope": "actual OS process-lifetime highwater at named phase boundaries, not per-phase-exclusive RSS"}


def _encode(field, point):
    return encode_point(field, point)


def _decode(field, point):
    return None if point is None else tuple(field.coerce(c) for c in point)


def _key(point):
    return (-1,) if point is None else tuple(itertools.chain.from_iterable(point))


def _label(point):
    return json.dumps(point, separators=(",", ":"))


def _work(counter, **extra):
    return {**counter.snapshot(), "convention": "core calls counted; phase operations leaf-exclusive, timings inclusive",
            "unpriced_work": list(UNPRICED), **extra}


def _trim(poly):
    poly = list(poly)
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def _poly_add(a, b, p, counter):
    counter.inc("polynomial.coefficient_add", max(len(a), len(b)))
    return _trim([((a[i] if i < len(a) else 0)+(b[i] if i < len(b) else 0)) % p
                  for i in range(max(len(a), len(b)))])


def _poly_mul(a, b, p, counter):
    values = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            counter.inc("polynomial.coefficient_multiply_accumulate")
            values[i+j] = (values[i+j]+x*y) % p
    return _trim(values)


def expanded_map(p, depth, counter=None):
    """Return ascending coefficients N,D for the literal composite x-map.

    N_next=N²+a_j D², D_next=N D, a_next=-4a_j. These are constructed
    independently of point-chain evaluation. No cancellation/pole deletion.
    """
    counter = counter if counter is not None else Counter()
    numerator, denominator, a = [0, 1], [1], 1
    for _ in range(depth):
        n2 = _poly_mul(numerator, numerator, p, counter)
        d2 = [(a*c) % p for c in _poly_mul(denominator, denominator, p, counter)]
        counter.inc("polynomial.coefficient_scale", len(d2))
        denominator = _poly_mul(numerator, denominator, p, counter)
        numerator = _poly_add(n2, d2, p, counter)
        a = -4*a % p
    return {"numerator": numerator, "denominator": denominator,
            "degree": 2**depth, "coefficient_order": "ascending"}


def _eval(field, polynomial, x):
    value = field.zero
    for coefficient in reversed(polynomial):
        value = field.add(field.mul(value, x), coefficient)
    return value


def _expanded_point(field, point, rational_map):
    if point is None:
        return None
    x, y = point
    n, d = rational_map["numerator"], rational_map["denominator"]
    nv, dv = _eval(field, n, x), _eval(field, d, x)
    if dv == field.zero:
        return None
    np = [i*n[i] for i in range(1, len(n))] or [0]
    dp = [i*d[i] for i in range(1, len(d))] or [0]
    derivative_numerator = field.sub(field.mul(_eval(field, np, x), dv),
                                     field.mul(nv, _eval(field, dp, x)))
    return (field.mul(nv, field.inv(dv)),
            field.mul(y, field.mul(derivative_numerator, field.inv(field.mul(dv, dv)))))


def _chain(field, point, depth):
    """Projective point chain, including O and every x=0 pole branch."""
    path, a = [point], field.one
    for _ in range(depth):
        if point is not None:
            x, y = point
            if x == field.zero:
                point = None
            else:
                point = (field.add(x, field.mul(a, field.inv(x))),
                         field.mul(y, field.sub(1, field.mul(a, field.inv(field.mul(x, x))))))
        path.append(point)
        a = field.mul(-4, a)
    return path


def _lifts(curve, x):
    """Paid exhaustive rational-y lifting, independent of catalog point lists."""
    f = curve.field
    rhs = curve.rhs(x)
    return [(x, y) for y in f.elements() if f.mul(y, y) == rhs]


def _arm_bases(p, depth, image, target_group, source_fiber):
    """Fresh counters per list/expanded/chain/P1 membership arm."""
    bases, works, paths, p1_roots, irrational = {}, {}, [], [], []
    for arm in ("list", "expanded", "chain", "p1_only"):
        counter, f = Counter(), None
        f = Field(p, counter=counter)
        with counter.phase("setup"):
            auxiliary = Curve(f, 1, 0)
            mapping = expanded_map(p, depth, counter) if arm in ("expanded", "p1_only") else None
            target = [_decode(f, point) for point in target_group]
            image_point = _decode(f, image)
            xset = {f.coerce(point[0]) for point in source_fiber} if arm == "list" else None
        accepted = []
        with counter.phase("membership"):
            for point in target:
                if point is None:
                    continue
                counter.inc("membership.attempt")
                if arm == "list":
                    good = point[0] in xset
                elif arm == "p1_only":
                    denominator = _eval(f, mapping["denominator"], point[0])
                    good = denominator != f.zero and f.mul(
                        _eval(f, mapping["numerator"], point[0]), f.inv(denominator)) == image_point[0]
                else:
                    good = False
                    for lift in _lifts(auxiliary, point[0]):
                        if arm == "chain":
                            path = _chain(f, lift, depth)
                            endpoint = path[-1]
                            if endpoint == image_point:
                                paths.append({"target": _encode(f, point), "source_lift": _encode(f, lift),
                                              "points": [_encode(f, node) for node in path],
                                              "x": [None if node is None else f.encode(node[0]) for node in path]})
                        else:
                            endpoint = _expanded_point(f, lift, mapping)
                        good = good or endpoint == image_point
                if good:
                    accepted.append(_encode(f, point))
        if arm == "p1_only":
            with counter.phase("full_P1_fiber_control"):
                for x in f.elements():
                    denominator = _eval(f, mapping["denominator"], x)
                    if denominator != f.zero and f.mul(_eval(f, mapping["numerator"], x),
                                                        f.inv(denominator)) == image_point[0]:
                        p1_roots.append(f.encode(x))
                        if not _lifts(auxiliary, x):
                            irrational.append(f.encode(x))
        bases[arm] = accepted
        works[arm] = _work(counter, setup_policy="fresh arm setup; shared discovery charged in catalog setup")
    return bases, works, paths, p1_roots, irrational


def auxiliary_catalog(p=97, depths=(0, 1, 2, 3), *, target_coefficients=(0, 2)):
    """Build every rational composite fiber with complete chain witnesses/costs.

    Returns JSON-native {p,depths,target,entries,work}. entries[d] contains a_j,
    expanded_map, full rational kernel, complete_kernel flag (size==2^d), pole
    paths, every finite image fiber in lex image order, first_coset_index selected
    by lex SOURCE A, and duplicate-base histograms. Each fiber has A,B,points,
    point/x paths, list/expanded/chain/P1 target bases and fresh membership work.
    Incomplete rational kernels retain ALL rational fibers but are inadmissible
    complete-geometric-kernel cells. No replacement/favorable coset selection.
    target G is serialized in POINT lex order, never as a verifier log table.
    Every call rebuilds and charges its own setup; import has no study effects.
    Optional target_coefficients is for explicit non-study software fixtures.
    """
    if len(set(depths)) != len(depths) or any(not isinstance(d, int) or d < 0 or d > 3 for d in depths):
        raise ValueError("distinct explicit depths from 0..3 required")
    counter, f = Counter(), None
    f = Field(p, counter=counter)
    with counter.phase("target_admission"):
        target_curve = Curve(f, *target_coefficients)
        subgroup = select_prime_subgroup(target_curve)
    target_group = sorted(subgroup["G"] or [], key=_key)
    target = {"p": p, "A": target_coefficients[0], "B": target_coefficients[1],
              "admission": {**subgroup, "P": _encode(f, subgroup["P"]),
                            "G": [_encode(f, point) for point in target_group] if subgroup["admitted"] else None}}
    entries = []
    for depth in depths:
        local = Counter()
        field = Field(p, counter=local)
        with local.phase("catalog_setup"):
            curves = [Curve(field, pow(-4, j, p), 0) for j in range(depth+1)]
            points = curves[0].points()
            mapping = expanded_map(p, depth, local)
        fibers, traces = {}, {}
        with local.phase("rational_fiber_census"):
            for point in points:
                path = _chain(field, point, depth)
                if not all(curves[j].is_on_curve(node) for j, node in enumerate(path)):
                    raise ArithmeticError("invalid intermediate map point")
                fibers.setdefault(path[-1], []).append(point)
                traces[point] = path
        kernel = fibers.get(None, [])
        if len(kernel) > 2**depth:
            raise ArithmeticError("rational kernel larger than separable degree")
        finite_images = sorted((point for point in fibers if point is not None), key=_key)
        finite_sources = [point for point in points if point not in kernel]
        first_source = finite_sources[0] if finite_sources else None
        first_image = traces[first_source][-1] if first_source is not None else None
        records, duplicate_histogram = [], Histogram()
        for image in finite_images:
            fiber = sorted(fibers[image], key=_key)
            representative = fiber[0]
            with local.phase("coset_certificate"):
                coset = sorted((curves[0].add(representative, k) for k in kernel), key=_key)
                if coset != fiber:
                    raise ArithmeticError("rational fiber differs from complete enumerated rational coset")
            encoded_fiber = [_encode(field, point) for point in fiber]
            bases, arm_work, membership_paths, p1_roots, irrational = _arm_bases(
                p, depth, _encode(field, image), target["admission"]["G"] or [], encoded_fiber)
            if not bases["list"] == bases["expanded"] == bases["chain"]:
                raise ArithmeticError("same-base arms disagree")
            key = _label(bases["list"])
            duplicate_histogram[key] += 1
            records.append({"index": len(records), "A": _encode(field, representative),
                "B": _encode(field, image), "points": encoded_fiber,
                "paths": [{"source": _encode(field, point),
                           "points": [_encode(field, node) for node in traces[point]],
                           "x": [None if node is None else field.encode(node[0]) for node in traces[point]]}
                          for point in fiber],
                "bases": bases, "membership_paths": membership_paths,
                "p1_x_roots": p1_roots, "p1_without_auxiliary_rational_lift": irrational,
                "complete_kernel_admitted": len(kernel) == 2**depth,
                "work": arm_work})
        poles = [{"source": _encode(field, point), "points": [_encode(field, node) for node in traces[point]],
                  "x": [None if node is None else field.encode(node[0]) for node in traces[point]]}
                 for point in kernel]
        entries.append({"d": depth, "a_j": [pow(-4, j, p) for j in range(depth+1)],
            "expanded_map": mapping, "source_point_count": len(points),
            "kernel": [_encode(field, point) for point in kernel], "pole_paths": poles,
            "geometric_degree": 2**depth, "complete_kernel": len(kernel) == 2**depth,
            "admission_reason": None if len(kernel) == 2**depth else "rational kernel smaller than separable geometric degree",
            "finite_fibers": records, "first_coset_index": finite_images.index(first_image) if first_image is not None else None,
            "first_coset_A": _encode(field, first_source),
            "finite_fiber_denominator": len(records),
            "duplicate_actual_base_histogram": dict(sorted(duplicate_histogram.items())),
            "work": _work(local, stored_source_points=len(points), stored_path_nodes=sum(len(x) for x in traces.values()))})
    return {"schema_version": "lattice_ic.auxiliary_catalog.v1", "p": p, "depths": list(depths),
            "target": target, "entries": entries, "work": _work(counter)}


def _alpha(curve, point, multiplier):
    return None if point is None else (curve.field.mul(multiplier, point[0]), point[1])


def action_certificate(curve, group, prime, generator, multiplier):
    """Full-G preservation/eigenvalue evidence; no scalar for a moved line."""
    group_set = set(group)
    images = [_alpha(curve, point, multiplier) for point in group]
    curve.counter.inc("action.membership_attempt", len(group))
    preserved = all(curve.is_on_curve(image) and image in group_set for image in images)
    eigenvalues = []
    if preserved:
        image = _alpha(curve, generator, multiplier)
        eigenvalues = [value for value in range(1, prime) if curve.mul(value, generator) == image]
    value = eigenvalues[0] if len(eigenvalues) == 1 else None
    verified = preserved and value is not None and all(
        image == curve.mul(value, point) for point, image in zip(group, images))
    return {"preserved": preserved, "admitted": verified, "lambda": value if verified else None,
            "multiplier": curve.field.encode(multiplier),
            "all_G": [{"point": _encode(curve, point), "image": _encode(curve, image)}
                      for point, image in zip(group, images)],
            "scalar_candidates": eigenvalues, "reason": None if verified else "no certified nonzero scalar action on this cyclic G"}


def _orbit_data(curve, base, multiplier, prime, eigenvalue):
    completed = set(base)
    for point in list(base):
        current = _alpha(curve, point, multiplier)
        for _ in range(prime):
            if current in completed:
                break
            completed.add(current)
            current = _alpha(curve, current, multiplier)
        else:
            raise ArithmeticError("action orbit did not close")
    ordered = sorted(completed, key=_key)
    representatives, lookup, orbits = [], {}, []
    for point in ordered:
        if point in lookup:
            continue
        orbit, current = [], point
        while current not in orbit:
            if current in lookup:
                raise ArithmeticError("overlapping inconsistent action orbits")
            exponent = len(orbit)
            lookup[current] = (len(orbits), pow(eigenvalue, exponent, prime))
            orbit.append(current)
            current = _alpha(curve, current, multiplier)
        if current != point:
            raise ArithmeticError("action is not a permutation")
        representatives.append(point)
        orbits.append(orbit)
    return ordered, representatives, lookup, orbits


def _histogram(curve, base, group, m):
    """Paid exhaustive candidate enumeration, including every empty/O cell."""
    buckets = {point: [] for point in group}
    for indices in itertools.product(range(len(base)), repeat=m):
        curve.counter.inc("relation.tuple_attempt")
        target = None
        for index in indices:
            target = curve.add(target, base[index])
        if target not in buckets:
            raise ArithmeticError("tuple sum left certified subgroup")
        buckets[target].append(list(indices))
    return buckets


def _rank_rows(base, representatives, lookup, target, indices, r, weight=1):
    raw = [0]*len(base)
    quotient = [0]*len(representatives)
    for index in indices:
        raw[index] += 1
        orbit, scalar = lookup[base[index]]
        quotient[orbit] = (quotient[orbit]+scalar) % r
    raw, quotient = [x % r for x in raw], [x % r for x in quotient]
    if target is None:
        return raw, quotient, raw, quotient
    raw_aug, quotient_aug = raw+[-weight % r], quotient+[-weight % r]
    if target in base:
        raw[base.index(target)] = (raw[base.index(target)]-weight) % r
        orbit, scalar = lookup[target]
        quotient[orbit] = (quotient[orbit]-weight*scalar) % r
        return raw_aug, quotient_aug, raw, quotient
    return raw_aug, quotient_aug, raw_aug, quotient_aug


def _rank(matrix, r, counter):
    counter.inc("rank.call")
    counter.inc("rank.input_entries", sum(map(len, matrix)))
    values = [[int(x) % r for x in row] for row in matrix]
    if not values:
        return 0
    position = 0
    for column in range(len(values[0])):
        pivot = next((i for i in range(position, len(values)) if values[i][column]), None)
        if pivot is None:
            continue
        values[position], values[pivot] = values[pivot], values[position]
        counter.inc("rank.modular_inverse")
        inverse = pow(values[position][column], -1, r)
        counter.inc("rank.modular_multiply", len(values[position]))
        values[position] = [x*inverse % r for x in values[position]]
        for i in range(position+1, len(values)):
            coefficient = values[i][column]
            counter.inc("rank.modular_multiply_subtract", len(values[i]))
            values[i] = [(x-coefficient*y) % r for x, y in zip(values[i], values[position])]
        position += 1
        if position == len(values):
            break
    return position


def _public_known(curve, generator, multiplier, eigenvalue, prime):
    """Only public O and signed action-orbit logs; no subgroup-index table."""
    known, witnesses = {None: 0}, [{"point": None, "scalar": 0, "sign": 0, "exponent": 0}]
    current, scalar = generator, 1
    for exponent in range(prime):
        for sign, point, value in ((1, current, scalar), (-1, curve.neg(current), -scalar % prime)):
            if point in known:
                _assert(known[point] == value, "inconsistent public action scalar")
            else:
                known[point] = value
                witnesses.append({"point": _encode(curve, point), "scalar": value,
                                  "sign": sign, "exponent": exponent})
        curve.counter.inc("public_action.orbit_step")
        current = _alpha(curve, current, multiplier)
        scalar = scalar*eigenvalue % prime
        if current == generator:
            break
    else:
        raise ValueError("public generator action did not close")
    return known, {"generator": _encode(curve, generator), "points": witnesses,
                   "policy": "O and ±alpha^j(P) only, evaluated from public P/lambda; no verifier G-index logs"}


def _normalized_rows(rows, variables, public_known, prime):
    known_columns = {i: public_known[point] for i, point in enumerate(variables) if point in public_known}
    unknown = [i for i in range(len(variables)) if i not in known_columns]
    normalized = [[row[i] % prime for i in unknown] +
                  [sum(row[i]*value for i, value in known_columns.items()) % prime] for row in rows]
    return normalized, unknown


def _known_affine_constraints(variables, public_known, prime):
    rows = []
    for i, point in enumerate(variables):
        if point in public_known:
            row = [0]*(len(variables)+1)
            row[i], row[-1] = 1, -public_known[point] % prime
            rows.append(row)
    return rows


def analyze_base(p, target_coefficients, group_encoded, base_encoded, r, multiplier, eigenvalue, lengths=(2, 3), *, generator_encoded=None):
    """Fresh, fully charged original/canonical-orbit tuple and rank census.

    Per fixed public R, report homogeneous O rows or augmented [base,-R] rows.
    Merge the target column if its point already has a known base action label;
    formal merged constraints are diagnostics; useful rank is rank(K+N)-rank(K)
    using only public signed action-orbit knowledge. Never pool target columns or
    use verifier scalar logs. Family witnesses transform all legs AND the target
    weight lambda^t. Every ordered tuple and zero cell remains in the result.
    """
    counter, f = Counter(), None
    f = Field(p, counter=counter)
    curve = Curve(f, *target_coefficients)
    group = [_decode(f, point) for point in group_encoded]
    original = sorted((_decode(f, point) for point in base_encoded), key=_key)
    with counter.phase("orbit_setup"):
        base, representatives, lookup, orbits = _orbit_data(curve, original, multiplier, r, eigenvalue)
    with counter.phase("public_known_setup"):
        generator = _decode(f, generator_encoded) if generator_encoded is not None else min((point for point in group if point is not None), key=_key)
        public_known, public_certificate = _public_known(curve, generator, multiplier, eigenvalue, r)
    panels = []
    for m in lengths:
        with counter.phase("original_base_relation_enumeration"):
            original_hist = _histogram(curve, original, group, m)
        with counter.phase("orbit_base_relation_enumeration"):
            buckets = _histogram(curve, base, group, m)
        targets = []
        with counter.phase("rank_and_action_certificates"):
            for target in group:
                raw_rows, quotient_rows, raw_constraints, constraints, families = [], [], [], [], []
                increments, formal_increments = [], []
                previous_rank, previous_formal = 0, 0
                variables = representatives+([target] if target is not None and target not in base else [])
                known_rows = _known_affine_constraints(variables, public_known, r)
                known_rank = _rank(known_rows, r, counter)
                for indices in buckets[target]:
                    rows = _rank_rows(base, representatives, lookup, target, indices, r)
                    for collection, row in zip((raw_rows, quotient_rows, raw_constraints, constraints), rows):
                        collection.append(row)
                    current_formal = _rank(constraints, r, counter)
                    formal_increments.append(current_formal-previous_formal)
                    previous_formal = current_formal
                    normalized, unknown = _normalized_rows(constraints, variables, public_known, r)
                    current_rank = _rank(known_rows+[row+[0] for row in constraints], r, counter)-known_rank
                    increments.append(current_rank-previous_rank)
                    previous_rank = current_rank
                    leg_points = [base[index] for index in indices]
                    family_rows = [[], [], [], []]
                    family_legs, weight = [], 1
                    for _ in range(max((len(orbit) for orbit in orbits), default=1)):
                        transformed_indices = [base.index(point) for point in leg_points]
                        transformed = _rank_rows(base, representatives, lookup, target, transformed_indices, r, weight)
                        family_legs.append(transformed_indices)
                        for collection, row in zip(family_rows, transformed):
                            collection.append(row)
                        leg_points = [_alpha(curve, point, multiplier) for point in leg_points]
                        weight = weight*eigenvalue % r
                    family_ranks = [_rank(matrix, r, counter) for matrix in family_rows]
                    if family_ranks[1] > 1 or family_ranks[3] > 1:
                        raise ArithmeticError("transformed quotient family exceeds one dimension")
                    normalized_family, unknown = _normalized_rows(family_rows[3], variables, public_known, r)
                    family_span_rank = _rank(known_rows+[row+[0] for row in family_rows[3]], r, counter)
                    normalized_family_rank = family_span_rank-known_rank
                    families.append({"legs": family_legs, "rows": family_rows, "ranks": family_ranks,
                                     "public_normalized_rows": normalized_family, "marginal_new_rank": normalized_family_rank})
                dimensions = [len(base)+(target is not None), len(representatives)+(target is not None),
                              len(base)+(target is not None and target not in base),
                              len(representatives)+(target is not None and target not in base)]
                normalized, unknown = _normalized_rows(constraints, variables, public_known, r)
                span_rank = _rank(known_rows+[row+[0] for row in constraints], r, counter)
                useful_rank = span_rank-known_rank
                if _rank(normalized, r, counter) != useful_rank or _rank([row[:-1] for row in normalized], r, counter) != useful_rank:
                    raise ArithmeticError("public known-log substitution created inconsistent affine rows")
                targets.append({"R": _encode(f, target), "homogeneous": target is None,
                    "count": len(buckets[target]), "tuples": buckets[target],
                    "rows": [raw_rows, quotient_rows, raw_constraints, constraints],
                    "ranks": [_rank(matrix, r, counter) for matrix in (raw_rows, quotient_rows, raw_constraints, constraints)],
                    "dimensions": dimensions, "formal_constraint_rank_increments": formal_increments,
                    "new_constraint_rank_increments": increments,
                    "public_normalized_rows": normalized, "unknown_quotient_columns": unknown,
                    "public_known_affine_constraints": known_rows, "public_known_rank": known_rank,
                    "rank_with_public_known": span_rank,
                    "marginal_new_rank": useful_rank,
                    "target_merged": target is not None and target in base,
                    "transformed_families": families})
        panels.append({"m": m, "original_histogram": [{"R": _encode(f, point), "count": len(original_hist[point])}
                                                       for point in group],
                       "original_tuple_total": len(original)**m, "completed_tuple_total": len(base)**m,
                       "targets": targets})
    return {"M_original": len(original), "M": len(base), "U": len(representatives),
            "base": [_encode(f, point) for point in base], "original_base": base_encoded,
            "representatives": [_encode(f, point) for point in representatives],
            "orbits": [[_encode(f, point) for point in orbit] for orbit in orbits],
            "row_order": ["raw_augmented", "quotient_augmented", "raw_constraints", "quotient_constraints"],
            "public_known": public_certificate,
            "rank_interpretation": "four formal ranks are diagnostics; marginal_new_rank substitutes only public O/±alpha^j(P) logs",
            "target_policy": "one fixed public point column per R; merged when action identifies it with a base column; never pooled",
            "census": panels, "work": _work(counter)}


def torsion_line_control(p=5, quadratic=(1, 1), A=0, B=1, ell=3, multiplier=(0, 1), *, y_multiplier=1):
    """Enumerate all rational order-ell lines; no scalar assigned to moved lines."""
    counter, field = Counter(), None
    field = Field(p, quadratic, counter=counter)
    curve = Curve(field, A, B)
    with counter.phase("torsion_line_control"):
        torsion = [point for point in curve.points() if curve.mul(ell, point) is None]
        unseen = set(torsion)-{None}
        lines = []
        while unseen:
            generator = min(unseen, key=_key)
            line = sorted((curve.mul(i, generator) for i in range(ell)), key=_key)
            unseen.difference_update(line)
            images = [None if point is None else (field.mul(multiplier, point[0]),
                                                 field.mul(y_multiplier, point[1])) for point in line]
            stable = all(curve.is_on_curve(point) and point in line for point in images)
            values = [value for value in range(1, ell) if all(image == curve.mul(value, point)
                      for point, image in zip(line, images))] if stable else []
            lines.append({"P": _encode(field, generator), "line": [_encode(field, point) for point in line],
                          "images": [_encode(field, point) for point in images], "stable": stable,
                          "lambda": values[0] if len(values) == 1 else None,
                          "scalar_admitted": stable and len(values) == 1})
    return {"p": p, "quadratic": list(quadratic) if quadratic is not None else None, "A": A, "B": B, "ell": ell,
            "multiplier": field.encode(multiplier), "y_multiplier": field.encode(y_multiplier),
            "torsion": [_encode(field, point) for point in torsion], "lines": lines,
            "work": _work(counter)}


def _generic_control(p, coefficients, group_encoded, base_encoded, seed, lengths):
    counter, field = Counter(), None
    field = Field(p, counter=counter)
    curve = Curve(field, *coefficients)
    group = [_decode(field, point) for point in group_encoded]
    permutation = list(range(len(group)))
    random.Random(seed).shuffle(permutation)
    labels = {point: permutation[i] for i, point in enumerate(group)}
    table = []
    with counter.phase("generic_oracle_setup"):
        for left in group:
            for right in group:
                table.append([labels[left], labels[right], labels[curve.add(left, right)]])
    lookup = {(a, b): c for a, b, c in table}
    base_labels = [labels[_decode(field, point)] for point in base_encoded]
    histograms = []
    with counter.phase("generic_tuple_enumeration"):
        for m in lengths:
            histogram = Histogram()
            for legs in itertools.product(base_labels, repeat=m):
                value = labels[None]
                counter.inc("generic.tuple_attempt")
                for leg in legs:
                    counter.inc("generic.oracle_add")
                    value = lookup[value, leg]
                histogram[value] += 1
            histograms.append({"m": m, "counts": [[label, histogram[label]] for label in sorted(permutation)]})
    return {"point_label_bijection": [[_encode(field, point), labels[point]] for point in group],
            "base_labels": base_labels, "zero_label": labels[None], "addition_table": table,
            "histograms": histograms, "work": _work(counter),
            "interpretation": "opaque cyclic-group control; mapping is verification/setup only, not a candidate scalar-log table"}


def _case(identifier, panel, inputs, observables, certificates, work, *, status="measured", limits=None):
    return {"id": identifier, "panel": panel, "status": status, "inputs": inputs,
            "observables": observables, "certificates": certificates, "work": work,
            "limits": list(limits or [])}


def run_experiment(seed):
    """Execute the literal prospective F97/F25 panel ONLY when externally admitted."""
    catalog = auxiliary_catalog()
    p, coefficients, lengths = 97, (0, 2), (2, 3)
    subgroup = catalog["target"]["admission"]
    counter, field = Counter(), None
    field = Field(p, counter=counter)
    curve = Curve(field, *coefficients)
    group = [_decode(field, point) for point in subgroup["G"] or []]
    action = action_certificate(curve, group, subgroup["r"], _decode(field, subgroup["P"]), 35) if subgroup["admitted"] else None
    cases = [_case("target-admission", "subgroup", catalog["target"],
                   {"admitted": subgroup["admitted"]}, subgroup, catalog["work"],
                   status="measured" if subgroup["admitted"] else "inadmissible"),
             _case("target-alpha", "action", {"alpha_x": 35},
                   {"cube_root_condition": pow(35, 3, p) == 1,
                    "admitted": bool(action and action["admitted"])}, action, _work(counter),
                   status="measured" if action and action["admitted"] else "inadmissible")]
    for entry in catalog["entries"]:
        depth = entry["d"]
        cases.append(_case(f"depth-{depth}", "kernel_and_poles", {"d": depth},
                           {"complete_kernel": entry["complete_kernel"], "rational_kernel_size": len(entry["kernel"]),
                            "finite_cosets": len(entry["finite_fibers"]),
                            "duplicate_base_histogram": entry["duplicate_actual_base_histogram"]},
                           {"kernel": entry["kernel"], "pole_paths": entry["pole_paths"]}, entry["work"],
                           status="measured" if entry["complete_kernel"] else "inadmissible",
                           limits=[] if entry["complete_kernel"] else [entry["admission_reason"]]))
        for fiber in entry["finite_fibers"]:
            inputs = {"d": depth, "fiber_index": fiber["index"], "A": fiber["A"], "B": fiber["B"]}
            certificates = {"catalog_fiber": fiber}
            analyses = {}
            admitted = entry["complete_kernel"] and subgroup["admitted"] and action and action["admitted"]
            if admitted:
                base = fiber["bases"]["list"]
                analyses["candidate"] = analyze_base(p, coefficients, subgroup["G"], base, subgroup["r"],
                                                       35, action["lambda"], lengths, generator_encoded=subgroup["P"])
                analyses["identity_alpha"] = analyze_base(p, coefficients, subgroup["G"], base,
                                                          subgroup["r"], 1, 1, lengths, generator_encoded=subgroup["P"])
                rng = random.Random(f"{seed}:depth{depth}:fiber{fiber['index']}")
                nonzero = [point for point in subgroup["G"] if point is not None]
                random_base = rng.sample(nonzero, len(base))
                analyses["size_matched_random_base"] = analyze_base(p, coefficients, subgroup["G"], random_base,
                                                                   subgroup["r"], 35, action["lambda"], lengths, generator_encoded=subgroup["P"])
                permutation = list(range(p))
                rng.shuffle(permutation)
                source_x = {point[0][0] for point in fiber["points"]}
                labeled_base = [point for point in nonzero if permutation[point[0][0]] in source_x]
                analyses["random_coordinate_labels"] = analyze_base(p, coefficients, subgroup["G"], labeled_base,
                                                                    subgroup["r"], 35, action["lambda"], lengths, generator_encoded=subgroup["P"])
                analyses["random_coordinate_labels"]["coordinate_permutation"] = permutation
                certificates["generic_group"] = _generic_control(p, coefficients, subgroup["G"],
                    analyses["candidate"]["base"], f"{seed}:{depth}:{fiber['index']}:generic", lengths)
                certificates["analyses"] = analyses
            maximum_marginal = max((target["marginal_new_rank"] for panel in analyses.get("candidate", {}).get("census", [])
                                    for target in panel["targets"]), default=0) if admitted else None
            cases.append(_case(f"d{depth}-fiber-{fiber['index']}", "finite_coset_comparison", inputs,
                {"original_M": len(fiber["bases"]["list"]), "max_separate_fixed_target_marginal_rank": maximum_marginal, "same_base_equality":
                 fiber["bases"]["list"] == fiber["bases"]["expanded"] == fiber["bases"]["chain"],
                 "first_coset_slice": fiber["index"] == entry["first_coset_index"],
                 "p1_extra_target_points": [point for point in fiber["bases"]["p1_only"]
                                             if point not in fiber["bases"]["list"]]},
                certificates, {"membership_arms": fiber["work"], "analyses": {name: value["work"] for name, value in analyses.items()},
                               "generic_control": certificates.get("generic_group", {}).get("work"),
                               "shared_setup": "actual catalog discovery charged once. Each alternative cold-start total adds identical catalog/work and entry/work to its fresh membership-arm and analysis work; do not sum these hypothetical cold starts as observed runtime. Reused catalog is explicit amortized setup, never a free candidate oracle",
                               "unpriced_work": list(UNPRICED)},
                status=("zero_yield" if maximum_marginal == 0 else "measured") if admitted else "inadmissible",
                limits=[] if admitted else ["complete rational kernel or target scalar-action admission unavailable; rational fiber retained"]))
    rank2 = torsion_line_control()
    cases.append(_case("rank2-all-lines", "rank2_torsion_control", {"p": 5, "quadratic": [1, 1], "A": 0, "B": 1, "ell": 3},
                       {"line_count": len(rank2["lines"]), "nonstable_lines": sum(not line["stable"] for line in rank2["lines"])},
                       rank2, rank2["work"]))
    result = {"schema_version": SCHEMA, "direction": "factorbase", "seed": seed,
              "parameters": {"target": [97, 0, 2], "alpha_x": 35, "auxiliary": [97, 1, 0],
                             "depths": [0, 1, 2, 3], "tuple_lengths": [2, 3],
                             "coset_schedule": "all rational finite image fibers; lex-source first slice identified"},
              "catalog": catalog, "cases": cases, "checks": {"producer_certificate_check": "pending"},
              "limitations": ["Exact synthetic tiny-curve enumeration, not an unknown-scalar or polynomial solver improvement.",
                              "No pooled distinct-target rank is called useful fixed-target rank.",
                              "No independent scientific validation or cryptographic extrapolation."],
              "work_accounting": {"convention": "actual core calls, leaf-exclusive phase operations; inclusive times not summed",
                                  "oracle_policy": "all target/kernel/coset enumeration and every tuple explicitly paid; no verifier logs supplied",
                                  "memory": {"process_peak_rss_bytes": _rss_bytes(), "scope": "OS process highwater; supervisor resource receipt separate",
                                             "stored_cases": len(cases)}, "unpriced_work": list(UNPRICED)},
              "instrument_scope": "literal finite fixture census; no cutoff/adaptive replacement or performance claim"}
    verification_wall, verification_cpu = time.monotonic(), time.process_time()
    verification = check_result(result)
    result["work_accounting"]["verification"] = {"wall_seconds": time.monotonic()-verification_wall,
        "cpu_seconds": time.process_time()-verification_cpu, "process_peak_rss_bytes": _rss_bytes(),
        "scope": "actual checker elapsed time included in supervisor total; verifier arithmetic excluded from candidate operation counts"}
    result["checks"] = {"producer_certificate_check": "passed", "certificate_items": verification["certificate_items"],
                        "independent_scientific_review": False}
    return result


def _assert(condition, message):
    if not condition:
        raise ValueError(message)


def _check_path(field, source, nodes, xs, depth):
    """Check recorded point equations and finite/pole branches directly."""
    _assert(len(nodes) == len(xs) == depth+1, "wrong path length")
    decoded = [_decode(field, node) for node in nodes]
    _assert(decoded[0] == source, "path source mismatch")
    for j, point in enumerate(decoded):
        curve = Curve(field, pow(-4, j, field.p), 0)
        _assert(curve.is_on_curve(point), "invalid path curve point")
        _assert(xs[j] == (None if point is None else field.encode(point[0])), "intermediate x mismatch")
        if j == depth:
            continue
        following = decoded[j+1]
        if point is None or point[0] == field.zero:
            _assert(following is None, "lost pole/projective branch")
        else:
            _assert(following is not None, "finite map incorrectly infinity")
            x, y = point
            a = field.coerce(pow(-4, j, field.p))
            _assert(field.mul(x, following[0]) == field.add(field.mul(x, x), a), "chain x equation failed")
            _assert(field.mul(field.mul(x, x), following[1]) ==
                    field.mul(y, field.sub(field.mul(x, x), a)), "chain y equation failed")
    return decoded[-1]


def check_catalog(catalog):
    """Substantive catalog verifier: complete partitions, cosets, maps and bases.

    Producer groups fibers by point chains; checker independently computes their
    endpoints from the expanded rational map/derivative and verifies every path
    equation, point, actual target subgroup and P1 lift condition. Not a boolean
    acceptance or a rerun of auxiliary_catalog(). Returns witness item count.
    """
    p, f = catalog["p"], Field(catalog["p"])
    _assert(catalog["schema_version"] == "lattice_ic.auxiliary_catalog.v1", "wrong catalog schema")
    target_data = catalog["target"]
    target_curve = Curve(f, target_data["A"], target_data["B"])
    admission = target_data["admission"]
    actual_order = len(target_curve.points())
    factors = {str(k): v for k, v in factorize(actual_order).items()}
    _assert(admission["order"] == actual_order and admission["factorization"] == factors, "target count/factorization mismatch")
    possible = sorted((int(k) for k, value in factors.items() if int(k) >= 5 and value == 1), reverse=True)
    _assert(admission["admitted"] == bool(possible), "wrong subgroup admission")
    group = []
    if possible:
        r = possible[0]
        _assert(admission["r"] == r, "wrong selected prime")
        generator = _decode(f, admission["P"])
        expected_generator = next(point for point in target_curve.points() if point is not None and target_curve.mul(r, point) is None)
        _assert(generator == expected_generator, "noncanonical generator")
        group = [_decode(f, point) for point in admission["G"]]
        expected = sorted((target_curve.mul(i, generator) for i in range(r)), key=_key)
        _assert(group == expected and len(set(group)) == r, "invalid target subgroup enumeration")
    else:
        _assert(admission["r"] is None and admission["P"] is None and admission["G"] is None, "invented rejected subgroup")
    _assert([entry["d"] for entry in catalog["entries"]] == catalog["depths"], "depth coverage mismatch")
    checked = 0
    for entry in catalog["entries"]:
        d = entry["d"]
        _assert(entry["a_j"] == [pow(-4, j, p) for j in range(d+1)], "wrong auxiliary coefficient")
        mapping = expanded_map(p, d)
        _assert(entry["expanded_map"] == mapping, "expanded polynomial mismatch")
        source_curve, codomain = Curve(f, 1, 0), Curve(f, pow(-4, d, p), 0)
        points = source_curve.points()
        partition = {}
        for point in points:
            endpoint = _expanded_point(f, point, mapping)
            _assert(codomain.is_on_curve(endpoint), "expanded map left codomain")
            partition.setdefault(endpoint, []).append(point)
        kernel = [_decode(f, point) for point in entry["kernel"]]
        _assert(kernel == partition[None], "incomplete or false rational kernel")
        _assert(entry["source_point_count"] == len(points), "source point census mismatch")
        _assert(entry["geometric_degree"] == 2**d and entry["complete_kernel"] == (len(kernel) == 2**d), "false complete-kernel admission")
        _assert(len(entry["pole_paths"]) == len(kernel), "missing kernel/pole branch")
        _assert([_decode(f, row["source"]) for row in entry["pole_paths"]] == kernel, "pole source mismatch")
        for row in entry["pole_paths"]:
            _assert(_check_path(f, _decode(f, row["source"]), row["points"], row["x"], d) is None, "kernel path not infinity")
        images = sorted((point for point in partition if point is not None), key=_key)
        _assert([_decode(f, fiber["B"]) for fiber in entry["finite_fibers"]] == images, "finite image fiber omitted/reordered")
        _assert(entry["finite_fiber_denominator"] == len(images), "wrong coset denominator")
        nonkernel = [point for point in points if point not in kernel]
        first_source = nonkernel[0] if nonkernel else None
        _assert(_decode(f, entry["first_coset_A"]) == first_source, "first source slice changed")
        first_image = _expanded_point(f, first_source, mapping) if first_source is not None else None
        _assert(entry["first_coset_index"] == (images.index(first_image) if first_image is not None else None), "first coset index wrong")
        duplicates = Histogram()
        for index, fiber in enumerate(entry["finite_fibers"]):
            image = images[index]
            domain = partition[image]
            _assert(fiber["index"] == index and [_decode(f, point) for point in fiber["points"]] == domain, "fiber points/number mismatch")
            representative = _decode(f, fiber["A"])
            _assert(representative == domain[0] and sorted((source_curve.add(representative, k) for k in kernel), key=_key) == domain, "fiber is not recorded rational coset")
            _assert(len(fiber["paths"]) == len(domain), "missing source paths")
            for point, row in zip(domain, fiber["paths"]):
                _assert(_decode(f, row["source"]) == point and _check_path(f, point, row["points"], row["x"], d) == image, "wrong finite path")
            source_x = {point[0] for point in domain}
            expected = [_encode(f, point) for point in group if point is not None and point[0] in source_x]
            for arm in ("list", "expanded", "chain"):
                _assert(fiber["bases"][arm] == expected, f"invalid {arm} target base")
            p1_roots = []
            irrational = []
            for x in f.elements():
                denominator = _eval(f, mapping["denominator"], x)
                if denominator != f.zero and _eval(f, mapping["numerator"], x) == f.mul(image[0], denominator):
                    p1_roots.append(f.encode(x))
                    if not _lifts(source_curve, x):
                        irrational.append(f.encode(x))
            _assert(fiber["p1_x_roots"] == p1_roots and fiber["p1_without_auxiliary_rational_lift"] == irrational, "false P1 lift control")
            p1_expected = [_encode(f, point) for point in group if point is not None and f.encode(point[0]) in p1_roots]
            _assert(fiber["bases"]["p1_only"] == p1_expected, "P1 target base mismatch")
            for row in fiber["membership_paths"]:
                target = _decode(f, row["target"])
                source = _decode(f, row["source_lift"])
                _assert(target in group and target is not None and source[0] == target[0], "false target/source membership lift")
                _assert(_check_path(f, source, row["points"], row["x"], d) == image, "membership path wrong image")
            _assert({tuple(tuple(c) for c in row["target"]) for row in fiber["membership_paths"]} ==
                    {tuple(tuple(c) for c in point) for point in expected}, "missing membership witnesses")
            duplicates[_label(expected)] += 1
            _assert(fiber["complete_kernel_admitted"] == entry["complete_kernel"], "fiber admission mismatch")
            checked += len(domain)+len(expected)+1
        _assert(entry["duplicate_actual_base_histogram"] == dict(duplicates), "duplicate/empty base histogram mismatch")
    return checked


def _independent_rank(rows, prime):
    """Separate full Gauss-Jordan checker, not producer core rank routine."""
    a = [[int(x) % prime for x in row] for row in rows]
    if not a:
        return 0
    pivot_row = 0
    for col in range(len(a[0])):
        pivot = next((j for j in range(pivot_row, len(a)) if a[j][col]), None)
        if pivot is None:
            continue
        a[pivot_row], a[pivot] = a[pivot], a[pivot_row]
        inverse = pow(a[pivot_row][col], -1, prime)
        a[pivot_row] = [x*inverse % prime for x in a[pivot_row]]
        for j in range(len(a)):
            if j != pivot_row:
                factor = a[j][col]
                a[j] = [(x-factor*y) % prime for x, y in zip(a[j], a[pivot_row])]
        pivot_row += 1
        if pivot_row == len(a):
            break
    return pivot_row


def check_analysis(analysis, p, coefficients, group_encoded, r, multiplier, eigenvalue, lengths):
    """Verify tuple completeness by independent all-target DP and row equations."""
    f, checked = Field(p), 0
    curve = Curve(f, *coefficients)
    group = [_decode(f, point) for point in group_encoded]
    base = [_decode(f, point) for point in analysis["base"]]
    original = [_decode(f, point) for point in analysis["original_base"]]
    _assert(len(set(base)) == len(base) and all(point in group and point is not None for point in base), "invalid orbit base")
    _assert(len(set(original)) == len(original) and len(original) == analysis["M_original"] and len(base) == analysis["M"], "base size wrong")
    # Rebuild allowable knowledge from public P and certified action, never
    # from the verifier enumeration index of any other subgroup point.
    public_generator = min((point for point in group if point is not None), key=_key)
    _assert(_decode(f, analysis["public_known"]["generator"]) == public_generator, "changed public generator")
    known, witnesses = {None: 0}, [{"point": None, "scalar": 0, "sign": 0, "exponent": 0}]
    current = public_generator
    for exponent in range(r):
        scalar = pow(eigenvalue, exponent, r)
        _assert(current == curve.mul(scalar, public_generator), "uncertified public action weight")
        for sign in (1, -1):
            point = current if sign == 1 else curve.neg(current)
            value = sign*scalar % r
            if point in known:
                _assert(known[point] == value, "inconsistent public known equations")
            else:
                known[point] = value
                witnesses.append({"point": _encode(f, point), "scalar": value, "sign": sign, "exponent": exponent})
        current = _alpha(curve, current, multiplier)
        if current == public_generator:
            break
    else:
        raise ValueError("public action orbit did not close")
    _assert(analysis["public_known"]["points"] == witnesses, "false or hidden public known-log certificate")
    representatives = [_decode(f, point) for point in analysis["representatives"]]
    _assert(len(representatives) == analysis["U"], "quotient dimension wrong")
    lookup, union = {}, set()
    for i, encoded_orbit in enumerate(analysis["orbits"]):
        orbit = [_decode(f, point) for point in encoded_orbit]
        _assert(orbit and orbit[0] == representatives[i] == min(orbit, key=_key), "noncanonical orbit representative")
        for j, point in enumerate(orbit):
            _assert(point not in union and _alpha(curve, point, multiplier) == orbit[(j+1) % len(orbit)], "invalid orbit closure")
            union.add(point)
            lookup[point] = (i, pow(eigenvalue, j, r))
    _assert(union == set(base) and set(original) <= union, "orbit union incomplete")
    expected_union = set()
    for point in original:
        current = point
        for _ in range(r):
            expected_union.add(current)
            current = _alpha(curve, current, multiplier)
            if current == point:
                break
    _assert(expected_union == set(base), "extraneous orbit completion")
    _assert([panel["m"] for panel in analysis["census"]] == list(lengths), "tuple-length coverage")
    for panel in analysis["census"]:
        m = panel["m"]
        def dp(points):
            counts = {None: 1}
            for _ in range(m):
                following = Histogram()
                for value, count in counts.items():
                    for point in points:
                        following[curve.add(value, point)] += count
                counts = following
            return counts
        complete_counts, original_counts = dp(base), dp(original)
        _assert(panel["original_histogram"] == [{"R": _encode(f, target), "count": original_counts.get(target, 0)} for target in group], "original census mismatch")
        _assert(panel["original_tuple_total"] == len(original)**m and panel["completed_tuple_total"] == len(base)**m, "first-moment total mismatch")
        _assert([_decode(f, item["R"]) for item in panel["targets"]] == group, "missing/reordered O or target cell")
        all_indices = set()
        for target_record in panel["targets"]:
            target = _decode(f, target_record["R"])
            variables = representatives+([target] if target is not None and target not in base else [])
            known_rows = []
            for i, point in enumerate(variables):
                if point in known:
                    row = [0]*(len(variables)+1)
                    row[i], row[-1] = 1, -known[point] % r
                    known_rows.append(row)
            known_rank = _independent_rank(known_rows, r)
            unknown = [i for i, point in enumerate(variables) if point not in known]
            def normalize(rows):
                return [[row[i] % r for i in unknown]+[sum(value*known[point] for value, point in zip(row, variables) if point in known) % r] for row in rows]
            def marginal(rows):
                normalized = normalize(rows)
                value = _independent_rank(known_rows+[row+[0] for row in rows], r)-known_rank
                _assert(_independent_rank(normalized, r) == value == _independent_rank([row[:-1] for row in normalized], r), "inconsistent public-normalized affine equations")
                return value
            tuples = target_record["tuples"]
            _assert(target_record["count"] == len(tuples) == complete_counts.get(target, 0), "target tuple count wrong")
            _assert(len(tuples) == len(set(map(tuple, tuples))), "duplicated tuples")
            expected_rows = [[], [], [], []]
            for indices, family in zip(tuples, target_record["transformed_families"]):
                _assert(len(indices) == m and all(isinstance(i, int) and 0 <= i < len(base) for i in indices), "invalid leg index")
                total = None
                for index in indices:
                    total = curve.add(total, base[index])
                _assert(total == target, "false actual point decomposition")
                all_indices.add(tuple(indices))
                rows = _rank_rows(base, representatives, lookup, target, indices, r)
                for destination, row in zip(expected_rows, rows):
                    destination.append(row)
                legs = [base[i] for i in indices]
                expected_family = [[], [], [], []]
                family_length = max((len(orbit) for orbit in analysis["orbits"]), default=1)
                _assert(len(family["legs"]) == family_length, "missing transformed family member")
                for t in range(family_length):
                    indices_t = [base.index(point) for point in legs]
                    _assert(indices_t == family["legs"][t], "false transformed leg")
                    weight = pow(eigenvalue, t, r)
                    transformed_total = None
                    for point in legs:
                        transformed_total = curve.add(transformed_total, point)
                    _assert(transformed_total == curve.mul(weight, target), "wrong target orbit weight")
                    rows_t = _rank_rows(base, representatives, lookup, target, indices_t, r, weight)
                    for destination, row in zip(expected_family, rows_t):
                        destination.append(row)
                    legs = [_alpha(curve, point, multiplier) for point in legs]
                _assert(family["rows"] == expected_family, "transformed row certificate mismatch")
                ranks = [_independent_rank(matrix, r) for matrix in expected_family]
                _assert(family["ranks"] == ranks and ranks[1] <= 1 and ranks[3] <= 1, "false transformed quotient rank")
                _assert(family["public_normalized_rows"] == normalize(expected_family[3]) and
                        family["marginal_new_rank"] == marginal(expected_family[3]) <= 1, "false normalized family rank")
                checked += 1
            _assert(len(target_record["transformed_families"]) == len(tuples), "missing family certificate")
            _assert(target_record["rows"] == expected_rows, "raw/quotient row mismatch")
            ranks = [_independent_rank(matrix, r) for matrix in expected_rows]
            _assert(target_record["ranks"] == ranks, "false fixed-target rank")
            expected_increments, formal_increments, previous, previous_formal = [], [], 0, 0
            for i in range(len(tuples)):
                formal = _independent_rank(expected_rows[3][:i+1], r)
                formal_increments.append(formal-previous_formal)
                previous_formal = formal
                value = marginal(expected_rows[3][:i+1])
                expected_increments.append(value-previous)
                previous = value
            _assert(target_record["new_constraint_rank_increments"] == expected_increments, "new rank increments wrong")
            _assert(target_record["formal_constraint_rank_increments"] == formal_increments, "formal rank increments wrong")
            useful = marginal(expected_rows[3])
            _assert(target_record["public_known_affine_constraints"] == known_rows and
                    target_record["public_known_rank"] == known_rank and
                    target_record["rank_with_public_known"] == useful+known_rank and
                    target_record["marginal_new_rank"] == useful and
                    target_record["public_normalized_rows"] == normalize(expected_rows[3]) and
                    target_record["unknown_quotient_columns"] == unknown, "public-known rank certificate mismatch")
            dimensions = [len(base)+(target is not None), len(representatives)+(target is not None),
                          len(base)+(target is not None and target not in base),
                          len(representatives)+(target is not None and target not in base)]
            _assert(target_record["dimensions"] == dimensions and target_record["homogeneous"] == (target is None)
                    and target_record["target_merged"] == (target is not None and target in base), "wrong fixed-target column policy")
        _assert(len(all_indices) == len(base)**m, "omitted ordered tuple coverage")
    return checked


def _check_lines(control):
    f = Field(control["p"], control["quadratic"])
    curve = Curve(f, control["A"], control["B"])
    ell = control["ell"]
    actual = [point for point in curve.points() if curve.mul(ell, point) is None]
    _assert([_decode(f, point) for point in control["torsion"]] == actual, "incomplete rational torsion")
    covered = set()
    for line in control["lines"]:
        point = _decode(f, line["P"])
        values = sorted((curve.mul(i, point) for i in range(ell)), key=_key)
        _assert([_decode(f, value) for value in line["line"]] == values and point is not None, "invalid torsion line")
        _assert(not (set(values)-{None}) & covered, "repeated torsion line")
        covered.update(set(values)-{None})
        images = [None if value is None else (f.mul(control["multiplier"], value[0]),
                                             f.mul(control["y_multiplier"], value[1])) for value in values]
        _assert([_decode(f, value) for value in line["images"]] == images, "torsion action wrong")
        stable = all(curve.is_on_curve(image) and image in values for image in images)
        scalars = [k for k in range(1, ell) if all(image == curve.mul(k, value) for value, image in zip(values, images))] if stable else []
        _assert(line["stable"] == stable and line["scalar_admitted"] == (stable and len(scalars) == 1), "nonstable line falsely admitted")
        _assert(line["lambda"] == (scalars[0] if len(scalars) == 1 else None), "false line eigenvalue")
    _assert(covered == set(actual)-{None}, "omitted rational cyclic line")
    return len(actual)


def _check_generic(control, p, coefficients, group_encoded, base_encoded, lengths):
    f = Field(p)
    curve = Curve(f, *coefficients)
    group = [_decode(f, point) for point in group_encoded]
    pairs = [(_decode(f, point), label) for point, label in control["point_label_bijection"]]
    mapping = dict(pairs)
    _assert([point for point, _ in pairs] == group and set(mapping.values()) == set(range(len(group))), "invalid generic relabeling")
    _assert(control["zero_label"] == mapping[None], "generic zero wrong")
    expected_table = [[mapping[a], mapping[b], mapping[curve.add(a, b)]] for a in group for b in group]
    _assert(control["addition_table"] == expected_table, "generic addition oracle wrong")
    base_labels = [mapping[_decode(f, point)] for point in base_encoded]
    _assert(control["base_labels"] == base_labels, "generic base mismatch")
    table = {(a, b): c for a, b, c in expected_table}
    _assert([row["m"] for row in control["histograms"]] == list(lengths), "generic m coverage")
    for row in control["histograms"]:
        counts = {mapping[None]: 1}
        for _ in range(row["m"]):
            following = Histogram()
            for a, n in counts.items():
                for b in base_labels:
                    following[table[a, b]] += n
            counts = following
        _assert(row["counts"] == [[label, counts.get(label, 0)] for label in range(len(group))], "generic tuple census wrong")
    return len(expected_table)


def check_result(result):
    """Validate exact frozen case coverage and actual certificates, not booleans."""
    required = {"schema_version", "direction", "seed", "parameters", "cases", "checks", "limitations", "work_accounting", "instrument_scope"}
    _assert(required <= set(result), "missing result fields")
    _assert(result["schema_version"] == SCHEMA and result["direction"] == "factorbase", "wrong result schema/direction")
    expected_parameters = {"target": [97, 0, 2], "alpha_x": 35, "auxiliary": [97, 1, 0],
                           "depths": [0, 1, 2, 3], "tuple_lengths": [2, 3],
                           "coset_schedule": "all rational finite image fibers; lex-source first slice identified"}
    _assert(result["parameters"] == expected_parameters, "changed frozen parameters")
    catalog = result["catalog"]
    _assert(catalog["p"] == 97 and catalog["depths"] == [0, 1, 2, 3]
            and catalog["target"]["A"] == 0 and catalog["target"]["B"] == 2, "changed catalog fixture")
    checked = check_catalog(catalog)
    expected_ids = ["target-admission", "target-alpha"]
    for entry in catalog["entries"]:
        expected_ids.append(f"depth-{entry['d']}")
        expected_ids.extend(f"d{entry['d']}-fiber-{fiber['index']}" for fiber in entry["finite_fibers"])
    expected_ids.append("rank2-all-lines")
    _assert([case["id"] for case in result["cases"]] == expected_ids, "deleted/reordered/extra planned case or control")
    cases = {case["id"]: case for case in result["cases"]}
    for case in result["cases"]:
        _assert({"id", "panel", "status", "inputs", "observables", "certificates", "work", "limits"} <= set(case), "incomplete case")
        _assert(case["status"] in {"measured", "zero_yield", "inadmissible", "bounded_instrument_stop", "invalid"}, "unknown shared case status")
    admission = catalog["target"]["admission"]
    _assert(cases["target-admission"]["certificates"] == admission, "admission case mismatch")
    _assert(cases["target-admission"]["status"] == ("measured" if admission["admitted"] else "inadmissible") and
            cases["target-admission"]["observables"] == {"admitted": admission["admitted"]}, "false target admission status")
    f, counter = Field(97), Counter()
    curve = Curve(f, 0, 2)
    group = [_decode(f, point) for point in admission["G"] or []]
    action = cases["target-alpha"]["certificates"]
    expected_action = action_certificate(curve, group, admission["r"], _decode(f, admission["P"]), 35) if admission["admitted"] else None
    _assert(action == expected_action, "all-G action/lambda certificate wrong")
    _assert(cases["target-alpha"]["observables"]["cube_root_condition"] == (pow(35, 3, 97) == 1), "cube-root condition wrong")
    _assert(cases["target-alpha"]["observables"]["admitted"] == bool(action and action["admitted"]) and
            cases["target-alpha"]["status"] == ("measured" if action and action["admitted"] else "inadmissible"), "false action status")
    for entry in catalog["entries"]:
        depth_case = cases[f"depth-{entry['d']}"]
        _assert(depth_case["certificates"] == {"kernel": entry["kernel"], "pole_paths": entry["pole_paths"]}, "missing kernel/pole control")
        _assert(depth_case["status"] == ("measured" if entry["complete_kernel"] else "inadmissible") and
                depth_case["observables"] == {"complete_kernel": entry["complete_kernel"], "rational_kernel_size": len(entry["kernel"]),
                    "finite_cosets": len(entry["finite_fibers"]), "duplicate_base_histogram": entry["duplicate_actual_base_histogram"]}, "false depth census status")
        for fiber in entry["finite_fibers"]:
            case = cases[f"d{entry['d']}-fiber-{fiber['index']}"]
            _assert(case["certificates"]["catalog_fiber"] == fiber, "fiber changed between case and catalog")
            admitted = bool(entry["complete_kernel"] and admission["admitted"] and action and action["admitted"])
            if not admitted:
                _assert(case["status"] == "inadmissible" and case["observables"]["max_separate_fixed_target_marginal_rank"] is None, "false complete-kernel/scalar admission")
            _assert(case["inputs"] == {"d": entry["d"], "fiber_index": fiber["index"], "A": fiber["A"], "B": fiber["B"]}, "wrong fiber inputs")
            _assert(case["observables"]["original_M"] == len(fiber["bases"]["list"])
                    and case["observables"]["first_coset_slice"] == (fiber["index"] == entry["first_coset_index"]), "wrong M/first-coset slice")
            _assert(case["observables"]["same_base_equality"] == (fiber["bases"]["list"] == fiber["bases"]["expanded"] == fiber["bases"]["chain"]) and
                    case["observables"]["p1_extra_target_points"] == [point for point in fiber["bases"]["p1_only"] if point not in fiber["bases"]["list"]], "false same-base or P1 control")
            if not admitted:
                _assert("analyses" not in case["certificates"], "invalid cell silently used for rank study")
                continue
            analyses = case["certificates"]["analyses"]
            _assert(set(analyses) == {"candidate", "identity_alpha", "size_matched_random_base", "random_coordinate_labels"}, "omitted base/control arm")
            base = fiber["bases"]["list"]
            _assert(analyses["candidate"]["original_base"] == base and analyses["identity_alpha"]["original_base"] == base, "same-base identity control mismatch")
            _assert(len(analyses["size_matched_random_base"]["original_base"]) == len(base), "random base not size matched")
            rng = random.Random(f"{result['seed']}:depth{entry['d']}:fiber{fiber['index']}")
            nonzero = [point for point in admission["G"] if point is not None]
            expected_random = rng.sample(nonzero, len(base))
            _assert(analyses["size_matched_random_base"]["original_base"] == expected_random, "changed seeded random base")
            permutation = list(range(97)); rng.shuffle(permutation)
            _assert(analyses["random_coordinate_labels"]["coordinate_permutation"] == permutation, "coordinate labels changed")
            source_x = {point[0][0] for point in fiber["points"]}
            _assert(analyses["random_coordinate_labels"]["original_base"] ==
                    [point for point in nonzero if permutation[point[0][0]] in source_x], "labeled base mismatch")
            for name, analysis in analyses.items():
                multiplier, eigenvalue = (1, 1) if name == "identity_alpha" else (35, action["lambda"])
                checked += check_analysis(analysis, 97, (0, 2), admission["G"], admission["r"], multiplier, eigenvalue, (2, 3))
            maximum_marginal = max((target["marginal_new_rank"] for panel in analyses["candidate"]["census"] for target in panel["targets"]), default=0)
            _assert(case["status"] == ("zero_yield" if maximum_marginal == 0 else "measured") and
                    case["observables"]["max_separate_fixed_target_marginal_rank"] == maximum_marginal, "false useful-yield summary/status")
            checked += _check_generic(case["certificates"]["generic_group"], 97, (0, 2), admission["G"], analyses["candidate"]["base"], (2, 3))
    rank2 = cases["rank2-all-lines"]["certificates"]
    _assert((rank2["p"], rank2["quadratic"], rank2["A"], rank2["B"], rank2["ell"], rank2["multiplier"]) ==
            (5, [1, 1], 0, 1, 3, [0, 1]), "changed rank2 fixture")
    checked += _check_lines(rank2)
    _assert(cases["rank2-all-lines"]["status"] == "measured" and cases["rank2-all-lines"]["observables"] ==
            {"line_count": len(rank2["lines"]), "nonstable_lines": sum(not line["stable"] for line in rank2["lines"])}, "false rank2 census")
    return {"certificate_items": checked, "scientific_validation": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    if args.check is not None:
        if args.output_dir is not None:
            parser.error("--check and --output-dir are exclusive")
        print(json.dumps(check_result(json.loads(args.check.read_text())), sort_keys=True))
        return 0
    if args.output_dir is None:
        parser.error("--output-dir required for execution")
    started = datetime.now(timezone.utc).isoformat()
    wall, cpu = time.monotonic(), time.process_time()
    result = run_experiment(args.seed)
    write_artifacts(result, args.output_dir, args.seed, started, wall, cpu)
    print(json.dumps({"direction": "factorbase", "cases": len(result["cases"]), "checks": result["checks"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
