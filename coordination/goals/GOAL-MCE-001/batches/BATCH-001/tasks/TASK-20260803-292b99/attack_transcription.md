# Attack transcription — `iacr:2026/1232` and the nearest primary statements of the 2026 line

**Task:** TASK-20260803-292b99 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true` (policy aliases do not resolve under this Claude Code harness)

---

## 0. What this document is, and what it is not

This is a **transcription**. Every block below marked `VERBATIM` is copied
character-for-character from a retrieved source whose URL, HTTP status, byte
count and sha256 are in `source_access_log.yaml`. Nothing here is this
program's assessment.

**Scope firewall, stated once and binding on the whole file.** This program
asserts **nothing** about Classic McEliece's security in either direction.
Several sources quoted below make statements about Classic McEliece's
parameters. Those statements are **theirs**, they are reproduced because the
task requires the scope of each claim to be transcribed alongside its headline,
and **this program neither adopts nor contradicts any of them.** A quotation is
not an endorsement and is not a finding.

**Relay, never launder.** Where a source says "we make the conjecture", this
document says "we make the conjecture". Where it says "under Heuristic 1", this
document says "under Heuristic 1". No hedge has been removed anywhere.

### Acquisition outcome, stated bluntly

| Object | Status |
|---|---|
| `iacr:2026/1232` **body / full text** | **NOT OBTAINED** |
| `iacr:2026/1232` **abstract + authors' revision note** | **OBTAINED**, two endpoints, cross-checked |
| `iacr:2024/1193` (KN-LIT-71d1a0) full text | **OBTAINED** (author's own site) |
| `arXiv:2304.14757` (KN-LIT-4c8135) full text | **OBTAINED** |
| `iacr:2025/531` (KN-LIT-7ee1a9) full text | **NOT OBTAINED** (abstract only) |

The `eprint.iacr.org` **abstract** endpoint returned HTTP 200; the **PDF**
endpoint returned HTTP 403 with `cf-mitigated: challenge`, twice, eight minutes
apart. These are reported separately and neither licenses a statement about the
other. A third data point that neither the goal record nor the batch opening
anticipated: `https://eprint.iacr.org/archive/versions/2026/1232` is an **HTML**
endpoint and it was **also** blocked (403, challenge). So the split is
**path-scoped, not format-scoped**, and "eprint HTML works" is not the correct
generalisation either.

**AGENTS.md rule 5.** The blocked body is an infrastructure outcome. It is not
negative mathematical evidence, and it says nothing about the attack.

---

## 1. PRIMARY TARGET — `iacr:2026/1232`

### 1.1 Bibliographic header, VERBATIM (source A01)

```
Paper 2026/1232
A Heuristic Subexponential Attack on the McEliece Cryptosystem

Pierre Briaud, XLIM, Centre National de la Recherche Scientifique
Axel Lemoine, French Institute for Research in Computer Science and Automation, Direction Générale de l'Armement
Hugues Randriambololona, ANSSI, Télécom ParisTech
Jean-Pierre Tillich, French Institute for Research in Computer Science and Automation
```

```
Category: Attacks and cryptanalysis
Publication info: Preprint.
Keywords: McEliece scheme, Algebraic cryptanalysis, Binary Goppa codes
History: 2026-06-12: revised / 2026-06-10: received
Short URL: https://ia.cr/2026/1232
License: CC BY
```

Note the title as printed by IACR capitalises differently from `KN-LIT-7c4620`'s
stored title. Stored: `A heuristic subexponential attack on the McEliece
cryptosystem`. As printed: `A Heuristic Subexponential Attack on the McEliece
Cryptosystem`. The BibTeX block on the same page also uses the printed form.
Recorded for the provenance upgrade; it is a capitalisation difference only.

### 1.2 THE COMPLEXITY STATEMENT AND ITS SURROUNDING SCOPE TEXT — abstract, VERBATIM

Source: A01 (`https://eprint.iacr.org/2026/1232`, HTTP 200, sha256
`6e27530d…f1a6`), independently cross-checked against A11
(`…/oai?verb=GetRecord…`, HTTP 200, sha256 `0de9ebdd…b3b3`), which returns the
same text in `dc:description`. Both are `eprint.iacr.org`, so this is a
**within-source control, not an independent-source control**.

