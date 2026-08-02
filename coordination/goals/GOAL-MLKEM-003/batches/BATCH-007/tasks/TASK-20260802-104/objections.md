# TASK-20260802-104 — red team: the argued case

**Target:** Coordinator snapshot `bd184fff917e84ff1f0c909412a3e49e2a5e784c`, the
TASK-20260802-101 source-adjudication package.
**Scope of this review:** the *interpretation*, its materiality, and its scope.
Arithmetic and quotation fidelity are TASK-20260802-103's job and are not
re-adjudicated here.
**Independent session.** I did not read the producer's conclusions as
authoritative and I re-ran two retrievals of my own (recorded in §0).
**Verdict: `pass_with_constraints`.** All three verdict *labels* survive an
adversarial reading. Two of the *supporting arguments* do not, and one of them
is the argument that protects the batch's headline. Constraints in §11.

---

## 0. Retrievals performed by this session

Two, both inside the access classes the handoff states are permitted. Recorded
so that nothing below rests on the producer's record alone.

| id | url | http_status | retrieved_at (UTC) | bytes | sha256 |
|---|---|---:|---|---:|---|
| `rt104-eprint-versions-retry` | `https://eprint.iacr.org/archive/versions/2022/1750` | 403 | 2026-08-02 | 5569 | (Cloudflare `Just a moment...` interstitial, not the object) |
| `rt104-cwi-33407-refetch` | `https://ir.cwi.nl/pub/33407/33407.pdf` | 200 | 2026-08-02 | 1021750 | `947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e` |

The second hash equals the producer's `cwi-33407-ducas-pulles-2023` record
exactly, so §1 below is derived from the same bytes the package is derived from.
The first independently confirms the producer's `eprint-2022-1750-versions`
403: I re-attempted the *HTML* versions listing in a session where ePrint HTML
otherwise works, and it is challenged too. No cheaper path exists there.

No GitHub host was contacted. No `raw.githubusercontent.com` substitution. No
`web.archive.org` attempt. No ePrint PDF attempt.

---

## 1. OBJ-1 — the incommensurability argument is wrong on the load-bearing figure

**Severity: high. This is the place the batch is about to claim more than it
measured.**

`adjudication_results.json`, Q3 → `sources_searched[1].note`:

> "Their T is a number of samples/candidates (e.g. T = 2.05n uniform samples),
> not a score threshold, so their Figure 4 log2 T axis is not commensurable
> with Carrier's Fig 4.1 T-axis."

and `source_adjudication.md` §Q3: *"The Ducas–Pulles result is the closest thing
in the corpus and it is **not commensurable** with the residual … it transfers
nothing."*

That is true of Ducas–Pulles' **Figure 4** and false of their **Figure 3**, and
Figure 3 is the object described by the §5.2 passage the producer actually
quoted. From the same bytes (`947f2826ce64…`), the Figure 3 legend reads
verbatim:

```
Legend: distribution of the scores on the x-axis and the logarithm (base 2) of the
survival function (SF) on the y-axis. Dashed blue line: prediction from the heuristic
analysis. Red line: experimental distribution. 2^45 samples per curve.
Fig. 3. The distribution of scores according to the prediction and determined
experimentally. The experimental data is obtained with unif_scores.py and listed in
data/unif_scores_nX.csv of the auxiliary files.
```

and Figure 5 is the same plot for BDD (good) targets:

```
Fig. 5. The distribution of scores according to the prediction and the distribution
determined experimentally. The experimental data is obtained with bdd_scores.py and
listed in data/bdd_scores_nX.csv of the auxiliary files.
```

