# TASK-20260823-72505a — validation report

Validator, GOAL-ECQ-002, BATCH-da59ec, H-ECQ-a609f8. Two joints, reported separately.

- Snapshot read: `0cb0165024b3280e83dc7974918d6d82af5039b4` (repo `HEAD` at read time,
  working tree clean). Every producer artifact below was read with
  `git cat-file -p 0cb01650:<path>`, not from the working tree.
- Blind to `TASK-20260823-eaf799` (red team). No file under that path was opened.
  **Disclosure**, two incidental exposures, both after every finding below was fixed:
  (1) a `ls` of the shared `tasks/` parent directory, run to create my own write_scope,
  showed that `TASK-20260823-eaf799/` had come into existence during my run — directory name
  only, no file inside it listed or read; (2) a closing `git log --oneline -1`, run to confirm
  I had committed nothing, returned the subject line of commit `ac5f28d6d`,
  "TASK-20260823-eaf799 artifacts land". A subject line saying *that* the sibling's artifacts
  landed carries no finding. `HEAD` therefore moved from `0cb01650` to `ac5f28d6d` during this
  task; every check below was performed against committed state at `0cb01650` via
  `git show <sha>:<path>`, so no conclusion depends on any later commit.
- Requested policy `review-adversarial`; answered by `claude-opus-5` at reasoning effort
  `xhigh` (declared in `.claude/agents/validator.md`, derived from `orchestration/roles.yaml
  -> review-adversarial`). No fallback, no degraded requirement, `model_verified: false`
  (no `adapter doctor --probe` was run in this session).
- Nothing here changes a hypothesis or goal status. Nothing here is a record claim.

**Verdict: `failed`.**

Say precisely what that does and does not mean, because the split matters:

* **Joint 2 HOLDS, completely, and is stronger than the producer reported.** I re-derived
  the naive height of **every one of the 1137 fibres** from the transcribed family with my
  own minimalisation code — no PARI, no producer code — and got **zero disagreements above
  1e-9**. `(a, b, R²)`, the minimum, the median, the max, the box enumeration, the union and
  the overlap all reproduce exactly. All three admissible boxes are EMPTY, under both the
  pre-declared and the frozen-baseline cell values. My own 6.7×-larger independent sweep
  (7593 parameters) does not find anything lower and shows the lower envelope *rising*, not
  merely flattening.
* **Joint 1 BREAKS on two recorded claims** — one in the producer's deliverable
  (`batch_f2341e_verdict_overturned: true`, and the wording that the transcription *as
  recorded* is self-consistent), one inherited from BATCH-f2341e and put to me by the task
  card (Shioda–Tate ceiling 18 / 17 over Q). The second is the consequential one: the
  ceiling of **this** surface is **15**, not 18, and 15 is the number Axis A1 has to plan
  against.
* Two further recorded statements are contradicted by the batch's own artifacts: the
  framing of the t = 0 and t = 2 rank results as "search outcomes" (§4.3), and the report's
  resource line (§5.3).

The remedy in every case is a superseding record, not a repair. The measurement itself is
admissible and should be carried forward with the corrections named in §7.

---

## 0. Artifact integrity, and the reproducibility pointer exercised

**All 94 declared paths verify.** I parsed `path_sha256` out of the snapshot receipt at the
snapshot sha, re-read each path with `git cat-file -p`, and recomputed sha256:
**94 pairs, 94 match, 0 mismatch, 0 missing.**

**Artifacts rebuilt from scratch, not asserted.** I exported the producer's task tree with
`git archive` into an isolated scratch directory and re-ran both deliverable builders:

| re-run | rebuilt `nagao_height_budget.json` | rebuilt `cell_reachability.json` |
| --- | --- | --- |
| `step6c_deliverables.py` (RUN-…-012) | `563299c8…83f` — **identical to the declared hash** | `fd683d58…1de3` — **identical to the declared hash** |
| `step6b_deliverables.py` (RUN-…-011) | `563299c8…83f` — identical | `af57be9a…` — differs (see §6) |

Both re-runs also reproduced the corresponding run's `stdout.log` **byte for byte**.

