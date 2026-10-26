#!/usr/bin/env python3
"""Independent public-equation and causal-trace checker, development version.

No producer arithmetic, private scalar labels, or third-party modules are used.
This checks recorded equations/state transitions, not execution attestation,
isolation, native counter accuracy, or scientific/performance qualification.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass, field
from math import isqrt
from pathlib import Path
from typing import Any, Iterable

MASK64 = (1 << 64) - 1
SCHEMA = "classical.ecdlp.endpoint-reuse.row.v1"
SCOPE = "classical_ecdlp_endpoint_reuse"
ARMS = {"static_full", "static_small", "harvest", "harvest_disabled", "rho_reference"}
STATUSES = {"solved", "failed", "censored", "invalid"}
Point = tuple[int, int] | None


class Invalid(ValueError):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Invalid(message)


def integer(value: Any, name: str, minimum: int = 0, maximum: int = MASK64) -> int:
    need(type(value) is int and minimum <= value <= maximum, f"invalid {name}")
    return value


def boolean(value: Any, name: str) -> bool:
    need(type(value) is bool, f"invalid {name}")
    return value


def text(value: Any, name: str) -> str:
    need(isinstance(value, str) and bool(value), f"invalid {name}")
    return value


def prime(n: int) -> bool:
    """Exact trial division in the declared small-parameter verification domain."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, isqrt(n) + 1, 2))


def mix64(value: int) -> int:
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    return (value ^ (value >> 31)) & MASK64


def rotl64(value: int, count: int) -> int:
    return ((value << count) | (value >> (64 - count))) & MASK64


def fingerprint(point: Point) -> int:
    if point is None:
        return mix64(0x6F726465722D6964)
    x, y = point
    return mix64(x ^ rotl64(y, 32) ^ 0x706F696E742D7631)


def table_hash(entries: Iterable[tuple[int, int]]) -> int:
    result = 0
    for fp, exponent in entries:
        result ^= mix64(fp ^ rotl64(exponent, 17) ^ 0x65726C61622D7631)
    return result


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int

    def point(self, value: Any, name: str = "point") -> Point:
        need(isinstance(value, dict), f"invalid {name} object")
        x = integer(value.get("x"), f"{name}.x", maximum=self.p - 1)
        y = integer(value.get("y"), f"{name}.y", maximum=self.p - 1)
        infinity = boolean(value.get("infinity"), f"{name}.infinity")
        if infinity:
            need(x == 0 and y == 0, "noncanonical identity")
            return None
        point = (x, y)
        need(self.on_curve(point), f"{name} is not on curve")
        return point

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return 0 <= x < self.p and 0 <= y < self.p and (y * y - x * x * x - self.a * x - self.b) % self.p == 0

    def double_j(self, point: tuple[int, int, int]) -> tuple[int, int, int]:
        x, y, z = point
        if not z or not y:
            return (0, 1, 0)
        p = self.p
        yy = y * y % p
        yyyy = yy * yy % p
        zz = z * z % p
        s = 4 * x * yy % p
        m = (3 * x * x + self.a * zz * zz) % p
        u = (m * m - 2 * s) % p
        return (u, (m * (s - u) - 8 * yyyy) % p, 2 * y * z % p)

    def add_j(self, left: tuple[int, int, int], right: tuple[int, int, int]) -> tuple[int, int, int]:
        x1, y1, z1 = left
        x2, y2, z2 = right
        if not z1:
            return right
        if not z2:
            return left
        p = self.p
        z1z1, z2z2 = z1 * z1 % p, z2 * z2 % p
        u1, u2 = x1 * z2z2 % p, x2 * z1z1 % p
        s1, s2 = y1 * z2 * z2z2 % p, y2 * z1 * z1z1 % p
        if u1 == u2:
            return self.double_j(left) if s1 == s2 else (0, 1, 0)
        h = (u2 - u1) % p
        i = 4 * h * h % p
        j = h * i % p
        r = 2 * (s2 - s1) % p
        v = u1 * i % p
        x = (r * r - j - 2 * v) % p
        return (x, (r * (v - x) - 2 * s1 * j) % p, ((z1 + z2) ** 2 - z1z1 - z2z2) * h % p)

    def affine(self, point: tuple[int, int, int]) -> Point:
        x, y, z = point
        if not z:
            return None
        inverse = pow(z, self.p - 2, self.p)
        square = inverse * inverse % self.p
        return (x * square % self.p, y * square * inverse % self.p)

    def multiply(self, point: Point, scalar: int) -> Point:
        need(type(scalar) is int and scalar >= 0 and self.on_curve(point), "bad multiplication input")
        result = (0, 1, 0)
        base = (0, 1, 0) if point is None else (*point, 1)
        while scalar:
            if scalar & 1:
                result = self.add_j(result, base)
            base = self.double_j(base)
            scalar >>= 1
        return self.affine(result)

    def add(self, left: Point, right: Point) -> Point:
        l = (0, 1, 0) if left is None else (*left, 1)
        r = (0, 1, 0) if right is None else (*right, 1)
        return self.affine(self.add_j(l, r))


