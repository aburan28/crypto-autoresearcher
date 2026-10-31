# SNFS observation cards — 2026-10-17

These cards present three patterns in saved data for the owner to inspect. They distinguish recorded values, derived arithmetic, possible explanations and proposed next measurements. They make no official scientific decision. The original records remain unchanged.

## 1. Rotation subsets: fixed m, changing density

**What stands out.** At fixed `m=4`, the rotation arm's sampled point density rises from 38.26% to 89.29% across the saved bit lengths. The hash and size arms remain near their nominal 6.25% density. The arms therefore sample markedly different subsets despite sharing `m`.

| c | Rotation: sampled point density | Hash: sampled point density | Size: sampled point density | Rotation: exact uniform-x density |
| --- | ---: | ---: | ---: | ---: |
| 13 | 38.264% | 6.103% | 6.498% | 38.103% |
| 17 | 46.407% | 6.323% | 6.345% | 46.589% |
| 19 | 50.561% | 6.258% | 6.175% | 50.388% |
| 31 | 68.119% | 6.208% | 6.169% | 68.134% |
| 61 | 89.292% | 6.262% | 6.160% | 89.464% |

Each sampled entry aggregates the saved `density_hits / density_n` over six seed/curve cells, 120,000 point draws per arm and `(c,m)`. These six-cell aggregates are descriptive. The plots also show cell min/max, which is spread, not a confidence interval. The size arm uses different matched-prime curves. No hypothesis test or significance label is assigned.

**Definition to inspect.** `rotmin(x)<2^(c-m)` accepts a representative if any cyclic rotation begins with `m` zero bits. It is a union over cyclic positions. At `m=1`, every representative `0<=x<2^c-1` has a zero bit and is accepted; all 30 saved rotation cells with `m=1` have sampled density 1.

**Derived reference.** Let `A_m` be the `m`-state automaton whose states are zero-run lengths `0,...,m-1`: a one returns to state zero; a zero advances unless it would complete an `m`-zero run. `trace(A_m^c)` counts indexed cyclic binary words avoiding that run. Since the all-ones word is excluded from `0<=x<2^c-1`, the number accepted is `2^c-trace(A_m^c)`. Dividing by `2^c-1` gives the exact uniform-x column. The derivation uses a unique trailing-zero state after each one; the all-zero word is outside the avoiding count. All 27 direct enumeration checks at `c=4,...,12`, `m=1,2,4` agree with the formula.

**Keep separate.** Point sampling weights x-coordinates by the curve equation and excludes `y=0` and O. The integer-reference column is not an exact point-density prediction. Original closure-ratio error bars omit density-estimation uncertainty and target clustering; these cards do not reinterpret them as significance tests.

**Proposed next measurement.** On the same finite curve populations, measure integer membership and point membership separately. Calibrate the control subsets to the measured rotation cardinality, using a calibration sample separate from the measurement sample and consistent O/`y=0` domains. Retain both the original nominal-density and calibrated-control tables. This is a proposed follow-up, not a rerun of the frozen grid.

Sources: `EXP-ECDLP-ad27ad / RUN-ECDLP-a5281a`, [derived table](rotation-density.csv), [formula checks](binary-count-checks.json), and the hash-pinned inputs in [observations.json](observations.json).

## 2. E3: a degree step and censored generic solvers

**What stands out.** Both generic encodings finish all nine degree-1 targets, but time out on every degree-2 target under the saved four-second wall cap. The geometry construction records explicit verified sections for six of the nine degree-2 targets.

| Historical pencil-map degree d | Unique targets | Raw encoding | Jet encoding | Geometry construction |
| --- | ---: | --- | --- | --- |
| 1 | 9 | 4 `sat`, 5 `unsat` | 4 `sat`, 5 `unsat` | 4 `sat`, 5 `unsat` |
| 2 | 9 | 9 timeouts | 9 timeouts | 6 `sat`, 3 `unsat` |

The table joins the actual saved target keys `(p,d,mode,trial)` across methods. There are 18 unique targets and 36 generic attempts, not 36 independent targets. Each degree includes two fresh and one planted target at each of `p=101,257,1021`. At degree 2, the six geometry successes comprise three planted and three fresh targets. At degree 1, the four comprise three planted and one fresh target. [Every target row](e3-target-outcomes.csv) is retained.

