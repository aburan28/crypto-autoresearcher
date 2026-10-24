# Blind derivation for J-algebra

Task: `TASK-20261023-5301b1`. Experiment: `EXP-ICPERF-3065f9`.
Snapshot: `8099215faa2ef4a0e2b679b124538e249c5fdf1f`.
This is an independent derivation of the statement, not a validation of the
unread producer implementation or a verdict on complete-solve performance.

## Statement, domain, and sources

The frozen specification names the reference target
`E.add(E.mul(a, P), E.mul(b, Q))`, a fixed window of four bits, and the same
public points for both arms. Here scalar `a,b` are distinct from the curve's
Weierstrass coefficients. Let `O` be infinity. Assume a valid additive group
and integers `0 <= a,b < 2**B`, where `B >= 1` is a declared cache bound.
The group is abelian, as the permitted elliptic-curve group is.
No independence assumption between `P` and `Q` is needed.

Mathematical inputs actually used are the published handoff, frozen
`experiments/EXP-ICPERF-3065f9/specification.yaml`,
`config/ic-target-benchmark.json`, the bound baseline
`src/crypto_autoresearcher/index_calculus/curve.py`, and public
`experiments/EXP-ICPERF-3065f9/runs/RUN-ICPERF-842b51/instances.json`.
The accompanying YAML lists every administrative source read as well.
The protected implementation, benchmark/analysis code, raw results,
validation output, measured reports, sibling review, and commit messages
were not read. Only commit identifiers, tree paths, and the permitted
files' blob bytes were inspected through Git.

The specification describes a random scalar distribution without stating
the exact sampling interval or RNG call order. Neither is needed for the
identity or count formula. If the intended domain is `0 <= a,b < N`, set
`B = (N-1).bit_length()`. The table below uses that conditional substitution;
it does not certify the unread sampler's range or the producer's cache bound.

## Radix identity

Put `r = 2**4 = 16` and `W = ceil(B/4)`. For `0 <= j < W`, define

```text
a_j = (a >> (4*j)) & 15
b_j = (b >> (4*j)) & 15
T_P[j,d] = [d * 16**j]P,  0 <= d < 16
T_Q[j,d] = [d * 16**j]Q,  0 <= d < 16.
```

Repeated Euclidean division by 16 gives unique digit expansions
`a = sum_j a_j*16**j` and `b = sum_j b_j*16**j`. Distributivity of integer
scalar multiplication over group addition therefore gives

```text
sum_j (T_P[j,a_j] + T_Q[j,b_j])
  = [sum_j a_j*16**j]P + [sum_j b_j*16**j]Q
  = [a]P + [b]Q.
```

This is a group identity, with no heuristic, timing, or distributional
premise. Starting an accumulator at `O` and omitting zero digits preserves
the identity because `T_X[j,0] = O`. Caching changes neither the scalar
pair nor its resulting point when the same expansion and points are used.
It says nothing about whether an unread implementation follows this definition.

If `t = B - 4*(W-1)`, the top digit has only `t` significant bits:
`0 <= a_(W-1), b_(W-1) < 2**t`. A partial top window must still be processed.
Using `floor(B/4)` windows loses high digits when `B` is not divisible by four.
A final-window mask of 15 is harmless for a valid input bound because the
unused high bits are already zero.

Conditional public-order substitution, derived from `instances.json`:

| Instance | N | B | W | Top significant bits |
|---|---:|---:|---:|---:|
| 12:0 | 2927 | 12 | 3 | 4 |
| 12:1 | 3119 | 12 | 3 | 4 |
| 12:2 | 2053 | 12 | 3 | 4 |
| 14:0 | 11681 | 14 | 4 | 2 |
| 14:1 | 16217 | 14 | 4 | 2 |
| 14:2 | 16111 | 14 | 4 | 2 |
| 16:0 | 53591 | 16 | 4 | 4 |
| 16:1 | 52121 | 16 | 4 | 4 |
| 16:2 | 64919 | 16 | 4 | 4 |

## Exact reference E.add-call count

Let `L(s) = s.bit_length()` and `H(s) = s.bit_count()` for nonnegative `s`,
so `L(0) = H(0) = 0`. In the permitted baseline `Curve.mul`, a positive
scalar has exactly `L(s)` loop iterations. Each iteration calls
`add(P,P)` once, including the final iteration whose doubled point is
discarded. A set bit additionally calls `add(R,P)` once. Thus

