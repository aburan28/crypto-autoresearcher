# TASK-20260724-234 — Validator notes on EXP-XEDN-002

Independent integrity validation of the EXP-XEDN-002 exact xedni census produced
by TASK-20260724-229 and snapshot-committed by TASK-20260724-231.

- Snapshot commit validated: `9f9186c65257aa30458c56d435bc6289e6aaeed7`
  (parent `68e375f720123d4f46b1b5bc686920d77bf5ecf4`).
- `HEAD` at validation time: `ae5503dc288efe74f23a870c59d5870c5f779d72`,
  working tree clean before and after every check.
- Terminal verdict: **passed** / `valid_with_findings`. Integrity only. This says
  nothing about whether the mathematics answers the intended question.

This document is ordered so that the independent derivation comes **before** any
statement about what the executor wrote, because that ordering is the whole point
of the check.

---

## 1. Independent derivation, done before reading `derivation.md`

I read only the frozen contract (`experiments/EXP-XEDN-002/specification.yaml`)
and the frozen predicate (`experiments/EXP-XEDN-001/xedni_sections.py`) before
writing this section. Coefficient convention: index `i` is the coefficient of
`t^i`, matching the frozen module.

### 1.1 What the frozen predicate actually accepts

`is_square_poly(f, p)` performs, in order:

1. reject if `len(f)` is even, i.e. if `deg f` is odd (after `trim`);
2. reject unless `lc(f)^((p-1)/2) == 1`, i.e. unless `lc(f)` is a **nonzero**
   quadratic residue — this is what rejects the zero polynomial, since
   `trim` sends `f = 0` to `[0]`, `lc = 0`, and `0^((p-1)/2) = 0 != 1`;
3. set `h = gcd(f, f')`, normalised monic;
4. reject unless `2 deg h == deg f`;
5. accept iff re-squaring verifies, `f == lc(f) * h^2`.

Write `f = c g^2` with `g` monic of degree `d` and `c != 0`. Then
`f' = 2 c g g'`, so `gcd(f, f') = g * gcd(g, g')` and
`deg gcd(f,f') = d + deg gcd(g,g')`. Step 4 therefore holds **iff**
`gcd(g, g') = 1`, i.e. iff `g` is squarefree. (If `g' = 0` then
`gcd(g,g') = g`, giving `deg h = 2d != d` for `d >= 1`; the degenerate `d = 0`
case is a nonzero constant, where `pgcd(f, [0])` returns `[1]`, `deg h = 0`, and
the re-squaring check passes.) Step 2 forces `c` to be a QR, so `c = e^2` and
`f = (e g)^2`.

> **Conclusion (mine).** `is_square_poly(f, p)` accepts `f` **iff**
> `f = y^2` for some nonzero **squarefree** `y in F_p[t]`.

Two consequences I noted before reading the executor's text:

- The predicate implicitly requires the square root to be **squarefree**, so it
  is a *strictly narrower* test than "is a perfect square". `f = 4 t^6 = (2t^3)^2`
  at `p = 5` is a genuine square that the predicate **rejects**.
- `y = 0` is excluded, so slots whose only section is the two-torsion `y = 0`
  section do not count.

I then verified this characterisation **exhaustively**, not by argument alone:
for every one of the `p^7` polynomials of degree `<= 6` at `p = 5` (78,125) and
`p = 7` (823,543) I compared my set `{ y^2 : y != 0 squarefree, deg y <= 3 }`
against the frozen oracle. **Zero disagreements at both sizes**
(`/tmp` script `validator_derive.py`; results reproduced in §5 below). The set of
`f` reachable from a slot is a subset of "degree `<= 6`", so this is strictly
stronger than the contract's "every enumerated slot at `p in {5,7}`".

### 1.2 `N_slots(p)`

`b` has 7 coefficients with `b_6 != 0`: `(p-1) p^6` choices. `x = t^2 + x_1 t + x_0`
has 2 free coefficients: `p^2` choices. Hence

```
N_slots(p) = (p-1) p^6 * p^2 = (p-1) p^8 .
```

### 1.3 `N_hit(p)`

Fix `x`. The map `b |-> f := x^3 + b` is a coefficient translation on `F_p^7`,
hence a bijection. Since `x^3` is monic of degree 6, `[t^6] f = 1 + b_6`, so
`b_6 != 0` corresponds exactly to `[t^6] f != 1`, and the lower coefficients of
`f` are unconstrained. The image set `F = { f : deg f <= 6, [t^6] f != 1 }`
does **not depend on `x`**, so

```
N_hit(p) = p^2 * M(p),   M(p) = #{ f in F : f = y^2, y != 0 squarefree } .
```

`deg f = 2 deg y <= 6`, so `deg y in {0,1,2,3}`. Let `Q_n` be the number of
**monic** squarefree polynomials of degree exactly `n`:
`Q_0 = 1`, `Q_1 = p`, `Q_n = p^n - p^{n-1}` for `n >= 2` (from
`Z(u) = Z(u^2) S(u)` with `Z(u) = 1/(1-pu)`, i.e. `S(u) = (1-pu^2)/(1-pu)`).
Writing `f = c g^2` with `g` monic squarefree and `c` a nonzero QR
(`(p-1)/2` values), and noting `[t^6] f = c` when `deg g = 3` (so the membership
condition `c != 1` removes exactly one QR):

| `deg y` | count of admissible `f` |
|---|---|
| 0 | `(p-1)/2` |
| 1 | `p (p-1)/2` |
| 2 | `(p^2-p)(p-1)/2` |
| 3 | `(p^3-p^2)(p-3)/2` |

Summing:

```
2 M(p) = (p-1) + (p^2-p) + (p^3-2p^2+p) + (p^4-4p^3+3p^2)
       = p^4 - 3p^3 + 2p^2 + p - 1     (even for odd p)
```

so my independent closed form is

```
validator_N_slots(p) = (p-1) p^8
validator_N_hit(p)   = p^2 (p^4 - 3p^3 + 2p^2 + p - 1) / 2
```

### 1.4 Comparison with the executor

The executor's `derivation.md` §1.1–§1.5 states

```
executor_N_slots(p) = (p-1) p^8
executor_N_hit(p)   = p^2 (p^4 - 3p^3 + 2p^2 + p - 1) / 2
```

**These agree exactly, symbol for symbol.** My derivation was written from the
frozen contract and the frozen predicate alone, and it independently reproduces
the same four degree strata, the same `(p-3)` leading-coefficient restriction at
`deg y = 3`, the same 2-to-1 `±y` factor, and the same squarefree requirement.
The formula is therefore **derived, not fitted**: the two independent routes
produce the same polynomial, and the small-`p` brute force below produces the
same integers.

I also confirmed the executor's exact identity, which I had not derived myself:
`2 p^3 P_lift = 1 - 2/p + p^{-3}`, since
`(p^3 - 2p^2 + 1)(p-1) = p^4 - 3p^3 + 2p^2 + p - 1`. This is an identity, not an
expansion, so `alpha = 3` exactly in the limit and `alpha_eff < 3` at every
finite pair.

### 1.5 Full slot-space brute force, my own code

Written by me; imports **nothing** from `experiments/EXP-XEDN-002/implementation/`.
It loads only the frozen predicate by file path (read-only) and enumerates every
`(b, x)` pair with `deg b = 6` exactly and `x` monic quadratic — no use of the
fibering bijection.

| `p` | slots enumerated | my hits | my closed form | executor closed form | agree |
|---|---|---|---|---|---|
| 5 | 1,562,500 (= full space) | **3,800** | 3,800 | 3,800 | yes |
| 7 | 34,588,806 (= full space) | **36,162** | 36,162 | 36,162 | yes |

Also produced by the same enumeration:

- slots with `x^3 + b == 0` identically: **25 at `p = 5`, 49 at `p = 7`**, i.e.
  exactly `p^2`, all rejected by the frozen predicate. This independently
  confirms the degenerate-`y = 0` control.
- genuine perfect squares the predicate rejects (non-squarefree root):
  60 of 312 `f`-values at `p = 5`, 168 of 1,200 at `p = 7`; in slot terms
  `4,675 - 3,800 = 875` at `p = 5`, matching the executor's
  `p^2 * p(p^2-2p-1)/2`. My witnesses include `y = t^3` giving `f = t^6`, and
  `y = 2t^3` giving `f = 4t^6`, both rejected.

Since `P_lift = M(p) / ((p-1) p^6) ~ 1/(2p^3)` under either semantics, this
predicate narrowness changes the **constant**, never the exponent.

---

## 2. Each required check

### 2.1 Artifact completeness and run schema — pass