@dataclass(frozen=True)
class Fixture:
    identifier: str
    curve: Curve
    base: Point
    order: int
    total_order: int

    def validate(self) -> None:
        c = self.curve
        need(3 < c.p < 1 << 20 and prime(c.p), "unsupported or composite field")
        need(0 <= c.a < c.p and 0 <= c.b < c.p, "noncanonical curve coefficients")
        need((4 * c.a ** 3 + 27 * c.b ** 2) % c.p != 0, "singular curve")
        need(2 < self.order < 1 << 19 and prime(self.order), "unsupported or nonprime subgroup order")
        need(self.base is not None and c.on_curve(self.base), "invalid generator")
        need(c.multiply(self.base, self.order) is None, "generator order equation failed")
        radius = isqrt(4 * c.p)
        need(abs(self.total_order - (c.p + 1)) <= radius and self.total_order % self.order == 0, "total-order assertion fails Hasse/divisibility")
        # This independently rules out two independent rational r-torsion generators.
        need(c.p + 1 + radius < self.order * self.order, "P-subgroup uniqueness not established by Hasse")


@dataclass(frozen=True)
class Target:
    fixture: str
    replicate: int
    identifier: str
    ordinal: int
    point: Point


@dataclass(frozen=True)
class Setting:
    cell_id: str
    fixture: str
    replicate: int
    dp_bits: int
    initial_chains: int
    endpoint_cap: int
    max_precomp_ops: int
    max_online_ops: int
    seed: int


def tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        need(reader.fieldnames is not None and len(set(reader.fieldnames)) == len(reader.fieldnames), "bad TSV header")
        forbidden = {"k", "secret", "secret_scalar", "hidden_scalar", "truth", "scalar_truth", "private_scalar"}
        need(not forbidden.intersection(reader.fieldnames), "private-label column is not an accepted public input")
        rows = list(reader)
    need(rows and all(None not in row and None not in row.values() for row in rows), "empty/malformed TSV")
    return rows


def load_fixtures(path: Path) -> dict[str, Fixture]:
    fixtures: dict[str, Fixture] = {}
    for row in tsv(path):
        required = {"fixture_id", "p", "a", "b", "gx", "gy", "r", "N"}
        need(required <= row.keys(), "fixture TSV columns")
        identifier = text(row["fixture_id"], "fixture id")
        need(identifier not in fixtures, "duplicate fixture id")
        c = Curve(int(row["p"]), int(row["a"]), int(row["b"]))
        f = Fixture(identifier, c, (int(row["gx"]), int(row["gy"])), int(row["r"]), int(row["N"]))
        f.validate()
        fixtures[identifier] = f
    return fixtures


