# Observation-collision audit — `EXP-SEMBIN-4fa22c`

**Task** `TASK-20260916-fc72a6` (executor)
**Audit** the `proof_search_map.observation_collision_search` of
`experiments/EXP-SEMBIN-4fa22c/specification.yaml`, whose status field reads
*REQUIRED BEFORE THE FIRST RUN and not yet performed*
**Goal** `GOAL-SEMBIN-fcb7a2` · **Batch** `BATCH-cbb416` · **Hypothesis** `H-SEMBIN-a7e721`
**Performed** 2026-09-16 · **Runs performed** 0 · **Measurements performed** 0
**Repository commit read** `de6c804682fe138a63e4c9cb4d2c224c4c42430d`
(branch `cursor/semaev-2015-audit-program-5b8b`)

Machine-readable companions: `searches.json` (63 queries, every one recorded,
including the four that returned nothing) and `verdict.json`.

**Everything in this report is an observation or a recommendation. It rules on
nothing.** Whether `EXP-SEMBIN-4fa22c` proceeds, is reframed, or stops is a
Coordinator decision; this task produces the input to it.

---

## Inference provenance

| field | value |
|---|---|
| `requested_policy` | `executor-implementation` |
| `resolved_model_id` | `claude-opus-4-5` (self-reported by this session; see below) |
| `fallback_used` | `true` |
| `fallback_reason` | No adapter backend is credentialed in this checkout. The runtime-native binding permitted by core rule 16 is the only route. `DEC-20260916-7b2235` records the finding and its standing condition; the contract's `inference.fallback_allowed` is `true` and the dispatch card declares it up front. |
| `degraded_allowed` | `false` |
| `model_verified` | `false` — `python3 -m orchestration.adapter doctor --probe` has no usable backend here. The identifier above is **unverified configuration, self-reported**, not an established fact, and no verified identifier has been invented in its place. |
| `independent_session_required` | `false` |

---

## Bottom line (a recommendation, not a ruling)

**`collision: partial`. Recommended disposition: `proceed`, with two reframings
the Coordinator may wish to impose.**

Three findings carry the verdict.

1. **No measurement of this contract's quantity on this contract's object
   exists.** Nothing in the tree measures a fake first fall degree `d'_F` — under
   Nagao's Definition 6 as the contract's `declared_conventions` make it precise —
   for a **coset-shifted EQS4** descent. The reason is structural rather than
   accidental, and it is the single most useful thing this audit found: **the
   program's shared Semaev/Weil-descent builder cannot construct a shifted
   instance at all.** `src/semaev_tree.py` contains no `coset`, `shift`, `v_i` or
   `offset` anywhere (query `T-04`, **empty result**), and its `make_V_subspace`
   returns the F₂-span of `{1, α, …, α^{k-1}}` — a subspace through the origin.
   Every descent this program has ever built from it is `v = 0`, which is
   **EQS2 in Nagao's own terminology** (Definition 4, `paper_fulltext.md:264-265`,
   "taking v1 = … = vN = 0"). DC-3 is therefore untouched by prior work, and
   `A-SHIFTED` is genuinely new.

2. **The contract's *control* arm is substantially pre-measured, and its
   instrument has been built twice before.** The same builder produces EQS1→EQS2
   — the chained S₃ system and its Weil descent — and at least two instruments in
   this program have run a Boolean-ring Macaulay first-fall scan over it at `n`
   values that overlap the contract's 7–12 range. This is the `partial` in the
   verdict. It is not a replication of the headline, but a Coordinator ruling that
   says "proceed, fully novel" would overstate it.

3. **Nothing contradicts `H-SEMBIN-a7e721`, and the goal record has already
   explained why nothing can.** `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`
   objective (2) states, before this audit ran, that *"GOAL-DREG-001's
   Macaulay-rank measurements … and every internal record that says 'first fall
   degree' are all silent about which of the two they mean. Until the map is
   stated, an internal degree measurement cannot be read as bearing on any Nagao
   or Semaev assumption in either direction."* This audit is an independent
   confirmation of that claim from the instrument side: every candidate it found
   uses a fall criterion that is **definably different** from the contract's, and
   none of them declares which of Definition 5 and Definition 6 it computes.

**The two reframings worth considering.** (a) The contract's `A-UNSHIFTED` arm
should be framed as a *replication with a changed instrument* rather than as
fresh measurement, and its result compared against the prior EQS2 records named
below — that comparison is free and is a control on the new instrument that the
contract does not currently have. (b) `C-3`'s known-answer fixture could cheaply
be widened to include one prior EQS2 instance, which would convert "two campaigns
measured nearby things" into "the new instrument agrees with the old one where
they overlap, and differs exactly where the definitions differ". Both are
additive; neither edits the frozen protocol, and imposing either is the
Coordinator's call.

---

## The yardstick: what makes a hit a collision

A hit is a collision only if it measures **the same quantity on a comparable
object**. From `experiments/EXP-SEMBIN-4fa22c/specification.yaml`
(`declared_conventions`, `instance_specification`, `metrics`) the contract's
quantity is pinned by five properties. Every candidate below is scored against
exactly these.

| # | property | the contract's choice |
|---|---|---|
| **P1** | **which degree** | the **FAKE** `d'_F`, computed in the Boolean ring where `X² ≡ X`. Not the true `d_F` (Definition 5), not `d_F4`, not `d_reg`, not a solving degree. |
| **P2** | **what counts as a fall** | the **equality form** of condition (1): a combination `Σ hᵢfᵢ` whose degree is **strictly less than `maxᵢ deg(hᵢfᵢ)`**, with all products at the same degree `d`. Any degree drop — not a drop to linear, and not a rank defect against a generic expectation. |
| **P3** | **trivial Koszul falls** | **excluded**, and the exclusion is itself **measured** as `M-2`, so the margin `M-2 − M-1` is visible. An instrument that admits them reads the ceiling (the literal true `d_F` of any cubic system with the field equations at `p = 2` is ≤ 5). |
| **P4** | **the object** | the **coset-shifted** degree-3 Weil descent of the third summation polynomial over `F_{2^n}`, `m = 3`, `n ∈ 7…12`, with the `v_i` of Definition 8 recorded as explicit field elements (DC-3), generators the **reduced multilinear** degree-3 descents (DC-4). |
| **P5** | **what is emitted** | `M-1` (one integer), `M-2` (the trivial ceiling), **`M-3` the full rank series per degree**, `M-4` shape + sha256, `M-5` cost — with `M-1` re-derivable from `M-3` without re-running the algebra. |

