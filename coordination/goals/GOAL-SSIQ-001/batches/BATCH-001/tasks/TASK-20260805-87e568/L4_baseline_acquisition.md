# L4 baseline acquisition — the Delfs–Galbraith `F_p`-restricted cost, from source

**Task:** TASK-20260805-87e568 · **Goal:** GOAL-SSIQ-001 · **Batch:** BATCH-001
**Role:** executor
**Repository revision at execution:** `d8701af525b7f39a90509c715ccadf96083ad150`, clean tree.
**Compute performed:** none. Every retrieval attempt — successful or not — is in
`source_access_log.yaml` with URL, timestamp, HTTP status and SHA-256.

---

## HEADLINE

> **The published DCC paper body was NOT obtained.** SpringerLink returns HTTP 200 with a
> JavaScript bot-challenge page instead of content for the article page, the DOI redirect,
> and the content PDF; Unpaywall and OpenAlex both report the work `closed` with no
> open-access location and no repository full text. That is an **infrastructure outcome**
> (AGENTS.md rule 5) and is recorded as one, never as a mathematical finding.
>
> **The published abstract WAS obtained**, from Springer's publisher metadata as relayed by
> the Semantic Scholar Graph API, and it contains the figure:
> *"We give an algorithm to construct isogenies between supersingular curves over `F_p`
> that works in `Õ(p^{1/4})` bit operations."*
>
> **The `Õ(p^{1/4})` figure is real and is now sourced better than "relayed from an
> abstract".** It appears in three mutually independent artefacts (§2), including the
> **body** of the arXiv v1 preprint (§3), where it is stated as a *heuristic birthday-paradox*
> running time for a *high-storage bi-directional search* on the `F_p`-restricted problem.
>
> **`KN-TECH-058` RC4 — "two retrievals returned two different abstracts, one containing no
> `p^{1/4}` figure at all" — is RESOLVED, with a mechanism** (§4). No downgrade is warranted
> and none is made; and per the task's constraint, no *upgrade* of a confidence label is
> asserted here either — that is the Coordinator's call on the evidence below.

**Binding constraint, restated where the number appears:** every figure in this document is
for the **`F_p`-restricted** problem (both curves supersingular *and defined over `F_p`*).
It may **never** be cited as evidence that exponent `1/4` is reachable for the general
problem over `F_{p²}`. The source itself is explicit that it is not (§5).

---

## 1. What was being resolved

`ledger/goals/GOAL-SSIQ-001/goal.yaml`, lever `L4`, `named_obstruction_to_audit_first`:

> the `F_p` locus has size `~p^{1/2}` inside `~p/12` curves, and the `Otilde(p^{1/4})` figure
> attached to it is CONTESTED in this corpus (KN-TECH-058 RC4). Establish the true `F_p`-side
> cost from the published paper before building anything on it; a lever resting on a
> contested figure is a lever resting on nothing.

`knowledge/techniques/KN-TECH-058.md`, "What is NOT corrected here", records three open
items about this source. Their status after this task:

| item | as recorded in KN-TECH-058 | status now |
|---|---|---|
| RC4 — two retrievals, two different abstracts, one with no `p^{1/4}` | open, "*direction of the discrepancy is unknown, the likeliest explanation (an arXiv-versus-DCC version difference) is itself unverified*" | **RESOLVED with a mechanism (§4). The conjectured explanation was close but not exactly right: the split is not arXiv-vs-DCC, it is arXiv *metadata* vs arXiv *LaTeX source* — and the DCC abstract agrees with the LaTeX source.** |
| descent structure taken from ar5iv's rendering of arXiv:1310.7789, "*unverified for the published DCC version*" | open | **STILL unverified for the published DCC version** (body not obtained). Independently corroborated for the *general* problem by a peer-reviewed third source (§5). |
| "*The quantitative memory profile of the inner `F_p` search was NOT obtained*" | open | **STILL NOT OBTAINED, and now known to be absent from the preprint body text** (§3.3). An exhaustive grep of the extracted preprint for `storage`/`space`/`memory` returns no space bound for the `F_p` algorithm. |

---

## 2. The three artefacts obtained, and exactly what each says

### 2.1 Published DCC abstract — via Springer metadata relayed by Semantic Scholar

Retrieval `dg_s2`, `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1007/s10623-014-0010-1?fields=...`,
HTTP 200, SHA-256 `a332a01cd4b8bbf0db21953954590f875c15920f53b10bca29ff2ac721dad0c7`.
The returned `abstract` field carries Springer's characteristic `\documentclass[12pt]{minimal}`
LaTeX-image markup, which identifies it as the **publisher's** abstract rather than arXiv's.
With that markup stripped, verbatim:

> Let `p>3` be a prime and let `E, E′` be supersingular elliptic curves over `Fp`. We want to
> construct an isogeny `ϕ:E→E′`. The currently fastest algorithm for finding isogenies between
> supersingular elliptic curves solves this problem in the full supersingular isogeny graph
> over `Fp2`. It takes an expected `O~(p1/2)` bit operations, and also `O~(p1/2)` space, by
> performing a "meet-in-the-middle" breadth-first search in the isogeny graph. In this paper we
> consider the structure of the isogeny graph of supersingular elliptic curves over `Fp`. We
> give an algorithm to construct isogenies between supersingular curves over `Fp` that works in
> `O~(p1/4)` bit operations. We then discuss how this algorithm can be used to obtain an
> improved algorithm for the general supersingular isogeny problem.

**Bibliographic identity independently confirmed** by Crossref (`dg_crossref`, HTTP 200,
SHA-256 `f3f5bed0037130e6357339f6a04df3891c2f4996e109c85b335100ac76b4a187`):
*Designs, Codes and Cryptography*, volume 78, issue 2, pages 425–440, print date 2016-02,
DOI `10.1007/s10623-014-0010-1`. This matches `KN-LIT-078`'s recorded venue and DOI exactly.

**Scope of this artefact: an ABSTRACT, not the body.** It is a *better-sourced* abstract than
before (publisher metadata rather than an unidentified retrieval), but it is still an
abstract, and "two sources agree" is not the primary text.

### 2.2 arXiv v1 LaTeX-source abstract — via ar5iv

Retrieval `dg_ar5iv`, `https://ar5iv.labs.arxiv.org/html/1310.7789`, HTTP 200, SHA-256
`6761f976e2f6a17bab30ed2f18294d2101ae8926aecba2dc27a446996d496f95`. Abstract as rendered
from the submitted LaTeX source, verbatim:

> Let `p>3` be a prime and let `E`, `E′` be supersingular elliptic curves over `F_p`. We want to
> construct an isogeny `φ:E→E′`. The currently fastest algorithm for finding isogenies between
> supersingular elliptic curves solves this problem in the full supersingular isogeny graph
> over `F_{p²}`. It takes an expected `Õ(p^{1/2})` bit operations, and also `Õ(p^{1/2})` space,
> by performing a "meet-in-the-middle" breadth-first search in the isogeny graph. In this paper
> we consider the structure of the isogeny graph of supersingular elliptic curves over `F_p`.
> We give an algorithm to construct isogenies between supersingular curves over `F_p` that
> works in `Õ(p^{1/4})` bit operations. We then discuss how this algorithm can be used to
> obtain an improved algorithm for the general supersingular isogeny problem.

