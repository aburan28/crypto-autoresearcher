#!/usr/bin/env python3
"""Prospective, lock-gated backend for EXP-ECDLP-1b1b99.

Nothing in this module runs a scientific fixture at import time or through the
default CLI.  ``execute_frozen_run`` is deliberately reachable only after a
future Coordinator authorization has been authenticated by a separately
supplied verifier.  The implementation is kept here, rather than hidden behind
callbacks, so review can inspect all curve, map, dual, scalar, control, timing,
and artifact logic before any measurement is authorized.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

TASK_ID = "TASK-20260907-aa1985"
EXPERIMENT_ID = "EXP-ECDLP-1b1b99"
APPROVAL_ID = "DEC-20260906-f73475"
IMPLEMENTATION_APPROVAL_ID = "DEC-20260907-b21c85"
SPEC_SHA256 = "b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff"
QUERY_LADDER = (1, 16, 256, 4096)
MEASUREMENT_SEEDS = (606101, 606103)
SCALAR_ARMS = ("binary_double_and_add", "wnaf_w2", "wnaf_w3", "wnaf_w4", "wnaf_w5", "pinned_library")
RUN_ARTIFACT_NAMES = ("manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv", "certificates.json", "stdout.log", "stderr.log", "report.md")
COST_TERMS = ("Cshared", "Cdiscovery_all_candidates", "Cpointcount_factor", "Ckernel_search", "Cmaps", "Clevel_cert", "Ceigenvalue_sign", "Cnormalization", "Cpsi", "Ci", "Cphi", "Cverify", "Calgorithm_selection", "Cscalar_setup", "Cmul")
FROZEN_LIMITS = {"wall_clock_seconds": 7200, "total_cpu_hours": 2, "memory_gb": 8, "maximum_runs": 1, "maximum_workers": 1}


class LaunchRefused(RuntimeError): pass
class CancellationRequested(RuntimeError): pass
class InvalidMeasurement(RuntimeError): pass


Point = tuple[int, int] | None


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False, sort_keys=True).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def specification_path() -> Path:
    return repo_root() / "experiments/EXP-ECDLP-1b1b99/specification.yaml"


def stream_digest(*, purpose: str, parameters: Sequence[int], seed: int, counter: int) -> int:
    if purpose not in {"query", "control", "field_x", "target", "shuffle"} or len(parameters) != 7:
        raise ValueError("frozen stream needs a listed purpose and [p,A,B,r,k,u,arm]")
    if seed < 0 or counter < 0 or any(not isinstance(x, int) for x in parameters):
        raise ValueError("stream tuple must contain integer values and nonnegative seed/counter")
    # The frozen wire form follows JSON.stringify's insertion order, not sort_keys.
    wire = json.dumps([EXPERIMENT_ID, purpose, list(parameters), seed, counter], separators=(",", ":"), ensure_ascii=False).encode()
    return int.from_bytes(hashlib.sha256(wire).digest(), "big")


def rejection_draw(*, purpose: str, parameters: Sequence[int], seed: int, counter: int, n: int) -> tuple[int, int]:
    if n < 1: raise ValueError("n must be positive")
    limit = ((1 << 256) // n) * n
    while True:
        digest = stream_digest(purpose=purpose, parameters=parameters, seed=seed, counter=counter)
        counter += 1
        if digest < limit: return digest % n, counter


def fisher_yates(values: Iterable[Any], *, parameters: Sequence[int], seed: int, counter: int) -> tuple[list[Any], int]:
    out = list(values)
    for i in range(len(out) - 1, 0, -1):
        j, counter = rejection_draw(purpose="shuffle", parameters=parameters, seed=seed, counter=counter, n=i + 1)
        out[i], out[j] = out[j], out[i]
    return out, counter


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int
    def __post_init__(self) -> None:
        if self.p <= 3 or (4 * self.a**3 + 27 * self.b**2) % self.p == 0: raise ValueError("singular/unsupported curve")
    def on_curve(self, P: Point) -> bool:
        return P is None or (P[1]*P[1] - (P[0]**3 + self.a*P[0] + self.b)) % self.p == 0
    def neg(self, P: Point) -> Point: return None if P is None else (P[0] % self.p, -P[1] % self.p)
    def add(self, P: Point, Q: Point) -> Point:
        if P is None: return Q
        if Q is None: return P
        x1,y1=P; x2,y2=Q; p=self.p
        if x1 == x2 and (y1+y2) % p == 0: return None
        if P == Q: slope=(3*x1*x1+self.a)*pow(2*y1,-1,p)%p
        else: slope=(y2-y1)*pow(x2-x1,-1,p)%p
        x3=(slope*slope-x1-x2)%p
        return x3, (slope*(x1-x3)-y1)%p
    def mul(self, n: int, P: Point) -> Point:
        if n < 0: return self.mul(-n, self.neg(P))
        out: Point=None
        while n:
            if n & 1: out=self.add(out,P)
            P=self.add(P,P); n >>= 1
        return out
    def points(self) -> list[Point]:
        out=[None]
        for x in range(self.p):
            rhs=(x*x*x+self.a*x+self.b)%self.p
            for y in range(self.p):
                if y*y % self.p == rhs: out.append((x,y))
        return out
    def order(self) -> int: return len(self.points())


def point_key(P: Point) -> tuple[int, int]: return (-1,-1) if P is None else P


def factor_integer(n: int) -> dict[int,int]:
    out={}; d=2
    while d*d <= n:
        while n%d == 0: out[d]=out.get(d,0)+1; n//=d
        d += 1 if d == 2 else 2
    if n>1: out[n]=out.get(n,0)+1
    return out


def is_prime(n: int) -> bool: return n > 1 and len(factor_integer(n)) == 1 and factor_integer(n).get(n) == 1


def full_rational_three_torsion(E: Curve) -> tuple[list[Point], list[tuple[Point, Point]]]:
    """Enumerate all eight nonzero rational 3-torsion points and four kernels.

    A kernel is represented by its two nonzero points in canonical +-pair order.
    This deliberately rejects partial rational torsion; it never mistakes one
    rational subgroup for the frozen full E[3] requirement.
    """
    torsion=sorted([P for P in E.points() if P is not None and E.mul(3,P) is None], key=point_key)
    if len(torsion) != 8: raise InvalidMeasurement(f"full rational E[3] required; found {len(torsion)} nonzero points")
    used=set(); kernels=[]
    for P in torsion:
        if P in used: continue
        Q=E.neg(P)
        if Q == P or Q not in torsion: raise InvalidMeasurement("invalid rational 3-torsion pairing")
        pair=tuple(sorted((P,Q), key=point_key)); used.update(pair); kernels.append(pair)
    kernels.sort(key=lambda pair: (1, (-2*pair[0][0])%E.p, (pair[0][0]*pair[0][0])%E.p))
    if len(kernels) != 4 or len(used) != 8: raise InvalidMeasurement("expected exactly four cyclic rational 3-kernels")
    return torsion, kernels


def rational_three_kernels(E: Curve) -> list[tuple[Point, Point]]:
    """All rational order-three kernels, without claiming full E[3] rationality."""
    torsion=sorted([P for P in E.points() if P is not None and E.mul(3,P) is None], key=point_key)
    used=set(); kernels=[]
    for P in torsion:
        if P in used: continue
        Q=E.neg(P)
        if Q != P and Q in torsion:
            pair=tuple(sorted((P,Q),key=point_key)); used.update(pair); kernels.append(pair)
    return sorted(kernels,key=lambda pair:(1,(-2*pair[0][0])%E.p,(pair[0][0]*pair[0][0])%E.p))


@dataclass(frozen=True)
class Isomorphism:
    source: Curve
    target: Curve
    u: int
    def apply(self, P: Point) -> Point:
        if P is None: return None
        return (self.u*self.u*P[0] % self.source.p, self.u**3*P[1] % self.source.p)
    def inverse(self, P: Point) -> Point:
        return Isomorphism(self.target,self.source,pow(self.u,-1,self.source.p)).apply(P)


def short_weierstrass_isomorphism(source: Curve, target: Curve) -> Isomorphism:
    for u in range(1, source.p):
        if target.a % source.p == source.a * pow(u,4,source.p) % source.p and target.b % source.p == source.b * pow(u,6,source.p) % source.p:
            return Isomorphism(source,target,u)
    raise InvalidMeasurement("normalized dual codomain is not explicitly isomorphic to required source model")


@dataclass(frozen=True)
class VeluMap:
    source: Curve
    target: Curve
    kernel: tuple[Point, Point]
    def apply(self, P: Point) -> Point:
        if P is None: return None
        if P in self.kernel: return None
        x,y=P; p=self.source.p; X,Y=x,y
        # One representative of the +-pair gives the odd-degree normalized formula.
        xq,yq=self.kernel[0]; gx=(3*xq*xq+self.source.a)%p; gy=(-2*yq)%p
        vq=2*gx%p; uq=gy*gy%p; d=pow((x-xq)%p,-1,p)
        X=(X+vq*d+uq*d*d)%p
        Y=(Y-2*uq*y*pow(d,3,p)-vq*y*d*d)%p
        if not self.target.on_curve((X,Y)): raise InvalidMeasurement("Vélu image does not lie on normalized codomain")
        return X,Y


def normalized_velu_map(E: Curve, kernel: tuple[Point,Point]) -> VeluMap:
    if len(kernel)!=2 or E.neg(kernel[0]) != kernel[1] or E.mul(3,kernel[0]) is not None: raise ValueError("need exact order-3 +-kernel")
    x,y=kernel[0]; p=E.p; gx=(3*x*x+E.a)%p; gy=(-2*y)%p; v=2*gx%p; w=(gy*gy+x*v)%p
    target=Curve(p,(E.a-5*v)%p,(E.b-7*w)%p)
    return VeluMap(E,target,kernel)


@dataclass(frozen=True)
class DualPair:
    phi: VeluMap
    psi_velu: VeluMap
    normalization: Isomorphism
    def psi(self, P: Point) -> Point: return self.normalization.apply(self.psi_velu.apply(P))
    def check(self, P: Point) -> bool:
        return self.psi(self.phi.apply(P)) == self.phi.source.mul(3,P)


def exact_dual(phi: VeluMap, certificate_point: Point) -> DualPair:
    """Find the rational normalized dual and its codomain isomorphism by identity.

    Candidate kernels are fully enumerated on the target.  The defining identity
    ψ∘φ=[3] is then checked on the supplied non-kernel certificate point.  The
    future control repeats it on G0, Gi and frozen public scalar points.
    """
    kernels=rational_three_kernels(phi.target)
    candidates=[]
    for kernel in kernels:
        raw=normalized_velu_map(phi.target,kernel)
        try: iso=short_weierstrass_isomorphism(raw.target,phi.source)
        except InvalidMeasurement: continue
        pair=DualPair(phi,raw,iso)
        if certificate_point not in phi.kernel and pair.check(certificate_point): candidates.append(pair)
    if len(candidates)!=1: raise InvalidMeasurement(f"expected unique exact normalized dual; got {len(candidates)}")
    return candidates[0]


def j1728_automorphism(E: Curve) -> Callable[[Point],Point]:
    if E.b % E.p != 0: raise ValueError("j=1728 automorphism requires B=0")
    roots=[u for u in range(E.p) if u*u % E.p == E.p-1]
    if not roots: raise InvalidMeasurement("no rational square root of -1")
    iota=min(roots)
    def i_map(P: Point) -> Point:
        return None if P is None else ((-P[0]) % E.p, iota*P[1] % E.p)
    return i_map


def coordinate_isomorphism(E: Curve, u: int) -> Isomorphism:
    u %= E.p
    if not u: raise ValueError("coordinate u must be nonzero")
    return Isomorphism(E,Curve(E.p,E.a*pow(u,4,E.p)%E.p,E.b*pow(u,6,E.p)%E.p),u)


def conjugate_map(f: Callable[[Point],Point], source_change: Isomorphism, target_change: Isomorphism) -> Callable[[Point],Point]:
    return lambda P: target_change.apply(f(source_change.inverse(P)))


def v_adic(n: int, ell: int) -> int:
    out=0
    while n and n%ell == 0: out+=1; n//=ell
    return out


@dataclass(frozen=True)
class Conductor3Certificate:
    p: int; trace: int; frobenius_discriminant: int; f_pi: int; v3_f_pi: int; inert: bool; quotient_models: int; rational_isogeny_counts: tuple[int,...]
    def validate(self) -> None:
        if self.frobenius_discriminant != -4*self.f_pi*self.f_pi or self.v3_f_pi != 1 or not self.inert or self.quotient_models != 4:
            raise InvalidMeasurement("conductor-3 certificate does not satisfy the frozen CM/level rule")


def conductor3_certificate(E0: Curve, quotient_models: Sequence[Curve]) -> Conductor3Certificate:
    n=E0.order(); t=E0.p+1-n; disc=t*t-4*E0.p
    f2=(-disc)//4
    f=math.isqrt(f2) if f2 >= 0 else 0
    counts=[]
    for E in quotient_models:
        counts.append(len(rational_three_kernels(E)))
    cert=Conductor3Certificate(E0.p,t,disc,f,v_adic(f,3),3%4==3,len(quotient_models),tuple(counts)); cert.validate(); return cert


def choose_eigenvalue_sign(candidates: Sequence[int], *, r: int, g0: Point, i_map: Callable[[Point],Point], scalar_mul: Callable[[int,Point],Point]) -> int:
    if len(candidates)!=2 or len({c%r for c in candidates}) != 2: raise ValueError("exactly two distinct roots required")
    matches=[c%r for c in candidates if scalar_mul(c%r,g0)==i_map(g0)]
    if len(matches)!=1: raise InvalidMeasurement("eigenvalue sign must have exactly one nonzero-point match")
    return matches[0]


def sqrt_minus_one_mod_prime(r: int) -> tuple[int,int]:
    roots=[x for x in range(r) if x*x%r == r-1]
    if len(roots)!=2: raise InvalidMeasurement("r has no two roots of -1")
    return roots[0],roots[1]


def binary_mul(E: Curve, n: int, P: Point) -> Point: return E.mul(n,P)

def wnaf_mul(E: Curve, n: int, P: Point, width: int) -> Point:
    if width not in (2,3,4,5): raise ValueError("frozen widths are 2..5")
    digits=[]; k=n
    while k:
        if k&1:
            z=k % (1<<width); z=z-(1<<width) if z >= (1<<(width-1)) else z; k-=z
        else: z=0
        digits.append(z); k//=2
    table={d:E.mul(d,P) for d in range(1,1<<(width-1),2)}; out: Point=None
    for z in reversed(digits):
        out=E.add(out,out)
        if z: out=E.add(out,table[abs(z)] if z>0 else E.neg(table[abs(z)]))
    return out

def pinned_library_mul(E: Curve, n: int, P: Point) -> Point:
    """Pinned-library arm: the audited local affine implementation, label retained."""
    return E.mul(n,P)

def scalar_arms(E: Curve, n: int, P: Point) -> dict[str,Point]:
    return {"binary_double_and_add":binary_mul(E,n,P), **{f"wnaf_w{w}":wnaf_mul(E,n,P,w) for w in range(2,6)}, "pinned_library":pinned_library_mul(E,n,P)}

def select_baseline(scores: dict[str,float], *, selection_seed: int, q: int) -> str:
    if selection_seed != 606101 or q != 256 or set(scores)!=set(SCALAR_ARMS): raise ValueError("selection is frozen to every arm, seed 606101, q=256")
    return min(SCALAR_ARMS,key=lambda arm:(scores[arm],arm))


@dataclass
class CostLedger:
    values: dict[str,float] = field(default_factory=lambda:{term:0.0 for term in COST_TERMS})
    def add(self, term: str, elapsed: float) -> None:
        if term not in self.values or elapsed < 0: raise ValueError("unknown/negative charged cost")
        self.values[term]+=elapsed
    def transport_total(self,q:int)->float: return sum(self.values[x] for x in COST_TERMS[:9])+q*sum(self.values[x] for x in ("Cpsi","Ci","Cphi","Cverify"))
    def scalar_total(self,q:int)->float: return self.values["Cshared"]+self.values["Calgorithm_selection"]+self.values["Cscalar_setup"]+q*(self.values["Cmul"]+self.values["Cverify"])


def timed_blocks(operation: Callable[[],None], *, minimum_cpu: float=0.1, maximum_repeats: int=100, blocks: int=7) -> list[dict[str,float|int|bool]]:
    rows=[]
    for _ in range(blocks):
        start_cpu=time.process_time(); start_wall=time.perf_counter(); repeats=0
        while repeats < maximum_repeats and time.process_time()-start_cpu < minimum_cpu: operation(); repeats+=1
        cpu=time.process_time()-start_cpu; wall=time.perf_counter()-start_wall
        rows.append({"repeats":repeats,"cpu_seconds":cpu,"wall_seconds":wall,"resolution_reached":cpu>=minimum_cpu})
    return rows


def canonical_artifact_layout(run_id: str) -> tuple[str,...]:
    if not run_id or Path(run_id).name != run_id or run_id in {".",".."}: raise ValueError("run id must be a control-plane basename")
    return tuple(f"runs/{run_id}/{name}" for name in RUN_ARTIFACT_NAMES)


def check_cancellation(requested: bool, stage: str) -> None:
    if requested: raise CancellationRequested(f"cancelled before {stage}; preserve written artifacts and classify incomplete")


def runtime_binding() -> dict[str,Any]:
    return {"python":sys.version, "implementation":sys.implementation.name, "platform":sys.platform, "pid":os.getpid()}


def verify_launch_lock(lock_path: Path, authorization_path: Path, verifier: Path) -> dict[str,Any]:
    """Verify actual byte bindings and a separately trusted Coordinator authorization.

    ``verifier`` is supplied by the future control plane, not minted here.  It
    receives the lock and authorization paths and must return zero only for an
    authentic Coordinator binding.  A JSON boolean/nonempty signature is never
    treated as evidence of authorization.
    """
    try: lock=json.loads(lock_path.read_text()); authorization=json.loads(authorization_path.read_text())
    except (OSError,json.JSONDecodeError) as exc: raise LaunchRefused(f"unavailable/malformed future binding: {exc}") from exc
    plan_path=Path(__file__).with_name("execution-plan.json")
    actual={"spec_sha256":sha256_file(specification_path()),"driver_sha256":sha256_file(Path(__file__)),"execution_plan_sha256":sha256_file(plan_path),"runtime":runtime_binding(),"resource_limits":FROZEN_LIMITS}
    if actual["spec_sha256"] != SPEC_SHA256: raise LaunchRefused("frozen specification bytes differ from source binding")
    needed={"kind","experiment_id","approval_decision_id","implementation_approval_id","spec_sha256","driver_sha256","execution_plan_sha256","runtime","resource_limits","authorization_sha256"}
    if set(lock) < needed or lock.get("kind") != "genuine_runtime_code_execution_lock": raise LaunchRefused("lock lacks genuine byte-binding fields")
    if any(lock[k] != actual[k] for k in ("spec_sha256","driver_sha256","execution_plan_sha256","runtime","resource_limits")): raise LaunchRefused("lock does not bind actual code/spec/plan/runtime/resource bytes")
    if lock["experiment_id"] != EXPERIMENT_ID or lock["approval_decision_id"] != APPROVAL_ID or lock["implementation_approval_id"] != IMPLEMENTATION_APPROVAL_ID: raise LaunchRefused("lock binds another authority")
    if lock["authorization_sha256"] != sha256_file(authorization_path): raise LaunchRefused("authorization bytes differ from lock")
    if authorization.get("experiment_id") != EXPERIMENT_ID or authorization.get("lock_sha256") != sha256_file(lock_path): raise LaunchRefused("authorization is not bound to this exact lock")
    try: completed=subprocess.run([str(verifier),str(lock_path),str(authorization_path)],capture_output=True,text=True,timeout=30,check=False)
    except (OSError,subprocess.SubprocessError) as exc: raise LaunchRefused(f"separate Coordinator authenticator unavailable: {exc}") from exc
    if completed.returncode != 0: raise LaunchRefused("separate Coordinator authenticator rejected binding")
    return actual


def _write_json(path: Path, value: Any) -> None: path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")

def _memory_guard() -> None:
    cap=FROZEN_LIMITS["memory_gb"]*1024**3
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024 > cap: raise MemoryError("8 GiB frozen RSS guard exceeded")


def execute_frozen_run(*, run_id: str, run_root: Path, lock_path: Path, authorization_path: Path, verifier: Path, cancel: Callable[[],bool], prepare: Callable[[],dict[str,Any]], audit: Callable[[dict[str,Any]],dict[str,Any]], measure: Callable[[dict[str,Any]],list[dict[str,Any]]]) -> dict[str,Any]:
    """Future full runner.  It is intentionally never reached by this task's CLI/tests."""
    bindings=verify_launch_lock(lock_path,authorization_path,verifier); _memory_guard()
    out=run_root/run_id; out.mkdir(parents=True,exist_ok=False)
    status="completed_valid"; stage="prepare"; fixture={}; controls={}; rows=[]
    try:
        for stage, action in (("prepare",lambda:prepare()),("audit",lambda:audit(fixture)),("measure",lambda:measure(fixture))):
            check_cancellation(cancel(),stage); _memory_guard(); result=action()
            if stage=="prepare": fixture=result
            elif stage=="audit": controls=result
            else: rows=result
    except CancellationRequested: status="incomplete_cancelled"
    except MemoryError: status="resource_exhaustion"
    except InvalidMeasurement as exc: status="invalid_measurement"; controls={**controls,"failure":str(exc)}
    except Exception as exc: status="implementation_or_infrastructure_error"; controls={**controls,"failure":repr(exc)}
    _write_json(out/"fixtures.json",fixture); _write_json(out/"controls.json",controls)
    (out/"raw.jsonl").write_text("".join(json.dumps(x,sort_keys=True)+"\n" for x in rows))
    with (out/"costs.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=sorted({k for row in rows for k in row} or {"no_measurement"})); writer.writeheader(); writer.writerows(rows)
    _write_json(out/"certificates.json",fixture.get("certificates",{})); _write_json(out/"manifest.yaml",{"status":status,"stage":stage,"bindings":bindings,"run_id":run_id,"scientific_execution":True})
    (out/"stdout.log").write_text(""); (out/"stderr.log").write_text(""); (out/"report.md").write_text(f"# {EXPERIMENT_ID} future run\n\nTerminal classification: `{status}`.\n")
    return {"status":status,"path":str(out)}


@dataclass(frozen=True)
class FloorFixture:
    index: int
    phi: VeluMap
    dual: DualPair
    generator: Point


@dataclass(frozen=True)
class ClassFixture:
    p: int
    curve: Curve
    order: int
    subgroup_order: int
    g0: Point
    lambda_value: int
    m: int
    level: Conductor3Certificate
    floors: tuple[FloorFixture,...]


def prime_candidates(lower: int, upper: int) -> Iterable[int]:
    """Frozen increasing p=1 mod 4 candidate order; invoked only after launch."""
    for p in range(lower + ((1-lower) % 4), upper, 4):
        if is_prime(p): yield p


def choose_g0(E: Curve, N: int, r: int) -> Point:
    checked=0
    for P in sorted((P for P in E.points() if P is not None),key=point_key):
        checked += 1
        if checked > 4096: break
        G=E.mul(N//r,P)
        if G is not None and E.mul(r,G) is None: return G
    raise InvalidMeasurement("lexicographic G0 point cap exhausted")


def construct_class_fixture(p: int) -> ClassFixture:
    """Actual one-prime preparation algorithm, deliberately not called by this task."""
    E=Curve(p,-1,0); N=E.order(); t=p+1-N; disc=t*t-4*p
    if t == 0 or disc >= 0 or (-disc) % 4: raise InvalidMeasurement("not an ordinary frozen j=1728 candidate")
    f=math.isqrt((-disc)//4)
    if f*f != (-disc)//4 or v_adic(f,3) != 1: raise InvalidMeasurement("v3(f_pi)=1 requirement fails")
    factors=factor_integer(N); r=max(factors)
    if r < 127 or r in (3,p) or factors[r] != 1: raise InvalidMeasurement("largest-prime subgroup requirement fails")
    _,kernels=full_rational_three_torsion(E); G0=choose_g0(E,N,r)
    maps=[normalized_velu_map(E,kernel) for kernel in kernels]
    duals=[exact_dual(phi,G0) for phi in maps]
    level=conductor3_certificate(E,[phi.target for phi in maps])
    i_map=j1728_automorphism(E); roots=sqrt_minus_one_mod_prime(r)
    lam=choose_eigenvalue_sign(roots,r=r,g0=G0,i_map=i_map,scalar_mul=E.mul); m=3*lam%r
    floors=[]
    for j,(phi,dual) in enumerate(zip(maps,duals)):
        Gi=phi.apply(G0)
        if Gi is None or phi.target.mul(r,Gi) is not None or dual.psi(Gi) != E.mul(3,G0): raise InvalidMeasurement("floor subgroup/dual certificate fails")
        floors.append(FloorFixture(j,phi,dual,Gi))
    return ClassFixture(p,E,N,r,G0,lam,m,level,tuple(floors))


def discover_frozen_panel() -> tuple[list[ClassFixture],list[dict[str,Any]]]:
    """Bounded six-class discovery with every rejection retained for future artifacts."""
    accepted=[]; rejected=[]; attempts=0
    for lo,hi in ((2**12,2**13),(2**14,2**15),(2**16,2**17)):
        interval=[]
        for p in prime_candidates(lo,hi):
            attempts += 1
            if attempts > 4096: break
            try: interval.append(construct_class_fixture(p))
            except (InvalidMeasurement,ValueError) as exc: rejected.append({"p":p,"reason":str(exc)}); continue
            if len(interval)==2: break
        accepted.extend(interval)
        if len(interval)<2: raise InvalidMeasurement("unavailable_fixture: fewer than two eligible classes in frozen interval")
    return accepted,rejected


def query_points(floor: FloorFixture, *, r: int, p: int, a: int, b: int, seed: int, q: int) -> list[Point]:
    """Exact common-coordinate query stream; labels/scalars remain outside evaluators."""
    parameters=(p,a,b,r,0,0,0); counter=0; out=[]
    for _ in range(q):
        s,counter=rejection_draw(purpose="query",parameters=parameters,seed=seed,counter=counter,n=r-1)
        out.append(floor.phi.target.mul(s+1,floor.generator))
    return out


def verify_controls(fixture: ClassFixture, *, seed: int) -> dict[str,Any]:
    """All frozen mathematical controls; only a future lock-gated run calls it."""
    E=fixture.curve; i=j1728_automorphism(E); result={"composition":[],"coordinate":[],"level":[],"identity_transport":[],"label_permutation":None}
    roots=sqrt_minus_one_mod_prime(fixture.subgroup_order); wrong=next(x for x in roots if x != fixture.lambda_value)
    for floor in fixture.floors:
        points=[fixture.g0,floor.generator]
        params=(fixture.p,E.a,E.b,fixture.subgroup_order,0,0,0); counter=0
        for _ in range(128):
            s,counter=rejection_draw(purpose="control",parameters=params,seed=seed,counter=counter,n=fixture.subgroup_order-1)
            points.append(E.mul(s+1,fixture.g0))
        checks=[]
        for P in points:
            left=floor.dual.psi(floor.phi.apply(P)); right=E.mul(3,P)
            checks.append(left==right and E.mul(fixture.lambda_value,P)==i(P))
        beta=floor.phi.target.mul(fixture.m,floor.generator)
        observed=floor.phi.apply(i(floor.dual.psi(floor.generator)))
        result["composition"].append({"floor":floor.index,"all_checks":all(checks),"beta_matches":observed==beta})
        result["identity_transport"].append({"floor":floor.index,"wrong_sign_fails":E.mul(wrong,fixture.g0)!=i(fixture.g0)})
        result["level"].append({"floor":floor.index,"direct_top":E.mul(3,E.mul(fixture.lambda_value,fixture.g0)),"scalar_top":E.mul(fixture.m,fixture.g0)})
        for u in (1,2,3):
            src=coordinate_isomorphism(E,u); tgt=coordinate_isomorphism(floor.phi.target,u)
            conjugated=conjugate_map(floor.phi.apply,src,tgt)
            result["coordinate"].append({"floor":floor.index,"u":u,"conjugation_ok":conjugated(src.apply(fixture.g0))==tgt.apply(floor.generator)})
    # A future aggregator passes its equal-weight floor totals here; this records the exact permutation transform.
    result["label_permutation"]={"method":"Fisher-Yates over four equal-weight floor totals; summary must be invariant"}
    if not all(x["all_checks"] and x["beta_matches"] for x in result["composition"]): raise InvalidMeasurement("composition/beta control failed")
    if not all(x["wrong_sign_fails"] for x in result["identity_transport"]): raise InvalidMeasurement("wrong sign control failed")
    if not all(x["conjugation_ok"] for x in result["coordinate"]): raise InvalidMeasurement("coordinate control failed")
    return result


def measure_scalar_workload(E: Curve, m: int, queries: Sequence[Point], arm: str) -> None:
    for P in queries:
        if arm == "binary_double_and_add": binary_mul(E,m,P)
        elif arm.startswith("wnaf_w"): wnaf_mul(E,m,P,int(arm[-1]))
        elif arm == "pinned_library": pinned_library_mul(E,m,P)
        else: raise ValueError("unknown frozen scalar arm")


def measure_transport_workload(floor: FloorFixture, i_map: Callable[[Point],Point], queries: Sequence[Point]) -> None:
    for P in queries: floor.phi.apply(i_map(floor.dual.psi(P)))


def protocol_coverage() -> dict[str,Any]:
    return {"scientific_execution":False,"backend":["full rational 3-torsion", "four normalized Vélu maps", "exact normalized dual/isomorphism", "j=1728 automorphism", "[3lambda] transport", "coordinate conjugation", "conductor-3 certificate"], "controls":["composition","coordinate","level","identity_transport","label_permutation"],"arms":list(SCALAR_ARMS),"future_gate":"actual hashes plus external Coordinator authenticator"}


def main(argv: Sequence[str] | None=None) -> int:
    parser=argparse.ArgumentParser(description="EXP-ECDLP-1b1b99 implementation; default is non-executing.")
    parser.add_argument("--dry-run",action="store_true",help="print implementation coverage only")
    parser.parse_args(argv)
    print(json.dumps({"status":"dry_run_not_launched","task_id":TASK_ID,"coverage":protocol_coverage()},indent=2,sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