**References and limitations.** The geometry program reads the generic experiment's target rows and recovers the pencil base points from the supplied cubic, rather than receiving their coordinates. It searches a fixed catalog of line/conic classes. `unsat` is preserved as the producer's literal status and scoped to the relevant encoding/catalog; it is not a statement about unrestricted sections. All ten geometry `sat` records carry saved verification flags. These are imported historical finite controls, not new canonical E3 campaign runs. `d` here is the degree in that plane-pencil encoding, not the projective degree D in the newer Weierstrass encoder.

**Question worth inspecting.** Which phase produces the degree-2 wall-cap discontinuity: coefficient construction, Groebner computation, conversion/root recovery, or a combination? The timeout records do not contain phase markers, so these data cannot distinguish them. Raw has `3d+1` unknowns and jet has `2d+1` in the inspected source, including the saturation variable; both have the same saved timeout pattern at `d=2`.

**Proposed next measurement.** Freeze these exact 18 target instances; add externally persisted phase markers to a versioned driver; record coefficient counts/degrees, saturation, memory and censored phases for each encoding. Preserve the four-second results and use a separately declared schedule for additional observations. Recheck every returned section by substitution. Keep geometry-catalog membership and generic solver outcomes as separate columns.

Sources: imported `blind-results.json`, `geometry-results.json` and their source programs; exact paths and SHA-256 values are pinned in [observations.json](observations.json).

## 3. Field lifts: repeated concrete inputs in the control table

**What stands out.** The 1,395 saved rows partition into 966 distinct keys `(g,p,reduction root,A,B,seed)`. There are 169 repeated-key groups, accounting for 429 additional rows beyond one per key. Five keys occur ten times each. Every repeated-key group has identical saved work-rung profiles and sampled point lists.

| Multiplicity of a seed-inclusive key | Number of keys |
| ---: | ---: |
| 1 | 797 |
| 2 | 59 |
| 3 | 40 |
| 4 | 40 |
| 5 | 15 |
| 7 | 5 |
| 8 | 5 |
| 10 | 5 |

One ten-row example has `g=t^3+t-1`, `p=4111`, reduction root 16, `(A,B)=(-16,11)`, seed 3. Its ten zero-based raw row indices and labels are preserved in [repeat groups](field-lift-repeat-groups.json). Dropping seed from the key gives 962 distinct algebraic inputs; this distinction is retained rather than treating different seeds as identical attempts.

**Sampler structure to inspect.** The source makes a monic polynomial of degree d and weight w, chooses the constant sign, and chooses `w-2` interior signs/positions. Its coefficient support has at most `2^(w-1) * binomial(d-1,w-2)` members before irreducibility and prime filters. For `d=3,w=3`, that is eight. The random-field loop allows repeated draws and uses the first admissible prime for each chosen polynomial; curve seeds reuse the `(seed,shape,k)` key. This is a concrete construction feature visible in the source, not an inferred statistical dependence test.

**Keep separate.** The partition is by literal algebraic input and seed, not by number-field isomorphism. It does not prove independence or dependence of every other row, and it does not alter the original table's intended weighting. Original rows remain available. The rank-descent arm was skipped in the source run; sampled points and residue counts are not substituted for rank certificates.

**Proposed next measurement.** Record the sampler's finite support and draw multiplicities by shape/seed. Collect a separately labeled table with unique field/prime/curve inputs, then multiple search seeds per input. Present both row-weighted and input-grouped summaries with their distinct sampling definitions. This would make generator reuse and within-input variation directly inspectable.

Sources: `EXP-ECDLP-4c6a09 / RUN-ECDLP-e89532`; `implementation/src/main.rs`, functions `random_shape` and the field/curve construction loop; [all repeated-key groups](field-lift-repeat-groups.json).

## Provenance and status

`analyze_archived.py` reads four saved JSON inputs and computes deterministic summaries; no curve or solver program was rerun. It additionally calculates the exact binary-word reference and the 27 small enumeration checks. `observations.json` pins the input hashes and analysis source. G3/G4 producer/checker exit codes are zero, while their supervisor receipts retain `invalid_output` for legacy manifest format. The E3 inputs are imported finite-control records. These distinctions remain visible and no status is upgraded by this presentation.

No official scientific conclusion or hypothesis/goal status is changed. Canonical graphs and historical reports are unchanged; the figures here are new descriptive views with their own source and tables. KB retrieval was unavailable; citations point to the inspected saved artifacts and code, and no literature novelty assertion is made.