> We provide a new way of performing an algebraic attack on the McEliece
> cryptosystem based on binary Goppa codes. It also applies in general to the
> case where the field over which the Goppa code is defined is of even
> characteristic. It is based on a new algebraic modeling for finding as in
> [CMT23,M25,BLT26] matrices of rank $2$ in the code of quadratic relations
> related to the Goppa code that is attacked. Such matrices are then used to
> recover the secret algebraic structure of the code, from which an equivalent
> secret key can be efficiently derived, leading to a full key-recovery attack.
> A byproduct of our approach is a new distinguisher for Goppa codes in even
> characteristic which is as the syzygy distinguisher of [R25] subexponential in
> the security parameter of the scheme. We demonstrate the effectiveness of our
> attack on McEliece TII challenges, some of which having been studied in
> [BLT26], and aimed at having $83$,$89$,$119$,$166$, $210$ and even $248$ bit
> security respectively and CFS keys with parameters $r=9$ and $m=16$,
> corresponding to a security of $74.9$ bits according to [LS12]. This CFS key
> was not attacked in practice in [BLT26] and took us 14 hours of computation
> and 24GB of RAM. We make the conjecture that this attack has a complexity
> which is of the same nature as the distinguisher, namely subexponential in the
> security parameter.

**The headline complexity statement, isolated:**

> We make the conjecture that this attack has a complexity which is of the same
> nature as the distinguisher, namely subexponential in the security parameter.

Two things the transcription must preserve and the summary must not smooth over:

1. The complexity statement is introduced by **"We make the conjecture that"**.
   The paper does not, in its abstract, state a proved or even a
   heuristically-derived exponent for the **attack**. It states a **conjecture**
   that the attack's complexity is "of the same nature as the distinguisher".
2. The **distinguisher** — the "byproduct" — is what carries the word
   "subexponential" attributively, and it is attributed by comparison: "which is
   as the syzygy distinguisher of [R25] subexponential in the security parameter
   of the scheme".

**No exponent, no formula, and no asymptotic expression for the attack appears
in the abstract.** Any exponent belongs to the body, which was not obtained.
There is nothing to mark `[EXTRACTION-DAMAGED]` here because there is nothing
to extract: the source is HTML, extraction is clean, and the number simply is
not present.

### 1.3 THE AUTHORS' OWN REVISION NOTE — VERBATIM

This is on the same ePrint record, labelled `Note:` by IACR. Reproduced in full
because it is the authors' own scope statement and the task requires scope text.

> Note: In order to avoid any misunderstanding, the two following sentences were
> changed
> "Such matrices are then used to recover the secret algebraic structure of the
> code. This breaks the scheme. «
> They were replaced by
> "Such matrices are then used to recover the secret algebraic structure of the
> code, from which an equivalent secret key can be efficiently derived, leading
> to a full key-recovery attack. »
> Note that the last paragraph in the introduction called « The impact on the
> McEliece scheme » leaves no doubt that this attack does not break Classic
> McEliece parameters.

(The unbalanced quotation marks, the French guillemets, and the non-breaking
spaces are the source's, not a transcription artefact. The raw characters were
checked against the un-rendered HTML.)

**Handling.** This note is the single most consequential piece of scope text on
the record, and it is exactly the kind of statement this program is forbidden to
convert into its own claim. What is transcribed is:

- the **authors** state that the sentence "This breaks the scheme." was
  **removed** in the 2026-06-12 revision and replaced by a full-key-recovery
  formulation;
- the **authors** state that a paragraph of their introduction, titled "The
  impact on the McEliece scheme", "leaves no doubt that this attack does not
  break Classic McEliece parameters";
- **this program has not read that paragraph.** It is in the body, and the body
  was not obtained. The authors' characterisation of their own paragraph is
  recorded at exactly their hedging level and is **not** verified here.

This program makes **no** statement about Classic McEliece's security. It also
does **not** treat the authors' note as licence to dismiss the paper — the
BATCH-001 opening (section 7) names dismissal on an untranscribed argument as
the same error as overclaiming, and the untranscribed object here is the
paragraph itself.

### 1.4 Code family and characteristic scope — VERBATIM fragments

> the McEliece cryptosystem based on binary Goppa codes

> It also applies in general to the case where the field over which the Goppa
> code is defined is of even characteristic.

> A byproduct of our approach is a new distinguisher for Goppa codes in even
> characteristic

See `rate_regime_extraction.md`. In short: the abstract states a **code family**
(Goppa codes) and a **field condition** (even characteristic), and states **no
rate condition at all**.

### 1.5 Demonstrated instances — VERBATIM fragments, with their own hedges

