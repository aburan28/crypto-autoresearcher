# Red Team report — EXP-ICINV-fcb497

```yaml
red_team_report:
  id: RT-20260807-257239
  task_id: TASK-20260807-68335d          # allocated for this report; bind or replace at archive
  reviewed_snapshot_commit: 0e78af07a
  claim_under_review: >-
    EV-ICINV-c68f13 / DEC-20260807-4261e3: that the multiplicative-order deficit
    observed at the three smallest decades of EXP-ICINV-fcb497 is UNRESOLVED and
    ambiguous between a CM reading and an integer reading (CONFOUND-1 / inference
    (4)(B)); that the remedy is the discriminating replication of
    KN-OPEN-2c095b and DEC-20260807-4261e3 next action N3; and that STAGE 0's
    gating question is an infrastructure-blocked retrieval.
  verdict_on_transition: >-
    `replicate` at `preliminary` is the right TRANSITION and the right STRENGTH.
    The REPLICATION AS SPECIFIED (N3) is the wrong experiment: its pre-registered
    discriminator tests a hypothesis that is already refutable from the archived
    per-instance tables, and its "else" branch would report a false positive as
    "the interesting signal". N3 must be rewritten before dispatch. STAGE-0
    successor N4 should run first, and it is not blocked.
```

**Status of the computations in this report.** Every number below marked
*[RT-probe]* was computed by this red-team session from the **archived
per-instance tables** of the 13 committed runs. They are exploratory red-team
probes, **not evidence**: no run record, no pre-registration, no manifest, no
certificate. They are reported to show that a cheap discriminating measurement
exists and what it indicates, and they must be re-derived inside a
pre-registered successor contract before any record cites them. Nothing in this
report edits any committed artifact.

---

## RT-1 (CRITICAL) — CONFOUND-1's "integer reading" is empirically false, and N3's decision rule would fire the wrong branch

**Targets.** `EV-ICINV-c68f13` `unresolved_confounds` CONFOUND-1 and `inference`
item (4)(B); `DEC-20260807-4261e3` `rationale` item "(B) A MISMATCH BETWEEN THE
NULL AND THE OBJECT" and `next_actions` N3; `KN-OPEN-2c095b` §"Statement",
§"Cheapest discriminating test", §"What would close this".

**The claim attacked.** CONFOUND-1 says the deficit is ambiguous between a CM
reading and the *integer reading*: "small integers simply have smaller
multiplicative order than uniform units mod the same `d`". N3 pre-registers a
two-branch discriminator on exactly that: curve ≈ small-integer null ⇒ integer
reading; curve below the small-integer null ⇒ "CM reading; that is the
interesting signal".

**What I found.** The integer reading is false at every tested decade, and the
control that KN-OPEN-2c095b calls the *cheapest discriminating test* can be run
right now from the committed tables — every instance already carries `d`, its
**verified full factorisation**, and `lambda`, so no curve, no point counting
and no new factoring is needed. *[RT-probe]*, small-integer null `a` uniform in
`[2, ⌊√d⌋]` with `gcd(a,d)=1`, identical order code path, 3 decades × 3 data
seeds × 3 independent RNG draws, `ks_crit = 0.0607`:

| | KS(small-int null, uniform-unit null) | KS(curve, small-int null) | KS(curve, uniform-unit null) |
|---|---|---|---|
| k12 (9 cells) | 0.022 – 0.041 | 0.077 – 0.094 | 0.066 – 0.101 |
| k14 (9 cells) | 0.015 – 0.045 | 0.117 – 0.142 | 0.104 – 0.121 |
| k16 (9 cells) | 0.019 – 0.038 | 0.066 – 0.103 | 0.072 – 0.095 |

Every one of the 27 small-integer-vs-uniform-unit comparisons is **below** the
critical value: a uniformly random small integer mod `d` is not distinguishable
from a uniformly random unit mod `d` by this statistic at this sample size.
Every curve-vs-small-integer comparison is **above** it, and is equal to or
larger than the curve-vs-uniform-unit deficit the record reports.

**Consequence.** N3 as written would return "curve sits below the small-integer
null too" and, by its own pre-registered rule, would record **"CM reading; that
is the interesting signal"**. RT-2 shows that conclusion is wrong. A
pre-registered rule that is guaranteed to produce a false positive is worse than
no rule, because it launders the false positive through SR7's
no-re-scoring-after-the-fact protection.

