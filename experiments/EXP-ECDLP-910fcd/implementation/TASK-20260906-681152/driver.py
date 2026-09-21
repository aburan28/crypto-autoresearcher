#!/usr/bin/env python3
"""Non-launching implementation adapter for EXP-ECDLP-910fcd.

This partial module contains arithmetic and deterministic-construction pieces
of the frozen Tate-character protocol. Its CLI does not invoke fixture
enumeration, T search, pairing evaluation, controls, timing, or persistence.
Irreducibility currently exposes certificate metadata only; witness generation
and remaining orchestration belong to a successor implementation task.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

TASK_ID = "TASK-20260906-681152"
EXPERIMENT_ID = "EXP-ECDLP-910fcd"
APPROVAL_ID = "DEC-20260906-f73475"
SPEC_SHA256 = "75148fa8dc182d14f0894b3e525418c72fc939338b6a60d2c07cd2fc9df32555"
POLYNOMIAL_CAP = 4096
T_ATTEMPT_CAP = 128
QUERY_COUNTS = (1, 64)
RNG_PURPOSES = {"query", "control", "field_x", "target", "shuffle"}
RUN_ARTIFACT_NAMES = ("manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv", "certificates.json", "stdout.log", "stderr.log", "report.md")
# Frozen source-documented independent calibration.  It is data only here:
# this implementation task must not evaluate the pairing or treat it as a selected cell.
CALIBRATION_FIXTURE = {"p": 103, "A": 1, "B": 18, "G": (33, 91), "r": 19, "k": 6}


class LaunchRefused(RuntimeError):
    """Raised before any future experiment path when the real lock is absent."""


class SearchExhausted(RuntimeError):
    """Bounded preparation exhausted without a valid candidate."""


class NoSolution(RuntimeError):
    """The explicit BSGS bounds contain no verified solution."""


class PairingPole(ValueError):
    """A Miller divisor evaluation hit a pole; caller must record/reject it."""


@dataclass(frozen=True)
class PolynomialField:
    """Polynomial-basis F_p^k, coefficients constant-first modulo monic x^k+modulus.

    The caller supplies the selected, certified irreducible modulus as its k
    lower coefficients.  Elements are immutable tuples and are therefore safe
    BSGS table keys.
    """
    p: int
    modulus: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.p < 2 or len(self.modulus) < 1 or self.modulus[0] % self.p == 0:
            raise ValueError("field requires p>=2 and irreducible monic modulus with nonzero constant")
        object.__setattr__(self, "modulus", tuple(c % self.p for c in self.modulus))

    @property
    def k(self) -> int: return len(self.modulus)
    @property
    def zero(self) -> tuple[int, ...]: return (0,) * self.k
    @property
    def one(self) -> tuple[int, ...]: return (1,) + (0,) * (self.k - 1)
    def element(self, coefficients: Sequence[int] | int) -> tuple[int, ...]:
        if isinstance(coefficients, int): coefficients = (coefficients,)
        if len(coefficients) > self.k: raise ValueError("unreduced element input")
        return tuple(coefficients[i] % self.p if i < len(coefficients) else 0 for i in range(self.k))
    def add(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]: return tuple((x+y) % self.p for x,y in zip(a,b))
    def neg(self, a: tuple[int, ...]) -> tuple[int, ...]: return tuple((-x) % self.p for x in a)
    def sub(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]: return self.add(a, self.neg(b))
    def mul(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
        work = [0] * (2*self.k-1)
        for i,x in enumerate(a):
            for j,y in enumerate(b): work[i+j] = (work[i+j] + x*y) % self.p
        for degree in range(2*self.k-2, self.k-1, -1):
            c = work[degree]
            if c:
                for j,m in enumerate(self.modulus): work[degree-self.k+j] = (work[degree-self.k+j] - c*m) % self.p
        return tuple(work[:self.k])
    def pow(self, a: tuple[int, ...], exponent: int) -> tuple[int, ...]:
        if exponent < 0: return self.pow(self.inv(a), -exponent)
        out, base = self.one, a
        while exponent:
            if exponent & 1: out = self.mul(out, base)
            base = self.mul(base, base); exponent >>= 1
        return out
    def inv(self, a: tuple[int, ...]) -> tuple[int, ...]:
        if a == self.zero: raise PairingPole("zero denominator in finite field")
        return self.pow(a, self.p**self.k-2)
    def div(self, a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]: return self.mul(a, self.inv(b))


Point = tuple[tuple[int, ...], tuple[int, ...]] | None


@dataclass(frozen=True)
class ShortWeierstrassCurve:
    field: PolynomialField
    A: tuple[int, ...]
    B: tuple[int, ...]
    def __post_init__(self) -> None:
        object.__setattr__(self, "A", self.field.element(self.A)); object.__setattr__(self, "B", self.field.element(self.B))
        if self.field.add(self.field.mul(self.field.element(4), self.field.mul(self.field.mul(self.A,self.A),self.A)), self.field.mul(self.field.element(27), self.field.mul(self.B,self.B))) == self.field.zero: raise ValueError("singular short-Weierstrass curve")
    def is_on_curve(self, P: Point) -> bool:
        if P is None: return True
        x,y=P; return self.field.mul(y,y) == self.field.add(self.field.add(self.field.mul(self.field.mul(x,x),x), self.field.mul(self.A,x)),self.B)
    def neg(self, P: Point) -> Point: return None if P is None else (P[0], self.field.neg(P[1]))
    def add(self, P: Point, Q: Point) -> Point:
        if P is None: return Q
        if Q is None: return P
        f=self.field; x1,y1=P; x2,y2=Q
        if x1 == x2 and f.add(y1,y2) == f.zero: return None
        if P == Q:
            if y1 == f.zero: return None
            slope=f.div(f.add(f.mul(f.element(3),f.mul(x1,x1)),self.A), f.mul(f.element(2),y1))
        else: slope=f.div(f.sub(y2,y1),f.sub(x2,x1))
        x3=f.sub(f.sub(f.mul(slope,slope),x1),x2); y3=f.sub(f.mul(slope,f.sub(x1,x3)),y1)
        return (x3,y3)
    def scalar_mul(self, n: int, P: Point) -> Point:
        if n < 0: return self.scalar_mul(-n,self.neg(P))
        out=None
        while n:
            if n&1: out=self.add(out,P)
            P=self.add(P,P); n >>= 1
        return out


def _line_over_vertical(curve: ShortWeierstrassCurve, P: Point, Q: Point, R: Point) -> tuple[int, ...]:
    """g_{P,Q}(R)=ell_{P,Q}(R)/v_{P+Q}(R), with poles reported explicitly."""
    if P is None or Q is None: return curve.field.one
    if R is None: raise PairingPole("Miller evaluation at infinity is unsupported")
    f=curve.field; x1,y1=P; x2,y2=Q; x,y=R
    if x1 == x2 and f.add(y1,y2) == f.zero: return f.sub(x,x1)
    if P == Q:
        if y1 == f.zero: return f.sub(x,x1)
        slope=f.div(f.add(f.mul(f.element(3),f.mul(x1,x1)),curve.A),f.mul(f.element(2),y1))
    else: slope=f.div(f.sub(y2,y1),f.sub(x2,x1))
    numerator=f.sub(f.sub(y,y1),f.mul(slope,f.sub(x,x1))); S=curve.add(P,Q)
    return numerator if S is None else f.div(numerator,f.sub(x,S[0]))


def miller_function_at(*, curve: ShortWeierstrassCurve, r: int, P: Point, R: Point) -> tuple[int, ...]:
    """Binary Miller f_(r,P)(R), without a hidden pairing/discrete-log routine."""
    if r < 1 or not curve.is_on_curve(P) or not curve.is_on_curve(R): raise ValueError("invalid Miller input")
    bits=bin(r)[3:]; V=P; value=curve.field.one
    for bit in bits:
        value=curve.field.mul(curve.field.mul(value,value),_line_over_vertical(curve,V,V,R)); V=curve.add(V,V)
        if bit == "1": value=curve.field.mul(value,_line_over_vertical(curve,V,P,R)); V=curve.add(V,P)
    return value


def shifted_divisor_miller(*, curve: ShortWeierstrassCurve, r: int, P: Point, T: Point, shift: Point) -> tuple[int, ...]:
    """Evaluate f_(r,P)((T+S)-(S)); both supports are explicit and poles reject."""
    shifted=curve.add(T,shift)
    return curve.field.div(miller_function_at(curve=curve,r=r,P=P,R=shifted), miller_function_at(curve=curve,r=r,P=P,R=shift))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def stream_digest(*, purpose: str, parameters: Sequence[int], seed: int, counter: int) -> int:
    """The frozen SHA-256 source; parameters are [p,A,B,r,k,u,arm]."""
    if purpose not in RNG_PURPOSES or len(parameters) != 7:
        raise ValueError("invalid frozen RNG purpose or parameter tuple")
    if seed < 0 or counter < 0 or any(not isinstance(v, int) for v in parameters):
        raise ValueError("RNG tuple, seed, and counter must be nonnegative integers")
    payload = [EXPERIMENT_ID, purpose, list(parameters), seed, counter]
    return int.from_bytes(hashlib.sha256(canonical_json(payload)).digest(), "big")


def rejection_draw(*, purpose: str, parameters: Sequence[int], seed: int, counter: int, n: int) -> tuple[int, int]:
    if n < 1 or n > (1 << 256):
        raise ValueError("draw modulus must be in [1,2^256]")
    limit = ((1 << 256) // n) * n
    while True:
        digest = stream_digest(purpose=purpose, parameters=parameters, seed=seed, counter=counter)
        counter += 1
        if digest < limit:
            return digest % n, counter


def fisher_yates(values: Iterable[Any], *, parameters: Sequence[int], seed: int, counter: int) -> tuple[list[Any], int]:
    out = list(values)
    for i in range(len(out) - 1, 0, -1):
        j, counter = rejection_draw(purpose="shuffle", parameters=parameters, seed=seed, counter=counter, n=i + 1)
        out[i], out[j] = out[j], out[i]
    return out, counter


def polynomial_coefficients(index: int, *, p: int, k: int) -> tuple[int, ...]:
    """Decode I=sum(a_j p^j), constant coefficient first, without field work."""
    if p < 2 or k < 1 or index < 0 or index >= p**k:
        raise ValueError("polynomial index outside degree-k base-p range")
    out: list[int] = []
    for _ in range(k):
        out.append(index % p)
        index //= p
    return tuple(out)


def bounded_monic_polynomials(*, p: int, k: int, cap: int = POLYNOMIAL_CAP) -> Iterable[tuple[int, tuple[int, ...]]]:
    """Frozen increasing-I search, skipping a0=0 without charging a trial."""
    if cap < 1:
        raise ValueError("polynomial cap must be positive")
    tried = 0
    for index in range(p**k):
        coefficients = polynomial_coefficients(index, p=p, k=k)
        if coefficients[0] == 0:
            continue
        yield index, coefficients
        tried += 1
        if tried == cap:
            return


def select_irreducible_polynomial(*, p: int, k: int, is_irreducible: Callable[[tuple[int, ...]], bool], cap: int = POLYNOMIAL_CAP) -> tuple[int, tuple[int, ...], list[int]]:
    """Bounded selection; caller archives the returned tested-I sequence/certificate."""
    tested: list[int] = []
    for index, coefficients in bounded_monic_polynomials(p=p, k=k, cap=cap):
        tested.append(index)
        if is_irreducible(coefficients):
            return index, coefficients, tested
    raise SearchExhausted(f"no irreducible polynomial in at most {cap} nonzero-constant trials")


def is_prime(n: int) -> bool:
    if n < 2: return False
    if n % 2 == 0: return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0: return False
        d += 2
    return True


def factor_integer(n: int) -> list[tuple[int, int]]:
    """Deterministic trial factorization for the frozen toy panel; no timing selection."""
    out=[]; d=2
    while d*d <= n:
        e=0
        while n%d == 0: n//=d; e+=1
        if e: out.append((d,e))
        d=3 if d==2 else d+2
    return out + ([(n,1)] if n>1 else [])


def multiplicative_order_mod(a: int, r: int) -> int:
    if math.gcd(a,r) != 1: raise ValueError("embedding order requires gcd(p,r)=1")
    order=r-1
    for q,_ in factor_integer(order):
        while order%q == 0 and pow(a,order//q,r)==1: order//=q
    return order


def irreducibility_certificate(*, p: int, coefficients: tuple[int, ...]) -> dict[str, Any]:
    """Return a deterministic certificate request record for the selected polynomial.

    The actual Rabin/Frobenius witness is intentionally exposed as data so a
    reviewed runner can persist every power/gcd, rather than relying on a
    library boolean with no certificate.
    """
    k=len(coefficients)
    if not is_prime(p) or k < 1 or coefficients[0] % p == 0: raise ValueError("invalid monic irreducibility input")
    return {"method":"rabin_frobenius", "p":p, "degree":k, "lower_coefficients":list(coefficients), "prime_divisors_degree":[q for q,_ in factor_integer(k)], "required_equalities":["x^(p^k)=x mod f"] + [f"gcd(x^(p^{k//q})-x,f)=1 for q={q}" for q,_ in factor_integer(k)]}


def first_primes_from(start: int, count: int = 32) -> list[int]:
    out=[]; n=max(2,start)
    while len(out)<count:
        if is_prime(n): out.append(n)
        n+=1
    return out


def fixture_bin(k: int) -> str | None:
    return "1" if k==1 else "2" if k==2 else "3_6" if 3<=k<=6 else "7_12" if 7<=k<=12 else None


def deterministic_fixture_candidates(*, b: int, point_count: Callable[[int,int], int], supersingular: Callable[[int,int], bool]) -> Iterable[dict[str, Any]]:
    """Frozen p/B/r ordering only; caller persists every accepted/rejected record."""
    for p in first_primes_from(1<<b):
        for B in range(16):
            discriminant=(4 + 27*B*B) % p  # A=1, hence 4*A^3+27*B^2
            if discriminant == 0 or supersingular(p,B): continue
            N=point_count(p,B)
            for r,e in sorted(factor_integer(N), reverse=True):
                if 17<=r<=251 and r!=p and e==1:
                    k=multiplicative_order_mod(p,r); yield {"p":p,"A":1,"B":B,"N":N,"r":r,"k":k,"bin":fixture_bin(k)}


def legendre_symbol(a: int, p: int) -> int:
    a %= p
    return 0 if a == 0 else (-1 if pow(a,(p-1)//2,p) == p-1 else 1)


def sqrt_fp(a: int, p: int) -> int | None:
    """Deterministic Tonelli-Shanks, returning the smaller integer root."""
    a %= p
    if a == 0: return 0
    if legendre_symbol(a,p) != 1: return None
    if p % 4 == 3: return min(pow(a,(p+1)//4,p), (-pow(a,(p+1)//4,p))%p)
    q,s=p-1,0
    while q%2==0: q//=2; s+=1
    z=2
    while legendre_symbol(z,p) != -1: z+=1
    m,c,t,x=s,pow(z,q,p),pow(a,q,p),pow(a,(q+1)//2,p)
    while t != 1:
        i=1; u=t*t%p
        while u != 1: u=u*u%p; i+=1
        b=pow(c,1<<(m-i-1),p); x=x*b%p; t=t*b*b%p; c=b*b%p; m=i
    return min(x,(-x)%p)


def count_short_weierstrass_points(p: int, B: int) -> int:
    """Exact deterministic #E(F_p) for the frozen toy range, including infinity."""
    if not is_prime(p): raise ValueError("point count requires prime p")
    return 1 + sum(1 + legendre_symbol((x*x*x + x + B) % p,p) for x in range(p))


