# TASK-20260823-6040d1 — validation report

Validator, GOAL-ECQ-002, BATCH-f2341e. Two joints, reported separately.

- Snapshot read: `ab0aa5404319796966241478dc44e25592139b44` (repo `HEAD` at read time,
  working tree clean). All state below is committed state at or before that sha.
- Blind to `TASK-20260823-07a54b`. No file under that path was opened.
- Requested policy `review-adversarial`; answered by `claude-opus-5` at reasoning
  effort `xhigh` (the effort declared in `.claude/agents/validator.md`, derived from
  `roles.yaml -> review-adversarial`). No fallback, no degraded requirement,
  `model_verified: false` (no `adapter doctor --probe` was run in this session).
- Nothing in this report changes a hypothesis or goal status, and a passing check
  here is not support for H-ECQ-d60d07, not a record claim, and not a speedup.

**Verdict: `failed`.** Joint 2 holds under independent re-verification. Joint 1
breaks on one specific, downstream-consequential item: the only computational check
`TASK-20260823-d1cb76` actually executed reaches a conclusion that is demonstrably
false, and that false conclusion removed the highest exactly-known Q(t)-rank family
from the campaign and drove the recommendation. Details in J1-F1. The remedy is a
superseding record, not a repair; the executor's receipt is unaffected.

---

## 0. Artifact integrity (both joints)

| check | result |
| --- | --- |
| declared paths in `archives/TASK-20260823-744c38/receipt.yaml` | 127 |
| present on disk, sha256 matching the receipt | **127 / 127** |
| present in the snapshot commit `ab0aa540`, blob sha256 matching the receipt | **127 / 127** |
| `icarm_database_20260823.json` sha256 | `118db069…cadc59` — matches `GOAL-ECQ-002.preregistered_baseline.snapshot_sha256` |
| `frontier_20260823.json` sha256 | `5eea69cffb50c63597568a66e68f630a59df814204a534ad9041c042ce850835` (recorded here; the goal record binds only the database) |

Every hash relied on below was recomputed by this task, not read from the receipt.
The receipt's `commit_sha`/`parent_sha` are `null` by its own declared design; per
CLAUDE.md ("Archive receipts bind to CONTENT first") the archive is **content-verified**
at `ab0aa540`, which is the binding that matters. That is an integrity pass and
nothing more: binding a file is not reading it, and the receipt says so itself.

---

## JOINT 1 — the base family (`TASK-20260823-d1cb76`)

### 1.1 What I re-derived myself

The handoff requires at least one family's ceiling re-derived independently. I did
more than that: I regenerated Mestre's construction from scratch, in my own
bivariate-polynomial code over Q (`sympy` is absent in this environment; the
arithmetic is exact `Fraction`).

For **both** published 6-tuples, `(-17,-16,10,11,14,17)` and `(399,380,352,47,4,0)`:

| re-derived here | result |
| --- | --- |
| `p(x,T) = q(x-T)q(x+T)`, `g` = polynomial part of `sqrt(p)`, `r = g^2 - p` | `p = g^2 - r` holds identically ✓ |
| `deg_x r` | **4** for both tuples |
| the 12 sections `(±T + a_i, g(±T+a_i, T))` on `y^2 = r(x,T)` | **12 / 12 hold IDENTICALLY in T** ✓ |
| `T`-degrees of `(r_4, r_3, r_2, r_1, r_0)` | **(4, 4, 6, 6, 8)** |
| `deg_T A`, `deg_T B` for `Y^2 = X^3 - 27I X - 27J` | 12 and 18 |
| minimality | `v_{T=0}(A) = 4`, `v_{T=0}(B) = 6` → **non-minimal at T = 0** |
| after reduction | `deg A' = 8`, `deg B' = 12`, `gcd(A', B') = 1` (no further non-minimal place anywhere), `deg Δ' = 20` |
| **surface degree** | **d = max(⌈8/4⌉, ⌈12/6⌉) = 2 exactly** — an elliptic **K3** |
| **Shioda–Tate ceiling** | **10d − 2 = 18 over C̄**, 17 over Q(T) under the cited Elkies refinement |

Consistency check on the ceiling: `deg Δ' = 20` on the affine line plus an Euler
contribution 4 at `T = ∞` gives 24 = 12d at d = 2. ✓

