# TASK-20260802-104 — Red-team objections to the BATCH-007 source adjudication

- Report id: `RT-20260802-3a440d`
- Goal `GOAL-MLKEM-003` · Batch `BATCH-007` · Package under review: snapshot commit
  `38cc4402087bae7578472d03dffda61764d1d3bf` (producer task `TASK-20260802-101`)
- Role: red-team · independent session · did not produce the package · edited no
  producer artifact, no ledger record, no `experiments/` path, and made no commit
- Requested policy `review-adversarial`, `reasoning_effort: xhigh`,
  `independent_session_required: true`; resolved model `claude-opus-5`;
  `fallback_used: true`
- **Verdict: `blocking_objections`** (one of three verdicts is falsified by
  retrievable primary evidence; two carry label overclaims). Nothing below is a
  claim about the security of ML-KEM, and nothing below asserts an ML-KEM break.

---

## 0. What I re-derived myself, with provenance

Everything I fetched, in retrieval order. All on 2026-08-02 UTC.

| # | url | http | retrieved_at (UTC) | bytes | sha256 | status |
|---|---|---|---|---|---|---|
| R1 | `https://eprint.iacr.org/2022/1750.pdf` | 403 | 2026-08-02T17:45:15Z–17:45:17Z | 5381 | `aa340c87cd39d440e3e874af2462d3b6dc7d254e10d9882a666a5fabcaee57a9` | **unretrieved** — Cloudflare `Just a moment...` interstitial, not solved |
| R2 | `https://eprint.iacr.org/2023/302.pdf` | 403 | 2026-08-02T17:45:15Z–17:45:17Z | 5378 | `240044d763f4ccc293ff4913b9afea0857dec011e10ad9e9e5322b69c47567c0` | **unretrieved** — same interstitial |
| R3 | `https://eprint.iacr.org/archive/versions/2022/1750` | 403 | 2026-08-02T17:45:15Z–17:45:17Z | 5441 | `9908799f9206621a9d7dc712965720d6abe3a3ad69a6761c0b0c0cd40f671b03` | **unretrieved** — same interstitial |
| R4 | `https://hal.science/hal-05406481v1/file/2022-1750.pdf` | 200 | 2026-08-02T17:45:34Z–17:45:40Z | 1252838 | `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` | **retrieved**, `application/pdf` |
| R5 | `https://inria.hal.science/hal-05406481/file/2022-1750.pdf` | 200 | 2026-08-02T17:45:34Z–17:45:40Z | 1252838 | `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` | **retrieved**, `application/pdf` |
| R6 | `https://hal.science/hal-05406481/document` | 200 | 2026-08-02T17:45:34Z–17:45:40Z | 1252838 | `083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` | **retrieved**, `application/pdf` (re-fetched once more for text extraction; identical sha256) |
| R7 | `https://api.openalex.org/works?filter=title.search:Does%20the%20Dual-Sieve%20Attack%20on%20Learning%20with%20Errors%20even%20Work` | 200 | 2026-08-02T17:46:53Z | 13824 | `67a4f75b3e0d31bc56c52db882cb0a03249f6de4703a8072018583e96027bbd5` | retrieved |
| R8 | `https://api.openalex.org/works/doi:10.1007/978-3-030-92068-5_2` | 200 | 2026-08-02T17:46:53Z–17:47:09Z | 14933 | `90d35bafbd3fec58dbb57d9c4beaa2bf2a885126374a99e630ef3758c119cdc2` | retrieved |
| R9 | `https://ir.cwi.nl/pub/33407` | 200 | 2026-08-02T17:47:09Z–17:47:11Z | 23524 | `e23603497e2ea34de3663ccdeb9c2a0d0472b077501643b6e1545507a264644f` | retrieved |
| R10 | `https://lup.lub.lu.se/record/292b3d98-754c-414d-95db-ee38806157f9` | 200 | 2026-08-02T17:47:09Z–17:47:11Z | 46819 | `738f31b520f15fe3199228603dd7c02a5ed79a9222a5e0933f760f11370ff483` | retrieved (no full-text link exposed) |
| R11 | `https://ir.cwi.nl/pub/33407/33407.pdf` | 200 | 2026-08-02T17:47:18Z–17:47:20Z | 1021750 | `947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e` | **retrieved**, `application/pdf`, 36 pages, `/CreationDate D:20230228174928+01'00'` |
| R12 | `git ls-remote https://github.com/ludopulles/DoesDualSieveWork` | exit 0 | 2026-08-02T17:49:13Z | — | `HEAD = refs/heads/main = f390d77b21d40d711add90791fbe86d2c695ce35` | retrieved |
| R13 | `https://raw.githubusercontent.com/ludopulles/DoesDualSieveWork/main/data/{unif,bdd}_scores_n{40,50,60,70,80,90}.csv` | 200 ×12 | 2026-08-02T17:49:24Z (loop start; no end stamp recorded) | 5110/22369, 6380/22637, 14839/22991, 20868/22977, 43961/23251, 80027/23345 | see `red_team_report.yaml` `own_retrievals` | **retrieved** |

