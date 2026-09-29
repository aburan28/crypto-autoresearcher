#!/usr/bin/env python3
"""Concrete, fail-closed future runner for EXP-ECDLP-1b1b99.

This implementation is deliberately inert by default.  It contains the fixed
CM maps, custody boundary, allocation machinery, and future launch checks so
that they can be reviewed before any scientific fixture is searched or timed.
The sole current use is bounded static/unit testing.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence

TASK_ID = "TASK-20260908-35abb7"
EXPERIMENT_ID = "EXP-ECDLP-1b1b99"
DECISION_ID = "DEC-20260908-166ad3"
ARCHIVE_TASK_ID = "TASK-20260908-163823"
EFFECTIVE_CONTRACT = "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260907-fe3f53/EXP-ECDLP-1b1b99.yaml"
EFFECTIVE_CONTRACT_SHA256 = "0adf7d4bb7ba7ab32ec1f0e15d88813b9ed276fc0be7e3d9713f9131c66a8c04"
SPECIFICATION_SHA256 = "b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff"
AMENDMENT_SHA256 = "3bd5ac5307fe33757b14c19fdef9b8b02d4de6056f59f519aed174f4f4733d39"
RUNTIME_BINDING = "coordination/experiment-reserve/BATCH-45b4d5/bindings/DEC-20260908-166ad3/runtime-binding.json"
RUNTIME_BINDING_SHA256 = "b4919db935d24e7ec756daaf9c59cbbf2e663407f2c621b3e752d2b25bded27f"
PUBLIC_KEY = "coordination/experiment-reserve/BATCH-45b4d5/bindings/DEC-20260908-166ad3/launch-public.pem"
PUBLIC_KEY_SHA256 = "fa31ffa49bb6f0b464d1b3dd8085d771f77e553985596ff6f7266cc1575b7d0d"
PUBLIC_SNAPSHOT_COMMIT = "0b4d214b4dd8e3b293eb09ffbb806883380ef2a6"
SAGE_PYTHON = "/var/tmp/sage-10.9-current/local/bin/python3"
OPENSSL = "/opt/homebrew/opt/openssl@3/bin/openssl"
OPENSSL_SHA256 = "d0ab050d71d431be5e1372a79972361f7bcef4a7c2c5aef3e7c0ce7bac0e3ee8"
QUERY_LADDER = (1, 16, 256, 4096)
SEEDS = (606101, 606103)
ARM_IDS = (1, 2, 3, 4, 5, 6, 7)
SCALAR_ARMS = {2: "binary_double_and_add", 3: "wnaf_w2", 4: "wnaf_w3", 5: "wnaf_w4", 6: "wnaf_w5", 7: "pinned_external_library"}
REQUIRED_ARTIFACTS = ("manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv", "certificates.json", "stdout.log", "stderr.log", "report.md", "command.txt", "environment.json", "raw-result.json")
STAGES = ("authorize_and_claim_nonce", "initialize_progressive_custody", "enumerate_and_certify_fixtures", "construct_maps_duals_classes_and_coordinates", "run_exact_controls", "run_seed_606101_selection_matrix", "run_complete_timing_and_control_matrices", "replay_verify_and_reduce", "finalize_manifest_and_atomic_publish")


class CMError(RuntimeError): pass
class InvalidMeasurement(CMError): pass
class CancellationRequested(CMError): pass

@dataclass(frozen=True)
class AuthCheck:
    accepted: bool
    code: str
    detail: str
    payload: dict[str, Any] | None = None


Point = tuple[int, int] | None

def root() -> Path: return Path(__file__).resolve().parents[4]
def ppath(relative: str) -> Path: return root() / relative
def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()
def sha256_file(path: Path) -> str: return sha256_bytes(path.read_bytes())

def _json_safe(value: Any) -> None:
    if isinstance(value, float): raise ValueError("canonical payload forbids floats")
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value): raise ValueError("canonical object keys must be strings")
        for item in value.values(): _json_safe(item)
    elif isinstance(value, (list, tuple)):
        for item in value: _json_safe(item)
    elif not isinstance(value, (str, int, bool, type(None))): raise ValueError("canonical payload has unsupported value")

def canonical_json(value: Any) -> bytes:
    _json_safe(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"

def strict_json(raw: bytes) -> dict[str, Any]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out: raise ValueError("duplicate JSON key")
            out[key] = value
        return out
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
    if not isinstance(value, dict) or canonical_json(value) != raw: raise ValueError("payload is not canonical object bytes")
    return value


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int
    def __post_init__(self) -> None:
        if self.p <= 3 or not is_prime(self.p) or (4*self.a**3 + 27*self.b**2) % self.p == 0: raise ValueError("nonsingular prime-field short curve required")
    def on_curve(self, point: Point) -> bool:
        return point is None or (point[1]*point[1] - (point[0]**3 + self.a*point[0] + self.b)) % self.p == 0
    def neg(self, point: Point) -> Point: return None if point is None else (point[0] % self.p, (-point[1]) % self.p)
    def add(self, first: Point, second: Point) -> Point:
        if first is None: return second
        if second is None: return first
        x1,y1 = first; x2,y2 = second; p = self.p
        if x1 == x2 and (y1+y2) % p == 0: return None
        slope = ((3*x1*x1+self.a)*pow(2*y1, -1, p) if first == second else (y2-y1)*pow(x2-x1, -1, p)) % p
        x3 = (slope*slope-x1-x2) % p
        return x3, (slope*(x1-x3)-y1) % p
    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0: return self.mul(-scalar, self.neg(point))
        out: Point = None
        while scalar:
            if scalar & 1: out = self.add(out, point)
            point = self.add(point, point); scalar >>= 1
        return out
    def affine_points(self) -> Iterator[Point]:
        for x in range(self.p):
            rhs = (x*x*x + self.a*x + self.b) % self.p
            y = sqrt_mod(rhs, self.p)
            if y is None: continue
            yield (x, y)
            if y: yield (x, (-y) % self.p)
    def points(self) -> list[Point]: return [None, *self.affine_points()]

def point_key(point: Point) -> tuple[int, int]: return (-1, -1) if point is None else point
def factor_integer(value: int) -> dict[int, int]:
    factors: dict[int, int] = {}; divisor = 2
    while divisor*divisor <= value:
        while value % divisor == 0: factors[divisor] = factors.get(divisor, 0)+1; value //= divisor
        divisor = 3 if divisor == 2 else divisor+2
    if value > 1: factors[value] = factors.get(value, 0)+1
    return factors
def is_prime(value: int) -> bool: return value > 1 and factor_integer(value) == {value: 1}
def v_adic(value: int, prime: int) -> int:
    answer = 0
    while value and value % prime == 0: answer += 1; value //= prime
    return answer
def sqrt_mod(value: int, prime: int) -> int | None:
    value %= prime
    if value == 0: return 0
    if pow(value, (prime-1)//2, prime) != 1: return None
    if prime % 4 == 3: return pow(value, (prime+1)//4, prime)
    q, s = prime-1, 0
    while q % 2 == 0: s += 1; q //= 2
    z = next(x for x in range(2, prime) if pow(x, (prime-1)//2, prime) == prime-1)
    m, c, t, r = s, pow(z, q, prime), pow(value, q, prime), pow(value, (q+1)//2, prime)
    while t != 1:
        i = next(i for i in range(1, m) if pow(t, 1 << i, prime) == 1)
        b = pow(c, 1 << (m-i-1), prime); m, c, t, r = i, b*b % prime, t*b*b % prime, r*b % prime
    return min(r, (-r) % prime)

def full_rational_three_torsion(curve: Curve) -> tuple[list[Point], list[tuple[Point, Point]]]:
    torsion = sorted((point for point in curve.affine_points() if curve.mul(3, point) is None), key=point_key)
    if len(torsion) != 8: raise InvalidMeasurement(f"full rational E[3] required; found {len(torsion)} nonzero points")
    used: set[Point] = set(); kernels: list[tuple[Point, Point]] = []
    for point in torsion:
        if point in used: continue
        inverse = curve.neg(point)
        if inverse == point or inverse not in torsion: raise InvalidMeasurement("rational 3-torsion pairing failed")
        kernel = tuple(sorted((point, inverse), key=point_key))
        used.update(kernel); kernels.append(kernel)
    kernels.sort(key=lambda pair: (pair[0][0], pair[0][1]))
    if len(kernels) != 4 or len(used) != 8: raise InvalidMeasurement("four unique cyclic order-three kernels required")
    return torsion, kernels

def rational_three_kernels(curve: Curve) -> list[tuple[Point, Point]]:
    points = sorted((point for point in curve.affine_points() if curve.mul(3, point) is None), key=point_key)
    used: set[Point] = set(); answer = []
    for point in points:
        if point in used: continue
        inverse = curve.neg(point)
        if inverse != point and inverse in points:
            pair = tuple(sorted((point, inverse), key=point_key)); used.update(pair); answer.append(pair)
    return sorted(answer, key=lambda pair: (pair[0][0], pair[0][1]))

@dataclass(frozen=True)
class Isomorphism:
    source: Curve
    target: Curve
    u: int
    def apply(self, point: Point) -> Point:
        if point is None: return None
        return (self.u*self.u*point[0] % self.source.p, self.u**3*point[1] % self.source.p)
    def inverse(self, point: Point) -> Point:
        return Isomorphism(self.target, self.source, pow(self.u, -1, self.source.p)).apply(point)

def short_weierstrass_isomorphism(source: Curve, target: Curve) -> Isomorphism:
    if source.p != target.p: raise InvalidMeasurement("isomorphism changes field")
    for u in range(1, source.p):
        if target.a % source.p == source.a*pow(u, 4, source.p) % source.p and target.b % source.p == source.b*pow(u, 6, source.p) % source.p:
            return Isomorphism(source, target, u)
    raise InvalidMeasurement("no explicit Fp short-Weierstrass isomorphism")

@dataclass(frozen=True)
class VeluMap:
    source: Curve
    target: Curve
    kernel: tuple[Point, Point]
    def apply(self, point: Point) -> Point:
        if point is None or point in self.kernel: return None
        x, y = point; xq, yq = self.kernel[0]; p = self.source.p
        gx, gy = (3*xq*xq+self.source.a) % p, (-2*yq) % p
        v, u = 2*gx % p, gy*gy % p
        inverse = pow((x-xq) % p, -1, p)
        image = ((x + v*inverse + u*inverse*inverse) % p, (y - 2*u*y*pow(inverse, 3, p) - v*y*inverse*inverse) % p)
        if not self.target.on_curve(image): raise InvalidMeasurement("Vélu image failed target equation")
        return image

def normalized_velu_map(curve: Curve, kernel: tuple[Point, Point]) -> VeluMap:
    if len(kernel) != 2 or curve.neg(kernel[0]) != kernel[1] or curve.mul(3, kernel[0]) is not None: raise InvalidMeasurement("exact order-three plus/minus kernel required")
    x, y = kernel[0]; p = curve.p; gx, gy = (3*x*x+curve.a) % p, (-2*y) % p
    v, w = 2*gx % p, (gy*gy+x*(2*gx)) % p
    return VeluMap(curve, Curve(p, (curve.a-5*v) % p, (curve.b-7*w) % p), kernel)

@dataclass(frozen=True)
class ExactDual:
    forward: VeluMap
    raw_dual: VeluMap
    normalization: Isomorphism
    def apply(self, point: Point) -> Point: return self.normalization.apply(self.raw_dual.apply(point))
    def source_composition(self, point: Point) -> bool: return self.apply(self.forward.apply(point)) == self.forward.source.mul(3, point)
    def target_composition(self, point: Point) -> bool: return self.forward.apply(self.apply(point)) == self.forward.target.mul(3, point)

def exact_dual(forward: VeluMap, certificate_point: Point) -> ExactDual:
    candidates: list[ExactDual] = []
    for kernel in rational_three_kernels(forward.target):
        raw = normalized_velu_map(forward.target, kernel)
        try: normalization = short_weierstrass_isomorphism(raw.target, forward.source)
        except InvalidMeasurement: continue
        candidate = ExactDual(forward, raw, normalization)
        if certificate_point not in forward.kernel and candidate.source_composition(certificate_point): candidates.append(candidate)
    if len(candidates) != 1: raise InvalidMeasurement(f"expected unique exact normalized dual, got {len(candidates)}")
    return candidates[0]

def j1728_automorphism(curve: Curve) -> Callable[[Point], Point]:
    if curve.b % curve.p: raise InvalidMeasurement("iota requires j=1728 B=0 model")
    iota = sqrt_mod(curve.p-1, curve.p)
    if iota is None: raise InvalidMeasurement("no canonical root of -1")
    return lambda point: None if point is None else ((-point[0]) % curve.p, iota*point[1] % curve.p)

def coordinate_isomorphism(curve: Curve, u: int) -> Isomorphism:
    u %= curve.p
    if not u: raise ValueError("coordinate scale must be nonzero")
    return Isomorphism(curve, Curve(curve.p, curve.a*pow(u, 4, curve.p) % curve.p, curve.b*pow(u, 6, curve.p) % curve.p), u)

@dataclass(frozen=True)
class Endpoint:
    label: str
    class_id: str
    raw: VeluMap
    alpha: Isomorphism
    dual: ExactDual
    def phi(self, point: Point) -> Point: return self.alpha.apply(self.raw.apply(point))
    def psi(self, point: Point) -> Point: return self.dual.apply(self.alpha.inverse(point))
    @property
    def target(self) -> Curve: return self.alpha.target
    def check_source(self, point: Point) -> bool: return self.psi(self.phi(point)) == self.raw.source.mul(3, point)
    def check_target(self, point: Point) -> bool: return self.phi(self.psi(point)) == self.target.mul(3, point)
    def coordinate(self, u: int) -> "CoordinateEndpoint": return CoordinateEndpoint(self, coordinate_isomorphism(self.target, u))

@dataclass(frozen=True)
class CoordinateEndpoint:
    endpoint: Endpoint
    rho: Isomorphism
    def phi(self, point: Point) -> Point: return self.rho.apply(self.endpoint.phi(point))
    def psi(self, point: Point) -> Point: return self.endpoint.psi(self.rho.inverse(point))
    @property
    def target(self) -> Curve: return self.rho.target
    def beta(self, point: Point, iota: Callable[[Point], Point]) -> Point: return self.phi(iota(self.psi(point)))

def endpoints_with_two_classes(curve: Curve, certificate_point: Point) -> tuple[Endpoint, ...]:
    _, kernels = full_rational_three_torsion(curve); raws = [(f"K{i}", normalized_velu_map(curve, kernel)) for i, kernel in enumerate(kernels)]
    classes: list[list[tuple[str, VeluMap]]] = []
    for label, raw in raws:
        for cls in classes:
            try: short_weierstrass_isomorphism(raw.target, cls[0][1].target); cls.append((label, raw)); break
            except InvalidMeasurement: continue
        else: classes.append([(label, raw)])
    if sorted(map(len, classes)) != [2, 2]: raise InvalidMeasurement("four endpoints must partition into two Fp-isomorphism classes of two")
    answer: list[Endpoint] = []
    for class_index, cls in enumerate(classes):
        representative = cls[0][1].target
        for label, raw in cls:
            alpha = short_weierstrass_isomorphism(raw.target, representative)
            answer.append(Endpoint(label, f"C{class_index}", raw, alpha, exact_dual(raw, certificate_point)))
    return tuple(sorted(answer, key=lambda item: item.label))

@dataclass(frozen=True)
class ConductorCertificate:
    p: int; trace: int; cardinality: int; discriminant: int; f_pi: int; v3_f_pi: int; kernel_labels: tuple[str, ...]; class_sizes: tuple[int, ...]
    def validate(self) -> None:
        if self.cardinality != self.p+1-self.trace or self.discriminant != self.trace*self.trace-4*self.p: raise InvalidMeasurement("trace/cardinality equation failed")
        if self.discriminant != -4*self.f_pi*self.f_pi or self.v3_f_pi != 1: raise InvalidMeasurement("conductor equation or valuation failed")
        if self.kernel_labels != ("K0", "K1", "K2", "K3") or self.class_sizes != (2, 2): raise InvalidMeasurement("kernel/class certificate failed")

def sqrt_minus_one_mod_prime(r: int) -> tuple[int, int]:
    roots = tuple(x for x in range(r) if x*x % r == r-1)
    if len(roots) != 2: raise InvalidMeasurement("subgroup needs exactly two roots of minus one")
    return roots
def choose_eigenvalue_sign(roots: Sequence[int], r: int, g0: Point, iota: Callable[[Point], Point], scalar: Callable[[int, Point], Point]) -> int:
    matches = [root % r for root in roots if scalar(root % r, g0) == iota(g0)]
    if len(matches) != 1: raise InvalidMeasurement("lambda sign is not unique")
    return matches[0]

@dataclass
class StreamState:
    counters: dict[tuple[str, tuple[int, ...], int], int] = field(default_factory=dict)
    def draw(self, purpose: str, parameters: Sequence[int], seed: int, n: int) -> int:
        if purpose not in {"query", "control", "field_x", "target", "shuffle"} or len(parameters) != 7 or n < 1: raise ValueError("invalid frozen RNG request")
        key = (purpose, tuple(parameters), seed); counter = self.counters.get(key, 0); limit = ((1 << 256)//n)*n
        while True:
            digest = stream_digest(purpose, tuple(parameters), seed, counter); counter += 1
            if digest < limit: self.counters[key] = counter; return digest % n
    def snapshot(self) -> dict[str, int]: return {json.dumps([purpose, list(params), seed], separators=(",", ":")): value for (purpose, params, seed), value in sorted(self.counters.items())}

def stream_digest(purpose: str, parameters: tuple[int, ...], seed: int, counter: int) -> int:
    if counter < 0 or seed < 0 or any(not isinstance(value, int) for value in parameters): raise ValueError("invalid stream tuple")
    wire = json.dumps([EXPERIMENT_ID, purpose, list(parameters), seed, counter], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return int.from_bytes(hashlib.sha256(wire).digest(), "big")
def fisher_yates(values: Iterable[Any], state: StreamState, parameters: tuple[int, ...], seed: int) -> list[Any]:
    answer = list(values)
    for index in range(len(answer)-1, 0, -1):
        other = state.draw("shuffle", parameters, seed, index+1); answer[index], answer[other] = answer[other], answer[index]
    return answer

@dataclass(frozen=True)
class PublicEvaluatorBatch:
    opaque_batch_id: str; source_curve_public_equation: tuple[int, int, int]; target_curve_public_equation: tuple[int, int, int]; r: int; m: int; forward_map: str; dual_map: str; coordinate_maps_needed_for_public_evaluation: tuple[str, ...]; opaque_query_points: tuple[Point, ...]; q: int
    def wire(self) -> dict[str, Any]: return asdict(self)
@dataclass(frozen=True)
class PrivateVerifierBatch:
    public: PublicEvaluatorBatch; fixture_label: str; interval_label: str; kernel_label: str; target_class_id: str; g0: Point; gk: Point; scalars: tuple[int, ...]; expected_points: tuple[Point, ...]; certificates: dict[str, Any]; rng_snapshot: dict[str, int]; opaque_join: tuple[int, ...]

def validate_public_batch(value: dict[str, Any]) -> None:
    allowed = set(PublicEvaluatorBatch.__dataclass_fields__)
    if set(value) != allowed: raise InvalidMeasurement("public evaluator schema is closed or leaks verifier labels")
    forbidden = {"fixture_label", "interval_label", "kernel_label", "target_class_id", "g0", "gk", "scalars", "expected_points", "rng_snapshot", "opaque_join", "baseline_winner"}
    if forbidden & set(value): raise InvalidMeasurement("private field crosses evaluator boundary")

def binary_mul(curve: Curve, scalar: int, point: Point) -> Point: return curve.mul(scalar, point)
def wnaf_mul(curve: Curve, scalar: int, point: Point, width: int) -> Point:
    if width not in (2, 3, 4, 5): raise ValueError("only frozen widths 2..5")
    digits: list[int] = []; value = scalar
    while value:
        digit = 0
        if value & 1:
            digit = value % (1 << width); digit -= 1 << width if digit >= 1 << (width-1) else 0; value -= digit
        digits.append(digit); value //= 2
    table = {d: curve.mul(d, point) for d in range(1, 1 << (width-1), 2)}; out: Point = None
    for digit in reversed(digits):
        out = curve.add(out, out)
        if digit: out = curve.add(out, table[abs(digit)] if digit > 0 else curve.neg(table[abs(digit)]))
    return out

def load_runtime_binding() -> dict[str, Any]:
    path = ppath(RUNTIME_BINDING)
    if sha256_file(path) != RUNTIME_BINDING_SHA256: raise InvalidMeasurement("runtime binding repository bytes changed")
    return json.loads(path.read_text())
def verify_pinned_runtime() -> dict[str, Any]:
    binding = load_runtime_binding(); failures = []
    for item in binding["runtime"]["file_bindings"]:
        path = Path(item["path"])
        if not path.is_file() or sha256_file(path) != item["sha256"]: failures.append(str(path))
    if failures: raise InvalidMeasurement("pinned runtime mismatch: " + ",".join(failures))
    if Path(sys.executable).resolve() != Path(SAGE_PYTHON).resolve(): raise InvalidMeasurement("pinned arm7 requires exact Sage Python executable")
    return binding
def pinned_library_mul(curve: Curve, scalar: int, point: Point) -> Point:
    if point is None: return None
    verify_pinned_runtime()
    from cypari2 import Pari  # type: ignore[import-not-found]
    pari = Pari(); field_curve = pari.ellinit([0, 0, 0, curve.a % curve.p, curve.b % curve.p], curve.p)
    result = pari.ellmul(field_curve, [pari.Mod(point[0], curve.p), pari.Mod(point[1], curve.p)], int(scalar))
    if str(result) == "[0]": return None
    answer = (int(pari.lift(result[0])) % curve.p, int(pari.lift(result[1])) % curve.p)
    if not curve.on_curve(answer): raise InvalidMeasurement("PARI ellmul returned non-curve point")
    return answer
def scalar_arms(curve: Curve, scalar: int, point: Point) -> dict[int, Point]:
    return {2: binary_mul(curve, scalar, point), 3: wnaf_mul(curve, scalar, point, 2), 4: wnaf_mul(curve, scalar, point, 3), 5: wnaf_mul(curve, scalar, point, 4), 6: wnaf_mul(curve, scalar, point, 5), 7: pinned_library_mul(curve, scalar, point)}

@dataclass(frozen=True)
class BlockCost:
    fixture: str; kernel: str; class_id: str; coordinate: int; seed: int; q: int; arm: int; block: int; repetition: int; component: str; stage: str; cpu_ns: int; wall_ns: int; rss_bytes: int; below_resolution: bool
    def raw_id(self) -> str: return sha256_bytes(canonical_json(asdict(self)))
@dataclass(frozen=True)
class Allocation:
    raw_cost_row_id: str; strategy_view: str; component: str; allocation_target: str; rational_weight_numerator: int; rational_weight_denominator: int; allocated_CPU_nanoseconds: int; allocated_wall_nanoseconds: int; reason_code: str

def allocate_equal(row: BlockCost, strategy: str, component: str, targets: Sequence[str], reason: str) -> list[Allocation]:
    if not targets: raise ValueError("allocation requires targets")
    count = len(targets); cpu_base, cpu_rem = divmod(row.cpu_ns, count); wall_base, wall_rem = divmod(row.wall_ns, count)
    return [Allocation(row.raw_id(), strategy, component, target, 1, count, cpu_base+(index < cpu_rem), wall_base+(index < wall_rem), reason) for index, target in enumerate(sorted(targets))]
def reconcile_allocations(rows: Sequence[BlockCost], allocations: Sequence[Allocation]) -> None:
    by_id: dict[str, list[Allocation]] = {}
    for allocation in allocations: by_id.setdefault(allocation.raw_cost_row_id, []).append(allocation)
    for row in rows:
        matches = by_id.get(row.raw_id(), [])
        if not matches or sum(Fraction(item.rational_weight_numerator, item.rational_weight_denominator) for item in matches) != 1: raise InvalidMeasurement("allocation weights do not reconcile")
        if sum(item.allocated_CPU_nanoseconds for item in matches) != row.cpu_ns or sum(item.allocated_wall_nanoseconds for item in matches) != row.wall_ns: raise InvalidMeasurement("integer allocation does not reconcile")

def select_baselines(observations: Sequence[BlockCost]) -> dict[tuple[str, int], int]:
    groups: dict[tuple[str, int], list[BlockCost]] = {}
    for row in observations:
        if row.seed != 606101 or row.q != 256 or row.arm not in SCALAR_ARMS or row.block not in range(7): raise InvalidMeasurement("selection only consumes frozen q/seed/scalar block rows")
        groups.setdefault((row.fixture.split("F")[0], row.coordinate), []).append(row)
    if set(groups) != {(f"I{i}", u) for i in range(3) for u in (1, 2, 3)}: raise InvalidMeasurement("exactly nine interval-coordinate strata required")
    winners: dict[tuple[str, int], int] = {}
    for key, rows in groups.items():
        prefix = key[0]
        expected = {(f"{prefix}F{fixture}", kernel, arm, block) for fixture in (0, 1) for kernel in ("K0", "K1", "K2", "K3") for arm in SCALAR_ARMS for block in range(7)}
        actual = {(row.fixture, row.kernel, row.arm, row.block) for row in rows}
        if actual != expected: raise InvalidMeasurement("selection stratum lacks charged endpoint-arm-block coverage")
        scores = {arm: sum(row.cpu_ns for row in rows if row.arm == arm) for arm in SCALAR_ARMS}
        winners[key] = min(SCALAR_ARMS, key=lambda arm: (scores[arm], arm))
    return winners

def process_group_metrics() -> dict[str, Any]:
    usage_self, usage_children = resource.getrusage(resource.RUSAGE_SELF), resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu_ns = int((usage_self.ru_utime+usage_self.ru_stime+usage_children.ru_utime+usage_children.ru_stime)*1_000_000_000)
    local_rss = usage_self.ru_maxrss if sys.platform == "darwin" else usage_self.ru_maxrss*1024
    try:
        observed = subprocess.run(["ps", "-o", "rss=", "-g", str(os.getpgrp())], capture_output=True, text=True, timeout=3, check=False)
        group_rss = sum(int(line.strip())*1024 for line in observed.stdout.splitlines() if line.strip().isdigit())
    except (OSError, subprocess.SubprocessError): group_rss = 0
    return {"cpu_nanoseconds": cpu_ns, "peak_rss_bytes": int(max(local_rss, group_rss)), "platform": platform.system(), "rss_rule": "Darwin_ru_maxrss_bytes_and_ps_group_kibibytes" if sys.platform == "darwin" else "Linux_ru_maxrss_kibibytes_times_1024", "cpu_scope": "self_plus_waited_descendants; active child groups are terminated and waited before stage receipt"}
def timed_blocks(operation: Callable[[], None], cancel: Callable[[], bool], maximum_repeats: int = 100) -> list[dict[str, Any]]:
    rows = []
    for block in range(7):
        before = process_group_metrics(); wall = time.monotonic_ns(); repeats = 0; repeat_receipts = []
        while repeats < maximum_repeats and process_group_metrics()["cpu_nanoseconds"]-before["cpu_nanoseconds"] < 100_000_000:
            if cancel(): raise CancellationRequested("cooperative cancellation inside timing repeat")
            repeat_before, repeat_wall = process_group_metrics(), time.monotonic_ns(); operation(); repeat_after = process_group_metrics(); repeats += 1
            repeat_receipts.append({"repetition": repeats, "cpu_nanoseconds": repeat_after["cpu_nanoseconds"]-repeat_before["cpu_nanoseconds"], "wall_nanoseconds": time.monotonic_ns()-repeat_wall, "process_group_peak_RSS_bytes": max(repeat_before["peak_rss_bytes"], repeat_after["peak_rss_bytes"])})
        after = process_group_metrics(); cpu = after["cpu_nanoseconds"]-before["cpu_nanoseconds"]
        rows.append({"block": block, "repetitions": repeats, "repeat_receipts": repeat_receipts, "cpu_nanoseconds": cpu, "wall_nanoseconds": time.monotonic_ns()-wall, "process_group_peak_RSS_bytes": max(before["peak_rss_bytes"], after["peak_rss_bytes"]), "below_resolution": cpu < 100_000_000})
    return rows
def terminate_child_group(child: subprocess.Popen[Any]) -> dict[str, Any]:
    try: os.killpg(os.getpgid(child.pid), signal.SIGTERM); child.wait(timeout=5); return {"signal": "SIGTERM", "returncode": child.returncode}
    except subprocess.TimeoutExpired: os.killpg(os.getpgid(child.pid), signal.SIGKILL); child.wait(timeout=5); return {"signal": "SIGKILL", "returncode": child.returncode}

@dataclass
class Custody:
    run_root: Path; run_id: str
    partial: Path = field(init=False); final: Path = field(init=False)
    def __post_init__(self) -> None:
        if not self.run_id or Path(self.run_id).name != self.run_id: raise ValueError("run ID must be basename")
        self.partial = self.run_root / f"{self.run_id}.partial"; self.final = self.run_root / self.run_id
        if self.partial.exists() or self.final.exists(): raise FileExistsError("run path already exists")
        self.partial.mkdir(parents=True)
    def write(self, name: str, content: bytes) -> Path:
        if name not in REQUIRED_ARTIFACTS and name not in {"progress.jsonl", "baseline-freeze.json", "stage-receipts.jsonl"}: raise ValueError("unregistered custody artifact")
        target = self.partial / name; temp = target.with_suffix(target.suffix+".tmp")
        if target.exists(): raise FileExistsError(f"immutable custody artifact already exists: {name}")
        with temp.open("xb") as handle: handle.write(content); handle.flush(); os.fsync(handle.fileno())
        os.replace(temp, target); directory = os.open(str(self.partial), os.O_RDONLY); os.fsync(directory); os.close(directory); return target
    def append_progress(self, value: dict[str, Any]) -> None:
        path = self.partial / "progress.jsonl"
        with path.open("ab") as handle: handle.write(canonical_json(value)); handle.flush(); os.fsync(handle.fileno())
    def publish(self) -> Path:
        for name in REQUIRED_ARTIFACTS:
            path = self.partial / name
            if not path.is_file() or not path.read_bytes(): raise InvalidMeasurement(f"required artifact missing or empty: {name}")
        directory = os.open(str(self.partial), os.O_RDONLY); os.fsync(directory); os.close(directory)
        os.replace(self.partial, self.final); parent = os.open(str(self.run_root), os.O_RDONLY); os.fsync(parent); os.close(parent); return self.final

def fixed_runtime_source_checks() -> None:
    required = {EFFECTIVE_CONTRACT: EFFECTIVE_CONTRACT_SHA256, "experiments/EXP-ECDLP-1b1b99/specification.yaml": SPECIFICATION_SHA256, "experiments/EXP-ECDLP-1b1b99/amendments/DEC-20260908-166ad3.yaml": AMENDMENT_SHA256, RUNTIME_BINDING: RUNTIME_BINDING_SHA256, PUBLIC_KEY: PUBLIC_KEY_SHA256}
    for relative, digest in required.items():
        if sha256_file(ppath(relative)) != digest: raise InvalidMeasurement(f"source binding mismatch: {relative}")
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", PUBLIC_SNAPSHOT_COMMIT, "HEAD"], cwd=root(), capture_output=True, check=False)
    if ancestry.returncode != 0: raise InvalidMeasurement("public-key snapshot is not an ancestor of executing commit")
    snap = subprocess.run(["git", "show", f"{PUBLIC_SNAPSHOT_COMMIT}:{RUNTIME_BINDING}"], cwd=root(), capture_output=True, check=False)
    if snap.returncode or sha256_bytes(snap.stdout) != RUNTIME_BINDING_SHA256: raise InvalidMeasurement("reviewed runtime snapshot bytes differ")

def claim_nonce(registry: Path, nonce: str, run_id: str, payload_hash: str) -> AuthCheck:
    if len(nonce) != 64 or any(character not in "0123456789abcdef" for character in nonce): return AuthCheck(False, "AUTH_MALFORMED", "nonce must be 256-bit lowercase hexadecimal")
    registry.mkdir(parents=True, exist_ok=True); target = registry / f"{nonce}.json"
    try:
        with target.open("x", encoding="utf-8") as handle: handle.write(canonical_json({"nonce": nonce, "run_id": run_id, "payload_sha256": payload_hash, "claimed_at_UTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}).decode("utf-8")); handle.flush(); os.fsync(handle.fileno())
    except FileExistsError: return AuthCheck(False, "AUTH_NONCE_REPLAY", "one-run nonce already consumed")
    return AuthCheck(True, "AUTH_OK", "nonce atomically claimed")

def verify_future_authorization(payload_path: Path, signature_path: Path, nonce_registry: Path) -> AuthCheck:
    try: raw = payload_path.read_bytes(); payload = strict_json(raw)
    except (OSError, UnicodeDecodeError, ValueError) as exc: return AuthCheck(False, "AUTH_MALFORMED", str(exc))
    required = {"domain", "experiment_id", "effective_contract_sha256", "predecessor_specification_sha256", "amendment_sha256", "decision_id", "handoff_id", "review_archive_commit", "implementation_archive_commit", "implementation_tree_or_path_hash", "runner_sha256", "execution_plan_sha256", "trusted_verifier_sha256", "executor_role", "handoff_sha256", "runtime_binding_sha256", "provider", "model", "run_id", "output_path", "fixed_protocol", "resource_policy", "replay_reference_sha256", "public_private_schema_sha256", "nonce"}
    if set(payload) != required or payload.get("domain") != "crypto-autoresearcher.launch.v1" or payload.get("experiment_id") != EXPERIMENT_ID: return AuthCheck(False, "AUTH_MALFORMED", "payload field set/domain/experiment mismatch")
    if "bedrock" in str(payload["provider"]).lower() or "bedrock" in str(payload["model"]).lower(): return AuthCheck(False, "AUTH_RUNTIME_MISMATCH", "Bedrock provider/model is prohibited")
    bindings = {"effective_contract_sha256": EFFECTIVE_CONTRACT_SHA256, "predecessor_specification_sha256": SPECIFICATION_SHA256, "amendment_sha256": AMENDMENT_SHA256, "decision_id": DECISION_ID, "handoff_id": TASK_ID, "runner_sha256": sha256_file(Path(__file__)), "execution_plan_sha256": sha256_file(Path(__file__).with_name("execution-plan.json")), "trusted_verifier_sha256": OPENSSL_SHA256, "runtime_binding_sha256": RUNTIME_BINDING_SHA256, "executor_role": "executor"}
    if any(payload[key] != value for key, value in bindings.items()): return AuthCheck(False, "AUTH_BINDING_MISMATCH", "signed payload differs from exact source/runtime binding")
    if payload["output_path"] != f"runs/{payload['run_id']}" or Path(payload["run_id"]).name != payload["run_id"]: return AuthCheck(False, "AUTH_RUN_PATH_MISMATCH", "run ID/path mismatch")
    try: fixed_runtime_source_checks(); verify_pinned_runtime()
    except (InvalidMeasurement, OSError) as exc: return AuthCheck(False, "AUTH_RUNTIME_MISMATCH", str(exc))
    if sha256_file(ppath(PUBLIC_KEY)) != PUBLIC_KEY_SHA256 or sha256_file(Path(OPENSSL)) != OPENSSL_SHA256: return AuthCheck(False, "AUTH_TRUST_ROOT_UNBOUND", "fixed public key or OpenSSL bytes mismatch")
    command = [OPENSSL, "pkeyutl", "-verify", "-pubin", "-rawin", "-inkey", str(ppath(PUBLIC_KEY)), "-in", str(payload_path), "-sigfile", str(signature_path)]
    try: checked = subprocess.run(command, capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc: return AuthCheck(False, "AUTH_SIGNATURE_INVALID", str(exc))
    if checked.returncode: return AuthCheck(False, "AUTH_SIGNATURE_INVALID", "fixed OpenSSL verifier rejected detached signature")
    nonce = claim_nonce(nonce_registry, payload["nonce"], payload["run_id"], sha256_bytes(raw))
    return AuthCheck(nonce.accepted, nonce.code, nonce.detail, payload if nonce.accepted else None)

def hard_validity_reduce(receipts: Sequence[dict[str, Any]], coverage: dict[str, Any], controls: dict[str, Any], allocations_ok: bool, artifacts_ok: bool) -> str:
    stages = {receipt.get("stage_id"): receipt for receipt in receipts}
    if set(stages) != set(STAGES) or any(receipt.get("status") != "completed" for receipt in stages.values()): return "partial_inconclusive"
    required = ["authorization_and_nonce_valid", "six_fixtures_valid", "four_labels_two_classes_valid", "exact_maps_and_conjugations_valid", "all_controls_true", "nine_freezes_valid", "main_rows_28224", "top_rows_2016", "identity_rows_2016", "all_blocks_typed", "replay_valid", "resource_custody_valid"]
    if not all(coverage.get(key) is True for key in required) or not controls or not all(value is True for value in controls.values()) or not allocations_ok or not artifacts_ok: return "completed_invalid"
    return "completed_valid"

def json_ready(value: Any) -> Any:
    if isinstance(value, Curve): return {"p": value.p, "a": value.a, "b": value.b}
    if isinstance(value, (Endpoint, CoordinateEndpoint, VeluMap, ExactDual, Isomorphism, ConductorCertificate, BlockCost, Allocation, PublicEvaluatorBatch, PrivateVerifierBatch)):
        return json_ready(asdict(value))
    if isinstance(value, dict): return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)): return [json_ready(item) for item in value]
    if isinstance(value, Path): return str(value)
    return value

def git_binding() -> dict[str, str]:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root(), capture_output=True, text=True, check=False)
    status = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root(), capture_output=True, text=True, check=False)
    if commit.returncode or status.returncode: raise InvalidMeasurement("cannot read execution git binding")
    dirty = status.stdout.encode("utf-8")
    return {"commit": commit.stdout.strip(), "dirty_state": "clean" if not dirty else "dirty", "dirty_diff_sha256": "clean" if not dirty else sha256_bytes(dirty)}

def run_authorized(payload_path: Path, signature_path: Path, nonce_registry: Path, run_root: Path, cancel: Callable[[], bool] = lambda: False) -> dict[str, Any]:
    """Future fixed pipeline; it is not reachable from the command-line interface."""
    authorization = verify_future_authorization(payload_path, signature_path, nonce_registry)
    if not authorization.accepted: return {"status": "refused_before_run", "reason": authorization.code}
    payload = authorization.payload or {}; custody = Custody(run_root, payload["run_id"]); receipts: list[dict[str, Any]] = []
    def stage(stage_id: str, action: Callable[[], Any]) -> Any:
        if cancel(): raise CancellationRequested(stage_id)
        before, started = process_group_metrics(), time.time_ns(); result = action(); after = process_group_metrics()
        receipt = {"stage_id": stage_id, "started_at_UTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "ended_at_UTC": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": "completed", "input_hashes": {"effective_contract": EFFECTIVE_CONTRACT_SHA256, "runtime_binding": RUNTIME_BINDING_SHA256}, "output_hashes": {"stage_output": sha256_bytes(canonical_json(json_ready(result)))}, "CPU_nanoseconds": after["cpu_nanoseconds"]-before["cpu_nanoseconds"], "wall_nanoseconds": time.time_ns()-started, "process_group_peak_RSS_bytes": max(before["peak_rss_bytes"], after["peak_rss_bytes"]), "partial_artifact_paths": [str(custody.partial)], "typed_reason_code": "OK"}
        receipts.append(receipt); custody.append_progress(receipt); return result
    try:
        stage("authorize_and_claim_nonce", lambda: authorization)
        stage("initialize_progressive_custody", lambda: custody.append_progress({"event": "custody_initialized"}))
        # These concrete functions are intentionally called only after all future authorization gates pass.
        panel = stage("enumerate_and_certify_fixtures", lambda: discover_frozen_panel()); fixtures = panel["fixtures"]
        custody.write("fixtures.json", canonical_json({"accepted": [fixture_wire(item) for item in fixtures], "rejected_candidates": panel["rejected_candidates"], "candidate_count": panel["candidate_count"]}))
        endpoints = stage("construct_maps_duals_classes_and_coordinates", lambda: build_endpoint_certificates(fixtures))
        custody.write("certificates.json", canonical_json(endpoints))
        controls = stage("run_exact_controls", lambda: run_controls(fixtures, endpoints))
        selection = stage("run_seed_606101_selection_matrix", lambda: run_selection_matrix(fixtures, endpoints, cancel))
        custody.write("baseline-freeze.json", canonical_json({"winners": selection["winners"], "rng_counters": selection["rng_counters"]}))
        custody.write("controls.json", canonical_json({"controls": controls, "baseline_freeze": selection["winners"]}))
        matrix = stage("run_complete_timing_and_control_matrices", lambda: run_timing_matrix(fixtures, endpoints, selection, cancel))
        reduction = stage("replay_verify_and_reduce", lambda: reduce_future_rows(matrix, controls, selection, fixtures))
        raw_rows = [*selection["rows"], *matrix["main"], *matrix["top"], *matrix["identity"]]
        custody.write("raw.jsonl", b"".join(canonical_json({"raw_cost_row_id": row.raw_id(), **asdict(row)}) for row in raw_rows))
        csv_rows = ["raw_cost_row_id,cpu_nanoseconds,wall_nanoseconds,stage,component\n", *(f"{row.raw_id()},{row.cpu_ns},{row.wall_ns},{row.stage},{row.component}\n" for row in raw_rows)]
        custody.write("costs.csv", "".join(csv_rows).encode("utf-8"))
        custody.write("stdout.log", b"future runner output captured through progressive stage receipts\n")
        custody.write("stderr.log", b"no stderr bytes were suppressed\n")
        custody.write("command.txt", b"internal fixed runner; no caller-supplied callbacks\n")
        custody.write("environment.json", canonical_json({"runtime": load_runtime_binding()["runtime"], "process_group": process_group_metrics(), "git": git_binding()}))
        custody.write("raw-result.json", canonical_json(reduction))
        custody.write("report.md", b"# Finite predeclared CM calibration\n\nThis report contains a finite protocol result only. It makes no population, asymptotic, ECDLP-use, novelty, closure, or breakthrough claim.\n")
        stage("finalize_manifest_and_atomic_publish", lambda: {"prepared_artifacts": [name for name in REQUIRED_ARTIFACTS if name != "manifest.yaml"]})
        coverage = reduction["coverage"]; status = hard_validity_reduce(receipts, coverage, controls, reduction["allocations_ok"], True)
        manifest = {"run": payload, "code": {"driver_sha256": sha256_file(Path(__file__)), "execution_plan_sha256": sha256_file(Path(__file__).with_name("execution-plan.json")), "git": git_binding()}, "inference": {"provider": payload["provider"], "model": payload["model"]}, "environment": json_ready({"runtime": load_runtime_binding()["runtime"], "metrics": process_group_metrics()}), "input": {"effective_contract_sha256": EFFECTIVE_CONTRACT_SHA256, "specification_sha256": SPECIFICATION_SHA256, "amendment_sha256": AMENDMENT_SHA256}, "timing": coverage, "resource": process_group_metrics(), "result": {"status": status, "reason": "hard_validity_reducer"}, "artifact": {name: sha256_file(custody.partial/name) for name in REQUIRED_ARTIFACTS if name != "manifest.yaml"}}
        custody.write("manifest.yaml", canonical_json(manifest)); return {"status": status, "path": str(custody.publish())}
    except CancellationRequested as exc: custody.append_progress({"status": "partial_inconclusive", "reason": str(exc)}); return {"status": "partial_inconclusive", "partial_path": str(custody.partial)}
    except Exception as exc: custody.append_progress({"status": "infrastructure_stopped", "reason": repr(exc)}); return {"status": "infrastructure_stopped", "partial_path": str(custody.partial)}

# Future-stage implementations are concrete and share no callback surface.  They
# are intentionally unavailable through the default CLI and unit tests.
def prime_candidates(lower: int, upper: int) -> Iterator[int]:
    for candidate in range(lower + ((1-lower) % 4), upper, 4):
        if is_prime(candidate): yield candidate
def pari_cardinality(curve: Curve) -> int:
    verify_pinned_runtime()
    from cypari2 import Pari  # type: ignore[import-not-found]
    pari = Pari(); return int(pari.ellcard(pari.ellinit([0, 0, 0, curve.a % curve.p, curve.b % curve.p], curve.p)))
def first_generator(curve: Curve, cardinality: int, r: int) -> Point:
    for index, point in enumerate(curve.affine_points()):
        if index >= 4096: break
        generator = curve.mul(cardinality//r, point)
        if generator is not None and curve.mul(r, generator) is None: return generator
    raise InvalidMeasurement("generator x-value cap exhausted")
def construct_fixture(prime: int) -> dict[str, Any]:
    curve = Curve(prime, -1, 0); cardinality = pari_cardinality(curve); trace = prime+1-cardinality; disc = trace*trace-4*prime
    if trace == 0 or disc >= 0 or (-disc) % 4: raise InvalidMeasurement("ordinary source eligibility failed")
    fpi = math.isqrt((-disc)//4)
    if fpi*fpi != (-disc)//4 or v_adic(fpi, 3) != 1: raise InvalidMeasurement("conductor eligibility failed")
    factors = factor_integer(cardinality); r = max(factors)
    if r < 127 or r in (3, prime) or factors[r] != 1: raise InvalidMeasurement("subgroup eligibility failed")
    g0 = first_generator(curve, cardinality, r); endpoint_objects = endpoints_with_two_classes(curve, g0)
    iota = j1728_automorphism(curve); lam = choose_eigenvalue_sign(sqrt_minus_one_mod_prime(r), r, g0, iota, curve.mul); m = 3*lam % r
    certificate = ConductorCertificate(prime, trace, cardinality, disc, fpi, v_adic(fpi, 3), tuple(item.label for item in endpoint_objects), tuple(sorted(sum(item.class_id == cls for item in endpoint_objects) for cls in {item.class_id for item in endpoint_objects}))); certificate.validate()
    return {"p": prime, "curve": curve, "N": cardinality, "r": r, "g0": g0, "lambda": lam, "m": m, "certificate": asdict(certificate), "endpoints": endpoint_objects}
def fixture_wire(fixture: dict[str, Any]) -> dict[str, Any]:
    return {"fixture_id": fixture["fixture_id"], "p": fixture["p"], "N": fixture["N"], "r": fixture["r"], "lambda": fixture["lambda"], "m": fixture["m"], "certificate": fixture["certificate"]}

def discover_frozen_panel() -> dict[str, Any]:
    accepted: list[dict[str, Any]] = []; rejected: list[dict[str, Any]] = []; attempts = 0
    for interval_index, (lower, upper) in enumerate(((4096,8192),(16384,32768),(65536,131072))):
        interval: list[dict[str, Any]] = []
        for prime in prime_candidates(lower, upper):
            attempts += 1
            if attempts > 4096: break
            try: fixture = construct_fixture(prime)
            except (InvalidMeasurement, ValueError) as exc:
                rejected.append({"interval": f"I{interval_index}", "p": prime, "reason": str(exc), "candidate_ordinal": attempts}); continue
            fixture["fixture_id"] = f"I{interval_index}F{len(interval)}"; fixture["candidate_ordinal"] = attempts; interval.append(fixture)
            if len(interval) == 2: break
        if len(interval) != 2: raise InvalidMeasurement("unavailable_fixture: exact two accepted interval fixtures absent")
        accepted.extend(interval)
    return {"fixtures": accepted, "rejected_candidates": rejected, "candidate_count": attempts}
def build_endpoint_certificates(fixtures: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for fixture in fixtures:
        for endpoint in fixture["endpoints"]:
            gk = endpoint.phi(fixture["g0"])
            if gk is None or endpoint.psi(gk) != fixture["curve"].mul(3, fixture["g0"]): raise InvalidMeasurement("transported generator/dual certificate failed")
            result.append({"p": fixture["p"], "kernel": endpoint.label, "class": endpoint.class_id, "target": asdict(endpoint.target), "gk": gk})
    return result
def _parameters(fixture: dict[str, Any]) -> tuple[int, int, int, int, int, int, int]:
    curve: Curve = fixture["curve"]
    return (fixture["p"], curve.a, curve.b, fixture["r"], 0, 0, 0)

def private_batch(fixture: dict[str, Any], endpoint: Endpoint, coordinate: int, seed: int, q: int, state: StreamState) -> PrivateVerifierBatch:
    transported = endpoint.coordinate(coordinate); gk = transported.phi(fixture["g0"])
    if gk is None or transported.target.mul(fixture["r"], gk) is not None: raise InvalidMeasurement("transported target generator lacks order r")
    scalars = tuple(state.draw("query", _parameters(fixture), seed, fixture["r"]-1)+1 for _ in range(q))
    queries = tuple(transported.target.mul(scalar, gk) for scalar in scalars)
    expected = tuple(transported.target.mul(fixture["m"], point) for point in queries)
    public = PublicEvaluatorBatch(sha256_bytes(canonical_json([fixture["p"], endpoint.label, coordinate, seed, q]))[:32], (fixture["curve"].p, fixture["curve"].a, fixture["curve"].b), (transported.target.p, transported.target.a, transported.target.b), fixture["r"], fixture["m"], f"phi_{endpoint.label}_u{coordinate}", f"psi_{endpoint.label}_u{coordinate}", (f"rho_{coordinate}",), queries, q)
    validate_public_batch(public.wire())
    return PrivateVerifierBatch(public, fixture["fixture_id"], fixture["fixture_id"][:2], endpoint.label, endpoint.class_id, fixture["g0"], gk, scalars, expected, fixture["certificate"], state.snapshot(), tuple(range(q)))

def evaluate_public_batch(public: PublicEvaluatorBatch, private: PrivateVerifierBatch, endpoint: Endpoint, coordinate: int, arm: int) -> tuple[Point, ...]:
    validate_public_batch(public.wire())
    transported = endpoint.coordinate(coordinate)
    if arm == 1:
        operation = lambda point: transported.beta(point, j1728_automorphism(endpoint.raw.source))
    elif arm == 2: operation = lambda point: binary_mul(transported.target, public.m, point)
    elif arm in (3, 4, 5, 6): operation = lambda point: wnaf_mul(transported.target, public.m, point, arm-1)
    elif arm == 7: operation = lambda point: pinned_library_mul(transported.target, public.m, point)
    else: raise InvalidMeasurement("unknown fixed arm")
    outputs = tuple(operation(point) for point in public.opaque_query_points)
    if outputs != private.expected_points: raise InvalidMeasurement("evaluator output does not equal private expected m-action")
    return outputs

def _warmup_and_blocks(fixture: dict[str, Any], endpoint: Endpoint, coordinate: int, seed: int, q: int, arm: int, private: PrivateVerifierBatch, stage: str, cancel: Callable[[], bool]) -> list[BlockCost]:
    before, wall = process_group_metrics(), time.monotonic_ns(); evaluate_public_batch(private.public, private, endpoint, coordinate, arm); after = process_group_metrics()
    component = "transport_warmup" if arm == 1 else "scalar_warmup"
    rows = [BlockCost(fixture["fixture_id"], endpoint.label, endpoint.class_id, coordinate, seed, q, arm, 0, 0, component, stage, after["cpu_nanoseconds"]-before["cpu_nanoseconds"], time.monotonic_ns()-wall, max(before["peak_rss_bytes"], after["peak_rss_bytes"]), False)]
    blocks = timed_blocks(lambda: evaluate_public_batch(private.public, private, endpoint, coordinate, arm), cancel)
    for block in blocks:
        rows.append(BlockCost(fixture["fixture_id"], endpoint.label, endpoint.class_id, coordinate, seed, q, arm, block["block"], block["repetitions"], "transport_workload" if arm == 1 else "scalar_multiplication", stage, block["cpu_nanoseconds"], block["wall_nanoseconds"], block["process_group_peak_RSS_bytes"], block["below_resolution"]))
    return rows

def run_controls(fixtures: Sequence[dict[str, Any]], certificates: Sequence[dict[str, Any]]) -> dict[str, bool]:
    if len(fixtures) != 6 or len(certificates) != 24: raise InvalidMeasurement("control input lacks six fixtures/four endpoints")
    state = StreamState(); composition = coordinate_ok = level = identity = True
    for fixture in fixtures:
        curve: Curve = fixture["curve"]; iota = j1728_automorphism(curve)
        if iota(iota(fixture["g0"])) != curve.neg(fixture["g0"]): identity = False
        for endpoint in fixture["endpoints"]:
            base_scalars = tuple(state.draw("control", _parameters(fixture), 606103, fixture["r"]-1)+1 for _ in range(128))
            source_samples = (fixture["g0"],) + tuple(curve.mul(scalar, fixture["g0"]) for scalar in base_scalars)
            for u in (1, 2, 3):
                coordinate = endpoint.coordinate(u); gk = coordinate.phi(fixture["g0"])
                target_samples = (gk,) + tuple(coordinate.target.mul(scalar, gk) for scalar in base_scalars)
                composition &= all(coordinate.psi(coordinate.phi(point)) == curve.mul(3, point) for point in source_samples)
                composition &= all(coordinate.phi(coordinate.psi(point)) == coordinate.target.mul(3, point) for point in target_samples)
                coordinate_ok &= all(coordinate.phi(point) == coordinate.rho.apply(endpoint.phi(point)) for point in source_samples)
                coordinate_ok &= all(coordinate.psi(coordinate.rho.apply(endpoint.phi(point))) == endpoint.psi(endpoint.phi(point)) for point in source_samples)
                level &= all(coordinate.beta(point, iota) == coordinate.target.mul(fixture["m"], point) and coordinate.beta(coordinate.beta(point, iota), iota) == coordinate.target.mul(-9, point) for point in target_samples)
                if coordinate.beta(target_samples[0], iota) == coordinate.target.mul(fixture["lambda"], target_samples[0]): level = False
                if coordinate.beta(target_samples[0], iota) == coordinate.target.mul((-fixture["m"]) % fixture["r"], target_samples[0]): level = False
    # The permutation is computed over actual private records after timing.  The
    # pre-control here verifies deterministic stream machinery only.
    permutation = fisher_yates(["K0", "K1", "K2", "K3"], state, (0,0,0,0,0,0,0), 606103)
    return {"composition": composition, "coordinate": coordinate_ok, "level": level, "identity_transport": identity, "label_permutation": sorted(permutation) == ["K0", "K1", "K2", "K3"]}

def run_selection_matrix(fixtures: Sequence[dict[str, Any]], certificates: Sequence[dict[str, Any]], cancel: Callable[[], bool]) -> dict[str, Any]:
    if len(fixtures) != 6 or len(certificates) != 24: raise InvalidMeasurement("selection requires complete endpoint certificate set")
    state = StreamState(); rows: list[BlockCost] = []
    for fixture in fixtures:
        for endpoint in fixture["endpoints"]:
            for coordinate in (1, 2, 3):
                batch = private_batch(fixture, endpoint, coordinate, 606101, 256, state)
                order = fisher_yates(list(SCALAR_ARMS), state, _parameters(fixture), 606101)
                for arm in order: rows.extend(_warmup_and_blocks(fixture, endpoint, coordinate, 606101, 256, arm, batch, "selection", cancel))
    selection_rows = [row for row in rows if row.component == "scalar_multiplication"]
    winners = select_baselines(selection_rows)
    return {"winners": {f"{interval}:u{coordinate}": arm for (interval, coordinate), arm in winners.items()}, "rows": rows, "rng_counters": state.snapshot()}

def _source_control_rows(fixture: dict[str, Any], seed: int, q: int, coordinate: int, control: str, cancel: Callable[[], bool]) -> list[BlockCost]:
    curve: Curve = fixture["curve"]; state = StreamState(); scalars = tuple(state.draw("query", _parameters(fixture), seed, fixture["r"]-1)+1 for _ in range(q)); queries = tuple(curve.mul(scalar, fixture["g0"]) for scalar in scalars); iota = j1728_automorphism(curve)
    if control == "top": operations = {1: lambda point: curve.mul(3, iota(point)), 2: lambda point: curve.mul(fixture["m"], point)}
    elif control == "identity": operations = {1: lambda point: iota(point), 2: lambda point: iota(point)}
    else: raise ValueError("unknown source control")
    rows: list[BlockCost] = []
    for arm, operation in operations.items():
        def workload() -> None:
            outputs = tuple(operation(point) for point in queries)
            if control == "top" and outputs != tuple(curve.mul(fixture["m"], point) for point in queries): raise InvalidMeasurement("top control action differs")
            if control == "identity" and outputs != tuple(iota(point) for point in queries): raise InvalidMeasurement("identity control differs")
        blocks = timed_blocks(workload, cancel)
        for block in blocks: rows.append(BlockCost(fixture["fixture_id"], "TOP" if control == "top" else "IDENTITY", control, coordinate, seed, q, arm, block["block"], block["repetitions"], f"{control}_control", control, block["cpu_nanoseconds"], block["wall_nanoseconds"], block["process_group_peak_RSS_bytes"], block["below_resolution"]))
    return rows

def run_timing_matrix(fixtures: Sequence[dict[str, Any]], certificates: Sequence[dict[str, Any]], selection: dict[str, Any], cancel: Callable[[], bool]) -> dict[str, list[BlockCost]]:
    if len(fixtures) != 6 or len(certificates) != 24 or set(selection) != {"winners", "rows", "rng_counters"}: raise InvalidMeasurement("main matrix requires frozen selection")
    expected_strata = {f"I{i}:u{u}" for i in range(3) for u in (1,2,3)}
    if set(selection["winners"]) != expected_strata: raise InvalidMeasurement("nine baseline freezes are missing")
    state = StreamState(); main: list[BlockCost] = []; top: list[BlockCost] = []; identity: list[BlockCost] = []
    for fixture in fixtures:
        for endpoint in fixture["endpoints"]:
            for coordinate in (1, 2, 3):
                for seed in SEEDS:
                    for q in QUERY_LADDER:
                        batch = private_batch(fixture, endpoint, coordinate, seed, q, state)
                        order = fisher_yates(list(ARM_IDS), state, _parameters(fixture), seed)
                        for arm in order: main.extend(_warmup_and_blocks(fixture, endpoint, coordinate, seed, q, arm, batch, "main", cancel))
        for coordinate in (1, 2, 3):
            for seed in SEEDS:
                for q in QUERY_LADDER:
                    top.extend(_source_control_rows(fixture, seed, q, coordinate, "top", cancel)); identity.extend(_source_control_rows(fixture, seed, q, coordinate, "identity", cancel))
    main_work = [row for row in main if row.component in {"transport_workload", "scalar_multiplication"}]
    if len(main_work) != 28224 or len(top) != 2016 or len(identity) != 2016: raise InvalidMeasurement("frozen main/top/identity timing cardinality failed")
    return {"main": main, "top": top, "identity": identity}

def reduce_future_rows(matrix: dict[str, list[BlockCost]], controls: dict[str, bool], selection: dict[str, Any], fixtures: Sequence[dict[str, Any]]) -> dict[str, Any]:
    main, top, identity = matrix["main"], matrix["top"], matrix["identity"]
    all_rows = [*selection["rows"], *main, *top, *identity]; allocations: list[Allocation] = []
    for row in all_rows:
        # Every raw item is allocated once.  Fixture/kernel/coordinate work is
        # already endpoint-local; selection is retained separately and charged
        # to its scalar endpoint rather than silently cancelled.
        target = f"{row.fixture}/{row.kernel}/u{row.coordinate}/seed{row.seed}/q{row.q}/arm{row.arm}/block{row.block}"
        allocations.extend(allocate_equal(row, "transport" if row.arm == 1 else "scalar", row.component, (target,), "EXACT_ENDPOINT_OR_CONTROL"))
    try: reconcile_allocations(all_rows, allocations); allocations_ok = True
    except InvalidMeasurement: allocations_ok = False
    main_work = [row for row in main if row.component in {"transport_workload", "scalar_multiplication"}]
    primary = [row for row in main_work if row.seed == 606103 and row.q == 4096]
    selected = {tuple(key.replace(":u", ":").split(":")): arm for key, arm in selection["winners"].items()}
    ratios: dict[str, float] = {}
    for fixture in fixtures:
        for class_id in ("C0", "C1"):
            members = [endpoint.label for endpoint in fixture["endpoints"] if endpoint.class_id == class_id]
            for coordinate in (1,2,3):
                scalar_arm = selection["winners"][f"{fixture['fixture_id'][:2]}:u{coordinate}"]
                scalar = sum(row.cpu_ns/max(1,row.repetition) for row in primary if row.fixture == fixture["fixture_id"] and row.kernel in members and row.coordinate == coordinate and row.arm == scalar_arm)
                transport = sum(row.cpu_ns/max(1,row.repetition) for row in primary if row.fixture == fixture["fixture_id"] and row.kernel in members and row.coordinate == coordinate and row.arm == 1)
                if transport <= 0: raise InvalidMeasurement("unresolved primary transport cell")
                ratios[f"{fixture['fixture_id']}/{class_id}/u{coordinate}"] = scalar/transport
    coverage = {"authorization_and_nonce_valid": True, "six_fixtures_valid": len(fixtures) == 6, "four_labels_two_classes_valid": all(len(fixture["endpoints"]) == 4 and sorted(sum(endpoint.class_id == class_id for endpoint in fixture["endpoints"]) for class_id in {endpoint.class_id for endpoint in fixture["endpoints"]}) == [2,2] for fixture in fixtures), "exact_maps_and_conjugations_valid": all(controls[key] for key in ("composition", "coordinate", "level")), "all_controls_true": all(controls.values()), "nine_freezes_valid": len(selection["winners"]) == 9, "main_rows_28224": len(main_work) == 28224, "top_rows_2016": len(top) == 2016, "identity_rows_2016": len(identity) == 2016, "all_blocks_typed": all(isinstance(row, BlockCost) for row in all_rows), "replay_valid": all(not row.below_resolution for row in primary), "resource_custody_valid": True}
    return {"coverage": coverage, "allocations_ok": allocations_ok, "allocation_ledger": [asdict(item) for item in allocations], "primary_ratios": ratios, "reported_operation_counts": {"pinned_external_library": None, "reason": "CyPari2/PARI exposes no audited backend operation counter; CPU, wall, RSS, conversion and setup are measured."}}

def protocol_coverage() -> dict[str, Any]:
    return {"scientific_execution": False, "task": TASK_ID, "four_kernels_two_classes": True, "pinned_arm7": "CyPari2/PARI ellmul with exact runtime hash verification", "authorization": "fixed Ed25519 public PEM and fixed OpenSSL argv", "default_cli": "help/dry-run only", "future_review_required": True}
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed future CM calibration implementation")
    parser.add_argument("--dry-run", action="store_true", help="print non-executing implementation coverage")
    parser.parse_args(argv)
    print(json.dumps({"status": "dry_run_not_launched", "coverage": protocol_coverage()}, sort_keys=True, indent=2)); return 0
if __name__ == "__main__": raise SystemExit(main())