> We demonstrate the effectiveness of our attack on McEliece TII challenges,
> some of which having been studied in [BLT26], and aimed at having
> $83$,$89$,$119$,$166$, $210$ and even $248$ bit security respectively

> and CFS keys with parameters $r=9$ and $m=16$, corresponding to a security of
> $74.9$ bits according to [LS12]. This CFS key was not attacked in practice in
> [BLT26] and took us 14 hours of computation and 24GB of RAM.

Transcription notes, not interpretation:

- The bit figures 83, 89, 119, 166, 210, 248 are given as what the **TII
  challenges** were "**aimed at having**", i.e. they are the challenges' design
  targets, not measured attack costs.
- 74.9 bits is attributed to `[LS12]`, not derived by these authors.
- 14 hours and 24 GB of RAM are stated as **their measured cost** for the one
  CFS key with $r=9$, $m=16$.
- **The abstract does not state which of the listed TII challenges were actually
  solved**, nor with what resources. "some of which having been studied in
  [BLT26]" qualifies prior study, not present success. Anyone needing the
  per-challenge outcome must read the body.
- "TII challenges" and "CFS keys" are **not** Classic McEliece parameter sets.
  The abstract names no Classic McEliece parameter set anywhere.

### 1.6 Reference keys appearing in the abstract, untranscribed

`[CMT23]`, `[M25]`, `[BLT26]`, `[R25]`, `[LS12]`. The bibliography is in the
body and was not obtained, so **none of these is expanded here as a
transcription**. One identification is offered explicitly as an *inference*, not
a transcription: the abstract's own words are "the syzygy distinguisher of
[R25]", and the paper titled *The syzygy distinguisher* is
Randriambololona, `iacr:2024/1193` (KN-LIT-71d1a0), whose ePrint record (B02)
shows a Eurocrypt **2025** publication. That makes `[R25]` almost certainly
KN-LIT-71d1a0. **Labelled inference. Not verified against the paper's
bibliography.**

`[BLT26]` is plausibly a Briaud–Lemoine–Tillich 2026 work on the CFS and TII
challenges, which would correspond to `KN-LIT-d6d510` as titled in this corpus.
**Labelled conjecture about a citation key. Not verified. Not relied on.**

### 1.7 What of the primary target remains unknown

Everything in the body, specifically:

- the exponent, the base, and the parameter the subexponentiality is in;
- the definition of "security parameter" the claim is stated in;
- **the numbered heuristics** — see `heuristics_enumerated.md`, which records
  that the paper's own heuristics were **not obtained** and enumerates nothing
  in their place;
- the new algebraic modeling, and the rank-2-matrix step;
- the per-challenge experimental results;
- the paragraph "The impact on the McEliece scheme";
- whether any rate condition appears in the body (the abstract states none).

---

## 2. NEAREST PRIMARY STATEMENT OBTAINED IN FULL — `iacr:2024/1193`, *The syzygy distinguisher*

This is secondary target 1 and it is also the object the primary target's own
abstract anchors its subexponentiality to ("as the syzygy distinguisher of
[R25]"). Full text obtained.

**Source B01.** `https://perso.telecom-paris.fr/randriam/maths/distingueur.pdf`,
HTTP 200, 726 538 bytes, sha256
`b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0`,
`application/pdf`. Extracted with `pdfminer.six` (90 136 chars).

**VERSION CAVEAT, load-bearing.** This is the **author's own copy**, dated
2025-05-02 in the site's directory index (A25). Its title block reads *"(Eurocrypt
2025 version, expanded, with supplementary material and errata)"*. The ePrint
record (B02) reports **"2025-10-16: last of 4 revisions"**. **This copy is
therefore probably NOT the latest ePrint version.** Every quotation below is
scoped to this sha256 and to no other version.

### 2.1 Abstract, VERBATIM (B01, agrees with B02)

> We present a new distinguisher for alternant and Goppa codes, whose complexity
> is subexponential in the error-correcting capability, hence better than that of
> generic decoding algorithms. Moreover it does not suffer from the strong regime
> limitations of the previous distinguishers or structure recovery algorithms: in
> particular, it applies to the codes used in the Classic McEliece candidate for
> postquantum cryptography standardization. The invariants that allow us to
> distinguish are graded Betti numbers of the homogeneous coordinate ring of a
> shortening of the dual code.
> Since its introduction in 1978, this is the first time an analysis¹ of the
> McEliece cryptosystem breaks the exponential barrier.

