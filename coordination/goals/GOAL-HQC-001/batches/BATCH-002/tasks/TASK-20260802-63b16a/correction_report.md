# Correction report — TASK-20260802-63b16a

**Goal**: `GOAL-HQC-001` · **Batch**: `BATCH-002` · **Role**: executor
**Question**: `RQ-HQC-001` · **Produced**: 2026-08-02
**Repo commit at start**: `7f8a78d47bd35298cd140838381872d65bb2c0f1`, clean tree
(`git status --porcelain` empty; only `git rev-parse` / `git status` were run — no
state-mutating git command).

**Supersedes on the points below** (never edits):
`coordination/goals/GOAL-HQC-001/batches/BATCH-001/tasks/TASK-20260802-6344ed/dfr_model_transcription.md`
§2 and anomaly X6, and
`.../proposed_kn_lit_entries.md` PROP-S1. Those artifacts are snapshot-committed and
immutable; nothing under `BATCH-001/` was read-modified by this task.

**The Coordinator files `CORR-20260802-3ae664` from this report.** This report makes
no state transition and files no ledger record.

---

## 0. Headline, stated before the detail

**The numeric correction stands and is unchanged: RS-S3's minimum distance is 59, not
49.** Three independent derivations, all internal to the primary specification, force
it; two of them are the ones the handoff named and both survive scrutiny; a third was
found during verification.

**The attribution in the correction's own framing does not stand.** BATCH-002-OPENING
§3 states that `[90, 32, 49]` "is the **transcription's own** error", and red-team
objection O1 hypothesised "a `5`→`4` digit misread from a `2.6×`-scale page clip". I
tested that hypothesis directly and **it is false**. The published PDF displays `49`.
`TASK-20260802-6344ed` transcribed the source faithfully, and X6's first half is a
**genuine source anomaly**, exactly as that task classified it.

So the correction that BATCH-002 must carry is not "the transcription misread the
specification". It is: **the published specification prints a minimum distance for
RS-S3 that contradicts its own definition, its own Table 3, and its own generator
polynomial, and the value its decoder actually uses is 59.** The consequence for a
downstream re-derivation is identical either way; the record of who erred is not, and
a `CORR` record that says the transcription erred would itself be wrong.

I am recording this rather than executing the framing I was given, per AGENTS.md
rule 9 and the executor contract's "record, never discard". **The disposition is the
Coordinator's; this report only measures.**

---

## 1. Method and independence

Nothing below is taken from the handoff, the transcription, or either BATCH-001
review. Every number was read off a copy of the specification that this session
downloaded itself.

| step | detail |
|---|---|
| Re-acquisition | `curl -sS -L --max-time 180 https://pqc-hqc.org/doc/hqc_specifications_2025_08_22.pdf` |
| Bytes | 876 126 |
| sha256 | `174186cb5fdc0108aad914391360c222f52ea533bfb406146fac124b3a25406d` — **byte-identical** to the value recorded by `TASK-20260802-6344ed` and re-confirmed by `TASK-20260802-b8d69f`. Third independent fetch, same hash. |
| Metadata | PDF 1.5, 51 pp., producer pdfTeX-1.40.26, creationDate `D:20250822133716Z` |
| Toolchain | PyMuPDF 1.28.0 (MuPDF 1.29.0), Python 3.11 |
| Two channels | (a) `page.get_text("text")` — the PDF's own character codes, immune to visual misreading; (b) page rendering at **6×** (BATCH-001 used 2.6×) and reading the image |
| RMRS | `https://arxiv.org/pdf/2005.10741`, 525 223 B, sha256 `cbb7dbd670f27cdcf602438018df52745c0af495050aedb3b83a0b00986f5446` — byte-identical to the recorded value |
| Storage | Session scratchpad only. **No third-party PDF is committed.** |

Both channels were used because they fail differently: a rendering can be misread by
eye, and a text layer can be mangled by extraction. Agreement between them is what
makes the finding in §2.3 decisive.

---

## 2. Correction 1 — RS-S3 minimum distance

### 2.1 What the primary text actually says

SPEC §3.4.2, printed p.17 (text layer, verbatim):

> Let p be a prime number and q is any power of p. Following [24], a Reed-Solomon code
> RS[n, k, d_min] with symbols in F_q has the following parameters:
> • Block length n = q − 1 ;
> • Number of parity-check digits n − k = 2δ, with δ, the correcting capacity of the
>   code and k the number of information bits ;
> • Minimum distance d_min = 2δ + 1.