def first_subgroup_generator(*, p: int, B: int, N: int, r: int) -> tuple[int,int]:
    """Frozen x/root ordering and [N/r] projection; raises rather than selecting by runtime."""
    # Integer affine law keeps base-field construction independent of a selected extension modulus.
    def add(P, Q):
        if P is None: return Q
        if Q is None: return P
        x1,y1=P; x2,y2=Q
        if x1==x2 and (y1+y2)%p==0: return None
        lam=((3*x1*x1+1)*pow(2*y1,-1,p) if P==Q else (y2-y1)*pow((x2-x1)%p,-1,p))%p
        x3=(lam*lam-x1-x2)%p; return (x3,(lam*(x1-x3)-y1)%p)
    def mul(n,P):
        out=None
        while n:
            if n&1: out=add(out,P)
            P=add(P,P); n>>=1
        return out
    for x in range(min(p,4096)):
        y=sqrt_fp(x*x*x+x+B,p)
        if y is None: continue
        for yy in sorted({y,(-y)%p}):
            G=mul(N//r,(x,yy))
            if G is not None and mul(r,G) is None: return G
    raise SearchExhausted("generator scan exhausted prescribed x/root ordering")


def select_second_argument(*, candidates: Iterable[Any], evaluate: Callable[[Any], Any], power: Callable[[Any, int], Any], one: Any, r: int, cap: int = T_ATTEMPT_CAP) -> tuple[Any, Any, list[dict[str, Any]]]:
    """Take the first defined nontrivial reduced-Tate value, retaining every attempt."""
    if cap < 1:
        raise ValueError("T-attempt cap must be positive")
    attempts: list[dict[str, Any]] = []
    for ordinal, candidate in enumerate(candidates):
        if ordinal >= cap:
            break
        try:
            value = evaluate(candidate)
            accepted = power(value, r) == one and value != one
            attempts.append({"ordinal": ordinal, "status": "accepted" if accepted else "rejected_nonprimitive"})
            if accepted:
                return candidate, value, attempts
        except Exception as exc:  # Future runner records an exceptional divisor, never substitutes zero.
            attempts.append({"ordinal": ordinal, "status": "rejected_exception", "exception_type": type(exc).__name__})
    raise SearchExhausted(f"no acceptable T in at most {cap} generated candidates")


def reduced_tate(*, miller_value: Any, p: int, k: int, r: int, power: Callable[[Any, int], Any]) -> tuple[Any, int]:
    """Apply the mandatory final exponent (p^k-1)/r to a non-reduced Miller value."""
    if p < 2 or k < 1 or r < 2 or (pow(p, k) - 1) % r:
        raise ValueError("invalid reduced-Tate parameters: r must divide p^k-1")
    exponent = (pow(p, k) - 1) // r
    return power(miller_value, exponent), exponent


def public_reduced_tate(*, P: Any, T: Any, p: int, k: int, r: int, miller_evaluate: Callable[[int, Any, Any], Any], power: Callable[[Any, int], Any]) -> tuple[Any, int]:
    """Public Tate interface: evaluate f_(r,P) on its documented divisor, then reduce it.

    ``miller_evaluate`` is deliberately explicit so the future backend must expose
    shifted-divisor/pole handling rather than making an undocumented library call.
    """
    return reduced_tate(miller_value=miller_evaluate(r, P, T), p=p, k=k, r=r, power=power)


def multiplicative_bsgs(*, base: Any, target: Any, order: int, one: Any, multiply: Callable[[Any, Any], Any], inverse: Callable[[Any], Any], power: Callable[[Any, int], Any], verify: Callable[[int], bool]) -> int:
    """Explicit bounded BSGS: baby exponents 0..m-1 and giant steps 0..m."""
    if order < 2:
        raise ValueError("BSGS order must be at least two")
    m = math.isqrt(order - 1) + 1
    babies: dict[Any, int] = {}
    value = one
    for j in range(m):
        babies.setdefault(value, j)
        value = multiply(value, base)
    factor = inverse(power(base, m))
    giant = target
    for i in range(m + 1):
        j = babies.get(giant)
        if j is not None:
            candidate = i * m + j
            if candidate < order and verify(candidate):
                return candidate
        giant = multiply(giant, factor)
    raise NoSolution("no multiplicative BSGS solution within declared order")


def additive_bsgs(*, base: Any, target: Any, order: int, identity: Any, add: Callable[[Any, Any], Any], negate: Callable[[Any], Any], scalar_mul: Callable[[int, Any], Any], verify: Callable[[int], bool]) -> int:
    if order < 2:
        raise ValueError("BSGS order must be at least two")
    m = math.isqrt(order - 1) + 1
    babies: dict[Any, int] = {}
    point = identity
    for j in range(m):
        babies.setdefault(point, j)
        point = add(point, base)
    step = negate(scalar_mul(m, base))
    giant = target
    for i in range(m + 1):
        j = babies.get(giant)
        if j is not None:
            candidate = i * m + j
            if candidate < order and verify(candidate):
                return candidate
        giant = add(giant, step)
    raise NoSolution("no additive BSGS solution within declared order")


@dataclass(frozen=True)
class PublicTarget:
    """Producer-facing input: deliberately contains Q but never its scalar label."""
    target_id: int
    Q: Any


def evaluator_decode(target: PublicTarget, *, G: Any, r: int, add: Callable[[Any, Any], Any], negate: Callable[[Any], Any], scalar_mul: Callable[[int, Any], Any], identity: Any) -> int:
    return additive_bsgs(base=G, target=target.Q, order=r, identity=identity, add=add, negate=negate, scalar_mul=scalar_mul, verify=lambda a: scalar_mul(a, G) == target.Q)


@dataclass(frozen=True)
class CostLedger:
    """The frozen model preserves the character-only setup and every shared cost."""
    shared: float
    field: float
    search_t: float
    chi_g: float
    field_table: float
    chi_q: float
    field_giant_steps: float
    curve_table: float
    curve_giant_steps: float
    curve_verify: float

    def character_total(self, q: int) -> float:
        return self.shared + self.field + self.search_t + self.chi_g + self.field_table + q * (self.chi_q + self.field_giant_steps + self.curve_verify)

    def curve_total(self, q: int) -> float:
        return self.shared + self.curve_table + q * (self.curve_giant_steps + self.curve_verify)


def canonical_artifact_layout(run_id: str) -> tuple[str, ...]:
    if not run_id or "/" in run_id or "\\" in run_id or run_id in {".", ".."}:
        raise ValueError("run_id must be a nonempty control-plane allocated basename")
    return tuple(f"runs/{run_id}/{name}" for name in RUN_ARTIFACT_NAMES)


def prospective_stage_manifest(*, run_id: str, stage: str, source_sha256: str, driver_sha256: str) -> dict[str, Any]:
    """Construct, but never write, the future stage manifest bound to canonical paths."""
    if stage not in {"prepare", "audit_measure", "report"}: raise ValueError("unknown frozen stage")
    return {"status":"not_launched", "run_id":run_id, "stage":stage, "experiment_id":EXPERIMENT_ID, "spec_sha256":source_sha256, "driver_sha256":driver_sha256, "artifacts":list(canonical_artifact_layout(run_id)), "cancellation":"persist completed prior-stage artifacts and mark incomplete"}


def write_future_artifact(*, launch_lock: Path, destination: Path, payload: bytes) -> None:
    """Fail closed: this task has no genuine lock verifier and never writes run artifacts."""
    require_launch_lock(launch_lock)
    root = Path("runs").resolve()
    resolved = destination.resolve()
    if root not in resolved.parents or resolved.name not in RUN_ARTIFACT_NAMES:
        raise LaunchRefused("future artifact path is outside the canonical run layout")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".partial")
    temporary.write_bytes(payload)
    temporary.replace(destination)