P2 is the property most hits fail, and it fails silently: four different
definitions in this repository are all called "first fall degree".

---

## Method, and the limit on it

**The kb retrieval index — the instrument this audit was supposed to use — could
not be called.** `AGENTS.md`'s knowledge-retrieval policy names `search_knowledge`
as the thing to run before "proposing an experiment likely to duplicate earlier
work", and the contract's own `proof_search_map` names it too. Six independent
probes (`P-01`…`P-06`, recorded in `searches.json`) establish it is unavailable:
no `crypto-kb` MCP namespace is exposed to this session, `kb/.venv` does not
exist, `kb/.env` does not exist, `uv` is not installed, nothing answers at the
configured `http://localhost:6333`, and neither `qdrant_client` nor `crypto_kb`
imports. I verified this rather than taking the brief's word for it.

What was run instead: 63 recorded queries — 36 broad screens, 20 targeted
queries, 7 availability probes — over the 76,056 files under `knowledge/`,
`ledger/`, `experiments/`, `coordination/`, `docs/` and `inputs/`, with
`--no-ignore-vcs` so generated artifacts were searched rather than skipped.
Every query is in `searches.json` with its exact command, complete hit count and
hit list; the four that returned nothing (`T-04`, `T-10`, `T-11`, `T-15`) are
recorded as empty and three of them are load-bearing.

**What this costs the recall claim, stated as `AGENTS.md` requires.** This report
states a **recall floor**, never a clean bill of novelty. Absence of a hit is not
evidence that nothing was tried. Three losses are specific and unrecoverable by
grep: (1) the index retrieves on *meaning*, so a record that measured this
quantity while calling it a "solving degree", a "step degree", a "rank defect" or
a "degree drop" is reachable by the index and reachable here only if I guessed
the wording — I widened the query set for exactly this reason and it is still a
guess-list; (2) the index covers staged corpus material beyond this checkout,
which this search cannot see at all; (3) the index ranks and resolves exact
identifiers first, whereas a tree search returns a flat list, which is why
several screens below return thousands of files and are labelled screens rather
than findings. Re-running this audit against a live index would be cheap and
would raise the floor.

---

## Candidates

Ordered by closeness. Every near-miss has its difference named.

### C-1 — `EXP-DREG-001`, the `d_ff` ladder on the Semaev arm — **closest measurement, NOT a collision**

**What it is.** `experiments/EXP-DREG-001/DREG_dff.sage` measures `d_ff` for "the
boolean chained Semaev m=3 system (sem arm) and the T11 support-matched null
(null arm)", `max_D = 6`, ≥ 8 targets per `n`. Runs
`RUN-DREG-001-DFF-N12-SEM{,-b,-c}` exist at `n = 12`, inside the contract's `n`
range, with `nb = 24` Boolean variables and an equation-degree histogram of
degrees 2 and 3. It has a matched null arm, which is the same shape as the
contract's `C-2`.

**Scored against the yardstick.**

- **P1 — matches.** It is a Boolean-ring computation (`X² ≡ X` via monomials as
  frozensets), so it is a *fake*-side quantity.
- **P2 — FAILS, and this is the decisive difference.** Its fall criterion is the
  first `D` at which the echelonised row space **contains a polynomial of degree
  ≤ 1** (`deg_le1_cols`, `DREG_dff.sage:80-86`). The contract's `M-1` fires on
  **any** degree drop below `maxᵢ deg(hᵢfᵢ)`. "A linear polynomial appears" is a
  strictly stronger event than "the degree dropped", so this is a different
  quantity and, where both are defined, it is weakly the larger of the two. Two
  numbers that are not the same number cannot collide.
- **P3 — FAILS.** No trivial-Koszul exclusion and no `M-2` analogue. Zero rows are
  skipped, which incidentally discards the `fⱼfₖ + fₖfⱼ` syzygies, but the Koszul
  submodule is never projected out and the trivial fall degree is never reported,
  so the margin the contract exists to show is absent.
- **P4 — FAILS on the shifts, and on the system.** Built from
  `h012_peel_rank.build_system`, which sits on the shared `semaev_tree` builder:
  **no coset shifts anywhere** (`T-04`, empty), so this is EQS2, not EQS4. The
  system is also the *chained* two-equation system with an auxiliary variable
  `u₁` ranging over the full field plus three `x` variables confined to `V`
  (24 Booleans at `n = 12`), where the contract's object is a single S₃ descent in
  three point-coordinates all confined to `V + vᵢ` (12 Booleans at `n = 12`).
- **P5 — FAILS.** Returns `(d_ff, n_rows, n_cols)` at the falling degree only. No
  rank series, so `M-1` is not re-derivable from it.

**Evidential status, which is weaker than it looks.**
`RUN-DREG-001-DFF-N12-SEM` and `-b` are both `failed_infrastructure`,
`valid: false`, "exit code 1". `-c` is `censored_timeout` with `valid: null` and
only two of eight targets resolved. **No `EV-DREG-*` evidence record mentions a
first fall or `d_ff` at all** (`T-11`, empty result) — the `d_ff` ladder is a
declared *secondary* metric of `EXP-DREG-001` that was never promoted into
evidence. And the prior recorded in the manifest's `expected.prior` field points
at a result artifact, `h012/ic_first_fall_t3`, **which does not exist in this
checkout** (`T-10`, empty result): the only surviving trace of that earlier
series is an unsourced sentence in a manifest field.

Measured values do exist in `-c`'s `raw-result.json`. They are cited rather than
restated here; see `verdict.json → values_disclosed_deliberately` for the one
numeric relation I judged load-bearing enough to disclose deliberately, and
`experiments/EXP-DREG-001/runs/RUN-DREG-001-DFF-N12-SEM-c/raw-result.json` for
the integers themselves.

### C-2 — `EXP-SIG-007/src/ic_first_fall_fast.py` — the same quantity as C-1, in its original form