```text
C_mul(s) = L(s) + H(s)
C_ref(a,b) = L(a) + H(a) + L(b) + H(b) + 1.
```

The last `+1` is the outer `E.add`, even if one or both products are
infinity. The baseline increments `ops.group_ops` at entry to `add`, before
any infinity/inverse/doubling branch. Consequently these are call counts,
not field-arithmetic costs, and depend on the scalar values rather than
the points or intermediate cancellations. For any `0 <= a,b < 2**B`,
`1 <= C_ref(a,b) <= 4*B + 1`.

Examples derived without any target trace:

| a | b | C_ref |
|---:|---:|---:|
| 0 | 0 | 1 |
| 1 | 0 | 3 |
| 0 | 1 | 3 |
| 16 | 0 | 7 |
| 16 | 1 | 9 |
| 15 | 16 | 15 |

For a fixed list of `T` scalar pairs the target-only reference count is
`T + sum_i (L(a_i)+H(a_i)+L(b_i)+H(b_i))`. If, additionally, both scalars
were uniform on `[0,N)`, the expected per-target count would be
`1 + (2/N)*sum_(s=0)^(N-1)(L(s)+H(s))`; this is conditional, not an
assertion about the unread sampler. No actual trace total is inferred.

The radix identity alone fixes neither candidate setup calls nor its
per-target addition schedule. For example, combining every selected table
entry in one accumulator and combining separate scalar accumulators have
different overheads. Cache construction, full solver work, storage, and
verification must be charged at their specified boundaries. A reduction
in this target-only count cannot establish a complete-solve speedup.

## Boundary controls and the known-false construction

`a=0` and `b=0` have all-zero digits, so their group contribution is `O`.
Both zero returns `O` with exactly one reference `add` call. Infinity
points, an intermediate infinity, and a final cancellation are valid group
values; they retain the same reference call formula. On the 14-bit public
orders, scalar 4096 explicitly exercises the nonempty fourth window.

An intentionally wrong cache uses `[2**j]P` for window `j`, retaining the
correct digit extraction at `4*j`. In the additive group Z/101Z, take
`P=1, Q=7, a=16, b=0, B=8`. Correct radix evaluation is 16. The wrong
shift returns 2. Thus equality rejects the mutant. The difference 14 is
nonzero modulo 101. This is a machine-checkable negative control with a
known-false conclusion, independent of elliptic-curve or producer code.
The script also rejects that mutant on each permitted public instance.

## Reproducible arithmetic certificate

This script is reviewer-authored. It executes only the permitted `curve.py`
through `runpy`, without importing the package's initializer or producer
target module. It does not launch a solve, benchmark, scientific trial, or
model request. Table arithmetic is an independent implementation of the
definition above. The assertions compare it with the bound baseline and
the count formula, including every required boundary and negative control.

