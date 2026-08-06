# Red team notes — TASK-20260803-f42495

**Supersedes TASK-20260803-95d8be** (died on a provider session limit). I did not
open the `rt_checks.py` it left behind; I listed the directory and read only its
`infra_failure_receipt.yaml`. Everything here is re-derived.

Requested policy `review-adversarial` / `xhigh` / independent session; resolved
`claude-opus-5`; `fallback_used: true`; `model_verified: false`. Not a rule-12
`review-breakthrough` pass, and rule 12 remains UNMET and UNWAIVED.

Verdict: **pass_with_constraints**. Twelve numbered objections in `report.yaml`.

---

## 1. The two facts the Coordinator note told me to verify

Verified in the pinned clone at `/tmp/le`, HEAD = `3e48ef421ec2…`, worktree
clean, `estimator/lwe_dual.py` sha256 `8f6a0775…a8b` matching the pinned blob
byte for byte (29 728 bytes).

**Fact 1 — confirmed.** `class MATZOV` opens at line 496, `Nf` at 526, `mu = 0.5`
at 539, and the sample-count expression at 552–556. `N` is a closed form; nothing
in it models dependence between score contributions. The note's quotation is
faithful.

**Fact 2 — confirmed as a grep, and the grep is stronger than the note said:**
zero occurrences of `Pwrong`, `false_pos`, `fpfn`, `Phi_inv` in lines 496–700, in
the whole file, and in the entire `estimator/` package.

**But the note over-reads its own grep.** It writes "There is no false-positive
cost anywhere in the class … and here not even the analytic term appears." That
is wrong. Line 555 is

```python
* (k_enum * cls.Hf(params.Xs) + k_fft * log(p) + log(1 / mu))
```

That bracket is the log of the number of candidate hypotheses being scored —
`2^{k_enum·H}` enumerated guesses × `p^{k_fft}` FFT bins — plus `log(1/mu)`. It
multiplies `N`, i.e. it inflates the required sample count so that the best wrong
candidate stays below the right one. That *is* the analytic false-positive
handling, and it is exactly where the independence assumption earns its keep. The
absence of a `Pwrong` identifier is a fact about naming.

The note's reason 1 is sound and sufficient on its own. Reason 2, as written, is
not, and a downstream record repeating it will be repeating an error that the
next person to read the source will find.

## 2. Going past the note: `mu = 0.5` is not the load-bearing thing

The note leads with `mu = 0.5` as the visible symptom. I subclassed `MATZOV`,
rescaling `N` by the exact bracket ratio for a new `mu` (so I never transcribed
the hard `exp()` factors), checked the subclass reproduces the pinned optimum at
**delta exactly 0.000e+00** on all three sets, and swept with full
re-optimisation inside `RC.MATZOV`:

| mu | K512 | K768 | K1024 |
|---|---|---|---|
| 2^-10 | +0.109951 | +0.000000 | +0.000000 |
| 2^-40 | +0.109952 | +0.000000 | +0.000000 |
| 2^-128 | +0.267033 | +0.000001 | +0.000000 |

Tightening the target advantage by **128 bits** costs the attacker at most a
quarter of a bit. The structural reason is checkable without compute:
`log(1/0.5) = 0.693` sits inside a bracket dominated by `k_fft·log p`
(≈80.5 / 83.2 / 166.4 nats), and on Kyber-768/1024 the required `N` sits *below*
the sieve's free output (`log2 N` = 119.7530 / 165.9385 vs `0.2075·β_sieve` =
120.9725 / 166.8300), so small inflations cost literally nothing.

This matters operationally. The producer's own remediation plan (`gap_report`
§8.2, H17) proposes spending a Coordinator cost-model amendment to "expose mu…
the largest nameable remaining term." It is worth 0.27 bits. The load-bearing
objects are `exp(4·(lsigma_s·π/q)²)` at line 553 and the union bracket at 555.

## 3. (a) Does the internal finding survive? No — not as the note states it.

The note's claim is that ANOM-3 "stands or falls on the function identity alone."
I reproduced ANOM-3 exactly (primal_bdd 140.199473 / 200.958715 / 270.723623;
matzov 139.656041 / 196.366243 / 262.335680; margins **+0.543432 / +4.592472 /
+8.387943**) and then attacked the survival argument three ways.