Two earlier `raw.githubusercontent.com` probes returned HTTP 200 but were lost to
a local write error (`curl: (23)`, target path was a directory). They are
superseded by R13 and are recorded here rather than omitted.

I recomputed the following from bytes only. No number below is recalled.

---

## 1. The two headline objections

### O1 — Q3's answer is false, and the falsifier was three cheap hops away

Q3 answers, verbatim in `adjudication_results.json`:

> "No. No retrieved source reports a MEASURED Pwrong at or near the aligned Pgood
> ~ 1/2 operating threshold."

The producer names the source most likely to contradict this — Ducas–Pulles,
ePrint 2023/302 — and records it as unretrieved after **two** attempts, both
against `eprint.iacr.org`.

I retrieved it in three hops from information the producer already had in its own
toolkit: OpenAlex (R7) → CWI institutional repository landing (R9) → PDF (R11).
Elapsed: about eleven seconds. The paper's own §1.1 names its data repository,
`https://github.com/ludopulles/DoesDualSieveWork`, whose auxiliary CSVs I then
fetched (R12, R13).

That data is the measurement KN-OPEN-016's residual names, literally and in the
same units. In `data/bdd_scores_nX.csv` the column `cdf_real` is the measured CDF
of the score of a **BDD (correct) target**; the score at which it first reaches
0.5 *is* the operating threshold `T` in Carrier's own convention ("we select `T`
… ensuring that `Pgood ≈ 1/2`", vendored extract
`extracts/carrier-hal-05406481/page27_threshold_choice.txt`). In
`data/unif_scores_nX.csv` the column `log2_sf_real` is the measured log₂ survival
function of the score of a **uniform (wrong) target** — that is, measured
`log2(Pwrong)` at each score. Both files at a given `n` carry the **same** `N`
(number of dual vectors) in their metadata rows, so the two measurements are on a
common score scale with no `k_fft`-style rescaling needed.

Reading measured `log2(Pwrong)` at the measured `Pgood = 1/2` threshold:

| n | N (same in both files) | T at `Pgood = 1/2` | first measured uniform score ≥ T | measured `log2(Pwrong)` there | model prediction there | top of measured uniform support |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | 284 | 29.43 | 30.00 | **−7.301** | −7.403 | 120.56 = 4.10 × T |
| 50 | 1196 | 76.59 | 77.00 | **−10.135** | −10.252 | 283.85 = 3.71 × T |
| 60 | 5040 | 198.21 | 199.00 | **−14.655** | −14.729 | 465.99 = 2.35 × T |
| 70 | 21238 | 515.87 | 516.00 | **−21.712** | −21.789 | 1003.37 = 1.94 × T |
| 80 | 89494 | 1345.29 | 1346.00 | **−33.151** | −33.235 | 1958.43 = 1.46 × T |
| 90 | 377126 | 3521.49 | 3655.21 | **−46.415** | −55.530 | 3916.47 = 1.11 × T |