**Correction needed.** `KN-OPEN-2c095b`'s dichotomy and `DEC-20260807-4261e3`
N3's discriminator must be superseded by a three-arm design (RT-2). The
smallness of `λ` is not the confound; CONFOUND-1 names the true structural fact
(`|λ| ≤ √p + 1`) but attaches the wrong consequence to it.

**Cheapest test that settles it.** Already run above; ~90 seconds of CPU against
the committed tables, zero new instances.

---

## RT-2 (CRITICAL) — the deficit is reproduced by an object with no elliptic curve in it: the missing null is the curve-free family, not the small-integer family

**Targets.** `EV-ICINV-c68f13` `inference` (4); `DEC-20260807-4261e3` rationale
"(A) … (B) … (C)"; `KN-OPEN-2c095b` §"Why the question exists" and §"Cheapest
discriminating test".

**The derivation the record stopped one step short of.** CONFOUND-1 derives
`λ = ±round(t/2)`, hence `|λ| ≤ √p + 1`. Correct — I verified the derivation and
verified it against **all 21 000 archived instances** *[RT-probe]*. But T3 and
the frozen `lambda_rule` give more. With `v = ±1` and `λ = ∓u`,

```
d = N(u + vπ) = u² + uvt + v²p   and   λ ≡ -u·v⁻¹  =⇒  λ² - tλ + p ≡ 0 (mod d)
```

and, because `t - 2λ = ε ∈ {0, ±1}` (this is what `u = round(-t/2)` *means*),

```
d = p - λ² - ελ      exactly, as integers, with ε ∈ {0, ±1}
```

Checked on every archived instance: exact on 21 000 of 21 000, modulo the
handful of large-conductor rows where `|u| > d/2` so the stored residue is not
the signed representative (see RT-7). Two consequences the record does not
state:

1. **`λ² ≡ p (mod d)`, always.** The curve-derived `λ` is not merely a small
   integer; it is a *square root of `p` modulo `d`*, and the residue `p mod d`
   is the perfect square `λ²` whenever `λ² < d`.
2. **`d` is a deterministic function of `(p, λ)`.** Conditional on `d`, the
   value `λ` is forced up to sign and an `ε` shift. The matched null therefore
   draws from a set of `(d, a)` pairs of which **all but ~2 are arithmetically
   unrealisable** — it is not "unmatched on the support of λ", it is matched on
   a marginal while destroying the only coupling in the object.

**The null-object control (`docs/inventor-protocol.md` §3).** The identical
measurement against a random instance of the same shape, with no elliptic curve
anywhere in it: draw `λ'` uniform in `[2, ⌊√p⌋]`, set `d' = p - λ'²`, compute
`m' = ord_{d'}(λ')`, and compare to a uniform unit mod the **same** `d'`.
*[RT-probe]*, n = 1000, `ks_crit = 0.0607`:

| decade | curve vs its uniform-unit null | **curve-free vs its uniform-unit null** |
|---|---|---|
| k12 | 0.087 | **0.107** |
| k14 | 0.121 | **0.162** |
| k16 | 0.072 | **0.113** |
| k18 | 0.032 | 0.035 |
| k20 | 0.081 | **0.086** |
| k22 | 0.061 | **0.088** |
| k24 | 0.044 | 0.035 |

Same sign (curve-free median below its null median at all seven decades),
comparable or larger magnitude, and **the same non-monotone failure to decay**.

**What this settles.** The deficit is a property of the coupled pair
`(λ, d = p - λ² - ελ)` — i.e. of `λ² ≡ p (mod d)` — and is reproduced without
elliptic curves. Under the inventor protocol this is a **controlled null**, not a
finding. The record's three-way split is therefore wrong in its options as well
as its weights:

- (A) "small-`d` arithmetic artefact" is recorded as SUPPORTED by the monotone
  rise of distinct `(d,m)` pairs and by sub-criticality at k24. That reading is
  weakened: the curve-free null shows the deficit still present at k20 and k22
  where atomicity is already mild, and the seven-point sequence is non-monotone
  in both samples. Reading a trend off seven non-monotone points is exactly the
  "what should have destroyed it" failure the protocol flags: `p` is the
  parameter meant to destroy this quantity, and it does not decay in `p`.