**(i) "The estimator's own frame" is not one frame.** `primal_bdd` is costed from
a BKZ simulation plus one SVP call at η+1. `matzov` is costed from an explicitly
*truncated* asymptotic — the estimator's authors wrote the disclaimer themselves
at `lwe_dual.py:551`, `# p.29, we're ignoring O()`. Comparing a cost that drops an
O() factor against one that does not is not a within-frame comparison, and the
Kyber-512 margin of **0.543432 bits is smaller than a single dropped factor of
2**. The note's own asymmetry is the point: `primal_bdd` does not rest on the
disputed law, `matzov` does. Sharing a discredited assumption contaminates the
*comparison* precisely because only one side carries it. If matzov is cheap
because it assumes something contested, "dual beats primal" is a property of the
assumption.

**(ii) The batch's own diagnostic convicts ANOM-3.** The card and `gap_report` §4
both rest on: *a gap that grows with β is a systematic modelling difference, not
noise.* ANOM-3's gap grows monotonically with β:

| | K512 | K768 | K1024 |
|---|---|---|---|
| ANOM-3 margin/β (β = 387/589/823) | 0.0014042 | 0.0077971 | 0.0101919 |
| scouting gap/β, the one it convicted | 0.01067 | 0.01411 | 0.01632 |

Same monotone shape. The batch applied its diagnostic to the finding that
embarrassed the scouting and did not apply it to the finding that flatters the
campaign. That asymmetry is the objection; I am not asserting the diagnostic
proves ANOM-3 is an artifact, only that the batch owes it the same test it
demanded elsewhere.

**(iii) The decay test — what should destroy it, and does it?** The parameter
that is supposed to destroy this signal is inflation of the required sample count,
which is the direction the Ducas–Pulles objection acts. I inflated `Nf`'s output
by 2^δ with full re-optimisation:

| | N×2^0 | ×2^1 | ×2^2 | ×2^4 | ×2^8 | ×2^16 | δ_flip |
|---|---|---|---|---|---|---|---|
| K512 | +0.543432 | +0.276399 | +0.076049 | −0.331512 | — | — | **≈ 2.3732** |
| K768 | +4.592472 | +4.592470 | +4.305263 | +3.884454 | +3.024729 | +0.728911 | > 16 |
| K1024 | +8.387943 | +8.187715 | +8.163606 | +7.688228 | +6.923698 | +5.233394 | > 16 |

So the honest answer is **per parameter set**, and the note's global "it survives"
is wrong at Kyber-512 and defensible at Kyber-768/1024. At Kyber-512, understating
the sample count by a factor of 5.2 erases ANOM-3 — well inside the uncertainty
the Ducas–Pulles objection opens. At Kyber-768/1024 the quantity *does* decay
under the parameter meant to destroy it, which under inventor-protocol §3 is a
point **in the finding's favour**. I record that in the direction it falls.

I do not know Ducas–Pulles's repaired constant and did not invent one. This is a
sensitivity, not a correction.

## 4. (b) The temptation, attacked on its own terms

**Free-memory gate counts, and a discarded number.** The migration from
`dual_hybrid(fft=True)` to `matzov` silently threw away the only memory figure
the instrument supplied on the dual side, and nobody noticed:

```
primal_bdd      keys: beta, d, eta, problem, red, rop, svp, tag
matzov          keys: N, beta, beta_, guess, m, p, problem, red, rop, t, zeta
dual_hybrid+fft keys: beta, d, m, MEM, problem, REPETITIONS, rop, t, tag, zeta
```

`dual_hybrid(fft=True)` reports `mem` = 2^92.699292 / 2^135.198091 / 2^184.641891.
`matzov` reports none. `primal_bdd` reports none. ANOM-3 compares two attacks in a
convention where memory is free *and unreported*, having replaced the one attack
that at least printed a number.

Reconstructing matzov's memory the way EV-MLKEM-020 reconstructed primal's — FFT
table `p^{k_fft}` cells (an *inference* from `T_fftf`'s `p**(k+1)` at line 513,
labelled as such, not a quotation from MATZOV-2022), sampling sieve ≈ N vectors —
gives peak **2^116.0964 / 2^131.4803 / 2^240.0000** Z_q-equivalent against
primal's **2^88.494071 / 2^131.657286 / 2^180.924993**. My reconstruction
reproduces EV-MLKEM-020's primal figures to |Δ| < 4.0e-07, so the recipe is
theirs and it is calibrated; a self-consistency check also holds on all three
sets (`log2 N` 81.0788/119.7530/165.9385 vs `0.2075·β_sieve`
81.1325/120.9725/166.8300 — the sieve produces just enough).

Two consequences, and they do not both go the same way:

- **The ordering flips at c_flip = 0.019688 at Kyber-512** — *below*
  EV-MLKEM-020's own primal c\* of 0.03164649, and 17× below the 3D-mesh
  convention 1/3 — and 0.141988 at Kyber-1024. At Kyber-768 matzov uses 0.1770
  bits *less* memory, so charging there widens the margin and there is no flip.
- **Against the cutoffs**, matzov's own c\* is 0.028803 / 0.080877 / 0.040268
  versus primal's 0.031646 / 0.045886 / 0.007055. So matzov's undercut is *more*
  memory-robust than primal's at 768/1024 and slightly less at 512. Every one is
  still one to two orders below 1/3, so ANOM-3 does not rescue the security
  reading — but saying it is uniformly more fragile would be as dishonest as the
  overclaim, and I am not saying it.

And a blunt one: at Kyber-1024 the reconstructed FFT table is **2^240 cells**
against a claimed total cost of 2^262.34. A cost model that charges nothing for
2^240 cells of storage is not costing an algorithm anyone could run.

**The NIST floors are a convention, and an unread one.** 143/207/272 come from a
parenthetical in Carrier's abstract and a column of MATZOV's Table 1. No primary
FIPS 203 or NIST text is readable here (producer H8, EV-MLKEM-020 H11,
EV-MLKEM-015's boundaries all say so). The convention itself is a deliberately
conservative floor *for the defender* — EV-MLKEM-020 OBJ-10 established this and
cited Wiener's own statement that counting only processor steps is conservative
for the cryptographer. Sitting 3.34/10.63/9.66 bits under a conservative floor, in
a model that charges nothing for 2^240 cells, against numbers nobody here has
read, is a statement about a convention.

*(I have a vague impression that NIST's categories are defined relative to
AES/SHA key search rather than as hard gate thresholds. That is recollection, not
evidence, it is not sourced here, and no record may cite it.)*

**Is matzov just an aggressive parameterisation?** Not in the sense of the
producer tuning it: ANOM-3's headline uses S1, the estimator's own default call,
and both sides are optimised inside their own frames. The aggression is in the
*cost function*, not the tuning: `matzov` prices one pass at advantage 0.5 with no
repetition and an admitted dropped O(), while its own siblings `dual` and
`dual_hybrid` take `success_probability = 0.99` and report `repetitions`. Neither
`matzov` nor `primal_bdd` exposes a success probability at all, so **the
instrument provides no way to normalise the two attacks to a common success
event**. That is an unnumbered assumption under the package's own standard.

## 5. (c) EV-MLKEM-015: right about what it named

`experiments/EXP-MLKEM-015/implementation/reproduce_estimates.py:16` reads
`from estimator.lwe_dual import dual_hybrid`, and line 43 calls it with
`fft=fft`. So the record imported the module-level function directly and never
touched the public alias. Its 143.79 / 203.79 / 273.82 are **exactly right for the
callable it ran** (I reproduce the first two at Δ ≤ 3.13e-13).

What fails is the `inference` field: "any dual claim that undercuts these
dual_hybrid+fft numbers … must justify ingredients beyond **the public MATZOV
dual in lattice-estimator**." That sentence identifies the callable it ran with
the public MATZOV dual, and `estimator/lwe.py:13`
(`from .lwe_dual import matzov as dual_hybrid`) says they are different objects,
4.132437 / 7.421620 / 11.481588 bits apart. The same conflation appears in the
boundary line "lattice-estimator matzov dual ≠ Carrier polar-code repair."

The defect is older and wider than one record:
`experiments/EXP-MLKEM-015/specification.yaml:45` enumerates
`attack ∈ {primal_usvp, primal_bdd, dual_hybrid}` — the experiment **contract**
never enumerated the estimator's MATZOV implementation. It passed a validator and
a red team in BATCH-001 and was reused through BATCH-010; EV-MLKEM-020's
VAL-CTRL-A quotes "dual_hybrid 145.528285", a third distinct number, so the
BATCH-010 validator inherited the same binding.

**What a record should say when a public API name and its function diverge.**
Record the fully-qualified callable actually imported, its defining locus, and the
pin — never the alias alone. "`estimator.lwe_dual.dual_hybrid` (module-level
function over `class DualHybrid`, `lwe_dual.py:25`/`:742`) with `fft=True`, at pin
3e48ef4." Where an alias *is* used, record the alias **and** its resolution and
the binding line: "`LWE.dual_hybrid` → `estimator.lwe_dual.matzov`, bound at
`estimator/lwe.py:13`." A cost figure without a resolved callable and a pin is not
reproducible; it is a number with a nickname.