Footnote 1, VERBATIM: *"we exclude results such as [28] that use an attack model
for which direct countermeasures exist"*.

The ePrint abstract (B02) renders the same sentence as *"this is the first time
an analysis (in the CPA model) of the McEliece cryptosystem breaks the
exponential barrier"* — an inline parenthetical where B01 uses a footnote.
Recorded because it is a difference between two retrieved versions.

**It is a DISTINGUISHER, not a key recovery.** RQ-MCE-e65b3c's constraint
"Distinguisher is not break" applies and is stated here explicitly, as required.

### 2.2 The complexity statement — Theorem 3, VERBATIM with damage marking

Context line immediately preceding, VERBATIM: **"Now, under Heuristic 1, we
have:"**

> **Theorem 3.** Asymptotically, q-ary alternant (including Goppa) codes of dual
> rate R can be distinguished from random codes, with complexity at most

Equation (92), raw pdfminer output, unedited:

```
                        (cid:16)
                     ω R2
                     1−R +o(1)
                                (cid:17) (logq logq (n))3
                                        (logq (n))2 n
              κ = q
                                                          (92)
```

**[EXTRACTION-DAMAGED]** — superscript/exponent grouping is not recoverable
from the extracted character stream, and the `(cid:NN)` tokens are unmapped
glyphs (large parentheses). **This equation as extracted may not carry a
claim.**

A **cross-check within the same document** raises confidence in one reading
without removing the damage marker. Section 5's closing argument states,
VERBATIM:

> In [5, §3.4], the security level 2^b — or less formally, the number b of
> targeted "bits of security" — of the Classic McEliece system, essentially
> defined as the complexity of the currently best attack (namely, by information
> set decoding), is shown asymptotically to be linear in t ∝ n/ log(n). Then in
> (92) we have
>
>     log(κ) / (n/ log(n))  ∝  (log log(n))³ / log(n)  →  0
>
> which means that the complexity of our distinguisher is subexponential in b
> (although, admittedly, only very slightly so).

Dividing the reading `log_q κ ≍ (ω R²/(1−R) + o(1)) · (log_q log_q n)³ /
(log_q n)² · n` by `n/log n` yields `(log log n)³ / log n`, which is what the
paper's own displayed proportionality says. The two are consistent.
**Nevertheless equation (92) stays marked [EXTRACTION-DAMAGED] and no numeric
claim is built on it in any deliverable of this task.** The internal consistency
check is reported as a check, not as a repair.

The paper immediately defines, VERBATIM: **"where ω ≈ 2.372 is the exponent of
linear algebra."**

**Note the hedge the paper puts on its own headline**, VERBATIM: *"subexponential
in b (although, admittedly, only very slightly so)"*.

### 2.3 The paper's own conclusion about finite parameters — VERBATIM

> We presented the first structural analysis of the McEliece cryptosystem whose
> asymptotic complexity is better than that of generic decoding algorithms; more
> precisely, subexponential in the error-correcting capability of the code.
> However this is only an asymptotic result: for concrete, finite parameters,
> such as those proposed in the Classic McEliece specification, a naive
> implementation of our distinguisher still falls beyond the best attacks by a
> non-negligible factor.

Followed immediately by, VERBATIM: **"Problem 1. Improve the implementation of
this distinguisher."**

Again: the sentence about Classic McEliece is **the paper's**, quoted because it
is the paper's own scope statement. This program adopts no position on it.

### 2.4 Example 2 — the paper's applied table

The paper gives a table headed, VERBATIM: *"The following table shows how the
distinguisher from Proposition 8 applies to Classic McEliece parameters."*

Reproduced from the pdfminer extraction. **The whole table is marked
[EXTRACTION-DAMAGED]: column alignment in a five-column LaTeX table is exactly
the failure mode the task warns about, and the row-to-column association below
is a reconstruction from the extraction order, not a read of the rendered
table.**

```
(n, m, t)   (3488, 12, 64)  (4608, 13, 96)  (6688, 13, 128)  (6960, 13, 119)  (8192, 13, 128)
r*          427             683             939              867              939
s           377             568             816              769              848
r* − s      50              115             123              98               91
[ns, ks]    [3111, 391]     [4040, 680]     [5872, 848]      [6191, 778]      [7344, 816]
ks(ks+1)/ns 49.27           114.62          122.61           97.89            90.78
dGV         921             1069            1650             1828             2256
d⊥GV        55              62              122              108              110
κ           2528            (21080)         (21224)          21030            2997
```