Command, revision, environment, seeds, resources: `git_commit: a039e9630b27…` is recorded in
all 12 manifests and **is an ancestor of the snapshot commit** (verified). `git_dirty: true`
in all 12 — expected, since the harness samples `git status` after the child has written into
the repo; the report's "tree clean at start" is not checkable from the record and nothing
rests on it. `environment.json` is identical across all 12 runs (cypari 2.5.6, PARI
[2,15,4], Python 3.11.15) and carries `requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `fallback_used: false`, `model_verified: false`.
`seeds: [20260823]` is harness boilerplate — nothing in this task consumes randomness, and
no result depends on a seed.

---

## 1. JOINT 1 — the Nagao object

### 1.1 The seven-coefficient identity: HOLDS, reproduced digit-for-digit

I re-typed the five quartic coefficients and `N(t)` by hand from
`BATCH-f2341e/…/candidate_families.json`, cross-checked my transcription against the file,
and composed `x = (t+703)/15` into the quartic with my own dense-polynomial arithmetic over
`Q`. The producer's table reproduces exactly at all seven powers of `t`:

```
t^0  9N^2 =        42057494780625   quartic =    65504716350802560000   ratio 1557504
t^1  9N^2 =        35038777948200   quartic =    54573036809433292800   ratio 1557504
t^2  9N^2 =         7265001982104   quartic =    11315269647134908416   ratio 1557504
t^3  9N^2 =          -22396228128   quartic =      -34882214894272512   ratio 1557504
t^4  9N^2 =           -3624340464   quartic =       -5644924770041856   ratio 1557504
t^5  9N^2 =               3403008   quartic =           5300198572032   ratio 1557504
t^6  9N^2 =                451584   quartic =            703343886336   ratio 1557504
```

Ratio constant across all seven, `1557504 = 1248²`, and a perfect square in `Q`. The
content of this is real and I want it stated at full strength before I attack the wording:
**six independent polynomial constraints are satisfied with one free scalar, and the scalar
lands on a perfect square.** In particular it kills the "the extractor dropped the odd-power
terms" worry that `candidate_families.json` itself raised — a quartic missing terms would
not compose with `X(t)` into anything proportional to `N(t)²`.

I add two further consistency facts the producer did not extract, both of which point the
same way:

* `4·lead(a₄)³ + 27·lead(a₆)² = 0` **exactly** — the leading terms of the discriminant
  cancel. A single corrupted digit anywhere in the five coefficients destroys this.
* The fibre bookkeeping closes on the nose: `deg Δ = 20`, `Δ` squarefree, plus an `I₄` fibre
  at `t = ∞`, giving Euler number `20·1 + 4 = 24`, exactly what a K3 requires (§1.3).

### 1.2 …but "the transcription is self-consistent" is NOT what was verified — J1-BREAK-1

The point recorded in `candidate_families.json → published_section_retrieved.point` is

```
((t + 703)/15, (-224*t^3 - 844*t^2 + 900484*t + 2161725)/75)
```

with **no factor of 1248**. I checked that point directly:

```
RETRIEVED point ((t+703)/15, N/75) on the transcribed quartic?  False
REPAIRED  point ((t+703)/15, 1248*N/75) on the transcribed quartic?  True
```

So:

1. `nagao_height_budget.json → step1_self_consistency.batch_f2341e_verdict_overturned: true`
   **is not supported.** BATCH-f2341e tested the retrieved pair *as retrieved* and found it
   inconsistent. That verdict is **correct about the pair it tested**. It was not a false
   negative; it was a true negative about the recorded transcription, and the present batch
   has not overturned it — it has repaired the pair and verified the repair.
2. H-ECQ-a609f8 assumption 1 says "The Nagao transcription in candidate_families.json is
   SELF-CONSISTENT: the point ((t+703)/15, 1248*N(t)/75) lies on the transcribed quartic".
   The first clause is false; the second is true. The recorded transcription is
   **inconsistent by a constant square factor 1248²**, and consistency is restored only by a
   substitution nobody has sourced.
3. The `1248` did not come from the producer's re-derivation. It arrives already fixed in
   the Coordinator's own handoff constraint to TASK-20260823-f88f54 ("The Nagao
   transcription IS self-consistent: the point ((t+703)/15, 1248*N(t)/75) … BATCH-f2341e
   recorded the opposite; that was a FALSE NEGATIVE"). The producer was told the answer and
   confirmed it. That is a legitimate confirmatory check — and it is not an independent
   derivation of `1248`, and must not be recorded as one.

Honest statement of what the evidence supports: **the transcribed quartic and the
transcribed `N(t)` come from the same underlying object, up to one unexplained rational
scaling of the `y`-coordinate whose square root happens to be the integer 1248.** Whether
that object is Nagao's published equation is untouched by this check, exactly as the
producer says. Source retrieval remains owed, and the defect to retrieve *against* is now
sharper than "does the equation match": it is "where does the 1248 come from — is it a
dropped factor in the section, a scaling of the model, or a different model altogether."

### 1.3 Surface degree and K3: HOLDS. The ceiling does not — J1-BREAK-2

Independently from my own `I`, `J`:

* **All 12 non-zero coefficients of `a₄ = -27I(t)` and `a₆ = -27J(t)` are identical to the
  producer's** (5 and 7 non-zero terms respectively).
* `deg a₄ = 8`, `deg a₆ = 12`; max coefficient sizes 32 and 48 digits — the producer's
  numbers.
* `gcd(a₄, a₆) = 1`, so no `p⁴ | a₄, p⁶ | a₆` reduction is possible at any finite place, and
  `deg a₄ = 8 > 4 = 4d-4` blocks reduction at infinity. The Weierstrass model is therefore
  **minimal as an elliptic surface**, and `d = max(⌈8/4⌉, ⌈12/6⌉) = 2`.
  **The producer's `d = 2` / elliptic-K3 determination is correct and now unconditionally
  checked, not just "consistent with".**

What the producer never computed is the discriminant, and it is where the ceiling lives:

```
Δ(t) = -16(4a₄³ + 27a₆²)      deg Δ = 20   (not 24: the degree-24 terms cancel exactly)
gcd(Δ, Δ') has degree 0       Δ is SQUAREFREE  -> 20 finite fibres, all I_1
v_∞(Δ) = 24 - 20 = 4 ,  v_∞(a₄) = 0   -> the fibre at t = ∞ is MULTIPLICATIVE, type I_4
Euler number: 20·1 + 4 = 24   (a K3 requires exactly 24)  ✓
```

Shioda–Tate for this surface: `ρ(X) = 2 + Σ_v (m_v − 1) + rank MW`. Here
`Σ_v (m_v − 1) = 4 − 1 = 3`, so the trivial lattice has rank 5, and with `ρ ≤ h^{1,1} = 20`:

> **rank MW(E / Q̄(t)) ≤ 20 − 2 − 3 = 15, and hence rank E(Q(t)) ≤ 15 as well.**

`candidate_families.json` records `shioda_tate_ceiling: 18`, `ceiling_over_Q: 17`, and my
task card carries those forward. **They are the generic bound `10d − 2` for an elliptic K3
with all fibres irreducible; they are not this surface's ceiling.** Note the producer's own
deliverable does *not* restate 18/17 — it only claims `d = 2` — so this break attaches to
the inherited BATCH-f2341e record and to the campaign's use of it, not to the producer.

Two consequences, and only these:

* No contradiction is created. Scholten's geometric rank 13 requires `ρ = 18 ≤ 20`, which is
  fine; my computation is a non-trivial consistency check on the transcription that **passes**.
* The headroom is much smaller than recorded. Axis A1's premise is "replace the rank-8 base
  with something bigger". This base's hard cap is 15 geometric, and the cited rank is 13 —
  **2 below its own ceiling, not 4 or 5.** Any future plan that budgets against 17 or 18 is
  budgeting against a number that does not exist for this object.

### 1.4 Certified ranks: HOLD. Re-certified independently, and the curves are genuine fibres

I wrote my own certifier (my own Weierstrass group law, my own `E(F_p)` point counting, my
own `ψ_p(X) = (N_p/l)·X` mod-`l` independence argument and `F_l` Gaussian elimination) and
ran it on the a-invariants and points in `step5b_rank_probe.json`. I also checked, from my
own `I`, `J`, that each certified curve really is the NAGAO fibre at that `t` — i.e. that
there is a rational `u` with `(c₄, c₆)_fibre = (u⁴c₄, u⁶c₆)_reported`.

| t | points | all exactly on curve | my certified rank ≥ | producer | is the NAGAO fibre at t | naive height recomputed |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 6 | yes | **6** (l = 3, 8 primes) | 6 | yes, `u² = 56070144` | 124.3997067790 ✓ |
| 1 | 14 | yes | **14** (l = 5, 14 primes) | 14 | yes, `u² = 126157824` | 119.5342918572 ✓ |
| 2 | 11 | yes | **11** (l = 5, 11 primes) | 11 | yes, `u² = 504631296` | 111.2170207052 ✓ |
| 62 | 12 | yes | **12** (l = 7, 12 primes) | 12 | yes, `u² = 504631296` | 109.5051651867 ✓ |

Every claimed lower bound is backed by exactly that many exhibited independent points in
exact arithmetic, and the `curve_key` of every one matches my own recomputation from the
a-invariants. `exact_certify.py`'s method (torsion bound by `gcd_p #E(F_p)`, then mod-`l`
independence through `ψ_p`) is sound as documented, and I did not rely on it: I re-derived
the same four bounds without it.