Five run directories, each containing exactly `manifest.yaml`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log`, `raw-result.json` and nothing
else. Every manifest has a top-level `run` key and non-empty `id`,
`experiment_id`, `status`, `code` (with `commit`, `command`, `entrypoint`,
`dirty_tree`, `frozen_predicate_sha256`), `environment`, `inputs` (with
`parameters` and `seeds`), `timing`, `result`. `inputs.parameters.field_bits` is
10 in every run (`<= 32`, claim tier stays `toy`). Every
`result.certificate.kind` is `none`, which is in the allowed set. Every
`command.txt` contains the manifest's `code.command` verbatim. Every
`environment.json` records Python 3.12.3, numpy 2.4.4, sympy 1.14.0, pyyaml
6.0.1 and the frozen-predicate SHA-256.

`sha256sum experiments/EXP-XEDN-001/xedni_sections.py` =
`76f0cfe2f32362ff1110fc7c7b42db40d293099ae7718927c46223a42450b34f`, matching the
value recorded in `derivation.md`, `execution-report.yaml`, all five manifests
and all five `environment.json` files.

`python3 tools/validate_ledger.py` exits 1 with `FAIL: 154 new validation
error(s)`. **Not one of the 154 lines references any `experiments/EXP-XEDN-002/`
path**, and no line mentions "XEDN" at all. I confirmed the 154 are pre-existing
by extracting the merge-base `123fb746` with `git archive` into `/tmp` and
running the identical command there: the sorted error sets are **byte-identical**
(`diff` empty). Note that `validate_ledger.py` does not inspect run manifests
under `experiments/`, so the manifest-schema conclusion above rests on my own
schema checker, not on that tool.

Schema deviation from the `docs/` template, matching the sibling EXP-FB3-001
package: manifests use `result.validity` / `result.validity_reason` instead of
`result.valid` / `result.invalid_reason`, and place `peak_memory_mb` inside
`timing` instead of a separate `resources` block. The frozen specification's
`required_artifacts` list does not mandate the template's field names, so this is
a house-style difference, not a contract breach. The specification also lists
"implementation files under `experiments/EXP-XEDN-002/implementation/`" rather
than the template's `implementation.md`; the seven implementation files are all
present, so the frozen list is satisfied.

### 2.2 Immutability handling of the invalid run — pass, with a disclosure nuance

`RUN-XEDN-002-A`'s manifest still reads `status: completed` and
`result.validity: valid`, and contains no occurrence of the string "invalid". It
was therefore **not corrected in place** — which is what AGENTS.md rule 4
requires, since the defect (an unverified `inference.resolved_model` string) was
discovered after the record was frozen.

The invalidity is recorded in three other places: `execution-report.yaml`
`runs.invalid` (`classification: invalid_record_metadata`, with a reason and an
explicit note that "the manifest ... still reads status: completed / validity:
valid because it was frozen before the defect was found and must not be
edited"); `RUN-XEDN-002-A2`'s `result.validity_reason`, which names A and states
why it supersedes it; `DEV-3` in the deviation list; and the snapshot receipt's
own notes. `analysis.md` line 15 lists A as "superseded, metadata defect".

No analysis number depends on A. Every mention of `RUN-XEDN-002-A` in
`analysis.md` and `derivation.md` is a supersession note; the arm-A tables cite
`RUN-XEDN-002-A2`. I confirmed the two records' `raw-result.json` payloads are
identical outside `_meta` — the eight differing leaves are `run_id`, `command`,
`started_at`, `finished_at`, `wall_clock_seconds`, `peak_memory_mb`,
`inference.resolved_model` and `inference.reasoning_effort`, plus one key present
only in A2 (`inference.resolved_model_source`).

The two sub-requirements in my task card ("left unedited" and "its manifest
states its invalidity") are mutually exclusive here. The executor chose
immutability, which is the correct precedence under AGENTS.md rule 4. The
residual risk is discoverability: a reader who opens only
`runs/RUN-XEDN-002-A/manifest.yaml` sees `valid`. I record that as an
observation for the Coordinator, not as a defect in this package.

### 2.3 Snapshot receipt integrity — pass

All 40 recorded `path_sha256` values reproduce, twice over:

- against the **working tree**: 40/40 match, 0 mismatches, 0 missing;
- against the **committed blobs** at `9f9186c`: 40/40 match.

Commit `9f9186c65257aa30458c56d435bc6289e6aaeed7` is reachable from `HEAD`, has
exactly the recorded parent `68e375f720123d4f46b1b5bc686920d77bf5ecf4`, changes
exactly 41 paths, and the changed-path set equals the receipt's `declared_paths`
set exactly (`changed_not_declared` and `declared_not_changed` both empty). The
commit message names the task (`TASK-20260724-231`) and all seven record and run
IDs. The 41st declared path is the receipt itself, whose hash is legitimately
absent (`receipt_self_hash_excluded: true`).

The receipt's `commit_sha` field is `null`, which is structurally unavoidable
when the receipt is committed inside the commit it describes. The binding SHA is
carried by `dispatch_queue.json` at `tasks[5].archive.commit_sha =
9f9186c65257aa30458c56d435bc6289e6aaeed7`, committed by `ae5503d`, and I
confirmed it independently from Git as above.

`python3 tools/research_dispatch.py .../dispatch_queue.json --output /tmp/plan.json
--report /tmp/plan.md` exits 0. All ten dispatch gates pass, including
`completed_archive_commits_verified` and `claim_relevant_tasks_have_independent_review`.
TASK-20260724-234 appears as a ready validator task with exactly the write scope
I used. Plan SHA-256 `495d583421309c179c2cefa44503c02c23d4303d3be76ae150ee4dad37f17ca3`.

Receipt note 3 ("`experiments/EXP-XEDN-001` was verified unchanged by this task")
also checks out: `xedni_sections.py`, `smoke_results.json` and `contract.md` are
byte-identical to their blobs at the snapshot's parent.

### 2.4 Arm B honesty about what was exhausted — pass

The coverage claim is precisely right. Recomputing from
`RUN-XEDN-002-B/raw-result.json`:

| `p` | `x` tested | of `p^2` | slots enumerated | fraction of full space | frozen hits | `n_x * Q(p)` (mine) |
|---|---|---|---|---|---|---|
| 5 | 25 | 25 | 1,562,500 | 100.0000% | 3,800 | 3,800 |
| 7 | 49 | 49 | 34,588,806 | 100.0000% | 36,162 | 36,162 |
| 11 | 12 | 121 | 212,587,320 | **9.9174%** | 65,400 | 12 × 5,450 |
| 13 | 6 | 169 | 347,530,248 | **3.5503%** | 66,960 | 6 × 11,160 |

`12/121 = 9.91736%` and `6/169 = 3.55030%`, and slot fractions agree to 12
decimal places, so the "9.92%" and "3.55%" figures are correct. `Q(11) = 5450`
and `Q(13) = 11160` come from my own formula. The `x` lists **are** recorded:
`actual_coverage.<p>.x_list_enumerated` holds all 12 and all 6 as strings (the
key `analysis.md` cites), and `planned_coverage.<p>.x_list` holds the same lists
as integer triples (the key `execution-report.yaml` cites). Both lists include
`x = t^2`, `x = t^2 + t` and the planted `x* = t^2 + 5t + 3`, as claimed;
`planned_coverage` carries no list at `p = 5, 7` because there the plan was all
`p^2` values. Seeds `[20260718, 20260724]` are in the manifest.

Every substantive statement describes the `p = 11, 13` work as partial:
`analysis.md` §3 says "Full-space verification with the frozen predicate reached
`p = 5` and `p = 7` **only**", labels the rows "complete `b`-marginals for 12/6
listed `x`", prints both percentages, and states the remaining `x` "were **not**
tested with the frozen predicate at those sizes".
`execution-report.yaml` has a dedicated `what_was_NOT_exhausted` field, a
boundary sentence ("Any statement that the frozen predicate was exhaustively
validated applies to `p = 5` and `p = 7`"), `DEV-1` with the percentages, and
`full_space_verified_with_frozen_predicate: false` inside the raw record at
`p = 11, 13`. `derivation.md` §1.5 distinguishes "full slot space at `p = 5, 7`"
from "every enumerated complete `b`-marginal at `p = 11, 13`". I found **no**
place where a partial enumeration is called exhaustive. The one loose phrase is
the run-list parenthetical at `derivation.md` line 12, "`runs/RUN-XEDN-002-B`
(exhaustive frozen-predicate enumeration)", which omits the qualifier that every
substantive statement supplies four lines later; wording only.

The uses of "exhaustive verification at `p <= 13`" in `analysis.md` §Scale
boundary and §8.7 refer to **arm C**, whose independent fibering did cover the
full space at `p = 13`. I verified that independently (§2.7), so those sentences
are accurate.

### 2.5 Controls

**(a) Frozen predicate vs an independent square test — pass.** Three
algorithmically distinct implementations, all written by me:
(i) the frozen gcd-based oracle; (ii) top-down square-root extraction plus an
elementary root-multiplicity squarefree test (no gcd, no factorisation);
(iii) `sympy` `factor_list` over `GF(p)`, accepting iff every factor multiplicity
is exactly 2 and `lc` is a QR.

| population at `p = 101` | tested | frozen accepts | independent accepts | disagreements |
|---|---|---|---|---|
| random sextics, seed 20260718 | 100,000 | 0 | 0 | **0** |
| random sextics, seed 20260724 | 100,000 | 0 | 0 | **0** |
| random sextics, `sympy` cross-check | 5,000 | 0 | 0 | **0** |
| planted `y^2`, `y` squarefree | 3,948 | 3,948 | 3,948 | **0** |
| planted `y^2`, `y` **not** squarefree | 4,052 | 0 | 0 | **0** |
| non-residue-scaled squares `n·y^2` | 4,000 | 0 | 0 | **0** |
| perturbed non-squares | 4,000 | 0 | 0 | **0** |

Random sextics are almost never squares, so agreeing on them is nearly
vacuous — the contract control as written has little power. I therefore added the
adversarial planted rows, which are the informative direction, and all three
implementations agree three ways with **zero** disagreements. Together with the
exhaustive `p^7` comparison of §1.1 this pins the predicate's semantics
completely: nonzero perfect square with squarefree root; no false positives;
`f = 0` rejected.

**(b) Smoke consistency — pass.** `P_lift(101) = 504950/1061520150601 =
4.756857e-07` from my own closed form. Times the smoke's 5,760 slots gives
`lambda = 0.00273995`, i.e. the ~0.00274 the task card names, and
`P(observe 0) = exp(-lambda) = 0.997264`. The recorded observation of 0 in
`experiments/EXP-XEDN-001/smoke_results.json`
(`random_slots_tested: 5760`, `random_sections_found: 0`) is the *expected*
outcome. The executor's one-sided 95% upper limit on the rate given zero hits,
`5.201e-04`, comfortably contains `4.757e-07`. I also checked the part-4 negative
control independently: the exact frozen-predicate rate on degree-exactly-6
polynomials is `(p-1)/(2p^4) = 50/104060401 = 4.8049e-07`, predicting 0.0961
squares in 200,000 samples against 0 observed, `P(0) = 0.9084`. The executor's
own conclusion — the smoke could not have detected this rate and carries almost
no information about the exponent — is correct and is the honest reading.

**(c) Degenerate `y = 0` count — pass.** `x^3 + b = 0` iff `b = -x^3`, one `b`
per `x`, and `deg(-x^3) = 6` with leading coefficient `-1 != 0`, so all `p^2` lie
inside the family. My own full-space enumeration counted exactly 25 at `p = 5`
and 49 at `p = 7`; the run record reports 25 / 49 / 121 / 169 and that all are
rejected by the frozen predicate. Counting them would give
`p^2 (Q(p) + 1)`, a relative `O(p^{-4})` change and no exponent change.

**(d) Planted-section control and its deviation — pass, deviation is real and
disclosed.** The deviation is genuine, and it originates in the **frozen input**,
not in this experiment. With `x* = t^2+5t+3` and `y* = t^3+2t^2+4t+7`, the `t^6`
coefficients of `y*^2` and `x*^3` are both 1 and cancel, so
`b = y*^2 - x*^3` has degree 5. The run record states
`b_planted_degree: 5`, `b_degree_is_6: false`, and a `deviation_note` saying the
surface "lies OUTSIDE the frozen deg-b-exactly-6 census family"; `DEV-4` records
it; `analysis.md` control 2 marks it "pass, with a recorded deviation". The frozen
`smoke_results.json` independently records `planted_surface_b_degree: 5`, so the
executor's cross-reference is accurate. The recovery itself checks out: exactly
one hit among all 10,201 monic quadratics at `p = 101`, at `(x_0, x_1) = (3,5)`,
found by both the frozen predicate and the independent reference, matching the
smoke's "1 section, recovered". Treating it as a test of the enumerator rather
than as a census member is the right call.

### 2.6 The iso-triviality finding — correct, and properly disclosed

This is the most consequential item in the package, and I checked it four ways.

1. **Is `j = 0`?** Yes. For `y^2 = x^3 + a(t)x + b(t)` in characteristic `> 3`,
   `j = 1728 · 4a^3 / (4a^3 + 27b^2)`. With `a = 0` identically the numerator
   vanishes, and the denominator `27 b^2` is nonzero because `deg b = 6` forces
   `b != 0`. The discriminant `-16(4a^3 + 27b^2) = -432 b^2` is likewise nonzero,
   so the generic fibre is smooth and `j = 0` is the honest constant value, not an
   artefact of a degenerate model. Under the standard definition of isotriviality
   (constant `j`, equivalently mutually isomorphic smooth fibres over the
   algebraic closure) **every** member of the frozen family is isotrivial.
2. **Is it a family of sextic twists?** Yes. Over the algebraic closure,
   `x = b^{1/3} X`, `y = b^{1/2} Y` turns `y^2 = x^3 + b` into `Y^2 = X^3 + 1`,
   so the family is the sextic-twist family of the single `j = 0` curve.
3. **Is the count of `F_p(t)`-constant members `(p-1)p`?** Yes, and the "exactly"
   is justified. A Weierstrass isomorphism between two short forms with `a = A = 0`
   in characteristic `> 3` must be `x = u^2 X`, `y = u^3 Y` for `u in F_p(t)^*`,
   which sends `b` to `b/u^6`. So `y^2 = x^3 + b` is `F_p(t)`-isomorphic to a
   constant `Y^2 = X^3 + c` iff `b = c u^6`; writing `u = f/g` in lowest terms and
   using `deg b = 6` forces `g` constant and `deg u = 1`, i.e.
   `b = c'(t + a_0)^6`. That gives `p` choices of `a_0` times `p-1` choices of
   `c'`. I enumerated these directly and got 20 / 42 / 110 / 156 distinct `b` at
   `p = 5, 7, 11, 13`, all of degree exactly 6 — matching the record.
