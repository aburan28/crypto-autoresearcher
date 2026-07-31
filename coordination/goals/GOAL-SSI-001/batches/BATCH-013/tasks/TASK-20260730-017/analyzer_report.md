# Bounded idealized reachable-state audit

Task `TASK-20260730-017` executes one deterministic, discrete-combinatorics
package under `DEC-20260730-011`. It does not run the pinned simulator, any
curve/isogeny computation, or a quantum circuit.

## Finite model and bounds

This audit uses only the conditional kernel extracted in BATCH-012. For each
`n in {2,3,4}` and `ell in {2,4}`, let `r = log2(ell)`. A base-child vector is
enumerated as every distinct sorted tuple

\[
  \operatorname{sort}\{ \sum_{b=0}^{r-1} e_b z_b \bmod n:
  (e_0,\ldots,e_{r-1})\in\{0,1\}^r\},
\]

where `(z_0,...,z_(r-1))` ranges over `[0,n-1]^r`. This is the finite
ideal-random interpretation of the extracted base subset-sum construction.
It supplies reachable children for a **one-internal-node** model; it does not
model concrete `HashDRBG` state, deeper regenerated children, or the supplied
interval schedule.

For every ordered reachable pair `(v1,v2)`, every internal `s in [1,n-1]`,
and `theta in {1/2,3/4,1}`, the analyzer forms

\[
 c_q=\#\{(i,j): \lfloor(v_1[i]+v_2[j])/s\rfloor=q\},\quad
 p(v_1,v_2)=\frac{\sum_{q:c_q\ge\lceil\theta\ell\rceil}c_q}{\ell^2}.
\]

`alwaysKeep` is false throughout. All arithmetic is exact integers and
`fractions.Fraction`; there is no seed or randomness in this analysis.

## Observation

The package checks 1,014 parameterized ordered child-pair states across 36
`(n, ell, s, theta)` rows and finds 16 zero-progress states. A representative
witness is

\[
 (n,\ell,s,\theta,v_1,v_2)=(3,2,1,3/4,(0,1),(0,2)).
\]

Here `ceil(theta*ell)=2`, while the four pair sums fall into distinct
integer-width-one bins: `0, 1, 2, 3`. Thus every `c_q=1` and
`p(v1,v2)=0`. Both child vectors are reachable in the stated model by the
single base draws `z=1` and `z=2`, respectively. The smallest nonzero
probability observed over the enumerated state set is `1/4`.

This witness shows that the selected finite idealized one-level model does not
have a positive conditional progress lower bound over its enumerated state
space at all tested parameter rows. It strengthens the reason for retaining
the C2 stopping control. It does **not** establish that this parameter tuple is
used by the pinned simulator's actual schedule, that its concrete DRBG reaches
this state, or that a complete end-to-end retry process has a heavy tail.

## Non-extrapolation

`non_extrapolation: true`. Finite coverage neither proves nor disproves a
history- and parameter-uniform progress bound for the implementation. It
cannot supply a global stopping tail, finite joint `Q/S/P/C` expectations, a
memory peak, or an end-to-end recovery result. The separate recovery
specification is an unimplemented required schedule, not evidence that the
pinned simulator implements one.

## Reproduction command and embedded source

Run from repository root with Python 3 standard library:

```sh
python3 - <<'PY'
from fractions import Fraction
from itertools import product

thresholds = (Fraction(1, 2), Fraction(3, 4), Fraction(1, 1))
rows, witnesses, positive = [], [], []
for n in (2, 3, 4):
    for ell in (2, 4):
        r = ell.bit_length() - 1
        vectors = {
            tuple(sorted(
                sum(((mask >> bit) & 1) * z[bit] for bit in range(r)) % n
                for mask in range(ell)
            ))
            for z in product(range(n), repeat=r)
        }
        for s in range(1, n):
            for theta in thresholds:
                required = -(-theta.numerator * ell // theta.denominator)
                checked = zero = 0
                local_positive = []
                for v1 in vectors:
                    for v2 in vectors:
                        counts = {}
                        for a in v1:
                            for b in v2:
                                q = (a + b) // s
                                counts[q] = counts.get(q, 0) + 1
                        p = Fraction(
                            sum(c for c in counts.values() if c >= required),
                            ell * ell,
                        )
                        checked += 1
                        if p == 0:
                            zero += 1
                            witnesses.append((n, ell, s, str(theta), v1, v2))
                        else:
                            local_positive.append(p)
                            positive.append(p)
                rows.append((n, ell, len(vectors), s, str(theta), required,
                             checked, zero,
                             min(local_positive) if local_positive else None))
print(len(rows), sum(row[6] for row in rows), sum(row[7] for row in rows),
      min(positive))
PY
```

Observed output summary: `36 1014 16 1/4`.
