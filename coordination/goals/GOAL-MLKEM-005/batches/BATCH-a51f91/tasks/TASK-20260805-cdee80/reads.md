# TASK-20260805-cdee80 — four literature reads

**Role:** executor. **Goal:** GOAL-MLKEM-005. **Batch:** BATCH-a51f91.
**Repository commit at execution:** `096b9256b287810acd005f259825b6b9b0c9c42a`
(branch `claude/mlkem-campaign-005`; working tree clean except this task
directory, which was untracked at start).
**Executed:** 2026-08-05, 16:32Z–17:0xZ.

**Rule 12: UNMET and UNWAIVED.** Nothing here changes the status of any
`EV-MLKEM-*` record, any `KN-*` entry, or any hypothesis. No ML-KEM break
claim is made or implied. This is a literature-read record: it reports what
four documents say, and where they could not be obtained it says so.

**This document records observations only.** The Executor does not decide
whether the campaign closes. The verdict in §3 is a reading of the retrievable
record; the decision belongs to the Coordinator after Reviewer/Red Team.

---

## Summary table

| # | Paper | Status | Basis |
|---|-------|--------|-------|
| (i) | Bernstein, *Multi-ciphertext security degradation for lattices*, ePrint 2022/1580 | **READ** (full text, 55 pp, v2023.03.17) | PDF retrieved 200 from `cr.yp.to`; abstract cross-checked against live ePrint landing page (200) |
| (ii) | Aggarwal–Jin, *Time vs Success Probability Tradeoff for SVP and BDD…*, ePrint 2026/1364 (`KN-LIT-7661`) | **PARTIAL** (abstract only) | ePrint landing page 200; PDF 403 (Cloudflare), reader proxy 403, no arXiv record |
| (iii) | Duman–Hövelmanns–Kiltz–Lyubashevsky–Seiler, CCS 2021 = ePrint 2021/1351 | **UNOBTAINABLE** (full text); abstract READ | ePrint landing page 200; ePrint PDF 403 ×2 (incl. browser UA), ACM DL PDF 403, reader proxy 403, Wayback 429/reset, no arXiv, no institutional copy found |
| (iv) | Ducas–Pulles, *Does the Dual-Sieve Attack on LWE even Work?*, ePrint 2023/302 §5–6 (`KN-LIT-111`) | **READ** (§5–6 in full, 36-pp copy) | ePrint PDF 403; §5–6 read from a version-verified local copy — see provenance caveat in §4.0 |

Every fetch, with status code, is in `receipt.json`.

---

## 1. (i) Bernstein, ePrint 2022/1580 — the dominator — **READ**

### 1.0 What was read, and how it was obtained

`https://eprint.iacr.org/2022/1580.pdf` returned **HTTP 403** (Cloudflare
interstitial, `Just a moment...`), twice, including with a browser
`User-Agent`. The paper was instead retrieved from the author's own site:

- `https://cr.yp.to/papers/lprrr-20230317.pdf` → **HTTP 200**,
  `application/pdf`, 821,460 bytes, 55 pages,
  sha256 `7b0e27261f4f9abcd7aa02fc9e3ed441b1f2d5b2ae3d7b5352f47e325e04f970`.
- `https://cr.yp.to/papers/lprrr-20221114.pdf` → **HTTP 200**, 783,194 bytes,
  50 pages (the earlier version; not read).

Version identification is not an inference. The ePrint landing page for
2022/1580 (fetched 200 today) gives contact author
`authorcontact-lprrr@box.cr.yp.to` and History `2023-03-17: revised`,
`2022-11-14: received` — matching both `cr.yp.to` filenames exactly. The PDF's
own last line of page 1 reads: *"Permanent ID of this document:
cff870df5aeaaa8a4fd37778bac69658864897ef. Date: 2023.03.17."* The abstract in
the PDF is the abstract on the ePrint landing page.

*(Incidental: this is also where `KN-LIT-4974`'s `downloads/lprrr-*.pdf`
filenames come from — they are Bernstein's own filenames. See
`corpus_hygiene.json`.)*

### 1.1 What the paper actually claims

Stated contributions (§1.2, verbatim structure):

1. **§2** — asymptotic analysis and parameter optimization for the well-known
   *single-target* lattice attacks, assuming the existing heuristics.
2. **§3** — asymptotic analysis of an attack **breaking many ciphertexts for
   one public key**. "This attack has total heuristic cost asymptotically
   similar to the single-target message-recovery attacks, i.e., much lower
   heuristic cost per ciphertext. **This does not rely on key recovery**: it
   applies even if the cryptosystem is modified to put extra defenses around
   the secret key."