> Shortened Reed-Solomon codes used in HQC. Depending on HQC parameters, we construct
> shortened Reed-Solomon (RS-S1, RS-S2 and RS-S3) codes such that k is equal to 16, 24
> or 32 from the following RS codes RS-1, RS-2 and RS-3 from [24]. The shortened codes
> are obtained by subtracting 209 from the parameters n and k of the code RS-1,
> subtracting 199 from the parameters n and k of the code RS-2 and by subtracting 165
> from the parameters n and k of the code RS-3.

SPEC §3.4.2, printed p.18 (both channels, **6× render below**):

> • RS-S1[46 = 255 − 209, 16 = 225 − 209, 31] ;
> • RS-S2[56 = 255 − 199, 24 = 223 − 199, 33] ;
> • RS-S3[90 = 255 − 165, 32 = 197 − 165, 49].
>
> One should note that shortening the Reed-Solomon code does not affect its error
> correcting capacity.

SPEC Table 3, printed p.18 (6× render):

| Code | n | k | δ |
|---|---|---|---|
| RS-1 | 255 | 225 | 15 |
| RS-2 | 255 | 223 | 16 |
| RS-3 | 255 | 197 | 29 |
| RS-S1 | 46 | 16 | 15 |
| RS-S2 | 56 | 24 | 16 |
| RS-S3 | 90 | 32 | **29** |

### 2.2 Route (i) — MDS / Singleton. **APPLIES.** Twice over.

The handoff flagged a caveat: the specification uses *shortened* Reed-Solomon codes,
and asked me to check whether MDS-ness survives rather than assume it. It does, and
for a stronger reason than general coding theory.

**(i-a) The specification states the relation itself, so no external theory is
needed.** §3.4.2's own two bullets are `n − k = 2δ` and `d_min = 2δ + 1`. Eliminating
δ gives, for every code in the family the specification says it uses,

```
d_min = (n − k) + 1
```

That *is* the MDS/Singleton equality, asserted by the source about its own
construction. Applying it to the printed (n, k):

| code | n − k + 1 | printed d |
|---|---|---|
| RS-S1 | 46 − 16 + 1 = **31** | 31 ✓ |
| RS-S2 | 56 − 24 + 1 = **33** | 33 ✓ |
| **RS-S3** | 90 − 32 + 1 = **59** | **49 ✗** |

**(i-b) The construction described is shortening, not puncturing, and that is
checkable rather than assumed.** The general fact is that shortening an MDS
[n, k, d] code yields [n−1, k−1, d] — n and k drop together, d is unchanged, MDS-ness
survives — whereas puncturing yields [n−1, k, d−1] and destroys the value of d. Which
operation applies is decided by the text, not by the name: §3.4.2 says the codes are
"obtained by subtracting 209 from the parameters n **and** k", i.e. the **same
amount from both**. That is shortening. Confirmed on the arithmetic of all three
rows: RS-1 (255, 225) − 209 → (46, 16); RS-2 (255, 223) − 199 → (56, 24); RS-3
(255, 197) − 165 → (90, 32). Since n − k is invariant under this operation, `n−k+1`
is invariant, and the mother codes are already MDS by (i-a): RS-3 has
255 − 197 + 1 = 59 = 2·29 + 1 ✓.

The specification also asserts the preservation directly — "shortening the
Reed-Solomon code does not affect its error correcting capacity" — which is the δ-form
of the same statement.

**Route (i) verdict: SURVIVES, on the specification's own stated definitions plus a
checked identification of the operation as shortening. It does not depend on
importing MDS theory from outside the document.**

### 2.3 Route (ii) — the transcribed δ. **APPLIES.**

Table 3 gives δ = 29 for RS-S3 (and 29 for its mother code RS-3). §3.4.2's third
bullet gives `d_min = 2δ + 1`. Hence

```
d = 2 · 29 + 1 = 59
```

Cross-checked on the siblings: δ = 15 → 31 ✓ (printed 31); δ = 16 → 33 ✓ (printed
33). The δ value was read by me from a **6× rendering** of Table 3, not taken from the
BATCH-001 transcription.

**Route (ii) verdict: SURVIVES.**

### 2.4 Route (iii) — a third derivation, found during verification

Not named in the handoff. SPEC §3.4.2 prints the generator polynomials of RS-S1,
RS-S2 and RS-S3 in full, and states they "are identical to the generator polynomials
of Reed-Solomon codes RS-1, RS-2 and RS-3 respectively". For a Reed-Solomon code the
generator has degree n − k = 2δ. Reading the highest printed term:

| polynomial | highest term | degree | ⇒ δ | ⇒ d = 2δ+1 |
|---|---|---|---|---|
| g₁(x) (RS-S1) | `+ x³⁰` | 30 = 46 − 16 | 15 | 31 ✓ |
| g₂(x) (RS-S2) | `+ x³²` | 32 = 56 − 24 | 16 | 33 ✓ |
| **g₃(x) (RS-S3)** | `+ x⁵⁸` | **58 = 90 − 32** | **29** | **59** |

The specification also writes the generator as `g(x) = (x + α)(x + α²)···(x + α^{2δ})`
— degree 2δ by construction. So the printed 58-degree polynomial is a third,
independent, purely textual witness that δ_e = 29 for RS-S3.

**Three routes, three agreements on 59, and all three agree with the printed value on
both sibling rows.** The `49` is isolated to a single bracket.

### 2.5 The attribution test — and the finding that reverses it

The claim under test: `49` is an extraction artefact introduced by
`TASK-20260802-6344ed`'s 2.6× page clip.

**Test 1 — PDF text layer.** `page.get_text("text")` on printed p.18 returns, in the
PDF's own character codes:

```
• RS-S3[90 = 255 −165, 32 = 197 −165, 49].
```

A text-layer read cannot make a visual `5`/`4` confusion; it reports the glyph codes
the file contains. It says `49`.

**Test 2 — 6× rendering**, more than twice BATCH-001's scale. The rendered bullet
reads `RS-S3[90 = 255 − 165, 32 = 197 − 165, 49].` The digit is unambiguous at that
scale and the two sibling bullets render `31` and `33` in the same font at the same
size.

**Both channels agree. The published specification prints 49.**