**[EXTRACTION-DAMAGED] — the κ row is not usable.** The extracted values
`2528`, `(21080)`, `(21224)`, `21030`, `2997` are almost certainly *powers of
two* whose superscript markup was flattened (i.e. `2^528`, `(2^1080)`,
`(2^1224)`, `2^1030`, `2^997`), which the surrounding text about complexities
"well beyond security levels" would be consistent with. **That reading is a
reconstruction and is NOT transcribed as a fact.** No deliverable of this task
carries a κ value. This is precisely the class of error that cost GOAL-HQC-001
BATCH-001 50.7 bits at NIST-5, and it is being refused rather than committed.

The `(n, m, t)` triples above are **transcribed from KN-LIT-71d1a0, which is a
third party for this purpose.** They are **not** a transcription of Classic
McEliece's own specification, which is `TASK-20260803-f3aece`'s deliverable.
Do not use this row as a parameter source.

The paper's own commentary on that table, VERBATIM:

> We observe that the condition dGV (ns, ks) > ks + 1 − ks(ks+1)/ns is always
> satisfied with a large margin, so we could choose a smaller s and still be able
> to distinguish. Concerning the complexity estimate κ, it relies on the
> condition dGV (ns, ns − ks) > ks(ks+1)/ns. We see this condition is satisfied
> for the parameter sets (3488, 12, 64), (6960, 13, 119), (8192, 13, 128), but
> for (4608, 13, 96) and (6688, 13, 128) it is not (then, it would still be
> possible to give a complexity estimate, using Lemma 5 instead of Heuristic 1).
> These complexities improve those from [7], although they remain practically
> unreacheable and well beyond security levels.

("unreacheable" is the source's spelling.)

Two transcribed facts worth the Coordinator's attention, stated as
transcription and nothing more: (a) the paper reports that **for two of the five
parameter triples it lists, the condition its Heuristic-1-based complexity
estimate relies on is NOT satisfied**, and it names Lemma 5 as the fallback;
(b) the paper's own characterisation of the resulting complexities is
"practically unreacheable and well beyond security levels".

---

## 3. SECONDARY TARGET 2 IN FULL — `arXiv:2304.14757` (KN-LIT-4c8135)

**Source C02**, HTTP 200, 526 690 bytes, sha256
`ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`, 36 pages.
Title confirmed at C01: *Polynomial time key-recovery attack on high rate random
alternant codes*, Bardet Magali, Mora Rocco, Tillich Jean-Pierre. **Version
caveat:** the URL carried no version suffix, so arXiv served the current version
at 03:16:58Z; the version number was not recorded.

Abstract, VERBATIM (C01):

> A long standing open question is whether the distinguisher of high rate
> alternant codes or Goppa codes \cite{FGOPT11} can be turned into an algorithm
> recovering the algebraic structure of such codes from the mere knowledge of an
> arbitrary generator matrix of it. This would allow to break the McEliece scheme
> as soon as the code rate is large enough and would break all instances of the
> CFS signature scheme. We give for the first time a positive answer for this
> problem when the code is {\em a generic alternant code} and when the code field
> size $q$ is small : $q \in \{2,3\}$ and for {\em all} regime of other
> parameters for which the aforementioned distinguisher works. […]

Body statement of the restriction, VERBATIM (C02):

> Here we break for the first time the m “ 2 barrier, which was even conjectured
> at some point to be the ultimate limit for such algebraic attacks to work in
> polynomial time and show that we can actually attack McEliece-alternant for any
> extension degree m provided that the rate of the alternant code is sufficiently
> large (6) and the field size sufficiently low q “ 2 or q “ 3.

(`“` is the extraction's rendering of `=`; this is a known pdfminer ligature
artefact in this document and is left as extracted.)

And, VERBATIM, the sentence that decides the code family:

> Opening the road for attacking the CFS scheme. Interestingly our attack does not
> work at all when the alternant code has the additional structure of being a
> Goppa code.

Table 1, VERBATIM as extracted:

```
paper                 restriction
[SS92, CGG`14]        m “ 1
[COT14]               m “ 2 + Wild Goppa code
this paper            q “ 2 or q “ 3, m arbitrary + high rate condition (6)
                      (does not apply in the particular case of Goppa codes)
