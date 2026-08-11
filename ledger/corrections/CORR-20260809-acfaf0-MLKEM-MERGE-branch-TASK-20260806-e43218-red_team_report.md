# Independent Red Team report — Sections A, B, and C

TASK-20260806-e43218 / BATCH-a44d08 / GOAL-MLKEM-005  
Review target: the frozen producer snapshot in commit
`7700090428ae7f8b5dbaaf7bb54a7a253c53fae8`  
Claim tier: **TOY**

This is an **independent Red Team session**. I did not originate the
pre-registration or any producer artifact. I did not modify any producer,
Validator, queue, goal, ledger, receipt, or Git state, and I ran no BKZ, LLL,
or other reduction. My two adversarial probes were in-memory NumPy/closed-form
controls and wrote no data. This report is the only artifact I produced.

Nothing in this report is a claim about a standardized scheme, a standardized
parameter set, cryptographic-scale behavior, an attack cost, or a breakthrough.
The narrow observations reviewed here concern specified toy frame
presentations at `d in {100,140}` only.

---

## 0. Red Team disposition

**Disposition: SEVERE OBJECTIONS; do not admit either Section B's operating-
characteristic claim or Section C's confirmatory falsification. Preserve only
the narrow Section A presentation-level observation and the raw Section C toy
separation as instrument observations.**

The three producer packages are hash-bound, parseable, and mechanically
reducible. That infrastructure success is not the same as mathematical or
instrument validity:

1. **Section A — narrow observation survives, broad interpretation does not.**
   The raw count is reproducible: `E_I` rejects M-D at all 36 frozen points and
   does not reject the M-K upper-capacity curve at any point; the combined
   frozen verdict remains `NEITHER` in all four cells because the M-K `V`
   magnitude is rejected at 22 of 32 discriminating points. The `E_I` boundary
   is a relation between the explicit block-triangular presentation, its tail
   QR frame, and a distinguished coordinate block. It is not a property of the
   lattice alone. A lightweight isometry control below moves `E_I` from nearly
   `1` to about `0.30` on the same isometric lattice when the standard axes are
   held fixed, and restores it exactly only when the distinguished block is
   transported with the isometry. The existing Haar/permutation/block-swap
   controls are useful presentation controls, but they do not discharge AM-4.

2. **Section B — the headline diagnoses its positive control, not the AM-3
   gate.** The frozen control chose, in three cells, a steeply decreasing step
   and added too little even to make the step increase. In those cells the
   control could not possibly create the monotonicity violation it claimed to
   inject; the frozen run was in precisely that arrangement. Independently,
   the statement that exchangeability makes the Studentized mean exactly
   `t_7` is false. I built a continuous iid, symmetric, exchangeable flat-step
   null whose per-step false-failure probability is at least `1/256 =
   0.00390625`, already above the declared `0.002`. The multiplication
   `48 * 0.002 = 0.096` is arithmetically correct but its per-step premise is
   not established.

3. **Section C — one raw separation is strong under the instrument's nominal
   between-frame floor, but the confirmatory verdict is inadmissible.** Ten
   pairs, not the declared twelve, were realized. Zero of those ten actual
   float32 frame pairs meets the frozen `1e-9` match requirement; residuals are
   `8.84e-7` to `2.30e-6` at the per-pair maximum. The float64 closed-form
   inverse is not the frame that was projected. Of the two mechanical firing
   pairs, `(100,40,t=0.0075)` exceeds its own nominal relative detection floor
   by only `0.25` percentage points, while `(140,40,t=0.0050)` exceeds it by
   `13.15` percentage points and is the strongest raw observation. Even the
   latter is not confirmatory evidence under the frozen protocol: the actual
   match gate failed and the paired `n=8` uncertainty omits uncalibrated
   finite-`N` quantile error from the shared error corpus.

The narrowest defensible batch result is therefore:

> On the exact toy basis presentations and frozen grids, the stored arrays show
> a tail-frame energy boundary associated with the distinguished `k`-block;
> the full M-K and M-D magnitude models both fail the frozen Section A score.
> Section B establishes that its frozen positive control is defective and
> yields no real-arm verdict or justified `0.096` false-failure bound. Section
> C contains a substantial raw cross-family tail-quantile difference in one
> toy cell, but it does not establish a confirmatory equal-`V` result because
> the actual frame matches fail the frozen tolerance and the falsifier lacks a
> calibrated null including finite-sample quantile error.

---

## 1. Scope, governing artifacts, and exact-session provenance