Structurally that is Carrier's Figure 4.1: score threshold on the x-axis,
log2 of the tail probability on the y-axis, heuristic prediction against
experiment. For uniform (= wrong) targets it *is* the survival function
`P[score ≥ x]` — the definition is stated in the same document ("the survival
function (SF) of D is `P[X ≥ x]`"). Ducas–Pulles measure it over dimensions
n = 40–90 with **2^45 samples per curve**, and measure the good-target
distribution on the same score axis in Figure 5.

Sampling depth, for comparison. Carrier's estimator is
`|{z ∈ Z_q^{k_fft} : F(z) ≥ T}| / q^{k_fft}` over 4000 iterations at
`q = 241, k_fft = 3`, so its effective sample count is
`4000 · 241³ = 2^35.70`. Ducas–Pulles' is `2^45`. The neighbouring attack's
analogous measurement is roughly **9.4 bits deeper** than the one KN-FIND-012
audits.

**What this does and does not do.**

- It does **not** overturn Q3's verdict label. On the narrow reading — "does any
  retrieved source report *Carrier's* `Pwrong`, for *Carrier's* polar-decoding
  score function, at the aligned `Pgood` threshold" — the answer is still no,
  and `indeterminate` stands.
- It does **not** overturn KN-FIND-012 or KN-FIND-014. Those are claims about
  what *Carrier's* Figure 4.1 covers, and they survive intact.
- It **does** destroy the sentence "it transfers nothing," and with it any
  reading of Q3 as establishing that the residual measurement is novel in kind.
  The measurement type is established prior art in the immediately adjacent
  attack, published in 2023, by the authors of the objection this whole lane is
  built on, at greater depth, with the good-target and wrong-target
  distributions both plotted.
- It **does** mean the residual must be restated. What is undone is the
  *instantiation* for the polar-code score function — not the *measurement*.
- It also narrows a headline number honestly: Ducas–Pulles' 2^45 does not close
  the residual either. Kyber-scale `log2(Pwrong) = −119.57` is ~74 bits below a
  2^45 floor rather than ~84 bits below a 2^35.7 floor. The extrapolation
  problem is real at either depth; the specific "~84 bits" figure is
  instrument-relative.

**Cheapest check (zero network):** `pypdf` extraction over the already-hashed
CWI PDF, printing the `Fig. 3` and `Fig. 5` captions and the legend block. I
ran exactly this. The producer's own extract file
`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/ducas-pulles-2023-sec5.2-5.3-excerpt.txt`
already contains the §5.2 and §5.3 sentences ("We measured the score
distribution for uniform targets… plotted our result in Figure 3"; "We measured
the score distribution for BDD targets… plotted our result in Figure 3"); only
the caption and legend were outside the extracted window.

---

## 2. OBJ-2 — the instrument behind "none of them reports the quantity" has no
discriminating power

**Severity: high.**

`fetch_sources.py`, three times (Ducas–Pulles, Pouly–Shen, MATZOV):

```python
r["mentions_Pwrong_token"] = "Pwrong" in joined
```

`Pwrong` is Carrier's own notation. A literal substring test for it returns
`False` on every paper that is not Carrier's, *regardless of whether that paper
measures the quantity*. The instrument measures notation, not content.

This is the inventor-protocol §3 situation exactly, and the null-object control
is already available and already run: apply the instrument to a document that
demonstrably **does** report the quantity — Ducas–Pulles, per OBJ-1 — and it
returns `False`. I confirmed this directly against `947f2826…`:
`"Pwrong" in text` → `False`; `"survival function (SF)" in text` → `True`. A
matched null. Under §3 that is a controlled null, not a finding, and the
`mentions_Pwrong_token: false` fields may not be carried as support for
anything.

The aggravating detail is placement. In `adjudication_results.json` the fields
`mentions_Pwrong_token: false` and `reports_pwrong_at_operating_threshold:
false` sit in the same object, in that order, for each source. A downstream
reader will take the first as evidence for the second. It is not; it is
evidence about naming conventions.

**Cheapest check:** re-run the same three cached PDFs with a content vocabulary
— `{"survival function", "score distribution", "uniform target", "BDD target",
"false candidate", "log2", "SF"}` — and report per-source hit counts alongside
the token result. Zero network; all three objects are hashed and re-fetchable
from hosts that answered 200.

---

## 3. OBJ-3 — the "byte-identity" observation overstates its scope, and is
near-vacuous within it

**Severity: high (scope), medium (strength).**

`source_adjudication.md` unexpected observation 6:

> "the HAL object the findings were derived from has not changed since it was
> vendored, so none of KN-FIND-012/013/014/016 was derived from a copy that has
> since been silently replaced."

**Scope defect.** The byte-identity check covers one object: the HAL PDF. But

- KN-FIND-012's evidence is `experiments/EXP-MLKEM-011/vendor-lock/data/Pwrong_*.out`
  and `Pgood_*.out`;
- KN-FIND-014's is `experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py`;
- KN-FIND-013 is built on KN-FIND-012's numbers.

All three trace to `kevin-carrier/CodedDualAttack` — the exact object Q2 could
not reach. For three of the four findings named, the proposition asserted by
observation 6 is precisely what this session could not test. Only KN-FIND-016's
PDF source is covered.

**And the code side is worse than untested for one of them.**
`experiments/EXP-MLKEM-011/specification.yaml` line 22 records
`code: https://github.com/kevin-carrier/CodedDualAttack/tree/main/verifyModel`
— an unpinned branch URL, no commit — and
`experiments/EXP-MLKEM-011/runs/RUN-MLKEM-011-001/fig41_left_gaussian_baseline.json`
records the data path as `/tmp/CodedDualAttack/verifyModel/ScoreExperimentalDistribution/data/…`.
So KN-FIND-012's upstream repository state is not recorded anywhere.
KN-FIND-014's is (`9c1367f85d26038244bc83c025d84c0b7006f2ee`, in
`EXP-MLKEM-013/specification.yaml`). That asymmetry is invisible in the package
and should not be.

**Strength defect, within scope.** The HAL object's own metadata
(`extracts/carrier-hal-05406481-pdf-metadata.json`) reads `/Creator: HAL`,
`/CreationDate: D:20260721165108+02'00'` — HAL regenerates the cover-sheeted
PDF, and did so on 2026-07-21. EXP-MLKEM-010 ran 2026-07-31; the re-fetch is
2026-08-02. The demonstrated stability window is **two days**, over a
HAL-regenerated derivative rather than over the authors' file. What actually
excludes a silent author-side replacement is `version_i: 1` in the HAL API
record, which the producer did capture — that is the load-bearing fact, and the
hash comparison is close to decorative next to it.

**Cheapest check:** `git log --diff-filter=A -- experiments/EXP-MLKEM-011/vendor-lock/data/`
to date the vendoring, and `grep -rn "9c1367f\|commit" experiments/EXP-MLKEM-011/`
to confirm no commit pin exists. Then restate observation 6 as covering
KN-FIND-016's PDF source only.

---

## 4. OBJ-4 — Q1 is a near-vacuous question and its verdict label names the
wrong proposition

**Severity: medium.** The handoff asks for the strongest case that Q1 is a
trivium dressed as a result. Here it is, then the honest other side.

**(a) The answer was determined before the session began.** ePrint records the
last revision as 2025-06-11 (`extracts/eprint-2022-1750-abstract-page.txt`
line 44). KN-FIND-016 was added 2026-07-31 — thirteen months later. The authors
were never notified by this program. There is no counterfactual world in which
the cell had changed in response to anything. Q1's entire informational yield
over the pre-existing vendored artifact is one HTML line reading "last of 3
revisions." Thirty-five retrieval attempts; for Q1, one bit.

**(b) The defect it confirms is, by the program's own finding, immaterial.**
KN-FIND-016 records that Table 5.1's nine Algorithm-3.1 cells match the
authors' pickle within 0.05 bits, that the abstract's 3.5/11.9/12.3 shortfalls
are "arithmetically supported given the authors' intermediates," and that the
only consequence of the `143.30` typo was an 8.8-bit anomaly in the program's
*own* paper-only recomputation, which correcting the typo *removes*. The typo
is an appendix transcription slip whose discovery made the paper look **more**
internally consistent, not less. Confirming it survives is confirming the
persistence of a defect that the program has already shown does not touch the
security claim.

**(c) The verdict label names the finding, not the proposition.**
`confirmed_in_current_source` reads as "KN-FIND-016 is confirmed." KN-FIND-016's
substantive claim is *"`143.30` is a transcription error for ≈`134.30`."* Q1 did
not adjudicate that — the `verdict_scope` string says so explicitly and
correctly ("This says nothing about whether 143.30 is in fact a transcription
error"). But enum labels travel and scope strings do not. Anyone consuming the
enum will raise KN-FIND-016's confidence on evidence that bears on none of its
content. This is the implicit inference the handoff asked me to attack, and it
is live at the level of vocabulary rather than of prose.

**The honest other side, which I do hold.** Q1 establishes one thing that is not
trivial: the four findings target the **published CRYPTO 2025 version of
record** — `Published by the IACR in CRYPTO 2025`, DOI
`10.1007/978-3-032-01855-7_15` — not a superseded preprint. That cuts both
ways and both cuts are informative. It *raises* the stakes of KN-FIND-012 and
KN-FIND-014, because peer review did not close the Fig-4.1 coverage gap. It
*lowers* the stakes of KN-FIND-016, because peer review did not catch the typo
either, which is what one expects of an immaterial appendix slip. Together with
the retitling (below), that is the batch's durable output, and the headline
should lead with it rather than with "the erratum is unfixed."

The retitling discovery is worth its own sentence. The 2023 objection
literature cites this paper as three-author *"Faster dual lattice attacks by
using coding theory"*; the current revision is four-author *"Assessing the
Impact of a Variant of MATZOV's Dual Attack on Kyber."* Anyone reconciling
KN-LIT-111's bibliography with KN-LIT-7617 needs that, and it was obtainable
only from primary sources. It is a better result than Q1.

**Constraint:** Q1 may not raise KN-FIND-016 above `confidence: provisional`.
**Cheapest check:** read `knowledge/findings/KN-FIND-016.md` lines 43–47 against
`adjudication_results.json` Q1 `verdict_scope`. They describe different
propositions.

---

## 5. OBJ-5 — Q1's revision-identity inference, and why its stated remedy would
misfire

**Severity: medium.** The handoff asks whether `confirmed_in_current_source` is
honest here or whether it should be `indeterminate`.

**Answer.** It is honest for the proposition actually tested and dishonest for
the proposition the label implies. Specifically:

- *"The authors' own deposit of the 2025-06-11 build prints 143.30, and ePrint
  records no revision after 2025-06-11"* → `confirmed_in_current_source`. Fully
  supported.
- *"The bytes ePrint serves today print 143.30"* → `indeterminate`. Never
  tested.

The fix is to the proposition, not to the enum. Rewriting the verdict to
`indeterminate` would discard a real, verified fact; leaving the proposition
unstated licenses the second reading. Restate and keep.

**The scenario in which the inference is wrong.** HAL v1 holds the CRYPTO 2025
camera-ready rather than ePrint revision 3. This is not idle: HAL's own
`producedDate_s` is `2025-08-17` and the conference was August 2025, so the
deposit is plausibly conference-associated. A camera-ready and an ePrint
revision built from a shared source on 2025-06-11 would carry the same
`/ModDate` while differing in body content after copy-editing.

**The retrieved fact that would have caught it** is the per-revision listing at
`https://eprint.iacr.org/archive/versions/2022/1750`, which enumerates each
revision's timestamp and archive PDF URL. It is 403 Cloudflare-challenged. I
re-attempted it independently this session and confirm the 403 (§0), so this is
a genuine dead end in this harness, not a producer omission.

**Countervailing, and the producer under-uses it.** The ePrint `Note` — "This
version of the paper differs only in the title" — implies revisions 2 and 3
have identical bodies, so the HAL-vs-rev2/rev3 ambiguity is *immaterial for
Table C.2*; and the title page carries the rev-3 title, so HAL ≠ rev1. That is
a stronger defence of Q1 than the four-point chain the package actually gives.
But the `Note` has a second natural reading — *"this ePrint version differs
only in the title from the published version"* — under which it says nothing
about rev2→rev3 while resolving the package's "Springer version unknown" item.
The package commits to one reading silently. Both readings support Q1; they
support it for different reasons and license different downstream statements
about the Springer version of record.

**The stated remedy would misfire.** `verdict_sensitivity` says "the residual
is one successful GET of `https://eprint.iacr.org/2022/1750.pdf`." That
implies a hash comparison. It cannot be one: the HAL object has a HAL cover
sheet (37 pages; the paper's title page is page 2) and `/Creator: HAL`,
`/CreationDate: D:20260721165108`. **Byte-identity with any ePrint-hosted PDF
is impossible by construction**, so a naive execution of the stated remedy
returns a mismatch and could be misread as contradicting Q1. The residual check
must be content-level: extract the Table C.2 page from ePrint bytes, read the
`CN/Kyber-512` cell, and compare `/ModDate`.

**Cheapest check:** the single most-available target for ePrint-hosted bytes is
already named in the package's own provenance — the Wayback availability API
returned 200 and named snapshot
`web/20260114001146/https://eprint.iacr.org/2022/1750.pdf` (2026-01-14, after
both the last revision and the HAL deposit). That URL is 403 by egress policy
*here*; it is one GET from any session where web.archive.org is permitted, and
it is a fixed immutable URL rather than a hope that Cloudflare does not fire.
Compare content, not hashes.

---

## 6. OBJ-6 — Q2 as posed cannot adjudicate what it is being used for, even with
access

**Severity: medium.** First, the rule-5 audit the handoff asked for, because it
matters that this comes out clean: **I find no leakage of infrastructure
failure into evidence about KN-FIND-014.** `adjudication_results.json` Q2 sets
`observed_head_commit_sha: null` explicitly rather than omitting it, states
"neither confirmed nor contradicted," cites rule 5 by name, records the
`numpy/numpy` control probe establishing the denial is session-wide, and
records the `raw.githubusercontent.com` non-attempt with its reason. Q2 is the
cleanest part of the package and the non-attempt is the right call.

The objection is to the question, not the answer.

The paper's footnote (`extracts/carrier-hal-05406481-fig4.1-validation-section.txt`)
cites `https://github.com/kevin-carrier/CodedDualAttack/tree/main/verifyModel`
— a **branch pointer**, mutable, not a commit. So:

1. "Does the asymmetry persist at current HEAD" is not the question that bears
   on the published Figure 4.1. HEAD in 2026-08 is not the object CRYPTO 2025
   cited. The question that bears is *what was the state of
   `verifyModel/ScoreExperimentalDistribution/FFT_sample.py` at or before the
   2025-06-11 build.*
2. The Q2 `remedy` asks only for `commits/main → sha` and a diff against
   `9c1367f`. That cannot answer (1). Run in that order it produces a
   HEAD-vs-9c1367f comparison and no statement about the published figure at
   all.
3. The `incidental_gain` says the footnote "confirms that this code is the code
   the paper itself offers as the experimental backing for Approximation 4.9."
   The footnote offers a *directory as of an unspecified time*. Identifying it
   with `9c1367f` is an inference of the same species as Q1's revision-identity
   inference, and unlike Q1's it is not labelled as one. (The path *does* line
   up — `EXP-MLKEM-013/specification.yaml` names
   `verifyModel/ScoreExperimentalDistribution/FFT_sample.py`, which is inside
   the cited directory — so this is a labelling defect, not a mis-attribution.)

**Cheapest check:** once access exists, one call —
`GET /repos/kevin-carrier/CodedDualAttack/commits?path=verifyModel/ScoreExperimentalDistribution/FFT_sample.py&until=2025-06-12`
— returns the commit that backed the published figure. Do that **before** the
HEAD diff, and pin it.

---

## 7. OBJ-7 — the corpus sweep is incomplete in the one direction that would
settle novelty, and a relevant signal sits unexamined in a *retrieved* extract

**Severity: medium.**

The sweep had exactly two seeds: one ePrint full-text search (`coded dual
attack`) and Semantic Scholar citation edges of the Carrier DOI. It never
followed an edge *out of a retrieved abstract*, and it never searched for the
**quantity** under any name (see OBJ-2).

The concrete miss is in a file the package already committed.
`extracts/eprint-2026-1326-abstract.txt` names the provable-dual-attack line —
Pouly–Shen (EUROCRYPT 2024) → **Qu–Xu (ASIACRYPT 2025)** → LaMS — and states,
verbatim:

> "We also correct a parameter issue in previous Kyber estimates. With this
> correction, LaMS reduces the estimated attack cost by 22/31/41 bits for
> Kyber-512/768/1024, respectively, relative to the corrected CRT-based attack
> of Qu and Xu."

A **published correction to previous Kyber dual-attack estimates** is the same
species of object as KN-FIND-016, and a 22/31/41-bit re-costing is the same
species as KN-FIND-013's Δ-sensitivity. Neither is surfaced anywhere in the Q3
discussion, and Qu–Xu (ASIACRYPT 2025) never entered the retrieval set at all,
despite being named in a retrieved document. That is a live edge into precisely
the region where prior art for this program's findings would live.

**Cheapest check:** four requests, all in the permitted HTML class, no PDFs —
three ePrint searches (`score distribution dual attack`, `survival function LWE
dual`, `false candidates FFT distinguisher`) plus one landing-page GET for the
Qu–Xu paper.

---

## 8. OBJ-8 — a re-asserted quantity is a resolution artifact and is not flagged
as one

**Severity: medium. This is the "what should the quantity have done" check.**

`source_adjudication.md` §Q3 restates, now from the primary source, that "the
measured Pwrong support in the current text ends at T ≈ 1600–1800," and
KN-FIND-012 records `last T with Pwrong>0 = 1802` at `log2(Pwrong) ≈ −35.70`.

Carrier's estimator is `|{z ∈ Z_q^{k_fft} : F(z) ≥ T}| / q^{k_fft}` over 4000
iterations at `q = 241, k_fft = 3`. Its smallest attainable non-zero value is
therefore `1 / (4000 · 241³)`, and

```
log2(4000 · 241³) = 35.70
```

which matches the recorded floor to two decimals. **The "floor" is the
estimator's resolution limit, not a property of the distribution.**

Apply the inventor-protocol §3 question. The parameter that is supposed to
destroy this quantity is the iteration count: `T_last-positive` should march
outward as `−log2(iters · q^{k_fft})` deepens. A number that is fixed by the
sample budget carries no information about the soundness of Approximation 4.9 —
it reports how long the authors ran the script.

**This does not touch KN-FIND-012's real content.** The gap between the
measured `Pwrong` support and the `Pgood` operating threshold is real, the
`fraction_inside = 0` result is real, and the extrapolation distance to
Kyber-scale `log2(Pwrong) = −119.57` is real. What must stop is citing `1802`
or `−35.70` as though they were evidence *about the paper*.

**Cheapest check:** one line, no network, no new data — recompute
`−log2(4000 · 241³)` and compare to `−35.70`.

**Constructive follow-on, and this is the useful part.** The same closed form
inverts. It gives, directly, the iteration count needed for a Fig-4.1-style
simulation to reach the aligned `Pgood` threshold, and the count needed to
reach `−119.57` (which will be absurd, and *that* is the honest statement of
the residual). This converts KN-OPEN-016's residual from "unmeasured" into
"costed," which is a stronger deliverable than either and costs nothing.

---

## 9. OBJ-9 — partial access does not license partial novelty claims

**Severity: medium.** The handoff asks this directly.

`PUBLICATION-CANDIDATES.md` lines 7–12 state the correct rule for a total
block: *"Novelty therefore cannot be adjudicated here in either direction."*
Under *partial* access that rule does not weaken. It sharpens, and it sharpens
**by class**, not by fraction:

> A novelty claim is licensable only where the retrievable class is the class in
> which the prior art would live.

Here the retrievable class is HTML abstracts plus non-ePrint mirrors. The class
in which a re-measurement of a score survival function lives is the **full text
of PDFs**, and every ePrint PDF path in this harness is 403. Four full texts on
the direct follow-up line — Guo–Johansson (2021/948), 2026/1400, 2026/1326,
2026/599 — are unread, and the producer itself names 2026/1400 as "the most
likely single place a re-measurement or re-derivation of these quantities would
appear." So the novelty answer for the KN-OPEN-016 residual is **still not
adjudicable**, and 50% of the sources is not 50% of an answer.

Worse for the batch: the one class that *was* retrievable already contains
adverse prior art (OBJ-1). Partial access moved the novelty answer toward *less
novel*, not toward *novel*. Any document that reads this batch as strengthening
a publication posture has the sign backwards.

**Pareto honesty.** `adjudication_results.json` carries no `dominated_by` and no
`sota_delta` field. Inventor-protocol §5 makes an unchecked `null` a
fabrication under AGENTS rule 5; an *absent* field accompanied by a prose
dismissal of the single candidate frontier row is the same defect wearing a
different hat. If any part of this package is to support a publication posture
it needs, at minimum:

```
dominated_by: "Ducas-Pulles CRYPTO 2023 §5.2/5.3 (Fig. 3 uniform-target SF,
               Fig. 5 BDD-target scores, 2^45 samples, n=40..90) — for the
               measurement type"
sota_delta:   "no new measurement; the polar-code score-function instantiation
               is undone, and Carrier's own Fig 4.1 coverage gap is the finding"
```

**Cheapest check:** `grep -n "dominated_by\|sota_delta" adjudication_results.json`
→ absent.

---

## 10. OBJ-10 — the abstract-tension observation is over-read

**Severity: low.**

Unexpected observation 5 contrasts the abstract's *"we fully back up our
analysis with experimental evidences"* against Fig 4.1's `T ∈ [200, 1600]`.
Two problems, both small:

1. **Partial quotation of the referent.** The same abstract
   (`extracts/eprint-2022-1750-abstract-page.txt` line 13) also says *"we
   confirm their strong distortion properties through benchmarks"* — a second,
   distinct experimental component. The authors' "fully back up" covers more
   than `Pwrong`; contrasting it with `Pwrong` coverage alone overstates the
   tension.
2. **A universal claim over a document read in three slices.**
   `fetch_sources.py` extracts exactly three regions of the 37-page PDF: the
   title page, the page matching `"Table C.2" and "143.30"`, and the block after
   `"Validating our Analysis Through Simulations"`. "The **only** experimental
   validation of `Pwrong` in the paper" is not supported by that. Relatedly,
   "Figure 4.1 plots Pwrong only; no Pgood curve appears on it" is inferred from
   *text extraction*, which cannot see curves.

The narrowest valid version survives and should replace it: *the paper's own
`Pwrong` validation spans `T ∈ [200, 1600]` at `n = 43/50`, `k_fft = 3`, while
Table C.2 applies the approximation at `log2(Pwrong) = −119.57`.* That is
KN-FIND-012, already established.

**Cheapest check:** extract all 37 pages of the vendored PDF and grep
`experiment|simulation|benchmark|Figure`; render the Fig 4.1 page to an image to
confirm the absent `Pgood` curve. Both zero-network, on the file already in
`experiments/EXP-MLKEM-010/vendor-lock/`.

---

## 11. Closure-standard audit, and the constraints

**Premature closure: none found, and the package actively resists it.**
Unexpected observation 4 ("The lane is active, not saturated") cites 2026/1400,
2026/1326 and 2026/599 and refuses to treat the direction as mined out. That is
correct and I endorse it. Q2's remedy is real forward guidance naming a
concrete unblock (`add_repo`).

**Illegitimate closure: none asserted, but one is available downstream.** If the
batch headline is consumed as *"the four findings are confirmed against the
authoritative current text,"* that is a closure of the source-verification lane,
and under §4 it does not qualify: three of the four findings' upstream objects
(the `CodedDualAttack` artifacts) were never reached, and one of those three has
no commit pin at all (OBJ-3).

**The one closure the batch has actually earned**, stated at the §4 standard:

> *Named obstruction.* Every `eprint.iacr.org` **PDF** path in this harness
> returns HTTP 403 with `cf-mitigated: challenge`, and the block is path-class
> wide — demonstrated by the `2023/302.pdf` control, and extending to the HTML
> `/archive/versions/` path, which I re-attempted independently this session
> (§0). `web.archive.org` is separately blocked by egress policy, removing the
> standard fallback. *Therefore* no ePrint-hosted byte is obtainable in this
> harness, and no ePrint-hosted-bytes question can be answered here by any
> amount of further effort. *Forward guidance:* route PDF needs through HAL,
> institutional repositories and Zenodo (all 200 here); route the code lane
> through `add_repo`; and for the one question that genuinely needs ePrint
> bytes, the fixed immutable target is the Wayback snapshot the availability
> API already named (OBJ-5).

That is a closure. "Two of three questions came back unconfident" is not one —
it is a report about this session's network, and if it appears in a summary it
should be phrased in those terms.

### Constraints attached to `pass_with_constraints`

1. **OBJ-1 is binding.** The Q3 "not commensurable / transfers nothing"
   argument may not be carried forward in any downstream record. It requires a
   superseding correction (never an overwrite — AGENTS rule 2) naming
   Ducas–Pulles Fig. 3 and Fig. 5.
2. **No novelty statement** — in either direction — may cite this package,
   per OBJ-9. If one is made anyway, my verdict converts to
   `blocking_objections`.
3. **Q1 may not raise `KN-FIND-016` above `provisional`** (OBJ-4), and its
   proposition must be restated per OBJ-5.
4. **Observation 6 must be re-scoped** to KN-FIND-016's PDF source (OBJ-3).
5. **`1802` / `−35.70` may not be cited as evidence about the paper** (OBJ-8).
6. Any deliverable built on this package must carry `dominated_by` and
   `sota_delta` (OBJ-9).

---

## 12. The single cheapest check that falsifies the batch headline

**One zero-network `pypdf` extraction of the `Fig. 3` caption, its legend block,
and the `Fig. 5` caption from the already-retrieved, already-hashed CWI copy of
Ducas–Pulles (`sha256 947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e`).**

No network. No new source. No new permission. The bytes are already in the
package's provenance record and I re-fetched them to confirm the hash.

That one command converts

> "no retrieved source reports the quantity; Ducas–Pulles' `T` is a sample
> count, not a score threshold, so it is not commensurable and transfers
> nothing"

into

> "a retrieved source plots the wrong-target score survival function against
> its heuristic prediction, on a score axis, at 2^45 samples — roughly 9.4 bits
> deeper than Carrier's 2^35.70 — and plots the good-target distribution on the
> same axis in the adjacent figure. The residual is an instantiation gap for
> the polar-code score function, not a measurement-type gap."

Everything else in this report is a constraint on how the package may be used.
That is the one thing that changes what it says.

---

## 13. Narrowest supported statement

> Against the authors' own HAL deposit of the 2025-06-11 build of ePrint
> 2022/1750 (`sha256 083b1422…`, byte-identical to what HAL served on
> 2026-08-02, HAL `version_i: 1`), the Table C.2 `CN/Kyber-512`
> `log2(Tsample)` cell reads `143.30`, and ePrint's landing page records no
> revision after 2025-06-11. The identity of that deposit with the bytes ePrint
> serves is inferred, not verified. Nothing was retrieved bearing on
> `kevin-carrier/CodedDualAttack` at any commit. No retrieved source reports
> `Pwrong` for Carrier's polar-code score function at the aligned `Pgood`
> threshold; the analogous measurement for the neighbouring MATZOV/LW21
> dual-sieve **is** reported by Ducas–Pulles (CRYPTO 2023, Fig. 3 and Fig. 5),
> at greater sampling depth, and closes neither the extrapolation to Kyber
> scale nor the residual for Carrier's score function.

Estimate/table tier. No ML-KEM break claim. No crypto-scale claim. No promotion
or closure of any hypothesis, finding, or open problem.