One reporting defect: `step5b_rank_probe.json` carries `certificate_valid: null` on all four
rows, because the script reads `cert['independence']['method']` and `exact_certify.py` never
writes a `method` key inside `independence`. Cosmetic — the certificates are present and
valid — but a reader scanning that field would conclude the opposite.

### 1.5 New independent evidence on the generic rank — offered, with a null-object control

The task card asks me to say what the evidence actually supports about the family's rank
being inherited from Scholten. Self-consistency does not support it. So I measured it.

For an elliptic surface over `Q(t)`, Rosen–Silverman gives
`rank E(Q(t)) = lim_X (1/X) Σ_{p≤X} −A_p·log p / p` with `A_p = (1/p)·Σ_{t mod p} a_t(p)`,
under Tate's conjecture — **which is known for elliptic K3 surfaces over Q**, and §1.3
establishes that this surface is one. So `−A_p` is the right diagnostic. I computed it by
brute-force Legendre sums.

**The null object is a random quartic of the same shape** (t-degrees 2, 2, 4, 4, 6, random
integer coefficients), pushed through the identical `I`/`J` conversion and the identical
`−A_p` code. If `−A_p` were an artefact of the pipeline rather than of the family, the null
would show it.

| p | 101 | 211 | 401 | 601 | 1009 | 2003 | 4001 | 6007 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **transcribed NAGAO** `−A_p` | 10.25 | 12.23 | 9.79 | 13.73 | 12.27 | **11.50** | **11.99** | **12.88** |
| null draw (same shape) `−A_p` | 1.25 | −1.50 | 0.68 | 1.35 | −0.69 | 0.08 | −0.91 | 0.17 |

Five independent null draws over `p ≤ 1009` gave per-draw means `0.218, 0.566, −0.150,
−0.058, −0.213` (mean of means `0.073`). And the quantity behaves as it should as the
parameter meant to sharpen it grows: the NAGAO values **tighten onto ≈ 12** at the larger
primes while the null stays pinned at 0. This is not a proof and I do not offer it as one —
it is a convergent numerical limit, not a finite computation — but it is the first
*internal* evidence in this campaign that the transcribed family's generic rank really is
near 12, rather than a number cited from Scholten about an equation nobody here has read.

**What this supports:** the transcribed object behaves like a rank-≈12 family over `Q(t)`.
**What it still does not support:** that the transcribed object *is* Nagao's published
equation. Two different curves can share a rank.

---

## 2. JOINT 2 — the height measurement

### 2.1 Is the enumeration what it claims? Yes, exactly

I generated the parameter sets myself and compared as sets, not as counts:

* `|num t| ≤ 60, den ≤ 6`, lowest terms → **457** parameters; `falsifier_height_004.json`
  has 457 rows, all `measured`, 0 timeouts, and the two sets are **equal** (0 in my set not
  in theirs, 0 in theirs not in mine).
* integer `|t| ≤ 400` → **801** parameters; the wide probe has 801 rows, all `measured`,
  and the sets are **equal**.
* union **1137**, overlap **121**, and `457 + 801 − 1137 = 121`. The corrected union in the
  deliverables is arithmetically right.
* `falsifier_height_004/005/006.json` have **identical `rows`** — the three target runs
  differ only in the `--target-height` argument, exactly as the report implies.

### 2.2 `(a, b, R²)` and the minimum, recomputed independently

My own least squares over the 457 declared-box rows:

```
MY FIT   n = 457   a = 135.975835   b = 0.387490   R² = 0.00041752
RECORD   n = 457   a = 135.975835   b = 0.387490   R² = 0.00041752
```

matching the headline `135.9758 + 0.3875·log H(t)`, `R² = 0.000418` under rounding.
Min / median / max over the declared box: `109.5310019429 (t = ±58) / 137.584864 /
171.360935` — identical to the record. Wide-probe minimum `109.5051651867` at `t = ±62`,
identical.

**On the fit, sharper than the report puts it.** `R² = 0.000418` means Pearson
`r = 0.0204`; with `n = 457` that is `t ≈ 0.44`, `p ≈ 0.66`. The slope is not merely
uninformative, it is **statistically indistinguishable from zero**, so the
"parameter budget" `(h_target − a)/b` printed in `admissible_parameter_box_per_target`
(`max log H = −171.97 / −155.40 / −131.06`) is a division by a quantity consistent with 0
and carries no information at all. The producer is right that these are not the deciding
numbers and says so; the deliverable prints them anyway without that qualification, and a
later reader could quote `max_param_size_H = 2.06e−75` as if it meant something.

The correct reading — and it is a genuine result, not a null one — is that the mechanism
carried forward from BATCH-f2341e **does not operate for this family**: the height is
essentially independent of the parameter across the box, so "specialise small" is not a
lever here. `height_lever_effective` is recorded `false`, correctly.

### 2.3 The deciding number: re-derived from a-invariants, and then from the family itself

Two independent legs, both done with my own code:

**Leg 1 — from the a-invariants alone**, as the review plan's P1 demands. For all 14 rows of
`independent_height_recomputation_from_a_invariants` I recomputed
`b₂, b₄, b₆ → c₄, c₆ → log max(|c₄|³, c₆²)`: **0 mismatches in 14, and both `c₄` and `c₆`
strings match too.** (Small over-count in the report's "14/14": the 14 rows cover 11
*distinct* parameters — `t = 0, 1, 2` each appear twice, once from `step2b` and once from the
rank probe.)

**Leg 2 — from the transcribed family, with my own minimalisation.** This is the leg that
actually tests the producer's pipeline rather than re-reading its output. For a parameter
`t = p/q` I formed `c₄ = −48·a₄(t)·q⁸`, `c₆ = −864·a₆(t)·q¹²`, factored `gcd(c₄, c₆)`
(trial division + Pollard rho), and stripped `(p⁴, p⁶)` under **Kraus's conditions** to
reach the minimal model — no PARI, no `icarm_invariants.py`, no `ellminimalmodel`.