- (B) as stated (smallness of `λ`) is **refuted** by RT-1.
- (D), missing entirely: **the algebraic coupling**, which the curve-free null
  reproduces.

**Correction needed.** Supersede CONFOUND-1 and `KN-OPEN-2c095b` with the
identity `d = p - λ² - ελ`, `λ² ≡ p (mod d)`, and make the **curve-free family
the primary null**. Restate the open question as: *does the curve-derived sample
differ from the curve-free `(λ, p-λ²)` family at all, once both are compared
against their own matched uniform-unit null?* — i.e. does the class-number
weighting on `t` contribute anything. That is the only place an elliptic curve
can still enter.

**Cheapest test.** Three arms, one pass, seconds of compute, no new curve
sampling for two of the three arms:
`A` = curve-derived (already archived); `B` = curve-free `(λ', p-λ'²)`;
`C` = uniform-unit null on the matched `d`. Pre-register on `KS(A,B)`, not on
`KS(A,C)`. **A fourth arm is a trap and must be excluded**: "another square root
of `λ²` mod `d`" is degenerate — the square roots of `λ²` are `λ` times the
2-torsion of `(Z/d)*`, so their orders differ from `m` by at most a factor 2 and
the arm returns `KS ≈ 0.01` by construction *[RT-probe: 0.008–0.019 across
k12–k24]*. I flag it because it is the arm a reader of `λ² ≡ p (mod d)` will
reach for first.

---

## RT-3 (HIGH) — STAGE 0 is not blocked, and §4.14 of the source anticipates the mechanism

**Targets.** `experiments/EXP-ICINV-fcb497/specification.yaml`
`stage0_retrieval_frozen.primary_source.urls_in_order` and
`fallback_source.paths_in_order`; `EV-ICINV-c68f13` OBS-1;
`DEC-20260807-4261e3` next action N4 and the `status_transitions` entry for
`IDEA-20260807-9fb27c`; `KN-OPEN-2c095b` §"Related, and deliberately not merged".

**The 403s are infrastructure and are not being read as mathematics here.** What
I am attacking is the *frozen retrieval list*, which contains four URLs, all on
`eprint.iacr.org`. The paper is not unavailable; the contract pinned one
publisher domain.

Retrieved this session by `curl`:

```
https://arxiv.org/pdf/2003.10118   HTTP 200   371582 bytes
sha256(velu_arxiv.pdf) = 058162905a84b39fc6e23f12341b02899cce9328e9b45ac20750fa86cdfedd11
title: "FASTER COMPUTATION OF ISOGENIES OF LARGE PRIME DEGREE"
authors: DANIEL J. BERNSTEIN, LUCA DE FEO, ANTONIN LEROUX, AND BENJAMIN SMITH
arXiv:2003.10118v1 [cs.CR] 23 Mar 2020   (only one version listed on the abs page)
```
`https://msp.org/obs/2020/4-1/obs-v4-n1-p05-s.pdf` also returns HTTP 200 with
`application/pdf` (964 073 bytes) and is a second independent path.

Text extracted with `pdftotext 26.04.0`;
`sha256(velu.txt) = 8107b15796deff6270f618211c093d7c91890af4932daf5ba1ffc9ed04500953`,
83 739 bytes. Byte-verified substrings, with offsets into that text:

- offset **24651**: Theorem 4.11 — `"in e\nO(max(#I, #J, #K)) Fq -operations"`,
  under the hypothesis (same theorem) `"Let P be an element of E(Fq )"`.
- offset **27015**: §4.14 *Irrational generators* —
  `"need not be in E(Fq )"`, in the sentence *"The point P in Lemma 4.9,
  Algorithm 2, and Theorem 4.11 need not be in E(Fq): everything is defined over
  Fq if x(P) is in Fq. More generally, take P in E(Fqe) with x(P) in Fqe for some
  minimal e ≥ 1. The q-power Frobenius π on E maps P to π(P) = [λ]P for some
  eigenvalue λ in Z/nZ of order e in (Z/nZ)*."*
