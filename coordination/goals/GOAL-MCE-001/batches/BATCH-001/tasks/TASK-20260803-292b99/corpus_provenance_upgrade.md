# PROPOSED corpus provenance upgrades — not filed

**Task:** TASK-20260803-292b99 · **Goal:** GOAL-MCE-001 · **Batch:** BATCH-001
**Role:** executor · **Date:** 2026-08-03
**Requested policy:** `executor-implementation` · **Resolved model:** `claude-opus-5` ·
**fallback_used:** `true`

---

## 0. Status of this document

**PROPOSED. NOT FILED. NOTHING UNDER `knowledge/` WAS WRITTEN OR MODIFIED BY
THIS TASK.** `knowledge/INDEX.md` and `knowledge/SOURCES.md` were not touched.
Filing is a ledger-archive act belonging to `TASK-20260803-a561d8`, and these
proposals are reviewed first (`TASK-20260803-409c5e`, `TASK-20260803-08e883`).

**Dedup determination, performed before writing anything.** All four papers
reached by this task are **already in the corpus**. Zero new `KN-LIT` entries are
proposed. Every proposal below is an **upgrade to an existing entry**. This is
the explicit guard against the GOAL-HAWK-001 BATCH-001 failure of creating a
duplicate for a paper already held.

| Paper | Existing entry | Action proposed |
|---|---|---|
| `iacr:2026/1232` | **KN-LIT-7c4620** | provenance upgrade (partial: abstract-level) |
| `iacr:2024/1193` | **KN-LIT-71d1a0** | provenance upgrade to `read` + two corrections |
| `arXiv:2304.14757` | **KN-LIT-4c8135** | provenance upgrade to `read` + one material addition |
| `iacr:2025/531` | **KN-LIT-7ee1a9** | NO provenance upgrade + one correction |

Per `knowledge/SEEDING.md` ("Corrections supersede; never silently rewrite a
claim") each correction below is written as a **superseding addition to the
entry body**, not as a silent edit of an existing sentence.

---

## 1. KN-LIT-7c4620 — `iacr:2026/1232` — PARTIAL provenance upgrade

### 1.1 What changed, and what did not

**Full text was NOT obtained.** The `citation_verified` axis therefore **must NOT
go to `read`** as `knowledge/SEEDING.md` defines it: *"`read` — you fetched the
actual paper (PDF/abstract) and the claims in this entry reflect its real
content, not a search snippet."*

This is a genuinely borderline case and it is resolved conservatively, with the
reasoning exposed rather than buried:

- SEEDING.md's `read` definition literally says "(PDF/**abstract**)", and the
  abstract *was* fetched — twice, from two endpoints, verbatim.
- But the same definition requires "the claims in this entry reflect its real
  content", and the entry's substantive claims (subexponentiality, code family
  reach, heuristic assumptions) rest on a body that was **not** read.

**Recommendation: keep `citation_verified: web` and record the abstract-level
retrieval explicitly in the body.** Rationale: a reader grepping for `read`
entries is looking for "someone here has the paper". Nobody has this paper. A
`read` flag here would be exactly the false confidence
`knowledge/SEEDING.md` exists to prevent, and this program has already been
burned once by 7457 unconfirmed `read` flags (`KN-OPEN-3f7a21`).

**If the Coordinator disagrees**, the only defensible alternative is a new
enumerated value such as `abstract` — which is a schema change and therefore not
this task's to propose unilaterally. Flagged for decision, not decided here.

### 1.2 Proposed frontmatter changes

```diff
- title: "A heuristic subexponential attack on the McEliece cryptosystem"
+ title: "A Heuristic Subexponential Attack on the McEliece Cryptosystem"
  year: 2026
- venue: null
+ venue: null            # unchanged; ePrint record shows "Publication info: Preprint."
  identifiers:
    eprint: "iacr:2026/1232"
-   doi: null
+   doi: null            # unchanged; the ePrint record shows NO DOI for this paper
    url: "https://eprint.iacr.org/2026/1232"
- tags: [code-based, mceliece, structural-attack, key-recovery, goppa, subexponential, heuristic, algebraic-cryptanalysis]
+ tags: [code-based, mceliece, structural-attack, key-recovery, goppa, subexponential, heuristic, algebraic-cryptanalysis, even-characteristic, distinguisher, cfs, tii-challenges]
  confidence: reported
  citation_verified: web
```