def control_definitions() -> dict[str, str]:
    return {"exact_character":"exhaustive verifier-only a=0..r-1 identities", "null_and_injection":"trivial character ambiguous; injected label access must fail audit; flipped value fails exact check", "base_field_isotropy":"k>1 base-field T=G trivial; extension T nontrivial first", "coordinates":"u=2 transport preserves decoded scalar", "full_decoder":"bounded field and curve BSGS with final curve verification"}


def require_launch_lock(path: Path) -> None:
    """Parse a prospective lock shape, then fail closed because no verifier exists."""
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LaunchRefused(f"genuine future launch lock unavailable or malformed: {exc}") from exc
    required = {"kind", "approved", "experiment_id", "approval_decision_id", "spec_sha256", "driver_sha256", "execution_plan_sha256", "runtime", "resource_limits", "signature", "runtime_verified", "code_verified"}
    if required - set(lock) or lock.get("kind") != "genuine_runtime_code_execution_lock" or lock.get("approved") is not True:
        raise LaunchRefused("lock does not have the required genuine-lock shape")
    if (lock.get("experiment_id"), lock.get("approval_decision_id"), lock.get("spec_sha256")) != (EXPERIMENT_ID, APPROVAL_ID, SPEC_SHA256):
        raise LaunchRefused("lock binds a different frozen protocol")
    if lock.get("runtime_verified") is not True or lock.get("code_verified") is not True:
        raise LaunchRefused("lock has unresolved runtime/code verification")
    if not all(isinstance(lock.get(k), str) and lock[k] for k in ("driver_sha256", "execution_plan_sha256", "runtime", "signature")):
        raise LaunchRefused("lock has unresolved content bindings")
    raise LaunchRefused("genuine content/runtime/signature verifier not implemented")