**Word-for-word identical to §2.1** (modulo Springer's math rendering). Same paper, one
preprint, one published record, one abstract text.

### 2.3 arXiv v1 METADATA abstract — the one with no `p^{1/4}`

Retrievals `dg_arxiv_abs` (`https://arxiv.org/abs/1310.7789`, HTTP 200, SHA-256
`cad7092ad9f577b6d83ef3b1295c18c8378351907428ff78bc3a53357470938d`) and `dg_arxiv_api`
(`http://export.arxiv.org/api/query?id_list=1310.7789`, HTTP 200, SHA-256
`2a5de4f2d2c6d824685cd1ff98f85f946b3bdb1d39377e982e5aed8c54a4ac1d`) return the same,
**different**, text — verbatim:

> Let `p>3` be a prime and let `E, E'` be supersingular elliptic curves over `F_p`. We want to
> construct an isogeny `phi: E --> E'`. The currently fastest algorithm for finding isogenies
> between supersingular elliptic curves solves this problem by performing a "meet-in-the-middle"
> breadth-first search in the full supersingular 2-isogeny graph over `F_{p^2}`. In this paper
> we consider the structure of the isogeny graph of supersingular elliptic curves over `F_p`.
> We give an algorithm to construct isogenies between such supersingular elliptic curves that
> **works faster than the usual algorithm**. We then discuss how this results can be used to
> obtain an improved algorithm for the general supersingular isogeny problem.

*(emphasis added)*. **No complexity figure appears anywhere in it.** The arXiv API also
reports exactly one version, `v1`, submitted `2013-10-29T12:46:51Z`, with **no
`Journal reference:` and no `Related DOI:`** field on the abs page.

---

## 3. What the preprint BODY says — the part an abstract cannot settle

Source: `dg_ar5iv` (§2.2). **This is the arXiv v1 preprint of 2013-10-29, not the published
DCC version of 2016.** Every statement below is labelled accordingly and none of it is
attributed to the published paper.

### 3.1 The `Õ(p^{1/4})` figure in the body

Section 3, verbatim:

> From both vertices we perform a breadth-first search (or a random walk in a lower storage
> version) in the graph `X(F_p, L)` whose edges are isogenies of degree `ℓ ≤ B`. Since the
> graph is connected for a big enough bound `B ≤ 6 log(|d|)²`, the algorithm invariably finds
> a path between the two vertices representing the elliptic curves. […] A very basic version
> of the **high-storage** bi-directional-search algorithm for computing a path in the subgraph
> of `X(F̄_p, L)` is given as Algorithm 1. **By the birthday paradox, the heuristic running
> time of the algorithm is `Õ(p^{1/4})` binary operations.**

*(emphasis added)*. Four properties of the figure, all from that sentence and its context:

| property | value | why it matters |
|---|---|---|
| **status** | **heuristic** ("by the birthday paradox"), not proven | it is the same evidential class as the frozen source's Heuristic 1 — a plausible model, not a theorem |
| **problem** | `F_p`-restricted: both `E_0`, `E_1` supersingular **and defined over `F_p`**, reduced to a common `F_p`-rational endomorphism ring `O_K` and placed on the surface | **not** the `F_{p²}` problem |
| **algorithm** | **high-storage** bi-directional search (Algorithm 1) | memory is not negligible; see §3.3 |
| **mechanism** | birthday collision inside the `F_p`-rational subgraph | `p^{1/4} = (p^{1/2})^{1/2}` = square root of the size of the `F_p` locus. The exponent is a *consequence of the locus size*, nothing more |

### 3.2 The mechanism is the locus size, stated by the source

Section 4, verbatim:

> Since the graph is an expander, we expect the walks to quickly be sampling uniformly from
> the graph, and so we expect to select a vertex in the subset of `j ∈ F_p` with probability
> approximately `p^{1/2}/p = 1/p^{1/2}`.

This is the source's own statement of the `L4` obstruction the goal record names ("*the
`F_p` locus has size `~p^{1/2}` inside `~p/12` curves*"), now from primary text rather than
from a program-internal restatement.

### 3.3 Memory — still not stated, and now known to be absent

An exhaustive search of the extracted preprint text for `storage`, `space` and `memory`
returns exactly five relevant occurrences: the abstract's `Õ(p^{1/2})` **space** for the
`F_{p²}` meet-in-the-middle; §1's "*the algorithm requires large storage*" (about the earlier
`[Gal99]` method); §3's "*or a random walk in a lower storage version*" and "*high-storage
bi-directional-search algorithm*"; and §4's "*low storage*"/"*little storage*" (about the
descent phase). **There is no space bound stated for the `F_p` algorithm anywhere in the
preprint body.** Remark 4 of §3 offers the alternative without analysing it:

> A better algorithm would use Pollard-style random walks (i.e., walks that are deterministic
> and memoryless, so that when two walks collide they follow the same path from that point
> onwards) and distinguished points. The details of such algorithms are given in [GHS02, GS13].

**Consequence for the corpus:** `KN-TECH-058`'s "*the quantitative memory profile of the
inner `F_p` search was NOT obtained*" remains true and is now sharper — it was not obtained
because, in the preprint at least, it is not there. Whether the published DCC version adds
one is **unknown and untested**, because the body was not obtained. Any `L4` cost model must
carry `Õ(p^{1/4})` time with **memory unstated by the source**, and must not silently assume
either `Õ(p^{1/4})` memory or polynomial memory.

---

## 4. RC4 resolved: why two retrievals returned two different abstracts

`KN-TECH-058` recorded that "*two retrievals under the identifiers `KN-LIT-078` lists
returned two different abstracts, one of which contains no `p^{1/4}` figure at all*", called
this "*a stronger sourcing defect than 'relayed'*", and noted that the likeliest explanation
— an arXiv-versus-DCC version difference — "*is itself unverified*".

**Mechanism, established:**

- arXiv holds **one** version of this paper (`v1`, 2013-10-29; `dg_arxiv_api`).
- Its **metadata abstract** — the field arXiv's abs page and API serve, entered by the
  submitter into the submission form — is the shorter text with no complexity figures (§2.3).
- Its **LaTeX source abstract** — the text actually printed in the paper — carries
  `Õ(p^{1/2})` time, `Õ(p^{1/2})` space, and `Õ(p^{1/4})` (§2.2).
- The **published Springer abstract** is word-for-word the LaTeX one (§2.1).