Title change rationale: IACR prints title-case (`A Heuristic Subexponential
Attack on the McEliece Cryptosystem`) and its own BibTeX block uses the same.
Capitalisation only; no semantic change.

`+distinguisher` rationale: the paper's abstract states the approach yields a
distinguisher as a byproduct, distinct from the key-recovery claim. Tagging both
lets `RQ-MCE-e65b3c`'s "distinguisher is not break" constraint be enforced by
grep.

### 1.3 Proposed body addition (appended, superseding nothing)

> ## Primary-text retrieval, 2026-08-03 (TASK-20260803-292b99)
>
> **Abstract-level primary text obtained. FULL TEXT NOT OBTAINED.**
>
> Retrieved: `https://eprint.iacr.org/2026/1232`, HTTP 200, 17 323 bytes,
> sha256 `6e27530d976a4841fe86e41a016741c9d770735e597862a57d083bbe9b58f1a6`,
> 2026-08-03T03:08:49Z. Cross-checked against the IACR OAI-PMH record
> (`?verb=GetRecord&metadataPrefix=oai_dc&identifier=oai:eprint.iacr.org:2026/1232`),
> HTTP 200, sha256 `0de9ebddac8b755d9b77b68c77664c1fa3a88731c7114854d495db6229a3b3a0`:
> the `dc:description` carries the same abstract text. Both endpoints are on
> `eprint.iacr.org`, so this is a within-source control, not an
> independent-source control.
>
> **The PDF endpoint is a separate question and returned a separate answer.**
> `https://eprint.iacr.org/2026/1232.pdf` returned **HTTP 403** with
> `cf-mitigated: challenge` (Cloudflare bot protection) at 03:09:16Z and again
> at 03:16:58Z. The challenge was not circumvented. Additionally
> `https://eprint.iacr.org/archive/versions/2026/1232` — an **HTML** endpoint —
> also returned 403 with the same header, so the block is path-scoped and not
> format-scoped. No HAL deposit exists (checked by title, and by each of
> Tillich, Lemoine, Briaud, and by year); OpenAlex count 0; OpenAIRE total 0; no
> Wayback capture. Paper licence is **CC BY**; the block is bot protection, not
> an authorization wall.
>
> ### What the abstract establishes (VERBATIM claims, at the source's own hedging level)
> - Code family: *"the McEliece cryptosystem based on binary Goppa codes"*, and
>   *"It also applies in general to the case where the field over which the Goppa
>   code is defined is of even characteristic."*
> - Mechanism: *"a new algebraic modeling for finding as in [CMT23,M25,BLT26]
>   matrices of rank $2$ in the code of quadratic relations related to the Goppa
>   code that is attacked"*, used *"to recover the secret algebraic structure of
>   the code, from which an equivalent secret key can be efficiently derived,
>   leading to a full key-recovery attack."*
> - Byproduct: *"a new distinguisher for Goppa codes in even characteristic which
>   is as the syzygy distinguisher of [R25] subexponential in the security
>   parameter of the scheme."*
> - **Complexity claim, stated as a CONJECTURE:** *"We make the conjecture that
>   this attack has a complexity which is of the same nature as the
>   distinguisher, namely subexponential in the security parameter."*
>   **No exponent, no formula, no asymptotic expression appears in the abstract.**
> - Demonstrated instances: McEliece **TII challenges** *"aimed at having
>   $83$,$89$,$119$,$166$, $210$ and even $248$ bit security respectively"* (the
>   challenges' design targets, in the abstract's own words "aimed at having" —
>   the abstract does not say which were solved), and **CFS keys with $r=9$,
>   $m=16$** at *"a security of $74.9$ bits according to [LS12]"*, which
>   *"took us 14 hours of computation and 24GB of RAM."*
> - **RATE REGIME: the abstract states NONE.** No rate condition, no genus
>   condition, no degree restriction, no extension-degree restriction. The only
>   restriction of any kind stated is the field condition **even characteristic**.
>   Whether the body imposes one is **unknown**.
> - **Authors' own revision note (2026-06-12), VERBATIM:** the sentence *"This
>   breaks the scheme."* was removed and replaced by the full-key-recovery
>   formulation; and *"Note that the last paragraph in the introduction called «
>   The impact on the McEliece scheme » leaves no doubt that this attack does not
>   break Classic McEliece parameters."* **That paragraph was not read. This
>   program neither adopts nor contradicts the authors' characterisation of it,
>   and asserts nothing about Classic McEliece's security.**
>
> ### What remains unread
> The body in full: the exponent, the definition of "security parameter" in
> which subexponentiality is claimed, **every numbered heuristic**, the algebraic
> modeling, the per-challenge experimental results, the bibliography (so
> `[CMT23]`, `[M25]`, `[BLT26]`, `[R25]`, `[LS12]` are **not** expanded here),
> and the paragraph "The impact on the McEliece scheme".
>
> **The paper's heuristic count is UNKNOWN, not zero.** No heuristic of this
> paper has been enumerated by this program, and none was reconstructed from
> memory.
>
> Full retrieval record: `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/source_access_log.yaml`.
> Transcriptions: `attack_transcription.md`, `heuristics_enumerated.md`,
> `rate_regime_extraction.md` in the same directory.