The measured wrong-target survival function covers the good-target median at
every dimension, and continues past it by factors 1.11× to 4.10×. At n = 90 the
measured value exceeds the model prediction by **9.1 bits** at the first grid
point above the threshold — this is the "waterfall-floor" the abstract advertises,
landing precisely in the threshold region, and in the direction that *increases*
`Pwrong`. (At n = 90 the tail grid is sparse, so `−46.415` is measured slightly
above T; because a survival function is non-increasing, measured
`log2(Pwrong)` at T is ≥ −46.415. The bracket is what matters.)

So the residual measurement is not absent from the literature. Q3's verdict is
correct only under the scope fence the producer added — "over the sources
actually retrieved in this task" — and that fence does not make the verdict true,
it makes it **unfalsifiable**. Under `docs/inventor-protocol.md` §4, a
negative-existence result whose scope is "the sources I happened to retrieve" is
a fatigue report about the search, not a statement about the problem, and its
honest status is `unverified`.

**Steelman, and the narrowing the producer should have written.** Ducas–Pulles
measure the MATZOV/Dual-Sieve-FFT score of [LW21, GJ21, MAT22] as reconstructed in
their §2.3, *not* Carrier's polar-coded score under Approximation 4.9, and they do
it at n = 40…90, which is toy scale against Kyber's β ≈ 384–816 (AGENTS rule 7).
So this does **not** settle whether *Carrier's* `Pwrong` has been measured at
*Carrier's* threshold. The defect is that Q3 never states which of these two
questions it is asking, and the two have different answers. As asked, the answer
is *yes, at toy dimensions, for the dual-sieve score*; as the producer's evidence
supports, the answer is *no, for Carrier's polar-coded score at Carrier's Fig 4.1
parameters*. The batch must carry the second, explicitly narrowed, and must
record the first as counter-evidence.

**Cheapest check:** `curl -sL https://raw.githubusercontent.com/ludopulles/DoesDualSieveWork/main/data/bdd_scores_n90.csv`
and `.../unif_scores_n90.csv` (23 345 + 80 027 bytes); take the first `score`
whose `cdf_real ≥ 0.5` (3521.49) and read `log2_sf_real` at the first uniform
`score ≥` it (3655.21 → −46.415).

---

### O2 — The batch endorses a statistic that is exactly a counting-resolution floor

This is the "ask what the reported quantity should have done" test
(`docs/inventor-protocol.md` §3), applied to the single number the batch
reproduces most proudly.

`source_adjudication.md` §"Reproduction check" reports, as agreement with
EV-MLKEM-011: last `T` with `Pwrong > 0` = 1802, `log2(Pwrong)` there = −35.7045.
The archived file header
(`inputs/MLKEM-DUAL-SOURCES-20260802/extracts/codeddualattack/Pwrong_q241_m40_n43_nfft8_kfft3_nlat35_beta032_beta144_N25971.out.header.txt`)
gives `q = 241`, `k_fft = 3`, `nb_iteration = 4000`, and states that line *i* is
`P(F ≥ i)` for a uniform target. The FFT scores all `q^{k_fft}` candidates per
iteration, so the experiment scores

    nb_iteration · q^{k_fft} = 4000 · 241³ = 55 990 084 000 = 2^35.7045

candidates in total, and the smallest non-zero empirical probability it can
represent is one count in that many, i.e. `log2 = −35.7045`.

**The recorded floor equals the resolution limit to four decimal places.** And it
is not a coincidence of one file — all three archived `Pwrong` files terminate at
their own resolution limit:

| file (`nb_iteration`) | `nb·q^{k_fft}` | resolution floor `−log2` | recorded last-positive `log2(Pwrong)` | Δ (bits) |
|---|---:|---:|---:|---:|
| `…nlat35_beta032_beta144_N25971` (4000) | 2^35.7045 | −35.7045 | −35.7045 | 0.0000 |
| `…nlat35_beta037_beta144_N200001` (1) | 2^23.7387 | −23.7387 | −23.74 | 0.0013 |
| `…n50_nlat42_beta035_beta141_N25970` (6000) | 2^36.2894 | −36.2894 | −36.29 | 0.0006 |

