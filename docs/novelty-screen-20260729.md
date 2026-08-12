# Novelty Screen — 2026-07-29

A literature screen of the four internal findings identified as the strongest
publication candidates in this repository. **None survives as novel.**

This document is a screen report, not a state transition. It recommends
novelty verdicts; only the Coordinator may record them (AGENTS.md rule 1), and
any recorded verdict supersedes rather than overwrites (rule 2). Nothing here
edits a `KN-FIND-*` entry.

## Scope and method

Screened, in the order they were ranked before the screen: **KN-FIND-006**
(Semaev/Weil-descent Macaulay rank deficit), **KN-FIND-002** (GGM simulability
of augmented ECDLP oracles), **KN-FIND-009** (endomorphism witness-lattice
degeneracy), **KN-FIND-007** (decomposition-yield conservation).

Method: targeted web search plus corpus search, followed by retrieval of the
identified prior art. **Depth limit, stated up front:** one paper was fetched
in full; the rest rest on abstracts and search-result summaries, and two PDF
fetches returned no extractable text. Every verdict below is therefore a
screen verdict at `citation_verified: web`, not a closure. The specific
readings that would settle each one are named per finding.

## Verdicts

| Finding | Recommended `novelty_status` | Decisive prior art |
|---|---|---|
| KN-FIND-006 | `known` (thin unproved residue) | KN-LIT-7604, KN-LIT-7605, KN-LIT-7607, KN-LIT-005 |
| KN-FIND-002 | `known` (superseded framework) | KN-LIT-7606 |
| KN-FIND-009 | `known` (folklore) | GLV; standard CM relation |
| KN-FIND-007 | `known` (standard counting) | KN-LIT-022 and the Gaudry/Diem line |

### KN-FIND-006 — Semaev/Weil-descent rank deficit

Three load-bearing claims, all anticipated:

1. *Systems depart from the Bardet–Faugère–Salvy semi-regular prediction.*
   Established: Petit–Quisquater (KN-LIT-005) conjectured the low degrees of
   regularity; Kosters–Yeo (KN-LIT-7604) cast doubt on the heuristic tying
   first fall degree to degree of regularity.
2. *The degree-3 mechanism* — "a subset-sum of descended quadrics degenerates
   to an **affine** form `P`, the multiplier is its exact complement, the
   relation is `P*(1+P) = 0`". KN-LIT-7604 reports first fall degree **2** for
   the Weil descent to `F_2` of `S_3` on ordinary curves, caused by "the
   existence of a group morphism to `F_2` which gives a linear polynomial
   after Weil descent". Same family, same structural source, one degree lower.
3. *Bounded in system size, hence no asymptotic leverage.* Proved:
   KN-LIT-7605 bounds the last fall degree independently of `n`, and
   KN-LIT-7607 establishes the last-fall-degree machinery and shows the first
   fall degree assumption is unsafe for exactly these systems.

Residue: `deficit(D=3) = 1`, `deficit(D=4) = 8k − 1 = 8·dim(V)`, and the
identification of the generic degree-4 syzygies as `n_q` Frobenius plus
`C(n_q,2)` Koszul. The finding itself records this as "measured-exact over
k = 3..7, **not derived**", with two mechanism hypotheses already refuted.
Five points fitting a linear form, under a headline that restates a theorem.

**Settles it:** read KN-LIT-7604 on the `F_2` descent of `S_3` and confirm
whether its group-morphism linear polynomial *is* the affine form in the
degree-3 mechanism. This is the highest-value unread item in the screen.

### KN-FIND-002 — GGM simulability of augmented oracles

Superseded by a stronger, current framework: the Structured Generic-Group
Model (KN-LIT-7606) formalises generic algorithms that exploit non-generic
group structure and proves `Ω(min{√q, 1/δ})` for exploiting a `δ` fraction of
elements, with lower bounds stated for elliptic-curve point structure. The
underlying move in KN-FIND-002 — an oracle that is a deterministic function of
public data is simulable — is the standard Shoup/Maurer simulator argument.

Independent of novelty, a **scoping defect**: "closes all jet-based ECDLP
candidates at exponent 1/2" claims more than a plain-GGM argument can deliver.
Index calculus over small-degree extension fields (KN-LIT-022) is a real
non-generic algorithm, which is why KN-LIT-7606 exists. The claim holds *in
the model*, and should say so.

**Settles it:** determine whether KN-LIT-7606's elliptic-curve-point results
already cover jet/dual-number, elliptic-net, and incidence oracles
specifically. Constructive follow-up either way: re-express the four
classifications inside that model and see whether any survives with
non-trivial `δ`.

