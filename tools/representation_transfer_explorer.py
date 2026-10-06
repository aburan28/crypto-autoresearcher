#!/usr/bin/env python3
"""Bounded, offline representation-transfer laboratory (toy fields only).

This searches representation chains and checks maps; it has no DLP solver,
network integration, external-target loader, or production-curve execution.
"""
from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
from typing import Callable


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def __post_init__(self):
        if type(self.p) is not int or not 5 <= self.p <= 101 or any(
                self.p % d == 0 for d in range(2, math.isqrt(self.p) + 1)):
            raise ValueError("laboratory requires a prime field with 5 <= p <= 101")
        object.__setattr__(self, "a", self.a % self.p)
        object.__setattr__(self, "b", self.b % self.p)
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular elliptic curve")

    def contains(self, point):
        return point is None or (point[1]**2 - point[0]**3 - self.a*point[0] - self.b) % self.p == 0

    def points(self):
        return [None] + [(x, y) for x in range(self.p) for y in range(self.p)
                         if self.contains((x, y))]

    def add(self, left, right):
        if left is None:
            return right
        if right is None:
            return left
        x, y = left
        u, v = right
        if x == u and (y + v) % self.p == 0:
            return None
        slope = ((3*x*x + self.a) * pow(2*y, -1, self.p) if left == right
                 else (v-y) * pow(u-x, -1, self.p)) % self.p
        z = (slope*slope - x - u) % self.p
        return z, (slope*(x-z)-y) % self.p

    def mul(self, scalar, point):
        if scalar < 0:
            point = None if point is None else (point[0], -point[1] % self.p)
            scalar = -scalar
        out = None
        while scalar:
            if scalar & 1:
                out = self.add(out, point)
            point = self.add(point, point)
            scalar >>= 1
        return out

    def subgroup(self, generator):
        if generator is None or not self.contains(generator):
            raise ValueError("nonzero curve generator required")
        values = [None]
        point = generator
        for _ in range(2*self.p + 2):
            if point is None:
                return values
            values.append(point)
            point = self.add(point, generator)
        raise ValueError("point enumeration failed")


def identity(curve, generator, order, cofactor):
    """Same EC1 canonical preimage as tools/curve_identity.py; no new EC namespace."""
    field = {"characteristic": curve.p, "degree": 1, "representation": "prime-residue",
             "element_encoding": "integer"}
    record = {"model": "short-weierstrass", "a": curve.a, "b": curve.b,
              "subgroup_order": order, "cofactor": cofactor,
              "generator": list(generator), "target_group": "generator-subgroup"}
    sha = digest({"field": field, "curve": record})
    return {"curve_id": f"EC1P{curve.p.bit_length()}Ctoytransferh{sha[:12]}",
            "curve_uid": f"urn:ec-record:1:sha256:{sha}", "field": field, "curve": record}


def check_map(source: Curve, target: Curve, generator, transform: Callable):
    """Exhaustive homomorphism and scalar checks on the declared cyclic subgroup.

    A finite test certifies only this enumerated toy subgroup, not a general
    algebraic identity or a production parameter set. Injection is mandatory.
    """
    points = source.subgroup(generator)
    images = [transform(point) for point in points]
    checks = {"identity": images[0] is None,
              "on_curve": all(target.contains(point) for point in images),
              "injective": len(set(images)) == len(images),
              "scalar": all(images[k] == target.mul(k, images[1]) for k in range(len(points))),
              "homomorphism": all(transform(source.add(p, q)) == target.add(fp, fq)
                                  for p, fp in zip(points, images)
                                  for q, fq in zip(points, images))}
    return {"status": "verified_toy_subgroup" if all(checks.values()) else "rejected",
            "checks": checks, "subgroup_order": len(points),
            "source_curve": asdict(source), "target_curve": asdict(target),
            "source_generator": list(generator),
            "target_generator": list(images[1]) if images[1] is not None else None,
            "subgroup_sha256": digest(points),
            "pairs_checked": len(points)**2, "scope": "enumerated cyclic subgroup only"}


@dataclass
class Node:
    uid: str
    kind: str
    metadata: dict
    fingerprint: dict


@dataclass
class Edge:
    uid: str
    source: str
    target: str
    family: str
    status: str
    certificate: dict
    costs: dict
    obligations: list[str]