Consequence: the endpoint of the measured `Pwrong` support — and therefore the
program's "`fraction_inside = 0`" and "aligned `T`-gap ≈ 421" statistics that
KN-FIND-012 and KN-FIND-014 headline and that BATCH-007 re-endorses — is set by
the authors' **sample budget**, not by the score distribution. The parameter that
is supposed to destroy the gap is `nb_iteration`; it was never varied, and the
identical measurement was never run against a matched-budget control. A quantity
that terminates exactly at 1/(sample count) is a measurement artifact tell.

This does *not* show the coverage gap is spurious. It shows the gap is
**confounded** and that the standing records state it in a form that invites the
wrong reading ("the empirical pillar does not cover the threshold regime" reads
as a property of the analysis; it is at least partly a property of the run
length). Ducas–Pulles is the existence proof that the control is runnable: same
score function, uniform-target survival measured down to 2^−44…2^−48 by FFT-bucketed
enumeration, and at that budget the wrong-target support *does* cover the
good-target median at every dimension tested.

**Cheapest check:** one line — `python3 -c "import math; print(-math.log2(4000*241**3))"`
→ `-35.70450…`, against EV-MLKEM-011's recorded `−35.70` and the batch's
recomputed `−35.7045`. Zero network. Bytes already in the repository.

---

## 2. Q1 — the Table C.2 cell

### O3 — The program is treating a self-correcting appendix typo as a finding

The brief asks whether the program is mistaking a typo for a defect, and whether
Table C.2's other columns or Table 5.1 constrain the cell arithmetically. They
do, twice over. I recomputed both from the vendored extract
`extracts/carrier-hal-05406481/page37_tables_C1_C2.txt` (no external data, no
pickle):

1. **Theorem 4.1 constrains it.** `T = Tsample + R·(N·Tdec + TFFT)` applied to
   the printed Table C.2 rows reproduces Table 5.1 to ≤ 0.05 bits for **8 of 9**
   rows (C0: 121.82 / 173.02 / 238.99; CC: 139.53 / 195.10 / 259.65; CN-768:
   189.80; CN-1024: 254.63). The ninth, CN/Kyber-512, gives 143.30 against Table
   5.1's 134.5. Substituting `log2(Tsample) = 134.30` gives **134.52**. The
   corrected value is *forced* by the paper's own two tables; nothing outside the
   PDF is needed to detect it or to repair it.
2. **The ε column independently vindicates the rest of the row.** With
   `ε = R · q^{k_fft} · Pwrong`, `q = 3329`, and `k_fft` read from Table C.1, the
   printed `log2(ε)` reproduces for **all nine rows** to ≤ 0.01 bits (CN/Kyber-512:
   `7.71 + 9·11.7009 − 120.51 = −7.492` vs printed `−7.49`). So `Pwrong` and `R`
   in the CN/Kyber-512 row are internally consistent; `Tsample` is the sole
   outlier in the entire table.

Therefore: the slip is *detectable, correctable, and demonstrably non-propagating
from the published document alone*. It cannot reach any headline number, because
Table 5.1 already carries the corrected total. Under
`docs/target-result-profile.md` this is a proofreading observation, not a
cost-model or heuristic finding, and KN-FIND-016's item 3 should be recorded as
exactly that. Its persistence in the current revision carries no information
about the analysis and should not be given equal billing with Q2 and Q3 in the
batch's headline.

**Cheapest check:** the recomputation above, from
`extracts/carrier-hal-05406481/page37_tables_C1_C2.txt` and
`experiments/EXP-MLKEM-010/runs/RUN-MLKEM-010-001/theorem41_recompute.json`
(whose nine `recomputed_log2` values I reproduce exactly).

### O4 — DEC-20260802-002 overstated Q1's falsification value, and the batch inherited it

The authorizing decision justifies the whole batch with:

> "If the Table C.2 transcription error is already corrected by the authors,
> KN-FIND-016 is a finding about a superseded document and the program should
> know that before spending a batch on G6K."

That is not true of KN-FIND-016, only of one of its three items. Items 1 and 2 —
Table 5.1 matches `optimized_withExperimentalPolar.pkl` for all nine cells within
0.05 bits, and the abstract's 3.5 / 11.9 / 12.3-bit shortfalls are the CC column —
rest on the pickle and on Theorem 4.1, and are entirely unaffected by whether the
authors fixed a printed digit. The cheap-falsification-before-expensive-measurement
ordering was the right call; the specific falsification target chosen for it could
not have falsified what the decision said it would.