def load_targets(path: Path, fixtures: dict[str, Fixture]) -> dict[tuple[str, int, str], Target]:
    targets: dict[tuple[str, int, str], Target] = {}
    ordinals: set[tuple[str, int, int]] = set()
    for row in tsv(path):
        required = {"fixture_id", "replicate", "target_id", "target_ordinal", "qx", "qy", "infinity"}
        need(required <= row.keys(), "target TSV columns")
        fid, rid, identifier, ordinal = row["fixture_id"], int(row["replicate"]), row["target_id"], int(row["target_ordinal"])
        need(fid in fixtures and rid >= 0 and identifier and ordinal >= 0, "bad target identity")
        need(row["infinity"] in {"0", "1"}, "bad target infinity flag")
        f = fixtures[fid]
        q = f.curve.point({"x": int(row["qx"]), "y": int(row["qy"]), "infinity": row["infinity"] == "1"}, "target")
        need(f.curve.multiply(q, f.order) is None, "target is outside prime-order subgroup")
        key = (fid, rid, identifier)
        need(key not in targets and (fid, rid, ordinal) not in ordinals, "duplicate target identity/ordinal")
        targets[key] = Target(fid, rid, identifier, ordinal, q)
        ordinals.add((fid, rid, ordinal))
    return targets


def load_settings(path: Path, fixtures: dict[str, Fixture], targets: dict[tuple[str, int, str], Target]) -> dict[str, Setting]:
    settings: dict[str, Setting] = {}
    groups: set[tuple[str, int]] = set()
    for row in tsv(path):
        required = {"cell_id", "fixture_id", "replicate", "dp_bits", "initial_chains", "endpoint_cap", "max_precomp_ops", "max_online_ops", "seed"}
        need(required <= row.keys(), "settings TSV columns")
        cell, fid = text(row["cell_id"], "settings cell"), text(row["fixture_id"], "settings fixture")
        rep = integer(int(row["replicate"]), "settings replicate")
        need(fid in fixtures and cell not in settings and (fid, rep) not in groups, "duplicate/unknown settings cell")
        dp = integer(int(row["dp_bits"]), "settings DP bits", maximum=63)
        cap = integer(int(row["endpoint_cap"]), "settings cap", minimum=1, maximum=fixtures[fid].order)
        initial = integer(int(row["initial_chains"]), "settings initial chains", minimum=1, maximum=cap)
        settings[cell] = Setting(cell, fid, rep, dp, initial, cap, integer(int(row["max_precomp_ops"]), "settings precomp limit"), integer(int(row["max_online_ops"]), "settings online limit"), integer(int(row["seed"]), "settings seed", minimum=1))
        groups.add((fid, rep))
    need(groups == {(fid, rep) for fid, rep, _ in targets}, "settings/public target cell coverage differs")
    return settings


@dataclass
class PendingTarget:
    target: Target
    known_before: int
    pending: dict[int, tuple[int, int, Point]] = field(default_factory=dict)
    proposals: list[tuple[int, int]] = field(default_factory=list)
    proposed_slots: set[int] = field(default_factory=set)
    verified_scalar: int | None = None
    ready: bool = False
    lookups: int = 0
    witness_checks: int = 0
    terminal_count: int = 0
    peak_pending: int = 0
    lookup_context: tuple[int, int, int] | None = None
    lookup_witness_indices: set[int] = field(default_factory=set)
    rejected_witnesses: int = 0
    unmatched_dp: int = 0
    chain_limits: int = 0
    capacity_drops: int = 0


@dataclass
class Cell:
    key: tuple[str, int, str, str]
    fixture: Fixture
    arm: str
    capacity: int
    dp_bits: int
    setup_status: str
    initial_count: int
    expected_hash: int
    known: list[tuple[int, int]] = field(default_factory=list)
    active: PendingTarget | None = None
    completed_targets: set[str] = field(default_factory=set)
    last_ordinal: int = -1
    setup_finalized: bool = False

    @property
    def mask(self) -> int:
        return (1 << self.dp_bits) - 1

    def finish_setup(self) -> None:
        if self.setup_finalized:
            return
        need(len(self.known) == self.initial_count, "missing initial endpoint witnesses")
        need(len({e for _, e in self.known}) == len(self.known), "duplicate initial endpoint exponent")
        need(self.known == sorted(self.known, key=lambda x: x[0]), "initial endpoint prefix not fingerprint sorted")
        need(table_hash(self.known) == self.expected_hash, "initial table audit hash differs")
        self.setup_finalized = True