```

Condition (6) itself: see `rate_regime_extraction.md`. It is
**[EXTRACTION-DAMAGED]** and is not reconstructed.

---

## 4. SECONDARY TARGET 3 — `iacr:2025/531` (KN-LIT-7ee1a9), ABSTRACT ONLY

Full text **NOT obtained**: `inria.hal.science/*/document` served a
proof-of-work bot interstitial under HTTP 200 (D01, D02) and it was not
circumvented. ePrint abstract obtained at D03, sha256 `88035f1a…b299`.

Abstract, VERBATIM:

> Distinguishing Goppa codes or alternant codes from generic linear codes
> [FGO+11] has been shown to be a first step before being able to attack McEliece
> cryptosystem based on those codes [BMT24]. Whereas the distinguisher of [FGO+11]
> is only able to distinguish Goppa codes or alternant codes of rate very close to
> 1, in [CMT23a] a much more powerful (and more general) distinguisher was
> proposed. It is based on computing the Hilbert series $\{\mathrm{HF}(d),~d\in
> \mathbb{N}\}$ of a Pfaffian modeling. The distinguisher of [FGO+11] can be
> interpreted as computing $\mathrm{HF}(1)$. Computing $\mathrm{HF}(2)$ still
> gives a polynomial time distinguisher for alternant or Goppa codes and is
> apparently able to distinguish Goppa or alternant codes in a much broader
> regime of rates as the one of [FGO+11]. However, the scope of this
> distinguisher was unclear. We give here a formula for $\mathrm{HF}(2)$
> corresponding to generic alternant codes when the field size $q$ satisfies $q
> \geq r$, where r is the degree of the alternant code. We also show that this
> expression for$\mathrm{HF}(2)$ provides a lower bound in general. The value of
> $\mathrm{HF}(2)$ corresponding to random linear codes is known and this yields
> a precise description of the new regime of rates that can be distinguished by
> this new method. This shows that the new distinguisher improves significantly
> upon the one given in [FGO+11].

("expression for$\mathrm{HF}(2)$" — missing space — is the source's.)

Transcribed, not interpreted: this abstract states the *existence* of "a precise
description of the new regime of rates", and **does not give that description in
the abstract**. The regime is in the body, which was not obtained. It is also a
**distinguisher**, not a key recovery.

---

## 5. Deviations, and things that surprised the executor

Recorded under AGENTS.md rule 8 rather than dropped.

1. **DEV-1** — routes beyond the declared order 1–7 were attempted after the
   declared order was exhausted (OAI-PMH, author homepages, an open directory
   index, an ePrint listing mirror, Internet Archive, OpenAIRE, a search engine
   used only for host discovery). Logged individually in
   `source_access_log.yaml`.
2. **An HTML eprint endpoint was blocked** (`/archive/versions/2026/1232`, A03).
   The batch opening and the goal record both frame the eprint situation as
   "abstract pages work, PDF does not". The measured situation is finer-grained
   than that and the coarser statement would be wrong.
3. **`inria.hal.science` returns HTTP 200 for a bot interstitial** (D01, D02).
   Any retrieval log that records status codes without inspecting content type
   will record a false success here. Same trap in reverse at A23
   (scholar.archive.org: HTTP 200, rate-limit body).
4. **Challenge-page sha256 is not reproducible.** A02 and A29 returned the same
   5615 bytes with different sha256 values; the challenge body carries a
   per-request nonce. A validator re-acquiring a blocked URL should expect the
   hash to differ and should not read that as a discrepancy.
5. **`pdfminer.six` was unusable until `cffi` was installed.** The system
   `cryptography` package raised `ModuleNotFoundError: No module named
   '_cffi_backend'` followed by a pyo3 panic. `pip install cffi` fixed it. This
   modified the session's Python environment; it wrote nothing to the repo.
6. **A lead was found and deliberately not fetched**:
   `https://classic.mceliece.org/mceliece-610-20260623.pdf` surfaced in a search
   for this exact title (A18). It is a Classic McEliece project document and
   therefore a *third party's* characterisation of the attack. Fetching it into
   a verbatim-transcription deliverable would have imported an interested
   party's reading. It is recorded as a lead for the Coordinator and is not
   quoted anywhere.
7. **The abstract-level result is weaker than the goal record hoped for and is
   reported as such.** RQ-MCE-e65b3c set the bar at "primary text obtained and
   transcribed, or unavailability recorded with routes tried". What was obtained
   is the authors' abstract and revision note — genuinely primary, genuinely
   authored by them, published by IACR — and **not** the body, and therefore
   **not** the numbered heuristics that the goal's first completion criterion
   names. The gap is stated, not papered over.