- offset **28171**: `"typically e is in O(ℓ)"`, in *"…it should be noted that the
  requirement that (I, J) = (LI′, LJ′) is quite strong: typically e is in O(ℓ),
  so #L is not in Õ(√#S), and a suitable index system (I, J) with #I and #J in
  Õ(√#S) does not exist."*

**Three consequences.**

1. **The gating question has an answer.** The `Õ(√ℓ)` count is stated in
   `F_q`-operations under the hypothesis that the kernel generator's
   `x`-coordinate is `F_q`-rational; §4.14 treats the irrational case explicitly
   and states that the `F_q`-descent requires a Galois-stable index system that
   *typically does not exist*. That is closer to the KERNEL_FIELD reading than
   to BASE_FIELD, but it is not the binary the contract's classifier encodes —
   the correct axis is the field of definition of `x(P)`, and the obstruction is
   the index-system condition, not the arithmetic cost per operation.
2. **`IDEA-20260807-9fb27c`'s mechanism is anticipated in the source.** §4.14's
   `e` *is* the experiment's `m = ord_d(λ)` — same object, same definition — and
   `"typically e is in O(ℓ)"` is BDFLS's own statement of **HEUR-ORD-1**. The
   proposal's `novelty_status: unverified` with an unread BDFLS attribution
   should become *anticipated by BDFLS §4.14*, not left at `unverified`. This
   is a scope and novelty correction, not an adverse mathematical finding: the
   21 000 measured instances remain a toy-scale empirical check of a remark the
   source asserts without data.
3. **The 127 undetermined barrier rows are undetermined for exactly one
   reason.** I read all 175 table rows plus 2 required rows: every one of the
   127 carries the *identical* reason string, keyed to STAGE-0 AMBIGUOUS. So N4
   unblocks all 127 at essentially zero compute.

**Caveats I hold myself to.** arXiv v1 is not the ANTS XIV proceedings version;
this retrieval is not a run record; the contract's byte-verification path must
be re-run against a pinned artifact under a new run id, exactly as N4 says. I
supply the sha256 so the claim is checkable rather than asserted. Nothing here
converts N4 into a research task.

**Cheapest test.** Re-run STAGE 0 unchanged with
`https://arxiv.org/pdf/2003.10118` and `https://msp.org/obs/2020/4-1/obs-v4-n1-p05-s.pdf`
appended to `urls_in_order` in a **successor** contract. Minutes.

---

## RT-4 (MEDIUM) — the 2^384 row uses an exponent the experiment measured and did not obtain

**Target.** `runs/RUN-ICINV-kf-decide/concrete-cost-table.json`
`modeled_cost_rows[PS-P256]` and `[PS-P384]`, `m_exponent_used: 1.0`;
`EV-ICINV-c68f13` OBS-11.

`PS-P256 = 2^384` and `PS-P384 = 2^576` are `d^{1/2} · d^{m_exp}` with
`m_exponent_used = 1.0`, justified as "MODELED ONLY under H1 (m ~ d ~ p)". But
`m_exponent` is precisely the quantity this experiment measured, and the measured
medians of `log m / log d` are `0.687, 0.615, 0.647, 0.802, 0.724, 0.723, 0.792`
across k12…k24 — hovering near 0.72 with no visible trend toward 1. The
`PS-TOY-24` row correctly uses the measured 0.792; the two cryptographic rows
silently switch to 1.0. At the measured exponent, `PS-P256` is `2^330`, not
`2^384` — a 54-bit swing in the headline, taken by substituting an asymptotic
assumption for the measurement, in a table whose stated purpose is to keep
measured and modeled bases unmixed (`no_row_mixes_bases: true`).

This is **not** a claim that 1.0 is wrong asymptotically — `log ord_d(a)/log d → 1`
slowly is the standard expectation and the o(1) at `d = 2^24` is plausibly ~0.2.
It is a claim that the row's basis is under-disclosed and its sensitivity
untested, which is AGENTS rule 7 (toy-scale data must not carry a
cryptographic-scale figure) applied to an exponent rather than to a conclusion.

Second, smaller point: the row reports memory equal to time (`2^384`
`F_p`-elements). No time–memory interpolation is stated. That is defensible only
because the row is not an attack cost — and that is exactly why a bare `2^384`
escapes its condition when quoted. The condition is stated in
`conditional_on`, in `EV-ICINV-c68f13` OBS-11, in `DEC-20260807-4261e3`
`limitations`, and in `KN-OPEN-2c095b` §Scope — thorough, and I checked each
path — but the *row itself* does not carry a `not_an_attack_cost: true` field,
and the number is the thing that travels.

**Cheapest test.** Add a sensitivity row at the measured exponent, and a
`not_an_attack_cost` flag, in the successor contract. Zero compute.

---

## RT-5 (MEDIUM) — CONFOUND-2 is settleable from the committed data, and the answer is more favourable than the record assumes

**Target.** `EV-ICINV-c68f13` CONFOUND-2 ("Whether this makes the nominal
threshold conservative or anti-conservative … is NOT settled by these data").

It is settled by these data, by comparing two samples drawn from the *same*
population: seed A's curve sample against seed B's curve sample. *[RT-probe]*,
all three pairs per decade, `ks_crit = 0.0607`:

| decade | KS(curve seed A, curve seed B) | KS(null A, null B) |
|---|---|---|
| k12 | 0.021, 0.024, 0.026 | 0.034, 0.051, 0.053 |
| k14 | 0.028, 0.033, 0.038 | 0.044, 0.045, 0.056 |
| k16 | 0.024, 0.026, 0.029 | 0.035, 0.038, 0.046 |
| k18 | 0.041, 0.053, 0.054 | 0.029, 0.041, 0.055 |
| k20 | 0.041, 0.055, **0.070** | 0.037, 0.060, **0.089** |
| k22 | 0.022, 0.031, 0.036 | 0.044, **0.060**, **0.060** |
| k24 | 0.030, 0.042, 0.043 | 0.031, 0.039, 0.042 |

Reading: the nominal 0.0607 is approximately calibrated at k12–k18 despite the
replicated-atom structure (same-population KS ≤ 0.054 there), and is **mildly
anti-conservative at k20–k22**, where identical populations reach 0.070–0.089.

Two effects, in opposite directions:

- It **supports** the record's own treatment of the dissenting seed 20260807:
  its k20 deficit of 0.081 and k22 deficit of 0.061 sit inside the
  same-population spread at those decades. The "below the resolvable floor"
  reasoning survives, now with a measured basis rather than an assumption.
- It **does not** undercut the k14 cells the anomaly rests on: same-population
  KS there is ≤ 0.038, against an observed 0.104–0.121. The deficit at k14 is a
  genuine population difference. (RT-2 then says what population.)

**Correction needed.** CONFOUND-2 should be superseded by a measured statement
with these figures, and the record's own significance calls at k20/k22 marked as
inside the empirical same-population band. This is a place where the record is
*more* pessimistic than the data require.

**Cheapest test.** Already run — seed-vs-seed KS on the committed tables, seconds.

---

## RT-6 (MEDIUM) — the barrier audit's coverage is being described in a way that invites both misreadings

**Target.** `EV-ICINV-c68f13` OBS-9; `DEC-20260807-4261e3` rationale "AUDIT-Z IS
NOT CONFIRMED"; the handoff's question 3.

The record does not read `OUTCOME_AUDIT_PARTIAL` as "nothing to see" — it says
explicitly that a partial audit may not be reported as a confirmation, and
states the narrow version ("among the 50 rows the audit could classify, none
changes its exponent"). I checked the apparent arithmetic gap: the table holds
175 rows plus 2 `required_rows`, `row_count: 177`, `48 + 2 = 50` classified. It
reconciles; there is no discrepancy.

The objection is different. "127 undetermined out of 177" reads as an instrument
that mostly could not decide, on 127 separate grounds. It is not. All 127 carry
one identical reason string, keyed to a single blocking gate that RT-3 shows is
retrievable. And the 48 determined rows are determined by a STAGE-0-independent
argument (`R1-counts-evaluations`: the quoted figure counts isogeny evaluations,
so a correction inside one evaluation cannot move it), so they are robust in
*both* branches of the gate. The honest phrasing is: *48 rows are settled
unconditionally; 127 are pending one retrievable fact; 0 change their exponent
in either group so far.* As written, the record understates how close AUDIT-Z is
to being dischargeable — which, under the program's own symmetry between
premature closure and overclaiming, is the mirror-image error to the one it is
carefully avoiding.

**Cheapest test.** N4 (RT-3), then re-run STAGE 1 unchanged.

---

## RT-7 (LOW-MEDIUM) — OBS-8 leads with the weaker of two arguments, and names one small-`m` family where the tail contains two

**Target.** `EV-ICINV-c68f13` OBS-8; `DEC-20260807-4261e3` rationale "A SMALL-m
FAMILY WAS FOUND"; `KN-OPEN-2c095b` §"Related" first bullet.

**On the dismissal.** The `|t| ≤ 2` characterisation is correct — I confirm from
the derivation that `|t| ≤ 2` forces `λ ∈ {±1}` and `m ≤ 2`. But the record
leads with the density argument (`O(1/√p) → 0`), which is an asymptotic claim
that seven decades below `2^24` cannot see, exactly the objection the handoff
raises. The *sufficient* argument is already on the record and is unconditional
on density: mechanism STEP 4 / `H-ENDO-001` makes the endomorphism act as a
scalar on the prime-order subgroup, so the family is not an attack **at any
density**. The dismissal is therefore **safe**, but it is safe for the second
reason, not the first, and the record orders them the wrong way round. If the
density argument ever fails, nothing changes; if STEP 4 ever fails, the density
argument would not have saved it. Lead with STEP 4 and demote density to
secondary.

**On the characterisation.** OBS-8 says "the family is: ordinary `E/F_p` with
`|t| ≤ 2`". The small-`m` tail contains a **second, distinct** population that
OBS-8 does not name: the large-conductor branch where `d ≪ √p`. Example from the
committed table *[RT-probe, `RUN-ICINV-kf-stage3-k12`, seeds 20260807 and
20260814]*: `p = 4093, t = 127, u = 63, v = -1, d = 61, λ ≡ 2 (mod 61), m = 60`.
Here `d`, not `m`, is what is small; `|λ| ≤ √p + 1` is satisfied only in the
signed-lift sense and the stored residue is not the signed representative. These
rows are also the only ones on which the identity of RT-2 needs its
`mod d` caveat. Calling the `|t| ≤ 2` set "the" small-`m` family, without naming
the small-`d` set beside it, is an incomplete characterisation of a deliverable
the decision explicitly hands forward.

**Cheapest test.** Stratify the small-`m`/small-`d` tail by `d/p` and by
conductor bin — one pass over the archived `per-instance-measurements.json`,
seconds, no new runs.

---

## RT-8 (LOW) — CONFOUND-4 (the k = 5 minimiser window) and D1

**CONFOUND-4.** The concern is real but bounded and testable from the committed
data: `degree_window` carries all five admissible `α` per instance with their
`log_m_over_log_d`, and `window_spread_log_m_over_log_d` is recorded per
instance (0.084 and 0.198 in the two k24 rows I read). Whether the
smallest-degree choice biases the statistic can be answered by recomputing the
primary statistic at ranks 1–4 of the same window and comparing. Zero new runs.
The record correctly declines to claim it is tested; it should note that it is
*cheaply* testable rather than leaving it as a standing confound.

**D1 (13 runs against a frozen cap of 12).** The disposition is correct and I
endorse it. Invalidating `RUN-ICINV-kf-decide` would destroy the artifact SR7
exists to produce and hand terminal-state selection back to a human after the
data were seen. Refusing to file a retroactive amendment is the right call. No
objection.

---

## Baseline comparison

`sota_delta: 0.0` against `0.886·√N` (KN-TECH-001, -006, -018, -031) is correct
and I found no path by which it could be otherwise. This experiment evaluates no
isogeny, implements no square-root Vélu, computes no discrete logarithm, and
recovers no source or target. `certificate.kind: none` with `verifier: no-claim`
is right, not a gap. Pollard-rho and BSGS are untouched. The only quantitative
movement ever claimed is **upward**, in a cost figure, against the lane's own
interest — and RT-3 shows the source itself already states that the
square-root-Vélu speedup does not survive an irrational kernel generator.

`dominated_by` is populated (Pollard rho with distinguished points, BSGS) rather
than `null`, and there is no eliminated search dimension whose own cost went
uncharged — on the contrary, `hidden_overhead` explicitly charges the
subexponential factorisation of `d ~ p` that the audit pays and an attacker
never would, which is the `KN-LIT-7593` discipline applied correctly and against
the lane's interest.

`affected_vs_safe_scope` lists **no** affected constructions and gives a reason
for each "safe" entry that is a *different* dominating argument (STEP 4 scalar
action for prime-field ECDLP; `m = O(1)` for CSIDH-style action steps), not
"never considered". **No scope inflation found.**

---

## What I checked that came back clean

- **Run-set integrity.** 13 run directories, matching tally, `all_pinned: true`
  with per-file sha256, memory reconciliation in band in all 13, resource use
  three orders of magnitude under caps.
- **Raw-vs-summary.** I recomputed `log m / log d` medians directly from
  `per-instance-measurements.json` and reproduced the reported decade medians and
  KS statistics, including k14 seed 20260807 `D = 0.121`. The Coordinator record
  disclosed that it had no Bash tool and could only compare two written
  artifacts; that check now exists.
- **Barrier table arithmetic.** `row_count: 177` = 175 rows + 2 `required_rows`;
  `48 + 2 = 50` classified, 127 undetermined, 0 changed. Reconciles.
- **The derivational flag.** `proof_status_note` correctly separates
  `λ = ±round(t/2)` as *derivational, confirmed against but not established by*
  the table. That distinction is exactly right and is the reason RT-2 was
  findable at all.
- **D4** (T5 artifact gap): the substance is present in all 13 manifests'
  `memory_reconciliation`; refusing a corrective run to copy verified numbers
  into a second file is the right call.
- **Claim tier `toy`**, strength `preliminary` computed from the frozen
  calibration rather than chosen, dissenting seed named, `independently_reviewed:
  false` and CONFOUND-6 recorded on the face of both records rather than
  omitted. The records disclose their own worst facts. That is not common and it
  should be said.
- **No fabrication found.** Every number I spot-checked against the artifacts
  matched.

---

## Narrowest supported statement

Over the tested instances, parameters, solver and budget: the distribution of
`log m / log d` for the `Z[π]`-minimal non-scalar endomorphism's eigenvalue
shows a deficit against a uniform-unit null matched on `d` at the smaller
decades; that deficit is **not** explained by the smallness of `λ`, and is
**reproduced by a curve-free family** `(λ', d' = p - λ'²)` of the same shape.
Nothing in this run set is evidence about CM structure of elliptic curves beyond
the class-number weighting on `t`, which remains untested. The square-root Vélu
operation count's field of statement is answerable from a retrievable source
whose §4.14 already asserts the campaign's own heuristic. No attack, no speedup,
`sota_delta` 0.0, claim tier `toy`.

---

## Next concrete action (one)

**Run N4 first, against `https://arxiv.org/pdf/2003.10118` (sha256 above) and
`https://msp.org/obs/2020/4-1/obs-v4-n1-p05-s.pdf`, under a successor contract
with a new run id and the contract's unchanged byte-verification path.** It is
minutes of work, it discharges the gate that makes 127 of 177 barrier rows
undetermined, and — because §4.14 states the campaign's own heuristic and its own
negative conclusion — it changes what the replication should ask before that
replication is designed. N3 should be rewritten only after N4 returns, as the
three-arm design of RT-2 (curve / curve-free / uniform-unit), pre-registered on
`KS(curve, curve-free)`, with the small-integer arm demoted to a
already-answered control and the "other square root" arm excluded as degenerate.

```yaml
artifact_paths:
  - experiments/EXP-ICINV-fcb497/red-team-report.md
objections: [RT-1, RT-2, RT-3, RT-4, RT-5, RT-6, RT-7, RT-8]
required_controls:
  - curve-free null (λ' uniform in Hasse window, d' = p - λ'²) as PRIMARY null
  - small-integer null (already run here; answered, keep as a recorded control)
  - EXCLUDE the "other square root of λ² mod d" arm as degenerate by construction
  - seed-vs-seed same-population KS as the calibration reference, per decade
  - rank-1..4 window recomputation for CONFOUND-4
counterexample_or_mutation: >-
  Mutation: delete the elliptic curve. λ' uniform in [2, √p], d' = p - λ'².
  The deficit survives at every decade. The reported signal does not survive
  its null object.
narrowest_supported_statement: see above
```