So the split is **not** preprint-vs-published. It is **arXiv metadata vs the paper's own
text**, and the published version sides with the paper's own text. Any retrieval that hit
the arXiv abs page or the arXiv API saw no `p^{1/4}`; any retrieval that hit ar5iv, the PDF,
or a publisher-metadata aggregator saw it. Both earlier retrievals were correct readings of
what they fetched.

Two contributing factors worth recording, since they will recur:

1. The arXiv record carries **no `Journal reference:` and no `Related DOI:`**, so nothing on
   the arXiv side points a retriever at the published version. `KN-LIT-078`'s "*The IACR
   ePrint number could NOT be confirmed*" note is consistent with this: the identifier trail
   for this paper is genuinely thin.
2. Semantic Scholar's `year` field for this record reads `2013` while `venue` reads
   *Designs, Codes and Cryptography* — a preprint/published conflation inside the aggregator
   itself. Crossref (`2016`) is the authority for the publication date.

**Per the task's constraint, no confidence label is upgraded here on the strength of
"sources agreeing".** What changed is that the defect is now *explained* rather than
*unexplained*, and that the figure now has a body-level occurrence (§3.1) rather than only
abstract-level ones. Whether that warrants a corpus change is the Coordinator's decision,
and the honest input to it is: *body obtained for the preprint, not for the published
version; figure is heuristic; memory unstated.*

---

## 5. Independent peer-reviewed corroboration of the descent cost

Retrieval `sccs_abs`, `https://eprint.iacr.org/2021/1488`, HTTP 200, SHA-256
`08edb71a330b791272f021c67f128de2a54fb682849757268090799e47729c00`. This is
Corte-Real Santos–Costello–Shi, *Accelerating the Delfs–Galbraith algorithm with fast
subfield root detection*, recorded on the page as "*A minor revision of an IACR publication
in CRYPTO 2022*" — i.e. reference **`[15]`** of the frozen source. Abstract, verbatim in the
load-bearing parts:

> We give a new algorithm for finding an isogeny from a given supersingular elliptic curve
> `E/F_{p²}` to a subfield elliptic curve `E′/F_p`, **which is the bottleneck step of the
> Delfs-Galbraith algorithm for the general supersingular isogeny problem.** […] Though the
> **asymptotic `Õ(p^{1/2})` complexity of our improved algorithm remains unchanged from that
> of the original Delfs-Galbraith algorithm**, our theoretical analysis and practical
> implementation both show a significant reduction in the runtime of the subfield search.

*(emphasis added)*. This is a peer-reviewed, openly accessible, third-party statement that
(a) the Delfs–Galbraith **general** complexity is `Õ(p^{1/2})`, and (b) the bottleneck is the
**descent to the subfield**, not the `F_p`-restricted phase. It corroborates the preprint's
own §4, verbatim:

> Run random walks in the graph from `E_0` and `E_1` until we hit a supersingular curve defined
> over `F_p`. **This step should require `Õ(p^{1/2})` steps.** Then apply the new isogeny
> algorithm for supersingular elliptic curves over `F_p`, which only requires `Õ(p^{1/4})`
> steps. […] **The second stage has no effect on the asymptotic running time.**

*(emphasis added)*.

**This is the single most decision-relevant sentence for L4, and it comes from the source
itself:** in Delfs–Galbraith's own accounting, the `p^{1/4}` phase is *asymptotically free*
and the whole cost of the general problem is the `p^{1/2}` descent. L4's
`claim_that_would_have_to_be_true` — "*a descent to the `F_p`-rational subgraph cheaper than
`p^{1/2}`*" — is therefore aimed at exactly the quantity the source says is the bottleneck,
which is the right target; and the `Õ(p^{1/4})` figure, correctly understood, contributes
**nothing** to lowering it.

**No verdict on L4 is returned here.** This deliverable is a baseline acquisition; the
lever's method-ceiling audit is not this task's scope, and the observations above are
recorded for whoever runs it.

---

## 6. Acquisition failure: every route tried for the published DCC body