Procedure: rule 4 makes the fix a *superseding* record, never an edit. Rule 12 —
unmet, unwaived — makes ANOM-3 unable to correct it. This report performs no
correction and authorises none.

## 6. (d) The Coordinator's error, and the note written while I was down

**The card.** It states the gap as fact ("Coordinator scouting found it is
SUPERLINEAR in beta"), poses a two-branch question, and instructs "decompose the
gap into named, individually-sized modelling differences." That presupposes the
gap *is* made of modelling differences. There is no step "first verify the two
sides name the same attack." The consequence is legible in the deliverable: the
wrong-callable finding arrives as `D1_attack_function_identity`, a row in a table
of *named modelling differences* — a container that reads as a finding about the
estimator rather than about the comparison. The card's binary also omitted the
branch that actually obtained; the producer supplied it itself (§6, "supports
neither branch of the question as posed"). To the producer's credit, D1 is in the
one-paragraph headline at 96.4/85.4/81.3 %, and §9 flags the stale card. That is
rule-9 compliance under a card that made it awkward.

**Would a different card have found ANOM-3 sooner?** Yes, and much sooner. ANOM-3
is one call to `lwe_dual.matzov`: 14.1 s for Kyber-512, 48.6 s for all three on
this machine. Any card in BATCH-001 through BATCH-010 saying "tabulate every
attack this harness actually serves, at all three sets, under RC.MATZOV" would
have produced it. EV-MLKEM-020's own `scope_statement` records that the served
attack set was narrower than claimed and that `dual` and `primal_hybrid` fail: the
campaign spent ten batches auditing what does *not* run and never once enumerated
what does.

**The note.** It does a great deal right — labelled NOT EVIDENCE, dated,
attributed, scoped to a named snapshot, committed durably (`0cf03c06`,
15:43:18 UTC, ahead of the successor task at `6876940e`, 15:45:12), forbidding
citation as validation, every factual claim at a checkable locus. Far better than
leaving the reading undocumented overnight.

It also does three things a Coordinator input to a review should not: it answers
the reviewer's designated lead objection; it directs the reviewer's budget on that
question ("the retry should not spend its budget re-deriving it"); and it
pre-announces the **split** — "Dissolved" / "Survives" — which is the interpretive
verdict `agents/red-team.md` assigns to the red team as
`narrowest_supported_statement`. It is written by the role whose scouting error is
under review, about the significance of the finding that error produced.
AGENTS.md's model-policy section requires "a reviewer that did not originate the
claim"; the note does not breach that literally, but supplying the reviewer's
conclusion in advance produces exactly the correlation the requirement exists to
prevent. The right form was a *question* in the card — "verify whether `Nf` models
dependence between score contributions, and state what follows."

Net: it **informed** rather than controlled this review — but only because I
ignored the budget instruction and re-derived both facts. Had I complied, OBJ-1
and OBJ-2 would both have propagated into EV-MLKEM-021.

## 7. (e) Negative residuals: honest, and diagnosed too kindly

The producer states the over-attribution plainly (`fraction_attributed` =
1.112888 / 1.070009 / 0.978413 in `results.json`; §4 "This **over-attributes** …
Stated rather than suppressed") and concludes "the true attribution lies between
the two rows." That is a bracketing story. The real defect is a category error.

D2/D3/D4 are **not** differences between the estimator and the publication. They
are measurements of the estimator's own *optimiser slack* — grid resolution,
unoptimised `m`, unpassed `β_sieve` — applied to **one side only**, with no
matching relaxation of Carrier's fixed published number. Only D1 is of the type
the card asked for. Summing them into a column headed "total attributed" and
comparing it to a gap is what makes the parts exceed the whole.

Two consequences the report does not draw:

1. "The residual brackets zero and does not scale" is **not** corroboration. A
   one-sided relaxation started above a target will cross it, for *any* target it
   started above. The crossing carries no information about Carrier.
2. H9's own `cost_to_the_conclusion` says the boxes are local and a global
   re-optimum would be lower still. So a wider search makes S4 strictly cheaper
   than Carrier on all three sets, and "the pinned public estimator reproduces
   Carrier's published headline" degrades into "the estimator undercuts Carrier by
   an amount bounded only by the search box." The agreement is a property of the
   box.

And the precision is unearned: the D1-only row (+0.156041 / +1.266243 /
+2.635680) is quoted to six decimals while H17's unmapped `log2(R)` =
9.39 / 9.49 / 15.15 sits in the source's own Table C.2. One decimal place.

## 8. (f) Were the rejected explanations dismissed to protect D1?

**No, and I say so plainly.**

- **Core-SVP vs gates** — correctly rejected. 24.15/22.04/20.58 bits against a
  4.29/8.69/14.12 gap, and its parameter-scaling has the **wrong sign** (it
  shrinks while the gap grows). Units quoted from archived bytes on both sides.
- **Sieve cost model** — correctly rejected and independently corroborated.
  GJ21−MATZOV = 5.5551/6.5465/6.2462 reproduces MATZOV's own "≈6 bits in rank
  400", and it is roughly **flat** in β, so it cannot be the growth term.
- **Dimensions-for-free** — the one whose stated justification is weak. Its
  magnitude (7.9984/10.3055/12.9912) *and* growth shape both match the gap, so it
  is D1's direct competitor, and the evidence that Carrier applies it identically
  is a paraphrase plus "Table C.1 prints two block-size columns" — an inference,
  where the sieve-model cancellation had a quotation. **But I checked the archive
  and the conclusion survives on better grounds than the report gives.** From
  `…/extracts/carrier-hal-05406481/page37_tables_C1_C2.txt`, Carrier CC
  (β_bkz, β_sieve, log2 N) = (384, 387, 80.31) / (581, 574, 119.12) /
  (811, 792, 164.35), against the estimator's matzov S1 (387, 391, 81.0788) /
  (589, 583, 119.7530) / (823, 804, 165.9385). A d4f convention differing by the
  8–13 bits at stake could not leave two independent optimisers within 2–12 on
  every block size and within 0.63–1.59 bits on log2 N. The report's reason is
  thin; the conclusion is right for a reason it has the data for and does not use.

One caveat on that same agreement: the report calls the parameter convergence
"the strongest non-numerical corroboration available." It corroborates
**implementation fidelity** — which is a genuine partial answer to the note's own
open question 2 — and it does **not** corroborate model soundness. Two
near-identical cost models landing on near-identical optima is expected.

## 9. (g) The cheapest single check that falsifies the headline

**Get a Sage-computed reference for `estimator.lwe_dual.matzov` at Kyber-768 and
Kyber-1024 under `RC.MATZOV` at pin `3e48ef4`,** and compare against
196.3662433540 and 262.3356800075. Install Sage and run
`LWE.estimate(schemes.Kyber768)` / `Kyber1024`, or just run the estimator's own
doctest suite at the pin.

Why this and nothing else: every load-bearing number in the batch other than
Kyber-512 flows through the `.n(30)` rebinding on a path with **no known-answer
coverage**. The harness control covers `primal_bdd` and `dual_hybrid(fft=True)`
only. The producer's Sage cover for `matzov` (H5/CTRL-3) is Kyber-512 only, from
the estimator's committed doctest, and my own independent CTRL-RT-2 is likewise
Kyber-512 only. The two uncovered numbers carry ANOM-3's 4.59 and 8.39 bit
margins, D1's 7.42 and 11.48, the 1.27 and 2.64 bit Carrier residuals, and every
"below the cutoff" sentence for 768 and 1024. One disagreement falsifies the
headline, ANOM-3 and the Carrier agreement simultaneously, and nothing else in the
package survives independently of it. It is the producer's own §8.1, it costs one
Sage install and minutes of compute, and it is the only check here that can fail
catastrophically rather than incrementally.

Runner-up, if Sage is unavailable: re-run stages 2–4 with the search boxes doubled
(~60 s). If S4 keeps falling, §4's "independent convergence" corroboration is a
property of a local search.

## 10. What I am not saying

No ML-KEM break. No security proof. No FIPS 203 parameter set affected or cleared.
No status change to EV-MLKEM-015 or any other record; rule 12 is UNMET and
UNWAIVED and ANOM-3 stays gated. KN-OPEN-016 remains open and untouched by this
batch — it asks what the dual attack costs *after* the heuristics are repaired,
and this batch measured the cost *before* repair, inside an implementation of the
unrepaired law. My §3(iii) sensitivity is the closest anything here comes to that
question, and it is a sensitivity, not a repair.

Finally, the credit, because it is deserved and the objections above should not
be read as a demolition: I found no fabrication, no scope inflation, no
unreproduced number, and no suppressed inconvenient result in the producer's
package. It ran its control first, numbered eighteen heuristics with falsifiers,
disclosed its own over-attribution, its own stale task card, and a mid-task HEAD
move, refused "best attack" phrasing, and declined to assert the one thing it
would have been most tempting to assert. My twelve objections are against the
interpretation being built on it, the sizing method, and the process — not against
its integrity.
