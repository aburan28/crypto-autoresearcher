# Pure Mathematical Core API V6

## Status and scope

Status: `review_required`.

This contract defines source text for one pure mathematical kernel. It does not
authorize writing, importing, compiling, testing, or executing that source.

The only prospective source path is:

```text
experiments/EXP-SGCP-SECANT-REP-001/src/sgcp_secant_math_core.py
```

The core implements curve validation, one six-point sign-complete factor base,
one coordinate chart, all 21 unordered pair additions, nonidentity pair-sum
fibers, and least `(slope,i,j)` selection. Everything beyond that list is
forbidden.

## Module boundary

The module may import only:

```python
from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
from typing import Generic as _Generic
from typing import TypeAlias as _TypeAlias
from typing import TypeVar as _TypeVar
```

It has no project-local import, CLI, entry point, file or stream operation,
serialization, hashing, randomness, clock, environment access, network access,
subprocess, dynamic loading, cache, mutable global, scalar multiplication, DLP
table, formal universe, conflict graph, optimizer, decision, evidence label, or
campaign identifier.

Top-level execution is limited to class, enum, type-alias, function, immutable
tuple, and integer declarations. Local lists and dictionaries are permitted
only during a call and are converted to immutable tuples before return.

`__all__` is the exact immutable tuple:

```text
Addition
AdditionBranch
AffinePoint
CandidateCore
ChartFixture
CoreApi
CoreError
CoreErrorCode
CoreOps
CoreResult
Curve
CurveInput
FactorBase
Failure
Fiber
FiberSet
Infinity
Representative
RepresentativeTable
SectionDiagnostics
Success
Witness
build_candidate_core
```

Names beginning with `_` are private. No other non-private name is allowed.

## Immutable types

Every record is `@_dataclass(frozen=True, slots=True)`. Every enum derives only
from `_Enum` and uses the exact member order shown.

```python
class AdditionBranch(_Enum):
    SECANT = "secant"
    TANGENT = "tangent"
    VERTICAL = "vertical"

class CoreApi(_Enum):
    BUILD_CANDIDATE_CORE = "build_candidate_core"

class CoreErrorCode(_Enum):
    TYPE_MISMATCH = "type_mismatch"
    MODULUS_NOT_ODD_PRIME = "modulus_not_odd_prime"
    NONCANONICAL_COEFFICIENT = "noncanonical_coefficient"
    SINGULAR_CURVE = "singular_curve"
    FACTOR_BASE_SIZE = "factor_base_size"
    NONCANONICAL_POINT = "noncanonical_point"
    DUPLICATE_POINT = "duplicate_point"
    FACTOR_BASE_ORDER = "factor_base_order"
    POINT_NOT_ON_CURVE = "point_not_on_curve"
    TWO_TORSION_POINT = "two_torsion_point"
    FACTOR_BASE_NOT_SIGN_COMPLETE = "factor_base_not_sign_complete"
    ZERO_CHART_SCALAR = "zero_chart_scalar"
    NONINVERTIBLE_DENOMINATOR = "noninvertible_denominator"
    INTERCEPT_MISMATCH = "intercept_mismatch"
    INTERNAL_INVARIANT_FAILURE = "internal_invariant_failure"

@_dataclass(frozen=True, slots=True)
class CurveInput:
    p: int
    a: int
    b: int

@_dataclass(frozen=True, slots=True)
class Curve:
    p: int
    a: int
    b: int

@_dataclass(frozen=True, slots=True, order=True)
class AffinePoint:
    x: int
    y: int

@_dataclass(frozen=True, slots=True)
class Infinity:
    pass

@_dataclass(frozen=True, slots=True)
class FactorBase:
    points: tuple[AffinePoint, ...]

@_dataclass(frozen=True, slots=True)
class ChartFixture:
    curve: Curve
    u: int
    factor_base: FactorBase

@_dataclass(frozen=True, slots=True)
class Addition:
    result: AffinePoint | Infinity
    branch: AdditionBranch
    slope: int | None
    intercept: int | None

@_dataclass(frozen=True, slots=True)
class Witness:
    i: int
    j: int
    result: AffinePoint
    slope: int
    intercept: int

@_dataclass(frozen=True, slots=True)
class Fiber:
    result: AffinePoint
    witnesses: tuple[Witness, ...]

@_dataclass(frozen=True, slots=True)
class FiberSet:
    fibers: tuple[Fiber, ...]

@_dataclass(frozen=True, slots=True)
class Representative:
    result: AffinePoint
    witness: Witness

@_dataclass(frozen=True, slots=True)
class RepresentativeTable:
    entries: tuple[Representative, ...]

@_dataclass(frozen=True, slots=True)
class SectionDiagnostics:
    nonidentity_fiber_count: int
    nonsingleton_fiber_count: int
    choice_product: int
    minimum_slope_tie_fibers: int
    slope_collision_pairs: int

@_dataclass(frozen=True, slots=True)
class CandidateCore:
    fixture: ChartFixture
    fibers: FiberSet
    representatives: RepresentativeTable
    diagnostics: SectionDiagnostics

@_dataclass(frozen=True, slots=True)
class CoreOps:
    integer_remainder_tests: int
    field_reductions: int
    field_additions: int
    field_subtractions: int
    field_multiplications: int
    field_squarings: int
    field_negations: int
    field_inversions: int
    point_membership_checks: int
    chart_curve_transforms: int
    chart_point_transforms: int
    unordered_pairs_enumerated: int
    ec_additions: int
    secant_branches: int
    tangent_branches: int
    vertical_pairs_excluded: int
    fiber_witnesses_inserted: int
    sort_keys_emitted: int
    representative_keys_compared: int
    slope_collision_checks: int

@_dataclass(frozen=True, slots=True)
class CoreError:
    code: CoreErrorCode
    api: CoreApi
    indices: tuple[int, ...]

_T = _TypeVar("_T")

@_dataclass(frozen=True, slots=True)
class Success(_Generic[_T]):
    value: _T
    operations: CoreOps

@_dataclass(frozen=True, slots=True)
class Failure:
    error: CoreError
    operations: CoreOps

CoreResult: _TypeAlias = Success[_T] | Failure
```