**Consequence for the correction's framing.** BATCH-002-OPENING §3's sentence "It is
the **transcription's own** error", `DEC-20260802-344883` D-2's phrasing, and red-team
O1's misread hypothesis are **not supported**. `TASK-20260802-6344ed` recorded the
source faithfully, recorded Table 3's δ = 29 beside it, and classified the pair as
anomaly X6, an observation of the source document. **That classification was correct**,
and the completion-gate row it was said to violate ("every damaged formula rendering
is marked EXTRACTION-DAMAGED") was not violated: the rendering was not damaged.

What BATCH-001 *did* omit is the arithmetic — it recorded that the two printed values
disagree without deriving which one the rest of the document forces. That omission is
real, it is what the red team's O3 objects to in general terms, and it is what this
report closes. It is a different defect from the one the correction was framed around.

### 2.6 A supported hypothesis about the source's error — recorded at its own strength

Not required by the handoff; recorded because it is cheap, it corroborates §2.5, and
withholding it would leave the reader without the most parsimonious explanation.

RMRS (`arXiv:2005.10741`, the specification's reference [4]) Figure 6 gives the 2020
HQC-RMRS parameter sets, whose external Reed-Solomon codes are:

```
HQC-RMRS-128 : [80, 32, 49]        (49 = 80 − 32 + 1, correct for n = 80)
HQC-RMRS-192 : [76, 32, 45]
HQC-RMRS-256 : [78, 32, 47]
```

The numeral `49` is exactly the minimum distance of RMRS's first external code, whose
length is 80. The specification's RS-S3 has length 90. **This is consistent with an
unrevised carry-over of a value from the 2020 paper when the length changed**, and it
independently explains why `49` would be present in the source rather than introduced
in transcription.

**Status of this paragraph: a hypothesis supported by a numeral coincidence and a
shared lineage, not an established fact.** I did not and cannot establish the
document's edit history. It is recorded as a lead, and no downstream record should
cite it as more.

### 2.7 What the corrected value is worth

`δ_e` is the summation lower limit of Theorem 6.1. The red-team report
`TASK-20260802-73a352` §O1 computed, from the transcribed model at NIST-5 with
p_i = 2^{−11.321} and n_e = 90:

```
d_e = 59 → δ_e = 29 :  DFR ≤ 2^-260.51   (clears the 2^-256 design target)
d_e = 49 → δ_e = 24 :  DFR ≤ 2^-209.77   (misses it by ~46 bits)
```

**Those two figures are the red team's, relayed, not recomputed by this task.** This
task ran no arithmetic on Theorem 6.1 and makes no statement about whether any HQC
parameter set meets its DFR target. What this task establishes is only which value of
d_e the specification's own definitions force: **59**.

### 2.8 How the corrected value is carried into the corpus

`KN-LIT-b9e1a8` "Published-text inconsistencies" item 1 records: the printed bracket
verbatim (`49`), Table 3's δ = 29, all three derivations giving 59, the sibling-row
agreement, and the statement that the value implied for Theorem 6.1 is
**d_e = 59**. It does not silently substitute 59 for the printed value — that would be
laundering the source under `knowledge/SEEDING.md` §3 — and it does not leave 49
standing unqualified, which would set the 46-bit trap.

---

## 3. Correction 2 — SPEC Eq. (13) and the over-cautious damage marker

**Status: the marker is over-cautious, not wrong. Independently re-confirmed, and the
filed entry cites undamaged prose instead.**

`TASK-20260802-b8d69f` rendered SPEC p.44 and found the BATCH-001 rendering of
Eq. (13) exact. I re-ran that check independently at 5× on printed p.44 and read it
off the image:

```
Adv^{IND-CCA2}_{HQC-KEM}(A) ≤ 1/(2^{|k|} · 2^{|salt|}) + 3q_RO/2^{|k|} + (q_RO + q_D)·δ
                            + 2 · (Adv_{2-DQCSD-P}(B₁) + Adv_{3-DQCSD-PT}(B₂)) .   (13)
```

Both denominators are legible; the transcription's rendering matches. **Nothing false
propagated from the marker** — it was conservative in the safe direction.

Per the handoff's Duty 2, the filed entry does **not** restate a formula under a
damage marker. `KN-LIT-b9e1a8`'s IND-CCA2 bullet instead cites **SPEC §6.2.3, printed
p.45**, which enumerates all four terms in undamaged running prose. Verbatim from that
page:

> • The first two terms 1/(2^{|k|}·2^{|salt|}) and 3q_RO/2^{|k|} remain unchanged since
>   they are independent of the output of the sampler ;
> • The third term (q_RO + q_D) · δ is related to the δ-correctness of the scheme. …
>   Using Lemma 6.4, the above probability increases by at most (τ^{ω_r}_max)³ ;
> • The fourth term 2 · (Adv_{2-DQCSD-P}(B₁) + Adv_{3-DQCSD-PT}(B₂)) must be adjusted …

This discharges the `DEC-20260802-344883` D-6 citation fix in the form the validator
recommended: the entry's claim now rests on prose that was never marked damaged, and
the `[EXTRACTION-DAMAGED]` marker on the frozen BATCH-001 artifact is **left exactly
where it is**. It is not removed, edited, or contradicted — it is superseded by a
better-sourced citation in the new record.

Transcription assumption **A21** carries the same citation defect (it cites "Theorem
6.3's third summand"). A21 lives in the frozen artifact and is not edited; this report
records that §6.2.3 p.45 is its undamaged source, for whatever record the Coordinator
files.

---

## 4. X6's second half — explicit verdict

**The two halves of X6 were bundled and they do NOT have the same status in one
respect and DO in another. Both are source anomalies; only the first is arithmetically
decidable.**

### 4.1 The verdict

> **X6 second half — the external-code dimension: GENUINE SOURCE ANOMALY, not a
> transcription error.** The specification says two different things about the same
> object in two adjacent subsections, and `TASK-20260802-6344ed` quoted the first of
> them exactly.

### 4.2 Evidence, from the primary text

SPEC **§3.4.1**, printed p.17, text layer, verbatim:

> For the external code, we use a Reed-Solomon code of dimension 32 over F256.

SPEC **§3.4.2**, printed p.17, verbatim:

> … we construct shortened Reed-Solomon (RS-S1, RS-S2 and RS-S3) codes such that k is
> equal to 16, 24 or 32 …

SPEC **Table 3**, p.18 (6× render): RS-S1 k = 16, RS-S2 k = 24, RS-S3 k = 32.

SPEC **Table 5**, p.29: k = 128 / 192 / 256 **bits** at NIST-1/3/5. Over F₂₅₆ each
symbol is 8 bits, so 128/8 = 16, 192/8 = 24, 256/8 = 32 symbols — matching Table 3 row
for row, and matching §4.1's prose that k is "its dimension" for the concatenated
code C.

I verified the BATCH-001 transcription's §2 quotation of §3.4.1 against my own text
extraction: it is **exact, including "dimension 32 over F256"**. The transcription did
not paraphrase and did not introduce the discrepancy.

**Therefore §3.4.1's blanket "dimension 32" is true for HQC-5 only.** It is an
over-general sentence in the published document, inconsistent with §3.4.2, Table 3 and
Table 5 at NIST-1 and NIST-3.

### 4.3 Corroborating provenance, at its own strength

RMRS §4.1 (`arXiv:2005.10741`, printed p.8) reads:

> For the external code, we chose a Reed-Solomon code of dimension 32 over F256 …

and RMRS Figure 6 uses k = 32 at **all three** of its security levels. So the sentence
was **correct in the 2020 paper** and is inherited near-verbatim by the specification,
which then moved to k ∈ {16, 24, 32}. As in §2.6, this is a supported explanation of
*why* the sentence is there, not an established claim about the document's edit
history.

### 4.4 How this half differs from the first half

| | X6 first half (RS-S3 d = 49) | X6 second half (dimension 32) |
|---|---|---|
| Faithfully transcribed? | **Yes** | **Yes** |
| Source anomaly or transcription error? | **Source anomaly** | **Source anomaly** |
| Decidable from the document's own arithmetic? | **Yes** — three routes force 59 | **No** — nothing in the document is *wrong*; one sentence is *over-general*. §3.4.2 and the tables are unambiguous, so a re-derivation has a determinate answer without needing to correct anything |
| Consequence if taken at face value | δ_e = 24 instead of 29, changing Theorem 6.1's tail | A reader would use k_e = 32 at all three levels. This does **not** silently corrupt Theorem 6.1, because n_e and δ_e come from Table 3 and Table 5, not from §3.4.1 |
| Correction owed | Record d_e = 59 with derivations | Record that §3.4.1's sentence is level-specific; take k_e from Table 3 / Table 5 |

**So the bundling was the defect.** One half needed an arithmetic correction and got
none; the other needed only a scope note. `KN-LIT-b9e1a8` records them as items 1 and
2 of its "Published-text inconsistencies" section, separately.

---

## 5. Deviations from the handoff, recorded rather than absorbed

1. **Duty 1's stated premise is falsified.** The handoff and BATCH-002-OPENING §3 both
   assert the RS-S3 error is the transcription's. Measurement (§2.5) says it is the
   source's. The handoff explicitly instructed me to verify rather than trust, and to
   "say so plainly" if a route did not survive; the analogous obligation applies to a
   premise that does not survive. **`CORR-20260802-3ae664` should not assert that
   `TASK-20260802-6344ed` erred on this point.** The numeric correction it carries is
   unaffected.
2. **The handoff's caveat pointed at the wrong risk, and the right answer is
   stronger than requested.** The caveat asked whether MDS-ness survives shortening,
   warning that if not, the correction would rest on route (ii) alone — "a materially
   weaker footing". In fact route (i) survives twice over (§2.2), route (ii) survives,
   and a route (iii) exists that neither the handoff nor either review named. The
   correction rests on **three** independent internal derivations, not one.
3. **Two supported-but-unestablished provenance hypotheses are recorded** (§2.6,
   §4.3) with their status stated in-line. They are leads, not findings.
4. **No `KN-LIT-2141` upgrade was filed**, per `DEC-20260802-344883`
   (`not_warranted`: Guo–Johansson was never read in full). Not touched.
5. **Nothing under `BATCH-001/` was written.** Nothing under `ledger/` was written.
   No state-mutating git command was run. Writes are confined to the four declared
   paths plus this task directory.
6. **No experiment, no decoding trial, no measurement, no hypothesis, and no security
   assessment of HQC in either direction.** `RQ-HQC-001`'s toy claim-tier ceiling is
   untouched. Nothing here is admissible toward an AGENTS.md rule 13 closure quorum:
   this is one session on one model.

---

## 6. What this report does not establish

- **Not** that HQC-5, or any parameter set, meets or misses its DFR target. §2.7's
  figures are the red team's, relayed.
- **Not** that assumptions A1–A23 hold. A5 and A17 in particular are untested here
  and by this program.
- **Not** the edit history of either primary document (§2.6, §4.3 are hypotheses).
- **Not** that the specification contains no further anomalies. I re-read printed
  pages 17, 18, 29, 32, 34, 38, 39, 44 and 45 of the specification and pages 1, 4 and
  8–14 of RMRS. That is targeted verification of the points this task was assigned,
  not a fresh full-document audit.
- **Not** anything about whether `KN-LIT-4c1133`'s claims are correct; it is filed at
  abstract level and says so.