**Generic rank, re-derived rather than cited.** Specialisation
`E(Q(T)) → E_{T_0}(Q)` is a group homomorphism, so independence of the images
implies independence of the sections and gives an unconditional lower bound on the
rank over Q(T) — no Silverman exceptional-set caveat. I mapped the 12 sections to
11 Jacobian classes `[P_i] − [P_1]` via the classical quartic→Weierstrass
transformation (every mapped point verified on the resulting model in exact
arithmetic), then certified independence with my own stdlib exact certifier
(§2.3):

| tuple | T₀ | exhibited points | **exactly certified rank over Q** |
| --- | --- | --- | --- |
| `(-17,-16,10,11,14,17)` | 11 | 11 | **≥ 11** (ℓ = 2, torsion bound 1) |
| `(399,380,352,47,4,0)` | 1 | 11 | **≥ 11** (ℓ = 2, torsion bound 1) |

**Therefore `rank E(Q(T)) ≥ 11` for Mestre's family is now re-derived in this
repository, not merely cited** — which is exactly what GOAL-ECQ-002 C2 asks for and
what `TASK-20260823-d1cb76` could not supply. The bound is on the span of the 12
exhibited sections; 11 is also the ceiling of that method (12 affine points, one
spent as origin, and `r_4(T)` is not a square in Q[T] for either tuple, so there are
no rational points at infinity to add a 12th class).

I also ran the producer's own §5 falsifiers, which it flagged as unrun:

- *"assert `p = g^2 - r` symbolically and print `deg_x r`. If it is 5 for both
  published 6-tuples, MESTRE-1991-QT11 must be withdrawn."* — `deg_x r = 4` for
  both. **The recommendation survives this falsifier.**
- *"Run the naive height of the minimal model before running anything else …
  nobody in this program has run it."* — run, over T₀ ∈ {1..12, −1, −3, −5}:

| tuple | naive height of minimal model | max height-pairing rank over tested T₀ |
| --- | --- | --- |
| A `(-17,…,17)` | **79.62 … 107.61** (all **below** 118.770) | 11 (at T₀ = 11; 6–10 elsewhere) |
| B `(399,…,0)` | **122.52 … 144.03** (all **above** 118.770) | 11 (at 10 of 15 T₀) |

Read against the frozen frontier: the exactly certified rank-11 curve at T₀ = 11
has naive height **107.614**, minimal model `[1,0,0,-78984475693156,221488815067190876711]`,
against the pre-registered r ≥ 11 cell of **61.507** (curve 50). **No cell is taken
and nothing is claimed.** The campaign-relevant reading is that this base arrives at
rank 11 having already spent ~107.6 of a 118.770 budget, leaving ~11 units to buy
the remaining +4 rank — a much tighter box than the report's "heights in the 60–120
range ⇒ mechanism intact" suggests.

### 1.2 Field discipline and ceilings as stated by the producer — checked

- The `conventions` block is **correct**: for an elliptic surface with section and
  `χ(O_S) = d`, `e = 12d`, `h^{1,1} = 10d`, and
  `rank MW ≤ ρ − 2 − Σ_v(m_v − 1) ≤ 10d − 2`; `d = 1 → 8`, `2 → 18`, `3 → 28`,
  `4 → 38`. I re-derived `h^{1,1} = b_2 − 2p_g = (12d−2) − 2(d−1) = 10d`. ✓
  (Unstated qualification: the bound presumes a relatively minimal, non-split,
  non-isotrivial surface. It holds for every family listed; recording it would cost
  one line.)
- The `d ≥ ⌈(r+2)/10⌉` rule is correct and, importantly, is applied to the
  **geometric** rank throughout, with `rank_{Q(t)} ≤ rank_{Q̄(t)}` the only
  inference drawn. ✓
- **Rank over Q(t) vs Q̄(t) — the silent-+1 risk — is handled correctly.** Every
  family carries both fields separately; `unknown` is recorded where a source gives
  only one. Specifically:
  - **Nagao**: 12 over Q(t), 13 over Q̄(t), with the title/Corollary-1 discrepancy
    flagged and "use 12, do not average" stated. Correct discipline.
  - **Kloosterman**: 15 is identified as **geometric**, with `rank_{Q(t)} ≤ 15` the
    only inference. Correct — and the executor's §4b independently corroborates it
    (certified ranks 0–1 over Q at small t).
  - **Kuwata π₆**: geometric `16 + h` vs ≤ 11 Q-rational sections, correctly
    presented as the published proof that the geometric/rational gap can be large.
  - **No family claims a rank above its own stated ceiling.** ✓
