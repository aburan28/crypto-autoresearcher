# Exact rank traffic model v3

## Handoff: complete elimination access ceiling

### Claim or task

Freeze a complete logical coefficient-access model for every exact unfolding
rank job, including elimination updates that were omitted from the v2 ceiling.

### Status

`RESTRICTED THEOREM` for the specified incremental row-basis implementation.
This is an algorithm-specific upper bound, not a lower bound for all exact
rank algorithms.

### Assumptions

- Orient each unfolding with
  `r=min(B^k,B^(5-k))` working rows and
  `c=max(B^k,B^(5-k))` coefficients per row.
- The producer uses an incremental normalized row basis. The verifier uses an
  independently coded column basis on the transposed orientation with the same
  access ceiling.
- Pivot indices increase strictly. Each evolving row scans monotonically, so
  no coefficient is examined more than once by pivot search.
- A row swap changes pointers and pivot metadata only. It does not copy `c`
  field coefficients.
- One `F_p2` coefficient occupies two base-field words. Metadata bytes are
  accounted separately.

### Evidence so far

Put

```text
P = c*r
E = c*r*(r-1)/2
N = E+P = c*r*(r+1)/2.
```

`P` is the working matrix size, `E` is the maximum number of coefficient
positions updated while eliminating earlier pivots, and `N` is the total
multiplication ceiling after including one full-row normalization per pivot.

The complete field-word traffic ceiling is:

| Phase | Field-word accesses |
|---|---:|
| Materialize working rows | `2P` |
| Monotone pivot scans | `P` |
| Elimination updates | `3E` |
| Normalize pivot rows | `2P` |
| Digest pivot-row certificate | `P` |
| **Total** | **`T=3E+6P`** |

Each elimination update reads one target coefficient and one normalized pivot
coefficient, then writes the target coefficient. The multiplication and
subtraction share those accesses; they are not separate memory passes.

The v2 value `3N` was invalid because it did not include a complete
elimination-update stream. V3 replaces it rather than reinterpreting it.

Across the exact frozen job matrix:

| Field | `N` multiplications | `E` subtractions | `P` coefficients | `T` field words |
|---|---:|---:|---:|---:|
| `F_p` | 159007996 | 152824740 | 6183256 | 495573756 |
| `F_p2` | 14725568 | 14109700 | 615868 | 46024308 |

Converting `F_p2` traffic to two base-field words gives

```text
2*46024308 = 92048616
```

base-field-word equivalents. The complete rank ceiling per baseline path is

```text
495573756+92048616 = 587622372
```

base-field-word equivalents, before separately reported pointer, pivot-index,
JSON, timing, and process metadata bytes. At the largest canonical base-field
width of three bytes, this is 1762867116 logical bytes. It is cumulative
traffic, not peak resident state.

The run emits observed counts for every phase. It is invalid if an observed
count exceeds its bound or if an implementation uses a different access
schedule without a versioned model.

### Failure modes

- Charging arithmetic operations but not their reads and writes.
- Counting multiplication and subtraction as separate coefficient passes when
  the implementation fuses them.
- Copying complete rows during a purported pointer swap.
- Restarting pivot scans from column zero and still claiming the monotone-scan
  ceiling.
- Hiding certificate reads, extension-word width, or metadata.
- Confusing cumulative logical traffic with peak RSS.

### Next concrete action

Bind this model and `execution-matrix-v3.json` into `contract-v3.md` and
`specification-v3.json`, then obtain one independent accounting review before
implementation.

### Artifact paths

- `execution-matrix-v3.json`
- `contract-v3.md`
- `specification-v3.json`