**Cheapest check:** `ledger/decisions/DEC-20260802-002.yaml`
`why_this_is_not_the_paused_next_action`, read against `knowledge/findings/KN-FIND-016.md`
"What is established", items 1–3.

### O5 — Identification-chain item (6) is inert and should be struck, not counted

The sixth link in Q1's chain is the ePrint landing-page note *"This version of the
paper differs only in the title"*, glossed as "consistent with no numerical change
in the last revision". The ePrint `Note:` field is free-form author text with no
date and no stated referent; it is overwritten at each revision, so nothing in the
retrieved bytes says which pair of versions it compares. Under the competing and
at least equally natural reading — "this ePrint version differs from the published
version only in the title" — the note is vacuous here, because I checked and the
three titles are the same string: ePrint `<title>` and OAI `<dc:title>`
= "Assessing the Impact of a Variant of MATZOV's Dual Attack on Kyber"; the HAL
PDF `/Title` is the same; Springer's JSON-LD `headline` is the same modulo a
typographic apostrophe.

This is a small point with a specific cost: presenting six links where three carry
the argument inflates the apparent strength of a metadata chain the producer
itself flags as not a byte comparison. Links (1)–(3) are sound and sufficient for
what they establish; (6) should be removed.

**Cheapest check:** `inputs/MLKEM-DUAL-SOURCES-20260802/eprint-2022-1750/landing.html`
(the `<strong>Note:</strong>` block), `oai_getrecord.xml` `<dc:title>`,
`springer_landing.html` JSON-LD `headline`, and
`extracts/carrier-hal-05406481/pdf_metadata.json` `/Title`.

### O6 — "HAL unretrieved" was a client artifact, and the `/CreationDate` gloss is falsified

The producer records the HAL file as unretrieved (Anubis proof-of-work
interstitial) and uses that, with the ePrint 403, to explain why no byte
comparison was possible. I fetched the same file at three URLs with plain `curl`
(R4, R5, R6): HTTP 200, `application/pdf`, 1 252 838 bytes, sha256
`083b142256eecaebfa72dfccf847151b2175666a3979cef4e7383376757b8005` — **byte-identical
to the program's vendor-lock artifact**
`experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`
(`cmp` clean). From those fresh bytes I extracted PDF page 37 and confirmed the
Q1 locus independently: the `CN: Kyber-512` row reads
`−120.51 7.71 143.30 117.91 124.00 0.71 −7.49`, `143.30` occurs once on the page
and once in the whole document, and `134.30` occurs zero times document-wide.

Two consequences, one favourable to the package and one not.

*Favourable, and unclaimed by the batch:* the vendor-lock artifact is now
reproducible today from the authoritative repository, not merely vendored once.
That is a genuine strengthening of Side A that the batch could have recorded and
did not.

*Unfavourable:* the adjudication's interpretive gloss that
`/CreationDate D:20260721165108+02'00'` is "HAL's cover-page stamping **at download
time**, 2026-07-21" is falsified — a download on 2026-08-02 carries the same
2026-07-21 stamp. The gloss appears inside the very argument that asks a reader to
trust embedded PDF timestamps as revision evidence, so an incorrect model of how
one of those timestamps is produced is a defect in that argument, even though it
does not change the verdict.

**Cheapest check:** `curl -sL -o /tmp/x.pdf https://hal.science/hal-05406481/document && sha256sum /tmp/x.pdf experiments/EXP-MLKEM-010/vendor-lock/Carrier-2022-1750-hal-05406481.pdf`.

### O7 — `confirmed_in_current_source` overclaims for Q1; the self-flag is honest but structurally misplaced

The brief asks whether the producer's self-flagging is adequate or cosmetic. My
judgement: **substantively honest, structurally insufficient — and now moot in a
way that makes the label worse, not better.**

The prose in `source_adjudication.md` and the `residual_uncertainty` field in
`adjudication_results.json` are unusually candid: they state the identification is
a metadata chain, name byte identity as the thing not achieved, and name the exact
GET that would settle it. That is not cosmetic. But:

- the load-bearing token that downstream automation and EV-MLKEM-017 will quote is
  `"verdict": "confirmed_in_current_source"`, and it carries no qualifier;
- the declared enum contains `indeterminate`, which is available and unused, and
  the JSON has no `verdict_basis: byte_comparison | metadata_chain` field to carry
  the distinction machine-readably (the `comparison.side_b_full_text_retrieved:
  false` flag exists but is one nesting level away from the verdict);
- **and, per O6, the byte comparison against Side A was available in this session
  at zero cost.** Doing it would not have closed the real gap — Side A is the
  vendored artifact, so re-fetching it says nothing about the ePrint-hosted bytes —
  but the producer's stated reason for the gap ("no fresh copy of the full text
  was obtained this session") was avoidable, and it is the reason the reader is
  asked to accept the metadata chain.

The honest label for Q1, against the question as posed ("does the cell still read
143.30 **in the current revision of ePrint 2022/1750**"), is
`indeterminate`, with the finding recorded as *confirmed in the only retrievable
authoritative full text, whose compile timestamp falls 6 m 32 s before the current
ePrint revision's OAI datestamp*. I now hold that full text and confirm the cell
in it; I do not hold the ePrint bytes and neither does the program.

**Cheapest check:** `adjudication_results.json` `questions[0].verdict` against
`questions[0].comparison.side_b_full_text_retrieved` and `verdict_enum`.

---

## 3. Q2 — the `k_fft` score-scale asymmetry

### O8 — Head == pin makes Q2 self-answering; the verdict reports a tautology in the vocabulary of corroboration

`git ls-remote` resolves `HEAD` and `refs/heads/main` to
`9c1367f85d26038244bc83c025d84c0b7006f2ee`, the pinned commit. The producer says
so plainly and marks `head_equals_pinned: true`. But `confirmed_in_current_source`
then conflates two epistemically different states:

- (i) *a newly retrieved authoritative source independently says the same thing* —
  corroboration; and
- (ii) *the source is the identical object already held* — zero new bits.

Q2 is case (ii). "The current head IS the pinned commit, so the asymmetry cannot
have changed" is a correct sentence and an empty confirmation: it establishes only
that the repository was not updated between 2025-04-13 and 2026-08-02. The
appropriate label is something like `unchanged_since_derivation`, which the enum
lacks. Q1 is a weaker instance of the same problem: the text adjudicated *is*
Side A.

More important is what the verdict is silently read as licensing. It confirms that
KN-FIND-014's **quoted code facts** are accurate at that commit. It does not
confirm KN-FIND-014's **interpretation** of those facts, and the producer says so:
EV-MLKEM-013's synthetic identity check (raw cosine sum equals `fftn(·).real`, with
the factor exactly `k_fft`) was not re-run. So the load-bearing step — that
dividing `Pgood` by `k_fft = 3` is the *correct* alignment, which is what converts
a raw `T`-gap of ~1262 into the reported aligned gap of 420.56 and sets the whole
Q3 comparison — remains resting on a single un-replicated 2026-07-31 run. It is
also the step whose failure would change Q3's headline number, and it was the
cheapest thing in the batch to re-run: the identity is a ten-line NumPy check.