### 1.4 What must NOT be written into this entry

- Any exponent, complexity formula, or bit-security figure for the attack. None
  was obtained.
- Any statement that the attack does or does not threaten Classic McEliece.
- Any expansion of `[R25]` as a fact. `attack_transcription.md` §1.6 records the
  identification with `iacr:2024/1193` as a **labelled inference**, and it should
  stay labelled that way if it is carried across at all.

---

## 2. KN-LIT-71d1a0 — `iacr:2024/1193`, *The syzygy distinguisher* — FULL provenance upgrade + 2 corrections

### 2.1 Proposed frontmatter change

```diff
- citation_verified: web
+ citation_verified: read
- tags: [code-based, mceliece, structural-attack, key-recovery, distinguisher, syzygy, commutative-algebra, alternant-codes, algebraic-cryptanalysis]
+ tags: [code-based, mceliece, structural-attack, distinguisher, syzygy, commutative-algebra, alternant-codes, goppa, betti-numbers, subexponential, heuristic, algebraic-cryptanalysis]
  confidence: reported
```

`confidence` stays `reported`: nothing in this paper was re-derived or reproduced
by this program.

### 2.2 CORRECTION 1 (superseding, not a silent edit) — the `key-recovery` tag is wrong

The entry currently carries the tag `key-recovery`. **The paper is a
distinguisher and explicitly is not a key recovery.** Its own text distinguishes
the two, VERBATIM: *"Distinguishers address the decisional version of the
problem […] Key recovery attacks address the computational version"*, and its
contribution is stated as *"a new distinguisher for alternant and Goppa codes"*.

`RQ-MCE-e65b3c` constrains: *"Distinguisher is not break […]
docs/claims-and-verification.md forbids promoting one to the other. Any
deliverable naming a distinguisher states which it is."* A `key-recovery` tag on
a distinguisher paper is a grep-level promotion of exactly the kind forbidden.
**Proposed: drop the tag and record the correction in the body.**

### 2.3 CORRECTION 2 — the entry should carry the paper's own finite-parameter caveat

Proposed body addition:

> ## Primary text read, 2026-08-03 (TASK-20260803-292b99) — provenance upgrade web → read
>
> Retrieved from the sole author's own institutional page:
> `https://perso.telecom-paris.fr/randriam/maths/distingueur.pdf`, HTTP 200,
> 726 538 bytes, sha256
> `b69f8256133dcfd8c9d5dae196b8f653f5b956532a7ba949f400af3b902d68c0`,
> `application/pdf`, 2026-08-03T03:14:08Z. Extracted with `pdfminer.six`.
> The ePrint abstract page (`https://eprint.iacr.org/2024/1193`, HTTP 200,
> sha256 `bb35bf020a539b0f1b31d092cd56ba4de1ec6841aaefd7c870f938546173c9b2`)
> confirms DOI `10.1007/978-3-031-91095-1_12`, *"A major revision of an IACR
> publication in EUROCRYPT 2025"*, licence CC BY.
>
> **VERSION CAVEAT — load-bearing.** The retrieved file is the author's copy,
> self-described *"(Eurocrypt 2025 version, expanded, with supplementary material
> and errata)"*, dated 2025-05-02 in the site directory index. The ePrint record
> shows **"2025-10-16: last of 4 revisions"**. **This is therefore probably NOT
> the latest version, and every claim recorded from it is scoped to the sha256
> above.** One difference between the two retrieved versions is already visible:
> the ePrint abstract reads *"an analysis (in the CPA model)"* where this PDF uses
> a footnote, *"we exclude results such as [28] that use an attack model for which
> direct countermeasures exist"*.
>
> ### CORRECTION (supersedes the `key-recovery` tag)
> **This paper is a DISTINGUISHER and not a key-recovery attack.** The original
> entry's `key-recovery` tag is withdrawn. The paper itself separates the two
> notions explicitly. Per `RQ-MCE-e65b3c` and
> `docs/claims-and-verification.md`, a distinguisher may not be promoted to a
> break, including by tagging.
>
> ### Claims read (VERBATIM, at the source's own hedging level)
> - *"We present a new distinguisher for alternant and Goppa codes, whose
>   complexity is subexponential in the error-correcting capability, hence better
>   than that of generic decoding algorithms."*
> - *"Moreover it does not suffer from the strong regime limitations of the
>   previous distinguishers or structure recovery algorithms: in particular, it
>   applies to the codes used in the Classic McEliece candidate for postquantum
>   cryptography standardization."*
> - *"Since its introduction in 1978, this is the first time an analysis of the
>   McEliece cryptosystem breaks the exponential barrier."* (with the footnote
>   excluding attack-model results, above)
> - **The complexity claim is CONDITIONAL and the paper says so in the sentence
>   introducing it:** *"Now, under Heuristic 1, we have: Theorem 3.
>   Asymptotically, q-ary alternant (including Goppa) codes of dual rate R can be
>   distinguished from random codes, with complexity at most …"*. The displayed
>   formula (92) is **[EXTRACTION-DAMAGED]** from the two-column PDF and **is not
>   transcribed into this corpus.** Its qualitative consequence, which the paper
>   states in clean prose, is: *"the complexity of our distinguisher is
>   subexponential in b (although, admittedly, only very slightly so)"*, where
>   `ω ≈ 2.372 is the exponent of linear algebra`.
> - **Rate regime:** the theorem is stated in the **dual** rate R, and the paper
>   states VERBATIM *"However here we allow any R."* Heuristic 1's random-code
>   null model does carry rate conditions; for q = 2 the paper gives clean
>   numeric thresholds **R < 0.277** (part 1) and **R < 0.141** (part 2), and its
>   proof of Theorem 3 argues the relevant shortened code has rate `o(1)` so both
>   are satisfied. **Do not read 0.277/0.141 as primal-rate thresholds for a
>   McEliece code; R here is a dual rate and the conditions are applied to a
>   shortened code.**
> - **Unproven inputs, numbered by the paper:** Heuristic 1 (one statement, two
>   parts) and Experimental facts 1–4. The paper flags all of them, states
>   *"we will not be able to give proofs"*, gives partial theoretical arguments
>   and sampling experiments, and records its own counterexamples (Golay code for
>   Experimental fact 2; *"one can find counterexamples"* for Experimental fact 3).
>   Enumerated in
>   `coordination/goals/GOAL-MCE-001/batches/BATCH-001/tasks/TASK-20260803-292b99/heuristics_enumerated.md` §2.
> - **The paper's own finite-parameter caveat, VERBATIM:** *"However this is only
>   an asymptotic result: for concrete, finite parameters, such as those proposed
>   in the Classic McEliece specification, a naive implementation of our
>   distinguisher still falls beyond the best attacks by a non-negligible
>   factor."* Its first open problem is *"Problem 1. Improve the implementation of
>   this distinguisher."*
> - The paper reports that for two of the five parameter triples in its Example
>   2, the condition its Heuristic-1-based complexity estimate relies on is **not**
>   satisfied, naming Lemma 5 as the fallback.
>
> ### Not recorded here, deliberately
> The κ complexity values in Example 2 are **[EXTRACTION-DAMAGED]** (flattened
> superscripts) and are **not** transcribed. The `(n, m, t)` triples in that
> table are this paper's reproduction of Classic McEliece parameters and are **not
> a substitute for the Classic McEliece specification**.
>
> This entry asserts nothing about Classic McEliece's security. Sentences above
> that mention Classic McEliece are the paper's, quoted.

---

## 3. KN-LIT-4c8135 — `arXiv:2304.14757` — FULL provenance upgrade + one material addition

### 3.1 Proposed frontmatter change