### 1.1 Governing task and write boundary

I followed the exact handoff embedded in
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/dispatch_queue.json`:

- task: `TASK-20260806-e43218`;
- role: `red-team`;
- dependency snapshot: `TASK-20260806-f4d678`;
- only artifact:
  `coordination/goals/GOAL-MLKEM-005/batches/BATCH-a44d08/reviews/TASK-20260806-e43218/red_team_report.md`;
- requested inference policy: `review-adversarial`;
- independent session required: `true`;
- maximum runs: `1`;
- claim tier: TOY.

The relevant repository contracts read for this review were `AGENTS.md`,
`agents/red-team.md`, `docs/task-lifecycle.md`,
`docs/dynamic-subagent-dispatch.md`, and the canonical harness skill at
`plugins/crypto-autoresearcher-harness/skills/crypto-autoresearcher-harness/SKILL.md`.

### 1.2 Exact independent-session receipt

The native-session receipt is
`/tmp/codex-runtime-TASK-20260806-e43218.json`.

| field | verified value |
|---|---|
| role | `red-team` |
| task | `TASK-20260806-e43218` |
| independent session | `true` |
| independent session id | `019fe509-0376-7050-9705-c43752fd5af7` |
| requested policy | `review-adversarial` |
| provider | `openai` |
| resolved model | `gpt-5.6-sol` |
| reasoning effort | `xhigh` |
| fallback used | `false` |
| degraded requirements | none |
| verification status | `verified` |
| verification scope | `exact_codex_session_only` |
| receipt file SHA-256 | `03b765f3c8137e8714605ccb8379b81dc09ee0f4350779a08dab92d533bb9a96` |

The repository preflight passed generated-binding and role-authority checks.
Its direct API doctor reported no configured usable backend; that failure was
limited to credentials. The canonical harness explicitly permits a verified
authenticated native Codex session in that circumstance. The receipt above
verifies that exact native session and records provider `openai`, not a
prohibited provider. This is infrastructure provenance only.

### 1.3 Frozen ordering and snapshot integrity

I read both snapshot receipts and inspected both commits directly.

| archive | commit | parent | exact changed set |
|---|---|---|---|
| preregistration, `TASK-20260806-0a1072` | `9cb2d3e28ae7a474edbb116d694969470829e112` | `68168fc9e205f44fe5ba4e3cce06c9390759490e` | receipt, `prereg.md`, sidecar |
| producers, `TASK-20260806-f4d678` | `7700090428ae7f8b5dbaaf7bb54a7a253c53fae8` | `974ad579443984d9369ac050dadd800caa5d10f4` | receipt plus all 12 producer artifacts |

`git merge-base --is-ancestor 9cb2d3e... 7700090...` returned success. The
preregistration blob in the notarizing commit hashes to
`8d00ca3f0977e7367cfd10f4eb01cc0d4d24dfdc1ecf9739ba3cc299ee2a6c80`.
Every producer blob in `7700090...` matches the corresponding SHA-256 in the
queue/archive binding. The two on-disk receipts contain `commit_sha: null`
because they are committed in the commits they describe; the completed queue
archive blocks carry the externally verifiable commit IDs and parents.

I decoded all six batch JSON files with duplicate-key and non-finite-number
rejection, loaded all three producer YAML manifests and the Validator YAML in
full, and read all Markdown and Python producer artifacts. Parsing succeeded.
Independent raw reductions gave:

- Section A: 36 points; `E_I` M-K rejected 0, M-D rejected 36; discriminating
  `V` M-K rejected 22, M-D rejected 32; four `beta=d/2` `V` rows excluded;
- Section B: 48 steps, nine positive sample deltas, zero frozen violations;
  the `c=6` positive control fires in one of four cells;
- Section C: ten realized pairs; zero actual frame pairs within `1e-9`; two
  mechanical firing pairs under the declared critical value.

The Validator report at
`reviews/TASK-20260806-7418bc/validation_report.yaml` was read as an adversarial
input, not accepted as authority. I independently recomputed the points above
and independently built the controls in Sections 3 and 4 below. Where this
report agrees with the Validator, the agreement comes from the shared frozen
artifacts plus an independent derivation; where the Validator admits Section
A's boundary, I narrow that admission further by applying AM-4 explicitly.

---

## 2. Evidence classes

The remainder never mixes the following three kinds of evidence:

| class | what it can establish here | what it cannot establish |
|---|---|---|
| **Mathematical evidence** | capacity bounds; exact `V_TL` reachability; exact counterexamples to the Student-`t` assumption; invariance or non-invariance identities | an empirical tail law outside the proved identity |
| **Instrument evidence** | what the frozen arrays, nulls, and in-memory probes returned at their stated toy parameters and precision | a lattice-invariant statement or transport to another scale |
| **Infrastructure evidence** | hashes, commits, parseability, exact-session provenance, deterministic reproduction metadata | truth of any mathematical interpretation |

This distinction matters especially in Section C: the second-order variance
identity is mathematical evidence; the `2^-10` order-statistic differences are
instrument evidence; the snapshot and run manifests are infrastructure
evidence.

---

## 3. Section A — `k != d/2`

Producer: `TASK-20260806-3084bc`  
Frozen source: `prereg.md` Section 2  
Headline reviewed: **the `E_I` confinement/spill boundary tracks `k`, not
`d-k`; the combined frozen verdict is `NEITHER` in all four cells.**

### 3.1 Arrangement in which the check could not fail

**Named arrangement A-CF-1 — scoring an algebraic extremum on a construction
that puts the frame at that extremum.** For any rank-`beta` projector `P` and
any `k`-coordinate subspace,

```text
max(0, 1-(d-k)/beta) <= tr(P Pi_I)/beta <= min(1,k/beta).
```

The frozen M-K `E_I` curve is the upper bound everywhere; the frozen M-D curve
is the lower bound everywhere. If the explicit block-triangular QR construction
places its tail frame at the upper extreme, the `E_I` arm cannot reject M-K and
must reject M-D whenever the bounds differ. It then measures which extreme the
chosen presentation occupies, not a free two-sided magnitude law.

**Was the frozen run in A-CF-1? Yes, for the `E_I` headline.** All 36 points
lie within `0.0013` of the upper curve under an absolute floor `0.02`; all 36
reject the lower curve. The between-basis SE falls as low as `6.6e-11`, so the
huge quoted SE separations are numerical consequences of a nearly deterministic
presentation, not 36 independent discoveries. **No, for the full two-observable
mechanism.** The `V` arm is not forced to the M-K curve and rejects it at 22 of
32 discriminating points. That is why the frozen cell verdicts are correctly
`NEITHER`, not support for M-K.

**Named nearby control A-NC-0 — the upper-bound interior.** A Haar frame at the
same `(d,k,beta)` has `E_I` near `k/d`, strictly between the two extremes over
the low-`beta` region. The producer's N-A1 returns that interior value; hence
the code path itself does not force the extreme. This control distinguishes an
implementation identity from the presentation's geometry, but it does not make
the geometry lattice-invariant.

### 3.2 AM-4 invariance attack

AM-4 in `DEC-20260806-14ac13` says that a predicate offered as an
**ADJUDICATOR** of a lattice claim must survive at least ambient isometry, row
permutation, and unimodular basis change. Section A explicitly says it is not
such an adjudicator. That is a legitimate scope choice, but it has a sharp
consequence: AM-4 is not “passed”; it is the reason the conclusion must remain
about the named presentation and distinguished block.

I built a read-only, in-memory nearby-object control from the exact frozen
`(d,k,i)=(100,30,0)` basis, seed `910300`, with no reduction. The control
computed the same tail-QR `E_I` and `V` after transformations. Selected rows:

| `beta` | original `E_I` | Haar ambient isometry, fixed axes | coordinate permutation, fixed axes | coordinate permutation, transported `K_I` | original `V` | Haar-isometric `V` |
|---:|---:|---:|---:|---:|---:|---:|
| 15 | 0.999999941 | 0.305778326 | 0.358258698 | 0.999999941 | 5.862390 | 0.200144 |
| 30 | 0.999995207 | 0.302893837 | 0.366664944 | 0.999995207 | 20.999712 | 0.346726 |
| 35 | 0.857142639 | 0.304075736 | 0.346375079 | 0.857142639 | 18.617134 | 0.351746 |
| 85 | 0.352941173 | 0.298487714 | 0.305176912 | 0.352941173 | 1.135945 | 0.249297 |

The maximum fixed-axis `E_I` change under the coordinate-permutation isometry
was `0.641741`; under a general Haar ambient isometry it was `0.698351`. The
maximum `V` change under the Haar isometry was `20.652987`. When the
distinguished block was transported with the coordinate permutation, `E_I`
returned to the original value to `5.6e-17`.

This is decisive about scope:

- `E_I` is invariant/equivariant for the **pair** “frame plus transported
  distinguished block”; it is not a scalar of the lattice with standard axes
  forgotten.
- `V`, being a moment of the projector diagonal in the standard coordinates,
  is invariant under coordinate permutations but not under a general ambient
  isometry.
- Therefore the boundary can be real as a feature of the explicit q-ary basis
  construction and still be entirely a coordinate/presentation effect for any
  lattice-level question.

I also tested one deterministic random row permutation and one unimodular
change consisting of 80 elementary row shears on that same basis. In this one
probe, `E_I` moved by at most `4.4e-6`; `V` moved by as much as `0.607` under
the shears. These are useful nearby observations, not a proof of row- or
unimodular-invariance. The frozen producer did not pre-register or execute the
full AM-4 family, and one robust seed cannot establish a universal statement.

### 3.3 Are N-A1, N-A2, N-A3, and the mirrored pairs sufficient?

No, not for AM-4 or for any claim beyond the explicit presentation.

- **N-A1 Haar** is a good identical-code-path null. It shows the scorer can
  return an interior value. It changes the object and does not test invariance
  of the same lattice.
- **N-A2 coordinate permutation** scores a permuted basis against the
  **unpermuted** coordinate range. It intentionally breaks the distinguished
  block association and returns near `k/d`. This is affirmative evidence of
  presentation dependence, not evidence of lattice invariance. Scoring the
  transported block restores `E_I` exactly in my probe.
- **N-A3 block swap** uses a different block-triangular object, not `B -> BH`
  or `B -> UB` on a fixed lattice. Its frozen formula is dimensionally
  inadmissible with `A^T`; the producer chose the shape-consistent `A`. The
  implemented object makes the tail frame coordinate-aligned and forces
  `V=beta(1-beta/d)`, moving `V` by up to `2.3x`. It tests “which labelled
  block?” but is not a same-object invariance control.
- **Mirrored `k` pairs** compare different constructions. They separate block
  size/role effects, but they do not preserve one lattice under the AM-4
  transformations.

Thus the controls are sufficient for the narrow statement “the implemented
observable follows the implemented `I`-block label rather than a fixed index
range.” They are insufficient for “the boundary is a property of a q-ary
lattice,” “all presentations of this construction behave this way,” or any
statement about an off-diagonal fpylll `k` convention. The producer itself
found that fpylll's `k` counts q-scaled rows whereas the preregistration's `k`
counts identity rows; that nomenclature collision alone forbids silent
transport to another basis generator.

### 3.4 Cheapest falsifier, nearby control, and narrow conclusion

**Cheapest decisive falsifier A-F1.** On one frozen basis, pre-register three
`beta` values bracketing `k`, then score `E_I` under:

1. the original presentation;
2. a fixed ambient Haar isometry with standard axes held fixed;
3. the same isometry with `Pi_I` transported as `H^T Pi_I H`;
4. at least one random row permutation and a short ladder of elementary
   unimodular shears.

No reduction, error draw, or quantile is needed; the work is a handful of
`d x d` QR decompositions. My one-basis version completed as a lightweight
shell probe and already discriminated fixed-axis from transported-block
readings. A successor should freeze the transformations and repeat over all
eight existing seeds before claiming more.

**Named nearby control:** `A-NC-ISO`, the same isometric lattice scored once
against fixed standard axes and once against the transported block projector.

**Narrowest defensible Section A conclusion:** at the exact frozen toy cells,
for the explicit `B=[[I_k,A],[0,qI]]` row ordering and its distinguished
identity block, unreduced `E_I` follows the upper capacity curve and its first
sampled departure occurs above `beta=k`, not above `beta=d-k`. This is a
presentation-level boundary observation. The frozen full mechanisms are both
rejected (`NEITHER`) because their `V` magnitudes fail. No claim is licensed
for a lattice invariant, another basis ordering, another generator convention,
or another scale.

**Evidence classification:** the capacity interval is mathematical evidence;
the 36-point counts and my transformation table are instrument evidence; the
commit/hash chain and fpylll nomenclature record are infrastructure evidence.

---

## 4. Section B — AM-3 replacement gate

Producer: `TASK-20260806-e17677`  
Frozen source: `prereg.md` Section 3  
Headline reviewed: **the AM-3 gate is `INADMISSIBLE` because three of four
positive-control cells do not return AM3-FAIL at `c=6`.**

### 4.1 Arrangement in which the check could not fail

**Named arrangement B-CF-1 — an injection that never creates the event it is
supposed to test.** The frozen control adds `c*SE_diff` to the upper endpoint,
so its new step is

```text
Delta_i(c) = Delta_i(0) + c*SE_diff(A,t_i).
```

If the selected step satisfies `Delta_i(0) <= -6*SE_diff`, then every frozen
`c <= 6` leaves `Delta_i(c) <= 0`. The control cannot create a monotonicity
violation, so it cannot return AM3-FAIL for the reason claimed. Under the frozen
admissibility clause, the headline `INADMISSIBLE` is then guaranteed by the
control construction.

**Was the frozen run in B-CF-1? Yes, in three of four cells.** The selected
steps and maximum injections were:

| cell | frozen selected step | original `Delta` | `6*SE_diff` | injected `Delta` at `c=6` | result |
|---|---:|---:|---:|---:|---|
| `d100_b30` | 0 | `-0.037829` | `0.012147` | `-0.025682` | TIE |
| `d100_b40` | 7 | `-0.000849` | `0.008888` | `+0.008039` | FAIL |
| `d140_b30` | 0 | `-0.045354` | `0.010590` | `-0.034764` | TIE |
| `d140_b40` | 1 | `-0.017249` | `0.009328` | `-0.007921` | TIE |

The preregistration calls the step rule “data-independent.” The algorithm was
pre-specified, but the realized index is data-dependent: the same observed
`SE_diff` selects the step and scales the injection, while the selected step's
observed `Delta` determines whether a violation was created. That coupling is
the failure. The run validly executed the frozen text; its headline is evidence
that the positive control is inadmissible, not that the AM-3 gate lacks power.

**Named nearby control B-NC-FLAT:** a synthetic or held-out flat step with the
same eight-draw dispersion, into which a known post-injection increase is
forced. The existing scorer implementation check is too weak because it uses
an unspecified “large” increase rather than the gate-commensurable frozen
operating point.

### 4.2 Exchangeability is not a Student-`t` assumption

The preregistration defines a flawless step by `true Delta <= 0` and
exchangeable paired differences, then states that the Studentized mean is
**exactly** `t_7`. That implication is false. Exact Student calibration requires
much stronger assumptions, classically independent Gaussian paired
differences. Exchangeability alone gives neither Gaussianity nor the required
independence structure.

I built a continuous null stronger than the degenerate Rademacher example:

```text
X_j = S_j + U_j,
S_j in {-1,+1} iid equiprobable,
U_j iid Uniform[-0.01,0.01], independent of S_j.
```

The `X_j` are iid, continuous, symmetric, exchangeable, and have true mean
zero: a flawless flat step under the frozen definition. Set lower endpoint
`-X_j/2`, upper endpoint `+X_j/2`, and a constant Haar reference. On the event
that all eight signs are `+1`, which has exact probability `1/256 =
0.00390625`, all differences lie in `[0.99,1.01]`. A range bound gives:

```text
AM-3 statistic > 261.4 > 4.2071245566.
```

Therefore the per-step false-failure probability is at least `0.00390625`,
already larger than the declared `0.002`, even under iid continuous symmetric
differences. This is not a rescoring of the frozen data and not an alternative
verdict. It is a mathematical counterexample to the claimed operating-
characteristic derivation.

Consequences for multiplicity:

- `12 x 4 = 48` is the correct frozen count.
- The union-bound arithmetic `48*0.002=0.096` is correct **conditional on** a
  valid `0.002` per-step bound.
- The continuous null disproves that bound under the declared null class.
- `48/256=0.1875` is only a reference showing why the premise matters, not a
  replacement family bound; the actual endpoint-sharing dependence was not
  calibrated.
- The Sidak number is irrelevant without independence and valid per-step
  p-values.

The use of the same `2^20` error corpus across frame draws makes the actual
paired differences particularly unsuitable for an unexamined iid-Gaussian
assumption. The artifacts provide no distributional diagnostic or exact
randomization calibration establishing the missing premise.

### 4.3 Positive-control admissibility and the cheapest decisive falsifier

The positive control is not admissible as a power test because it does not
force its advertised alternative. The cheapest repair is arithmetic and needs
no new object measurement:

```text
injection_i(c) = -Delta_i(0) + c*SE_diff(A,t_i),
```

which makes the realized post-injection step exactly
`Delta_i(c)=c*SE_diff`. A prospectively frozen version should choose the cell
and step independently of the scored realization, or use a held-out/synthetic
flat path, and should test the target step rather than the maximum over a cell
that may already contain another violation.

**Cheapest decisive falsifier B-F1:** before any successor real-arm scoring,
run two controls only:

1. an exact flat-path control with the measured eight-draw covariance shape,
   forced to `Delta=c*SE_diff` for the frozen `c` grid;
2. a null-calibration control using fresh/held-out seeds or an exact
   sign/randomization method whose assumptions match the paired differences.

Cost: arithmetic on eight-value arrays plus a bounded null simulation or exact
enumeration; no basis generation and no reduction. The exact continuous null
above is already an `O(1)` falsifier of the current `0.096` proof.

**Narrowest defensible Section B conclusion:** the frozen run validly shows
that the frozen positive-control design is defective in three cells. It does
not show that the AM-3 gate itself is powerless. The real-arm AM3-TIE/PARTIAL
readings remain withheld. The declared `0.096` is a nominal Gaussian/
Student-reference arithmetic value, not a justified bound under the frozen
exchangeability definition.

### 4.4 AM-4 scope

Section B's `V` and `D` path is not an AM-4 adjudicator. `V` is not invariant
under a general ambient isometry. With a coordinate-iid but non-rotational CBD
error law, `D` is invariant in distribution under signed coordinate
permutations but not under arbitrary ambient rotations; row permutations and
unimodular basis changes can alter the tail GSO frame. Nothing in Section B
tests those same-object transformations. Applying AM-4 adversarially therefore
reinforces the existing scope: this is an instrument-path check on named frame
presentations, never a lattice claim.

**Evidence classification:** the continuous exchangeable counterexample is
mathematical evidence; the `c=6` table and 48 stored steps are instrument
evidence; the corrupted shared `stdout.log` and otherwise intact JSON/snapshot
are infrastructure evidence. The stdout collision is not mathematical
evidence in either direction.

---

## 5. Section C — matched-`V` cross-family comparison

Producer: `TASK-20260806-c973e6`  
Frozen source: `prereg.md` Section 4  
Headline reviewed: **`L2 TAIL-SUFFICIENCY FALSIFIED` from two mechanical
firing pairs.** This wording is retained only as the frozen producer label; it
is not admitted as a conclusion here.

### 5.1 Arrangements in which the check could not fail

Two distinct “could not fail” arrangements matter.

**Named arrangement C-CF-1 — forced agreement at the degenerate coordinate
projector.** At `V=beta(1-beta/d)`, GR at `t=0` and TL at `u=1` are coordinate
projectors of the same distribution. An equality/support check there cannot
fail for the mechanism-relevant reason; agreement is forced by the object.
**Was the frozen scored family in C-CF-1? No.** The point was excluded by the
degeneracy and `m3` rules and retained only as an instrument check. That is a
sound exclusion.

However, the nearby instrument check exposes the score's fragility: in
`d140_b40` the equal-distribution null gives `|t|=4.5268`, above the frozen
critical value, and is saved from a formal firing only because the relative
difference is `4.5308%`, `0.4692` percentage points below the `5%` effect bar.
The producer identifies the immediate cause: TL is one repeated frame there,
so the paired SE is mis-scaled by a factor `3`. This is not a calibrated
false-positive rate, but it is a nearby-object warning that the t component can
fire on a null.

**Named arrangement C-CF-2 — a persistent family offset divided by vanishing
paired dispersion.** If the same finite error corpus gives all eight paired
differences an implementation- or family-specific offset greater than `5%`
with `SE_paired -> 0`, condition (i) diverges and condition (ii) is true; the
OR-over-pairs headline must fire even if the offset is a sampling/instrument
artifact. **Was the frozen run exactly in C-CF-2? No:** every scored pair had a
positive paired SE and distinct TL frames. **Was it close enough to dismiss the
concern? Not established:** the same finite error corpus is reused across all
frames, finite-`N` order-statistic error is omitted, and no exchangeable matched
family null calibrates the joint score. The degenerate nearby control shows the
relevant SE collapse can occur in the instrument.

**Named nearby control C-NC-EXCH:** two independently generated, genuinely
exchangeable frame families with equal `V` and equal relevant diagonal moments,
scored across independent error corpora. Its family-wise firing rate is the
missing null calibration.

### 5.2 Reachability and declared versus realized `n_C`

The exact TL reachable interval at `(d,beta)=(140,30)` is
`[8.5714285714,23.5714285714]`. The preregistration says the committed
unreduced `V=6.750435` is inside; it is not. Excluding that unreachable target
and applying the frozen survivor rule leaves only one, rather than two, graded
targets in that cell. Its planned three comparisons therefore become one,
giving `n_C=10`, not `12`.

The producer reports both critical values:

- declared `n_C=12`: `|t|crit=3.6358074219539622`;
- realized `n_C=10`: `|t|crit=3.4994832973505026`.

The declared-12 score is more conservative and both scores identify the same
two pairs, so this discrepancy is not the source of the firing. It is still a
material preregistration defect: the frozen family was not fully reachable, and
the exact family composition used for the advertised design did not exist.
The correct evidence is “ten realized reachable comparisons, with both
critical-value readings disclosed,” not “twelve matched comparisons.”

### 5.3 The float64/float32 match is not a semantic detail

The frozen requirement is `|V_TL-V_GR| <= 1e-9`. The projection consumes
float32 GR and TL frames. On those actual frames:

```text
passing pairs                    0 / 10
per-pair max residual range      8.842e-7 ... 2.305e-6
global max residual              2.3047695059e-6
```

The `<=5.33e-15` number belongs to the float64 closed-form inverse before the
TL frame is cast to float32. It is not the `V` of the frame passed to
`project_D`. Thus all ten confirmatory pairs fail the literal frozen matching
gate.

The producer's post-hoc robustness argument multiplies the mismatch by a
within-GR empirical `dD/dV <= 0.0048` and obtains a tiny effect. That is useful
forward guidance, but it cannot repair the confirmatory gate for two reasons:

1. the frozen tolerance was an antecedent, not an effect-size covariate;
2. a slope measured along GR does not bound the cross-family local response
   while the very proposition under test is whether `D` is determined by `V`
   alone.

I do not infer that the `1e-6` mismatch caused the observed `0.0040` and
`0.0063` differences; the scale comparison makes that implausible. The narrower
point is procedural and decisive: no exact frozen matched-`V` confirmatory pair
was actually measured.

### 5.4 Does the separation survive the instrument's own detection floor?

Under the instrument's **stated** between-frame floor, the two firing rows are:

| pair | relative difference | nominal relative floor | margin | `|t|` |
|---|---:|---:|---:|---:|
| `d100_b40 / graded_t0.0075` | `17.4773%` | `17.2268%` | `+0.2505` pp | `3.6887` |
| `d140_b40 / graded_t0.0050` | `23.7382%` | `10.5923%` | `+13.1459` pp | `8.1481` |

So the honest answer is split:

- the first apparent separation only barely clears the instrument's own
  nominal floor and is fragile;
- the second clears that nominal floor substantially and is the strongest raw
  instrument observation in the batch;
- neither clears a floor that includes finite-`N` order-statistic uncertainty,
  because no such floor was computed or null-calibrated.

All eight non-firing pairs have nominal floors above the `5%` practical bar
(`6.29%` to `17.23%`) and are correctly upper bounds, not agreement. The fact
that the strongest row survives the nominal floor should be preserved as raw
instrument evidence; it should not be promoted past the failed matching gate
and missing null calibration.

### 5.5 AM-4 invariance attack

Section C tests synthetic frame families under a coordinate-product error law;
it is not an AM-4 adjudicator. Applied adversarially:

- `V=sum(P_aa-beta/d)^2` and
  `m3=sum(P_aa-beta/d)^3` are invariant under coordinate permutations but not
  under general ambient isometries;
- `D` under the CBD coordinate law is invariant in distribution under signed
  coordinate permutations, not arbitrary rotations;
- the tail GSO frame can depend on row order and unimodular basis presentation;
- the TL construction is tied to coordinate pairs `(a,a+beta)`.

Thus even an exact equal-`V` tail difference would establish a statement about
these frame families and this coordinate error law at the measured quantile,
not about a lattice. This is distinct from AM-4's formal adjudicator rule:
because no adjudicator claim is made, failing AM-4 does not invalidate the raw
frame experiment; it forbids any silent lattice-level generalization.

### 5.6 Cheapest decisive falsifier, nearby control, and narrow conclusion

**Cheapest decisive falsifier C-F1:** prospectively rerun only the robust
`(d,beta,t)=(140,40,0.0050)` row and a matched null, with:

1. both GR and TL frames retained and projected in float64, with actual
   post-construction `V` verified within the frozen tolerance;
2. several pre-registered independent error seeds so finite-`N` quantile
   variation enters the uncertainty;
3. a genuinely exchangeable equal-`V`, equal-moment null family and a nearby
   different-`m3` control;
4. a pre-registered family definition and calibration method that does not
   assume exact Student `t` from exchangeability.

Cost: one toy cell, the existing eight frame seeds, `N=2^20` per declared
error seed, pure NumPy projection, no basis reduction. The producer's complete
four-cell workload took one run and no reduction; the successor should spend
its budget on independent error-seed replication rather than another broad
grid.

**Named nearby control:** `C-NC-EXCH` above, paired with the existing degenerate
coordinate-projector check but using two genuinely replicated families so the
SE is not collapsed by one repeated TL frame.

**Narrowest defensible Section C conclusion:** ten near-matched float32 toy
pairs were measured. One row, `d140_b40/graded_t0.0050`, shows a large raw
cross-family `2^-10` tail-quantile separation under the instrument's nominal
between-frame floor. The batch does not establish the frozen confirmatory
equal-`V` conclusion because zero actual pairs meet the preregistered match
tolerance and the false-falsification rate is not calibrated for the shared
finite error corpus. The established second-order variance identity remains
untouched.

**Evidence classification:** the reachable interval and second-order identity
are mathematical evidence; the ten pair arrays, nominal floors, and degenerate
nearby check are instrument evidence; dtype mismatch, environment-prose
discrepancy, hashes, and manifests are infrastructure evidence.

---

## 6. Cross-section scope and cost-model challenges

There is no end-to-end attack or cost model in these producer packages, and no
such model is inferred here. The relevant cost challenge is instead about
**instrument cost omitted from evidentiary claims**:

- Section A's apparent billions-of-SE separation is driven by deterministic
  between-presentation dispersion near machine precision; it is not an
  end-to-end statistical cost.
- Section B prices multiplicity but not the distributional assumptions needed
  to make each comparison a valid `0.002` test.
- Section C prices between-frame dispersion but not repeated error-corpus
  sampling of a `2^-10` order statistic, and its actual match precision is three
  orders of magnitude looser than the frozen threshold.

The cheapest successor work is therefore calibration and nearby-object
falsification, not more dimensions, more grid points, or any reduction.

---

## 7. Concrete successor requirements

Before any Coordinator decision treats a headline as more than stated here:

1. **Section A:** freeze and run `A-NC-ISO` over all eight existing seeds,
   including a general ambient isometry, transported projector, row
   permutation, and a bounded unimodular-shear ladder. State the theorem's
   object as `(frame, distinguished block)` if that is what is intended. Do not
   call the result a lattice property.
2. **Section A:** repair the N-A3 dimensional typo only through a successor
   preregistration and preserve the current artifact unchanged. Freeze one
   generator convention with separate names for identity-block size and
   q-row count.
3. **Section B:** replace the positive control with one that algebraically
   forces its claimed post-injection `Delta`; choose the step on held-out or
   synthetic data, or correct the injection for the pre-existing `Delta`.
4. **Section B:** replace the exact-`t_7` assertion with a prospectively valid
   calibration under the actual paired-difference null. State all assumptions;
   if an exact sign/randomization method is used, establish its symmetry or
   randomization justification. Recompute multiplicity only after per-step
   validity exists.
5. **Section C:** make the actual projected frames satisfy the registered
   `V`-match tolerance. A float64 closed form followed by float32 projection is
   not sufficient.
6. **Section C:** replicate the robust `d140_b40/t=0.0050` row with independent
   error corpora and a genuine matched-family null. Include finite-`N`
   order-statistic variation in the uncertainty and pre-register the family-
   wise calibration.
7. **Section C:** freeze reachability from exact intervals before declaring the
   family size; do not repeat the false `(140,30)` unreduced inclusion.
8. Preserve all current defects immutably: the Section A N-A3 typo, the Section
   C unreachable target, actual float32 residuals, wrong prose inversion count,
   environment-line mismatch, and shared-stdout infrastructure collision.
   Corrections require successor records, not edits.

### Final Red Team disposition

**RETURN TO COORDINATOR WITH SEVERE OBJECTIONS.** Admit the snapshot and raw
arrays as infrastructure-complete toy artifacts. Admit Section A only at the
explicit presentation/block boundary and retain `NEITHER` for both full
mechanisms. Treat Section B's only result as “the frozen positive control is
defective”; withhold real-arm readings and the `0.096` bound. Preserve Section
C's `d140_b40/t=0.0050` separation as a high-priority raw instrument lead, but
do not admit the frozen confirmatory falsification until actual-frame matching
and null-calibrated finite-sample uncertainty are prospectively repaired.

No official hypothesis, goal, experiment, evidence, or ledger status is changed
by this report.