**What it is.** The instrument C-1 was reimplemented from
("monoset-native copy of `ic_first_fall_fast.first_fall_degree`"). Its docstring
is unusually clear about what it computes: the degree-≤`D` Boolean Macaulay
matrix over GF(2), row-reduced, "the first degree `D` at which a *linear*
(degree ≤ 1) polynomial appears in the row space. That `D` is the FIRST-FALL
DEGREE `d_ff` — exactly the quantity the Petit–Quisquater conjecture claims stays
bounded as `n` grows." Its `main()` builds the object directly:
`build_chained_system_symbolic(t, …)` then `weil_descend_to_F2(polys, n, k, α, Rh)`
with `k = ⌈n/t⌉`, over `n ∈ 8…18`, `t = 3`.

**Difference named.** Identical to C-1's, because it is the same algorithm: P1
matches, **P2 fails** (fall-to-linear, not any degree drop), **P3 fails** (no
Koszul exclusion, no `M-2`), **P4 fails** (`v = 0`, EQS2; chained system with the
auxiliary variable), **P5 fails** (no rank series). One addition: the quantity is
explicitly framed against the **Petit–Quisquater** conjecture, not against
Nagao's Definition 6, and the contract's whole point is that those framings are
about different numbers until someone states the map.

**Validation status.** `EXP-SIG-007` holds six `completed_valid` runs, but they
are for that experiment's own subject — an `n = 21` residual-5 / rank-deficit
measurement. `ic_first_fall_fast.py` is carried in its `src/` as part of a pinned,
hash-recorded source bundle, **not** as the metric instrument those runs
validated. So: the file is committed and hashed, and it is **not** validated as a
first-fall instrument by any run record I found.

### C-3 — `EXP-ECTD-9e4248/driver/reused/macaulay.py` — a validated Macaulay instrument, for a different quantity in a different characteristic

**What it computes.** Its docstring gives the frozen operational definition:
build `M_D` from generators `{S3(x1,x2,x_R), g(x1), g(x2)}` over **`F_p`**, rows
`{monomial · fᵢ : deg ≤ D}`, columns all monomials of total degree ≤ `D` in
`(x1, x2)`; `expected_rank(D) = min(#rows, #cols)`;
`first_fall_degree = smallest D ≥ D0 with actual_rank(D) < expected_rank(D)`. It
is a genuine Macaulay-matrix rank instrument and it does compute a rank per
degree.

**Difference named — three, and each is independently disqualifying.**

- **P1/P4 — wrong ring and wrong characteristic.** `F_p` with `p` prime
  (`pow(mat[r][col], p-2, p)` is a Fermat inverse), on a two-variable Semaev
  system with `x_R` a constant. **No Weil descent, no Boolean ring, no
  multilinear reduction.** `mvpoly.monomials_up_to_degree` uses
  `combinations_with_replacement`, i.e. full exponent monomials — the fake/true
  distinction the contract exists to draw does not arise here at all.
- **P2 — a third definition of "fall".** Rank defect against the *generic
  full-rank expectation* `min(#rows, #cols)`. That is neither the contract's
  degree-drop nor C-1's fall-to-linear.
- **P3 — the worst failure for this contract's purposes.** A rank-defect-against-
  generic criterion fires on **every** linear dependence among the Macaulay rows,
  and the trivial Koszul syzygies are exactly such dependencies. This instrument
  is, by construction, the "instrument that admits trivial Koszul falls" the
  contract's `declared_conventions` says "measures the ceiling and not the
  system".
- **P5 — partial.** It computes a rank at each `D` but discards the series,
  returning only the falling degree and its defect.

**Validation status — the one candidate that is properly validated.**
`EXP-ECTD-9e4248` holds two `completed_valid` runs (`-impl`, `-screen`) plus one
deliberately retained `invalid_measurement` run, and
`macaulay_rank_defect_at_first_fall` is a declared meter of that contract. So:
**yes, it is validated by run records — as a meter for that experiment's object**
(a vertical-conductor screen across ordinary `F_p` curves at 40–60 bits), which is
not this contract's object.

**Would it compute `M-1` and `M-3` unchanged? No.** See "Reusable
implementations" below for what an adaptation would actually cost, and for the
one property that makes this file the most interesting of the three anyway.

### C-4 — `EXP-ALPF-012`, `round006_exp011_binary_fppr.sage` — **the closest match on instrument *shape*, including an M-2 analogue**

This is the candidate the opening grep's list under-sold, and the one I would put
in front of the Coordinator first if the question is about reuse rather than
about collision.

**What it is.** A binary FPPR / Petit–Quisquater first-fall calibration whose v2
construction is: build `S₃(x1, x2, x3_target)` over `F_{2^n}`; substitute
`xᵢ = Σⱼ t_{i,j}·basisⱼ`; project to `GF(2)[t]` via the F₂-basis; **reduce modulo
`t_k² − t_k`, i.e. multilinearise**; then include the field equations explicitly
and run the meter. Its `meter_run` computes, per degree `D`, a Macaulay rank on
top forms, subtracts a `trivial_koszul(degs, n_vars, D)` term, and sets
`d_ff` to the first `D` at which the **non-trivial** defect is positive. That is
structurally the contract's `M-1` — "a fall is a rank defect beyond the trivial
one" — and it is the only instrument found that carries a trivial-Koszul term at
all. It also ships a `run_self_validation()` with positive and negative controls,
which is the shape of the contract's `C-3`.

**Difference named.**

- **P3 — near-miss, and the gap is precise.** `trivial_koszul(degs, n_vars, D)` is
  an **analytic count predicted from the degree sequence**, not the rank of the
  actually-computed Koszul submodule, and it is not reported as a degree. The
  contract's `M-2` is a **measured** degree — the `D` at which the first trivial
  fall actually occurs — and its `M-1` requires a kernel vector demonstrably
  outside the span of the trivial syzygies. A predicted count and a measured
  submodule can disagree; the script's own v1 post-mortem records
  `trivial_koszul` going **negative** (an over-count) on a wrong degree profile,
  which is precisely that disagreement being observed.
- **P2 — near-miss.** The meter works on **homogeneous top forms**
  (`top_form`, `macaulay_homog`), the standard semiregularity framing, and reads a
  fall as `d_ff < D_reg_pred`. The contract's `M-1` is on the **affine** Boolean
  Macaulay matrix with columns the Boolean monomials of degree ≤ `d`.