```diff
- citation_verified: web
+ citation_verified: read
- tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, polynomial-time, high-rate, algebraic-cryptanalysis]
+ tags: [code-based, mceliece, structural-attack, key-recovery, alternant-codes, polynomial-time, high-rate, small-field, not-goppa, groebner, algebraic-cryptanalysis]
```

`key-recovery` is **correct** here and stays: this paper does claim key recovery.

**Coverage caveat that must travel with the upgrade:** the full text was
obtained and read **selectively by targeted search**, not cover to cover. The
`read` flag is proposed on the basis that the paper is in hand at a recorded
sha256 and its scope statements were read in the original; a reviewer should
know the enumeration of its heuristics is **not certified complete**.

### 3.2 Proposed body addition — THE MATERIAL CORRECTION

The existing entry says *"Alternant codes are the family containing Goppa codes;
the result is confined to the high-rate regime"* and flags the rate threshold as
*"the single most important number in the paper"*. Having read the paper, **the
rate threshold is not the only load-bearing restriction, and arguably not the
decisive one for this goal.**

> ## Primary text read, 2026-08-03 (TASK-20260803-292b99) — provenance upgrade web → read
>
> Retrieved: `https://arxiv.org/pdf/2304.14757`, HTTP 200, 526 690 bytes, sha256
> `ebbd94ac3cd00b0f0e723aeab56fd3b0820c89d47072fc8241f12c5f93c564b8`, PDF v1.4,
> 36 pages, 2026-08-03T03:16:58Z. Identity confirmed at
> `https://arxiv.org/abs/2304.14757` (`citation_title` and three authors).
> **Version caveat:** the URL carried no version suffix, so arXiv served the
> current version at that timestamp; the version number was not recorded.
> **Read selectively by targeted search, not cover to cover.**
>
> ### MATERIAL ADDITION — the attack does not apply to Goppa codes
> The paper states VERBATIM: *"Interestingly our attack does not work at all when
> the alternant code has the additional structure of being a Goppa code."*
> Its Table 1 lists the restriction for this paper as
> *"q = 2 or q = 3, m arbitrary + high rate condition (6) (does not apply in the
> particular case of Goppa codes)"*, and §3.2 is titled *"What is wrong with Goppa
> codes?"*, stating *"Goppa codes behave differently from random alternant codes
> and provide counterexamples to Heuristic 18."*
>
> The original entry recorded the high-rate scoping and did **not** record the
> Goppa exclusion. Since the McEliece cryptosystem this program is studying uses
> **binary Goppa** codes, the exclusion is at least as load-bearing as the rate
> threshold, and its absence made the entry read as closer to McEliece than the
> paper claims. **This addition supersedes the impression left by the original
> "Contribution" paragraph; the original text is not deleted.**
>
> ### The full stated restriction (three conjuncts, not one)
> 1. **Code family:** *generic alternant* codes — **explicitly NOT Goppa codes**.
> 2. **Field size:** *"q ∈ {2,3}"* / *"the field size sufficiently low q = 2 or
>    q = 3"*.
> 3. **Rate:** *"provided that the rate of the alternant code is sufficiently
>    large (6)"*. **Condition (6) itself is [EXTRACTION-DAMAGED] from the PDF and
>    is NOT transcribed into this corpus.** What is clean: it is a lower bound on
>    `n − 1`, and `e := max{ i ∈ ℕ | r ≥ q^i + 1 } = ⌊log_q(r−1)⌋`. **The numeric
>    rate threshold this entry previously flagged as missing is still missing, and
>    that is now a recorded extraction failure rather than an unattempted read.**
>
> ### Epistemic status, at the paper's own hedging level
> VERBATIM: *"By using certain heuristics that we confirmed experimentally we are
> able to prove that the Gröbner basis computation takes polynomial time and give
> a complete algebraic explanation of each step of the computation."* The
> polynomial-time claim is conditional on heuristics and the paper says so in the
> same sentence. Numbered unproven inputs found: **Conjecture 18, Heuristic 23,
> Assumption 28, Assumption 29 (High rate regime, q ≥ 3), Assumption 30 (High
> rate regime, q = 2)**, plus at least one unnumbered heuristic step. Enumeration
> **not certified complete**; see `heuristics_enumerated.md` §3.
>
> A discrepancy is recorded and not repaired: the prose refers to *"Heuristic
> 18"* while the numbered statement at 18 is labelled *"Conjecture 18"*.
>
> ### Artifact the paper points to (recorded, not fetched)
> *"A proof-of-concept implementation in MAGMA of the whole attack can be found at
> https://github.com/roccomora/HighRateAlternant."*
>
> This entry asserts nothing about Classic McEliece's security.