def protocol_coverage() -> dict[str, Any]:
    return {"field": "bounded_monic_polynomials and select_irreducible_polynomial preserve increasing-I, a0!=0, and cap=4096", "T": "select_second_argument retains rejected/exceptional attempts and cap=128", "pairing": "public_reduced_tate calls the explicit Miller/divisor interface; reduced_tate mandates final exponent (p^k-1)/r", "decoder": "multiplicative_bsgs and additive_bsgs use explicit m=ceil(sqrt(r)), bounded baby/giant tables, collision and curve verification", "isolation": "PublicTarget has no scalar label; evaluator_decode consumes only Q and public group data", "control_fixture": CALIBRATION_FIXTURE, "controls": ["exact_character", "null_and_injection", "base_field_isotropy", "coordinates", "full_decoder"], "future_run": "no launch implementation; a genuine verified lock and review remain required"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run adapter for EXP-ECDLP-910fcd; performs no measurement.")
    parser.add_argument("--dry-run", action="store_true", help="print the protocol-to-code coverage (default)")
    parser.add_argument("--launch-lock", type=Path, help="validate a future lock, then refuse to launch")
    args = parser.parse_args(argv)
    if args.launch_lock is not None:
        require_launch_lock(args.launch_lock)
        raise LaunchRefused("lock validation does not launch this adapter; reviewed runner required")
    print(json.dumps({"status": "dry_run_not_launched", "task_id": TASK_ID, "experiment_id": EXPERIMENT_ID, "coverage": protocol_coverage()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