3. **§4** — asymptotic analysis of an attack **breaking one out of many
   ciphertexts for one public key**, beating the usual single-target
   message-recovery attack by a factor `2^{Θ(n / lg n)}` for a wide range of
   parameters, "contrary to the statement `Adv^{IND-CPA}_{PKE} ≈
   Adv^{(n,q_C)-IND-CPA}_{PKE}`".

Plus **Appendix A** (gaps in the previous literature's arguments, including
§A.4 on Duman et al. — see §3 below) and **Appendix B** (a FrodoKEM-specific
attack).

Quantitatively:

- **§3 (all-for-the-price-of-one).** If parameters are chosen so the usual
  single-target message-recovery attack has heuristic cost `2^{(1+o(1))λ}`,
  then total heuristic cost `2^{(1+o(1))λ}` suffices to decrypt `T`
  ciphertexts for any `T ≤ 2^{(0.19…+o(1))λ}`; heuristic per-ciphertext cost
  `2^{(1+o(1))λ}/T`, as low as `2^{(0.80…+o(1))λ}`.
- **§4 (one-out-of-many).** One can heuristically reduce the block size β from
  §3.3 by `Θ(n / lg n)` for breaking one out of `T` ciphertexts, provided
  `lg T ∈ Θ(n)`. Worked numerical example: for χ = binomial on {−16,…,16}
  (New Hope 2015) and `Q₀ = 0.501`, β drops by `(0.60537… + o(1)) β / lg β`
  for breaking one out of `2^{(0.0574+o(1)) β}` ciphertexts.
- The paper notes this is a **larger** heuristic improvement than the
  "dimensions for free" improvements of [45] and [44], so under the existing
  heuristics the standard message-recovery attack *plus* dimensions-for-free is
  outperformed by this one-out-of-many attack for that conservative `(χ, Q₀)`.

### 1.2 The mechanism, as the paper states it

This matters because it is the mechanism this campaign studies. §4.1–§4.4:

- Starting from the many-ciphertext attack of §3.3, **reduce β**. That reduces
  the cost of the BKZ-β step and of precomputing the short-vector database.
  "The critical question is then how far one can reduce β so that the resulting
  algorithm, when applied to one target, still has **success probability at
  least 1/T**."
- The probabilistic step that is isolated and analysed rigorously is the
  **2-norm distribution of the ciphertext randomness** `(b, d)`. §4.2 computes
  it by generating functions: with `g = Σ_i χ_i z^{i²}`, the chance that
  `Σ_j v_j² = ℓ` is the coefficient of `z^ℓ` in `gⁿ`, with saddle-point
  asymptotics `(c + o(1)) n^{−1/2} (g(ρ)/ρ^y)ⁿ` where `ρ g′(ρ) = y g(ρ)`.
- §4.3 defines **`SqueezedLPR`**: LPR except encryption rejects `(b, d)` unless
  the sum of squares of the first `(1+x₀)n` components is *exactly*
  `y(1+x₀)n`. Under the standard analysis this replaces `s²` by `y` in the
  target's squared 2-norm, i.e. drops `S₁` from `lg s` to `(lg y)/2`, which
  reduces β by `((2 lg s − lg y)/(Q₀ + 1/2) + o(1)) β / lg β`.
- §4.4 then observes that an ordinary LPR ciphertext **has a chance of being a
  SqueezedLPR ciphertext**, quantified in §4.2; in a large enough collection
  one expects to find one. That is the one-out-of-many attack.

So the load-bearing object is explicitly a **tail of the ciphertext-randomness
2-norm distribution**, and the selection is best-of-`T` on that statistic.

### 1.3 Does it already bound the effect? — what the paper does and does not give

**It does bound the asymptotic effect, and it gives Kyber-specific constants.**
§4.5 ("Countermeasures") recomputes the leading constant for other error
distributions, via the Sage script printed as Fig. 4.5.1:

| χ | constant (drop in β, relative to β/lg β) |
|---|---|
| binomial on {−16,…,16} (New Hope 2015) | `0.60537…` |
| binomial on {−8,…,8} (newer New Hope) | `0.59739…` |
| **binomial on {−3,…,3} — "one of the distributions used in the latest version of Kyber"** | **`0.56984…`** |
| **binomial on {−2,…,2} — "another distribution used in the latest version of Kyber"** | **`0.54668…`** |
| uniform on {−1,0,1} | `0.32860…` |

(all at `Q₀ = 0.501`, `S₀ = 0`, batch size ≤ `2^{(0.057+o(1))β}`).

**It does not give a concrete ML-KEM/Kyber bit figure, and says so.**
Footnote 19, attached to the Kyber rows above, verbatim:

> A full analysis of Kyber would also have to account for the rounding in Kyber
> ciphertexts, which complicates single-target and multi-target attacks. This
> rounding is mostly in the C component but also a little in the B component,
> slightly increasing the effective size of d. The latest Kyber documentation
> claims that the rounding in the latest version of Kyber-512 gains several
> bits of security for attacks against the ciphertexts. **The concrete
> question—not addressed by this paper's asymptotics; see Section 1.3—is then
> the extent to which security is damaged by variations in the effective size
> of (b, d).**

§1.3 ("Caveats") adds, in the paper's own words: concrete input sizes of
interest may be too small for asymptotic speedups to apply; "Perhaps Kyber-512
is too small for the heuristic multi-target speedups to be applicable";
relying on heuristics is error-prone; and — importantly for how this paper
should be cited —

> Sections 2, 3, and 4 of this paper are saying that two ideas visible in the
> literature—the idea that the existing heuristics accurately predict lattice
> security via the standard analysis, and the idea that multi-target lattice
> security matches single-target lattice security—**cannot both be correct**.
> This paper is not saying that one idea is accurate and the other idea is
> inaccurate; it seems more likely that there are serious inaccuracies in both
> ideas.

It also flags the free-RAM model: "like many previous papers on this topic,
this paper relies on unrealistic models of computation where arbitrarily large
arrays can be accessed for free."

**Appendix B** gives the one concrete number in the paper: a `2^{88}`-guess
attack breaking one out of `2^{40}` ciphertexts for a FrodoKEM-640 public key,
against FrodoKEM's claim of a large margin. That number is FrodoKEM-640, not
ML-KEM, and must not be transported.

### 1.4 Observation bearing on `IDEA-20260805-3d71ca`'s novelty claim

`IDEA-20260805-3d71ca` (`literature_context[0]`) recorded, from the **abstract
page only**, that "No Kyber/ML-KEM bit figure was found on that page." The full
text confirms there is **no ML-KEM bit figure anywhere in the paper**, and the
paper explicitly names the concrete question as unaddressed (footnote 19
above). But the full text **does** contain Kyber-error-distribution-specific
asymptotic constants (`0.56984…` for η=3, `0.54668…` for η=2) that the abstract
page does not. That narrows — it does not close — the gap the proposal claimed.
Recorded as an observation for the Coordinator; scoring the proposal's
`newness_score` is not the Executor's call.

---

## 2. (ii) Aggarwal–Jin, ePrint 2026/1364 (`KN-LIT-7661`) — **PARTIAL**

Full text **not obtained**: `https://eprint.iacr.org/2026/1364.pdf` → **403**
(Cloudflare); reader-proxy route → 403; no arXiv record found for the title or
for `au:Aggarwal AND ti:"Success Probability"`. The **landing page was fetched
200** and read. Nothing below is from the body of the paper.

