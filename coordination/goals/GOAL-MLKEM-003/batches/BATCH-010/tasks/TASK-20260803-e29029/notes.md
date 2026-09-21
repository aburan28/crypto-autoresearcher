# Red team, TASK-20260803-e29029 — the argued case

**Target** the derivation snapshot-committed as `7afc38466bb697ac309a89a49e92f396393a5e73`
under `coordination/goals/GOAL-MLKEM-003/batches/BATCH-010/tasks/TASK-20260803-648a0b/`.
**Role** Red Team, independent session. I did not produce this package and have not repaired it.
**Verdict** `pass_with_constraints`.

> No ML-KEM break is claimed or implied here. Nothing in this report is a security
> proof either: a memory charge that raises an estimated attack cost above a NIST
> cutoff is a statement about one cost model at one parameter set under stated
> heuristics. AGENTS.md rule 12 is UNMET and UNWAIVED. Nothing here changes or
> treats as corrected EV-MLKEM-011, EV-MLKEM-013, EV-MLKEM-017, KN-FIND-012 or
> KN-FIND-014.

---

## 0. What I ran, and what it settled

One run, as budgeted. `/tmp/claude-0/-home-user-crypto-autoresearcher/5cc33d08-b894-5d89-8a26-7f062c61725d/scratchpad/rt_e29029_probe.py`
(sha256 `7ddaeafd14d6a2cb09caef679fb75eb49e70675452b4b8f2126d77669bbe400c`;
stdout `…/rt_e29029_probe.out`, sha256 `181c1c74af63df150cd12aae5cfcaf23dea91d185e4af996c4f0f70f793f02c4`;
wall 25.9 s; Python 3.11.15, mpmath 1.3.0, scipy 1.17.1).

Step 0 was the known-answer control, re-run by me rather than quoted:

```
$ PYTHONPATH=/home/user/crypto-autoresearcher/tools/sage_free_estimator/shim:/tmp/le \
  /usr/local/bin/python3 /home/user/crypto-autoresearcher/tools/sage_free_estimator/known_answer_control.py
set             log2(rop)          reference      delta  beta   eta      d
Kyber512   140.1994731076     140.1994731076   0.00e+00   389   422   1005
Kyber768   200.9587149141     200.9587149141   0.00e+00   606   640   1420
Kyber1024  270.7236234535     (no reference)         --   855   889   1867

PASS: every reference value reproduced exactly (delta 0.0) against lattice-estimator 3e48ef421ec2.
[control exit code: 0]
git -C /tmp/le rev-parse HEAD -> 3e48ef421ec256afddb3e7d2249a77eab6e9ba12  (pin match: True)
```

**Every headline number in the package reproduced.** β/η/d, the two sieve
dimensions, log2 M in vectors / Z_q / packed bits, the free-memory margins,
c\*, the c = 1/3 margins, the 10.5× / 7.3× / 47.2× ratios, the 6.97× / 65.86× /
2.42× multipliers, and the H9 sensitivity rows all came out identical on an
independent re-derivation. One reported quantity did not (§4.6). So this report
is not about arithmetic. It is about what the arithmetic is being asked to mean.

---

## 1. (a) Is c\* a finding or an inevitability?

### 1.1 The strongest case that it is an inevitability

`c* = margin / log2 M`. Both inputs pre-date the batch. The numerator is
EV-MLKEM-015's number, re-pinned by CTRL-2 at delta 0.0 and deliberately not
revised (H1). The denominator is `0.2075·n_peak + log2 n_peak` — one literal and
one logarithm.

Sweeping each input separately (probe RT-A) shows what c\* carries:

*Hold log2 M at the Kyber-512 value, sweep the margin.*

| margin (bits) | c\* | (1/3)/c\* |
|---:|---:|---:|
| 0.50 | 0.005650 | 59.0× |
| 1.00 | 0.011300 | 29.5× |
| **2.8005** | **0.031646** | **10.53×** |
| 6.00 | 0.067801 | 4.92× |
| 12.00 | 0.135602 | 2.46× |
| **29.498** | **0.333333** | **1.00×** |

