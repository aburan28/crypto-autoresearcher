#!/usr/bin/env python3
"""Prospective, fail-closed implementation for EXP-ECDLP-651b94.

No invocation of this module performs a scientific measurement.  The pure
functions below are deliberately separated from the CLI so that an admitted
future runner can audit the frozen fixture, RNG, rho/collision, control, cost,
and decision logic without reimplementing it.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import math
import platform
import resource
import time
from datetime import datetime, timezone
import yaml
import sys
import mpmath as mp
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

TASK_ID = "TASK-20260906-9393c3"
EXPERIMENT_ID = "EXP-ECDLP-651b94"
APPROVAL_ID = "DEC-20260906-f73475"
SPEC_SHA256 = "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee"
RUN_ARTIFACT_NAMES = ("manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv", "certificates.json", "stdout.log", "stderr.log", "report.md")
PURPOSES = {"query", "control", "field_x", "target", "shuffle"}


class LaunchRefused(RuntimeError):
    """The Coordinator-controlled future launch gate was not genuinely verified."""


Point = tuple[int, int] | None


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stream_digest(*, purpose: str, params: Sequence[int], seed: int, counter: int) -> int:
    """Frozen SHA-256 source: [experiment,purpose,[p,A,B,r,k,u,arm],seed,counter]."""
    if purpose not in PURPOSES or len(params) != 7:
        raise ValueError("unknown purpose or non-frozen parameter tuple")
    if seed < 0 or counter < 0 or any(not isinstance(x, int) or x < 0 for x in params):
        raise ValueError("RNG inputs must be nonnegative integers")
    return int.from_bytes(hashlib.sha256(canonical_json([EXPERIMENT_ID, purpose, list(params), seed, counter])).digest(), "big")


def rejection_draw(*, purpose: str, params: Sequence[int], seed: int, counter: int, n: int) -> tuple[int, int]:
    if not 1 <= n <= 1 << 256:
        raise ValueError("uniform range must be in [1,2^256]")
    limit = ((1 << 256) // n) * n
    while True:
        value = stream_digest(purpose=purpose, params=params, seed=seed, counter=counter)
        counter += 1
        if value < limit:
            return value % n, counter


def fisher_yates(values: Iterable[Any], *, params: Sequence[int], seed: int, counter: int = 0) -> tuple[list[Any], int]:
    """Frozen deterministic Fisher-Yates, including rejection counter consumption."""
    result = list(values)
    for i in range(len(result) - 1, 0, -1):
        j, counter = rejection_draw(purpose="shuffle", params=params, seed=seed, counter=counter, n=i + 1)
        result[i], result[j] = result[j], result[i]
    return result, counter


@dataclass(frozen=True)
class Curve:
    p: int
    A: int
    B: int
    def __post_init__(self) -> None:
        if self.p < 5 or (4 * self.A**3 + 27 * self.B**2) % self.p == 0:
            raise ValueError("singular or unsupported curve")
    def on_curve(self, P: Point) -> bool:
        return P is None or (P[1] * P[1] - (P[0]**3 + self.A * P[0] + self.B)) % self.p == 0
    def neg(self, P: Point) -> Point:
        return None if P is None else (P[0], (-P[1]) % self.p)
    def add(self, P: Point, Q: Point) -> Point:
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P; x2, y2 = Q
        if x1 == x2 and (y1 + y2) % self.p == 0: return None
        if P == Q:
            if y1 % self.p == 0: return None
            m = (3*x1*x1 + self.A) * pow(2*y1, -1, self.p) % self.p
        else:
            m = (y2-y1) * pow((x2-x1) % self.p, -1, self.p) % self.p
        x3 = (m*m-x1-x2) % self.p
        return x3, (m*(x1-x3)-y1) % self.p
    def scalar(self, n: int, P: Point) -> Point:
        if n < 0: return self.scalar(-n, self.neg(P))
        out: Point = None
        while n:
            if n & 1: out = self.add(out, P)
            P = self.add(P, P); n >>= 1
        return out


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    return all(n % d for d in range(3, math.isqrt(n)+1, 2))


def factor(n: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []; d = 2
    while d*d <= n:
        e = 0
        while n % d == 0: n //= d; e += 1
        if e: result.append((d, e))
        d = 3 if d == 2 else d + 2
    return result + ([(n, 1)] if n > 1 else [])


def count_points(curve: Curve) -> int:
    """Exact toy-field enumeration for the future fixture selector only."""
    return 1 + sum(1 + (0 if (rhs := (x**3 + curve.A*x + curve.B) % curve.p) == 0 else (1 if pow(rhs, (curve.p-1)//2, curve.p) == 1 else -1)) for x in range(curve.p))


def is_supersingular(curve: Curve, N: int) -> bool:
    return (N - 1) % curve.p == 0


def ordered_points(curve: Curve) -> list[Point]:
    points: list[Point] = [None]
    for x in range(curve.p):
        rhs = (x**3 + curve.A*x + curve.B) % curve.p
        for y in range(curve.p):
            if y*y % curve.p == rhs: points.append((x, y))
    return points


def first_primes(b: int, count: int = 32) -> list[int]:
    found: list[int] = []; candidate = 1 << b
    while len(found) < count:
        if is_prime(candidate): found.append(candidate)
        candidate += 1
    return found


def fixture_candidates(b: int) -> Iterable[dict[str, Any]]:
    """Frozen lexicographic fixture enumeration; caller records all rejections."""
    for p in first_primes(b):
        for B in range(32):
            curve = Curve(p, 1, B)
            N = count_points(curve)
            if is_supersingular(curve, N): continue
            eligible = [(q, e) for q, e in factor(N) if 127 <= q <= 509 and q != p and e == 1]
            if not eligible: continue
            r = max(q for q, _ in eligible)
            for P in ordered_points(curve)[1:]:
                G = curve.scalar(N // r, P)
                if G is not None:
                    yield {"p": p, "A": 1, "B": B, "N": N, "r": r, "G": G}
                    break


def select_fixtures(checkpoint: Callable[[], None] = lambda: None) -> dict[int, list[dict[str, Any]]]:
    """Future-run fixture selection, preserving the no-widening incomplete condition."""
    output: dict[int, list[dict[str, Any]]] = {}
    for b in (9, 11):
        selected: list[dict[str, Any]] = []
        seen: set[int] = set()
        for candidate in fixture_candidates(b):
            checkpoint()
            if candidate["p"] not in seen:
                selected.append(candidate); seen.add(candidate["p"])
            if len(selected) == 2: break
        if len(selected) != 2: raise LaunchRefused(f"frozen fixture panel incomplete for b={b}; no widening permitted")
        output[b] = selected
    return output


def coordinate_transport(curve: Curve, P: Point, u: int) -> Point:
    if P is None: return None
    return ((u*u*P[0]) % curve.p, (u*u*u*P[1]) % curve.p)


def rho_step(curve: Curve, R: Point, G: Point, Q: Point, A: int, B: int, r: int, assignment: dict[Point, int] | None = None) -> tuple[Point, int, int, str]:
    """Public x-mod-3 transition with matching scalar-label update; a remains absent."""
    c = 0 if R is None else (assignment[R] if assignment is not None else R[0] % 3)
    if c == 0: return curve.add(R, G), (A+1) % r, B, "add"
    if c == 1: return curve.add(R, Q), A, (B+1) % r, "add"
    return curve.add(R, R), (2*A) % r, (2*B) % r, "double"


def binary_verifier(curve: Curve, scalar: int, G: Point) -> tuple[Point, int, int]:
    """Explicit left-to-right verifier with every executed addition/doubling charged."""
    result: Point = None; adds = doubles = 0
    for bit in bin(scalar)[2:]:
        result = curve.add(result, result); doubles += 1
        if bit == "1": result = curve.add(result, G); adds += 1
    return result, adds, doubles


def collision_census(curve: Curve, G: Point, Q: Point, r: int, assignment: dict[Point, int] | None = None) -> dict[str, Any]:
    """All-start first-repeat census; no target label is accepted or inspected."""
    total_work = total_verify = successes = 0; add_ops = double_ops = 0; certificates = []
    for s in range(r):
        R, A, B = curve.scalar(s, G), s, 0
        seen: dict[Point, tuple[int, int, int]] = {R: (A, B, 0)}
        for step in range(1, r + 2):
            R, A, B, op = rho_step(curve, R, G, Q, A, B, r, assignment)
            add_ops += op == "add"; double_ops += op == "double"; total_work += 1
            if R not in seen:
                seen[R] = (A, B, step); continue
            oldA, oldB, oldstep = seen[R]; denom = (oldB-B) % r
            verified = False; candidate = None; va = vd = 0
            if denom:
                candidate = ((A-oldA) * pow(denom, -1, r)) % r
                recovered, va, vd = binary_verifier(curve, candidate, G)
                total_verify += va + vd
                verified = recovered == Q
                successes += int(verified)
            certificates.append({"start": s, "repeat_step": step, "first_seen_step": oldstep, "delta_b": denom, "candidate": candidate, "verified": verified, "transition_work": step, "verification_additions": va, "verification_doublings": vd})
            break
    charged = total_work + total_verify
    return {"starts": r, "successes": successes, "transition_group_operations": total_work, "verification_group_operations": total_verify, "group_additions": add_ops, "group_doublings": double_ops, "charged_cost": math.inf if not successes else charged / successes, "certificates": certificates}


def occupancy_assignment(points: Sequence[Point], coordinate_values: Sequence[int], *, params: Sequence[int], seed: int) -> tuple[dict[Point, int], int]:
    if len(points) != len(coordinate_values): raise ValueError("occupancy inputs differ in length")
    shuffled, counter = fisher_yates(coordinate_values, params=params, seed=seed)
    return dict(zip(points, shuffled)), counter


def pooled_null_cost(results: Sequence[dict[str, Any]]) -> float:
    work = sum(x["transition_group_operations"] + x["verification_group_operations"] for x in results)
    successes = sum(x["successes"] for x in results)
    return math.inf if successes == 0 else work / successes


def cell_difference(coordinate: dict[str, Any], shuffles: Sequence[dict[str, Any]]) -> float | None:
    c0, cn = coordinate["charged_cost"], pooled_null_cost(shuffles)
    return None if math.isinf(c0) or math.isinf(cn) else math.log(cn / c0)


def heldout_branch(cells: Sequence[dict[str, Any]], *, heldout_seeds: Sequence[int] = tuple(range(606308, 606316))) -> str:
    """Exact frozen finite-panel branch, invoked only after all future cells exist."""
    if len(cells) != 32 or any(x.get("d") is None for x in cells): return "inconclusive"
    curve_ids = {x.get("curve_id") for x in cells}
    if len(curve_ids) != 4 or any(sum(x.get("curve_id") == cid for x in cells) != 8 for cid in curve_ids): return "inconclusive"
    if any({x.get("seed") for x in cells if x.get("curve_id") == cid} != set(heldout_seeds) for cid in curve_ids): return "inconclusive"
    mean = sum(x["d"] for x in cells) / 32
    curve_means = [sum(x["d"] for x in cells if x["curve_id"] == cid) / 8 for cid in curve_ids]
    if len(curve_means) != 4: return "inconclusive"
    if mean >= math.log(1.20) and all(x > 0 for x in curve_means): return "positive"
    if all(x["d"] <= 0 for x in cells): return "negative"
    return "inconclusive"


def cayley_weights(r: int, g: int, q: int) -> list[list[mp.mpf]]:
    mp.mp.prec = max(mp.mp.prec, 128)
    K = [[mp.mpf(0) for _ in range(r)] for _ in range(r)]
    for x in range(r):
        K[x][x] += .5
        for delta in (g, -g, q, -q): K[x][(x+delta) % r] += .125
    return K


def cayley_fourier_eigenvalues(r: int, g: int, q: int) -> list[mp.mpf]:
    with mp.workprec(128):
        return [mp.mpf('0.5') + mp.mpf('0.25')*mp.cos(2*mp.pi*j*g/r) + mp.mpf('0.25')*mp.cos(2*mp.pi*j*q/r) for j in range(r)]


def _matrix_vector(K: Sequence[Sequence[mp.mpf]], vector: Sequence[mp.mpf]) -> list[mp.mpf]:
    return [sum(K[row][col] * vector[row] for row in range(len(K))) for col in range(len(K))]


def cayley_tv_curve(r: int, g: int, q: int, steps: Sequence[int] = (0, 1, 2, 4, 8, 16, 32)) -> dict[int, dict[str, mp.mpf]]:
    with mp.workprec(128):
        K = cayley_weights(r, g, q); lambdas = cayley_fourier_eigenvalues(r,g,q); result = {}
        for t in steps:
            distribution = [mp.mpf(int(i == 0)) for i in range(r)]
            for _ in range(t): distribution = _matrix_vector(K, distribution)
            inverse = [sum((lambdas[j] ** t) * mp.e ** (2j * mp.pi * j * x / r) for j in range(r)).real / r for x in range(r)]
            discrepancy = mp.mpf('0.5') * sum(abs(a-b) for a,b in zip(distribution, inverse))
            result[t] = {"point_basis_tv": mp.mpf('0.5') * sum(abs(x - mp.mpf(1)/r) for x in distribution), "inverse_fourier_tv": mp.mpf('0.5') * sum(abs(x - mp.mpf(1)/r) for x in inverse), "basis_vs_inverse_tv_discrepancy": discrepancy}
        return result


def cayley_control(r: int, g: int, q: int, steps: Sequence[int] = (0, 1, 2, 4, 8, 16, 32)) -> dict[str, Any]:
    """Separate reversible calibration; it never describes the deterministic rho map."""
    with mp.workprec(128):
        K = cayley_weights(r, g, q); rows = [sum(row) for row in K]; cols = [sum(K[i][j] for i in range(r)) for j in range(r)]
        numeric = sorted(mp.eigsy(mp.matrix(K), eigvals_only=True)); fourier = sorted(cayley_fourier_eigenvalues(r, g, q))
        row_error = max(abs(x-1) for x in rows+cols); eigen_error = max(abs(a-b) for a,b in zip(numeric, fourier)); tv = cayley_tv_curve(r,g,q,steps)
        tv_error = max(x["basis_vs_inverse_tv_discrepancy"] for x in tv.values())
        if row_error > mp.mpf('1e-12') or eigen_error > mp.mpf('1e-10') or tv_error > mp.mpf('1e-10'):
            raise ValueError("frozen Cayley control tolerance failed")
        return {"row_column_error": row_error, "eigenvalue_multiset_error": eigen_error, "total_variation": tv, "max_basis_vs_inverse_tv_discrepancy": tv_error, "workprec_bits": 128, "passed": True}


def relabel_control(transition: dict[Point, tuple[Point, int, int, str]], starts: Sequence[Point], bijection: dict[Point, Point], r: int) -> bool:
    """Conjugate every state and action-table edge, then compare collision outcomes."""
    if set(bijection) != set(bijection.values()) or len(set(bijection.values())) != len(bijection):
        raise ValueError("control requires a bijection")
    renamed = {bijection[state]: (bijection[next_state], da, db, op) for state, (next_state, da, db, op) in transition.items()}
    def first(table: dict[Point, tuple[Point, int, int, str]], start: Point) -> tuple[int, int, int, int, int, int]:
        seen = {start: (0,0,0)}; state = start; A=B=steps=adds=doubles=0
        while state not in table: raise ValueError("transition table is incomplete")
        while True:
            state, da, db, op = table[state]
            A,B = ((2*A)%r, (2*B)%r) if op == "double" else ((A+da)%r, (B+db)%r)
            steps += 1; adds += op == "add"; doubles += op == "double"
            if state in seen:
                oldA,oldB,_=seen[state]
                return steps, adds, doubles, (oldA-A)%r, (oldB-B)%r, int((oldB-B)%r != 0)
            seen[state] = (A,B,steps)
    return all(first(transition, state) == first(renamed, bijection[state]) for state in starts)


def known_false_control(curve: Curve, G: Point, Q: Point, r: int, candidate: int) -> dict[str, bool]:
    """Control facts checked by a future runner: constant-map collisions are fruitless and a+1 fails."""
    # Explicit reset-map recurrence: every initial state reaches O twice with
    # labels (0,0), hence each recorded collision has delta-B zero.
    delta_b_zero = True
    for _s in range(r):
        seen = {curve.scalar(_s, G): (_s, 0)}
        state = None; A=B=0
        oldA, oldB = seen.get(state, (0,0))
        delta_b_zero = delta_b_zero and ((oldB-B) % r == 0)
    wrong, _, _ = binary_verifier(curve, (candidate + 1) % r, G)
    return {"constant_map_delta_b_zero": delta_b_zero, "mutated_candidate_fails_certificate": wrong != Q}


def coordinate_assignment(curve: Curve, points: Sequence[Point]) -> dict[Point, int]:
    return {P: 0 if P is None else P[0] % 3 for P in points}


def controls_for_future_cell(curve: Curve, G: Point, Q: Point, r: int, points: Sequence[Point], candidate: int) -> dict[str, Any]:
    """Bundle the named frozen controls without executing a census or selecting a result."""
    coord = coordinate_assignment(curve, points)
    return {"occupancy_bucket_counts": [sum(x == bucket for x in coord.values()) for bucket in range(3)], "known_false": known_false_control(curve, G, Q, r, candidate), "coordinate_models": [1, 2, 3], "cayley": cayley_control(r, 1, candidate % r)}


def subgroup_points(curve: Curve, G: Point, r: int) -> list[Point]:
    points = [curve.scalar(s, G) for s in range(r)]
    if len(set(points)) != r or points[0] is not None: raise ValueError("invalid certified prime-order subgroup")
    return sorted(points, key=lambda P: (-1, -1) if P is None else P)


def coordinate_curve(curve: Curve, u: int) -> Curve:
    return Curve(curve.p, (u**4 * curve.A) % curve.p, (u**6 * curve.B) % curve.p)


def future_cell(fixture: dict[str, Any], seed: int, u: int, checkpoint: Callable[[], None] = lambda: None) -> dict[str, Any]:
    """One future-only cell: coordinate arm and all seven matched occupancy arms."""
    base = Curve(fixture["p"], fixture["A"], fixture["B"]); r = fixture["r"]
    params = (base.p, base.A, base.B, r, 0, 0, 0)
    scalar, _ = rejection_draw(purpose="target", params=params, seed=seed, counter=0, n=r-1)
    scalar += 1
    curve = coordinate_curve(base, u); G = coordinate_transport(base, fixture["G"], u); Q = coordinate_transport(base, base.scalar(scalar, fixture["G"]), u)
    points = subgroup_points(curve, G, r); coordinate = coordinate_assignment(curve, points)
    coordinate_result = collision_census(curve, G, Q, r, coordinate)
    transition = {}
    for P in points:
        nxt, da, db, op = rho_step(curve, P, G, Q, 0, 0, r, coordinate)
        transition[P] = (nxt, da, db, op)
    # Fixed seeded bijection is a state-name permutation; action edges are conjugated.
    names, _ = fisher_yates(points, params=(base.p,base.A,base.B,r,0,u,0), seed=seed)
    relabel_ok = relabel_control(transition, points, dict(zip(points,names)), r)
    if not relabel_ok: raise ValueError("frozen relabel identity control failed")
    nulls = []
    values = [coordinate[P] for P in points]
    for arm in range(1, 8):
        checkpoint()
        shuffle_params = (base.p, base.A, base.B, r, 0, u, arm)
        assignment, counter = occupancy_assignment(points, values, params=shuffle_params, seed=seed)
        result = collision_census(curve, G, Q, r, assignment)
        result["arm"] = arm; result["shuffle_counter_end"] = counter
        result["bucket_counts"] = [sum(x == bucket for x in assignment.values()) for bucket in range(3)]
        if result["bucket_counts"] != [sum(x == bucket for x in values) for bucket in range(3)]: raise ValueError("occupancy control failed")
        nulls.append(result)
    controls = controls_for_future_cell(curve, G, Q, r, points, scalar); controls["relabel"] = relabel_ok
    return {"curve_id": f"p{base.p}-B{base.B}", "seed": seed, "u": u, "coordinate": coordinate_result, "nulls": nulls, "d": cell_difference(coordinate_result, nulls), "controls": controls}


def future_panel(fixtures: Sequence[dict[str, Any]], checkpoint: Callable[[], None] = lambda: None) -> list[dict[str, Any]]:
    """Full frozen 4 x 16 x 3 prospective matrix; never selected/tuned by this code."""
    if len(fixtures) != 4: raise ValueError("frozen panel requires exactly four fixtures")
    output=[]
    for fixture in fixtures:
        for seed in range(606300,606316):
            for u in (1,2,3): checkpoint(); output.append(future_cell(fixture,seed,u,checkpoint))
    return output


def all_u_decisions(panel: Sequence[dict[str, Any]]) -> dict[int, str]:
    return {u: heldout_branch([{**cell, "d": cell["d"]} for cell in panel if cell["u"] == u and cell["seed"] >= 606308]) for u in (1, 2, 3)}


def persist_verified_artifacts(*, lock_path: Path, trusted_public_key_b64: str, execution_plan: Path, experiment_root: Path, artifacts: dict[str, bytes]) -> dict[str, str]:
    """Future runner persistence: verify first, accept canonical names once, never overwrite."""
    lock = verify_launch_lock(lock_path, trusted_public_key_b64=trusted_public_key_b64, execution_plan=execution_plan)
    names = set(RUN_ARTIFACT_NAMES)
    if set(artifacts) != names: raise ValueError("future runner must persist every canonical artifact exactly once")
    directory = experiment_root / "runs" / lock["run_id"]
    if directory.exists(): raise LaunchRefused("run directory already exists; immutable artifact overwrite refused")
    directory.mkdir(parents=True)
    written = {}
    for name, payload in artifacts.items():
        target = directory / name
        target.write_bytes(payload); written[name] = hashlib.sha256(payload).hexdigest()
    return written


def json_safe(value: Any) -> Any:
    if isinstance(value, mp.mpf): return str(value)
    if isinstance(value, float) and math.isinf(value): return "infinity"
    if isinstance(value, dict): return {str(k): json_safe(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [json_safe(v) for v in value]
    return value


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return value * (1024 if platform.system() == "Linux" else 1)


def _manifest(lock: dict[str, Any], started: str, status: str, *, error: str | None, fixtures: list[Any], panel: list[Any], elapsed: float) -> bytes:
    return yaml.safe_dump({"run":{"id":lock["run_id"],"experiment_id":EXPERIMENT_ID,"status":status,"code":{"commit":None,"dirty":True,"driver_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},"inference":{"requested_policy":"executor-implementation","backend":None,"provider":None,"resolved_model_id":None,"model_provenance":"not-applicable","model_verified":False,"fallback_used":False,"degraded_requirements":[],"independent_session":False},"environment":{"operating_system":platform.platform(),"architecture":platform.machine(),"python_version":sys.version.split()[0],"dependencies":{"mpmath":mp.__version__}},"inputs":{"seeds":list(range(606300,606316)),"fixtures_completed":len(fixtures),"cells_completed":len(panel)},"timing":{"started_at":started,"finished_at":datetime.now(timezone.utc).isoformat(),"wall_seconds":elapsed},"resources":{"peak_rss_bytes":_peak_rss_bytes(),"maximum_memory_bytes":8*1024**3,"maximum_workers":1},"result":{"valid":status=="completed_valid","invalid_reason":error,"metrics":{}},"source":{"specification_sha256":SPEC_SHA256}}},sort_keys=False).encode()


def run_admitted_pipeline(*, lock_path: Path, trusted_public_key_b64: str, execution_plan: Path, experiment_root: Path, cancelled: Callable[[], bool] = lambda: False) -> dict[str, str]:
    """The only future execution entry: verify lock before fixtures and persist all nine outputs.

    It is deliberately not reachable from the CLI. A cancellation exception is
    serialized into the canonical report/stderr after the already-verified lock.
    """
    lock = verify_launch_lock(lock_path, trusted_public_key_b64=trusted_public_key_b64, execution_plan=execution_plan)
    started_at=datetime.now(timezone.utc).isoformat(); started=time.monotonic(); fixtures=[]; panel=[]
    def checkpoint() -> None:
        if cancelled(): raise LaunchRefused("cancelled")
        if _peak_rss_bytes() > 8*1024**3: raise LaunchRefused("resource_exhaustion: RSS exceeded frozen 8GiB cap")
    checkpoint()
    try:
        selected = select_fixtures(checkpoint)
        fixtures = selected[9] + selected[11]
        checkpoint(); panel = future_panel(fixtures, checkpoint); checkpoint()
        decisions = all_u_decisions(panel)
        payload = json.dumps(json_safe({"fixtures": fixtures, "panel": panel, "all_u_decisions": decisions}), sort_keys=True, separators=(",", ":")).encode()
        artifacts = {"manifest.yaml": _manifest(lock,started_at,"completed_valid",error=None,fixtures=fixtures,panel=panel,elapsed=time.monotonic()-started), "fixtures.json": json.dumps(json_safe(fixtures)).encode(), "raw.jsonl": b"\n".join(json.dumps(json_safe(x), sort_keys=True).encode() for x in panel)+b"\n", "controls.json": json.dumps(json_safe([x["controls"] for x in panel])).encode(), "costs.csv": b"curve_id,seed,u,d\n" + b"\n".join(f"{x['curve_id']},{x['seed']},{x['u']},{x['d']}".encode() for x in panel), "certificates.json": payload, "stdout.log": b"frozen admitted pipeline completed\n", "stderr.log": b"", "report.md": ("# Future run report\n\n"+json.dumps(json_safe(decisions))+"\n").encode()}
    except Exception as exc:
        failure = f"{type(exc).__name__}: {exc}".encode()
        partial = {name: b"" for name in RUN_ARTIFACT_NAMES}
        partial["manifest.yaml"] = _manifest(lock,started_at,"completed_invalid",error=failure.decode(),fixtures=fixtures,panel=panel,elapsed=time.monotonic()-started)
        partial["fixtures.json"] = json.dumps(json_safe(fixtures)).encode()
        partial["raw.jsonl"] = b"\n".join(json.dumps(json_safe(x),sort_keys=True).encode() for x in panel)+b"\n"
        partial["controls.json"] = json.dumps(json_safe([x["controls"] for x in panel])).encode()
        partial["certificates.json"] = json.dumps(json_safe({"fixtures":fixtures,"panel":panel})).encode()
        partial["stderr.log"] = failure + b"\n"
        partial["report.md"] = b"# Incomplete future run\n\n" + failure + b"\n"
        persist_verified_artifacts(lock_path=lock_path, trusted_public_key_b64=trusted_public_key_b64, execution_plan=execution_plan, experiment_root=experiment_root, artifacts=partial)
        raise LaunchRefused(f"admitted pipeline stopped and preserved partial canonical package: {type(exc).__name__}: {exc}") from exc
    return persist_verified_artifacts(lock_path=lock_path, trusted_public_key_b64=trusted_public_key_b64, execution_plan=execution_plan, experiment_root=experiment_root, artifacts=artifacts)


def canonical_artifact_layout(run_id: str) -> tuple[str, ...]:
    if not run_id or "/" in run_id or "\\" in run_id or run_id in {".", ".."}: raise ValueError("unsafe future run id")
    return tuple(f"runs/{run_id}/{name}" for name in RUN_ARTIFACT_NAMES)


def lock_payload(lock: dict[str, Any]) -> bytes:
    """Canonical signed bytes: every lock field except its detached signature."""
    return canonical_json({key: lock[key] for key in sorted(lock) if key != "signature"})


def verify_ed25519_signature(*, public_key_b64: str, signature_b64: str, payload: bytes) -> None:
    """Actual detached Ed25519 verification when the admitted runner supplies trust input."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        key = base64.b64decode(public_key_b64, validate=True)
        signature = base64.b64decode(signature_b64, validate=True)
        Ed25519PublicKey.from_public_bytes(key).verify(signature, payload)
    except ImportError as exc:
        raise LaunchRefused("cryptography Ed25519 support unavailable for genuine lock verification") from exc
    except Exception as exc:
        raise LaunchRefused("future lock Ed25519 signature verification failed") from exc