What the abstract claims, beyond what `KN-LIT-7661` already records — and the
one thing worth adding to the corpus is the **explicit conjectured bound**,
which the entry does not state:

> Assuming that we cannot do much better than this, we conjecture that no
> algorithm can outperform this tradeoff — for any subexponential time bound
> `T(n) = 2^{o(n)}`, the success probability of solving **worst-case** SVP or
> BDD cannot exceed `2^{−(n² log log T(n)) / (c log T(n))}` for some constant
> `c > 1`, up to polynomial factors.

Also confirmed from the landing page: authors Divesh Aggarwal (NUS) and
Haoxiang Jin (UIUC); category Foundations; History `2026-07-06: approved`,
`2026-07-02: received`; the LWE/SIS reductions are derived **by applying the
conjecture**, not from a theorem.

**Observation on object identity — this is the load-bearing one for the batch.**
The quantity Aggarwal–Jin characterise is the success probability of solving
**worst-case** SVP/BDD as a function of a time budget, for blockwise-guessing
algorithms built on slide-reduced bases. The `p(β)` this campaign uses is the
per-attempt success probability of an **average-case** primal BDD/uSVP attack
at BKZ block size β against an ML-KEM instance. These are not the same object,
and the abstract does not assert that they are. Whether the tradeoff transfers
is not determinable from the abstract, and no such transfer is recorded here.
`KN-LIT-7661` itself already says "Full paper not read" and lists the lower
bounds and their tightness as NOT verified; that remains true after this task.

