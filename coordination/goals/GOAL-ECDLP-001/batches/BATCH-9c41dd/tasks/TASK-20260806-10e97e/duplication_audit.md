# DELIVERABLE ZERO — duplication audit, TASK-20260806-10e97e

Written **before** any proposal was drafted. Nothing below is a measurement.
This file records exactly which enumerations were executed, what they returned,
what coverage was achieved, and — one line each — what every committed proposal
in the seven target questions already covers. It also records every candidate
this session **dropped** because the audit found it already held.

Environment constraints that shaped the method, both inherited from the sibling
task's disclosure and both binding here:

- **No Bash tool.** `tools/allocate_id.py` could not be executed. ID allocation
  method and its provenance are recorded in §5 and in an
  `id_allocation_provenance` block inside every filed proposal.
- **`Glob` truncates at 100 results** and `ledger/proposals/` holds **262**
  files. Glob was therefore **not** used as the primary enumerator. `Grep` with
  `head_limit: 0` was, because it reports a total ("Found N total occurrences
  across M files") that makes truncation detectable rather than silent.

---

## 1. Enumerations executed, verbatim

| # | tool | pattern / glob | path | `head_limit` | returned |
|---|---|---|---|---|---|
| E1 | Grep (`count`) | `^\s*(id\|title\|class):` | `ledger/proposals` | 0 | **262 files**, 786 occurrences — the authoritative file count |
| E2 | Grep (`content`) | `^\s*question_id:\s*(RQ-ECDLP-002\|RQ-ICEX-001\|RQ-RELN-001\|RQ-SDEG-001\|RQ-MONO-001\|RQ-DREG-001\|RQ-SIG-001)\s*$` | `ledger/proposals` | 0 | **64 matching files** |
| E3 | Grep (`content`, `-A 9`) | `^\s*question_id:\s*RQ-ECDLP-002\s*$` | `ledger/proposals` | 0 | **34 files** with title/claim heads |
| E4 | Grep (`content`, `-A 8`) | the six satellite `question_id`s | `ledger/proposals` | 0 | **30 files** with title/claim heads |
| E5 | Grep (`content`) | `^\s*(id\|question_id\|title\|class\|novelty_status):` | `ledger/proposals`, glob `IDEA-20260806-*.yaml` | 0 | **5 files**, all `RQ-SSI-001` / `RQ-SSIQ-9702af` — none in scope |
| E6 | Glob | `ledger/proposals/IDEA-2026072*.yaml` | — | — | 39 files (chunked, under the 100 cap) |
| E7 | Glob | `ledger/proposals/IDEA-2026073*.yaml` | — | — | 19 files (chunked, under the 100 cap) |
| E8 | Glob | `ideas/catalogue-20260805/**` | — | — | 12 files (the 102-idea pre-ledger catalogue) |
| E9 | Grep (`files_with_matches`) | `Bernstein.?Lange\|non-uniform crack\|N\^\{1/3\}\|preprocessing frontier\|ST\^2\|cracks in the concrete` | repo root | 60 | 60 files (cap hit — see §4 caveat) |
| E10 | Grep (`files_with_matches`) | `preprocessing\|advice\|precomputation` | `knowledge/` | 40 | 40 files (cap hit — see §4 caveat) |
| E11 | Grep (`content`) | `[A-Z]{2,}-(\d{8}-)?(3b91c7\|7ea402\|c5d183\|20f6ab\|9d47e2)\b` | repo root | 10 | **0 matches** — token-freedom check |

Documents read in full during the audit: `AGENTS.md`, `CLAUDE.md`,
`agents/idea-generator.md`, `docs/inventor-protocol.md`,
`analysis/SSI-ECDLP-SYNTHESIS-20260803.md`, `knowledge/findings/KN-FIND-007.md`,
`knowledge/findings/KN-FIND-c41ea9.md`, `knowledge/findings/KN-FIND-002.md`,
`knowledge/techniques/KN-TECH-005.md`, `ledger/questions/RQ-ECDLP-002.yaml`,
`ledger/proposals/IDEA-20260805-1f4a11.yaml` (schema exemplar),
`ledger/proposals/IDEA-20260805-c06631.yaml` (first 120 lines),
`ideas/catalogue-20260805/INDEX.md`, `.../SCREENING.md`,
`.../A1-index-calculus.md`, `.../A3-representations.md`,
`.../A4-transfers-lattice.md`, and `.../A2-solving-degree.md` by section headers.

## 2. Achieved coverage, numerically

- `ledger/proposals/` total files: **262**. Enumerated by E1 with the total
  reported, so truncation is excluded. **Coverage of the proposal directory:
  262 / 262 = 100%.**
- Proposals in the seven target questions: **64** (E2, `head_limit: 0`, total
  reported). Split: **RQ-ECDLP-002 34**, RQ-ICEX-001 6, RQ-RELN-001 6,
  RQ-DREG-001 6, RQ-SDEG-001 4, RQ-MONO-001 4, RQ-SIG-001 4.
  The 34 matches the handoff's stated count exactly; the satellites total 30,
  matching the handoff's "~30 more". **Coverage of the target questions:
  64 / 64 = 100%**, at the granularity of `id + title/claim head`.
- Depth caveat, stated rather than hidden: 64/64 were enumerated and their
  titles read; **6 were read in full or near-full**
  (`IDEA-20260805-1f4a11`, `IDEA-20260805-c06631`, `IDEA-20260731-013`
  partially, plus `IDEA-20260802-002` by targeted grep, and the two named in
  `discriminated_from` blocks below). Every `discriminated_from` claim I file
  names a proposal whose title I read and, where the claim is load-bearing,
  whose body I opened. Where I could only read the title I say so in that
  proposal's `discriminated_from`.
- Pre-ledger catalogue `ideas/catalogue-20260805/`: **102 entries** across nine
  slices; the four ECDLP slices (**47 entries**: A1 13, A2 12, A3 11, A4 11)
  were read — A1, A3, A4 in full, A2 by entry headers. This catalogue mints no
  identifiers, and its own `SCREENING.md` records **0/102 unanimous survivors**;
  it is nonetheless prior art for duplication purposes and is used as such below.

## 3. One line per committed proposal in the target questions

### RQ-ECDLP-002 (34)

| id | what it already covers |
|---|---|
| `IDEA-20260725-006` | Correction to the degree-4 TTN witness at `p=101`: three curve cells carry three different normalized witnesses sharing a 27-position zero mask and four fixed rational values. |
| `IDEA-20260725-007` | Ensemble over re-seeded column-matched constructions to separate three explanations of the `extra_5` support-bias pair (369/909 at `n=9`, 0/1321 at `n=12`). |
| `IDEA-20260727-001` | Orbit-quotient and rank control for `H-STR-002`: does the `phi`-invariant displacement-rank result exceed the published automorphism factor-base reduction, and is `alpha` taken on a solvable matrix. |
| `IDEA-20260727-002` | Yield-charged descent cost: is the `H-IC-001` multi-target crossover an artifact of charging one Gröbner call on a trivial ideal at fixed `B=14`. |
| `IDEA-20260727-003` | Free-oracle admissibility frontier `F(beta,m) = max(B, c_LA·B^{omega})` — the relation-count and linear-algebra floor before any decomposition cost is charged. |
| `IDEA-20260727-004` | Simulation-overhead budget: a `SIMULABLE` verdict closes at exponent 1/2 only when `C_sim = N^{o(1)}`; otherwise the floor is `c·sqrt(N)/C_sim`. |
| `IDEA-20260727-005` | Exit-map classification barrier: every efficiently computable algebraic homomorphism out of a prime-order prime-field subgroup lands in one of three classes, each with exponent >= 1/2; self-maps exponent-neutral. |
| `IDEA-20260727-006` | Equidistribution-resolution gap: the factor-base size at which Weil error terms can certify Semaev yield exceeds, at every arity, the largest base at which index calculus could beat rho. |
| `IDEA-20260727-007` | Arity-five membership budget: the `alpha < 3/2` decomposition-query gate derived from the free-oracle floor, with `alpha` pre-registered on the successful-decomposition subset. |
| `IDEA-20260727-008` | Endomorphism-rank cost curve: adding endomorphisms to the witness lattice shrinks the Minkowski minimum, leaves the search exponent at 1/2, inflates the constant. |
| `IDEA-20260731-007` | Degree-split Semaev claw: meet-in-the-middle smoothness splitting of the membership search, `O~(B^{m/2}·u^{-u})` under `HEUR-DS-1`. |
| `IDEA-20260731-008` | Isogeny-transfer cost gate: charged `C_path(ell) + C_special(E'',N)`; generic `E` has `C_path >= 0.886 sqrt(N)` under `HEUR-ISO-1`. |
| `IDEA-20260731-009` | Crypto-size first-fall-degree correspondence: sample Semaev-shaped multihomogeneous systems without building a curve, `HEUR-FF-1`, KS distance 0.1. |
| `IDEA-20260731-010` | Shared-factor-base multi-target amortization: `C = C_rel + C_LA + T·C_desc`, break-even `T*` against `T·0.886 sqrt(N)`. |
| `IDEA-20260731-011` | Structure-destruction null control: any claimed sub-birthday speedup must vanish on a same-shape null object that preserves sizes and destroys the exploited structure. |
| `IDEA-20260731-012` | Large-prime variation: near-miss harvest over a shifted `(m-1)`-sumset with a public large-prime pool `L` and shared-large-prime relation combining. |
| `IDEA-20260731-013` | Shared distinguished-point table for `T`-target rho: measures the multi-target **generic baseline** `gamma` (independent runs `gamma=1` vs batch `gamma=1/2`). |
| `IDEA-20260731-014` | Solving-path re-randomization: is min-over-randomized-presentations Gröbner cost Semaev structure or a generic distributional artifact. |
| `IDEA-20260731-015` | Public-scalar factor base `F = {s_i P}` with public `s_i`: relation collection and linear algebra removable by construction; the standing `alpha < 3/2` gate belongs to a dominated variant. |
| `IDEA-20260801-003` | Governance gate: every sub-rho claim must first exhibit a closed-form charged target-descent-tree certificate including tree construction. |
| `IDEA-20260801-021` | Bezout obstruction `|F_p| <= 3 d_p` for a degree-`d_p` algebraic predicate; `|F_p| <= Delta_p` for any proper locus of finite intersection degree; charged-trial lower bound `Omega(N/B^m)`. |
| `IDEA-20260802-001` | Saddle-point smoothness reference: repairs the absolute Dickman reference every conditional exponent multiplies, and asks whether the measured departure is the reference or the sampler. |
| `IDEA-20260802-002` | Tracked-object enumeration with an **executable one-step propagation meter** `(L, b)`; twelve pre-registered projections; discharges `KN-OPEN-019` to a closure or a per-candidate obstruction. |
| `IDEA-20260802-003` | Enumerate-and-join exponent pinned at 1/2 identically in arity; the remaining escape is box-constrained small-root solving with feasibility curve `X_max(m,p,t)`. |
| `IDEA-20260802-004` | Crypto-scale validation of `HEUR-DS-1` **is** feasible: full factorization of Semaev intermediates at a 256-bit public curve, with the encoding choice exposed as the feasibility knob. |
| `IDEA-20260802-005` | Orbit-representative cost gate: a group action of order `r` buys `sqrt(r)` and costs `r`; decides `H-ENDO-001` cheaply in both directions. |
| `IDEA-20260802-006` | The **scalar index set** as tracked object: normalized additive-character bias `Bias(K)` of `{x(kP) : k in K}` for `K` a multiplicative coset. |
| `IDEA-20260802-007` | Shared charged-unit accounting layer with a planted-bug positive control and mandatory matched frontiers; retires wall clock as a decision variable. |
| `IDEA-20260803-e2f5bd` | Composes the Bezout bound with the arity threshold into a **description-degree window**, with `theta*(m)` and the quadratic-residue base as the null object showing where it does not reach. |
| `IDEA-20260805-1f4a11` | BKK-speedup trichotomy: the half-space membership vector `eps` as a forced-value object (`gamma_m = (m+1)/2^m` exactly), plus an Amdahl ceiling `1/(1-s) ~ 2x` end-to-end and the `o(1)` `c`-accounting. |
| `IDEA-20260805-38aebb` | Vertical isogeny volcano conserves (class number) x (short-endomorphism density); converts two undefended deferrals into one argued obstruction with a named residual. |
| `IDEA-20260805-6a14e3` | Object-class / unit / scale type-check of every declared feed edge in the `GOAL-PATH-001` dependency graph; DREG appears in zero of the three ICEX feed bindings. |
| `IDEA-20260805-c4f675` | The `H-PSEUDO` character-sum constant divided by its own extreme-value null; residual growth 0.004 rather than 0.079. |
| `IDEA-20260805-cc4c2c` | Graded calibration ladder for the transfer gate: embedding degree `k` supplies five interior points with forced costs; crossover `k*(p)` derivable at zero compute. |

### RQ-ICEX-001 (6)

| id | what it already covers |
|---|---|
| `IDEA-20260803-fa9839` | The **arity threshold**: closed-form, zero-compute statement of how cheap the decomposition oracle must be, per arity `m`, for point-decomposition index calculus to beat rho, gated on reproducing a known extension-field exponent. (Being frozen as `EXP-ICEX-146ff5` by `TASK-20260806-cd81c5`.) |
| `IDEA-20260805-bb4488` | `alpha = log C / log ell` is not identifiable: a constant-factor bias `log kappa / log ell` invisible to the replica CI; rho itself passes the "CI entirely below 1/2" predicate at every sealed toy cell. |
| `IDEA-20260805-c8524f` | The frozen ICEX exponent observable is a ratio, not a slope; applying the frozen estimator to the matched rho control returns a tight CI **excluding** 1/2 for an algorithm whose true exponent is 1/2. |
| `IDEA-20260805-c06631` | Per-coordinate baseline table: rho memory exponent **0**, BSGS full cost **2/3**, rho area-time **1**; replace the constant 1/2 threshold with a matched one. Rho's group-operation exponent is asserted **1/2 at every `theta`**. |
| `IDEA-20260805-45bf55` | A fixed attempt cap drives the measured exponent to 0 or 1 depending on the aggregate charged; `TIMEOUT_CENSORED` is named with no censoring fraction, survival estimator or attempts-per-replica pin. |
| `IDEA-20260805-4d31bc` | Report the crossover order `log ell*` rather than the exponent; it is a ratio of regression coefficients whose honest interval is a Fieller set, unbounded in 95% of replications when the slopes are indistinguishable. |

### RQ-RELN-001 (6)

| id | what it already covers |
|---|---|
| `IDEA-20260805-44bc0b` | The bounded-degree no-go turns on the coverage exponent `chi = m·log(Delta)/log(N)`; NFS and Gaudry-Diem both sit at `chi = 1` exactly — the nearby-object control `KN-OPEN-020` never had. |
| `IDEA-20260805-4ddd8c` | RELN's primary metric `p_exist(B)` is pinned by counting and cannot fail; the one free parameter is the normalized collision ratio `Xi`, exactly `1 - 1/M` for a random base. |
| `IDEA-20260805-5ac0a2` | The frozen reference curve is off by a derivable factor `2^m`: exact-counting audit of `HEUR-SEMAEV-2015-4.3` as transcribed into the protocol. |
| `IDEA-20260805-061f97` | Relations needed is not `B`: the left-kernel threshold is the fixed point of `x = 1 - e^{-mx}`, and the deviation of the touched-column curve from it is the program's first relation-independence measurement. |
| `IDEA-20260805-96cb3d` | The solve gap is zero by construction at every primary ladder cell; the complete fix-`(m-1)`-and-root-find baseline turns `p_solve` into a measurement of the solver. |
| `IDEA-20260805-a25f11` | Only the collision deficit is free: exact ceiling on `P(decomp)` at fixed `B`, derived threshold `B > (N/2)^{1/3}` below which the best base is worse than random, and a graded **additive-energy** census. |

### RQ-SDEG-001 (4)

| id | what it already covers |
|---|---|
| `IDEA-20260803-202a15` | One closed form for the `D6` below-freeze collapse that must predict **both** committed `n=12` deficits (7,110 and 17,947), or a named no-go condemning `d_reg` cost predictions at `D >= 6`. |
| `IDEA-20260805-83344d` | The `HEUR-DS-1` comparator is a discretization residue, not the Dickman function; `rho(u*)` as tracked object; extending the ladder to 28/32 bits converts a 3/3 FAIL into a spurious PASS. |
| `IDEA-20260805-2afd22` | Certificate-backed cost model certifying `1/m!` of its own cost; the decomposition certificate as tracked object plus a Nullstellensatz certificate for failed attempts already inside the solver's linear algebra. |
| `IDEA-20260805-decb14` | A cross-implementation smoothness comparator register the corpus already contains and never pointed at its own broken Dickman table, plus the exact fixed-`B` correction it makes unavoidable. |

### RQ-MONO-001 (4)

| id | what it already covers |
|---|---|
| `IDEA-20260803-ff7415` | Decides `KN-FIND-c41ea9`'s own untaken clause: is `2^{n-1}` split-compounding over `F_{q^n}` an exponent lever or a double count against the `1/n!` conservation identity. |
| `IDEA-20260805-a9a95d` | The relation-rate half of `KN-OPEN-009` is a Fourier identity, not monodromy: "deviant relation rates" become the normalized character bias of the factor base; exceptional-locus hunt moves from curves to factor bases. |
| `IDEA-20260805-cf2d5a` | The summation cover is a 2-Kummer cover: geometric monodromy is `(Z/2)^{m-2}` at every `m`, so `KN-OPEN-009`'s "full symmetric/wreath" premise is false and the `m >= 4` census becomes unnecessary. |
| `IDEA-20260805-90df50` | The one Galois-flavoured statistic not identically trivial on the factor-base sublocus: root-coincidence rate of the summation fibre, forced value `6(tau-1)/N` at `m=4`, driven by rational 2-torsion. |

### RQ-DREG-001 (6)

| id | what it already covers |
|---|---|
| `IDEA-20260801-002` | Direct `d_reg(n)` measurement without a Gröbner solve: pivot-degree Hilbert function by exact row-echelonization of the full-column Macaulay-like matrix at each degree, chained boolean Semaev `m=3, t=3`. |
| `IDEA-20260805-2dc8de` | The decision variable is unnormalised: RQ-DREG-001's departure criterion and every scale-free version of the same committed data point in opposite directions; the raw deficit is not even monotone. |
| `IDEA-20260805-90a841` | Block-incidence column law: a closed form for the boolean chained-Semaev `t=3` Macaulay support gap reproducing every committed column count at zero compute; retires the support-gap quarantine analytically. |
| `IDEA-20260805-61f7f4` | Zero-compute discriminating-power map over `(n, D, u_D)`: at `D=6`, `n in {10..13}`, every cell with `u_6` below `h_6` makes all three frozen collapse candidates predict the identical rank. |
| `IDEA-20260805-f49efb` | The block-matched null: DREG has never run its signal against a null of the same shape, and its two existing nulls disagree by 7,110 at the single decisive cell. |
| `IDEA-20260805-e732ed` | Audit of the `2^1194` crypto-scale headline: it is `N(966,150)^2` at `omega = 2` with no memory charged and assumes a genericity the chained system's block structure violates. |

### RQ-SIG-001 (4)

| id | what it already covers |
|---|---|
| `IDEA-20260805-8a68d3` | Plant a syzygy family of known size: the instrument behind ten evidence records has never been shown able to detect the quantity it reports. |
| `IDEA-20260805-d38a8c` | Leverage, not count: normalise the non-rewritable cascade by the gap it would have to close and decide the goal on a decay law needing no `D >= 6` null baseline. |
| `IDEA-20260805-bbfca9` | The trivial-syzygy family is enumerated with polynomial-ring degree arithmetic inside a boolean ring; repair the subtraction instead of rebuilding the null. |
| `IDEA-20260805-0d2a21` | The goal says prime-field decomposition cost and every measurement is a boolean Weil-descent system; state the `F_p` analogue exactly and run the smallest cell where the answer can differ. |

## 4. Candidates DROPPED because the audit found them already held

Dropping is the success mode of this step. Nine candidates were generated and
killed before drafting; each is recorded with the record that holds it.

| # | candidate object / claim | held by | verdict |
|---|---|---|---|
| D1 | Second moment of `c_D(r)`: coverage `>= (mean)^2/E[c^2]` makes the **additive energy** of the factor base the exact second-order design variable that `KN-FIND-007` leaves open. | `IDEA-20260805-a25f11` (RELN) — exact ceiling on `P(decomp)` at fixed `B` plus a graded additive-energy census | **DROP.** Same object (additive energy), same direction (a ceiling on decomposition probability). |
| D2 | Cheap-collision / free-homogeneous-relation supply as the complement of coverage; Sidon base has maximal coverage and zero free relations. | catalogue `A1-6` (`ideas/catalogue-20260805/A1-index-calculus.md`), exact identity `Sigma (c_D(r)-1)^+ = C(B+m-1,m) - |mD|` | **DROP.** Identical identity and identical dichotomy. |
| D3 | Enumeration dependency: consecutive `(m-1)`-tuple trials share `m-2` summands, so the effective trial count is `|(m-1)F|`, not `B^{m-1}`. | catalogue `A1-6` again (sumset size is the same quantity) | **DROP.** Restatement of D2 in walk language. |
| D4 | Coupon-collector correction: relations needed is `Theta((B/m) log B)`, not `B`. | catalogue `A1-8`; committed `IDEA-20260805-061f97` (left-kernel fixed point `x = 1-e^{-mx}`) | **DROP.** Both hold it, and `061f97` holds the sharper form. |
| D5 | Quadratic-character word `chi(x(R) - x(P_i))` / chord-discriminant character as a two-step multiplicative statistic. | **Screen 2** (`KN-FIND-c41ea9`) kills it outright: `disc_T S_3 = 16 f(x1) f(x2)` and `chi(f(x)) = +1` on every rational point, so the statistic is identically `+1` on the factor-base locus. | **DROP — screened, not merely duplicated.** Recorded because it is exactly the class the standing screen exists to catch. |
| D6 | Degree-`d` fibration of `E` used as a collision-space compressor (`sqrt(d)` gain from a `d`-to-1 map). | `IDEA-20260802-005` ("an action of order `r` buys `sqrt(r)` and costs `r`") + catalogue `A3-7` (degree is set by `d_iota`, not the model) | **DROP.** The general statement is the automorphism-quotient statement already filed. |
| D7 | Base-change `E/F_p -> E/F_{p^n}` to import Gaudry-Diem: the base field does not shrink, so `e = 2 - 2/g >= 1`. | catalogue `A4-4` (the base-field-shrinkage identity `e(n,g) = (2-2/g)/n`, forcing `e(1,g) >= 1`) | **DROP.** Identical identity, identical conclusion, with a better nearby-object control (`n=3`) than mine. |
| D8 | Generic-transport null: rerun every claimed cost measurement with the curve replaced by `Z/N` under a random relabelling. | `IDEA-20260731-011` (structure-destruction null control) | **DROP.** Same control, already committed. |
| D9 | Structured-GGM `delta`-mass screen (`Omega(min(sqrt N, 1/delta))`) applied to corpus representations. | catalogue `A3-1`; and blocked at source — `KN-LIT-7606`'s body is recorded unread and eprint is unreachable | **DROP.** Held, and its blocking step is unexecutable here. |

One further candidate, **the CM/norm-form lens** (`O`-ball factor bases via
`End(E)`, additive MITM in `O` mod `(pi)`), was worked through and found to
reproduce catalogue `A1-2`'s algebra-free meet-in-the-middle exponent exactly,
by the conservation identity. It is **not** filed as a standalone proposal; its
only non-duplicative residue — that multiplicative structure in `O` is unusable
because class membership cannot be tested without the answer — is carried as
forward guidance inside `IDEA-20260806-c5d183`.

**Caveats on this audit, stated rather than hidden.** E9 and E10 hit their
`head_limit` caps (60 and 40 files). They were scouting greps for the
preprocessing/advice literature, not the duplication enumeration, and their caps
therefore do **not** affect the 262/262 or 64/64 coverage figures. But they mean
my statement in `IDEA-20260806-3b91c7` that the corpus holds no **achievability**
row for the preprocessing frontier rests on: `KN-TECH-005` read in full (it
states the lower bound `S*T^2 = Omega~(n)` and no upper bound), catalogue
`A1-4`/`A1-13` read in full (both cite the frontier as a **bound**, and `A1-13`'s
row list contains no achievable preprocessing algorithm), and
`IDEA-20260805-c06631` read to line 120 (its rho rows assert group-operation
exponent `1/2` at every storage parameter `theta`). It does **not** rest on an
exhaustive sweep of `knowledge/`, and a red team should re-run E10 uncapped.

## 5. Identifier allocation provenance

`tools/allocate_id.py` is **not executable in this session** (no Bash tool).
Method actually used, and it is the property `AGENTS.md` rule 14 protects:

1. Five 6-hex tokens were chosen **without scanning committed state for a
   maximum, a next free number, or any existing token** —
   `3b91c7`, `7ea402`, `c5d183`, `20f6ab`, `9d47e2`.
2. Each was then *verified free*, not *derived from state*, by E11:
   `Grep` for `[A-Z]{2,}-(\d{8}-)?(3b91c7|7ea402|c5d183|20f6ab|9d47e2)\b`
   across the whole repository returned **0 matches**.
3. A broad substring grep for the five tokens returned only sha256 fragments
   inside `inputs/archive_from_autolab/*/file_manifest.jsonl` and one
   `experiments/EXP-SSIQ-4de240` raw result — none is an identifier.

Every filed proposal carries an `id_allocation_provenance` block stating this.
**The Coordinator must run `python3 tools/allocate_id.py --check` on all five
before the snapshot commit**; if any collides, the proposal is superseded under a
new id rather than renamed (`AGENTS.md` rule 15).