c\* is *exactly* linear in the margin. The headline "c\* is 10.5× below 1/3" is,
term for term, the sentence **"the Kyber-512 free-memory margin is 10.5× smaller
than 29.498 bits."** The 47.2× for Kyber-1024 is large not because Kyber-1024 is
robust but because its undercut is small; the statistic moves *inversely* with
the very quantity EV-MLKEM-015 was reporting, which is a presentation liable to
be read backwards.

*Hold the margin at 2.8005, sweep the peak sieve dimension.*

| n_peak | log2 M | c\* |
|---:|---:|---:|
| 100 | 27.39 | 0.102232 |
| 200 | 49.14 | 0.056986 |
| 385.08 | 88.49 | 0.031646 |
| 600 | 133.73 | 0.020942 |
| 825 | 180.88 | 0.015483 |

At any dimension a cryptographic sieve reaches, log2 M is O(100). Kyber's
parameters were selected to land within a few bits of a category boundary, so
the margin is O(1–10) by design. c\* = O(10⁻²) is therefore forced by the
*shape* of the problem, before any instrument runs.

The batch's two genuinely effortful inputs turn out not to be load-bearing on
the headline. Replacing the sourced 0.2075 with an arbitrary exponent (RT-B3):

| sieve exponent | log2 M | c\* | still < 1/3? |
|---:|---:|---:|:--|
| 0.05 | 27.84 | 0.100582 | yes |
| 0.10 | 47.10 | 0.059462 | yes |
| 0.2075 | 88.49 | 0.031646 | yes |
| 0.30 | 124.11 | 0.022564 | yes |
| 0.40 | 162.62 | 0.017221 | yes |