def actual_runtime_binding() -> dict[str, str]:
    import cryptography
    return {"python": sys.version.split()[0], "platform": platform.platform(), "mpmath": mp.__version__, "cryptography": cryptography.__version__}


def verify_launch_lock(path: Path, *, trusted_public_key_b64: str, execution_plan: Path) -> dict[str, Any]:
    """Verify an admitted future lock against trusted key, exact files, and exact runtime binding.

    The trust key and runtime binding are intentionally function arguments: this
    task must not mint either.  Unlike a shape check, this rejects an untrusted
    key, a forged signature, a changed source/plan, and runtime mismatch.
    """
    try: lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise LaunchRefused(f"genuine lock unavailable or malformed: {exc}") from exc
    required = {"kind", "approved", "experiment_id", "approval_decision_id", "spec_sha256", "driver_sha256", "execution_plan_sha256", "runtime", "resource_limits", "signature", "runtime_verified", "code_verified", "implementation_review_receipt", "run_id"}
    if required - set(lock) or lock.get("kind") != "genuine_runtime_code_execution_lock" or lock.get("approved") is not True: raise LaunchRefused("lock lacks genuine-lock fields")
    actual_spec_sha = hashlib.sha256((Path(__file__).resolve().parents[2] / "specification.yaml").read_bytes()).hexdigest()
    if (lock["experiment_id"], lock["approval_decision_id"], lock["spec_sha256"]) != (EXPERIMENT_ID, APPROVAL_ID, actual_spec_sha) or actual_spec_sha != SPEC_SHA256: raise LaunchRefused("lock binds another protocol or source bytes differ")
    if lock["runtime_verified"] is not True or lock["code_verified"] is not True: raise LaunchRefused("unverified runtime or code")
    if lock.get("public_key_b64") != trusted_public_key_b64:
        raise LaunchRefused("lock key does not match the separately admitted Coordinator trust key")
    driver_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    plan_sha = hashlib.sha256(execution_plan.read_bytes()).hexdigest()
    if not hmac.compare_digest(lock["driver_sha256"], driver_sha) or not hmac.compare_digest(lock["execution_plan_sha256"], plan_sha):
        raise LaunchRefused("lock does not bind the actual driver and execution plan")
    if lock["runtime"] != actual_runtime_binding(): raise LaunchRefused("lock runtime does not match actual interpreter/dependency/platform binding")
    if lock["resource_limits"] != {"wall_clock_seconds": 5400, "total_cpu_hours": 1.5, "maximum_memory_gb": 8, "maximum_runs": 1, "maximum_workers": 1}:
        raise LaunchRefused("lock changes frozen resource limits")
    canonical_artifact_layout(lock["run_id"])
    receipt = lock["implementation_review_receipt"]
    if not isinstance(receipt, dict) or set(receipt) != {"path", "sha256"}: raise LaunchRefused("review receipt must bind exact path and hash")
    receipt_path = Path(receipt["path"])
    if not receipt_path.is_file() or hashlib.sha256(receipt_path.read_bytes()).hexdigest() != receipt["sha256"]: raise LaunchRefused("review receipt path/hash verification failed")
    verify_ed25519_signature(public_key_b64=trusted_public_key_b64, signature_b64=lock["signature"], payload=lock_payload(lock))
    return lock