---

## 4. KN-LIT-7ee1a9 — `iacr:2025/531` — NO provenance upgrade, one correction

### 4.1 No upgrade

`citation_verified` **stays `web`**. Full text was **not** obtained:
`inria.hal.science/hal-05461754/document` and `.../hal-04953992/document` both
returned **HTTP 200 whose body is a proof-of-work bot interstitial**, not a PDF.
The challenge was not circumvented. Only the ePrint abstract was read (HTTP 200,
sha256 `88035f1a7a0f59750cbaf89a770295643f0e9a111d72b43bbb6d9ad497bfb299`).

### 4.2 CORRECTION — the `key-recovery` tag

Same defect as KN-LIT-71d1a0. The entry is tagged `key-recovery`; the paper is a
**distinguisher** analysis. Its abstract states *"Computing HF(2) still gives a
polynomial time **distinguisher** for alternant or Goppa codes"* and frames
distinguishing as *"a first step before being able to attack McEliece"* — i.e.
the paper itself places the key recovery elsewhere ([BMT24]).

**Proposed: drop `key-recovery`, add `distinguisher-only`, and add a body note.**

> ## Abstract read, 2026-08-03 (TASK-20260803-292b99) — NO provenance upgrade
>
> `citation_verified` stays `web`: the full text was **not** obtained.
> `inria.hal.science/*/document` returns a proof-of-work bot interstitial under
> HTTP 200 (not circumvented); the ePrint PDF endpoint is Cloudflare-challenged.
> The ePrint abstract was read: `https://eprint.iacr.org/2025/531`, HTTP 200,
> sha256 `88035f1a7a0f59750cbaf89a770295643f0e9a111d72b43bbb6d9ad497bfb299`.
>
> **CORRECTION:** this is a **distinguisher** result, not a key recovery. The
> `key-recovery` tag is withdrawn per `RQ-MCE-e65b3c`'s "distinguisher is not
> break" constraint.
>
> **Rate regime NOT obtained.** The abstract announces that the work *"yields a
> precise description of the new regime of rates that can be distinguished by
> this new method"* — and that description is in the body, which was not read.
> The abstract's own hedge is preserved: the degree-2 distinguisher *"is
> **apparently** able to distinguish Goppa or alternant codes in a much broader
> regime of rates"* than [FGO+11], whose reach the abstract characterises as
> *"only able to distinguish Goppa codes or alternant codes of rate very close
> to 1"*.

---

## 5. What is NOT proposed

- **No new `KN-LIT` entry.** All four papers were already held. Zero duplicates.
- **No `KN-TECH`, `KN-FIND`, or `KN-OPEN` entry.** BATCH-001 reproduced nothing,
  so nothing has become an internal finding
  (`knowledge/SEEDING.md`: *"A literature entry never becomes a finding"*).
  The zero-`KN-TECH`-on-ISD gap named in BATCH-001-OPENING §2 is **not** patched
  here and this task does not claim to have patched it.
- **No edit to `knowledge/INDEX.md` or `knowledge/SOURCES.md`.** Regeneration
  follows filing, and filing has not happened.
- **No `confidence` upgrade anywhere.** Nothing was re-derived or reproduced;
  `reported` is the honest ceiling for all four.
- **No change to any entry's characterisation of impact on Classic McEliece.**
  This program asserts nothing about that in either direction.

## 6. One corpus-wide observation, for the Coordinator to route (NOT a filing)

The `key-recovery` tag appears on **two** entries in this line whose papers are
distinguishers (`KN-LIT-71d1a0`, `KN-LIT-7ee1a9`). Both were filed 2026-08-03 by
`GATHER-20260803` without the papers being read. `RQ-MCE-e65b3c` makes
"distinguisher is not break" a binding constraint, and a mis-tag defeats it at
the grep level — which is precisely the channel `knowledge/SEEDING.md` says the
corpus exists to serve.

**This task checked two entries out of 169 and found the defect in both.** That
is a two-of-two sample and **not** an estimate of the rate across the sweep; the
proper response is a check, not an extrapolation. Whether a corpus-wide audit of
`distinguisher` vs `key-recovery` tagging is warranted is a Coordinator
decision, and no such audit was performed or is claimed here.