| # | route | URL | HTTP | outcome |
|---|---|---|---|---|
| 1 | DOI resolver | `https://doi.org/10.1007/s10623-014-0010-1` | 200 | **blocked** — 3,038-byte JavaScript "Client Challenge" interstitial, not article content |
| 2 | SpringerLink article page | `https://link.springer.com/article/10.1007/s10623-014-0010-1` | 200 | **blocked** — byte-identical challenge page (same SHA-256 as route 1) |
| 3 | SpringerLink content PDF | `https://link.springer.com/content/pdf/10.1007/s10623-014-0010-1.pdf` | 200 | **blocked** — byte-identical challenge page (same SHA-256) |
| 4 | Crossref metadata | `https://api.crossref.org/works/10.1007/s10623-014-0010-1` | 200 | **partial** — venue/volume/pages/date confirmed; `abstract: None`; no full text |
| 5 | Unpaywall | `https://api.unpaywall.org/v2/10.1007/s10623-014-0010-1?email=…` | 200 | **negative** — `is_oa: false`, `best_oa_location: null`, `oa_locations: []` |
| 6 | OpenAlex | `https://api.openalex.org/works/doi:10.1007/s10623-014-0010-1` | 200 | **negative** — `oa_status: closed`, `any_repository_has_fulltext: false`, no `abstract_inverted_index` |
| 7 | Semantic Scholar Graph | `…/paper/DOI:10.1007/s10623-014-0010-1?fields=…` | 200 | **partial success** — publisher abstract obtained (§2.1); `openAccessPdf.status: CLOSED`, `url: ""` |
| 8 | arXiv abs page | `https://arxiv.org/abs/1310.7789` | 200 | success, but **preprint metadata only** (§2.3) |
| 9 | arXiv API | `http://export.arxiv.org/api/query?id_list=1310.7789` | 200 | success, preprint metadata; confirms **v1 is the only version** |
| 10 | ar5iv | `https://ar5iv.labs.arxiv.org/html/1310.7789` | 200 | success — **preprint body** (§3); not the published version |
| 11 | author homepage | `https://www.math.auckland.ac.nz/~sgal018/` | 200 | **negative** — page fetched and inspected; no publication list, no link to this paper |
| 12 | CORE aggregator | `https://api.core.ac.uk/v3/search/works?q=…` | **429** | **rate-limited**, zero bytes returned. Not retried; the OA question was already settled negatively by routes 5–7 |
| 13 | local PDF named by `KN-LIT-1732` | `downloads/2607.14624v1.pdf` (for the L1 source, not this one) | n/a | **absent** — the path recorded in that corpus entry does not exist in this working tree or anywhere on the filesystem. Recorded because it is a corpus-integrity observation, not because it bears on L4 |

**Routes deliberately NOT taken:** no shadow-library or paywall-circumvention route was
attempted, and none should be. Per the environment note, TLS verification was never
disabled and `HTTPS_PROXY` was never unset; the Springer challenge pages are recorded as the
infrastructure outcomes they are.

**Named routes not yet tried, for a follow-up session:** (a) Christina Delfs' PhD thesis
(Universität Oldenburg), which covers this material and is likely openly deposited — a
*corroborating* artefact, not the published version, and specifically worth trying for the
memory profile of §3.3; (b) an institutional/library route with Springer access; (c) the
Corte-Real Santos–Costello–Shi CRYPTO 2022 **PDF body** (`eprint.iacr.org/2021/1488`), which
almost certainly restates the Delfs–Galbraith costs including memory — not extracted here
because no PDF text extractor is available in this environment (`pdftotext`, `pypdf` and
`PyMuPDF` all absent; an attempted `pip install pypdf` failed with a `pyo3_runtime`
`PanicException`). That is an environment limitation, logged in `task_report.yaml`, and it
is the cheapest thing to fix before the next literature task.

---

## 7. What may and may not be claimed from this document

**May be claimed:**
- The `Õ(p^{1/4})` figure attached to Delfs–Galbraith is genuine, appears in the published
  abstract and in the preprint body, and is a **heuristic** birthday-paradox running time for
  the **`F_p`-restricted** problem using a **high-storage** bi-directional search.
- The exponent `1/4` is `(1/2)·(1/2)`: a birthday bound over an `F_p` locus of size `≍ p^{1/2}`.
- Delfs–Galbraith themselves put the **general** problem at `Õ(p^{1/2})`, with the descent as
  the bottleneck and the `F_p` phase asymptotically free; Corte-Real Santos–Costello–Shi
  (CRYPTO 2022) independently restate both points.
- `KN-TECH-058` RC4's contested-retrieval defect has an established mechanism.

**May NOT be claimed:**
- That the **published DCC body** says anything in particular. It was not obtained.
- Any memory figure for the `F_p` algorithm. None is stated in the artefacts obtained.
- **That exponent `1/4` is reachable over `F_{p²}`.** Different problem, and the same source
  says the `F_{p²}` cost is `Õ(p^{1/2})`. This prohibition is absolute under the batch
  constraints and under `KN-TECH-058`'s own "*The `F_p` figures … `NOT` superseded … must not
  be widened*" rule.
- That absence of the published body is evidence against the figure. It is not, and
  `KN-TECH-058` already forbids that inference: "*absence of a stable source is not evidence
  the figure is wrong*". No `F_p` ranking is downgraded here.