H4's three-way sourcing of 0.2075 and H2's sieve-dimension resolution (which
H2's own direction clause concedes moves c\* "by a few percent") could both have
been skipped and the headline would read the same. A result that is invariant to
its own most carefully-sourced input is not resting on that input.

### 1.2 The strongest case against my own objection

Three points cut the other way, and I hold them.

1. **Being an identity is not a defect.** A derived quantity is not devalued by
   being derived; the discriminant of a quadratic is an identity in its
   coefficients and is still the thing you look at. The question is whether the
   identity answers a question someone actually had. KN-OPEN-017 records, in the
   corpus, that **no source had computed the memory charge for sieving**, and
   asks where the accounting moves the ranking. The batch supplies one point of
   that answer on the primal side at cryptographic dimensions. That is the
   question, asked before the batch, answered by the batch.

2. **The robustness is the finding, not the number.** My own RT-B3 sweep, meant
   as an attack, is the strongest thing in the package: the inequality
   `c* ≪ 1/3` holds for *every* sieve-memory exponent in [0.05, 0.40], for
   *every* unit in the chain, under *both* charge models, and (per my RT-C, §4.8)
   under within-instrument re-optimisation. So the qualitative conclusion is
   independent of the one input the community actually disputes. That is worth
   recording. The package buries it: the derivation report leads with
   `c* = 0.03164649` to eight figures and the 10.5× ratio, and never states the
   invariance that makes the conclusion durable.

3. **The magnitude was not *entirely* determined in advance.** The H2 question —
   which dimension the cost model sieves in — was live, was flagged in the task
   card as capable of changing the answer, and was resolved from named source
   lines rather than assumed. It is worth 7–13 bits of log2 M, i.e. roughly 10%
   of c\*. Resolving a 10% uncertainty in a quantity whose order of magnitude was
   fixed a priori is legitimate, modest work.

### 1.3 My judgement

**The number c\* is an inevitability. The robustness of the inequality
`c* ≪ 1/3` to every input the batch could not source is the actual finding, and
it is modest.** The package should be restated to lead with the inequality and
its invariance, and to demote `c* = 0.03164649` to what it is: the free-memory
margin divided by a memory figure, reported to a precision the inputs do not
support (H11 already concedes a one-bit cutoff error moves Kyber-1024's c\* by
0.006, i.e. ~85% of its value; that concession is in §8 item 6 and contradicted
by every table that prints eight digits).

---

## 2. (b) The case FOR the free-memory convention

### 2.1 The convention is a deliberate floor, and the batch never says so

H6 establishes *that* c = 0 is the convention — the cutoffs are gate counts with
no memory term, quoted as such by KN-LIT-7617 and KN-LIT-110, and KN-OPEN-017
records that core-SVP's 2^{0.292b} "charges nothing for memory or its access
pattern." Everything H6 asserts is about the convention's **existence**.

Nowhere in `derivation_report.md` or `heuristics.yaml` is the convention's
**purpose** stated. The purpose is the whole of the objection: a free-memory
gate count is chosen as a *lower bound on attack cost* so that a security claim
does not become hostage to a hardware model. Charging memory always moves the
estimate in the defender's favour, which is precisely why a conservative
standard refuses to do it. KN-LIT-094's own corpus entry contains the sentence
that makes this point — Wiener "states explicitly that counting only processor
steps is a conservative choice for the cryptographer" — and the batch cites
KN-LIT-094 four times without quoting it.

The consequence is not that the batch is wrong. It is that a reader cannot tell,
from the package, whether the free-memory result was overturned or merely
*departed from*. Those are different acts and only one of them is a criticism.

### 2.2 Is "the undercut does not survive memory charging" a criticism of EV-MLKEM-015?

**No, and the package's own H6 proves it is not.** EV-MLKEM-015's undercut is
declared by H6 to be a c = 0 statement. A c > 0 computation cannot contradict a
c = 0 statement; it reports a different quantity. EV-MLKEM-015 never claimed the
undercut survives memory charging, so nothing in it is corrected, weakened, or
qualified by this batch.

The derivation report is careful about this in §7 ("does not survive any of the
memory charges **examined here**"). The snapshot commit message is not:

> "The EV-MLKEM-015 undercut of the NIST cutoffs survives only under literally
> free memory."

Two defects in one sentence, both checkable at `git log -1 7afc38466bb6`.
First, the undercut survives for **all c < c\***, an interval of positive
width, not only at the point c = 0; "literally free memory" collapses an
interval to a point. Second, and worse for a durable record, the sentence reads
as a verdict on EV-MLKEM-015 rather than as a report of a different convention.
Commit messages are immutable; this one will be read by every future agent that
runs `git log` on this path.

### 2.3 Where the batch *is* entitled to charge memory

KN-OPEN-016's own closing line — "any program document citing dual-attack
security figures must mark them contested" — and KN-OPEN-017's standing request
for a full-cost sieving model together make the memory-charged computation a
legitimate, requested piece of work. The batch is not smuggling in a convention;
it is answering a corpus question. My objection is confined to the framing.

---

## 3. (c) H9: is the access-frequency range defensible or conclusion-preserving?

Three separate problems, in increasing order of severity.

### 3.1 The sensitivity table is not independent evidence

H9's crossing condition and the c = 1/3 margin row are the same number. Solving
`(margin + log2(1/f))/log2 M = 1/3` for f gives
`log2 f* = margin − (1/3)·log2 M`, which is *by construction* the charged margin
at c = 1/3. My probe (RT-A3) confirms the two columns coincide exactly:

| set | margin at c = 1/3 | log2 f\* with c\*(f) = 1/3 |
|---|---:|---:|
| Kyber-512 | −26.6975 | −26.6975 |
| Kyber-768 | −37.8445 | −37.8445 |
| Kyber-1024 | −59.0320 | −59.0320 |

So §5's sensitivity table is §4's headline table re-expressed. Presenting it as a
separate robustness check overstates how much independent support the conclusion
has.

### 3.2 The grid hides the exact crossings; the exact crossings favour the batch

The table steps f in decades of 2^10 and the prose says "only near f = 2^−30 does
Kyber-512's c\* cross 1/3." The exact crossings — 2^−26.70 / 2^−37.84 / 2^−59.03,
readable straight off a table already printed — are not stated. This is a
presentation choice that makes the crossing look remote rather than stating where
it is. Ironically the exact numbers are *better* for the batch than the grid, in
the sense of being precise; the grid is simply less informative than free
information already in hand. Cheap fix, no new computation.

### 3.3 The f-model is the wrong shape, and at c = 0 it contradicts CTRL-2

H9 writes the charged cost as `f · T · M^c`. Set c = 0 and the model returns
`log2 f + log2 T`, i.e. **a cost below the estimator's own free-memory gate
count**, which CTRL-2 pins at delta 0.0 (probe RT-A4):

| set | f | package model, log2 cost at c = 0 | CTRL-2-pinned |
|---|---:|---:|---:|
| Kyber-512 | 2^−10 | 130.1995 | 140.1995 |
| Kyber-512 | 2^−20 | 120.1995 | 140.1995 |
| Kyber-768 | 2^−20 | 180.9587 | 200.9587 |
| Kyber-1024 | 2^−20 | 250.7236 | 270.7236 |

Noting that few gates touch memory cannot make an attack cheaper than its own
gate count. The physically-shaped model is additive,
`(1−f)·T + f·T·M^c`, which reduces to `T` at c = 0 for every f. At f = 1 the two
agree exactly, so **the headline c\* is untouched**; the sensitivity rows are not:

| set | c\*(f = 2^−10) additive | c\*(f = 2^−10) as published | difference |
|---|---:|---:|---:|
| Kyber-512 | 0.142125 | 0.144648 | +1.8% |
| Kyber-768 | 0.121674 | 0.121841 | +0.1% |
| Kyber-1024 | 0.058086 | 0.062326 | **+7.3%** |

The published form is biased *against* the batch's own conclusion (it inflates
c\*), so this is a correctness defect and not a thumb on the scale. It should
still be corrected: it is a wrong equation in a durable artifact.

### 3.4 The axis H9 never explores is the one KN-OPEN-017 asks for

H9 varies the **number** of accesses. Wiener's charge is about the **distance**
of an access — the diameter of the region the wire must span. A list-decoding
sieve deliberately localises work into buckets/filters, so the memory an
individual access must reach is plausibly far smaller than the whole database,
and the right charge would be `M_eff^{1/3}` with `M_eff ≪ M`. KN-OPEN-017's
closing requirement is explicit: a full-cost sieving model must price "the
near-neighbour list **and its access pattern**." The batch prices the list. It
does not price the access pattern; H9 replaces it with the crudest possible
model (every gate reaches the whole database).

I checked whether the pinned instrument could supply a locality figure. It
cannot: `MATZOV.NN_AGPS` (`estimator/reduction.py:972–998`) holds only fitted
time coefficients `a` and `b` per near-neighbour variant, with no space or bucket
entry, and `estimator/lwe_primal.py` contains no `mem` field at all.

**This objection does not restore the undercut, and I say so.** For locality
alone to rescue it at c = 1/3 you would need `(1/3)·log2 M_eff ≤ margin`, i.e.
log2 M_eff ≤ 3 × margin = **8.40 / 18.12 / 3.83 bits** — an effective working set
of a few hundred elements or fewer. No sieve of this family has that. The
locality axis is a completeness gap in the batch's answer to KN-OPEN-017, not a
threat to its conclusion.

---

## 4. (d) H10: how much does "upper bound" cost the −26.70 / −37.84 / −59.03 headline?

H10's justification for not re-optimising is that it "requires a cost model for
lower-memory sieve variants ... that lattice-estimator's RC.MATZOV does not
provide." **That is true of *variant* sieves and false of the check that
matters.** Re-optimising β/η/d *within* RC.MATZOV needs nothing new: put the
charge inside the reduction cost model and the estimator re-optimises by itself.

I did it (probe RT-C). Advisory only: a charged reduction cost model is an
**uncovered path** — the harness's known-answer control covers
`primal_bdd`/`RC.MATZOV` and nothing else, so these figures carry no Sage
reference and are labelled `unable_to_check` in the report.

| set | c | re-optimised log2 cost | β | η | d | package Model B | recovered |
|---|---:|---:|---:|---:|---:|---:|---:|
| Kyber-512 | 1/6 | 154.378325 | 391 | 420 | 1002 | 154.5257 | +0.147 |
| Kyber-512 | 1/3 | 168.568366 | 393 | 418 | 1000 | 169.0295 | **+0.461** |
| Kyber-768 | 1/6 | 222.324332 | 608 | 638 | 1423 | 222.4553 | +0.131 |
| Kyber-768 | 1/3 | 243.700417 | 609 | 637 | 1425 | 244.1417 | +0.441 |
| Kyber-1024 | 1/6 | 300.309853 | 856 | 888 | 1871 | 300.3779 | +0.068 |
| Kyber-1024 | 1/3 | 329.881847 | 858 | 886 | 1880 | 330.2350 | **+0.353** |

(Kyber-768/1024 comparators are the derivation report's 4-decimal table values,
so their "recovered" column carries rounding at the 10⁻⁴ level; Kyber-512 uses
full-precision `results.json`.)

Three readings, all of which the package should have had:

1. **The "upper bound" caveat is worth under half a bit within RC.MATZOV**, not
   the open-ended concession H10 implies. A reader of §7 item 3 is told the
   −26.70 figure is an upper bound and given no scale; the scale is ≤ 0.47 bits
   against an undercut of 2.80. **No, a within-family re-optimising attacker
   cannot recover the undercut** — it would need 26.70 bits and gets 0.46.
2. **H10's predicted direction is half wrong**, which is checkable and worth
   correcting. H10 says the attacker moves "toward smaller sieve dimensions."
   The re-optimum moves β *up* (389→393, 606→609, 855→858) and η *down*
   (422→418, 640→637, 889→886): more BKZ preprocessing to shrink the *final*
   BDD call, which is the sieve that sets peak memory (H2/H3). The mechanism is
   right, the stated direction of β is not.
3. **A ceiling argument was available for free and was not made.** Under
   RC.MATZOV the charge adds `c·0.2075` per unit of sieve dimension, i.e. 0.0692
   at c = 1/3. Recovering 26.70 bits by shrinking the sieve dimension would need
   Δn ≈ 386 — the entire sieve — while the free-memory term grows at 0.296 per
   unit in the opposite direction. The method ceiling is nowhere near the
   headline. That is a two-line argument the batch could have written instead of
   an unquantified caveat.

What H10 *legitimately* leaves open is the part outside RC.MATZOV: tuple
sieving, reduced-database sieving, and enumeration hybrids. That is where the
c = 1/3 row could still move materially, and it is §5's cheapest check.

---

## 5. (e) H7: does the unsourced c = 1/2 borrow authority?

**Labelling: as good as labelling gets.** `results.json["charge_conventions"]`,
the §4 provenance table, H7's `validation_status`, and
`what_this_batch_did_not_validate` all say c = 1/2 and c = 1/6 are the batch's
own construction with no source. I could not find a place where the disclosure
is missing.

**Usage: not as good.** §5 states "c\* is ... **15.8× / 10.9× / 70.9× smaller
than the unsourced 2D exponent 1/2**", which puts an unsourced number into a
headline ratio. Delete that sentence and nothing is lost; the sourced 1/3 ratio
already carries the point, and 1/2 > 1/3 makes the second ratio arithmetically
redundant. c = 1/6 is worse: it is declared "probe point only, shape only," has
no interpretation at all, and still appears as a row in all three per-set margin
tables at the same typographic weight as the sourced rows.

**The real H7 problem is on the *sourced* side.** The label "SOURCED" on c = 1/3
is doing more work than the source supports. What KN-LIT-094 supplies (per its
corpus entry, `citation_verified: read`) is *one worked example*: BSGS costs
n^{1/2} processor steps and n^{2/3+o(1)} full cost. The batch back-derives a
general law from it — "that is exactly `T · M^{1/3}` at T = M = n^{1/2}" — and
applies the law to a sieve. BSGS makes n^{1/2} accesses each spanning a table of
n^{1/2} cells; a list-decoding sieve's access pattern is not that, and whether
the same exponent transfers is *precisely the question KN-OPEN-017 poses and
declares unanswered*. KN-LIT-094's own corpus entry states under "Not verified
here" that "the three-dimensional wiring bound and the per-attack derivations in
Sections 3 onward were not re-derived."

So the headline comparison "c\* is 10.5× below the sourced 3D exponent 1/3"
compares a computed quantity against an exponent whose applicability to this
algorithm is the open problem being cited as the motivation. That does not make
the comparison useless — 1/3 is the right order-of-magnitude anchor — but
"sourced" should read "transferred by analogy from KN-LIT-094's BSGS analysis;
the transfer to a bucketed sieve is not established."

---

## 6. (f) Direction asymmetry and selection effect

### 6.1 The case that this is a selection effect

The direction of this result was **determined before the run**. For M ≥ 1 and
c ≥ 0, `T·M^c ≥ T`: memory charging can only raise the estimate. A question
whose answer direction is fixed by construction is not a test, and the only free
content — the magnitude — was itself pinned to within ~15% by two numbers already
in the ledger (§1.1). After nine batches searching for a break, the program asked
one question that could not come out as a break and reported that it did not.

The inventor protocol's §3 test — *name the parameter that is supposed to destroy
the signal and show what happens as it increases* — has no answer here. There is
no parameter whose increase makes c\* stop being small.

### 6.2 The case against

Four things, and they are strong.

1. **The question predates the batch.** KN-OPEN-017 was added 2026-07-24 and
   states in terms that no corpus source computes the memory charge for sieving.
   The batch did not invent a convenient question.
2. **The Coordinator's own objective pre-committed to the direction**: "report
   the margin **in whichever direction it falls**" (BATCH-010
   `dispatch_queue.json`). That is a pre-registration, and it held.