class Explorer:
    def __init__(self):
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}

    def add_node(self, kind, metadata, fingerprint):
        uid = "urn:representation:1:sha256:" + digest({"kind": kind, "metadata": metadata})
        node = Node(uid, kind, metadata, fingerprint)
        if uid in self.nodes and self.nodes[uid] != node:
            raise ValueError("conflicting node evidence; use a new record")
        self.nodes[uid] = node
        return uid

    def add_edge(self, source, target, family, status, certificate, costs=None, obligations=None):
        if source not in self.nodes or target not in self.nodes:
            raise ValueError("edge endpoints must exist")
        if status not in {"verified_toy_subgroup", "formula_checked", "unimplemented", "rejected"}:
            raise ValueError("unsupported evidence status")
        if status == "verified_toy_subgroup":
            required = {"identity", "on_curve", "injective", "scalar", "homomorphism"}
            checks = certificate.get("checks", {})
            if certificate.get("status") != status or set(checks) != required or any(
                    value is not True for value in checks.values()):
                raise ValueError("verified edge requires a passing certificate")
            for endpoint, prefix in ((source, "source"), (target, "target")):
                node = self.nodes[endpoint]
                metadata = node.metadata
                record = metadata.get("curve", {})
                parameters = {"p": metadata.get("field", {}).get("characteristic"),
                              "a": record.get("a"), "b": record.get("b")}
                if (node.kind != "elliptic" or parameters != certificate.get(prefix + "_curve") or
                        record.get("generator") != certificate.get(prefix + "_generator") or
                        record.get("subgroup_order") != certificate.get("subgroup_order")):
                    raise ValueError("map certificate does not bind these endpoint subgroups")
        costs = costs or {"construction": None, "evaluation": None, "memory": None,
                          "unit": "unmeasured"}
        for key in ("construction", "evaluation", "memory"):
            value = costs.get(key)
            if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError("costs must be finite, nonnegative, or null")
        data = {"source": source, "target": target, "family": family,
                "certificate": certificate}
        uid = "urn:transfer:1:sha256:" + digest(data)
        self.edges[uid] = Edge(uid, source, target, family, status, certificate,
                               costs, obligations or [])
        return uid

    def search(self, start, max_depth=3, max_paths=200, include_obligations=True):
        if start not in self.nodes or not 1 <= max_depth <= 8 or not 1 <= max_paths <= 10000:
            raise ValueError("invalid start or search limits")
        adjacency = {uid: [] for uid in self.nodes}
        for edge in sorted(self.edges.values(), key=lambda edge: edge.uid):
            if edge.status == "rejected":
                continue
            if include_obligations or edge.status == "verified_toy_subgroup":
                adjacency[edge.source].append(edge)
        queue = deque([(start, (), (start,))])
        paths = []
        truncated = False
        while queue:
            node, chain, visited = queue.popleft()
            if len(chain) >= max_depth:
                continue
            for edge in adjacency[node]:
                if edge.target in visited:
                    continue
                if len(paths) >= max_paths:
                    truncated = True
                    queue.clear()
                    break
                next_chain = chain + (edge.uid,)
                edges = [self.edges[uid] for uid in next_chain]
                families = list(dict.fromkeys(e.family for e in edges))
                paths.append({"edges": list(next_chain), "destination": edge.target,
                              "status": "verified_toy_chain" if all(
                                  e.status == "verified_toy_subgroup" for e in edges) else "obligation_chain",
                              "structural_diversity": len(families),
                              "novelty_status": "unassessed",
                              "families": families,
                              "cost": self.path_cost(edges),
                              "advantage": None,
                              "obligations": list(dict.fromkeys(
                                  item for e in edges for item in e.obligations)),
                              "reason": "destination solver and matched baseline are absent"})
                queue.append((edge.target, next_chain, visited + (edge.target,)))
        # Diversity is a scheduling signal, never a performance or novelty claim.
        paths.sort(key=lambda item: (-item["structural_diversity"], len(item["edges"]), item["edges"]))
        return {"paths": paths, "truncated": truncated, "max_depth": max_depth,
                "max_paths": max_paths, "coverage": "simple paths in generated toy graph only"}

    @staticmethod
    def path_cost(edges):
        units = {edge.costs.get("unit") for edge in edges}
        result = {"unit": next(iter(units)) if len(units) == 1 else "incomparable"}
        for key in ("construction", "evaluation", "memory"):
            values = [edge.costs.get(key) for edge in edges]
            result[key] = None if len(units) != 1 or any(v is None for v in values) else (
                max(values) if key == "memory" else sum(values))
        return result


