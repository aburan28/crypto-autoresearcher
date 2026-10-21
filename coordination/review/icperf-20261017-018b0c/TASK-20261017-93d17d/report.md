# Blind J0 re-derivation — EXP-ICPERF-018b0c

**Task:** TASK-20261017-93d17d  
**Joint:** J0 — Independently reconstruct the target and call schedule from its stated parameters.  
**Verdict:** **inconclusive** for a uniquely specified admission schedule; the complete schedule under the natural four-torsion interpretation of `gamma` is derived below.

## Independent method and scope

`independent_schedule.py` implements multiplication and inversion in
`GF(2^61)` modulo `x^61+x^5+x^2+x+1`, and the affine group law for
`y^2+xy=x^3+31`. It uses only Python's standard library and the frozen
specification and fixture. The script checks that the source and generator
lie on the curve, `[4]P_source=G`, `[r]G=O`, that `[r]P_source` has exact
order four, and that every emitted raw channel projects by `[4]` to its
subgroup target. The code invokes no solver.

The unique field element satisfying `gamma^4=b` is
`gamma=70364449406991`; this is also the x-coordinate of
`T=[r]P_source=(70364449406991,2147483661)`. With that interpretation,
`R0=[4^-1 mod r]Q`, and the four raw points are `R0+[c]T` for `c=0..3`.
Their full coordinates and `gamma/(x+gamma)` values appear in
`blind_counts.json`.

| Target | Counter | Public scalar `k_j` | Subgroup point `Q_j=(x,y)` |
| ---: | ---: | ---: | --- |
| 0 | 0 | 106919752671816517 | (1250816774662656094, 719130459235150771) |
| 1 | 1 | 170711963231727215 | (1231810103128033020, 2086257710553374744) |
| 2 | 2 | 6718495876688090 | (1212505062386292020, 2145994571839816542) |
| 3 | 3 | 547768927640051783 | (1819855663958033427, 1201697634592310307) |
| 4 | 4 | 83989824178140575 | (1032815707205918473, 1794342060042239751) |
| 5 | 5 | 165121303974308139 | (2258622349727763509, 1573046746596171617) |
| 6 | 6 | 345861343518129524 | (1556187573938699746, 2167355200914579755) |
| 7 | 7 | 411739324728539494 | (1693601286062314442, 1240109355077386163) |

All eight scanned candidates satisfy the affine, nonzero-x and derived-pole
filters. None is rejected. The exact planned sequence is two planted labels
(`weighted`, `local_random`), then 64 natural labels: eight targets in order,
two bases per target with the first base alternating by target parity, and
channels 0, 1, 2, 3 within each base. All 66 labels, including ordinal and
candidate counter, are serialized in `blind_counts.json`. These are planned
labels; this review makes no statement about executed solver calls.

## Controls and specification gap

Changing the domain separator to `ICPERF-k11-natural-v2` changes the first
scalar to `431018338182958407` and the first point to
`(1599023312214376474,1792215615552220005)`. The pole predicate rejects
the constructed channel `T`: its x-coordinate is the derived `gamma`, and
`phi(T)` raises `pole x=gamma`. This is a predicate boundary control, not an
admitted nonidentity subgroup target.

The allowed specification states `x is not gamma` and gives
`t=gamma/(x+gamma)`, but neither it nor the fixture explicitly defines
`gamma` as the unique fourth root of `b`, the x-coordinate of `T`, or a
numeric field element. A literal alternative `gamma=714891581849174975`
(the first raw channel's x-coordinate) rejects counter 0 as a pole and
admits counters 1–8. Thus the two allowed input documents alone do not make
the admission schedule unique. The natural four-torsion interpretation
produces the concrete derivation above; binding that interpretation in the
frozen statement or a permitted immutable input would make J0 decidable.
This gap concerns reproducibility of J0 only and is not mathematical evidence
about relation yield or solver viability.

## Input custody and limits

The fixture's raw SHA-256 is
`230d941d79152b17697341f65e5a46ddd2e3deb5e58f9ca21be889e49a5df39a`,
matching the frozen specification. The other external input digests read were:

| Input | SHA-256 |
| --- | --- |
| `experiments/EXP-ICPERF-018b0c/specification.yaml` | `2e3682e98a8eedf7296b53248554ff19bf47a8392146b94670f2dad92ee90844` |
| `ledger/handoffs/TASK-20261017-93d17d.yaml` | `4e753170b6fa4b8c2e9cce931002aadfb0ae138f64d9351f50674deb113acbc7` |
| `ledger/handoffs/TASK-20261017-b5d54d.yaml` | `4ae9b686bc9f61a47a3d7e6147501a4c2db7392731a4ff180a7633092fc91388` |

This review read no prepared input, producer implementation, run, report,
earlier review, queue summary, or Git history. It did not validate the two
planted formulas, any executed model, cost, yield, or scientific conclusion.
The four files in this task's output directory are for the Coordinator's
content-first snapshot; this session does not commit or alter official state.

## Review attestation

See `review_attestation.yaml` for exact joint ownership, all external sources
read, blindness declaration, and per-joint verdict.