All integer fields require `type(value) is int`; Boolean values are rejected.
All operation counts are nonnegative exact integers. Domain failures return
`Failure` with the deterministic prefix counter and no partial value. Public
API domain failures never raise, log, mutate input, or use a sentinel.

Error indices are exact:

- a wrong `raw` object uses `()`;
- wrong `p`, `a`, or `b` field types use `(0,)`, `(1,)`, or `(2,)`;
- modulus failure uses `(0,)`;
- noncanonical `a` or `b` uses `(1,)` or `(2,)`;
- singularity uses `(1,2)`;
- a wrong points container uses `(3,)`;
- wrong factor-base length uses `(actual_length,)`;
- a wrong point, `x`, or `y` type uses `(3,i)`, `(3,i,0)`, or `(3,i,1)`;
- all other point-specific errors use `(i,)`;
- a wrong or zero chart scalar uses `(4,)`;
- pair-addition and internal witness errors use `(i,j)`.

## Public API

The only public function is:

```python
def build_candidate_core(
    raw: CurveInput,
    points: tuple[AffinePoint, ...],
    u: int,
) -> CoreResult[CandidateCore]:
    ...
```

The function is deterministic and referentially transparent. It performs the
following phases in exact order and returns on the first failure:

1. curve input type and field validation;
2. modulus validation;
3. coefficient validation;
4. discriminant validation;
5. factor-base container, point, uniqueness, order, membership, two-torsion,
   and sign-completeness validation;
6. chart scalar validation and chart transformation;
7. unordered pair enumeration and affine addition;
8. fiber ordering;
9. least-slope representative selection and diagnostics.

## Validation semantics

### Curve

`raw` must have exact type `CurveInput`. Its fields are checked in order
`p,a,b`. `p` must be an odd prime greater than three. Primality is deterministic
trial division:

1. reject `p<=3`;
2. count and evaluate `p mod 2`;
3. for odd divisors `d=3,5,...` while `d*d<=p`, count and evaluate `p mod d`;
4. reject at the first zero remainder; otherwise accept.

Each evaluated remainder increments `integer_remainder_tests` once.

`a` then `b` must satisfy `0<=value<p`; the first failure is
`NONCANONICAL_COEFFICIENT` with indices `(1,)` for `a` or `(2,)` for `b`.

The discriminant is computed as:

```text
a2 = square(a)
a3 = multiply(a2,a)
t1 = multiply(4 mod p,a3)
b2 = square(b)
t2 = multiply(27 mod p,b2)
disc = add(t1,t2)
```

Zero gives `SINGULAR_CURVE`.

### Factor base

`points` must have exact type `tuple` and length six. Each entry must have exact
type `AffinePoint`; coordinates are checked in index order, `x` before `y`, and
must satisfy `0<=coordinate<p`. Errors use indices `(i,)`.

After coordinate validation:

1. duplicate points are rejected at the second occurrence with `(i,)`;
2. points must be strictly increasing by `(x,y)`; the first out-of-order index
   gives `FACTOR_BASE_ORDER` with `(i,)`;
3. each point is checked for curve membership in index order;
4. the first point with `y=0` gives `TWO_TORSION_POINT`;
5. for each point in order, `(x,-y mod p)` must occur in the six-point set; the
   first miss gives `FACTOR_BASE_NOT_SIGN_COMPLETE`.

Membership computes and compares:

```text
square(y)
square(x)
multiply(square(x),x)
multiply(a,x)
add(x^3,a*x)
add(previous,b)
subtract(y^2,rhs)
```

and increments `point_membership_checks` once before those operations.
Sign-completeness increments `field_negations` once per visited point.

### Chart