**Status: still OPEN.** Any use of this paper's tradeoff for `p(β)` requires
the body of the paper, which this environment could not retrieve.

---

## 3. (iii) Duman–Hövelmanns–Kiltz–Lyubashevsky–Seiler, CCS 2021 — **UNOBTAINABLE (full text)** — and the **KILL VERDICT**

### 3.1 Identification (verified, not recalled)

The paper is:

> Julien Duman, Eike Kiltz, Kathrin Hövelmanns, Vadim Lyubashevsky, Gregor
> Seiler. **"Faster Lattice-Based KEMs via a Generic Fujisaki-Okamoto
> Transform Using Prefix Hashing."** ACM CCS '21. DOI
> `10.1145/3460120.3484819`. IACR ePrint **2021/1351**, received 2021-10-07.

Verified two ways: the ePrint author search `author:Duman` (HTTP 200) returns
2021/1351 with that title and author list; and IBM Research's publication page
for the same title (HTTP 200) carries `citation_doi = 10.1145/3460120.3484819`,
`citation_conference_abbrev = CCS`, `citation_publication_date = 2021/11/14`
and the five `citation_author` fields. **There is no corpus entry for this
paper** — `grep` over `knowledge/` for the title and for "prefix hashing"
returns nothing.

### 3.2 Retrieval failures (all recorded in `receipt.json`)