4. **Is the `mu_3` automorphism claim right?** Yes. `x -> zeta x` with
   `zeta^3 = 1` fixes `x^3`, hence maps sections to sections; a primitive cube
   root of unity exists in `F_p` iff `p = 1 mod 3`. I confirmed
   `{2,4}` are the nontrivial cube roots at `p = 7`, none at `p = 5`, which is
   exactly the `p = 7, 13` versus `p = 5, 11` split the executor reports. In the
   free-`x` convention this triples a surface's sections, which is a sufficient
   mechanism for the observed `p mod 3` oscillation in `P[>= s]` and in the
   maximum (3, 6, 3, 9). I also independently reproduced the exact mean sections
   per surface in the free-`x` convention, `(p-1)(p^3+1)/(2p^4)` =
   0.4032, 0.4298, 0.4548, 0.4617, which is smooth and monotone while `P[>= 1]`
   is not — consistent with clumping.

I also verified that the two quotations the finding rests on are real, not
paraphrased: `experiments/EXP-XEDN-001/contract.md` line 20 reads "iso-trivial
surfaces must be detected and excluded from census counts", and
`research_directions_20260718.md` line 414 excludes "constant/iso-trivial
surfaces ... j=0/1728 (extra sections may confound controls)".

**So the finding is correct**: the frozen specification's iso-triviality control
conflates isotriviality with constant coefficients when it says the count "must be
reported as exactly zero for this family ... b constant is excluded by
deg b = 6". Under the standard definition the count is the entire family, and the
inherited EXP-XEDN-001 constraint is not satisfiable as frozen, because applying
it would empty the family.