Additional scope point the batch should carry: the asymmetry lives in
`verifyModel/ScoreExperimentalDistribution/`, a *verification-model* directory. No
retrieved artifact shows that this directory's convention is the one used to
produce Table 5.1 or Table C.2, and the producer correctly declines to claim so
("Confirming the asymmetry in the code says nothing about whether it affects the
paper's published analysis"). That non-claim must survive into EV-MLKEM-017 rather
than being dropped in synthesis.

**Cheapest check:** re-run the EV-MLKEM-013 identity on
`experiments/EXP-MLKEM-013/vendor-lock/FFT_sample.py` (sha256
`2a5f3dedceb68b0836efc92f0b58294ce4193a9553493e7c0d4e4ce67b922531`): build a small
random `T`, compare `sum cos(...)` from `Score_Function.compute_score` against
`numpy.fft.fftn(T).real`, and confirm the ratio is exactly `k_fft`.

---

## 4. Retrieval asymmetry, closure standard, and the security inference

### O9 — Retrieval effort was allocated inversely to falsification value

Counted from `inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json` (25 `attempts`
+ 3 `addendum_attempts` = 28 records) plus the `code_repository` block:

- Carrier / ePrint 2022/1750 (the **confirming** side of Q1): ~17 attempts across
  eight hosts — `eprint.iacr.org`, `hal.science`, `api.archives-ouvertes.fr`,
  `api.openalex.org`, `api.semanticscholar.org`, `link.springer.com`,
  `web.archive.org`, plus the local baseline.
- `kevin-carrier/CodedDualAttack` (the **confirming** side of Q2): five routes
  (REST, web, codeload, `raw.githubusercontent.com`, git smart-HTTP), of which the
  fifth succeeded.
- Ducas–Pulles ePrint 2023/302 (the source the producer itself designates as
  **most likely to falsify Q3**): **two** attempts, one host, no OpenAlex query —
  even though OpenAlex was already used twice in the same session for other
  sources, and one OpenAlex call returns the CWI location that serves the PDF.
- Guo–Johansson: OpenAlex was queried and reported `is_oa: false`; the producer
  stopped there. I confirm OpenAlex reports no OA location (R8) and that the Lund
  record page (R10) exposes no full-text link — so for this source the negative
  stands on the evidence I could gather too.

The producer used ~1260 s of a granted 3000 s (`receipt.json` `budget.used`). This
was not a budget-forced omission. Under AGENTS rule 9 and
`docs/inventor-protocol.md` §3, a negative-existence verdict must spend at least as
much retrieval effort on the source that could refute it as on the sources that
confirm it. Here the ratio is roughly 8:1 the wrong way.

I record no view about intent. The auditable fact is the effort allocation and its
consequence, which O1 demonstrates.

**Cheapest check:** `provenance.json` `attempts[13]`, `attempts[14]` (the only two
Ducas–Pulles records) against the `code_repository` block and `receipt.json`
`budget.used.wall_clock_seconds_approx`.

### O10 — If any part of this batch reads as "the residual is dead", it needs a named obstruction

`docs/inventor-protocol.md` §4 applies to this batch's own output. As written, the
Q3 verdict plus KN-OPEN-016's "Residual open piece" reads as *the measurement
nobody has* — a statement about the search. The obstruction is nameable now, and
it is not "nobody has measured this":

> **Named obstruction.** Carrier's archived `verifyModel` outputs cannot exhibit
> `Pwrong` at the aligned `Pgood ≈ 1/2` threshold because each file's support
> terminates exactly at its counting-resolution floor `1/(nb_iteration · q^{k_fft})`
> — 2^−35.70, 2^−23.74, 2^−36.29 for the three archived files (O2) — while the
> aligned `Pgood` minimum for the only doubly-instrumented parameter set sits at
> score 2222.56, some 420.56 units beyond where that budget expires. The gap is a
> sample-budget boundary, not a measured absence of mass. Independently, for the
> *non-polar* Dual-Sieve-FFT score, the measurement does exist: Ducas–Pulles report
> measured `log2(Pwrong)` at the measured `Pgood = 1/2` threshold at six
> dimensions (O1), with a 9.1-bit excess over the model at n = 90.

> **Forward guidance — what remains open.** (a) Fit the measured Carrier `Pwrong`
> survival function on its measured range and extrapolate to the aligned `Pgood`
> median (2222.56) *against* Approximation 4.9's prediction at the same point. This
> costs no new compute — the `.out` files are already vendored — and converts
> "`fraction_inside = 0`" from a coverage statement into a quantitative test with a
> stated extrapolation assumption. (b) Estimate the `nb_iteration` needed to reach
> score 2222.56 at those parameters; if it is feasible, that is a cheaper route to
> the residual than the twice-blocked G6K branch. (c) Whether the Ducas–Pulles
> floor transfers to the polar-coded score is genuinely open — Carrier's abstract
> claims their analysis avoids the flawed independence assumptions, so this is a
> real question and not a rhetorical one. `unif_scores.py` in the Ducas–Pulles
> repository is the reference implementation of the FFT-bucketed enumeration that
> makes deep-tail sampling affordable.

### O11 — No security inference is licensed by any conjunction of the three verdicts

State the conjunction plainly, because the batch's own vocabulary ("erratum
survives", the `erratum` / `table-erratum` tags on KN-FIND-014 and KN-FIND-016)
invites the slide:

- **Q1 ⇒** an appendix intermediate-results table still contains one arithmetically
  self-correcting typographic cell. Not a claim about any headline number.
- **Q2 ⇒** one file in a verification-model directory of a GitHub repository has
  not changed since 2025-04-13. Not a claim about the paper's analysis.
- **Q3 ⇒** (as narrowed by O1) Carrier's own archived data does not measure
  `Pwrong` at their own operating threshold, for the reason named in O10. Not a
  claim that Approximation 4.9 is wrong, and not a claim that nobody has measured
  it.

None of the three, severally or jointly, constrains whether Carrier's Kyber cost
figures are right, and none is evidence about the security of ML-KEM in either
direction. "The erratum survives" ⇏ "the security claim is wrong": survival of a
typo in a table whose other columns already force the corrected value is
compatible with the analysis being entirely correct, and equally compatible with
it being wrong. The batch's own scope statement says this; the risk is that
EV-MLKEM-017 and DEC-20260802-003 (TASK-20260802-105 write scope) synthesize
"three confirmations" into standing for the program's critique. They must not.

**Cheapest check:** when written, `ledger/evidence/EV-MLKEM-017.yaml` fields
`direction`, `strength`, `claim_tier`, `boundaries`; and
`ledger/decisions/DEC-20260802-003.yaml` `non_claims`. If `direction: supports`
appears against any hypothesis about Carrier's cost model or ML-KEM security, this
objection has been realized.

---

## 5. Narrowest supported statement

> Against the vendored Carrier full text
> (`hal-05406481` v1, sha256 `083b1422…757b8005`, re-fetched independently on
> 2026-08-02 and byte-identical), Table C.2's `CN`/Kyber-512 `log2(Tsample)` cell
> reads `143.30`; that value is contradicted by Theorem 4.1 applied to the same
> row together with Table 5.1's `134.5`, which forces ≈ `134.30`, and no
> retrievable source shows an authors' correction. The identification of this
> text with ePrint 2022/1750 revision 3 rests on metadata, not bytes, and is
> **indeterminate** at the byte level. `kevin-carrier/CodedDualAttack` HEAD equals
> the pinned commit `9c1367f`, so KN-FIND-014's quoted code facts hold there and
> nothing about them can have changed; their interpretation was not re-derived.
> Carrier's three archived `Pwrong` files each terminate exactly at their
> counting-resolution floor, so the reported non-coverage of the aligned
> `Pgood ≈ 1/2` threshold is a sample-budget boundary; for the non-polar
> Dual-Sieve-FFT score, Ducas–Pulles do report measured `Pwrong` at the measured
> `Pgood = 1/2` threshold at n = 40…90.

Nothing here is a claim about the security of ML-KEM, and nothing here is an
ML-KEM break claim.

## 6. The cheapest single check that falsifies the batch's headline reading

**`python3 -c "import math; print(-math.log2(4000*241**3))"` → `-35.7045…`,
compared against the `−35.7045` the batch reports as reproducing EV-MLKEM-011.**

Zero network, one line, bytes already in the repository
(`extracts/codeddualattack/Pwrong_q241_…N25971.out.header.txt` supplies
`nb_iteration = 4000`, `q = 241`, `k_fft = 3`). Equality shows that the
`Pwrong` support endpoint the batch endorses — and therefore the
`fraction_inside = 0` and aligned-`T`-gap statistics resting on it — is the
experiment's counting-resolution limit rather than a property of the score
distribution, which falsifies the reading that BATCH-007's three confirmations
leave the standing findings and their residual undisturbed.

The cheapest *network* falsification, targeting Q3's verdict specifically, is
O1's two-CSV check (≈ 103 KB, seconds).