- **P4 — fails.** `S₃(x1, x2, x3_target)`: two free points and a target,
  `2l` variables. The contract's object is three point-coordinates, `3l`
  variables. **And no coset shifts.**
- **Field-equation placement — opposite to the contract's headline convention,
  and interestingly so.** This script keeps `t_k² + t_k` as an explicit degree-2
  generator whose leading form is `t_k²`, i.e. the field equations are *inside*
  with their squares retained. The contract's `d'_F` lives in the Boolean ring
  where `X_j² + X_j` is zero. These are the two arms of the contract's `C-6`,
  which makes this script a useful reference for the `C-6` comparison even though
  it is not a collision.

**Evidential status: could not determine.** I did not locate a run record tying
this script to a `completed_valid` run under `EXP-ALPF-012`; its artifacts sit
under `source/`, which is the imported-round layout the ALPF campaign uses. I did
not chase the ALPF import lineage far enough to say whether an equivalent receipt
exists elsewhere. See "What I could not determine".

### C-5 — `EXP-ALPF-006`, `round004_exp005_validated_firstfall.sage` — a *sensitivity-validated* meter, on a different representation

Its own contract header is worth the Coordinator's attention: it exists because a
previous round's meter was found **non-discriminating** ("DEFECT-A": it failed to
fire on systems with known early falls, "making all prior 'no fall' results
INCONCLUSIVE rather than bankable negatives"), and it re-decides an `m = 3`
Semaev negative under positive controls (planted-syzygy ideal, overdetermined
system, genuine extension-field Semaev instance) and negative controls
(semiregular random quadrics).

**Difference named.** The object is the `m = 3` Semaev system in **e-ring /
power-sum representations**, not the coset-shifted Weil descent; no shifts; and
the meter is the Macaulay-rank first-fall meter judged against `D_reg_pred`, not
the contract's equality-form degree drop with a measured Koszul margin. **Not a
collision.** It is, however, a directly relevant precedent for the contract's
`C-3` and for `proof_search_map.proves_too_much`: this program has already been
burned once by an unvalidated first-fall meter, and the technique note
`KN-TECH-1cd4bb` ("Planted-defect instrument-adequacy ladder — prove a
measurement instrument can MOVE at the exact shape being measured … before any
null result is read") is the abstraction of that lesson.

### C-6 — `EXP-SEMBIN-db9bc3` — asserts no measured degree; takes `d_F = 4` as an input

The brief asks specifically about this one. It is a **cost-model** experiment
("Write down what Nagao's `O(n^{8w+1})` costs"), and its `ARM K`
(`known-false-dF5.json`) is a sensitivity control on the *cost model*: it
recomputes time and memory with `d_F = 5` substituted for `d_F = 4` and checks the
cost rises as predicted. `d_F` is an **assumed input parameter** there, granted
from Nagao; nothing is measured.

Its evidence record `EV-SEMBIN-f4408c` says so explicitly — "no degree was
measured or asserted (`IMP-SEMBIN-ENGINE`)" — and so do its siblings:
`EV-SEMBIN-0c8bf4` ("No degree, Groebner or first-fall quantity is measured or
asserted"), `EV-SEMBIN-4614e7` ("no degree of regularity, first-fall degree or
`d_F4` is measured or asserted anywhere"). **The SEMBIN lineage is uniformly and
deliberately degree-free.** `DEC-20260913-8d19e5` is a literature-reading decision
about the 2013/549 → 2015/984 chain and the unproved `d_F ≤ d'_F` step; it records
no measurement and its own line 498 leaves that inequality open.

### C-7 — `EXP-SEMBIN-7e1371` — an approved sibling contract on the same family that has never run

"Locate the `d_F4 = 4` versus `d_F4 ≥ 5` boundary of Semaev's Assumption 1 in
`(n, m, t, k)` using degree-4 Macaulay rank certificates instead of Groebner
completions", status `approved`. **It has no `runs/` directory** (`T-15`, empty
result), so it asserts no value. **Difference named:** `d_F4` is the degree F4
actually reaches, a third quantity again — neither Definition 5's `d_F` nor
Definition 6's `d'_F` — and the object is Semaev's Assumption 1 family, unshifted.

Worth flagging to the Coordinator as a *scheduling* observation rather than a
collision: two approved contracts in this program now aim Macaulay-rank
instruments at overlapping `(n, m)` cells of the same unshifted family, and
neither cites the other.

### C-8 — `EXP-PFDR-5726af`, `EXP-PFGB-d630f6` — real measured first fall degrees, in the wrong characteristic

`EXP-PFDR-5726af`'s title states a measured result outright: "the forced cell
`(m, d, s) = (2, 2, 3)`: first fall degree 5 and fall dimension 4 on the
digit-presented Semaev arm, reproduced exactly by a block-factored null and
beaten by the support-matched null at 6". It has many `completed_valid` runs.
`EXP-PFGB-d630f6` is a "prime-field Semaev first-fall and true solving-degree
growth census with support-matched nulls".

**Difference named: `p ≠ 2`.** Both are over `F_p` with `p ∈ {4099, 65537}`. The
fake/true gap the contract measures is a **characteristic-2 Boolean-ring
phenomenon** — `d'_F` is defined by identifying `X²` with `X`, and the trivial
Koszul ceiling of 5 comes from `X_j² + X_j` at `p = 2`. Neither the quantity nor
the ceiling transfers. These are the best-executed first-fall measurements in the
program and they are simply about a different object. (Noted separately: the
contract's own `n`-series is `p = 2` only, and the batch opening report records
the `p ≥ 3` nearby-object control as deferred for cost.)

### C-9 — screened and dismissed, with the reason

- **`EXP-ECTD-abb8be`** — full-class Semaev/Macaulay meter screen across ordinary
  `F_p` isogeny classes at 40–56 bits. Wrong characteristic, wrong object; same
  meter family as C-3.
- **`EXP-SEMBIN-92724f`** (`EV-SEMBIN-4614e7`) — the `log2(m!)` localisation
  question. Its evidence record states no degree is measured.
- **`EXP-SEMBIN-911efe`** (`EV-SEMBIN-0c8bf4`) — factor-base shape at `t = 2`,
  `n ∈ {20, 22, 24}`; states "No degree, Groebner or first-fall quantity is
  measured or asserted".