**It is disclosed in committed artifacts, not only in a chat message**, in seven
places: `runs/RUN-XEDN-002-CTRL/raw-result.json` `control_4_isotriviality`
(with `j_invariant_of_the_family: 0`, `fraction: 1.0`, and an explanation that it
"CONTRADICTS the reading assumed by the EXP-XEDN-002 specification's control
text"); `execution-report.yaml` `controls.control_4_isotriviality`
(verdict `discharged_with_finding`, `exclusions_applied: none`);
`protocol_deviations` `DEV-5`; `anomalies`; `executor_assessment.
open_items_for_the_coordinator`; `analysis.md` control table row 4 and claim
boundary 1(a); and `derivation.md` Part 3 items 1–4 with the candidate-B2
cross-reference. Both readings are reported with their counts, nothing was
excluded from any count, and the executor explicitly leaves the resolution to the
Coordinator. That is the correct handling under AGENTS.md rules 1 and 8.

The finding does **not** change the arm-A or arm-C numbers. It bears on model
error — whether the census measured the intended object — which is the
Coordinator's and Red Team's call, not mine.

### 2.7 Arm C integrity — pass

**Methodology.** The fibering enumerates `(x, y)` pairs and bins by the induced
`b = y^2 - x^3`. It cannot double count or miss surfaces, and I verified each
step rather than accepting the argument:

- For fixed `x`, `y^2` determines `b` and conversely, and `y^2 = y'^2` iff
  `y' = ±y`, so the map is exactly 2-to-1 off `y = 0`. Every per-surface point
  count in the record is even, and I re-derived `points = 2 × slots` at all four
  sizes.
- `sum_s hist[s] = (p-1)p^6` (the surface count) and `sum_s s·hist[s] = N_hit(p)`
  from my own closed form, at all four sizes. A double count would break the
  second identity; a miss would break both.
- In my own reimplementation, **zero** counts landed on any `b` outside the
  family (`[t^6] b = 0`), so the `deg b = 6` filter is exact.

**Independent reproduction.** I wrote my own fibering and reproduced the
histograms **bin for bin**:

| `p` | my histogram (surfaces by hit-slot count) | identical to record |
|---|---|---|
| 5 | `[58860, 3500, 120, 20]` | yes |
| 7 | `[675108, 26901, 2751, 938, 105, 21, 70]` | yes |
| 11 | `[17077720, 617760, 18700, 1430]` | yes |
| 13 | `[56232878, 1549912, 95550, 33202, 6929, 2496, 156, 468, 39, 78]` | yes |

At `p = 5, 7` the fibering **method** is validated independently, because my
full slot-space brute force (§1.5) produced the same histograms without any
fibering. At `p = 11, 13` I could not brute-force the full space in budget, so
what I validated there is an independent *implementation* of the same method,
cross-checked against my proved closed form.

**`P[>= 1]` at `p = 5`.** My brute force gives 3,640 of 62,500 surfaces =
`5.824000e-02`, exactly the published value.

**`P[>= 9]`.** Exactly `0` at `p = 5, 7, 11` and `78 / 57,921,708 =
1.346645e-06` at `p = 13`, confirmed in my own histogram. `1/13 = 0.076923` is
larger by a factor of `5.71e4`. I additionally took the five section-rich
`p = 13` surfaces recorded in `top_surfaces` and, using the frozen predicate
directly on all 169 monic quadratics for each (no fibering at all), confirmed
each has exactly 9 hit slots and 18 points, with `deg b = 6`.

**Distinct versus independent.** Stated in `analysis.md` §4 ("neither is a count
of independent sections", "both columns are therefore **upper bounds** on the
number of independent sections"), in claim boundary 3, in the run record's
`counting_conventions` and `distinct_vs_independent` fields, and in
`derivation.md` H5 and uncovered case 7. `r <= 8` is flagged as a literature
input, not re-derived. The `s = 9` non-rate is stated correctly: because the
event is empty at three of four sizes, no decay exponent is defined, and the
executor says so instead of fitting one.

### 2.8 Arm D discipline — pass

- **Explicit hypotheses.** H1–H6 are stated in `derivation.md` §2.1: odd `p > 3`;
  the polynomial Weierstrass model with `deg a <= A`, `deg b <= B`; the section
  shape with `delta` free `x` coefficients and `deg y <= e`, sections integral;
  the slot-versus-surface distinction; distinct-not-independent; and uniform
  sampling within the stated coefficient box.
- **Rigorous versus counted.** Lemma D1 is genuinely rigorous and I checked its
  proof: if a slot is a hit with witness `y` of degree `k` then
  `2k = deg y^2 <= max(B, 3d, A+d) = M_0`, so `deg y <= E = min(e, floor(M_0/2))`;
  each `(a, x)` therefore has at most `p^{E+1}` hit `b`, and dividing by
  `p^{dim_a + B + 1 + delta}` gives `P_slot <= p^{E-B}`. At the frozen shape this
  is `p^{-3}`, which Part 1 attains. Corollary D1a's integrality step is also
  correct. Lemma D2 carries the sentence "**This is a parameter count, not a
  geometric theorem.**" in bold, and the marker legend defines `(P)` as
  "parameter count / heuristic".
- **Unproved steps named.** `derivation.md` §2.3 lists the marked steps
  ((i) independence of the `K` leading-coefficient conditions, (ii) point counts
  equal `p^{dim}`), notes that (iii) the `1/2` from the double cover is exact by
  Part 1, and uncovered case 11 says the two remaining heuristics "remain unproved
  in general; they are verified exactly only in the three configurations of the
  table in §2.3". `analysis.md` §5 and boundary 2 repeat this.
- **Not an unconditional no-go.** Stated three times: `derivation.md` §2.5 ("this
  parameter count does **not** exclude the prescribed construction"),
  `analysis.md` §5 ("Arm D is **not** an unconditional no-go for lifting") and
  boundary 2, and `execution-report.yaml` `not_a_no_go`. The `m = 9` boundary case
  on the full rational elliptic family is explicitly reported as `dim <= 1`, i.e.
  **not** negative.
- **Uncovered cases.** Eleven numbered items in §2.6, covering `p = 2, 3`,
  non-integral sections, other models and fibrations, extension fields and base
  changes, shapes outside the grid, structured subfamilies (with the observation
  that the xedni construction *is* such a subfamily, so the lemma does not close
  it), independence versus distinctness, search and descent cost, the number-field
  setting, crypto scale, and the two unproved heuristics.

I re-derived the arm-D arithmetic myself and it all holds: all 1,080 grid rows
match my own `c_slot = max(B, 3d, 2e, A+d) - e` and
`E - B` formulas; `c_slot = 0` occurs only for the all-constant configuration;
`min c_slot` with `e >= 1` is 1; `c_surf = 0` with monic `x` forces `d = e = 0`;
the free-`x` `c_surf = 0` table `(d, e) -> (max B, max A)` reproduces
`(0,0)->(1,1)`, `(0,1)->(2,2)`, `(1,1)->(3,2)`, `(1,2)->(4,3)`,
`(2,3)->(6,4)`, whose last row is indeed the rational-elliptic-surface integral
section shape; and the prescribed-target count
`dim <= dim_a + B - 1 - m - sum_i c_surf,i` follows from the stated conditions
because `-c_surf,i = delta_i + e_i - M_i`, giving `dim <= -4` for the frozen
family and `dim <= 1` for the full family at `m = 9`, with thresholds
`m >= 6` and `m >= 11`. The KN-LIT-021 attribution is accurate: that knowledge
entry states the classical failure "is driven by an absolute bound on the size of
the coefficients", which is what §2.5 cites it for.

### 2.9 Self-consistency and reproducibility — pass, with one finding

I wrote my own cross-checker (no import of the experiment's library) and ran
**506 assertions** across three batches (294 + 174 + 38), covering far more than
the 10 cells requested: all 8 `P_lift` rows (`N_slots`, `N_hit`, exact rational,
float, `2p^3 P`), all 7 `alpha_eff` values, the OLS exponent, all 9 arm-C rows at
all 4 sizes, the arm-B coverage table, the free-`x` and mathematical-square
variants, the `y = 0` variant, the false-negative counts, the induced exponents,
the smoke-consistency numbers, and the full manifest schema. Two initial
"failures" were defects in my own string matching, not in the artifacts, and both
re-verified as pass once corrected. Net: **0 substantive failures**.

The executor's own `verify_artifacts.py --reproduce` reports `259 checks, 0
failures`, which I confirmed by running it; it is read-only. My verdict rests on
my own checks, not on that script.

**Re-running recorded commands.** To avoid touching the immutable package I
cloned the repository into `/tmp` with `--no-hardlinks`, checked out the snapshot
commit `9f9186c`, moved three run directories aside inside the clone only, and
executed the recorded reproduction entry points:

| run | recorded command | recorded wall | my wall | payload outside `_meta` |
|---|---|---|---|---|
| RUN-XEDN-002-A2 | `bash .../run_arm.sh A2` | 2.332 s | 2.294 s | **identical** |
| RUN-XEDN-002-C | `bash .../run_arm.sh C` | 13.771 s | 12.873 s | **identical** |
| RUN-XEDN-002-CTRL | `bash .../run_arm.sh CTRL` | 19.434 s | 19.323 s | **identical** |

Peak memory also reproduced (243.2 → 243.3 MB, 447.8 → 448.0 MB, 66.3 → 65.7 MB).
Only `_meta` timing fields and `git_commit` differ, the latter because the clone's
`HEAD` is the snapshot commit rather than the pre-commit revision `e18c9bc`
the runs recorded. `/workspace` remained clean throughout, verified after every
step. I did not re-run `RUN-XEDN-002-B` (954 s); instead I recomputed `Q(p)` for
every one of its 92 work units from my own formula and enumerated the full slot
space myself at `p = 5, 7`, which is a stronger check than re-execution.

**Finding (F1).** One published number is wrong. `analysis.md` line 168 and
`execution-report.yaml` line 466 both state the clumping ratio `mean / P[>= 1]`
is "1.117 at `p = 7`, 13". Recomputed from the executor's own raw record:

| `p` | mean | `P[>= 1]` | ratio |
|---|---|---|---|
| 5 | 0.060800 | 0.05824000 | 1.0440 |
| 7 | 0.051229 | 0.04361278 | **1.1746** |
| 11 | 0.037224 | 0.03600723 | 1.0338 |
| 13 | 0.032562 | 0.02915712 | 1.1168 |

The `p = 13` value is right; the `p = 7` value should be **1.175**, and 1.117
looks like the `p = 13` figure duplicated. No such field exists in any
`raw-result.json`, so the error is confined to narrative prose and does not
propagate into any metric, table or gate statement. It is a secondary derived
diagnostic, and correcting it slightly *strengthens* the qualitative claim it
supports (larger clumping at `p = 1 mod 3`). Minor.

### 2.10 Budget and honesty compliance — pass

`992.142 s` of recorded run wall clock against 5,400 s; largest single run
`954.263 s` against the 1,800 s per-run cap; `0.90` CPU-hours against 2; peak
`0.44 GB` against 4 GB; `5` runs against 6. I confirmed the per-run wall clocks
sum to the reported total, and that the unrecorded pre-run probe time is
**disclosed rather than estimated** ("not individually timed, so no number is
reported for them"), which is the correct handling — a Validator must not accept
an invented measurement, and none was offered. `certificate.kind: none` in all
five runs, with a note explaining that a counting experiment has nothing to
certify.

The three required honesty statements are all present and plain:

- **Model error.** `analysis.md` §8.1: "An exact count removes sampling error
  only. It does not remove model error. If the frozen family or the frozen
  predicate is the wrong formalisation of the xedni idea, this experiment has
  answered a possibly wrong question exactly." It then lists four concrete
  instances (the `j = 0` family, monic `x` as a restriction, the per-slot metric's
  insensitivity, and `a = 0` removing the parameters the prescribed count needs).
- **`ECFG-P1543` / `ECFG-P1547`.** `analysis.md` §8.5 and
  `execution-report.yaml` boundaries both state these remain exactly as recorded
  and that nothing here adds to, replaces or reinterprets them. Both IDs exist in
  `ledger/FINDING-PF-IC-001.md`.
- **Phase-2 infeasibility as methodology only.** `analysis.md` §9 is titled
  "Methodology observation (not evidence)", cites AGENTS.md rule 5, and says the
  gate's mathematical content rests on the exact values, not on the earlier
  design's failure.

The executor also stays inside its role: `analysis.md` opens with a role boundary
disclaiming any status change, and `execution-report.yaml`'s
`gate_verdict.authority` begins "OBSERVATION ONLY". Claim tier `toy` is stated,
with `p = 809` (10 bits) as the largest closed-form size.

---

## 3. Findings the executor did not report

- **F1 — clumping ratio at `p = 7` misstated as 1.117; correct value 1.175.**
  Narrative only, in two artifacts, no propagation. Minor. (§2.9)
- **F2 — "identical raw-result.json" is imprecise.**
  `execution-report.yaml` says `RUN-XEDN-002-A`'s `raw-result.json` "is identical
  to `RUN-XEDN-002-A2`'s". The scientific payload is identical; eight `_meta`
  leaves differ and one key is present only in A2. True in substance, loose as
  written. Minor. (§2.2)
- **F3 — "same deterministic script, unchanged" is not literally true.**
  `arm_a_closed_form.py`'s `validity_reason` string was extended when A2 was
  created (A's manifest carries the short reason, A2's the long one that names A).
  The measured payload is unaffected, but both runs record the same
  `code.commit` with `dirty_tree: true`, so **no committed revision reproduces
  `RUN-XEDN-002-A`'s manifest text**. This is an inherent limitation of running
  with untracked files, correctly flagged as `dirty_tree` in both manifests; I
  note it so the Coordinator knows A is reproducible only up to that string.
  Minor.
- **F4 — one unqualified use of "exhaustive" for arm B.** `derivation.md` line 12
  labels `RUN-XEDN-002-B` "(exhaustive frozen-predicate enumeration)" without the
  `p <= 7` qualifier that every substantive statement carries. Wording only.
- **F5 — the contract's predicate control has little power as written.**
  Requiring agreement on `10^5` *random* sextics at `p = 101` is nearly vacuous,
  because the expected number of hits is 0.096: both implementations answer "no"
  essentially always. The executor satisfied the control and went beyond it
  (exhaustive `f`-space at `p = 5, 7`), and I added an adversarial planted
  population. This is a weakness of the frozen control text, not of the
  execution. Minor, addressed.
- **F6 — snapshot receipt carries `commit_sha: null`.** Coordinator-side, not
  executor-side, and resolvable: the SHA is bound in `dispatch_queue.json` and I
  confirmed it from Git. Identical to the pattern the sibling validation of
  EXP-FB3-001 recorded. Minor. (§2.3)
- **F7 — the independence of this validation session is partial.**
  `cursor-cloud run-info` reports this run as
  `bc-019f9556-c64d-7309-8a8d-c9483ea64e70` with
  `originalModelName: claude-opus-5-thinking-max` — the **same cloud-agent run
  and the same resolved model that produced the artifacts** (the executor's
  manifest cites the same `bc` id). The handoff sets
  `independent_session_required: true`. I am a separate Validator subagent with an
  independent context, I derived the closed form before reading
  `derivation.md`, and I did not originate any claim here; but this is not an
  independent session in the strict sense AGENTS.md's model policy intends, and
  the `review-xhigh` policy alias cannot be resolved in a Claude-family harness at
  all. I record this rather than let a `passed` verdict imply an independence it
  does not have. **The Coordinator should weigh this when deciding whether the
  `review-xhigh` independent-review requirement is discharged.**

## 4. Limits of this validation

1. My full slot-space brute force with the frozen predicate reached `p = 5`
   (1,562,500 slots) and `p = 7` (34,588,806 slots) only. At `p = 11` and
   `p = 13` I reproduced arm C's histograms with my own independent
   implementation of the same fibering method and cross-checked them against my
   proved closed form, and I spot-checked five `p = 13` surfaces directly with the
   frozen predicate; I did **not** enumerate those full slot spaces
   (2,143,588,810 and 9,788,768,652 slots, ~11,000 and ~51,000 CPU s) with the
   frozen predicate. The executor's `DEV-1` residual risk is therefore reduced but
   not eliminated.
2. I did not re-execute `RUN-XEDN-002-B` (954 s). Its content was checked by
   recomputing every one of its 92 per-`x` marginals from my own `Q(p)` and by my
   own full-space enumeration at `p = 5, 7`.
3. I verified Lemma D1's proof and every arithmetic step of the D2 grid and the
   prescribed-target count. I did **not** prove Lemma D2's two marked heuristics
   (independence of the leading-coefficient conditions, and `p^{dim}` point
   counts); I confirm only that they are marked as unproved and are verified in
   exactly three configurations, as claimed.
4. `r <= 8` (Shioda–Tate) and the KN-LIT-020 / KN-LIT-021 content are literature
   inputs. I confirmed both knowledge entries exist and that KN-LIT-021 supports
   the specific statement cited; I did not verify the underlying papers.
5. I validated that the iso-triviality finding is mathematically correct and
   properly disclosed. Whether it means the census tested the intended object,
   and what should follow for `H-XEDN-001`, is interpretation — the Coordinator's
   and Red Team's remit, not mine.
6. `tools/validate_ledger.py` does not inspect run manifests under
   `experiments/`; the manifest-schema conclusion rests on my own checker.
7. No evidence, decision or hypothesis-status record for EXP-XEDN-002 exists yet,
   so I could not check evidence-record scope language or claim-tier assignment.
   That is expected at this point in the lifecycle.
8. A `passed` verdict here means the receipt is **admissible evidence**. It does
   not support an ECDLP claim, does not demonstrate a speedup, and does not
   authorise any promotion or status transition.

## 5. Reproducing my checks

All validator scripts were written from scratch under `/tmp/val234/` and import
nothing from `experiments/EXP-XEDN-002/implementation/`. They load only the
frozen `is_square_poly` by file path, read-only.

| script | what it establishes | wall | peak RSS |
|---|---|---|---|
| `validator_derive.py` | exhaustive predicate semantics at `p = 5, 7` over all `p^7` polynomials; full slot-space brute force; my closed forms | 4.5 s | 191 MB |
| `check_snapshot.py` | 40 receipt hashes against worktree and committed blobs; parent, reachability, exact changed-path set | 0.2 s | 40 MB |
| `check_tables.py` | 294 assertions cross-checking every published table against raw JSON using my own formulas | 0.1 s | 60 MB |
| `check_armc_and_iso.py` | my own arm-C brute force at `p = 5, 7`; free-`x` totals; clumping ratios; iso-triviality counts | 13.6 s | 188 MB |
| `check_predicate_control.py` | three-way predicate agreement on 205,000 random and 16,052 adversarial planted cases | 6.8 s | 48 MB |
| `check_armc_1113.py` | my own fibering histograms at `p = 11, 13`; direct frozen-predicate check of five `p = 13` section-rich surfaces | 3.1 s | 1,303 MB |
| `check_schema_and_text.py` | 174 schema and textual-honesty assertions | 0.1 s | 45 MB |
| `check_final.py` | 38 assertions on induced exponents, the arm-D grid, and my two corrected checks | 0.1 s | 45 MB |

Plus: `tools/validate_ledger.py` at `HEAD` and at a `git archive` extract of the
merge-base `123fb746`; `tools/research_dispatch.py`;
`implementation/verify_artifacts.py --reproduce`; and three re-executions of
recorded commands inside an isolated `/tmp` clone.

No git write command was issued. Nothing outside
`coordination/goals/GOAL-ICLIFT-001/batches/BATCH-001/tasks/TASK-20260724-234/`
was created or modified.