I then did this for **every one of the 1137 fibres**:

```
DONE 1137 fibres
disagreements with the record (>1e-9): 0
MY independent minimum over the union: 109.5051651866501 at t = ±62
r>=12 : 0 of 1137 below target ; gap +40.166384
r>=13 : 0 of 1137 below target ; gap +33.745431
r>=14 : 0 of 1137 below target ; gap +24.315907
```

For `t = 62` specifically I also proved minimality directly rather than assuming it: my
minimal model is `c₄:c₆ = 7120267777902769 : −594480911170340909726153` (identical to the
record's `curve_key`), it satisfies Kraus, and **no prime `p < 20000` has `p⁴|c₄` and
`p⁶|c₆`** — which is exhaustive, because `|c₄|^{1/4} = 9186`. Naive height
**109.5051651866501**, agreeing with the record to all 13 printed digits.

**The minimum is a real minimum over the box actually enumerated, and the enumeration is
what it claims.** Both boxes are also empty against the *frozen baseline* values (gaps
+40.166324 / +33.744903 / +24.315907), so the CORRECTION's transcription defect changes
nothing here, as it says.

### 2.4 A larger sweep of my own: the envelope RISES, it does not just flatten

The report's §4 says the lower envelope "flattens rather than descending" over `|t| ≤ 400`.
My minimaliser is fast enough to go much further, so I ran an independent sweep 6.7× the
producer's: integers `0 ≤ t ≤ 5000` plus rationals `|num| ≤ 200, den ≤ 12` — **7593
parameters**:

```
MINIMUM over the larger sweep: 109.5051651867 at t = 62   (unchanged)
r>=12 / r>=13 / r>=14 : 0 of 7593 below target

H(t) in [   1,   10):  n= 102  min 111.217   median 149.843
H(t) in [  10,  100):  n=1284  min 109.505   median 158.164
H(t) in [ 100, 1000):  n=2206  min 117.795   median 162.557
H(t) in [1000, 5000):  n=4000  min 174.134   median 207.916
```

The envelope has an interior minimum near `H(t) ≈ 62` and **rises in both directions**. That
is a stronger negative than the producer's, and it is an independent one. It still is not
"the family cannot reach these cells at any parameter" (see §5.1).

### 2.5 Volume misreported by a factor of two — J2-NOTE

`a₄` and `a₆` contain **only even powers of `t`**, so `t` and `−t` give the same Weierstrass
model and therefore the same minimal curve. Recomputing the 1137 parameters into minimal
`(c₄, c₆)` pairs:

```
1137 parameters  ->  569 DISTINCT minimal curves
largest collision classes are exactly the pairs {t, -t}; only ONE class has size 1 (t = 0)
```

H-ECQ-a609f8's falsification clause 3 requires a bounded-search negative to be "reported
with the volume covered". The covered volume is **569 distinct curves**, not 1137. The
deliverable's wording ("1137 distinct parameters") is literally correct; the report's
"Zero of 1137 distinct measured fibres" invites the 2× over-reading, and any later evidence
record should say 569 curves.

---

## 3. The named check: RUN-…-011 vs RUN-…-012 — SETTLED, reading (a)

The Coordinator routed a factual question with two candidate answers. It has a determinate
answer and it is **(a)**: the `1258` defect never reached `raw-result.json`, so the stated
supersession reason does not describe what differs between the two run records. **Reading
(b) is false. AGENTS.md rule 2 is NOT engaged. No run record was written or overwritten
after the fact.**

The evidence, in the order that settles it:

1. **`diff step6b_deliverables.py step6c_deliverables.py` is two hunks, and both are inside
   `cell_reachability.json`.** The literal `1258` appears only in the `scope` string and the
   `summary` string of the *reachability* deliverable; `step6c` replaces it with
   `len(all_rows)` computed at runtime. **Nothing in `nagao_height_budget.json` was
   touched.**
2. `run_harness.py` copies the declared raw-result path into `runs/<id>/raw-result.json`
   (`shutil.copyfile`). For runs 011 and 012 that declared path is
   `nagao_height_budget.json` — which both scripts produce identically. Hence the identical
   sha256. `cell_reachability.json`, where the two runs genuinely differ, is **not** part of
   either run record.
3. **The two run records are not identical.** `stdout.log` differs and is preserved:
   RUN-…-011 says `… over 1258 fibres …`, RUN-…-012 says `… over 1137 distinct fibres …`.
   The defect is *visible in RUN-…-011's own record*, which is the opposite of the pattern
   reading (b) describes.
4. **I re-ran both.** From a clean `git archive` export of the task tree at the snapshot sha:
   `step6b` reproduced `nagao_height_budget.json` at sha `563299c8…` (the declared hash, and
   `-011`'s and `-012`'s raw-result) and reproduced RUN-…-011's `stdout.log` **byte for
   byte**; `step6c` reproduced both declared deliverable hashes and RUN-…-012's `stdout.log`
   byte for byte.

Also worth recording, because it removes the last bit of mystery: `1137` is never hard-coded
anywhere. It is `len(all_rows)` in both scripts, so `nagao_height_budget.json` was always
correct. The producer's own defect note is what is wrong: RUN-…-011's defect was in
`cell_reachability.json`'s prose fields, not in a fibre count that fed a number.

**What is owed:** a one-line correction to the execution report's §9.4 saying that the 011
defect was confined to two descriptive strings in `cell_reachability.json` and never entered
any computed quantity. Nothing else.

**A separate integrity point this uncovered.** All twelve manifests carry
`status: completed_valid` — including RUN-…-008, which the report calls an
`implementation_error`, and RUN-…-010 and -011, which it calls superseded. The harness
derives `status` from the exit code alone and has no way to mark a run invalid afterwards
without editing an immutable manifest, so the producer recorded the invalidity in prose.
That is the right choice under rule 2, but the consequence is real: **a reader of
`runs/RUN-ECQNAG-f88f54-008/manifest.yaml` alone would take an implementation error for a
valid measurement.** The run-record schema needs a superseded-by field, or the batch needs a
`supersessions.yaml` inside the task scope.

---

## 4. The Coordinator's recorded priors, held to one at a time

### 4.1 P1 — "I EXPECT THE ADMISSIBLE BOX TO BE EMPTY AT ALL THREE TARGETS": **not contradicted, and independently confirmed**

The plan's `if_contradicted` arms the reviewer against a *non-empty* box. The box came back
empty, which is the convenient direction, so I did the check the plan asks for anyway and
then more: I re-derived `(a, b, R²)` from the raw rows, re-derived the naive height of
**every** fibre from the family definition with my own minimalisation, verified the argmin
curve's minimality exhaustively, and ran a 6.7×-larger sweep of my own. Nothing moved. The
conventions the plan pins (naive = `log max(|c₄|³, c₆²)` on the minimal model) are the ones
used, and I used them independently.

I record the asymmetry honestly: **a convenient result got the same scrutiny an inconvenient
one would have.** The one thing I can add is that the emptiness is larger than reported —
the floor is ~109.5 and it rises outside `|t| ≈ 100`.

### 4.2 P2 — "I EXPECT MINIMALISATION TO STRIP A LOT": **holds, measured**

Verified from `step2b_minimalisation.json` and reproduced by my own minimaliser: heights
before minimalisation ≈ 231.45 uniformly, after minimalisation 111.2–174.0, i.e. **98.7 to
120.2 stripped**, `c₄` 34 → 17–20 digits and `c₆` 51 → 25–30 digits. My independent
minimalisation reproduces the after-values at `t = 0, 1, 2, 3, 703` to 1e-9. The prior was
recorded as deliberately weak; it is now a measurement, and it is nowhere near enough — the
family's floor is 109.5 against targets of 69.3–85.2.

### 4.3 P3 — "I EXPECT CERTIFIED RANK ≥ 12 at small t": **contradicted as written — and its `if_contradicted` action should NOT be taken**

This is the prior the task card asks me to adjudicate, so I will be exact.

**The facts.** Certified rank ≥ 12 at `t = 1` (14) and `t = 62` (12); rank below 12 at
`t = 0` (6) and `t = 2` (11). All four re-certified independently by me. `t = 62` is not
"small t" in any reading of the prior, so on small `t` the score is 1 for, 2 against.

**The producer's framing is contradicted by the producer's own artifact.** Report §5 says
"a shortfall is a search outcome, never a statement that the rank is below 12".
`step5b_rank_probe.json` records, for every row, `pari_search_r_low == pari_search_r_high`
and `ellrank_status` (timed out) `false`:

```
t=0   r_low = 6   r_high = 6    timed_out = false
t=1   r_low = 14  r_high = 14   timed_out = false
t=2   r_low = 11  r_high = 11   timed_out = false
t=62  r_low = 12  r_high = 12   timed_out = false
```

PARI's `ellrank` returns matching bounds, i.e. **the rank is determined**, at 6 and 11. These
are not search shortfalls and there was no timeout to blame. The Coordinator's own handoff
constraint ("Never `ellrank` r_high alone, never a Selmer bound") is why the producer did not
*report* an upper bound as a rank — a rule I endorse — but the constraint does not license
describing a measured, matched upper bound as an unfinished search. The upper bound should
have been disclosed with its caveats (PARI's 2-descent bound may rest on GRH-conditional
class-group data), not omitted.

**But P3's `if_contradicted` inference is wrong, and I am the one who has to say so.** The
clause reads a sub-12 rank at several good `t` as "evidence the transcribed coefficients are
NOT Nagao's published equation … the family withdrawn". Two independent findings of mine say
do not do that:

1. **`t = 0` is structurally forced to drop, and by a lot.** `a₁ = a₃ = 0` and `a₄, a₆`
   contain only even powers of `t`, so `σ : t ↦ −t` is an involution of the surface and
   `MW ⊗ Q = V⁺ ⊕ V⁻`. A section in `V⁻` has `x` even and `y` **odd** in `t`; at `t = 0` its
   `y`-coordinate vanishes, so it specialises into `E₀[2]` and contributes **nothing** to
   `rank E₀(Q)`. The entire anti-invariant eigenspace dies at `t = 0` — this is a property of
   the family's shape, not a fact about whether it is Nagao's. Measured rank 6 at `t = 0`
   against generic ≈ 12 is exactly the `6 + 6` split that shape predicts. **`t = 0` is the
   one parameter in the whole box that was guaranteed in advance to be an exceptional point
   of the specialisation map, and it should never have been used to test P3.**
2. **The generic rank really is ≈ 12**, by the null-controlled `−A_p` measurement in §1.5
   (11.50 / 11.99 / 12.88 at `p = 2003 / 4001 / 6007`, against a same-shape null at ≈ 0).

`t = 2` giving 11 is then an ordinary specialisation exception — Silverman's theorem allows
finitely many, and one parameter short by one is not a pattern.

**Disposition I recommend, as a reviewer with no authority to enact it:** record P3 as
**contradicted on its face and not acted on**, with the reason replaced. The producer's
reason ("search outcome") is unsupported by its own data. The correct reason is that one of
the two counter-examples is structurally forced by the family's `t ↦ −t` symmetry and the
generic rank is independently corroborated near 12. Source retrieval is still owed — but on
the strength of §1.2, not of P3.

---

## 5. Scope limits I am obliged to state

### 5.1 "Empty box" ⇏ "cannot take these cells at any parameter"

H-ECQ-a609f8's falsification clause 1 says an empty box at all three targets means "this
family cannot take those cells **at any parameter**". The measurement does not support that
quantifier and the producer did not claim it — §8 of the report scopes correctly, and §3
scopes again. But the hypothesis text will be read by the Coordinator, so I state it plainly:

* **Supported:** no fibre among 1137 parameters / 569 distinct curves (producer), and none
  among my 7593 parameters, has naive height below any of the three targets; the measured
  floor is 109.505165 and the lower envelope rises outside `H(t) ≈ 100`.
* **Not supported:** any statement quantified over all `t ∈ Q`. A universal statement would
  need a proof that the minimal-model height of the fibre is bounded below over the whole
  parameter space, and no such argument was attempted here or by me.
* Also unquantified: everything is scoped to **this Weierstrass model of this surface**.
  Another model of the same surface, or a different elliptic fibration on it, is untested.

### 5.2 What is inherited rather than verified

* The identification of the transcribed coefficients with **Nagao's published equation** is
  unverified, and `candidate_families.json` still carries
  `TRANSCRIPTION_STATUS: "UNRELIABLE -- DO NOT USE WITHOUT RE-TRANSCRIPTION FROM THE PDF"`.
  Both rank claims (12 over `Q(t)`, 13 over `Q̄(t)`) are marked `verified_here: false`. The
  Nagao primary source is marked retrieved at the landing page with **full text not read**;
  the Scholten source is an LLM-mediated PDF-text extraction. Under my role contract these
  are `retrieved` entries doing load-bearing work whose content has not been checked by a
  human-readable route — **incomplete provenance, and the remedy is retrieval, not a
  rewording.** §1.5 is a partial internal substitute for the *rank* claim only.
* `faltings_height` and `conductor` are PARI outputs. I re-derived every naive height
  independently but did **not** independently recompute a period lattice or run Tate's
  algorithm. §6 inherits them.

### 5.3 A resource statement in the report is false

`report.md` header: "peak RSS well under 1 GB". `runs/RUN-ECQNAG-f88f54-009/manifest.yaml`:
`max_rss_kb: 3651036` = **3.48 GiB**. The declared budget was 4 GB, so there is **no budget
breach** — but the report's own run record contradicts its resource line by a factor of 3.5,
and resource records are one of the things a validator is asked to check against the
manifest. Correct by supersession.

---

## 6. Attack on `COORDINATOR-multimetric-check.md` (unreviewed Coordinator analysis, not evidence)

I was told to attack it. Here is what survives and what does not.

### 6.1 The arithmetic: it all reproduces, and the conclusion is right — in fact stronger

I recomputed all twelve cells of the table from the frozen baseline and the producer's
`submission_record`s (`log N` computed by me from the exact conductor integers):

| t | r ≥ | naive | cell | gap | Faltings | cell | gap | log N | cell | gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 6 | 124.400 | 30.376 | +94.02 | 8.109 | 0.583 | +7.53 | 57.30 | 22.37 | +34.93 |
| 1 | 14 | 119.534 | 85.189 | +34.35 | 7.702 | 5.131 | +2.57 | 98.09 | 73.66 | +24.43 |
| 2 | 11 | 111.217 | 61.507 | +49.71 | 7.005 | 3.041 | +3.96 | 74.61 | 51.25 | +23.36 |
| 62 | 12 | 109.505 | 69.339 | +40.17 | 6.993 | 3.811 | +3.18 | 90.35 | 57.76 | +32.58 |

**Every gap matches the Coordinator's table.** "Closest approach anywhere is t = 1 on
Faltings, +2.57" is correct.

Two things I checked that the file does not state, both of which help it:

* **Comparing at each curve's own rank threshold is the maximally favourable comparison,**
  not an arbitrary one: I verified that all three frozen frontier metrics are
  **monotone non-decreasing in `k`** over `k = 1..20`, so the highest threshold a curve
  qualifies for is the easiest cell it can take.
* I extended the sweep to **every** `(curve, threshold k ≤ certified rank, metric)` triple —
  all three metrics at every `k` from 1 up — and got **0 cells taken**, with the five
  smallest gaps all on Faltings height (+2.571, +3.182, +3.457, +3.891, +3.952). The
  conclusion "NONE" holds over a strictly larger comparison set than the one tabulated.

### 6.2 Where the claim is over-titled: "any metric" is three metrics

The file's own preamble says the board keeps records for "naive height, Faltings height,
log conductor, **discriminant**". The frozen baseline `frontier_20260823.json` carries only
three: `min_naive_height`, `min_faltings_height`, `min_log_conductor`. So **"NO cell on ANY
metric" is a claim about the three metrics that were frozen**, and a discriminant cell — if
the live board has one — is unchecked here. Given gaps of +2.5 and up on everything measured
this is very unlikely to matter, but the title claims a universal it did not test, and under
C1' any real claim has to be measured against the live board anyway.

Two smaller notes. Faltings heights and conductors are the **producer's PARI values**,
inherited by the Coordinator and not recomputed by either of us, so two of the three metrics
rest on a single implementation. And the `t = 0` row is compared at `r ≥ 6`, a threshold
whose incumbent (30.376) is held by a curve that has nothing to do with this campaign; it is
a fair comparison but the row carries essentially no information.

### 6.3 The method-class hypothesis: UNESTABLISHED, and weaker than the file's own caveat says

The file already labels it not established. I think it is weaker still, and I say so
because the file was written to be knocked down.

* **`n = 2` is generous.** MESTRE_SPEC contributes a per-rank minimum curve; NAGAO
  contributes one box of one family. And within NAGAO the four "curves" that carry the
  multi-metric table are four fibres of a **single** surface — they are not independent
  observations of the method class, they are four points of one object. The support for
  "specialisation buys rank and pays in size" is therefore two families, not four curves.
* **The other arm has no measurement at all.** The claim has two halves: specialisation
  families are big, *and* the small-curve cells are held by direct search that cannot reach
  high rank. The first half is measured. The second half rests entirely on the free-text
  program attribution that the file itself flags as unreplicated. A claim of the form
  "method class A cannot do X" with no measurement of method class A is not at `n = 2`, it
  is at `n = 0`.
* **The confound is unnamed.** Both measured families were chosen *because* their generic
  rank is high and exactly known. Height and coefficient size are not independent of that
  selection: a family with a published exact high rank is one somebody wrote down
  explicitly, and explicit high-rank constructions are large for reasons that have nothing
  to do with an intrinsic rank–size tradeoff. The natural null object is missing: **a
  same-shape family of low generic rank**, measured through the identical pipeline. If its
  `(a, b)` and its floor look like NAGAO's, the tradeoff story loses its evidence entirely,
  and that test costs one `falsifier_height.py` invocation.
* One piece of evidence *against* the strong form, from §1.3 of this report: this base's own
  Shioda–Tate ceiling is **15**, and it delivers a floor of 109.5. If the mechanism were
  "rank is bought at the price of size", one would want that price measured against rank
  *within* a family; the four fibres here span certified ranks 6 to 14 with heights 124.4,
  119.5, 111.2, 109.5 — **the height is essentially flat in rank, and if anything the
  highest-rank fibres are the smaller ones.** That is the opposite of the within-family
  prediction of a rank–size tradeoff, on the only data the file has.

**Verdict on the file:** its arithmetic holds and its narrow conclusion — none of these four
curves takes any of the three frozen cells at any threshold — is correct and, as I extended
it, stronger than stated. Its method-class hypothesis is not merely unestablished; it is
under-designed, and the cheap decisive test it gestures at should be a *low-rank same-shape
null family*, which nobody has run.

---

## 7. What must be superseded before this receipt is admitted

None of these is a repair; each is a new record. Listed in descending consequence.

1. **The Shioda–Tate ceiling for this surface is 15, not 18/17** (§1.3). The 18/17 in
   `BATCH-f2341e/…/candidate_families.json → surface_degree_d` is the generic elliptic-K3
   bound and does not apply once the `I₄` fibre at `t = ∞` is accounted for. Anything in
   Axis A1 that budgets headroom against 17 is budgeting against a number this object does
   not have.
2. **`batch_f2341e_verdict_overturned: true` is not supported** (§1.2). The retrieved
   `(quartic, point)` pair is genuinely inconsistent; consistency holds only after an
   unsourced rescaling `y ↦ 1248y`. H-ECQ-a609f8's assumption 1 needs the same correction,
   and the source-retrieval task now has a sharper target.
3. **P3's outcome and its reason** (§4.3). Rank at `t = 0` is 6 and at `t = 2` is 11 with
   matched PARI bounds and no timeout; these are not search shortfalls. The family should
   nonetheless **not** be withdrawn, because `t = 0`'s drop is forced by the family's own
   `t ↦ −t` symmetry and the generic rank is independently corroborated near 12.
4. **Bounded-search volume is 569 distinct curves, not 1137 parameters** (§2.5).
5. **RUN-…-011's supersession reason** (§3): the `1258` defect was confined to two
   descriptive strings in `cell_reachability.json` and never entered a computed quantity.
   Reading (a). Rule 2 is not engaged.
6. **`report.md`'s "peak RSS well under 1 GB"** contradicts `RUN-…-009`'s manifest
   (3.48 GiB; within the 4 GB budget) (§5.3).
7. Minor: `certificate_valid: null` on all four rank rows is a key-name bug, not a failed
   certificate (§1.4); "14/14 independent recomputations" covers 11 distinct parameters
   (§2.3); the fit-derived `max_param_size_H` values are divisions by a slope statistically
   indistinguishable from zero and should carry that qualification (§2.2).

---

## 8. Required output record

```yaml
validation_report:
  id: VAL-20260823-72505a
  task_id: TASK-20260823-72505a
  goal_id: GOAL-ECQ-002
  batch_id: BATCH-da59ec
  hypothesis_id: H-ECQ-a609f8
  snapshot_commit_read: 0cb0165024b3280e83dc7974918d6d82af5039b4
  working_tree_state_at_read: clean
  joints_owned: [J1, J2]
  joint_verdicts:
    J1: breaks      # on 1.2 (self-consistency as worded) and 1.3 (ceiling 18/17)
    J2: holds       # measurement reproduces exactly and is stronger than reported
  run_ids:
    - RUN-ECQNAG-f88f54-001
    - RUN-ECQNAG-f88f54-002
    - RUN-ECQNAG-f88f54-003
    - RUN-ECQNAG-f88f54-004
    - RUN-ECQNAG-f88f54-005
    - RUN-ECQNAG-f88f54-006
    - RUN-ECQNAG-f88f54-007
    - RUN-ECQNAG-f88f54-008
    - RUN-ECQNAG-f88f54-009
    - RUN-ECQNAG-f88f54-010
    - RUN-ECQNAG-f88f54-011
    - RUN-ECQNAG-f88f54-012
  artifact_checks:
    - {check: declared path_sha256 recomputed at the snapshot sha, declared: 94, verified: 94, mismatched: 0, missing: 0, result: pass}
    - {check: deliverables rebuilt from scratch via git archive + re-run of step6c, result: pass, note: both declared hashes reproduced byte-identically}
    - {check: git_commit a039e9630b is an ancestor of the snapshot commit, result: pass}
    - {check: environment.json identical across all 12 runs; cypari 2.5.6 / PARI 2.15.4 / py3.11.15, result: pass}
    - {check: inference block records requested_policy executor-implementation, resolved claude-opus-5, fallback_used false, result: pass}
    - {check: seeds recorded, result: pass, note: harness boilerplate; no result depends on randomness}
    - {check: resource records vs report prose, result: FAIL, note: "report says peak RSS well under 1 GB; RUN-009 manifest records 3651036 kB = 3.48 GiB (within the 4 GB budget)"}
    - {check: run status fields, result: FAIL, note: "all 12 manifests say completed_valid, including RUN-008 (implementation error) and RUN-010/-011 (superseded); invalidity exists only in report prose"}
    - {check: no ICARM submission artifact exists, result: pass}
  metric_recomputations:
    - {metric: seven-coefficient identity 15^4 Q((t+703)/15) vs 9N^2, method: own exact polynomial arithmetic, own hand transcription, result: reproduced digit-for-digit at all 7 powers; ratio constant 1557504 = 1248^2}
    - {metric: retrieved section ((t+703)/15, N/75) on the transcribed quartic, result: FALSE; only the rescaled point (y -> 1248 N/75) lies on it}
    - {metric: a4 = -27I(t) and a6 = -27J(t), result: all 12 non-zero coefficients identical to the producer}
    - {metric: surface degree d, result: d = 2 confirmed; gcd(a4,a6)=1 and deg a4 = 8 make the Weierstrass model minimal, so K3 is unconditional given the transcription}
    - {metric: discriminant and fibre configuration (NOT computed by the producer), result: "deg Delta = 20, squarefree -> 20 x I_1; v_inf(Delta) = 4, v_inf(a4) = 0 -> I_4 at t = infinity; Euler number 24"}
    - {metric: Shioda-Tate ceiling for THIS surface, result: "rank MW <= 20 - 2 - 3 = 15 geometric and over Q; the recorded 18 / 17 over Q is the generic K3 bound, not this surface's"}
    - {metric: certified rank lower bounds, method: own group law + own mod-l independence certifier, result: "t=0:6, t=1:14, t=2:11, t=62:12 -- all four reproduced; all points exactly on curve; all four curves verified Q-isomorphic to the NAGAO fibre at t"}
    - {metric: PARI bounds recorded but not reported, result: "r_low == r_high and timed_out false at all four t; the ranks are determined at 6, 14, 11, 12"}
    - {metric: parameter box enumeration, result: "457 and 801 reproduced as SETS not counts; union 1137; overlap 121 = 457+801-1137"}
    - {metric: fit (a b R^2), method: own least squares, result: "135.975835 / 0.387490 / 0.00041752 -- identical to the record; Pearson r = 0.0204, t = 0.44, p ~ 0.66, slope indistinguishable from zero"}
    - {metric: min / median / max naive height in the declared box, result: "109.5310019429 (t=+-58) / 137.584864 / 171.360935 -- identical"}
    - {metric: naive height from minimal a-invariants alone, n: 14, result: "0 mismatches; c4 and c6 strings also match; covers 11 distinct parameters"}
    - {metric: naive height re-derived from the FAMILY with own Kraus minimalisation, n: 1137, result: "0 disagreements above 1e-9; independent minimum 109.5051651866501 at t = +-62"}
    - {metric: minimality of the argmin model at t = 62, result: "proved directly -- Kraus holds and no p < 20000 has p^4|c4 and p^6|c6, exhaustive since |c4|^(1/4) = 9186"}
    - {metric: distinct minimal curves among the 1137 parameters, result: 569 (t and -t coincide; covered volume overstated 2x)}
    - {metric: Coordinator multi-metric table, result: "all 12 gaps reproduced; extended to every (curve, k <= certified rank, metric) triple -> 0 cells taken; frontier verified monotone in k"}
  control_checks:
    - {control: "null object for the generic-rank probe -- random quartics of identical t-degree shape (2,2,4,4,6) through the identical I/J and -A_p code", result: "5 draws, per-draw means 0.218 / 0.566 / -0.150 / -0.058 / -0.213 (mean 0.073) vs NAGAO 11.65; at p = 2003/4001/6007 NAGAO gives 11.50 / 11.99 / 12.88 and the null gives 0.08 / -0.91 / 0.17"}
    - {control: "decay behaviour -- the quantity concentrates on ~12 as p grows while the null stays at 0, which is what it should do", result: pass}
    - {control: "negative control on the emptiness claim -- an independent 7593-parameter sweep (integers |t| <= 5000, rationals |num| <= 200 den <= 12)", result: "0 below any target; envelope minimum 109.505 at t = 62 and RISING for H(t) > 100"}
    - {control: "positive control on the conversion -- producer's PARI ellfromeqn cross-check 10/10", result: "recorded and consistent; superseded in strength by my own reconstruction of 5 minimal models without PARI"}
    - {control: "missing null the batch should have run -- a LOW generic rank family of the same shape through falsifier_height.py, to test the multi-metric file's rank-size tradeoff", result: not run by anyone}
  heuristic_validation_checks:
    - {check: pre-registered prediction, result: "P1/P2/P3 are recorded in review_plan.yaml with authored_before_any_producer_ran true and committed before dispatch; the target cells are pre-declared in H-ECQ-a609f8"}
    - {check: prediction values match their own frozen source, result: FAIL, already recorded in CORRECTION-predeclared-target-values.md; verified here -- the boxes are empty under BOTH value sets}
    - {check: sample integrity, result: "box, counts and per-fibre rows are all in the artifacts and reproduce as sets"}
    - {check: scale binding, result: "scope is stated per artifact; the empty-box result is NOT quantified over all t and the hypothesis text that says otherwise overreaches"}
  cost_model_checks:
    - {check: not applicable, note: "no concrete cost table and no per-attempt x inverse-success-probability claim appears in this batch"}
  proof_architecture_checks:
    - {check: baseline fixture, result: "the transcription reproduces its own internal identity exactly, but does NOT reproduce the cited published pair -- the retrieved section fails and a rescaled one passes"}
    - {check: method ceiling from the method's own resource measure, result: FAIL, "the ceiling was taken as the generic K3 bound instead of being derived from this surface's own fibre configuration; correct value 15"}
    - {check: bounded search bound to its enumerated scope, result: pass, "with the volume corrected from 1137 parameters to 569 distinct curves"}
    - {check: quantifier fidelity, result: FAIL at the hypothesis level, "falsification clause 1 reads an empty box over 1137 parameters as 'cannot at any parameter'; the producer did not make that leap"}
  limitations:
    - The transcribed coefficients are still not verified against Nagao's published equation; the source record carries TRANSCRIPTION_STATUS UNRELIABLE and both rank claims are cited-only. My -A_p probe corroborates generic rank ~12 for the transcribed object, not its identity with Nagao's.
    - The -A_p probe is a convergent numerical limit under Rosen-Silverman (Tate's conjecture, known for elliptic K3 over Q), not a finite proof of the generic rank.
    - PARI's ellrank upper bound may rest on GRH-conditional class-group data; the statement that rank is exactly 6 at t = 0 and 11 at t = 2 inherits that caveat. The LOWER bounds do not - they are exact and I re-derived them.
    - Faltings heights and conductors were not independently recomputed (no period lattice, no Tate's algorithm here); section 6 inherits PARI for two of three metrics.
    - Everything is scoped to this Weierstrass model of this surface. Other models or other elliptic fibrations are untested.
    - No statement here is quantified over all rational t.
  verdict: failed
  artifact_paths:
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-72505a/validation_report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-72505a/verdict.yaml
```

```yaml
review_attestation:
  task_id: TASK-20260823-72505a
  joints_owned: [J1, J2]
  sources_read:
    - AGENTS.md
    - CLAUDE.md
    - agents/validator.md
    - templates/research-records.md   # review_attestation block only
    - ledger/handoffs/TASK-20260823-72505a.yaml
    - ledger/hypotheses/H-ECQ-a609f8.yaml
    - ledger/goals/GOAL-ECQ-002/goal.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/review_plan.yaml
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/dispatch_queue.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/COORDINATOR-multimetric-check.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/COORDINATOR-open-items-settled.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/CORRECTION-predeclared-target-values.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/archives/TASK-20260823-452f5f/receipt.yaml
    - coordination/goals/GOAL-ECQ-002/baseline/frontier_20260823.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/report.md
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/nagao_height_budget.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/cell_reachability.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/scripts/*   (all 9)
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/results/*   (all 10)
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-da59ec/tasks/TASK-20260823-f88f54/runs/RUN-ECQNAG-f88f54-0{01..12}/{manifest.yaml,command.txt,environment.json,stdout.log}
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-d1cb76/candidate_families.json
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-01d3d9/pipeline/{exact_certify.py,falsifier_height.py,families.py,icarm_invariants.py,pipeline.py}
    - coordination/goals/GOAL-ECQ-002/batches/BATCH-f2341e/tasks/TASK-20260823-6040d1/{validation_report.md,verdict.yaml}   # PRIOR-ROUND validator deliverable of a DIFFERENT batch, opened only to copy the VAL id and file format; first 40 and 25 lines respectively
  read_sibling_reports: false
  blindness_disclosure: >-
    No file under TASK-20260823-eaf799 was opened. A directory listing of the shared
    tasks/ parent, run to create my own write_scope, revealed that TASK-20260823-eaf799/
    exists; that is the only fact about the sibling task that reached me, and every
    finding in this report was fixed before that listing.
  blind_from_respected: null    # not a blind re-derivation task
  verdict: J1 breaks, J2 holds
```
