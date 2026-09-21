# EXP-FB-001 analysis — factor-base structure sweep

**Run:** `RUN-FB-001-a` (valid). `p=16411`, `m=3`, `d ∈ {6,8,10,12}`, 3 seeds.
Structures compared: random (control), interval (small x), arithmetic-progression.
(The multiplicative-subgroup base yielded <3 liftable points and is excluded — noted.)

## Result (all d_reg=2)

| d | random yield | interval | ap | solve time (all structs) |
|---|---|---|---|---|
| 6  | 0.00330 | 0.00340 | 0.00340 | ~0.018 s |
| 8  | 0.00716 | 0.00716 | 0.00728 | ~0.10 s |
| 10 | 0.01318 | 0.01298 | 0.01328 | ~0.32 s |
| 12 | 0.02001 | 0.02165 | 0.02189 | ~1.13 s |

## Verdict — falsification MET
No structure exceeds 1.5× random on yield (max ~1.1×); `d_reg=2` for every structure and
`d`; solve-time scaling (`~d⁶ = ℓ²` at m=3) is identical across structures. Yield tracks the
combinatorial `|FB|³/N`. **Factor-base structure is not a scaling lever** — yield, solving
degree, and solve cost are structure-invariant. Scoped negative (toy `p≈2^14`); reinforces R8.
