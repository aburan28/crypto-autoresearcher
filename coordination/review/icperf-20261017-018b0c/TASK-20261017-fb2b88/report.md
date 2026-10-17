# Blind target and call-schedule derivation

Task: `TASK-20261017-fb2b88`  
Experiment: `EXP-ICPERF-018b0c`  
Joint: deterministic target/channel schedule and planned call count.

## Inputs and method

I derived this before reading any prepared target manifest, producer implementation, run record, report, or sibling review. The scientific inputs were only the [frozen specification](../../../../experiments/EXP-ICPERF-018b0c/specification.yaml) (SHA-256 `2e3682e98a8eedf7296b53248554ff19bf47a8392146b94670f2dad92ee90844`) and [curve fixture](../../../../research/icperf_ordinary_binary_fixture_20261017/fixture.json) (SHA-256 `230d941d79152b17697341f65e5a46ddd2e3deb5e58f9ca21be889e49a5df39a`). The handoff SHA-256 is `906023749190464c436d5dac873745a83243cbfa71778e57ad81d646dd12fb7c`.

The [independent script](independent_schedule.py) implements polynomial-basis arithmetic over `GF(2^61)` with modulus `x^61+x^5+x^2+x+1`, affine addition/doubling for `y²+xy=x³+b`, scalar multiplication, and the stated SHA-256 counter rule. It checks the fixture's generator and source equations, `[4]P_source=G`, `[r]G=O`, and that `T=[r]P_source` has order four. It obtains `gamma=x(T)=70364449406991`, verifies `gamma^4=b`, then computes `R_c=[4^{-1} mod r]Q_j+[c]T` and `phi(R_c)=gamma/(x(R_c)+gamma)`.

For each scanned candidate, the script checks all four channels for affine status, nonzero `x`, and `x != gamma`; it also rejects a duplicate subgroup point. It asserts `[4]R_c=Q_j` on every channel. [blind_counts.json](blind_counts.json) retains every scanned candidate, scalar, subgroup point, four raw points, four phi coordinates, admission decision, rejection reasons, and the full ordered natural-call schedule.

## Derived result

| Counter `j` | Scalar `k_j` | Decision |
| ---: | ---: | --- |
| 0 | 106919752671816517 | admitted, target 0 |
| 1 | 170711963231727215 | admitted, target 1 |
| 2 | 6718495876688090 | admitted, target 2 |
| 3 | 547768927640051783 | admitted, target 3 |
| 4 | 83989824178140575 | admitted, target 4 |
| 5 | 165121303974308139 | admitted, target 5 |
| 6 | 345861343518129524 | admitted, target 6 |
| 7 | 411739324728539494 | admitted, target 7 |

The scan stops after counter 7: eight distinct subgroup targets were admitted and zero candidates were rejected. Their 32 raw channel points are affine, have nonzero `x`, avoid `gamma`, and project under `[4]` to their corresponding subgroup points. The raw channels are distinct within each target.

## Discriminating controls

The same scalar function was run with only its domain separator changed to `ICPERF-k11-natural-v1-changed\0`. For each of the eight scanned counters, both the scalar and subgroup point differ from the frozen-domain result. At counter 0, for example, the changed scalar is `106430965579355307` instead of `106919752671816517`. The alternate results are recorded in `blind_counts.json` and are **control values**, not additions to the frozen target schedule. This checks that the derivation actually binds the stated domain bytes.

Because none of the naturally scanned candidates was rejected, I also exercised the same admission predicate on a **synthetic mutated candidate**. Starting from admitted counter 0, I replaced raw channel 0 with `T=[r]P_source`, a valid curve point whose `x=gamma` is the phi pole. The predicate rejected it with exactly `phi_pole` on channel 0. This deliberately corrupted channel is not a generated `R_0`, does not project to the source target, and is excluded from the eight-target schedule and call count. It tests rejection logic, not natural rejection frequency or a solver outcome.

The planned positive stage has **two** calls, ordered weighted then local random. Each of eight natural targets has four channels in each of two arms, giving `8 × 4 × 2 = 64` natural calls and **66 maximum planned calls** total. On even target indices, the arm order is weighted then local random; on odd indices it reverses. Each arm visits channels `0,1,2,3` in order. The natural stage remains conditional on both positive controls passing; admission, censoring, or an earlier stop can reduce actual calls. This derivation says nothing about solver outcomes or relations.

## Joint verdict and limits

**Holds for the assigned blind-derivation joint and the two controls:** the frozen statement and fixture yield a reproducible eight-target, four-channel schedule and its 66-call maximum; changing the domain changes the derived targets, and the admission predicate rejects a phi-pole channel. This is an independent predicted value to compare with producer artifacts after this report is frozen; it is not yet a comparison with them. The fixture's arithmetic claims beyond the checks listed here, formula generation, base tables, solver behavior, certificates, and measured costs are outside this joint.

No scientific solver trial was run. No scientific or goal status was changed.
