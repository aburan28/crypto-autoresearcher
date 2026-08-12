# Knowledge Seeding Protocol

How the corpus is populated and kept trustworthy. This extends the format in
`knowledge/README.md` with the discipline specific to *seeding* — importing
external prior art so novelty checks and coordinator deduplication have
something to bite on.

The corpus is a **retrieval substrate, not an authority**. Its job is to let
the Idea Generator answer "has this been done before?" and let the
Coordinator answer "is this proposal a duplicate?" by grepping, before any
compute is spent. A corpus seeded with hallucinated citations is worse than
an empty one: it manufactures false confidence in both directions. Every rule
below exists to prevent that.

## Two-axis provenance

Each entry carries two independent honesty axes. Do not collapse them.

- **`confidence`** — about the entry's *content claims* (complexity results,
  conjectures, mechanisms):
  - `established` — textbook-level, uncontested, and you can reconstruct the
    argument. Reserved; rare for research-frontier claims.
  - `reported` — the source states it; you are relaying it. Default for any
    claim you have not personally re-derived or reproduced.
  - `unverified` — you are recording it as a lead, source unconfirmed.
- **`citation_verified`** — about the *bibliographic reference itself*,
  independent of whether you believe the content:
  - `web` — author, title, venue, year confirmed against a primary index
    (IACR ePrint, publisher DOI, DBLP, arXiv, or an open preprint repository
    listed at https://doapr.coar-repositories.org/statuses/open/) during this
    entry's creation.
  - `read` — you fetched the actual paper (PDF/abstract) and the claims in
    this entry reflect its real content, not a search snippet.
  - `false` — reference recalled from memory; **must be verified before any
    novelty judgment relies on it.**

A web-verified citation whose PDF you have not read is
`confidence: reported`, `citation_verified: web`. That is the honest ceiling
for most seed entries and is perfectly acceptable — it means "this paper
provably exists and reportedly claims X," which is exactly what a novelty
check needs.

## Literature entry format

`knowledge/literature/KN-LIT-NNN.md`:

```markdown
---
id: KN-LIT-001
type: literature
title: exact paper title
authors: [Family Given, ...]
year: YYYY
venue: journal/conference, volume(issue):pages
identifiers:
  eprint: iacr:YYYY/NNN        # or null
  doi: 10.xxxx/...             # or null
  url: https://...
tags: [semaev, index-calculus, groebner, prime-field, ...]
confidence: reported
citation_verified: web
added: YYYY-MM-DD
superseded_by: null
---

## Contribution
One-paragraph statement of what the paper establishes or proposes.

## Key claims (as reported)
- Claim, with its stated scope (field type, curve family, asymptotics).
  Mark each claim's status if the paper itself frames it as heuristic,
  conjectural, or proven.

## Relevance to this program
Which research questions / hypotheses this bears on; what it forecloses
(a proposal matching this is `known`, not novel) and what it leaves open.

## Not verified here
Anything in this entry not checked against the primary source.
```

`techniques`, `findings`, and `open-problems` use the base schema in
`knowledge/README.md`; techniques add `complexity:` and `applicability:`
where meaningful.

## Seeding process

1. **Scope the seed set.** Enumerate the foundational and directly-relevant
   prior art for the program's active areas. For ECDLP index calculus the
   spine is: summation polynomials, point-decomposition index calculus,
   subexponential extension-field results, symmetry/representation speedups,
   Gröbner-complexity analyses, the generic baseline, and at least one survey.
2. **Verify every citation before writing it.** Confirm author/title/venue/
   year against a primary index and set `citation_verified` accordingly.
   Never seed a `citation_verified: false` entry from memory and leave it.
3. **Relay content, do not launder it.** Content claims are `reported` unless
   personally reproduced (a reproduction becomes an internal `finding`, not a
   literature edit). Preserve the source's own hedges (heuristic vs. proven).
4. **Tag for retrieval.** Use consistent lowercase tags so grep works:
   `semaev`, `summation-polynomial`, `index-calculus`, `point-decomposition`,
   `groebner`, `first-fall-degree`, `degree-of-regularity`, `weil-descent`,
   `prime-field`, `binary-field`, `extension-field`, `symmetry`, `baseline`,
   `pollard-rho`, `survey`.
5. **Record open problems explicitly.** Where the literature leaves a
   quantitative question open (e.g. "does index calculus beat rho over prime
   fields?"), write a `KN-OPEN` entry so the Idea Generator proposes *into*
   the gap rather than rediscovering the closed part.
6. **Regenerate `INDEX.md`** and cross-check tags for typos that would defeat
   grep.

## Maintenance

- Upgrade `citation_verified: web → read` (and refine claims) only after
  fetching the actual source; note the upgrade in the entry body.
- Corrections supersede; never silently rewrite a claim (typo fixes excepted).
- A literature entry never becomes a `finding`. Internal reproduction of a
  literature result is a *new* `KN-FIND` entry citing both the literature ID
  and the evidence record — the two provenance classes never merge.