`u` must have exact type `int`. Compute `u0=u mod p` and increment
`field_reductions` once. Zero gives `ZERO_CHART_SCALAR`.

Compute in this order:

```text
u2=square(u0)
u3=multiply(u2,u0)
u4=square(u2)
u6=multiply(u4,u2)
a'=multiply(u4,a)
b'=multiply(u6,b)
x'=multiply(u2,x)
y'=multiply(u3,y)
```

The last two operations repeat for each point in source-label order.
Increment `chart_curve_transforms` once and `chart_point_transforms` once per
point. Sort transformed points by `(x,y)` and increment `sort_keys_emitted` by
six. The sorted positions are the chart source labels.

## Field-operation semantics

Each private field wrapper increments its named counter exactly once before
returning the canonical residue. Squaring is not multiplication. One abstract
inversion uses `pow(value,-1,p)`, increments `field_inversions` once, and does
not charge its internal integer operations. Equality and tuple comparison are
uncharged. No floating-point operation is permitted.

## Pair addition and fibers

Enumerate pairs in lexicographic `(i,j)` order with outer `i=0..5` and inner
`j=i..5`. Increment `unordered_pairs_enumerated` and `ec_additions` once before
each pair. A successful factor base therefore enumerates exactly 21 pairs.

For `i=j`, use tangent:

```text
numerator = add(multiply(3 mod p,square(x_i)),a)
denominator = multiply(2 mod p,y_i)
```

For `i<j` and `x_i=x_j`, compute `add(y_i,y_j)`. Zero is the vertical identity:
increment `vertical_pairs_excluded`, return no witness, and continue. Nonzero
is `INTERNAL_INVARIANT_FAILURE` with `(i,j)`.

For `i<j` and `x_i!=x_j`, use secant:

```text
numerator = subtract(y_j,y_i)
denominator = subtract(x_j,x_i)
```

Increment exactly one of `tangent_branches` or `secant_branches`. A zero
nonvertical denominator gives `NONINVERTIBLE_DENOMINATOR`.

For tangent and secant, compute:

```text
lambda = multiply(numerator,invert(denominator))
x_R = subtract(subtract(square(lambda),x_i),x_j)
y_R = subtract(multiply(lambda,subtract(x_i,x_R)),y_i)
nu_left = subtract(y_i,multiply(lambda,x_i))
nu_right = subtract(negate(y_R),multiply(lambda,x_R))
```

Check result membership using the exact membership routine. A failure is
`INTERNAL_INVARIANT_FAILURE`. Unequal intercepts give `INTERCEPT_MISMATCH`.
Store canonical `lambda` and `nu_left`.

Each retained witness increments `fiber_witnesses_inserted`. Group witnesses by
`R=(x_R,y_R)`. Witnesses retain pair-enumeration order. Sort fibers by
`(x_R,y_R)` and increment `sort_keys_emitted` by the number of fibers.

## Representative selection

For each fiber in order, scan witnesses in stored order. Select the least
`(slope,i,j)`. Initialize from the first witness and increment
`representative_keys_compared` once for each later witness. Representatives
remain in fiber order.

For diagnostics:

- `nonidentity_fiber_count` is the number of fibers;
- `nonsingleton_fiber_count` counts fibers with at least two witnesses;
- `choice_product` is the exact product of all fiber witness counts, with
  multiplicative identity one;
- inspect every unordered pair of witnesses in each fiber, incrementing
  `slope_collision_checks` once;
- `slope_collision_pairs` counts inspected pairs with equal slopes;
- `minimum_slope_tie_fibers` counts fibers where at least two witnesses have the
  minimum slope.

## Composition and counters

The implementation uses one immutable-counter replacement at each operation;
no shared mutable counter exists. Private helpers return value-or-error plus
their local `CoreOps`. `build_candidate_core` combines phase counters by
componentwise integer addition in phase order.

On success:

```text
CandidateCore(
  fixture=transformed chart fixture,
  fibers=ordered fiber set,
  representatives=ordered table,
  diagnostics=exact diagnostics,
)
```

The counters are algorithmic development metadata only. They are not V5's
121-leaf ledger, process/resource measurements, failure charges, amortized
costs, or cryptanalytic evidence.

## Explicit exclusions

The core does not accept or derive seeds, curve order `q`, trace, j-invariant,
registered provenance, cap values, compiler/control indices, factor-base
digests, hash controls, source permutations, formal degree-four values,
conflict metrics, optimizer inputs, objective values, rank, relation matrices,
target descent, ECDLP instances, rho baselines, or experiment decisions.

A future independent verifier must not import this module or share normalized
function bodies with it. The V5 campaign wrapper remains unresolved and locked.

## Static review obligations

Before source writing, independent reviewers must establish:

1. formula correspondence with protocol v6;
2. total first-error and counter semantics;
3. purity and singleton-path closure;
4. no accidental campaign or evidence surface;
5. a closed Coordinator transition bound to the exact reviewed commit.

After source writing, a new exact-source review is required before importing,
compiling, testing, or executing the module.