| URL | Result |
|---|---|
| `https://eprint.iacr.org/2021/1351` (landing) | **200** — read |
| `https://eprint.iacr.org/2021/1351.pdf` | **403** Cloudflare |
| same, with browser User-Agent + Referer | **403** Cloudflare |
| `https://dl.acm.org/doi/pdf/10.1145/3460120.3484819` | **403** |
| `https://r.jina.ai/https://eprint.iacr.org/2021/1351.pdf` | 200 wrapper, content = Cloudflare challenge |
| `https://web.archive.org/web/2023id_/…1351.pdf` | connection reset; availability API **429** |
| arXiv API | no record |
| author/institutional pages probed | no PDF (IBM page's only PDF link is the 403 ACM one) |

**This is an acquisition failure under rule 5.** The body of 2021/1351 is not
summarised here and no mathematical conclusion is drawn from it.

### 3.3 What the DHKLS abstract actually says (read, 200)

The abstract is about the **Fujisaki–Okamoto transform**: that Bellare et al.
(EUROCRYPT 2020) show single-user security implies multi-user security with a
multiplicative gap equal to the number of users; that hashing the public key
into the random oracle ("domain separation") had no formal analysis; that this
work formally analyses domain separation in the FO transform in the multi-user
setting, shows including the public key matters for tightness in ROM and QROM,
and shows a ~32-byte unpredictable prefix suffices — yielding 2×–3× speedups in
Kyber keygen/encapsulation and up to 40% in Saber.

**The statement `Adv^{IND-CPA}_{PKE} ≈ Adv^{(n,q_C)-IND-CPA}_{PKE}` does not
appear in the abstract at all.** Per Bernstein it appears at [47, page 3] —
i.e. in the introduction, as a remark supporting the applicability of the main
FO theorem, not as the paper's headline theorem.

### 3.4 **KILL VERDICT: THE KILL CONDITION DOES NOT FIRE.**

Stated plainly, as the handoff requires: **this campaign does not close on a
citation to Duman et al.** The reduction is **not shown to be concretely tight
at ML-KEM parameters**; the only source that could be read on the question
states the opposite, in detail, and records that it went unanswered.

The verdict rests on Bernstein §A.4, read in full, which is the dominator's own
treatment of exactly this question. Its findings, as the paper states them:

1. **The claim is conditional, and the condition is unusual.** DHKLS's
   statement assumes "the hardness of MLWE as originally defined for the
   purpose of worst-case to average-case reductions […] **where the number of
   samples (using the same secret) is unlimited**." It is not an unconditional
   or concrete-cost statement.
2. **It is a proof outline, not a proof.** Bernstein reconstructs the intended
   reduction (`G′_j = −G₀^{−1}G_j`, `A′_j = A₀G′_j + A_j`, so `2s` samples
   reduce to `s` independent 1-sample problems, etc.), then states: "the
   conclusions drawn in [47] go beyond this in three ways that are not
   justified in [47]", and "the proof outline in [47] does not seem to have
   been written as a summary of a full proof."
3. **The many-sample assumption is argued to be vacuous in the relevant
   range.** "the Arora–Ge attack cited in [47, footnote 2] is already known to
   break the Module-LWE problem for (e.g.) the Kyber error distribution with a
   feasible number of samples, showing that a proof based on that problem would
   be vacuous for attacks against a feasible number of Kyber targets."
4. **The direction of implication does not give closeness of advantages.**
   "this does not logically follow from a one-way conversion of IND-CPA attacks
   into Module-LWE attacks. The obvious way to close this gap would be to prove
   a conversion the other way […] but the words 'plausibly much harder problem'
   in [47, footnote 2] indicate that a conversion is not known the other way."
5. **The gap is precisely this campaign's setting.** "The type of multi-target
   attack for which [47] claims provable security is not merely an attack
   against many independent keys, but **an attack against many ciphertexts per
   key**. However, if one wants to convert an attack against s ciphertexts for
   one key (with many ciphertexts multiplied by the same public G, making G a
   natural target for precomputation) into an attack against Θ(s) Module-LWE
   samples, it is not obviously sufficient to convert an attack against s
   independent keys into an attack against Θ(s) Module-LWE samples." And:
   "There is a proof gap at this point in [47]. It is clear how the proof
   techniques mentioned in [47] apply to multiple keys, but it is not clear how
   those techniques justify claiming multi-ciphertext security for a single
   key."
6. **Sample counting.** "the stated number of samples, 'max(n, q_C)', does not
   account for losing at least n samples as denominators, and for the
   possibility of needing more samples for the necessary invertibility. What is
   cited here in [47], namely the transformation from [15], does not count the
   number of samples, and does not handle Ring-LWE or Module-LWE."
7. **Disclosure history.** "These flaws were disclosed privately (in
   considerable detail) on 4 November 2022, and publicly […] on 14 November
   2022. At the time of this writing, there has been no response from the
   authors of [47]; the claim […] still appears in the latest version of [47]."
   ("At the time of this writing" = 2023-03-17, this version's date.)

A separate structural point, also from §A.4, that holds **even if the DHKLS
reduction were tight**: it would bound multi-target IND-CPA advantage in terms
of *many-sample MLWE hardness*, which is a different object from the concrete
cost of the best known primal attack against many ciphertexts under one key.
Bernstein's own reading of that branch: "if there is a conversion from a
multi-ciphertext attack into a multi-sample Module-LWE attack, the simplest
explanation is not 'these attacks do not exist, except that the Arora–Ge attack
suddenly breaks Module-LWE with enough samples', but rather **'Module-LWE
security degrades with the number of samples'**." A tight reduction would
relocate the degradation onto the MLWE-sample-count axis rather than forbid it.
(`IDEA-20260805-3d71ca` made the same distinction independently, at
`literature_context[1]`: "A reduction between problems and a concrete-cost
statement about the best known lattice algorithm are different objects.")

### 3.5 Residual uncertainty on the verdict — read this before relying on it

The verdict is **not** "DHKLS is wrong". It is: *on the record this environment
could retrieve, the DHKLS statement is not established as concretely tight at
ML-KEM parameters, so it does not bound the mechanism and the campaign does not
close on it.* Three limits:

- **I could not read 2021/1351.** Bernstein's quotations of it are extensive
  and specific, but they are one party's — and an adversarial party's —
  rendering of an unobtainable document. **A Reviewer should obtain 2021/1351
  and check the quotes at page 3 and footnote 2 before this verdict is treated
  as settled.**
- **The read is of the 2023-03-17 version.** Whether DHKLS responded after that
  date, or whether a later work established the tight multi-ciphertext-per-key
  reduction, was not checked and could not be checked from the abstract pages
  available. That is an open item, not a finding.
- **"Does not close" is not "is open".** Nothing here says the mechanism has
  room at ML-KEM parameters. §1.3 above records that Bernstein himself declines
  to say the heuristics are right, and names the concrete question as
  unaddressed by his asymptotics.

---

## 4. (iv) Ducas–Pulles, ePrint 2023/302, §5–6 — **READ**

### 4.0 Provenance caveat — flagged for the Validator

`https://eprint.iacr.org/2023/302.pdf` returned **403** to me today, exactly as
this repository's own committed provenance record shows it did on 2026-08-02
(`inputs/MLKEM-DUAL-SOURCES-20260802/provenance.json`, source_id
`ducas_pulles_eprint_pdf`: `"http_status": 403, "status": "unretrieved"`).

I read §5–6 from a **pre-existing PDF in this session's scratchpad**
(`ducas_pulles.pdf`, mtime 2026-08-02T17:47:20Z, 1,021,750 bytes, 36 pages,
sha256 `947f2826ce64d7a8c09493f9901ef418095b89a8660be075880f8874863eb62e`).
**I did not fetch that file and cannot attest its retrieval.** I verified it
instead:

- Its abstract, normalised (case-folded, ligatures expanded, non-alphanumerics
  stripped, hyphenation joined), is **character-identical, 1352 chars, to the
  abstract on the live ePrint landing page for 2023/302 that I fetched today at
  HTTP 200.** Title, both authors, both affiliations (CWI; Leiden) and the
  keyword list match.
- Section structure matches the paper as described: §5 Experiments (5.1–5.4),
  §6 Afterthoughts (6.1–6.3).

Two anomalies recorded rather than resolved:

- The in-repo extract `inputs/MLKEM-DUAL-SOURCES-20260802/ducas_pulles_score_loci.txt`
  is a **different typesetting** of the same paper (numeric citations `[31]`,
  `[16]`; the scratchpad copy uses alphanumeric `[LW21]`, `[GJ21]`, `[MAT22]`).
  Normalised text diverges after a 172-character common prefix. Same paper, two
  versions.
- That in-repo extract contains verbatim paper text, while the same task's
  committed `provenance.json` records the PDF as `unretrieved` (403). **The
  route by which a prior task obtained the full text is not recorded in this
  repository.** That is a provenance gap in an existing committed artifact,
  reported here, outside my write scope to fix.

### 4.1 §5 — Experiments

Setup: `W` is the output of a full sieve, all `(4/3)^{n/2}` vectors shorter
than `√(4/3)·GH(n)`. Three distributions measured: scores of uniform targets,
scores of BDD targets with Gaussian error, and scores of BDD targets with
Gaussian error **and modulus switching**. The paper states its own diagnostic
framing: "either the BDD scores are smaller than predicted, or the uniform
scores are higher than predicted."

Why the tail: "Because the contradictory regime only kicks in for rather large
values of T (say 2⁴⁰ even in small dimension) these unpredicted high scores
might be very rare and **we are interested in the tail of that distribution**."
The Guo–Johansson FFT trick is what makes tail experiments at that scale
feasible — 2⁴⁵ samples per curve for uniform targets, 2¹⁵ for BDD.

**§5.1 Implementation.** G6K [ADH+19], Python with a C binding for the WHT.
`unif_scores.py` over `(Z/qZ)^n`, `W` = full sieve on the dual of
`B·diag(2,…,2,1,…,1)` with the count of 2s equal to the FFT dimension,
≈2²⁵ samples/second/core, scores bucketed at width 1 with exceptional high
scores kept in a list. `bdd_scores.py` with `σ = ghf·GH(n)/√n`, `ghf ∈ (0,1)`.
`mod_switch.py` implements [MAT22, Alg. 2], sampling targets as in Kyber.

**§5.2 Uniform targets** (Fig. 3, n = 40…90). "On each of these curves, we see
a clear deviation from prediction for rare events: **large scores are more
likely to occur than predicted**. After following a *waterfall* shape, i.e. a
quadratic decay in logarithmic scale, the score probability seems to reach a
*floor*, where it decays much slower than a normal distribution predicts."
The floor is defined operationally as where the experimental survival function
exceeds the predicted one by a factor 2. Conclusion, verbatim: "in small
dimensions, the floor begins quite earlier than the contradictory regime,
vindicating the notion that the analysis might fail even in an earlier regime
than our predicted contradiction. In larger dimension both curves appear to
converge, but at this point, **one should not extrapolate this behavior to
higher dimensions without providing any theoretical justification**."

**§5.3 BDD targets** (σ = 0.7·GH(n)/√n; Table 1) — the numbers:

| n | 40 | 50 | 60 | 70 | 80 | 90 |
|---|---|---|---|---|---|---|
| predicted std. dev. | 11.77 | 24.33 | 50.10 | 103.0 | 211.5 | 434.2 |
| measured std. dev. | 20.07 | 53.89 | 148.0 | 412.9 | 1159 | 3313 |
| **ratio meas./pred.** | **1.705** | **2.215** | **2.954** | **4.009** | **5.480** | **7.630** |
| predicted average | 30.97 | 83.02 | 222.50 | 595.11 | 1598.6 | 4295.1 |
| measured average | 31.10 | 83.94 | 223.75 | 600.91 | 1611.3 | 4341.4 |
| **ratio meas./pred.** | **1.00** | **1.01** | **1.01** | **1.01** | **1.01** | **1.01** |
| measured median | 29.43 | 76.59 | 198.21 | 515.87 | 1345.2 | 3521.3 |
| **ratio med./avg.** | **0.95** | **0.92** | **0.89** | **0.87** | **0.84** | **0.82** |

The paper's reading: the variance ratio "appears to grow exponentially with the
dimension"; the average needs no Independence Heuristic (it is linear) and is
predicted well; the median is predicted equal to the average by the standard
analysis but is measurably lower, so the distribution is asymmetric.
Conclusion: "the standard analysis […] is completely off when it comes to
predicting the score of BDD targets. The distribution is definitely *not*
gaussian, nor even symmetric around its average, and its variance is hugely
underestimated."

**§5.4 With modulus switching** (Table 2; `k_enum = 0`, `k_fft = 20`,
`k_lat = 45`, `q = 3329`, `η = 3`, 100 samples, sieve in dimension 110 giving
13,393,776 dual vectors), against [MAT22]'s own bounds:

| p | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|
| std. dev. **upper bound** [MAT22, Lem. 5.7] | 4317 | 4317 | 4317 | 4317 | 4317 |
| measured | 2.53e5 | 7.42e5 | 1.19e6 | 1.42e6 | 1.47e6 |
| **ratio meas./u.b.** | **58.60** | **171.9** | **275.7** | **328.9** | **340.5** |
| average lower bound [MAT22, Lem. 5.4/5.5] | 8.08e4 | 4.26e5 | 1.61e6 | 3.15e6 | 4.66e6 |
| measured average | 9.46e4 | 6.81e5 | 1.89e6 | 3.36e6 | 4.79e6 |
| measured median | 6.84e3 | 4.32e5 | 1.57e6 | 3.06e6 | 4.54e6 |
| **ratio med./avg.** | **0.0723** | 0.63 | 0.83 | 0.91 | 0.95 |

An upper bound violated by 58×–340×, a bound that should be constant in `p` but
whose measured counterpart grows with `p`, and an extreme asymmetry at `p = 3`
(median more than ten times smaller than the average) which the authors flag as
"a good test case for a robust fix".

### 4.2 §6 — Afterthoughts

**§6.1** The waterfall-floor shape is the LDPC decoding-failure phenomenon
[Ric06, VCN14, ABH+22]; LDPC decoding likewise exploits short dual-code
vectors. "The analogy is striking."

**§6.2 Origin of correlation.** `⟨w, e⟩ mod 1` for `w ∈ W` can only be
independent if `W` is linearly independent. Fig. 6: a **long** relation
`w₃ = 5w₁ + 7w₂` leaves the score distribution close to the independent case; a
**short** relation `w₃ = w₁ + w₂` "changes that distribution severely." Because
`W` is a sieve output — the `(4/3)^{n/2}` shortest vectors — there are many
short relations: "we expect a constant fraction of vectors to belong to a
triple of the form `w₃ = ±w₁ ± w₂`", and for `k ≥ 4` each vector belongs to an
exponential number of such `k`-tuples. The authors add: "Fixing the analysis
via this angle would require understanding the much harder question of how
these correlations compound, and **we are doubtful if this would be a tractable
route**."

**§6.3 Is the dual attack fixable?** "The theoretical analysis of Section 4 and
the experiments of Section 5 **unequivocally invalidate the standard analysis
of the Dual-Sieve attack** (with or without FFT) as found in
[LW21, GJ21, MAT22, AS22, CST22]." But not dead: the Dual-Sieve-FFT stage could
be a first filtering stage, "the leftover problem is still the problem of
finding one BDD target among many candidates, but in an easier lattice." Three
methodological warnings the authors state explicitly:

- "**We insist that pulling the parameters of the attack outside of the
  contradictory regime is not a convincing way of substantiating a fix.** We
  need a sound analysis that precisely predicts the score behavior, and it
  should specifically be tested on the regime where the prior analysis made
  mispredictions."
- Taking `W = W₁ ∪ W₂` from two BKZ reductions and **summing** scores is a
  flawed fix: each half hits its own floor and "the sum of those two
  distribution will also have a floor at essentially the same height. Indeed,
  it would suffice to hit the floor of one of the functions, to hit the floor of
  the aggregate."
- Taking the **minimum** `f′ = min(f_{W₁}, f_{W₂})` is "more credible", but is
  conditional on `f_{W₁}, f_{W₂}` being "sufficiently independent (an
  assumption that would need substantiation)", and "might also amplify the
  issues with low scores for BDD targets observed in Section 5.3."

### 4.3 Observation for the batch, recorded without conclusion

Ducas–Pulles is a measured case where a **score distribution's mean was
predicted to within 1% at every dimension tested while its variance was
underestimated by a factor growing 1.7 → 7.6 over n = 40…90, its tail sat on a
floor the model does not have, and a published upper bound on the standard
deviation was violated by up to 340×.** The mechanism in (i) is a best-of-`T`
selection on the tail of a distribution. Whether that bears on this campaign's
control design is for the Reviewer and Coordinator; it is recorded here because
it is the exact failure mode the inventor protocol's "controls before belief"
clause describes, in the same problem family.

Note also that Ducas–Pulles concerns the **dual** attack's score distribution,
while Bernstein's mechanism is on the **primal** side. They are different
objects and are not merged here.

---

## 5. Protocol deviations and anomalies

1. **Deviation — source substitution for (i).** The handoff names ePrint
   2022/1580. That URL's PDF returned 403; the paper was read from the author's
   own site at `cr.yp.to`, version-matched to the ePrint History and to the
   ePrint abstract. Recorded rather than silently substituted.
2. **Deviation — (iv) read from an unattested local copy.** See §4.0. Verified
   by 1352-character normalised abstract identity against the live landing page,
   but not fetched by me.
3. **Anomaly — in-repo provenance gap.** `inputs/MLKEM-DUAL-SOURCES-20260802/`
   contains verbatim Ducas–Pulles body text
   (`ducas_pulles_score_loci.txt`) while its own `provenance.json` records the
   PDF as `unretrieved` / 403. Reported; outside write scope.
4. **Anomaly — the handoff carried no `inference` block at task start**
   (commit `096b9256b`), although AGENTS.md's required envelope specifies one.
   `receipt.json` recorded `executor-implementation` as the role default from
   `orchestration/model-policies.yaml` (`role_defaults.executor`) together with
   the resolved model and `fallback_used: true`. **Mid-task the Coordinator
   committed `b0a72b920`**, which added the block to this handoff: `policy:
   executor-implementation`, `reasoning_effort: null`, `fallback_allowed:
   true`, `degraded_allowed: false`, `independent_session_required: false`. It
   confirms the recorded policy and authorises the fallback. Both states are
   kept in `receipt.json`; neither overwrites the other.
5. **Anomaly — pre-batch screen's tag list for `KN-LIT-4974` was incomplete.**
   The handoff quotes `[dlp, pairing, pollard-rho, quantum, survey, symmetric]`;
   the file carries `[dlp, lattice, pairing, pollard-rho, provable-security,
   quantum, survey, symmetric]`. See `corpus_hygiene.json`.
6. **Scope-corrective observation.** The `downloads/…` symptom is **not**
   specific to `KN-LIT-4974`: 7,421 of 7,809 literature entries name
   `downloads/` paths, and `downloads/` does not exist and was never tracked in
   git. Quantified in `corpus_hygiene.json`.
7. **Rate limiting.** Semantic Scholar (429) and the Wayback availability API
   (429) were unavailable during this task, which limited the alternate-source
   search for (ii) and (iii). Recorded as an infrastructure condition, not as
   evidence that no copy exists.
8. **Anomaly — HEAD advanced during execution**, from `096b9256b` to
   `b0a72b920`, by the concurrent Coordinator commit noted in item 4. That
   commit touched only the batch `dispatch_queue.json`; no knowledge entry,
   ledger record, or input package this task read as evidence was changed.
   **Every measurement, grep, count and sha256 in these deliverables was taken
   at `096b9256b`**, and that is the revision to reproduce from.

## 6. What remains OPEN after this task

- **ePrint 2021/1351 body.** Unread. Required before the §3.4 verdict is
  treated as settled, and required to check Bernstein's [47, p. 3] and
  [47, fn. 2] quotations.
- **Post-2023-03-17 developments** on the DHKLS multi-target claim: unchecked.
- **ePrint 2026/1364 body.** Unread; the `p(β)` object-identity question in §2
  cannot be answered from the abstract.
- **`KN-LIT-4974` supersession.** Proposal drafted in `corpus_hygiene.json`;
  minting and `superseded_by` are the curator's/Coordinator's action, not mine.