class Checker:
    def __init__(self, fixtures: dict[str, Fixture], targets: dict[tuple[str, int, str], Target], expected_arms: set[str], settings: dict[str, Setting] | None = None):
        need(expected_arms and expected_arms <= ARMS, "unsupported expected arms")
        self.fixtures = fixtures
        self.targets = targets
        self.expected_arms = expected_arms
        self.settings = settings
        self.cell_identity: dict[tuple[str, int, str], str] = {}
        self.cells: dict[tuple[str, int, str, str], Cell] = {}
        self.coverage: set[tuple[str, int, str, str]] = set()
        self.results: list[dict[str, Any]] = []
        self.rows = 0

    def key(self, row: dict[str, Any]) -> tuple[str, int, str, str]:
        need(row.get("schema") == SCHEMA and row.get("scope") == SCOPE, "row schema/scope mismatch")
        fid = text(row.get("fixture"), "fixture")
        rid = integer(row.get("replicate"), "replicate")
        arm = text(row.get("arm"), "arm")
        cell_id = text(row.get("cell_id"), "cell id")
        need(fid in self.fixtures and arm in self.expected_arms, "unknown fixture/arm")
        if self.settings is not None:
            need(cell_id in self.settings, "cell absent from public settings")
            setting = self.settings[cell_id]
            need((fid, rid) == (setting.fixture, setting.replicate), "cell identity differs from public settings")
        return (fid, rid, arm, cell_id)

    def arena(self, row: dict[str, Any], cell: Cell, pending: PendingTarget | None, allow_final: bool = False) -> None:
        known = integer(row.get("known_count"), "known_count")
        count = integer(row.get("pending_count"), "pending_count")
        cap = integer(row.get("endpoint_cap"), "endpoint_cap")
        need(cap == cell.capacity and known + count <= cap, "endpoint arena capacity violation")
        if not allow_final:
            need(known == len(cell.known), "known prefix changed before commit")
            need(count == (len(pending.pending) if pending else 0), "pending count differs from staged witnesses")

    def target(self, row: dict[str, Any], cell: Cell) -> PendingTarget:
        cell.finish_setup()
        identifier = text(row.get("target_id"), "target id")
        key = (cell.key[0], cell.key[1], identifier)
        need(key in self.targets, "target not in public inputs")
        target = self.targets[key]
        need(integer(row.get("target_ordinal"), "target ordinal") == target.ordinal, "target ordinal differs from public input")
        need(identifier not in cell.completed_targets, "duplicate completed target")
        if cell.active is None:
            need(target.ordinal > cell.last_ordinal, "target order is not increasing")
            cell.active = PendingTarget(target, len(cell.known))
        else:
            need(cell.active.target.identifier == identifier, "interleaved unfinished targets in one cell")
        return cell.active

    def ingest(self, row: dict[str, Any]) -> None:
        need(isinstance(row, dict), "JSON row must be an object")
        self.rows += 1
        key = self.key(row)
        kind = row.get("row_kind")
        f = self.fixtures[key[0]]
        if kind == "fixture_validation":
            need(row.get("order") == f.order and row.get("total_order") == f.total_order, "fixture validation order mismatch")
            need(f.curve.point(row.get("base"), "base") == f.base, "fixture validation generator mismatch")
            curve = row.get("curve")
            need(isinstance(curve, dict) and (curve.get("p"), curve.get("a"), curve.get("b")) == (f.curve.p, f.curve.a, f.curve.b), "fixture validation curve mismatch")
            return
        if kind == "setup":
            need(key not in self.cells, "duplicate setup")
            identity = key[:3]
            need(identity not in self.cell_identity, "multiple independently initialized tables for one fixture/replicate/arm")
            self.cell_identity[identity] = key[3]
            status = row.get("status")
            need(status in {"ready", "failed", "censored", "invalid"}, "invalid setup status")
            cap = integer(row.get("endpoint_cap"), "endpoint cap")
            count = integer(row.get("known_count"), "initial known count", maximum=cap)
            params = row.get("parameters")
            need(isinstance(params, dict), "missing setup parameters")
            bits = integer(params.get("dp_bits"), "DP bits", maximum=63)
            if key[2] != "rho_reference" and status == "ready":
                need(cap > 0 and count > 0, "nonempty verified seed table required")
            if key[2] == "rho_reference":
                need(count == 0, "rho reference has no endpoint entries")
            if self.settings is not None:
                setting = self.settings[key[3]]
                need(cap == setting.endpoint_cap and bits == setting.dp_bits, "setup cap/DP bits differ from frozen settings")
                for name, expected in [("initial_chains", setting.initial_chains), ("endpoint_cap", setting.endpoint_cap), ("max_precomp_ops", setting.max_precomp_ops), ("max_online_ops", setting.max_online_ops), ("seed", setting.seed), ("threads", 1), ("walks", 1), ("early_abort", False)]:
                    need(params.get(name) == expected, f"setup parameter {name} differs from frozen settings")
                requested = setting.endpoint_cap if key[2] == "static_full" else (0 if key[2] == "rho_reference" else setting.initial_chains)
                need(params.get("requested_build_chains") == requested, "requested setup work differs from frozen arm")
            self.cells[key] = Cell(key, f, key[2], cap, bits, status, count, integer(row.get("table_state_hash64"), "table hash"))
            return
        need(key in self.cells, "row before setup")
        cell = self.cells[key]
        if kind == "initial_endpoint":
            need(not cell.setup_finalized and cell.active is None, "late initial endpoint witness")
            index = integer(row.get("index"), "endpoint index")
            need(index == len(cell.known) and index < cell.initial_count, "initial endpoint index gap/overflow")
            exponent = integer(row.get("exponent"), "initial exponent", maximum=f.order - 1)
            fp = integer(row.get("fp"), "initial fingerprint")
            point = f.curve.multiply(f.base, exponent)
            need(fp == fingerprint(point) and (fp & cell.mask) == 0, "initial endpoint fingerprint/DP equation failed")
            cell.known.append((fp, exponent))
            return
        pending = self.target(row, cell)
        if kind == "terminal":
            need(cell.arm == "harvest" and not pending.ready and pending.verified_scalar is None, "terminal outside enabled preverification phase")
            reason = row.get("reason")
            need(reason in {"unmatched_dp", "chain_limit"}, "unknown terminal reason")
            point = f.curve.point(row.get("point"), "terminal point")
            a = integer(row.get("offset_a"), "terminal offset", maximum=f.order - 1)
            fp = integer(row.get("fp"), "terminal fingerprint")
            attempt = integer(row.get("attempt"), "terminal attempt", minimum=1)
            need(point == f.curve.add(pending.target.point, f.curve.multiply(f.base, a)), "terminal D=Q+aP equation failed")
            need(fp == fingerprint(point), "terminal fingerprint equation failed")
            slot = row.get("pending_slot")
            if slot == MASK64:
                slot = None
            if reason == "unmatched_dp":
                need((fp & cell.mask) == 0, "non-DP terminal marked as DP")
                need(pending.lookup_context == (attempt, fp, a), "unmatched terminal lacks its lookup")
                bucket = {i for i, entry in enumerate(cell.known) if entry[0] == fp}
                need(pending.lookup_witness_indices == bucket, "unmatched terminal omits known-bucket equation checks")
                need(all(f.curve.multiply(f.base, cell.known[i][1]) != point for i in bucket), "matched endpoint marked as unmatched")
                pending.unmatched_dp += 1
                if slot is not None:
                    slot = integer(slot, "pending slot")
                    need(slot == len(cell.known) + len(pending.pending), "pending slot is not next arena slot")
                    need(slot < cell.capacity, "pending insertion beyond arena cap")
                    pending.pending[slot] = (fp, a, point)
                    pending.peak_pending = max(pending.peak_pending, len(pending.pending))
                else:
                    need(len(cell.known) + len(pending.pending) == cell.capacity, "DP dropped before arena filled")
                    pending.capacity_drops += 1
            else:
                need((fp & cell.mask) != 0 and slot is None, "chain-limit terminal admitted or is distinguished")
                pending.chain_limits += 1
            pending.lookup_context = None
            pending.lookup_witness_indices.clear()
            pending.terminal_count += 1
            self.arena(row, cell, pending)
            return
        if kind == "lookup":
            need(cell.arm == "harvest" and pending.verified_scalar is None, "lookup after public solution or on disabled path")
            self.arena(row, cell, pending)
            need(row.get("lookup_begin") == 0 and row.get("lookup_end_exclusive") == len(cell.known), "lookup includes pending/unallocated arena")
            fp = integer(row.get("fp"), "lookup fingerprint")
            a = integer(row.get("offset_a"), "lookup offset", maximum=f.order - 1)
            attempt = integer(row.get("attempt"), "lookup attempt", minimum=1)
            need(pending.lookup_context is None, "lookup before prior terminal/witness was resolved")
            point = f.curve.add(pending.target.point, f.curve.multiply(f.base, a))
            need(fp == fingerprint(point) and (fp & cell.mask) == 0, "lookup fingerprint/DP equation failed")
            pending.lookup_context = (attempt, fp, a)
            pending.lookup_witness_indices.clear()
            pending.lookups += 1
            return
        if kind == "lookup_witness":
            need(cell.arm == "harvest" and pending.verified_scalar is None, "lookup witness after public solution or on disabled path")
            self.arena(row, cell, pending)
            index = integer(row.get("entry_index"), "lookup index")
            need(index < len(cell.known), "lookup used pending endpoint")
            fp = integer(row.get("fp"), "witness fingerprint")
            exponent = integer(row.get("exponent"), "witness exponent", maximum=f.order - 1)
            a = integer(row.get("offset_a"), "witness offset", maximum=f.order - 1)
            candidate = integer(row.get("candidate_scalar"), "candidate scalar", maximum=f.order - 1)
            attempt = integer(row.get("attempt"), "witness attempt", minimum=1)
            need(pending.lookup_context == (attempt, fp, a), "witness lacks its lookup")
            need(index not in pending.lookup_witness_indices, "repeated lookup witness")
            need(cell.known[index] == (fp, exponent), "lookup witness differs from known prefix")
            need(candidate == (exponent - a) % f.order, "lookup candidate subtraction failed")
            need(row.get("public_equation_checked") is True, "lookup candidate lacks equation check")
            truth = f.curve.multiply(f.base, candidate) == pending.target.point
            need(boolean(row.get("verified"), "lookup verified flag") == truth, "lookup witness verification flag differs")
            pending.lookup_witness_indices.add(index)
            if not truth:
                pending.rejected_witnesses += 1
            pending.witness_checks += 1
            return
        if kind == "verified_solution":
            need(cell.arm == "harvest" and pending.verified_scalar is None and not pending.ready, "duplicate/out-of-order verified solution")
            self.arena(row, cell, pending)
            x = integer(row.get("verified_scalar"), "verified scalar", maximum=f.order - 1)
            need(row.get("public_equation_checked") is True and f.curve.multiply(f.base, x) == pending.target.point, "public solution equation failed")
            if "point" in row:
                need(f.curve.point(row["point"], "verified target") == pending.target.point, "verified target point differs")
            pending.verified_scalar = x
            pending.lookup_context = None
            pending.lookup_witness_indices.clear()
            return
        if kind == "harvest_proposal":
            need(cell.arm == "harvest" and pending.verified_scalar is not None and not pending.ready, "proposal before public scalar verification")
            self.arena(row, cell, pending)
            slot = integer(row.get("pending_slot"), "proposal slot")
            need(slot in pending.pending and slot not in pending.proposed_slots, "unknown/repeated pending proposal")
            # Producer activation iterates its original pending slots in arena order.
            need(slot == len(cell.known) + len(pending.proposed_slots), "proposal order differs from pending arena")
            fp, a, point = pending.pending[slot]
            exponent = integer(row.get("exponent"), "proposed exponent", maximum=f.order - 1)
            need(row.get("fp") == fp and exponent == (pending.verified_scalar + a) % f.order, "promoted exponent x+a failed")
            need(f.curve.multiply(f.base, exponent) == point, "promoted exponent does not label terminal")
            duplicate = exponent in {e for _, e in cell.known + pending.proposals}
            accepted = boolean(row.get("accepted"), "proposal accepted")
            need(accepted == (not duplicate), "exact exponent deduplication differs")
            if accepted:
                pending.proposals.append((fp, exponent))
            pending.proposed_slots.add(slot)
            return
        if kind == "harvest_commit_ready":
            need(cell.arm == "harvest" and pending.verified_scalar is not None and not pending.ready, "commit-ready before public verification")
            self.arena(row, cell, pending)
            need(len(pending.proposed_slots) == len(pending.pending), "unproposed pending endpoints")
            need(row.get("accepted_count") == len(pending.proposals), "commit-ready accepted count differs")
            pending.ready = True
            return
        need(kind == "target", "unknown row kind")
        status = row.get("status")
        need(status in STATUSES, "unknown target status")
        upstream = integer(row.get("upstream_status"), "upstream status", maximum=7)
        expected_status = "solved" if upstream == 0 else ("censored" if upstream in {3, 4} else ("invalid" if upstream in {1, 6} else "failed"))
        need(status == expected_status, "producer status differs from retained upstream outcome")
        need(f.curve.point(row.get("point"), "recorded target") == pending.target.point, "final target differs from public inputs")
        x = row.get("verified_scalar")
        need(boolean(row.get("public_equation_checked"), "final equation-check flag") == (x is not None), "final equation-check flag has no matching witness")
        if x is not None:
            x = integer(x, "final scalar", maximum=f.order - 1)
            need(row.get("public_equation_checked") is True and f.curve.multiply(f.base, x) == pending.target.point, "final public witness equation failed")
        if status == "solved":
            need(cell.setup_status == "ready" and x is not None, "solved status without ready setup/verified scalar")
        committed = boolean(row.get("harvest_committed"), "harvest committed flag")
        if cell.arm == "harvest":
            if status == "solved":
                need(pending.verified_scalar == x and pending.ready and committed, "solved harvest without verified commit sequence")
            if committed:
                need(status == "solved" and pending.ready, "activation on unsuccessful target")
                cell.known = sorted(cell.known + pending.proposals)
            else:
                need(status != "solved", "successful harvest did not commit")
        else:
            need(not pending.pending and not pending.proposals and not committed, "nonharvest arm changed endpoint table")
        self.arena(row, cell, None)
        need(row.get("table_state_hash64") == table_hash(cell.known), "final table audit hash differs")
        need(len({e for _, e in cell.known}) == len(cell.known), "duplicate final exponents")
        reuse = row.get("reuse")
        if cell.arm == "harvest":
            need(isinstance(reuse, dict), "harvest row lacks reuse state counters")
            for name, expected in [("known_before", pending.known_before), ("known_after", len(cell.known)), ("capacity", cell.capacity), ("pending_peak", pending.peak_pending)]:
                need(reuse.get(name) == expected, f"reuse.{name} differs from public trace")
            for name, expected in [("unmatched_dp", pending.unmatched_dp), ("chain_limit_restarts", pending.chain_limits), ("staged", len(pending.pending)), ("capacity_rejections", pending.capacity_drops), ("bucket_candidates_verified", pending.witness_checks), ("rejected_bucket_witnesses", pending.rejected_witnesses), ("proposed", len(pending.proposed_slots)), ("duplicates", len(pending.proposed_slots) - len(pending.proposals))]:
                need(reuse.get(name) == expected, f"reuse.{name} differs from public trace")
            if committed:
                need(reuse.get("inserted") == len(pending.proposals), "reuse.inserted differs from accepted proposals")
            else:
                need(reuse.get("inserted") == 0 and reuse.get("rolled_back") == len(pending.pending), "failed harvest did not discard its pending arena")
        coverage = (key[0], key[1], pending.target.identifier, key[2])
        need(coverage not in self.coverage, "duplicate target/arm coverage")
        self.coverage.add(coverage)
        self.results.append({"fixture": key[0], "replicate": key[1], "target_id": pending.target.identifier, "target_ordinal": pending.target.ordinal, "arm": key[2], "producer_status": status, "producer_upstream_status": upstream, "public_witness_verified": x is not None, "trace_integrity": "pass", "retained_terminal_equations": pending.terminal_count, "lookup_ranges_checked": pending.lookups, "lookup_witnesses_checked": pending.witness_checks, "promotions_checked": len(pending.proposed_slots), "insertions_committed": len(pending.proposals) if committed else 0, "endpoint_known_after": len(cell.known), "endpoint_pending_peak": pending.peak_pending, "endpoint_capacity": cell.capacity})
        cell.completed_targets.add(pending.target.identifier)
        cell.last_ordinal = pending.target.ordinal
        cell.active = None

    def finish(self) -> dict[str, Any]:
        for cell in self.cells.values():
            cell.finish_setup()
            need(cell.active is None, "truncated unfinished target event stream")
        expected = {(fid, rep, tid, arm) for fid, rep, tid in self.targets for arm in self.expected_arms}
        missing = expected - self.coverage
        need(not missing and self.coverage == expected, f"target coverage differs: {len(missing)} missing cases")
        return {"schema": "classical.ecdlp.endpoint-reuse.public-verification.v1", "status": "public_equations_and_trace_pass", "raw_rows": self.rows, "public_fixtures": len(self.fixtures), "public_target_ids": len(self.targets), "target_arm_cases": len(self.results), "expected_arms": sorted(self.expected_arms), "settings_cells": len(self.settings) if self.settings is not None else None, "producer_cells": len(self.cells), "verified_case_witnesses": sum(r["public_witness_verified"] for r in self.results), "producer_status_counts": {s: sum(r["producer_status"] == s for r in self.results) for s in sorted(STATUSES)}, "retained_terminal_equations": sum(r["retained_terminal_equations"] for r in self.results), "promotions_checked": sum(r["promotions_checked"] for r in self.results), "arithmetic": "independently_coded_python_Jacobian", "hidden_scalar_labels_read": False, "total_curve_order_independently_counted": False, "native_cost_counters_verified": False, "execution_or_isolation_attested": False, "scientific_review_or_performance_qualification": False, "table_state_hash64_is_cryptographic": False}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def verify(fixtures_path: Path, targets_path: Path, settings_path: Path, raw_paths: list[Path], expected_arms: set[str], output: Path) -> int:
    need(not output.exists(), "refusing to overwrite verification output directory")
    output.mkdir(parents=True)
    summary: dict[str, Any]
    checker: Checker | None = None
    location: dict[str, Any] = {}
    try:
        fixtures = load_fixtures(fixtures_path)
        targets = load_targets(targets_path, fixtures)
        settings = load_settings(settings_path, fixtures, targets)
        checker = Checker(fixtures, targets, expected_arms, settings)
        for path in raw_paths:
            with path.open() as stream:
                for line_number, line in enumerate(stream, 1):
                    location = {"raw_path": str(path), "line": line_number}
                    need(line.strip() != "", "empty raw JSONL line")
                    checker.ingest(json.loads(line))
        summary = checker.finish()
        code = 0
    except (Invalid, ValueError, KeyError, TypeError, OSError) as error:
        summary = {"schema": "classical.ecdlp.endpoint-reuse.public-verification.v1", "status": "invalid_public_record", "error": str(error), "location": location, "hidden_scalar_labels_read": False, "scientific_review_or_performance_qualification": False}
        code = 1
    summary["input_sha256"] = {str(p): digest(p) for p in [fixtures_path, targets_path, settings_path, *raw_paths] if p.is_file()}
    summary["verifier_sha256"] = digest(Path(__file__))
    (output / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    with (output / "cases.jsonl").open("w") as stream:
        for result in checker.results if checker else []:
            stream.write(json.dumps(result, separators=(",", ":"), sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--records", type=Path, action="append", required=True)
    parser.add_argument("--expect-arm", action="append", choices=sorted(ARMS), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        return verify(args.fixtures, args.targets, args.settings, args.records, set(args.expect_arm), args.out)
    except (Invalid, OSError) as error:
        print(json.dumps({"status": "verification_not_started", "error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