Run from the repository root with bytecode writes disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
from pathlib import Path
text = Path('coordination/tasks/TASK-20261023-5301b1/derivation.md').read_text()
script = text.split('```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(script, '<blind-arithmetic-certificate>', 'exec'))
PY
```

```python
import json
import runpy
from pathlib import Path

Curve = runpy.run_path(
    'src/crypto_autoresearcher/index_calculus/curve.py')['Curve']
instances = json.loads(Path(
    'experiments/EXP-ICPERF-3065f9/runs/RUN-ICPERF-842b51/instances.json'
).read_text())

def count_formula(a, b):
    return 1 + a.bit_length() + a.bit_count() + b.bit_length() + b.bit_count()

def independent_window(add, zero, P, Q, a, b, B, base_shift=4):
    if B < 1 or min(a, b) < 0 or max(a, b) >= (1 << B):
        raise ValueError('scalar outside declared nonnegative bit bound')
    W = (B + 3) // 4
    def rows(base):
        result = []
        for j in range(W):
            row = [zero, base]
            for d in range(2, 16):
                row.append(add(row[-1], base))
            result.append(row)
            if j + 1 < W:
                for _ in range(base_shift):
                    base = add(base, base)
        return result
    TP, TQ = rows(P), rows(Q)
    R = zero
    for j in range(W):
        da, db = (a >> (4*j)) & 15, (b >> (4*j)) & 15
        if da:
            R = add(R, TP[j][da])
        if db:
            R = add(R, TQ[j][db])
    return R

pair_checks = 0
def check_pair(E, P, Q, a, b, B):
    global pair_checks
    E.ops.group_ops = 0
    expected = E.add(E.mul(a, P), E.mul(b, Q))
    actual_calls = E.ops.group_ops
    assert actual_calls == count_formula(a, b), (a, b, actual_calls)
    actual = independent_window(E.add, None, P, Q, a, b, B)
    assert actual == expected, (a, b, actual, expected)
    pair_checks += 1
    return expected

add101 = lambda x, y: (x + y) % 101
good = independent_window(add101, 0, 1, 7, 16, 0, 8)
bad = independent_window(add101, 0, 1, 7, 16, 0, 8, base_shift=1)
assert good == 16 and bad == 2 and bad != good
# A partial high window is necessary: dropping it returns zero for 4096.
assert independent_window(add101, 0, 1, 7, 4096, 0, 14) == 4096 % 101
assert sum(((4096 >> (4*j)) & 15) * (16**j)
           for j in range(14 // 4)) == 0
for a, b, B in [(-1, 0, 8), (0, -1, 8), (256, 0, 8), (0, 256, 8)]:
    try:
        independent_window(add101, 0, 1, 7, a, b, B)
    except ValueError:
        pass
    else:
        raise AssertionError('missing scalar-bound rejection')

public_negative_controls = 0
public_bound_rows = []
for name, item in sorted(instances.items()):
    E = Curve(item['p'], item['a'], item['b'])
    P, Q = tuple(item['P']), tuple(item['Q'])
    N, k = item['order'], item['public_expected_k']
    B = (N - 1).bit_length()
    W = (B + 3) // 4
    assert E.is_on_curve(P) and E.is_on_curve(Q)
    assert E.mul(N, P) is None
    assert E.mul(k, P) == Q
    values = sorted({0, 1, 15, 16, 1 << (4*(W-1)), N-1})
    for a in values:
        for b in values:
            check_pair(E, P, Q, a, b, B)
    assert check_pair(E, P, Q, (-k) % N, 1, B) is None
    for X, Y, a, b in [(None, Q, 0, 0), (None, Q, 16, 1),
                       (P, None, 16, 0), (None, None, 16, 16),
                       (P, E.neg(P), 16, 16)]:
        check_pair(E, X, Y, a, b, B)
    expected = E.mul(16, P)
    wrong = independent_window(E.add, None, P, Q, 16, 0, B, base_shift=1)
    assert wrong != expected
    public_negative_controls += 1
    public_bound_rows.append({
        'instance': name, 'N': N, 'B': B, 'W': W,
        'top_bits': B - 4*(W-1),
        'reference_calls_at_Nminus1_pair': count_formula(N-1, N-1)})

print(json.dumps({
    'status': 'passed',
    'public_instances': len(instances),
    'reference_count_and_identity_pair_checks': pair_checks,
    'public_wrong_shift_controls_rejected': public_negative_controls,
    'synthetic_wrong_shift': {'modulus': 101, 'P': 1, 'Q': 7,
                              'a': 16, 'b': 0, 'correct': good,
                              'wrong': bad, 'rejected': bad != good},
    'partial_window_control_passed': True,
    'scalar_bound_negative_controls_rejected': 4,
    'public_bounds': public_bound_rows
}, indent=2, sort_keys=True))
```

## Verdict and limits

The certificate was executed twice with identical JSON output. Each execution
passed 378 reference-count and identity checks across nine public instances,
rejected nine public wrong-shift cases, passed the partial-window control,
and rejected four synthetic invalid scalar bounds. The synthetic wrong-shift
output was exactly `correct=16, wrong=2, rejected=true`. The accompanying
YAML retains the complete JSON result as parsed data, the exact command,
interpreter, and certificate code hash.

`J-algebra: holds` for the radix identity under its explicit nonnegative
bit-bound precondition and for the exact reference call formula bound to
the permitted `Curve.mul/add`. No mathematical counterexample or concrete
correctness blocker was found in that statement. The arithmetic certificate
does not read or validate producer cache construction, digit shifts, scalar
sampling, measured counts, target traces, solve certificates, or timing.
Those are outside this blind joint. There is no whole-claim performance
verdict, runtime model probe, or model-diversity attestation.