- **`EXP-FROB-91ee9c` / `H-FROB-d93575`** — the "fake degree" hits here are a
  *literature citation* ("True versus fake first fall degree, with `d_F ≤ d'_F`
  proved in the source as recorded"), not a measurement.
- **`KN-TECH-004`, `KN-TECH-011`, `KN-TECH-071`** — general technique notes on
  Gröbner complexity indicators and algebraic modelling of block ciphers. Context,
  no measurement. `KN-TECH-071` is a false positive of the opening regex (block
  ciphers).
- **`KN-TECH-b18366`** ("Chained S₃ presentation of point decomposition") and
  **`KN-TECH-1cd4bb`** (the planted-defect adequacy ladder) are the two technique
  notes that actually bear on this contract — the first describes the EQS1/EQS2
  object all the near-misses are built on, the second the `C-3` discipline.
- **`KN-OPEN-d218ec`** — see Q5. It is the open problem that *names* this gap.

---

## The six questions

### Q1 — Has any experiment measured a first fall degree for a summation-polynomial Weil descent?

**Yes — but never the contract's quantity, and never on a shifted instance.**

Two instruments have done it, and they are the same algorithm:
`EXP-SIG-007/src/ic_first_fall_fast.py` (C-2) and its monoset-native
reimplementation `EXP-DREG-001/DREG_dff.sage` (C-1).

- **Which quantity:** a **fake**-side quantity (Boolean ring, `X² ≡ X`), so P1
  matches — but under a **different fall criterion**: first degree at which a
  degree-≤1 polynomial appears in the row space, not the contract's equality-form
  degree drop, and with no trivial-Koszul exclusion.
- **Which field:** `F_{2^n}`.
- **Which `m` and `n`:** `t = m = 3`; `ic_first_fall_fast` is written for
  `n ∈ 8…18`; the recorded `EXP-DREG-001` ladder runs are at `n = 12`, which is
  inside the contract's 7–12 range.
- **Shifted or unshifted:** **unshifted — EQS2.** `src/semaev_tree.py` implements
  no coset shift of any kind (`T-04`, empty), and `make_V_subspace` is a subspace
  through the origin. This matches Nagao's Definition 4, "taking `v1 = … = vN = 0`".
- **Value:** cited, not restated. The recorded values live at
  `experiments/EXP-DREG-001/runs/RUN-DREG-001-DFF-N12-SEM-c/raw-result.json`
  (`runs[].d_ff`) and in the `expected.prior` field of the `-SEM` and `-SEM-b`
  manifests. See `verdict.json → values_disclosed_deliberately`.
- **Evidential weight: low.** The `-SEM` and `-SEM-b` runs are
  `failed_infrastructure`; `-c` is `censored_timeout` with `valid: null` and 2 of
  8 targets resolved; no `EV-DREG-*` record carries the series (`T-11`, empty);
  and the earlier series its prior cites is not in this checkout (`T-10`, empty).

Additionally `EXP-ALPF-012` (C-4) measures a fall degree on a **multilinearised
binary S₃ descent** with a trivial-Koszul term — closest on instrument shape,
different object (`S₃(x1,x2,x3_target)`, `2l` variables, no shifts) and a
homogeneous top-form construction.

### Q2 — `EXP-ECTD-9e4248/driver/reused/macaulay.py`

- **What it computes:** Macaulay matrix `M_D` over a **prime field `F_p`** for a
  two-variable Semaev system `{S3(x1,x2,x_R), g(x1), g(x2)}`, with
  `first_fall_degree` defined as the smallest `D ≥ D0` at which
  `actual_rank(D) < min(#rows, #cols)` — a **rank defect against the generic
  full-rank expectation**. Pure Python (`from . import mvpoly` only; `mvpoly` is a
  from-scratch multivariate implementation with `combinations_with_replacement`
  monomials).
- **Is it validated by a run record?** **Yes**, as a meter of *its own*
  experiment: `EXP-ECTD-9e4248` has two `completed_valid` runs (`-impl`,
  `-screen`) and `macaulay_rank_defect_at_first_fall` is a declared metric there.
  The object those runs validated is a vertical-conductor screen over ordinary
  `F_p` curves at 40–60 bits.
- **Would it compute this contract's `M-1` and `M-3` unchanged?** **No, on four
  counts.** (i) No Boolean/multilinear reduction — `mvpoly` keeps full exponents,
  so it computes in the wrong ring and cannot express `d'_F` at all. (ii) Wrong
  fall criterion — rank-defect-vs-generic is not the equality-form degree drop.
  (iii) **No trivial-Koszul exclusion, and the criterion is maximally sensitive to
  them**: Koszul syzygies *are* row dependencies, so this instrument fires on the
  trivial ceiling by construction, which is the specific failure the contract's
  `declared_conventions` names. There is no `M-2`. (iv) `M-3` is computed
  internally but discarded; only the falling degree and its defect are returned.
- **Recommendation (a recommendation):** do **not** adopt it as the `M-1`
  instrument. Its genuinely valuable property is a different one and is worth a
  Coordinator ruling on its own terms: **it is the only candidate that runs
  without an algebra engine.** `sage`, `sympy` and `galois` are all absent from
  this checkout (`P-07`), consistent with the program's standing impediment
  `IMP-SEMBIN-ENGINE`, and both C-1 and C-2 are Sage scripts. A pure-Python
  GF(2) Macaulay rank routine is the scarce resource here, and
  `macaulay.rank_mod_p` plus the `mvpoly` scaffolding is one, even though its
  fall criterion and its ring are wrong for this contract.

### Q3 — `EXP-SIG-007/src/ic_first_fall_fast.py`

- **What it computes:** the degree-≤`D` **Boolean** Macaulay matrix over GF(2)
  (monomials as frozensets, `m·μ = m ∪ μ`, mod 2), echelonised; returns the first
  `D` at which the row space contains a polynomial of degree ≤ 1. Its `main()`
  constructs the chained S₃ system and Weil-descends it to `F_2` over
  `n ∈ 8…18`, `t = 3`, `k = ⌈n/t⌉`. Requires **Sage** (`from sage.all import GF,
  Matrix`).
- **Is it validated by a run record?** **Not as a first-fall instrument.**
  `EXP-SIG-007` has six `completed_valid` runs, but that experiment's subject is
  an `n = 21` residual-5 / rank-deficit measurement; this file is carried in its
  `src/` bundle with recorded hashes as a pinned dependency, not as the metric
  those runs validated. `EXP-DREG-001` reimplemented its algorithm for the `d_ff`
  ladder, and **those** runs are `failed_infrastructure` or `censored_timeout`.
  I found no `completed_valid` run anywhere whose validated metric is this
  function's output. Stated as a limit: I checked the run manifests of
  `EXP-SIG-007` and `EXP-DREG-001`; I did not audit every experiment that vendors
  a copy of this file (`T-07` lists 19 copies of `semaev_tree.py` alone).
- **Would it compute this contract's `M-1` and `M-3` unchanged?** **No.** (i) The
  fall criterion is fall-to-linear, not the equality-form degree drop — P2 fails,
  and this is the crux. (ii) No trivial-Koszul exclusion and no `M-2` — P3 fails.
  (iii) No rank series — `M-3` is not emitted, so `M-1` would not be
  re-derivable, which `S-7` requires. (iv) Its builder cannot produce a shifted
  instance, so it cannot address `A-SHIFTED` at all without new code.
- **Recommendation (a recommendation):** it is the **right scaffolding and the
  wrong meter**. Its Boolean monoset arithmetic, its GF(2) Macaulay row
  construction and — more valuable — the `semaev_tree` descent pipeline behind it
  are directly relevant; its fall criterion must be replaced, `M-2` and `M-3`
  added, and `make_V_subspace` extended to emit cosets `V + vᵢ`. Whether that is
  reuse or a rewrite is a judgement call, and it is the Coordinator's.

### Q4 — Does any record assert a value for `d_F` or `d'_F` at EQS2 or EQS4 instances of Nagao's family?

**EQS4: no.** No record asserts any first-fall value for a coset-shifted
instance, and no code in the tree can build one (`T-04`, empty).

**EQS2: yes, in a weak and heavily qualified form** — the `EXP-DREG-001` `d_ff`
ladder at `n = 12` (C-1), whose runs are `failed_infrastructure` or
`censored_timeout`, which no evidence record carries, and whose quantity is
defined by a different fall criterion. Values are cited rather than restated;
paths are in Q1.

**Inside `DEC-20260913-8d19e5`'s lineage: no.** That decision is a
literature-reading `expand` about the 2013/549 → 2015/984 priority chain and the
`d_F ≤ d'_F` step; it asserts no measured degree and explicitly leaves the
inequality open.

**Inside `EXP-SEMBIN-db9bc3`: no.** It takes `d_F = 4` as a granted input and
tests cost sensitivity to `d_F = 5` (`ARM K`, `known-false-dF5.json`).
`EV-SEMBIN-f4408c` states "no degree was measured or asserted".

### Q5 — Does any existing measurement *contradict* `H-SEMBIN-a7e721`'s prediction?

**No — and the reason is definitional, not evidential, which makes the answer
more robust than a mere absence.**

Three independent blocks, any one of which is sufficient:

1. **Wrong arm.** The prediction is about `d'_F > 4` at **shifted EQS4**
   instances. Every existing measurement is on an unshifted construction, because
   no shifted construction exists in the codebase. A measurement on EQS2 cannot
   contradict a prediction about EQS4; the hypothesis's own `P-2` treats the two
   as distinct and allows either ordering.
2. **Wrong quantity.** Every candidate's fall criterion differs from the
   contract's equality form, and none excludes trivial Koszul falls. Two
   differently-defined numbers cannot contradict each other.
3. **The program has already ruled on this class of inference.**
   `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml` objective (2) states that internal
   degree measurements are "all silent about which of the two they mean" and that
   "until the map is stated, an internal degree measurement cannot be read as
   bearing on any Nagao or Semaev assumption in either direction." Stating that
   map is a **completion criterion of this very goal**. `KN-OPEN-d218ec` is the
   open problem that names the same gap from the Semaev side. So an existing
   internal measurement is currently barred by the goal's own frozen reasoning
   from contradicting anything here.

**What I am *not* saying.** There is a directionally relevant signal in the EQS2
records — enough that I judged one numeric relation load-bearing for the
Coordinator's ruling and disclosed it deliberately in
`verdict.json → values_disclosed_deliberately` rather than leaking it into this
prose. It bears on the contract's **control** arm and on how surprising the
headline would be; it is **not** a contradiction, for the three reasons above.

### Q6 — Is there a prior measurement of the trivial Koszul fall degree (`M-2`) anywhere, under any name?

**No prior *measurement* of `M-2`. One prior *prediction* of the trivial term
exists, and its failure mode is recorded.**

`EXP-ALPF-012`'s `meter_run` computes `trivial_koszul(degs, n_vars, D)` and
subtracts it before declaring a fall — structurally the contract's "a fall is a
rank defect beyond the trivial one". But it is an **analytic count predicted from
the degree sequence**, not the measured degree at which the first trivial fall
occurs, and it is never reported as a degree. The contract's `M-2` is a measured
degree whose margin against `M-1` is the thing that makes `M-1` readable.

The gap between a predicted count and the truth is not hypothetical here: that
script's own v1 post-mortem records `trivial_koszul` going **negative** — an
over-count — when fed the wrong degree profile. That is a recorded instance of
the predicted trivial term disagreeing with the system, and it is a concrete
argument for the contract's choice to *measure* `M-2` rather than predict it.

Query `Q-C03` (`[Kk]oszul`, 456 files) and `Q-C04` (trivial fall / syzygy, 129
files) were the screens; I found no other instrument that separates trivial from
non-trivial falls.

---

## Reusable implementations — assessment

**Recommended (a recommendation): write the `M-1`/`M-2`/`M-3` meter under this
contract, and reuse two things that are not the meter.**

| file | what validates it | what it gives | what would have to be adapted |
|---|---|---|---|
| `experiments/EXP-ECTD-9e4248/driver/reused/macaulay.py` + `mvpoly.py` | two `completed_valid` runs of `EXP-ECTD-9e4248` (`-impl`, `-screen`), where `macaulay_rank_defect_at_first_fall` is a declared meter — validated **for that experiment's `F_p` curve-screen object** | a **pure-Python, engine-free** Macaulay construction and modular Gaussian rank. The only engine-free candidate; `sage`/`sympy`/`galois` are all absent here (`P-07`, `IMP-SEMBIN-ENGINE`) | replace `mvpoly` monomials with Boolean (multilinear) monomials; specialise the rank to GF(2); **replace the fall criterion entirely** (rank-defect-vs-generic → equality-form degree drop); add the Koszul submodule and `M-2`; emit the full rank series for `M-3`. This is most of a rewrite with the rank kernel kept. |
| `src/semaev_tree.py` (and its 19 vendored copies) | no run record validates it *as a descent builder for this purpose*; it is hash-pinned in `EXP-SIG-007`'s source bundle and used by `EXP-DREG-001` | `build_chained_system_symbolic` + `weil_descend_to_F2` — a working `F_{2^n}` → GF(2) Weil descent onto a Boolean polynomial ring | **it cannot build the contract's object.** It has no coset shifts (`T-04`, empty), so `make_V_subspace` would need to emit `V + vᵢ`; and it builds the *chained* system with an auxiliary full-field variable rather than the single three-point S₃ descent DC-4 specifies. |
| `experiments/EXP-ALPF-012/.../round006_exp011_binary_fppr.sage` | **could not determine** — no run record located | the only existing trivial-Koszul-aware fall meter, plus a positive/negative self-validation harness of the shape `C-3` needs, plus a worked multilinearisation of an `S₃` descent | Sage-dependent; predicted rather than measured Koszul term; homogeneous top-form rather than affine construction; wrong object. Best used as a **reference and a source of fixtures**, not imported. |

**Why not simply adopt one.** Three reasons, and the third is the contract's own.
(i) No candidate computes the contract's quantity, so any adoption is an
adaptation whose correctness would itself need validating — and `C-3` exists
precisely to catch that. (ii) The two Boolean-ring candidates need Sage, which is
absent here. (iii) The contract's `dependencies` block already forbids importing
`EXP-ICPERF`'s converter on the grounds that reuse "would couple two audits
through one implementation — the exact defect the ICPERF review found when two
engines behind one converter were mistaken for independent agreement". That
reasoning is about `EXP-ICPERF`, and the contract says nothing about
`EXP-ECTD`'s or `EXP-SIG`'s files — **which is exactly why this is a Coordinator
ruling and not an executor's choice.** I note only that the same coupling
argument would apply with equal force to `EXP-DREG-001`, whose `d_ff` ladder is
itself a reimplementation of `ic_first_fall_fast`, so the program already has one
instance of two "independent" measurements sharing an algorithm.

---

## What I could not determine, and what it would cost

1. **Whether `EXP-ALPF-012`'s meter has a validating run record.** Its artifacts
   sit under `source/` in the ALPF campaign's imported-round layout, and I did not
   trace that import lineage to its receipts. *Cost:* reading the `EXP-ALPF-012`
   specification, its `runs/` directory, and the ALPF import decisions —
   perhaps twenty file reads. Worth doing before any reuse ruling on C-4.
2. **Whether any of the 19 other experiments vendoring `semaev_tree.py` holds a
   `completed_valid` run whose validated metric is a first-fall degree.** I
   checked `EXP-SIG-007` and `EXP-DREG-001` manifests only. *Cost:* a sweep of
   `manifest.yaml` status fields plus declared metrics across `EXP-SIG-001`…`008`,
   `EXP-ICI-001` and the rest of `T-07`'s list. This is the single largest
   remaining hole in the Q3 answer and is cheap to close.
3. **Whether the missing `ic_first_fall_t3.json` exists elsewhere in the
   program's history.** `T-10` is empty in this checkout; the artifact is cited as
   a prior by an `EXP-DREG-001` manifest. *Cost:* a `git log --all -- '*ic_first_fall_t*'`
   and possibly an object-store lookup. Matters only if the Coordinator wants that
   earlier series as a comparison point for the `A-UNSHIFTED` arm.
4. **Anything the kb index would have found that grep did not.** Structural and
   unrecoverable by more grepping — see "Method, and the limit on it". *Cost:*
   standing up Qdrant and ingesting (`make -C kb qdrant-up`, `crypto-kb
   stage-repo . && crypto-kb ingest`), then re-running this audit. This is the
   only action that would genuinely raise the recall floor.
5. **Whether the `EXP-ALPF-012` trivial-Koszul prediction and a measured `M-2`
   agree on any shared instance.** Answering it requires computing, which this
   task is forbidden to do and which `EXP-SEMBIN-4fa22c` itself would produce.

---

## An observation I was not looking for: a second lane opened underneath this task

While checking my write scope I found files I did not create, appearing *during*
this task. By the time I finished, `git status --porcelain` reported six entries
where it had reported two at the start. Recording the full picture because it
must not be misattributed to this task, and because it bears on scheduling.

**Not mine, and demonstrably so by timestamp** (this task's first write was
`searches.json` at 10:53:36; its last was `verdict.json` at 11:02):

| path | mtime | what |
|---|---|---|
| `coordination/review/sembin-20260916-e0a0c1/read-plan.yaml` | 10:51:19 | predates this task's first write |
| `ledger/decisions/DEC-20260916-441cd5.yaml` | 10:58:45 | a new opening decision |
| `ledger/goals/GOAL-SEMBIN-fcb7a2/checkpoints/BATCH-e0a0c1.yaml` | 11:01:33 | a new batch checkpoint |
| `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/` | — | a new batch directory |
| `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml` | 11:02:34 | **modified** — +68 lines |

A second Coordinator lane, `BATCH-e0a0c1` under `DEC-20260916-441cd5`, opened on
this goal while this task was running. Its appended goal-head entry describes
itself as an additive lane that "runs no experiment", reads
`EXP-SEMBIN-4fa22c`'s recorded Lemma 4 dependency, and deliberately leaves
`current_batch_id` and `dispatch_queue_path` naming `BATCH-cbb416`. That is the
`docs/concurrent-goal-lanes.md` discipline being followed correctly, so far as I
can see from the diff.

**This task wrote none of it.** My writes are exactly the three files in
`collision-audit/`. I read the `goal.yaml` diff only far enough to confirm the
change was additive and not mine; I did not open the new lane's read plan or
dispatch queue, and I make no claim about their contents or their merits.

One scheduling note, offered and not pressed: the new lane's declared subject —
Lemma 4 — is link 2 of `H-SEMBIN-a7e721`'s three-link chain, and this audit's
`C-9` records that `DEC-20260913-8d19e5` leaves `d_F ≤ d'_F` open. The two lanes
are working adjacent links of the same chain and the Coordinator may want them to
know about each other.

---

## Citations

Provenance per `templates/research-records.md`. Everything below marked
`internal` is a file in this repository that **I opened and read** during this
task. **No `recalled` citation appears in this report**, because every claim here
is about this repository's own contents.

| ref | provenance | what | verified_by |
|---|---|---|---|
| `experiments/EXP-SEMBIN-4fa22c/specification.yaml` | internal | the contract audited; `declared_conventions` supplied P1–P5 | executor, this task |
| `ledger/hypotheses/H-SEMBIN-a7e721.yaml` | internal | the prediction screened for contradiction in Q5 | executor, this task |
| `ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml` | internal | objective (2), the Definition 5 / Definition 6 gap, and the completion criterion on stating the map | executor, this task |
| `coordination/goals/.../BATCH-cbb416/opening-report.md` | internal | why this task exists and the declared kb limit | executor, this task |
| `coordination/review/sembin-20260916-cbb416/review-plan.yaml` | internal | `blind_rederivation.quantity` and the no-quoting obligation, read to calibrate disclosure | executor, this task |
| `inputs/NAGAO-2015-984/paper_fulltext.md` | internal (frozen source in-tree) | Definitions 2, 4, 6, 7, 8; the EQS1–EQS4 ladder; "taking `v1 = … = vN = 0`"; the FAKE-version passage | executor, this task |
| `experiments/EXP-DREG-001/DREG_dff.sage` and `runs/RUN-DREG-001-DFF-N12-SEM{,-b,-c}/` | internal | C-1: the fall-to-linear criterion, the object, and the run states | executor, this task |
| `experiments/EXP-SIG-007/src/ic_first_fall_fast.py`, `runs/*/manifest.yaml` | internal | C-2 / Q3 | executor, this task |
| `src/semaev_tree.py` | internal | the decisive absence of coset shifts; `make_V_subspace`; `build_chained_system_symbolic`; `weil_descend_to_F2` | executor, this task |
| `experiments/EXP-ECTD-9e4248/driver/reused/{macaulay,mvpoly}.py`, `specification.yaml`, `runs/*/manifest.yaml` | internal | C-3 / Q2 | executor, this task |
| `experiments/EXP-ALPF-012/source/round006_exp011_binary_fppr.sage` | internal | C-4 / Q6: the trivial-Koszul term and its recorded over-count | executor, this task |
| `experiments/EXP-ALPF-006/source/round004_exp005_validated_firstfall.sage` | internal | C-5: DEFECT-A and the sensitivity-validated meter | executor, this task |
| `experiments/EXP-SEMBIN-db9bc3/` incl. `runs/RUN-SEMBIN-251fd3/known-false-dF5.json` | internal | C-6 / Q4: `d_F` as an assumed input | executor, this task |
| `ledger/evidence/EV-SEMBIN-{0c8bf4,4614e7,f4408c}.yaml` | internal | the uniform "no degree measured or asserted" disclaimers | executor, this task |
| `ledger/decisions/DEC-20260913-8d19e5.yaml` | internal | Q4: the lineage asserts no measured degree | executor, this task |
| `experiments/EXP-SEMBIN-7e1371/specification.yaml` | internal | C-7: approved, never run, `d_F4` | executor, this task |
| `experiments/EXP-PFDR-5726af/specification.yaml`, `experiments/EXP-PFGB-d630f6/specification.yaml` | internal | C-8: measured first fall degrees over `F_p` | executor, this task |
| `knowledge/open-problems/KN-OPEN-d218ec.md`, `knowledge/techniques/KN-TECH-{004,011,071,b18366,1cd4bb}.md` | internal | C-9, Q5 | executor, this task |
| `ledger/goals/GOAL-SEMBIN-5078bc.yaml` (`IMP-SEMBIN-ENGINE`) | internal | the standing engine impediment, corroborated locally by `P-07` | executor, this task |

---

## Completion gate

| gate item | status |
|---|---|
| `report.md`, `searches.json`, `verdict.json` all exist under the write scope | **met** — all three under `coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-cbb416/collision-audit/` |
| `searches.json` records every query including empty ones | **met** — 63 entries (36 broad screens, 20 targeted, 7 probes); four empty results recorded and flagged: `T-04`, `T-10`, `T-11`, `T-15` |
| `searches.json` records the kb index as unavailable and how it was checked | **met** — `index_availability`, with six probes (`P-01`…`P-06`) and the recall-floor consequence |
| every one of Q1–Q6 has an answer or an explicit "could not determine" | **met** — six answers above; the sub-items I could not establish are named in "What I could not determine" and cross-referenced from Q3 and Q6 |
| no measurement was performed | **met** — 0 runs, 0 measurements, `maximum_runs: 0` respected. No algebra engine was invoked; none is installed (`P-07`). No first fall degree was computed. |
| no file outside the write scope created or modified | **met for this task**, but the working tree is not clean and the reason is a concurrent lane, not this task. At completion `git status --porcelain` reports six entries: `?? .../BATCH-cbb416/collision-audit/` (**mine**, in scope, the only thing this task wrote) and five belonging to `BATCH-e0a0c1` — `M ledger/goals/GOAL-SEMBIN-fcb7a2/goal.yaml`, `?? coordination/goals/GOAL-SEMBIN-fcb7a2/batches/BATCH-e0a0c1/`, `?? coordination/review/sembin-20260916-e0a0c1/`, `?? ledger/decisions/DEC-20260916-441cd5.yaml`, `?? ledger/goals/GOAL-SEMBIN-fcb7a2/checkpoints/BATCH-e0a0c1.yaml`. All five are timestamp-separable from this task's writes; see "An observation I was not looking for". **This task modified no tracked file and wrote nothing outside `collision-audit/`.** The Coordinator's snapshot task should stage only the three declared artifact paths, not `git add -A`. |
| no commit made | **met** — the Coordinator's archival task owns the commit. |