def cost_assessment(baseline, destination, transfer, targets=1):
    """Compare supplied complete cost records; never infer cost from geometry.

    Units and workload must match. Successes, misses and setup must have
    already been charged by the producing benchmark. None remains unknown.
    """
    if type(targets) is not int or targets < 1:
        raise ValueError("targets must be positive")
    records = [baseline, destination, transfer]
    if any(record is None for record in records):
        return {"status": "unknown", "estimated_advantage": None}
    if len({record.get("unit") for record in records}) != 1 or not baseline.get("unit"):
        return {"status": "incomparable", "estimated_advantage": None}
    if any(not record.get("workload") for record in records) or len({
            record["workload"] for record in records}) != 1:
        return {"status": "incomparable", "estimated_advantage": None}
    for record in records:
        for key in ("setup", "online", "verification", "memory"):
            value = record.get(key)
            if value is None:
                return {"status": "unknown", "estimated_advantage": None}
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError("invalid cost record")
    total = lambda record: record["setup"] + targets*(record["online"] + record["verification"])
    old = total(baseline)
    new = total(destination) + total(transfer)
    return {"status": "model_estimate", "estimated_advantage": old/new if new > 0 else None,
            "baseline_total": old, "transferred_total": new, "targets": targets,
            "unit": baseline["unit"], "memory_upper_bound": destination["memory"] + transfer["memory"],
            "claim": "supplied model only; no demonstrated ECDLP speedup"}


# Polynomial Euclidean algorithm over F_p for the degree-six cover's smoothness.
def trim(poly):
    poly = list(poly)
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def remainder(left, right, p):
    left, right = trim(left), trim(right)
    while left != [0] and len(left) >= len(right):
        shift = len(left) - len(right)
        scale = left[-1]*pow(right[-1], -1, p) % p
        for i, coefficient in enumerate(right):
            left[i+shift] = (left[i+shift] - scale*coefficient) % p
        left = trim(left)
    return left


def squarefree(poly, p):
    derivative = trim([(i*poly[i]) % p for i in range(1, len(poly))])
    left, right = trim(poly), derivative
    while right != [0]:
        left, right = right, remainder(left, right, p)
    return len(left) == 1


def cover_check(curve):
    """C: y^2=x^6+a*x^2+b -> E: v^2=u^3+a*u+b, (u,v)=(x^2,y).

    Checks the polynomial substitution and smoothness. This is a CURVE map,
    not executable arithmetic in Jac(C). The induced pullback is an obligation.
    """
    poly = [curve.b, 0, curve.a, 0, 0, 0, 1]
    if not squarefree(poly, curve.p):
        return {"status": "rejected", "reason": "degree-six model is not squarefree"}
    # Exact coefficient identity, rather than inferring a formula from point samples.
    substituted = [curve.b, 0, curve.a, 0, 0, 0, 1]
    rational_points = [(x, y) for x in range(curve.p) for y in range(curve.p)
                       if (y*y - x**6 - curve.a*x*x - curve.b) % curve.p == 0]
    return {"status": "formula_checked", "genus": 2, "degree": 2,
            "model": {"field_prime": curve.p, "equation": "y^2=x^6+a*x^2+b",
                      "a": curve.a, "b": curve.b},
            "map": {"u": "x^2", "v": "y", "direction": "C -> E"},
            "checks": {"squarefree": True, "polynomial_identity": substituted == poly,
                       "affine_images_on_E": all(curve.contains((x*x % curve.p, y))
                                                 for x, y in rational_points)},
            "affine_points_checked": len(rational_points),
            "scope": "degree-two curve-cover formula; Jacobian group map not executed"}