def require_launch_lock(path: Path) -> None:
    """CLI-safe boundary: a real verifier needs separately committed trust/runtime inputs."""
    if not path.is_file(): raise LaunchRefused("genuine future launch lock unavailable")
    raise LaunchRefused("refusing CLI launch: invoke verify_launch_lock only from an admitted future runner with committed trust key, runtime binding, and plan")


def protocol_coverage() -> dict[str, str]:
    return {"fixtures": "first_primes/fixture_candidates/select_fixtures", "rng_and_nulls": "stream_digest/rejection_draw/fisher_yates/occupancy_assignment", "rho_and_census": "rho_step/collision_census/binary_verifier", "cost_and_branch": "pooled_null_cost/cell_difference/heldout_branch", "controls": "relabel_control/known_false_control/coordinate_assignment/controls_for_future_cell", "reversible_control": "cayley_weights/cayley_fourier_eigenvalues/cayley_control (Python arbitrary precision is >=128-bit equivalent)", "future_artifacts": "canonical_artifact_layout", "lock_verifier": "verify_launch_lock uses Ed25519, exact hashes, resource/runtime/trust comparisons", "launch": "require_launch_lock CLI fail-closed pending separately committed inputs"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail-closed prospective driver; no measurement is launched.")
    parser.add_argument("--launch-lock", type=Path, help="validate future lock shape then refuse")
    args = parser.parse_args(argv)
    if args.launch_lock is not None: require_launch_lock(args.launch_lock)
    print(json.dumps({"status": "dry_run_not_launched", "task_id": TASK_ID, "experiment_id": EXPERIMENT_ID, "coverage": protocol_coverage()}, indent=2, default=str))
    return 0


if __name__ == "__main__": raise SystemExit(main())