- **Elkies rank-18 at d = 2 sitting exactly on the K3 ceiling** is flagged as an
  unresolved discrepancy rather than papered over. Correct handling of an
  unresolved source conflict.

### 1.3 Verified-vs-cited split — checked, and it is honest with one exception

The no-code-execution constraint is disclosed in the first section of `report.md`
and in `session_capability_disclosure` of the JSON, "verified here" is given an
explicit three-clause definition, every rank figure in §2 is marked
`verified_here: false`, and the items that could not be obtained at all (Kihara,
Elkies' equations, Nagao's generators, Kloosterman's Maple worksheets) are listed
with mechanisms. The `report.md` provenance header correctly records that the file
was transcribed by the orchestrating session after the subagent terminated and that
the JSON is authoritative; I found no substantive disagreement between the two.

Two defects in the split:

- **J1-F2 (moderate).** The predicted `T`-degrees `(6,7,8,9,10)` for
  `(r_4,…,r_0)`, listed under `verified_here` as "hand weighted-degree argument",
  are **not** the actual `(4,4,6,6,8)`. As an upper bound the claim is safe, but the
  ceiling derived from it — `deg A ≤ 16`, `deg B ≤ 24`, `d ≤ 4`, ceiling up to
  **38** — is 20 above the true **18**. `method_ceiling` in H-ECQ-d60d07 exists so
  that "an over-claim is visible immediately"; a ceiling loose by 20 is exactly the
  guard failing open. The producer did mark it "must be confirmed by the executor",
  which is why this is a defect and not a fabrication.
- **J1-F5 (minor).** `verified_by` fields name URLs, not the verifying agent, as
  `templates/research-records.md` and AGENTS.md rule 9 require. And the sole source
  for `rank ≥ 11 over Q(T)` is *Mestre's paper titles* — the CRAS notes were not
  opened. The producer says so plainly. §1.1 above now discharges that claim
  independently of the citation, which is the correct remedy.

### 1.4 J1-F1 (MAJOR) — the Nagao consistency check reaches a false conclusion

This is the one computational result `TASK-20260823-d1cb76` produced, it is listed
under `verified_here`, and it is load-bearing: it is why `NAGAO-1994` — the only
candidate with an exactly-known, peer-proved Q(t) rank (12, Scholten Corollary 1),
i.e. the best base on the table — is marked
`"NOT USABLE AS TRANSCRIBED"` / `TRANSCRIPTION_STATUS: "UNRELIABLE -- DO NOT USE"`,
and it is the stated empirical case for the whole "regenerate, never transcribe"
recommendation.

**The arithmetic reproduces exactly.** I recomputed the full identity

```
9*N(t)^2  vs  c4(t)(t+703)^4 + 15c3(t)(t+703)^3 + 225c2(t)(t+703)^2
              + 3375c1(t)(t+703) + 50625c0(t)
```

symbolically from the transcribed coefficients. The producer's two hand-computed
coefficients are right to the digit, including the breakdown:

- `t^6`: left `451584`, right `703343886336` = `14017536 − 6307891200 + 709637760000` ✓
- `t^5`: left `3403008`, right `5300198572032` ✓

**The conclusion drawn from them is wrong.** Computing all seven coefficients:

| t^k | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| right / left | 1557504 | 1557504 | 1557504 | 1557504 | 1557504 | 1557504 | 1557504 |

The ratio is **constant across every coefficient**, and

```
1557504 = 1248^2
```

so the right-hand side is exactly `(1248 · 3 · N(t))^2` and

**the point `((t+703)/15, 1248·N(t)/75)` lies exactly on the transcribed quartic.**

I verified this as an exact polynomial identity, not numerically.

The producer's report states the opposite in terms that are checkable and false:

> "It fails at two independent coefficients, **by factors that are not squares and
> so are not absorbed by any rescaling.**"

The factor is a single constant, `1248^2`, a perfect square, absorbed by exactly the
rescaling `y → 1248·y`. This was decidable from the two numbers the producer already
had, with one division, and with no code-execution tool.

**Scope of my correction, stated precisely.** This does **not** establish that the
transcribed coefficients are Nagao's equation. It establishes that the *evidence
offered* for "corrupted, or belonging to different models" does not support that
conclusion: the transcribed equation and the transcribed point are internally
consistent up to a square rescaling of `y`, which is the ordinary difference between
`y^2 = Q(x)` and `y^2 = λ^2 Q(x)` models, or a dropped constant factor in the
extraction of one coordinate. Retrieval of the source is still required before the
family is used.

The producer's secondary tell — "the quartic contains only even powers of `t` while
the point contains odd powers … an extractor that dropped odd-power terms would
produce exactly this pattern" — is likewise not evidence of corruption. It is
consistent with `E` being defined over `Q(t^2)` with sections split by the
`t → −t` eigenspace decomposition, which the producer itself notes "is not by itself
contradictory".

**Consequence, and it is real.** The disposition of the highest exactly-known Q(t)
rank in the candidate list rests on a false negative, and the recommendation moved
from Nagao (12, exact, peer-proved) to Mestre (≥ 11, cited from a title) partly
because of it. `sota_delta` in §6 records "vs Nagao, 12 → −1" without recording that
the −1 was self-inflicted.

**Corroboration in the other direction.** With the transcription no longer
discredited, I re-derived Nagao's surface degree from those same coefficients:
`deg A = 8`, `deg B = 12`, `gcd(A,B) = 1` (minimal), `deg Δ = 20` →
**`d = 2` exactly, elliptic K3, ceiling 18 over C̄ / 17 over Q(T)**. The producer's
conditional derivation of `d ≤ 2` was correct, and its condition is now much better
supported than the record says.

### 1.5 Joint 1 verdict

**breaks.** The ceiling framework and the Q(t)/Q̄(t) discipline are correct and I
found no silent +1. But the single executed check is wrong in a way that changed the
recommendation, and the recommended base's ceiling is stated 20 too loose. Both are
correctable by superseding records; neither is a fabrication, and the producer's
disclosure of its own constraints is exemplary. Concretely, the ledger archive
should (a) supersede the `NAGAO-1994` disposition and reinstate it as a candidate
pending source retrieval, (b) record `d = 2`, ceiling 18/17 for both
`MESTRE-1991-QT11` and `NAGAO-1994`, and (c) record that `rank ≥ 11 over Q(T)` for
Mestre's family is now re-certified in-repo by this task.

---

## JOINT 2 — the pipeline (`TASK-20260823-01d3d9`)

I did not accept the summary. Everything below was recomputed here.

### 2.1 CHECK 1 reproduction gate — verified independently on all 289 curves

I wrote my own invariant computation from the standard definitions (b/c-invariants,
`Δ = (c4^3 − c6^2)/1728` asserted exactly on every curve; PARI used only for
`ellminimalmodel`, `.omega`, `ellglobalred`) and ran it over the whole frozen
snapshot. It never read the producer's `icarm_invariants.py` before being written.

| metric | validator vs **board**, all 289 | validator vs **producer**, all 289 |
| --- | --- | --- |
| naive height | agree, max abs diff **2.842170943040401e-14** | max abs diff **0** |
| Faltings height | agree, max abs diff **1.7763568394002505e-15** | max abs diff **0** |
| minimal discriminant | **289 / 289** exact string match | — |
| curve_key `c4:c6` | **289 / 289** exact | — |

My worst-case figures are bit-identical to the producer's reported
`max_naive_height_abs_diff` and `max_faltings_height_abs_diff`, and my per-row values
match theirs to zero ulp.

**The conventions are pinned by my own measurement, not accepted.** On curves 42, 53,
244, 276 I evaluated four rival Faltings conventions:

| convention | curve 42 delta | 53 | 244 | 276 |
| --- | --- | --- | --- | --- |
| **−½ log A** | **0** | **0** | **0** | **0** |
| (1/12)log|Δ| − ½ log A | +0.3009 | +0.7110 | +6.427 | +9.058 |
| −log A | −0.9965 | −0.5614 | +5.131 | +7.822 |
| −½ log(A/2π) | +0.9189 | +0.9189 | +0.9189 | +0.9189 |

So `faltings_height = −½ log A`, `A = |Im(conj(ω1)·ω2)|` of the minimal model,
**with no (1/12)log|Δ| term** — confirmed, and then confirmed on all 289.
`naive_height = log max(|c4|^3, c6^2)` of the **minimal** model — confirmed on all 289.
`conductor = ellglobalred(E)[1]` — confirmed on a **30-curve sample I chose with my
own seed** (`random.Random(6040)`, 24 draws plus 42, 53, 244, 273, 276, 288):
**29 / 29 agree**, the 30th being #288 where the board stores `null`.

Every later comparison to the frontier therefore rests on the board's own conventions.

- **J2-G3 (minor, factual).** §1's evidence sentence mislabels one rival: on curve 42
  the 0.30 miss is `(1/12)log|Δ| − ½log A` ✓, but `−log A` misses by **0.9965**, not
  0.70; the 0.70 miss belongs to `(1/12)log|Δ| − log A`. The conclusion is right and
  is independently confirmed above; the citation of it is not.

### 2.2 The two exception classes — handled as claimed

- **#288**: board `conductor` is `null`; the producer computed one. Confirmed: a gap
  on the board's side, not a numerical disagreement. Denominator arithmetic checks:
  `289 − 8 timed out = 281 checked`, `280 agree`, 1 disagreement (#288). ✓
- **7 unmeasured conductors**: 8 curves (#9, #10, #11, #12, #66, #67, #199, #289)
  exceeded the 15 s guard; the 130 s retry (`RUN-…-010`, 961 s) resolved **only #66**
  and 7 remain unmeasured. Confirmed from `reproduce_icarm_conductor_retry.json`:
  `conductor {agree: 1, checked: 1}`, seven rows `conductor_timed_out: true` with
  `conductor_agrees: null`. Ranks 1, 13, 23, 24, 26, 27, 28, 29 all re-certified
  **8 / 8 agreeing** in that same run. Missing data is reported as missing and is
  excluded from the denominator, not counted as agreement. ✓ Correct under AGENTS.md
  rules 3 and 5.

### 2.3 Exact descent — re-run with my own certifier

I implemented the certificate from its mathematical statement (torsion bound by
`gcd_p #E(F_p)` at odd good p; `ψ_p(X) = (N_p/ℓ)·X` into `E(F_p)[ℓ]`; F_ℓ-rank of the
stacked images; primitive-relation contrapositive), in exact integer/`Fraction`
arithmetic, with no floating point in the chain. My implementation passes the same
five negative controls the producer reports for `RUN-…-001`:

| control | expected | mine |
| --- | --- | --- |
| P, 2P on 37a1 | 1 (not 2) | **1** |
| P, Q, P+Q on 389a1 | 2 (not 3) | **2** |
| generators of 389a1 | 2 | **2** |
| off-curve point | rejected | **rejected** ("point 0 NOT on curve") |
| 5-torsion (5,5) on 11a1 | rejected | **rejected** ("point 0 is torsion") |

Independent re-certification from the board's own points:

| board curve | board rank | **validator certified** |
| --- | --- | --- |
| #276 (rank-15 incumbent, the campaign's target cell) | 15 | **≥ 15** (ℓ = 3; ℓ = 2 reached only 14) |
| #244 (rank-14 incumbent) | 14 | **≥ 14** (ℓ = 2) |
| #273 (rank-30 record curve) | 30 | **≥ 30** (ℓ = 2) |

Each claimed rank is backed by exactly that many exhibited points, verified on the
curve in exact arithmetic and shown pairwise-independent as an F_ℓ-rank. I reproduced
the escalation phenomenon independently: on #276 the ℓ = 2 stack tops out at 14 and
ℓ = 3 gives 15 — so a shortfall is a property of `(ℓ, prime set)`, never of the curve.

- The producer's **6 escalated curves** (#273, #12, #11, #10, #168, #35) carry
  `certifier_escalated: true` in the artifact, all with `rank_agrees: true`, and
  `exact_certify.py` emits, on shortfall, the literal text *"the remainder are
  INCONCLUSIVE … this is not evidence of low rank"*. **Handled as claimed.** Board
  rank sum 3480 = certified rank sum 3480 over all 289.
- Auditing `exact_certify.py` itself: stdlib-only (`fractions`, `math`, `json`,
  `sys`), no PARI, no float; the method matches what I implemented independently; the
  certificate records `independent_point_indices`, so the exhibited-points claim is
  checkable per curve.

### 2.4 The three self-reported defects — confirmed handled in the artifacts

**Invalid runs `-002`/`-003` (cypari `AlarmInterrupt` is not an `Exception`).**
Confirmed, not merely asserted: both `raw-result.json` are the stub
`{"note": "producer wrote no raw result", "status": "invalid_measurement"}` (identical
sha256), both manifests carry `status: invalid_measurement`, both `stderr.log` end in
`cypari._pari.AlarmInterrupt` (in `-002` from `iferr(alarm(...))`, in `-003` from a
bare `alarm(...)` — two distinct attempts), and the fix is in the tree
(`icarm_invariants.py:43,73` and `pipeline.py:98,112`, all `except BaseException`).
`results/reproduce_icarm_all.json` is **byte-identical** to `-004`'s `raw-result.json`,
and nothing in `results/` matches `-002`/`-003`. **The quarantine is complete.**

**The regulator defect and the supersession of `-006…-009` by `-011…-014`.** This is
the item the archive receipt explicitly left open ("that `pipeline_validation.json`
actually draws from `-011 … -014` … is left to the validator"). It is real and it is
verifiable by content:

- `results/pipeline_{DEMO-SEC5-r5,DEMO-SEC3-r3,DEMO-NULL-r0,DEMO-SEC1-r1}.json` have
  sha256 **equal to the `raw-result.json` of `-011, -012, -013, -014`** and equal to
  none of `-006…-009`. `pipeline_validation.json` is assembled from those files.
  **The reruns are what is reported.**
- A full recursive diff of each superseded/superseding pair shows the **only** changed
  leaves are `regulator`, `numerical_regulator`, the new `numerical_regulator_over`
  flag, and timings (`seconds`, `wall_clock_seconds`). **No `certified_rank`, no
  `naive_height`, no `faltings_height`, no `discriminant`, no `curve_key`, no
  `conductor` changed anywhere.** The producer's claim that `-006…-009` remain valid
  as measurements of rank and height is therefore confirmed by content, not asserted.
- The collapse is exactly as described: `-006` carries `0.E-95` and `±3.745…E-96` at
  precisely the entries where the search returned dependent points; `-011` carries
  proper values (e.g. `113428.72…`, `983.55…`) at the same entries.

- **J2-G2 (moderate).** No run manifest carries `supersedes` / `superseded_by`, and
  `-006` and `-011` share **identical** `command.txt`, `git_commit` (`446ba733…`) and
  `git_dirty: true`. The code edit that distinguishes them is captured in no artifact,
  so `-006…-009` (and `-002`/`-003`) cannot be reproduced from their own records; the
  supersession is recoverable only by hashing `results/` against `raw-result.json`,
  which is what I did. Recommend the ledger archive record the supersession
  explicitly, and that future runs hash the source tree into the manifest.

**Seven unmeasured conductors** — see §2.2. Confirmed.

### 2.5 Metric recomputations from the raw run records

| quantity | producer | validator (recomputed from `runs/*/raw-result.json`) |
| --- | --- | --- |
| falsifier fits, all 5 families: intercept, slope, R², n | e.g. `17.96718739796337 / 2.136722252605693 / 0.10753056236288205 / 130` | **identical to full double precision, all 5 families** |
| admissible `log H` under h < 118.770, all 5 families | `47.1764 / 18.5279 / 5.1937 / 1.6804 / −3.7782` | **identical** |
| pooled mean certified rank (top / control) | `3.1166666666666667 / 2.4833333333333334` | **identical** |
| pooled max certified rank | `7 / 6` | **identical** |
| pooled mean naive height | `52.32381975768801 / 54.91241409686581` | **identical** |
| pooled min naive height | `15.72037011494433 / 11.3874642776054` | **identical** |
| observed rank difference | `0.6333333333333333` | **identical** |
| observed height difference | `−2.588594339177803` | `−2.5885943391777957` (float assoc., 1e-14) |
| permutation p, rank (20 000, seed 20260823) | `0.06830` | `0.06785` — agrees within Monte-Carlo error under my own shuffle |
| permutation p, height | `0.76901` | `0.75926` — same |
| null control DEMO-NULL-r0 mean rank (ordered / random) | `1.07 / 0.40` | **1.0667 / 0.4000, identical** |

Everything the report puts a number on reproduces from the immutable run records.

### 2.6 Controls before belief — checked against `docs/inventor-protocol.md` §3

The null-object control required by `H-ECQ-d60d07.nearby_object_control` is present
and behaves as it must. Mean certified rank in the ordered arm across the four
families, by declared generic rank of the base:

| generic rank of base | 0 (DEMO-NULL-r0) | 1 | 3 | 5 |
| --- | --- | --- | --- | --- |
| mean certified rank over Q | **1.07** | 2.07 | 3.87 | 5.47 |
| observed range, null family | **0 – 2**, never near 15 | | | |

That is monotone in the parameter meant to produce the effect, and the null object
does not produce the effect. The statistical signal claimed (Mestre-Nagao ordering)
is reported against a same-shape random-draw control at p = 0.067 and is explicitly
**not** claimed as significant; the statistic is used to order and never to certify,
and every rank in both arms comes from the exact certifier. This is the correct
handling.

Three limitations I measured that the report does not quantify:

- **J2-G6.** The arms are not disjoint: **24 of 60** ordered-arm draws also appear in
  the control arm (per family 8, 5, 4, 7 of 15). The producer discloses
  non-disjointness qualitatively; the boxes hold only 45–47 non-singular points, so
  the overlap is close to what independent uniform sampling would force (~5/family)
  rather than a bias — but the permutation test's exchangeability assumption is only
  approximately met, and taking the "top 15 of ~46" is a **top-third** selection
  ratio, a shallow test of an ordering statistic. No certified rank is affected.
- **J2-G5.** §3's "Both arms fully descended and exactly certified" overstates:
  **9/60** (ordered) and **11/60** (control) PARI `ellrank` calls timed out, and in
  those cases the certificate rests on the family's prescribed sections alone. The
  per-entry data discloses it; the §3 table does not.
- **J2-G7.** Entries with no `certified_rank` key are summarised as 0
  (`summarise_validation.py:113`). For DEMO-NULL-r0 all 11 such entries have PARI
  `r_low = r_high = 0`, so the imputation is correct there and the null-control
  numbers stand. The imputation rule is in code only, stated in no artifact.

### 2.7 Two further accuracy defects

- **J2-G1 (moderate).** `snapshot_sha256_declared` is **`null`** in
  `reproduce_icarm_all.json`, `reproduce_icarm_conductor_retry.json` **and**
  `pipeline_validation.json`, while §1 of the report asserts "declared sha256
  `118db069…cadc59`". The machine-readable artifacts do not bind their own input. I
  verified independently that the file consumed hashes to the pre-registered value
  and is committed at that hash, so there is no substantive harm — but the run
  records do not establish it on their own, which is precisely what a pre-registered
  baseline exists to make checkable.
- **J2-G4 (minor, factual).** §4's "PARI `ellrank` … `r_low` matched our exact
  certification in every non-timeout case" is not accurate: in `RUN-…-016` there are
  **6** non-timeout cases with `r_low = r_high = 1` and **no generator returned**, so
  the entry carries no `certified_rank` and is summarised as 0. The direction is
  conservative — the certifier under-reports, never over-reports — so §4b's
  "max 1, mean 0.4 / 0.2" understates rather than inflates.

### 2.8 Run-record and budget conformance

16 run records, ids `-001 … -016`, each with `manifest.yaml`, `command.txt`,
`environment.json`, `raw-result.json`, `stdout.log`, `stderr.log`. Manifests carry
id, task/goal/batch/hypothesis ids, `started_utc`, wall clock, `max_rss_kb`, user CPU,
`exit_code`, `status` + `status_reason`, `git_commit`, `git_dirty`, `seeds`,
`certificate`, `budget`, `artifacts`. `environment.json` carries Python 3.11.15,
cypari 2.5.6, PARI 2.15.4, and a full `inference` block (`requested_policy:
executor-implementation`, `resolved_model_id: claude-opus-5`, effort `medium`,
`model_verified: false`, `fallback_used: false`, `degraded_requirements: []`).
Budget: peak RSS 1 661 324 kB = **1.66 GB** at `-006`/`-011` against 4 GB; aggregate
child wall clock **1880.2 s** against 3600 s; 16 runs against 80. All within budget,
and the report's figures match. Seeds recorded and identical across runs (20260823);
only the random-sample control consumes randomness, as the manifest comment states.

### 2.9 Joint 2 verdict

**holds.** The reproduction gate, the height and conductor conventions, and the exact
descent all survive re-verification by an implementation that did not descend from
theirs. All three self-reported defects are handled in the artifacts exactly as
claimed, and the supersession is confirmable by hash rather than by prose. The
findings J2-G1…G7 are provenance and prose-accuracy defects: none of them changes a
number in `pipeline_validation.json`, and none of them touches a certified rank.

---

## 3. Out-of-scope observations (recorded, not adjudicated)

- **J2-G8 (process).** Neither `dispatch_queue.json` nor the handoff envelope carries
  a `review_plan`. AGENTS.md "Review architecture" requires one, written before any
  reviewer runs, with the Coordinator's recorded prior, enumerated owned joints, and
  declared blindness. My joints were assigned in the launch message only, so
  `tools/check_review_independence.py` has no plan to check this round against, and
  "the Coordinator's prior was recorded first" cannot be established after the fact.
  This is a defect in the round's setup, not in either producer's work.
- **J2-G9.** The archive receipt's `commit_sha`/`parent_sha` are `null` by declared
  design. Content binding verified here for all 127 paths at `ab0aa540`.
- The demo families in CHECK 2/3 are internal objects built in this task with
  prescribed sections, so their "certified rank r" largely re-certifies the sections
  that were put in by construction. The producer says so ("throwaway families … made
  to exercise and falsify, not to compete"). The slope trend b ≈ 2.1, 5.6, 21.2, 67.4
  is correctly flagged as **extrapolation, not measurement**, when read forward to
  rank 12–14.
- `check_5.any_frontier_cell_beaten: true` refers only to the t = 0 specialisation of
  DEMO-SEC5-r5 minimalising to 53a1 at h = 11.3875 vs the r ≥ 1 cell of 11.6136. The
  report describes it correctly as "a textbook curve that the board simply does not
  contain, not a discovery". Nothing was submitted; every emitted record carries
  `provenance.not_submitted: true`.

## 4. What this report does and does not support

It supports: the executor's receipt is admissible evidence within its stated scope
(289 board curves; internal demo families of generic rank ≤ 5; |t| ≤ 30 or |t| ≤ 15
with denominator ≤ 2; PARI 2.15.4 / cypari 2.5.6 / Python 3.11.15 on one 4-core
machine). It supports, newly and independently, that Mestre's family has
`rank ≥ 11 over Q(T)` and surface degree `d = 2` with Shioda–Tate ceiling 18 (17
over Q(T)) — a C2-relevant fact re-derived in-repo rather than cited.

It does not support: any statement about H-ECQ-d60d07's status, any ICARM record
claim, any rank ≥ 15 result, any speedup, or the usability of `NAGAO-1994` as a base
(J1-F1 removes the stated reason for excluding it; it does not establish that the
transcription is correct). Nothing here authorises a promotion, and no status was
changed by this task.

---

```yaml
review_attestation:
  task_id: TASK-20260823-6040d1
  joints_owned:
    - "JOINT 1: base family — generic rank over the field claimed (Q(t) vs Q-bar(t)),
       Shioda-Tate ceiling 10d-2 for the asserted degree d, verified-vs-cited split,
       and the Nagao transcription consistency-check diagnosis"
    - "JOINT 2: pipeline — ICARM reproduction gate, height/conductor conventions,
       independent re-run of exact-descent certification, and the three
       producer-self-reported defects (AlarmInterrupt quarantine, regulator
       supersession, unmeasured conductors)"
  sources_read:
    - agents/validator.md
    - AGENTS.md
    - ledger/handoffs/TASK-20260823-6040d1.yaml
    - ledger/goals/GOAL-ECQ-002/goal.yaml
    - ledger/hypotheses/H-ECQ-d60d07.yaml
    - templates/research-records.md          # review_attestation block only
    - .claude/agents/validator.md            # frontmatter/effort only
    - coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json
    - coordination/goals/GOAL-ECQ-002/baseline/icarm_database_20260823.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/dispatch_queue.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/archives/TASK-20260823-744c38/receipt.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-d1cb76/report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-d1cb76/candidate_families.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline_validation.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/exact_certify.py
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/icarm_invariants.py
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/pipeline.py       # grep only
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/summarise_validation.py  # grep only
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/falsifier_height.py      # grep only
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/results/*.json               # all 10
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/runs/RUN-ECQPIPE-01d3d9-001..016/*  # all 96
  read_sibling_reports: false
  blind_from_respected: null      # not a blind re-derivation task
  verdict: >-
    JOINT 1 breaks (J1-F1: the Nagao consistency-check conclusion is false and was
    load-bearing; J1-F2: the recommended base's ceiling is stated 20 too loose).
    JOINT 2 holds (every claim re-verified with an independent implementation; all
    three self-reported defects confirmed handled in the artifacts).
```
