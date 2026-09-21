# TASK-20260805-49acd8 — red team notes

**Report:** `RT-20260806-d008e0` (`report.yaml`, same directory).
**Snapshot reviewed:** `7983a474be82684cca63ffd79495a3a50e582e62`.
**Role:** red team, independent session. I did not produce this package and did
not repair it.

**AGENTS.md rule 12 is UNMET and UNWAIVED.** This report changes the status of no
`EV-MLKEM-*` record and no `KN-*` entry, and proposes none. No ML-KEM break claim.
Session recovery, not key recovery. Nothing here is subtracted from the in-repo
`primal_bdd` margins of 2.80 / 6.04 / 1.28 bits. Toy scale is never crypto-scale.

**Independence is procedural only.** I resolve to `claude-opus-5`, as does every
producer in this batch and every participant in GOAL-MLKEM-003 and -004.

---

## 1. What I did

I re-derived rather than read transcripts. Three independent lines:

1. **Algebra**, on the rotation-invariance argument that killed the T2 gate, and
   on the goal record's `G <= log2 M` convexity bound.
2. **Two numpy runs** (my full budget of 2), which exhibit the dynamic range of
   the T2 headline statistic under a projector-side manipulation, and test whether
   the "expected contrast exactly zero" claim holds for the *declared* statistic.
3. **One retrieval**, of the paper the batch declared unobtainable, followed by a
   first-hand check of the quotations the kill verdict rests on.

Both runs are in the session scratchpad, reproducible from the code below. They
are offered as re-derivation, **not** as run records: they sit outside the
repository and outside any archive task, exactly as this reviewer's role requires.

---

## 2. The lead question — K1

`K1` is defined only in `dispatch_queue.json`, on the ledger-archive task
`TASK-20260805-d23bf0`:

> K1 (no standardised mode yields M > 2^20 -> the mechanism is capped at
> <= log2 M bits on session recovery, campaign closes with a measured cap)

Note first that **the string `2^20` appears in no committed T1 handoff.** T1's
receipt describes its `2^20` occurrences as "restating the task's own question",
but the T1 card as committed at `096b9256b` contains no such threshold. The
threshold lived only on the archive task's card. That is a minor traceability gap
and I record it because the census's own section heading — "Does any standardised
mode exceed 2^20?" — is therefore not traceable to the producer's own handoff.

**Verdict: K1 did not fire, and it was the wrong question.** Four reasons, in
`report.yaml` `k1_adjudication`; the short form:

- Its antecedent quantifies over what modes **yield**; a documentary census can
  only report what specifications **state**. For 8 of 14 deployment modes the
  specification states nothing, and two of those eight argue the other way in
  their own text (ECH: "anonymity sets will typically involve many connections";
  CMS: the recipient key "is expected to be carried in a long-lived certificate
  and used over and over").
- Its branches are `> 2^20` and `not > 2^20`. The actual outcome — *eight modes
  state nothing in either direction* — is in neither. This is `KN-TECH-1a5b7e`
  mode 4 in a documentary lane: a partition of the **range of the quantity**, not
  of the **space of outcomes**, with no NEITHER branch. The batch produced this
  same failure twice, in K1 and in T2's 4·s gate, from one root.
- Its consequent, "capped at `<= log2 M` bits", leaves `M` unbound. Read as
  `M <= 2^20`, it licenses a 20-bit cap. But where the census finds a number, that
  number is 1, giving `G <= log2 1 = 0` — **zero** bits of room, not twenty. A
  rule that turns "no number found" into "the number is 2^20" manufactures a bound
  in the unsafe direction out of an absence.
- "closes with a **measured** cap" is a category error. There is no contrast, no
  comparator, no spread. T1 says so and refuses to invent a null to look rigorous.

### Is "M = 1 everywhere that matters" the honest reading?

**No, and T1 is right to decline it.** Recounting `census.json` by hand:

| bucket | rows | what they actually say |
|---|---|---|
| normative per-key single use, ML-KEM, unambiguous | R20, R21 | SSH and IKEv2, both "REQUIRED by this specification" |
| single use with a named caveat | R09, R22 | MLS KeyPackage is a SHOULD with a last-resort exception, and R11 records RFC 9420 registers **no ML-KEM cipher suite**; Signal PQXDH's retrieved text names Crystals-Kyber-1024, not FIPS 203 |
| **mis-bucketed** | R12, R14 | `m` reads "**1 per handshake**", and R14's own `key_role` reads "ephemeral (client-generated), **reuse permitted**". Their governing clause R13 permits key-share reuse and delegates the count to FIPS 203, which states none |
| no count bound at all | R06, R10, R15, R16, R17, R18, R19, R23 | HPKE recipient keys, MLS last-resort, ECH configs, X-Wing, LAMPS X.509, CMS, PKCS#11 tokens, Signal last-resort |

So the count supporting a `G <= 0` cap is **2 firm and 2 caveated**, not 6.
`census.md` is honest at row level — every qualifier above is the producer's own
text — and the compression happens in the single distribution sentence, which the
snapshot commit then repeats without those qualifiers.

The count-unstated set is not a rump: HPKE recipient keys, CMS/S-MIME, X.509
certified decapsulation keys, ECH configs and PKCS#11 token keys are a large part
of real ML-KEM usage. Whether the `M = 1` modes are "the dominant deployment" is
itself unmeasured, and the census does not claim it. **The eight-row absence
genuinely leaves the door open, exactly as T1 carefully says.**

### What the census actually produced

Two things, and the second is the better one.

1. **A lane closure at the `docs/inventor-protocol.md` §4 standard.** Named
   obstruction: in R20 and R21, `M = 1`, so `G <= log2 1 = 0` by the goal's own
   convexity bound. The mechanism has *provably zero* room there. Forward guidance:
   the static/reuse lane. Per the goal's own `non_terminal_conditions`, that
   "retires the LANE, never the goal".
2. **A normative dead end in the deployed standards stack.**
   `draft-ietf-tls-hybrid-design-16` §2 requires reusing implementations to
   "ensure that the number of reuses of a KEM public key abides by any bounds in
   the specification of the KEM"; `draft-connolly-tls-mlkem-key-agreement-05` §6.2
   repeats it verbatim; FIPS 203 states no such bound (R01); SP 800-227 states
   none for the static case (R03); the CFRG draft endorses reuse for "multiple
   incoming ciphertexts" without a count (R24). **The one free parameter of the
   mechanism is bounded neither by mathematics nor by the standards stack.** That
   is a defensive-vetting output — this goal's actual remit — and it is the most
   transportable thing the campaign has produced.

---

## 3. T2 — does the rotation-invariance argument sink the whole design?

### 3.1 The argument is right, and the executor's conduct was right

For a Haar-random rank-β projector drawn independently of `e`, conditional on any
fixed `e ≠ 0` rotation invariance makes `‖Pe‖²/‖e‖²` equal in law to the squared
norm of the first β coordinates of a uniform point on `S^{d−1}`, i.e.
`Beta(β/2,(d−β)/2)`. The law does not depend on `e`, so it survives marginalisation
over any error law. My check: `e = (1,0,…,0)`, 16,384 Haar draws at `d=100, β=30`,
KS 0.00794 against `Beta(15,35)`, **p = 0.2506**, mean 0.29938 against `β/d = 0.3`.

So the frozen file's own closed-form justification — that the anisotropy "widens
the distribution of `R` by a factor of approximately `sqrt(1.36) = 1.166` in
standard deviation and therefore pushes the lower quantiles down" — is **wrong in
magnitude (the widening is exactly zero) and wrong in sign** (the second-order
effect that does exist raises the lower quantile). Both are one line of algebra,
available on the day the card was frozen.

The executor ran the broken demonstration as declared, reported the failure as
declared, *found* a statistic that works, labelled it as not the declared one, and
**left it unused**. It also refused to edit a hash-frozen file to correct the
Coordinator's arithmetic. That is the behaviour the contract exists to produce and
it should be recorded as such.

### 3.2 But the diagnosis is over-stated, and there is a second defect

**"Expected contrast exactly zero" is exact for the marginal law of `R`. It is not
established for the declared statistic**, which is the mean over 8 Haar draws of
the *per-draw* empirical `2^-10` quantile ratio. `E_P[q_p(R|P)]` is not the
`p`-quantile of the mixture `E_P[F_{R|P}]`; equality of mixtures does not transfer.

I derived the leading correction *before* measuring it. `Var_total` is Beta's
variance on both arms and decomposes as `E_P[Var(R|P)] + Var_P(E[R|P])`. Isotropic
`Σ` makes `E[R|P] = β/d` deterministic so `Var_P(E[R|P]) ≈ 0`; the anisotropic arm
has `Var_P(E[R|P]) = v > 0`. So the anisotropic arm's **within**-draw sd is smaller
by `sqrt(1 − v/Var_total)` and its per-draw lower quantile sits **higher**:

```
shift_ratio  ≈  (q_Beta − β/d)/q_Beta · ( sqrt(1 − v/Var_total) − 1 )
```

Measured, `d=100, β=30`, 64 Haar draws, `2^20` CBD errors, the card's own
`c₁=√1.6 / c₂=√0.4` two-block scaling:

| quantity | value |
|---|---|
| `Var_P(E[R|P])` isotropic | 3.407e-09 (at the sampling floor `Var/N ≈ 3.9e-09`) |
| `Var_P(E[R|P])` anisotropic | 1.697e-05 |
| **predicted** shift ratio | **+0.002718** (= +0.84 s in the card's own units) |
| **observed** shift ratio | **+0.001366 ± 0.002295** (0.60 SE) |

0.60 SE from zero and 0.59 SE from my prediction: at `n = 64` it excludes neither.
The executor's own V6b, at 64 draws and `2^18` errors, measured **+0.00267** —
closer to my closed form than to zero. Narrowest supportable statement: **zero to
leading order, predicted ≈ +0.8 s at second order, unresolved.** In every case far
below 4 s, so `INSTRUMENT FAILURE` is the correct adjudication; only the stated
cause is over-claimed.

**The second defect is independent and the commit does not mention it.** The gate
is `|mean₈(demo) − mean₈(haar)| ≥ 4·s` with `s` the **Haar** arm's per-draw sd —
the arm whose between-draw location variance is structurally ≈ 0. From the
package's own `results.json`:

| cell | sd(real)/s | sd(haar)/s | sd(demo)/s | **SE(diff of 8-draw means)/s** |
|---|---|---|---|---|
| d100_b30 | 1.77 | 1.00 | 4.86 | **1.75** |
| d100_b40 | 0.63 | 1.00 | 5.79 | **2.08** |
| d140_b30 | 1.21 | 1.00 | 4.33 | **1.57** |
| d140_b40 | 1.48 | 1.00 | 5.75 | **2.06** |

So "4 s" is a ≈2.0–2.5σ test, and the four observed shifts are **0.45, 0.52, 1.25
and 1.81 σ** of the correct standard error — an ordinary null. The gate would have
been degraded even for a demonstration with a large true effect. It also fully
explains the producer's anomaly A1 (the rising 0.79 < 1.09 < 1.97 < 3.73) as `s`
fluctuating, which is what the producer guessed and declined to read into.

### 3.3 The real-basis arm is NOT undermined — and here is the control that proves it

**The rotation-invariance argument does not generalise, and the reason is precise.**
It applies to the Haar arm because that projector's *law* is `O(d)`-invariant. The
real arm's projector comes from a q-ary lattice `Λ_q(A)`, whose law is invariant
under the **signed-permutation (hyperoctahedral)** group, not `O(d)`. A `CBD_{η=2}`
error is a product measure over coordinates — also hyperoctahedral-invariant, not
rotation-invariant. Real projector and error share exactly the symmetry that would
have to be broken for a signal to exist, so a signal is *possible*.

The mechanism is concrete. For a coordinate-aligned rank-β `P`,
`R = Σ_{i∈S} eᵢ² / Σᵢ eᵢ²`, and `Var(Σ_{i∈S} eᵢ²) = β(E[e⁴] − 1) = 1.5β` for
`CBD_{η=2}` (`E[e⁴] = 2.5`, excess kurtosis −0.5) against `2β` for a Gaussian.
`R` is under-dispersed by a factor 0.75 in variance, so its lower quantiles sit
**above** the Beta quantiles.

I measured it. `d=100, β=30, k=d/2, q=3329`, `2^20` `CBD_{η=2}` errors shared
across arms, the package's own frozen quantile estimator, 8 draws per arm:

| arm | `r(2⁻¹⁰)` mean ± sd | shift from Haar, in units of the package's own `s` |
|---|---|---|
| `haar` (the package's null) | 1.00116 ± 0.00236 | — |
| **`coord`** (β random coordinate axes) | **1.09402 ± 0.00396** | **+39.3 s** |
| **`qary_raw`** (tail GSO of the **unreduced** q-ary basis) | **1.03719 ± 0.00236** | **+15.3 s** |

The frozen gate demanded **4 s**. A projector-side demonstration clears it by ~10×,
and the scientifically interesting arm — the unreduced q-ary basis at the same
`(d, k, q)` — clears it by ~4×. Against the correctly computed SE of the difference
of two 8-draw means these are ≈57σ and ≈30σ.

And it is **monotone**, which `GOAL-MLKEM-004` never achieved
(`DEC-20260805-0b3e11` records its sensitivity curve was provably non-monotone with
a crossing at `t* = 0.7259`, which is why no operational direction was available
there). Graded family `Q_t = QR(√(1−t)·E_S + √t·G)`, `t=0` coordinate-aligned,
`t=1` Haar:

| `t` | 0.00 | 0.05 | 0.10 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---|---|---|---|---|---|---|
| `r(2⁻¹⁰)` | 1.09304 | 1.08590 | 1.07675 | 1.05055 | 1.01755 | 1.00159 | 1.00098 |

Strictly decreasing, five interior points — `KN-TECH-1a5b7e`'s monotonicity
refinement satisfied, so a **directional** reading is available.

**Therefore C3 is not unmeetable by this design.** The defect is one wrong choice:
`prediction_frozen.json` names the removed object as "the PROVENANCE OF THE
PROJECTOR" and then declares a demonstration that manipulates the **error law**.
Obligation 3 is a property of an *(object, statistic)* **pair**; this design
satisfies it per statistic and violates it per **object**. The entry's own mode-2
catch line — "Obligation 3 applied per statistic, not per null" — needs the
extension "…and per object".

### 3.4 What that does *not* license

I do **not** re-read the package's real-arm ratios (pooled `2⁻¹⁰`: 0.99829,
1.00054, 0.99954, 1.00100) as a finding here. Its gate failed, and re-reading them
now is exactly the post-hoc statistic substitution the executor correctly refused.
The point is only that a *successor* with a valid pre-registered demonstration can
read them — and that without the coordinate-aligned arm they would be
uninterpretable anyway, since they conflate "the BKZ tail subspace is not
coordinate-aligned" with "CBD is close enough to spherical at `d = 100–140`".

**The decay prediction, which must be pre-registered as a falsifier.** The
parameter that should destroy this signal is `β`. The alignment departure scales
like `sd(R)/E[R] ~ sqrt(2(1 − β/d)/β)`, so it should **decay as ~1/√β** at fixed
`β/d`. A departure that stays flat as `β` grows is the canonical artifact tell
(`docs/inventor-protocol.md` §3). As a property of the formula only: at `β=606,
d=1420` the same alignment gives roughly a fifth of the toy-scale departure.
**Nothing measured at `d ≤ 140, β ≤ 40` is transported to `β = 606, d = 1420`.**

---

## 4. T4 — I attacked the kill verdict and it survived, but the acquisition record does not

### 4.1 The paper is obtainable, in two commands

`reads.md` §3.2 lists eight route rows and states "no institutional copy found".
None of the routes is an open-access aggregator. One call:

```
curl -s https://api.openalex.org/works/doi:10.1145/3460120.3484819
```

returns `is_oa: true`, `oa_status: gold`, and a repository location at
`https://pure.tue.nl/ws/files/362308384/3460120.3484819.pdf`. That URL returns
**HTTP 200, application/pdf, 1,832,736 bytes, 17 pages**,
sha256 `2198eaf192cd58aa48fc272ebe18c66145476bfbe6a951fadb15dc6eb59bcb4c`.
Elapsed: about ninety seconds.

**Scope:** this is the TU/e green-OA copy of the **CCS'21 published version**
(DOI `10.1145/3460120.3484819`), not the ePrint 2021/1351 PDF. The two may differ
and I assert only what I read.

Under `docs/inventor-protocol.md` §4, "unobtainable from four routes" is a count of
what the search did — a fatigue report about the search, whose honest status is
`unverified` — and it may not be presented as a property of the document. The
commit presents it as the latter. ("four" is also Coordinator-authored: the
producers' own list has at least seven failed routes for the body.)

### 4.2 Bernstein's Appendix A.4 quotations check out, at first hand

The disputed text sits on the paper's **third page** (running page 2724; the paper
begins at 2722) — exactly Bernstein's "[47, page 3]" and "[47, footnote 2]".

Body, verbatim from the retrieved copy:

> we do not have self-reductions that allow us to directly conclude that
> `Adv^IND-CPA_PKE ≈ Adv^(n,qC)-IND-CPA_PKE` … Nevertheless, if we assume the
> hardness of MLWE as originally defined for the purpose of worst-case to
> average-case reductions [28, 30, 32] **where the number of samples (using the
> same secret) is unlimited**, then we can show that
> `Adv^IND-CPA_PKE ≈ Adv^(n,qC)-IND-CPA_PKE`. In particular, if we assume that
> distinguishing `{(Aᵢ, Aᵢ·sᵢ + eᵢ)}_{1≤i≤k}` from uniform is hard for
> `k = max(n, qC)`,² then using the transformation from [2] …

Footnote 2, verbatim:

> Unless `k` is so large that the Arora-Ge [3] attack applies, it is not known that
> seeing more samples makes the MLWE problem any easier in practice. … the secrets
> in the `(n, qC)`-IND-CPA game are all distinct, and so it is a **plausibly much
> harder problem** than MLWE with many samples for the same secret.

Bernstein's characterisation is accurate on every point I could check: the
conditionality, the unlimited-sample wording, the `max(n, qC)` sample count, the
Applebaum–Cash–Peikert–Sahai transformation, the Arora–Ge footnote, and the
"plausibly much harder problem" phrase.

**So the kill verdict is confirmed, and on a stronger basis than the package had.**
The authors themselves write they "do not have self-reductions that allow us to
directly conclude" the equivalence and obtain it only under an explicitly stated
assumption; the passage contains no concrete parameters, no tightness constant, no
Kyber or ML-KEM bit figure, and no claim about the cost of the best known lattice
attack. A conditional equivalence between advantage functions is not a
concrete-cost bound on a primal attack against many ciphertexts under one key.
**Kill (iii) does not fire.** I attacked this verdict and failed; that is the
clearest negative result in this report, and it discharges the precondition
`reads.md` §3.5 attached to it.

### 4.3 Does footnote 19 leave enough room to be worth batches?

`reads.md` §1.3 records Bernstein's footnote 19: the concrete question is "not
addressed by this paper's asymptotics", and §1.3's caveats add "Perhaps Kyber-512
is too small for the heuristic multi-target speedups to be applicable". Read
together with this goal's own `ceiling_known_in_advance` — which forecloses moving
an exponent, provably — **the remaining space is a constant-factor,
deployment-parameterised question, and it is narrow.** It is worth further batches
for one reason and not the other: not because it might yield an exponent (it
cannot), but because it is a *defensive vetting* question with a cheap decisive
experiment and an already-sourced standards-side finding. If the decisive
experiment (§6, B2-A) also fails to discriminate, that reason expires and the
honest move is to hand the deployment finding to a standards-facing output.

---

## 5. Audit of snapshot commit `7983a474`

**Assume a tenth defect. There is one, and it is a manufactured number.**

### What is right, and worth saying

No sentence in the commit reads as a security claim. It carries "Session recovery,
not key recovery; nothing subtracted from the 2.80/6.04/1.28 bit primal_bdd
margins. No ML-KEM break. Rule 12 UNMET and UNWAIVED." It labels the package
`UNREVIEWED`. It self-reports four Coordinator defects, all caught by producers.
It does not inflate affected-vs-safe scope anywhere. `"Control PASSED verbatim at
delta 0.00e+00, twice, byte-identical"` traces exactly to
`TASK-20260805-9672b3/receipt.json`: `"run_twice": "… Byte-identical stdout both
times."` — no defect there.

### The defects

| # | sentence | finding |
|---|---|---|
| **D-1** | "P1 and P2 passed by **30-100x**" | **Material.** `grep -rn "30-100"` over the whole batch tree returns nothing — neither endpoint is a producer number. Recomputed from `results.json`: P1 @ 2⁻¹⁰ margins **29.3×, 92.9×, 108.1×, 50.1×**; P1 @ 2⁻¹⁶ margins **10.6×, 200.5×, 24.5×, 95.7×**; **P2 margins 290,246× / 268,923× / 359,398× / 403,519×**. Wrong at both ends for P1, wrong by 3–4 orders of magnitude for P2. The commit's own preamble says "Producer numbers stated as the producers'". The error is deflationary and the clause after it is correct, so nothing downstream is inflated — but a false number in an immutable commit is precisely the propagation hazard `KN-TECH-1a5b7e` records. |
| **D-2** | "6 fix M = 1" | **Material.** Repeats the producer's bucket without the producer's own row-level qualifiers. R12/R14 read "1 **per handshake**" and R14's own `key_role` reads "reuse permitted"; R09 is a SHOULD under a spec registering no ML-KEM cipher suite; R22's retrieved text names Kyber-1024. Breaches "with their own qualifiers". |
| **D-3** | "the frozen 4s gate failed … **BECAUSE** … EXPECTED CONTRAST EXACTLY ZERO" | **Material.** States one cause as *the* cause, and that cause is exact only for the marginal law (§3.2). The independent calibration defect — 4 s expressed in the per-draw sd of the arm with the structurally smallest between-draw variance, against a true SE of 1.57–2.08 s — is not mentioned. |
| **D-4** | "unobtainable from **four routes**" | **Material.** "four" is Coordinator-authored; the producers list ≥7 failed routes. And the document is obtainable (§4.1), so the sentence states a property of the search as a property of the document. |
| **D-5** | "**5,582** entries carry citation_verified: read with every identifier null" | **Minor.** No denominator, in a list headed "is SYSTEMIC" and flanked by two properly-fractioned figures. `ls knowledge/literature \| wc -l` = **7,809**, so 5,582/7,809 = 71.5%. `KN-TECH-1a5b7e`'s denominator caution has now cost three Coordinator commit messages, not two. |
| **D-6** | "KILL (iii) DOES NOT FIRE" | **Minor.** Drops `reads.md` §3.5's bolded precondition: "A Reviewer should obtain 2021/1351 and check the quotes at page 3 and footnote 2 **before this verdict is treated as settled**." The commit substitutes the weaker "its body was NOT summarised". The precondition is now discharged (§4.2), so the remedy is to record the discharge. |

**One adjacent finding, in coordination commit `0585d985f` rather than the
snapshot.** "Var_P(E[R\|P]) moves by a **factor 1198** against a closed form,
**agreeing to 0.69%**" attaches the agreement to the *factor*. The agreement is on
the **numerator** (1.508e-05 against the derived 1.497e-05). The factor's
denominator is the isotropic arm's `Var_P(E[R|P])`, which is exactly the sampling
floor, so the factor measures the floor: the executor's floor gives 1198, mine
gives **4982** for the identical construction. Report the signed numerator against
a floor stated as a floor.

**Not present:** the fabricated-attribution class (a string quoted as a producer's
that appears in no producer artifact). Every quoted string in the commit traces to
a declared artifact path. D-1 and D-4 are manufactured *numbers*, not manufactured
*quotations*, which is a lesser but real class.

---

## 6. Should BATCH-002 run?

**Yes — on a narrowed, pre-registered brief, and not by default.**

The goal is deliberately unbounded, so `closed_at_budget` cannot fire and "keep
going" is free to say. So let me state what would make me say **no**: if the only
proposal were another variation of the T2 measurement without the missing arm, or
another census, or another literature sweep, I would recommend pausing and handing
the deployment finding to a standards-facing output. That is not the situation.

**It also cannot close.** C1 is untouched (no numeric `dβ` bound with a core-SVP
bit value; T3's `design_audit` is explicitly `NOT A FINDING` and its quantities are
forced a priori). C3 is unmet. The stop rule requires C1–C3. And the goal's own
`non_terminal_conditions` bar closing on a negative result, a failed task, a lane
closure, or a judgement that the problem looks hard — three of which are on offer.

| | task | criterion | compute |
|---|---|---|---|
| **B2-A** | Re-run T2 at the same four cells with the same frozen P1/P2, same Haar null, same null-arm-first discipline. Replace **only** the sensitivity demonstration with the graded projector family `Q_t = QR(√(1−t)·E_S + √t·G)` at `t ∈ {0, .05, .10, .25, .50, .75, 1}`, threshold in units of **SE of the difference** at the declared draw count, both ends and monotonicity reported. **Add the missing arms**: unreduced q-ary tail GSO, LLL-only tail GSO, and a Gaussian-error null-of-the-null. Pre-register the ~1/√β decay as a falsifier at ≥2 β beyond {30,40}. | **C3** | small — BKZ reductions already cached; the new arms are ~1 s/draw of numpy |
| **B2-B** | The bound, using T3's already-verified conversion instrument. State C1 in its own sanctioned form — "≤ X bits, of which Y is model assumption, and X may be 0" — **separately for the two lanes the census separates**: (a) normative single-use lane, X = 0 exactly, naming R20/R21; (b) count-unstated lane, no bound sourceable, the number is a deployment-policy choice. Print the `f''` sensitivity table C1 requires and label it a model readout. Address the memory/data axes: a cost model that prices only BKZ blocks does not price a multi-ciphertext attack. | **C1** | zero |
| **B2-C** | Write up the normative dead end (`hybrid-design-16` §2 → FIPS 203 → nothing; SP 800-227 §4.1; CFRG draft §4) as a first-class defensive finding. All four rows already sourced with section and retrieval date. | C2 / defensive | zero |
| **B2-D** | Add an OA-aggregator step (OpenAlex/Unpaywall → institutional repository) to the literature-acquisition path before any further "unobtainable" finding is recorded, and record the 2021/1351 retrieval as a correction to this batch's acquisition table. | process | zero |

**Must not do:** re-score this batch's P1/P2 against a different rule; treat the
census as a measured cap or quote a 20-bit cap from it; transport any `d ≤ 140,
β ≤ 40` number — including mine — to `β = 606, d = 1420`; promote any `EV-MLKEM-*`
or `KN-*` record while rule 12 is unmet.

**Next concrete action: dispatch B2-A.** It is the only task that can discharge a
completion criterion; its sensitivity demonstration is already exhibited with a
numeric threshold, both ends of its dynamic range, five interior points and a
monotonicity result; and its expensive component is already cached.

---

## 7. Reproduction of my two runs

Both are pure numpy + scipy, single-cell, single-instance. They exhibit a dynamic
range; they establish no property of ML-KEM. They ran in the session scratchpad,
outside the repository and outside any archive task.

```python
# Run 1 — dynamic range of the T2 headline statistic under projector manipulation.
# d=100, beta=30, k=d/2, q=3329, N=2^20 CBD_{eta=2} errors shared across arms,
# frozen estimator q_emp(p) = sort(R)[round(p*N)-1], 8 draws per arm.
# Arms: haar = QR(Gaussian d x beta)
#       coord = beta random distinct coordinate axes
#       qary_raw = tail-beta GSO of the UNREDUCED q-ary basis [[I_k, A],[0, q I_{d-k}]]
#                  (this is fpylll's IntegerMatrix.random(d,"qary",k=d//2,q=q) shape,
#                   which measure.py line 102 uses)
#       graded(t) = QR( sqrt(1-t)*E_S + sqrt(t)*G )
# Plus: e=(1,0,...,0) over 16,384 Haar draws, KS against Beta(15,35).
# Wall clock 56.4 s.

# Run 2 — is "expected contrast exactly zero" exact for the DECLARED statistic?
# Same cell, 64 Haar draws, isotropic vs the card's own two-block anisotropic
# scaling c1=sqrt(1.6), c2=sqrt(0.4) applied to the SAME CBD draws.
# Closed form predicted BEFORE measurement:
#   shift ~= (q_Beta - beta/d)/q_Beta * (sqrt(1 - Var_P(E[R|P])/Var_Beta) - 1)
# Wall clock 47.3 s.
```

Full scripts: `rt_probe.py` and `rt_probe2.py` in the session scratchpad;
outputs `rt_probe_out.json`, `rt_probe2_out.json`. Every number quoted in
`report.yaml` and above is from those outputs or from a declared artifact path in
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-a51f91/`.

## 8. Limitations of this report

- Single cell (`d=100, β=30`), single instance, for both probes.
- `Q15` — the `primal_bdd(..., optimize_d=False)` anomaly — is **unchecked**: it
  needs the lattice-estimator at `/tmp/le`, outside my read scope.
- I read the **CCS'21 published version** of Duman et al., not ePrint 2021/1351.
- Independence is procedural only; every participant resolves to `claude-opus-5`.
- I did not commit anything, did not edit any producer artifact, and wrote only
  inside `.../tasks/TASK-20260805-49acd8/`.