def demo(max_depth=3, max_paths=200):
    started = time.perf_counter()
    curve = Curve(11, 1, 1)
    points = curve.points()
    candidates = [(len(curve.subgroup(p)), p) for p in points if p is not None]
    # Choose a prime-order subgroup so degree-two pullback injection has the
    # required coprimality. Never confuse ambient order with subgroup order.
    order, generator = max((n, p) for n, p in candidates if n > 2 and all(
        n % d for d in range(2, math.isqrt(n) + 1)))
    graph = Explorer()
    ident = identity(curve, generator, order, len(points)//order)
    start = graph.add_node("elliptic", ident, {"group_order": len(points),
                           "subgroup_order": order, "dimension": 1})
    elliptics = [(start, curve, generator)]
    # Fixed, bounded model family. Each destination's generator is bound explicitly.
    for scale in (2, 3):
        target = Curve(curve.p, curve.a*pow(scale, 4, curve.p), curve.b*pow(scale, 6, curve.p))
        forward = lambda p, s=scale: None if p is None else (
            p[0]*s*s % curve.p, p[1]*s*s*s % curve.p)
        target_generator = forward(generator)
        dest = graph.add_node("elliptic", identity(target, target_generator, order, len(points)//order),
                              {"group_order": len(points), "subgroup_order": order, "dimension": 1})
        cert = check_map(curve, target, generator, forward)
        cert["formula"] = {"x": "s^2*x", "y": "s^3*y", "s": scale}
        graph.add_edge(start, dest, "coordinate-isomorphism", cert["status"], cert)
        inverse_scale = pow(scale, -1, curve.p)
        backward = lambda p, s=inverse_scale: None if p is None else (
            p[0]*s*s % curve.p, p[1]*s*s*s % curve.p)
        back_cert = check_map(target, curve, target_generator, backward)
        back_cert["formula"] = {"x": "s^2*x", "y": "s^3*y", "s": inverse_scale}
        graph.add_edge(dest, start, "coordinate-isomorphism", back_cert["status"], back_cert)
        elliptics.append((dest, target, target_generator))
    for src, source_curve, _ in elliptics:
        cert = cover_check(source_curve)
        if cert["status"] == "rejected":
            continue
        jacobian = graph.add_node("jacobian", {"cover": cert["model"], "source_curve_uid":
                                 graph.nodes[src].metadata["curve_uid"]},
                                 {"genus": 2, "dimension": 2, "subgroup_order": order,
                                  "arithmetic": "unimplemented"})
        graph.add_edge(src, jacobian, "cover-pullback", "unimplemented", cert,
                       obligations=["Implement balanced divisor arithmetic for this degree-six model",
                                    "Implement f^*: E -> Jac(C), including points at infinity",
                                    "Check f_* f^*=[2] and exhaustive scalar preservation",
                                    "Prove injection on the selected subgroup",
                                    "Supply a non-IC, non-rho destination algorithm and matched cost evidence"])
    # Negative control: scalar preservation alone admits the zero map.
    zero_cert = check_map(curve, curve, generator, lambda point: None)
    graph.add_edge(start, start, "zero-map-control", zero_cert["status"], zero_cert)
    search = graph.search(start, max_depth, max_paths)
    return {"schema": "representation-transfer-explorer/v1", "scope": "fixed F_11 toy instance",
            "source": start, "nodes": [asdict(n) for n in graph.nodes.values()],
            "edges": [asdict(e) for e in graph.edges.values()], "search": search,
            "summary": {"nodes": len(graph.nodes), "edges": len(graph.edges),
                        "paths": len(search["paths"]),
                        "verified_toy_chains": sum(p["status"] == "verified_toy_chain" for p in search["paths"]),
                        "demonstrated_speedup": False, "destination_solver": "absent"},
            "environment": {"python": sys.version, "platform": platform.platform()},
            "development_elapsed_seconds": time.perf_counter()-started,
            "claim_tier": "software demonstration; not archived scientific evidence"}


def markdown(result):
    lines = ["# Representation transfer explorer", "", result["scope"], "",
             "A map certificate and a speedup certificate are separate obligations.", "",
             "| Family | Status | Missing work |", "| --- | --- | --- |"]
    for edge in result["edges"]:
        lines.append(f"| {edge['family']} | {edge['status']} | {'; '.join(edge['obligations']) or 'Destination cost evidence'} |")
    lines += ["", f"Paths retained: {result['summary']['paths']}; search truncated: {result['search']['truncated']}.",
              "", "No destination DLP algorithm or measured logarithm speedup is implemented.",
              "The cover formula is checked; the induced Jacobian map remains unimplemented."]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["demo"])
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--max-paths", type=int, default=200)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        result = demo(args.max_depth, args.max_paths)
    except ValueError as exc:
        parser.error(str(exc))
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        # Development outputs must not silently overwrite previous observations.
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
    else:
        print(encoded, end="")
    if args.report:
        with args.report.open("x", encoding="utf-8") as stream:
            stream.write(markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