3. **AGENTS rule 9 requires exactly this.** A program that only ever reports
   margin-reducing findings and declines to report the margin-restoring one is
   the failure mode rule 9 names. Reporting an inconvenient direction is
   compliance, not bias.
4. **The batch refused the overclaim available to it.** §7 item 2 says in terms
   that a raised estimate is not a proof of security; §7 items 3–5 list the
   assumptions that could move it back. A batch running a selection effect does
   not write its own §8.

### 6.3 Judgement

Not a rule-9 concern. The defect is not motive but **falsifiability**: the
package should state plainly that the direction of the result was determined by
the algebra and that only the magnitude was in question, so a reader does not
mistake a determined direction for a confirmed one. The honest null the protocol
asks for is not available for the *direction*; it is available for the
*denominator*, and §7 is where the package fails it.

---

## 7. The null object: CTRL-5 cannot fail

CTRL-5 is the package's inventor-protocol "controls before belief" check. It
re-runs the charging pipeline with `log2 M = 0` and confirms the margin does not
move for any c and that c\* does not exist.

`log2 M = 0` means `M = 1`, so `M^c = 1` for every c. **CTRL-5 asserts that
x · 1^c = x.** It is a property of exponentiation. It would pass identically if
the memory figure were off by fifty bits, if the sieve dimension were the wrong
one, if the unit chain were inverted, or if the pipeline were charging a number
read from a different scheme. It distinguishes nothing, and the derivation report
claims it does: "it distinguishes 'the memory figure produces the penalty' from
'the pipeline manufactures a penalty for anything fed into it'." It establishes
only the second half, and only in the degenerate case.

