# Pinned schedule/history reachability audit

Task `TASK-20260730-021` performs one deterministic, symbolic analysis. It
does not execute `CollimationSieve`, a curve/isogeny computation, or a quantum
circuit.

## Pin and finite model

Before enumeration, `schedule_pin.yaml` fixed the actual `src/Main.hs`
construction at `CollimationSieve@6f9188e4` with
`(logn, logl, logs, threshold) = (2, 2, 0, 3/4)`. Thus
`n = 4`, `L = 4`, and the source expression

```haskell
takeWhile (< n) (iterate (\t -> (2 * t * fromIntegral l) `div` 3) s) ++ [n]
```

gives the explicit interval list `[1,2,4]`. The root `S=1` frame has
`alwaysKeep=True`, so it cannot take the discard/retry branch. The only local
retry site in this schedule is an internal `S=2` frame.

The state at such a frame is
`(requested_length, schedule suffix, call_history, v1, v2, tape_position)`.
`call_history` records whether the first or second child is being generated
and whether the designated `S=2` retry has been consumed. The typed finite
choice tape contains exact base draws in `{0,1,2,3}` and exact enabled
collimation indices. It is an exhaustive ideal-choice model for the finite
branches, not a model or proof of the source repository's entropy-seeded
HashDRBG.

For each requested length that becomes reachable (`1,2,3,4`), the analyzer
reconstructs the two recursive base calls exactly as `sieve'` does, enumerates
their sorted subset-sum vectors, and then evaluates every `q` bin. A
zero-progress state is one where no bin has cardinality at least
`ceil((3/4)*requested_length)`.

## Findings

The enumeration examined 176 distinct `S=2` pre-collimation child-vector-pair
states: 16, 32, 64, and 64 for requested lengths 1, 2, 3, and 4,
respectively. Adding the initial/retry history marker gives 352 `S=2` control
states through one retry. It also checked 536 accepted child-vector pairs at
the root. No `S=2` state was zero-progress. The exact minimum conditional keep
probabilities were 1, 3/4, 3/4, and 3/4 for these four requested lengths.

Consequently, in the declared bounded model:

- `jointly_reachable: false` for the zero-progress class;
- `recurrent: false`, because there is no zero-progress state at either
  history marker;
- no witness trace exists.

This does not mean that the bounded schedule never retries. Across the
reachable requested lengths, 60 of the 176 vector-pair states have at least
one discarding sampled-index outcome (130 such `(v1,v2,I,J)` outcomes in
total). Each retry regenerates the same-level children from later typed-tape
symbols; exhaustive successor enumeration again has no zero-progress state.

This is an exclusion for this pre-pinned finite ideal-choice abstraction only.
It does not reject C2 globally, establish a global stopping tail, transfer to
the concrete HashDRBG, establish end-to-end finite `Q/S/P/C`, or clear the
memory and final-error-map gates. Recovery implementation and object-lifetime
tracing were not performed.

## Reproduction source

Run from the repository root with Python 3 standard library:

```sh
python3 - <<'PY'
from collections import defaultdict
from itertools import product
from fractions import Fraction

def ceildiv(a, b):
    return (a + b - 1) // b

def round_log2_for_reachable_l(l):
    return {1: 0, 2: 1, 3: 2, 4: 2}[l]

def ceil_sqrt(a):
    x = 0
    while x * x < a:
        x += 1
    return x

def base_vectors(requested_l):
    r = round_log2_for_reachable_l(requested_l)
    return sorted({
        tuple(sorted(
            sum(((mask >> bit) & 1) * z[bit] for bit in range(r)) % 4
            for mask in range(1 << r)
        ))
        for z in product(range(4), repeat=r)
    })

def bins(v1, v2, s=2):
    out = defaultdict(int)
    for a in v1:
        for b in v2:
            out[(a + b) // s] += 1
    return out

def pre_collimation_pairs(requested_l):
    first_l = ceil_sqrt(3 * requested_l)
    for v1 in base_vectors(first_l):
        second_l = ceildiv(3 * requested_l, len(v1))
        for v2 in base_vectors(second_l):
            yield first_l, second_l, v1, v2

for l in range(1, 5):
    required = ceildiv(3 * l, 4)
    probabilities = []
    zero = 0
    discard_outcomes = 0
    states_with_discard = 0
    for _, _, v1, v2 in pre_collimation_pairs(l):
        counts = bins(v1, v2)
        p = Fraction(sum(c for c in counts.values() if c >= required),
                     len(v1) * len(v2))
        probabilities.append(p)
        zero += p == 0
        bad = sum(c for c in counts.values() if c < required)
        discard_outcomes += bad
        states_with_discard += bad > 0
    print(l, len(probabilities), zero, min(probabilities),
          discard_outcomes, states_with_discard)
PY
```

The output is:

```text
1 16 0 1 0 0
2 32 0 3/4 10 8
3 64 0 3/4 60 26
4 64 0 3/4 60 26
```