### KN-FIND-009 — endomorphism witness-lattice degeneracy

`φ² + φ + 1 = 0` for `j = 0` curves is the defining GLV relation; the general
form `aφ²(P) + bφ(P) + cP = O` with discriminant `b² − 4ac` is standard enough
to appear in patent literature. Given the relation, `P + φ(P) + φ²(P) = O`
being a true relation carrying no discrete-log information is its immediate
consequence, and the established quantitative statement about automorphisms —
a `√|Aut|` speedup only — already says endomorphisms do not move this exponent.

This remains the best-engineered artifact in the repository: certificate
level, replayable instance, `∞`-norm first minimum exactly 1 against a
Minkowski-style prediction of `N^{1/6} ≈ 29.15`. Its value is expository, not
novel. Suggested home: a design-lessons note on why the natural endomorphism
relation lattice degenerates and what a non-degenerate construction must avoid.

### KN-FIND-007 — decomposition-yield conservation

Standard index-calculus counting. The decomposition probability is
`≈ q^(ℓk−n)/k!` (Gaudry/Diem line; KN-LIT-022 for the extension-field
setting), determined by parameter sizes and not by the shape of the factor
base. "Geometry redistributes but cannot change mean yield" restates that
identity in conservation language — a good framing, not a finding.

## The systemic cause, and it is not a missing corpus

The obvious diagnosis is that the corpus lacked these papers. It is wrong.

**KN-LIT-475 already held Huang–Kosters–Yeo, `iacr:2015/573`** — the paper
whose line proves the boundedness result KN-FIND-006 reports as a measurement.
It was present, and it was useless: authors truncated mid-affiliation
("Ming-Deh A. Huang (USC", "Michiel Kosters (TL@NTU"), the third author
dropped, a stray "?" in the title, and a body reading *"No abstract was
extractable from the first two pages of the local PDF; contribution recorded
from the title only."*

That is not one bad record. Of **7,599** literature entries, **1,939 (25.5%)**
carry that same "No abstract was extractable" body. A quarter of the corpus is
title-only, so a novelty screen searching it matches on titles alone and
silently misses any paper whose relevance lives in its content.

Two consequences worth acting on:

1. **Novelty screening belongs at proposal time, not publication time.** Four
   findings were written up, reviewed, promoted to the knowledge corpus, and
   only then screened. The cost of the correct ordering is one search per
   proposal.
2. **Stub density is a measurable corpus-health metric.** It is one grep, it
   is currently 25.5%, and it bounds how much any novelty check can be
   trusted. Backfilling the ~1,939 stubs — or at minimum those tagged
   `ecdlp` / `index-calculus` / `weil-descent` — is the highest-leverage
   corpus work available.

## What the harness got right

Every one of these four sat at `novelty_status: unverified`, because the Idea
Generator contract forbids claiming novelty from memory alone. Four
rediscoveries of known results, and not one became a novelty claim. The
distribution across the whole ledger at screen time — 7 `unverified`,
7 `adaptation`, 6 `known`, 2 `speculative`, 1 `methodological`, and zero
verified-novel — is the discipline working, not failing.

That is a measured result about the harness rather than an assertion about it,
and it belongs in any account of what this program has established.

## Changes proposed by this screen

Additive only; no finding record is modified.

- `knowledge/literature/KN-LIT-7604.md` — Kosters–Yeo, *Notes on summation
  polynomials* (arXiv:1503.08001)
- `knowledge/literature/KN-LIT-7605.md` — *On the last fall degree of Weil
  descent polynomial systems* (arXiv:2103.07282)
- `knowledge/literature/KN-LIT-7606.md` — Corrigan-Gibbs, Henzinger, Wu, *The
  Structured Generic-Group Model* (`iacr:2026/384`)
- `knowledge/literature/KN-LIT-7607.md` — Huang–Kosters–Yeo, *Last fall
  degree, HFE, and Weil descent attacks on ECDLP* (`iacr:2015/573`), full
  record superseding the stub
- `knowledge/literature/KN-LIT-475.md` — `superseded_by: KN-LIT-7607` only

IDs allocated above the maximum across `main` **and** all 66 remote branches
(max observed 7603), since unmerged branches stack literature IDs.

## For the Coordinator

Recommended, none enacted here:

1. Record `novelty_status: known` on KN-FIND-002, -006, -007, -009 by
   supersession, carrying the citations above.
2. Correct KN-FIND-002's "closed at exponent 1/2" to scope the claim to the
   generic group model.
3. Before treating KN-FIND-006 as fully closed, commission the KN-LIT-7604
   read named above — it is the one verdict most likely to be wrong and the
   one doing the most damage if it is.