Two nulls of the right shape, both cheap, both absent:

- **Null on the sign (I ran it, RT-B2).** Score the same costs against a cutoff
  they do *not* undercut: Kyber-1024's 270.7236 against the Category-3 cutoff 207
  gives margin −63.72, c\* = −0.352; Kyber-512's 140.1995 against 128 gives
  margin −12.20, c\* = −0.138. The pipeline does discriminate on the sign, and c\*
  correctly ceases to mean anything. Worth having; the package has nothing like
  it.
- **Null on the denominator (I ran it, RT-B3, §1.1).** Substitute an arbitrary
  sieve-memory exponent. The conclusion is unchanged across [0.05, 0.40]. This is
  the control that actually informs: it shows the finding is robust *and* shows
  that H4's sourcing effort was not load-bearing.

The right null for a memory-charging pipeline is a **memory figure of the wrong
shape**, not a memory figure of zero.

---

## 8. Scope: c\* is a per-attack quantity carrying a scheme-level name

`c* = 0.0316 / 0.0459 / 0.0071` is the critical exponent **of `primal_bdd` under
`RC.MATZOV` at the free-memory optimum**. The scheme-level question — what charge
exponent is needed before *no* attack undercuts the cutoff — is the maximum of
c\* over the attack frontier, and it is unknown. H12 gestures at this ("if a
cheaper attack exists ... c\* rises proportionally") but the direction is stated
too weakly: a low-memory attack has a *small* log2 M, so even a modest undercut
would give it a *large* c\*, and the scheme-level exponent could exceed 1/3 while
this one sits at 0.03.

Relatedly, no deliverable in the package carries a `dominated_by` or `sota_delta`
field (`grep -c` returns 0 across all four artifacts). For an Executor
observation record that is arguably not required. But the package does make a
frontier claim in prose — that charged sieving costs 169.70 / 244.84 / 331.03
bits — and reports only one point of a time–memory frontier while comparing it
against a scalar cutoff. The row that is missing is the low-memory one, and it is
the analogue of the van Oorschot–Wiener interpolation the program's own red-team
contract requires for exactly this situation: *check whether the memory-light
baseline dominates everywhere practical before charging the memory-heavy one.*

---

## 9. (g) The cheapest single check that would falsify the headline

The headline has two halves and they falsify differently.

**Half one — the number `c* = 0.0316/0.0459/0.0071`.** It is an identity in a
CTRL-2-pinned margin and a constructed log2 M, so only log2 M is falsifiable.
Cheapest check, one grep, no run:

```
grep -n "mem" /tmp/le/estimator/lwe_primal.py        # returns nothing
grep -n "short_vectors" /tmp/le/estimator/lwe_primal.py   # returns nothing
sed -n '410,420p' /tmp/le/estimator/reduction.py     # `# pick something`
```

I ran these. `lwe_primal.py` has **no memory field and never calls
`short_vectors`**; `MATZOV.NN_AGPS` holds only time-fit coefficients. So the
instrument supplies **no memory number for `primal_bdd` at all**. H4's
"in-instrument" sourcing (a) points at `reduction.py:415/854/936`, which live in
`short_vectors()` — a function this attack does not invoke — and whose 0.2075
literal the estimator's own authors annotated `# pick something`. H5's claim that
"numerator and denominator live in one convention" borrows the convention from
`lwe_dual.py:172`, a different module. The construction is defensible; the word
"SOURCED THREE WAYS, none of them an assumption made here" (H4) is not, and one
grep settles it.

**Half two — the conclusion "the undercut does not survive memory charging."**
That is a minimum over attacks asserted from a single point. The cheapest single
check that could falsify it:

> Run `primal_bdd` (and `primal_usvp`) in the same pinned harness under a
> **polynomial-memory, enumeration-based reduction cost model already shipped in
> the pin** — `RC.CheNgu12`, `RC.ABFKSW20`, or `RC.ABLR21`, all present at
> `/tmp/le/estimator/reduction.py:1040–1049` — and charge it `M^c` with M
> polynomial. If any lands below 143 / 207 / 272 at c = 1/3, the sentence falls.

One estimator call per set per model; seconds of compute; no new mathematics; no
new instrument. It is also the exact question KN-OPEN-017 asks (the
enumeration/sieving crossover under full cost), so the check pays twice.

I did **not** run it — the handoff budgets one run and I spent it on the control
plus RT-A/B/C — and I therefore assert nothing about its outcome. Marked
`unable_to_check`. The a-priori expectation, which is an argument and not a
computation, is that the enumeration models' super-exponential growth in β makes
recovery of 26.70 bits at β ≈ 389 implausible; that expectation is exactly what
the check is for.

---

## 10. Constraints attached to the pass

1. Restate the headline as the inequality and its invariance, not as an eight-digit
   critical exponent. Report c\* to at most two significant figures and state
   `c* = margin / log2 M` in the first sentence.
2. Any downstream ledger record must use the derivation report's qualified
   wording ("does not survive any of the memory charges **examined here**"), never
   the snapshot commit message's "survives only under literally free memory."
   Record that the commit message is stronger than its own artifacts support.
3. State that this batch does not contradict, correct, or qualify EV-MLKEM-015,
   whose undercut is a c = 0 statement by the batch's own H6.
4. Rename the headline quantity `c*(primal_bdd, RC.MATZOV)` and state that the
   scheme-level exponent is a maximum over the attack frontier and is unknown.
5. Correct the f-model to the additive form, or state that the multiplicative
   form is a first-order approximation valid only for `f·M^c ≫ 1`.
6. Correct or withdraw `log2_memory_bits_information_theoretic` (§4.6 of the
   report.yaml findings) and, if it is retained as a unit, restate the "c\* moves
   by about 15% across units" claim to include it.
7. Downgrade the "SOURCED" label on c = 1/3 to "transferred by analogy from
   KN-LIT-094's BSGS analysis," and delete the ratio-to-1/2 sentence.
8. Do not describe CTRL-5 as a null-object control. Replace it with RT-B2 (sign
   null) and RT-B3 (denominator null), or state that the control-before-belief
   obligation is unmet.
9. Nothing here supports closing KN-OPEN-016 or KN-OPEN-017; the batch does not
   claim to and neither do I. KN-OPEN-017 remains open on the access-pattern half
   of its own closure condition.

---

## 11. Provenance

- Reviewed snapshot: `7afc38466bb697ac309a89a49e92f396393a5e73`; working tree
  identical to it for the reviewed paths (`git diff --stat` empty).
- Reviewed file hashes: `derivation_report.md`
  `2efc50004842a7b36253a5c4c5b0bff4800384647c27e91bb3fba8639b1524e1`;
  `heuristics.yaml` `fc08ed1e1652fd26a6015bf499055e37bfc8c43b7302de1c0dcf01a47a5b16c2`;
  `memory_charged_derivation.py`
  `f3174028a6fae50f1a617cc3b8f1925ef648af41794ccd20f1779d8f1a3e110a`;
  `receipt.json` `aa10dd020a30903f87b7709631cd9f1e57d4ddbc70799fb57a51dc7b35a3ca9c`;
  `results.json` `99e4da7aa765001284d725c1d7c460537b5f4907a10823ad13cba3a39caabb8f`.
- Instrument: lattice-estimator `3e48ef421ec256afddb3e7d2249a77eab6e9ba12` at
  `/tmp/le`, verified by `git rev-parse HEAD` in this session.
- No network fetch was performed in this task, so there is no url/status/bytes to
  record. Every citation above is to a repository path or to a corpus entry read
  in this session; nothing is quoted from recollection.
- **Concurrency observation, recorded not repaired.** After my run finished, the
  shared tracked file `tools/sage_free_estimator/shim/sage/all.py` acquired an
  uncommitted modification (`git diff --numstat` → `15 0`, purely additive: three
  new methods `pi`/`e`/`euler_constant` on `_RealField`), attributed in its own
  docstring to "independent validation (BATCH-010 D4)", i.e. the concurrent task
  `TASK-20260803-90327f`. Timestamps: my probe stdout `01:49:41`, the shim
  modification `01:59:19`. **My run therefore executed against the shim exactly as
  committed**, and in any case the added methods are reached only from
  `estimator/prob.py:112,114,211,213` (the dual-attack distinguisher), never from
  the `primal_bdd` path, and the known-answer control reproduced the archived Sage
  reference at delta 0.0 during my run. I note this only because it means a
  shared instrument outside any declared `write_scope` was edited mid-batch while
  a snapshot was under review; that is the Coordinator's to resolve, not mine, and
  it does not affect any number in this report.
- Requested policy `review-adversarial`, reasoning effort `xhigh`, independent
  session `true`; resolved model `claude-opus-5`; `fallback_used: true` (the
  policy alias routes to a GPT-5.6-family model this Claude Code harness cannot
  resolve; subagents run `model: inherit`). `model_verified: false` — no
  `orchestration.adapter doctor --probe` was run.
