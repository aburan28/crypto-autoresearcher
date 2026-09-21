# TASK-20260823-d1cb76 — high-rank Q(t) base families for GOAL-ECQ-002

## PROVENANCE OF THIS FILE — read before citing it

This narrative was produced by the idea-generator subagent executing
TASK-20260823-d1cb76. It was NOT written to disk by that subagent: it reported
two attempts to write this path, both refused by its runtime with "Subagents
should return findings as text, not write report files". It therefore returned
the narrative as its output record, and the ORCHESTRATING SESSION transcribed it
here so that a declared artifact of the task is not silently missing.

Three consequences, stated so no later reader has to guess:

  - Authorship is the subagent's; the transcription is the orchestrator's.
  - This file was written AFTER the subagent terminated. It is not evidence of
    what the subagent had on disk at any point during its run.
  - The machine-readable deliverable candidate_families.json WAS written by the
    subagent itself and is the authoritative artifact. Where this file and that
    JSON disagree, the JSON wins.

Task: TASK-20260823-d1cb76. Role: idea-generator. Goal: GOAL-ECQ-002 (criterion
C2). Hypothesis served: H-ECQ-d60d07. Batch: BATCH-f2341e.

Requested inference policy `research-deep`; the subagent reported it was answered
by `claude-opus-5` at reasoning effort `high`, with no fallback and no degraded
requirement, i.e. the policy was honoured.

---

## 0. The session constraint that shapes everything below — read this first

**This session had no code-execution tool.** Available tools: Read, Grep, Glob,
Write, WebSearch, WebFetch, SendMessage. No shell, no PARI/GP, no cypari, no
Sage, no Python. `Read` additionally refused PDF rendering (`pdftoppm is not
installed`), so scanned journal articles could not be OCR'd.

Consequences, stated plainly rather than worked around:

- **No rank, regulator, minimal model, or naive height was computed here.** Any
  number below that is not a citation is either hand arithmetic or a labelled
  estimate.
- **"Verified here" means exactly three things**: (i) a source was retrieved over
  the network and its identifier recorded; (ii) a hand computation a reader can
  redo on paper — degree bookkeeping for the Shioda-Tate degree `d`, and
  leading-coefficient consistency checks; (iii) two independently prompted
  extractions of the same source text agreed digit-for-digit.
- The polynomial-identity check "does this published section actually lie on this
  curve" — which the handoff names as the minimum — **could not be run**, except
  in the one case where it reduced to two integer coefficients by hand. That case
  is reported in section 3, and it **failed**.

The half of the task that did not need compute (retrieval, field discipline,
degree/ceiling bookkeeping, choosing the base) is done. The half that needed
compute is specified precisely enough for the executor to run in minutes.

## 1. What I recommend as the base, and why

**Recommendation: `MESTRE-1991-QT11` — regenerate Mestre's rank >= 11 (and >= 12)
family over Q(T) inside this repo from the published construction, rather than
transcribing anybody's printed equation.**

The construction, exactly as printed in arXiv:math/0406579 section 1 (Arms,
Lozano-Robledo, Miller), citing Mestre's two 1991 CRAS notes:

1. `q(x) = prod_{i=1}^{6} (x - a_i)` for a 6-tuple of integers `a_i`.
2. `p(x,T) = q(x - T) q(x + T)`, degree 12 in `x`.
3. There exist `g(x,T)` of degree 6 in `x` and `r(x,T)` of degree <= 5 in `x`
   with `p(x,T) = g(x,T)^2 - r(x,T)`.
4. The curve is `y^2 = r(x,T)` over **Q(T)**.
5. When `deg_x r` is 3 or 4 the twelve points `P_{+-i}(T) = (+-T + a_i, g(+-T + a_i))`
   lie on it.
6. Two published working 6-tuples: `(-17, -16, 10, 11, 14, 17)` and
   `(399, 380, 352, 47, 4, 0)`.

Four reasons this dominates every alternative for *this* campaign:

- **No transcription risk at all.** Every other candidate requires copying
  20-digit integers out of a scan or a PDF text layer. Here the inputs are six
  small integers and the rest is deterministic polynomial algebra. The one family
  I did transcribe failed its consistency check (section 3) — that is the
  empirical case for avoiding transcription entirely.
- **The sections are free and their validity is a one-line identity.** Because
  `p(+-T + a_i, T) = 0` by construction, `g(+-T+a_i)^2 = r(+-T+a_i, T)` holds
  *identically in T*. Re-certifying "the claimed sections lie on the curve"
  collapses to the single identity `p = g^2 - r`, which is how `g` and `r` were
  produced. No point search, no luck.
- **It breaks the cap by 3.** Rank >= 11 over Q(T) against the rank-8 ceiling
  that closed GOAL-ECQ-001. Shioda-Tate then forces `d >= 2` unconditionally
  (`10d - 2 >= 11`), so the object is provably not a rational elliptic surface.
- **Its coefficients are as small as any r > 8 family is likely to get.** The
  tuple `(-17,-16,10,11,14,17)` has entries under 20. Everything else either
  starts at 10^18 (Nagao) or does not exist in printed form (Kihara, Elkies).

**Second choice, and the higher prize: `NAGAO-1994`, rank exactly 12 over Q(t).**
Worth one focused unblocking task (section 3): 12 > 11, and its rank is *exactly*
known from a peer source rather than asserted in a title.

## 2. Ranks over Q(t) versus over Q-bar(t)

| family | rank over **Q(t)** | rank over **Q-bar(t)** | `d` | ceiling `10d-2` | over Q |
|---|---|---|---|---|---|
| MESTRE-1991-QT11 | >= 11 (>= 12 companion note) | >= 11 (definitional) | >= 2 | >= 18 | — |
| NAGAO-1994 | **exactly 12** | **exactly 13** | 2 (K3) | 18 | 17 max |
| KIHARA-2001-QT14 | >= 14 (title only) | >= 14 (definitional) | >= 2 | >= 18 | 17 max if K3 |
| ELKIES-2006-QT18 | >= 18 | >= 18 | >= 2, probably >= 3 | 18 at d=2, 28 at d=3 | — |
| ELKIES-K3-17 | 17 | **unknown** (17 or 18; not retrieved) | 2 | 18 | 17 |
| KLOOSTERMAN-2005-GEOM15 | **unknown**, only <= 15 | exactly 15 | 2 (verified here) | 18 | — |
| KUWATA/KLOOSTERMAN pi_6 | **<= 11** (published bound) | 16 + h | 2 | 18 | — |
| INTERNAL-BASECHANGE-K3 | 8 + rank(twist) | >= same | 2 (verified here) | 18 | — |

Three load-bearing points:

- **Nagao is 12 over Q(t), not 13.** Scholten (arXiv:math/9709235) Theorem 2:
  `rank E(Q-bar(t)) = 13` exactly; Corollary 1: `rank E(Q(t)) = 12` exactly. The
  handoff already said this; this task confirms it from a retrievable source **and
  adds a discrepancy**: Nagao's own paper is *titled* "An example of elliptic
  curve over Q(T) with rank >= 13". Read literally, the title and Corollary 1
  disagree. I could not open Nagao's text (scan, no OCR), so I did not resolve it.
  **Use 12. Do not average.**
- **Kloosterman's rank 15 is geometric** — the paper's own title says "geometric
  Mordell-Weil rank 15". Nothing about Q(t) may be inferred beyond
  `rank_{Q(t)} <= 15`. Its coefficients are tiny, which makes it tempting; that is
  exactly the trap this column exists to catch.
- **Kuwata's pi_6 is the published proof that the gap is real and large**:
  geometric rank `16 + h` versus at most 11 Q-rational sections (Kloosterman,
  arXiv:math/0502017, Prop. 2.5). A campaign that reads geometric rank as Q(t)
  rank inflates its base by up to 7 here, not by one.

No family claims a rank above its own Shioda-Tate ceiling. The near-miss to watch
is ELKIES-2006-QT18: rank 18 at `d = 2` would sit *exactly* on the K3 geometric
ceiling, and arXiv:0709.2908 states no elliptic K3 has MW rank 18 over Q(T). Two
targeted extractions of that paper returned mutually inconsistent readings of this
point; flagged as unresolved in the JSON, not papered over.

## 3. What I re-derived versus what I am citing

### Re-derived here (hand algebra, reproducible on paper)

- **`d >= ceil((r+2)/10)` for every family**, from Shioda-Tate. Needs no equation,
  and gives `d >= 2` — cap broken — for Mestre, Nagao, Kihara and Elkies alike.
- **Nagao's `d = 2` (K3), conditional on the transcription.** Coefficient
  `t`-degrees `(2,2,4,4,6)` on `x^4...x^0` give quartic invariants `I` of degree
  <= 8 and `J` of degree <= 12, so `deg A <= 8`, `deg B <= 12`, so `d <= 2`. With
  `d >= 2` from rank 13, `d = 2`, ceiling 18, 17 over Q.
- **Kloosterman's `d = 2`, unconditionally**: `deg A = 8 > 4`, `deg B = 10`, so
  `d = max(ceil(8/4), ceil(10/6)) = 2` and `d = 1` is excluded.
- **Mestre's predicted `T`-degrees `(6,7,8,9,10)`** on `(r_4,...,r_0)` by a
  weighted-degree argument, giving `deg A <= 16`, `deg B <= 24`, `d <= 4` before
  minimalisation. My derivation, not the paper's; the executor's computation
  supersedes it.
- **A failed consistency check on Nagao — the most useful negative here.**
  Substituting `x = (t+703)/15` into the transcribed quartic and clearing `15^4`:

  `9*N(t)^2 = c_4(t)(t+703)^4 + 15c_3(t)(t+703)^3 + 225c_2(t)(t+703)^2 + 3375c_1(t)(t+703) + 50625c_0(t)`,
  with `N(t) = -224t^3 - 844t^2 + 900484t + 2161725`.

  Both sides degree 6. The `t^6` coefficients are **451 584** (left) versus
  **703 343 886 336** (right, = 14 017 536 - 6 307 891 200 + 709 637 760 000). The
  `t^5` coefficients are **3 403 008** versus **5 300 198 572 032**. It fails at
  two independent coefficients, by factors that are not squares and so are not
  absorbed by any rescaling.

  **What this does and does not mean.** It does *not* mean Scholten or Nagao is
  wrong. It means this session's retrieval pipeline (PDF text layer -> LLM
  extraction) produced an equation and a point that are mutually inconsistent —
  corrupted, or belonging to different models/parameters (Scholten's abstract uses
  `z` as the function-field variable, so a variable mismatch is live). A secondary
  tell points the same way: the transcribed quartic contains **only even powers of
  `t`** while the point contains odd powers — precisely the pattern an extractor
  that dropped odd-power terms would leave. **The transcription is recorded in the
  JSON and marked unusable.** Nothing downstream may specialise it.

### Cited, not verified here

Every rank figure in section 2 without exception; Mestre's construction as printed
in arXiv:math/0406579 section 1 (I read that paper's full text; I did **not** open
the CRAS notes, so Mestre's extra conditions for rank >= 12 are not in hand);
Elkies' K3 ceiling refinement (18 over C, 17 over Q); Kuwata's Theorem 2.1 and
Kloosterman's Prop. 2.5.

### Could not be obtained at all

- **Kihara 2001 (rank >= 14 over Q(t))** — bibliographically confirmed (Proc.
  Japan Acad. Ser. A 77 (2001) 50-51) but the article is a scan and no OCR was
  available. Per the handoff constraint, reported as **unavailable**; no equation
  offered, none reconstructed from memory. Its DOI was *not* confirmed — do not
  cite one from this task.
- **Elkies' rank-18 Q(t) and rank-17 K3 Weierstrass equations** — not printed in
  arXiv:0709.2908. Only the parametrising sextic `u^2 = 16t^6 - 19t^4 + 88t^2 - 48`
  and the construction were retrieved. (Two renderings of the `|t| = 14/13` point's
  `|u|` disagreed; both recorded, neither endorsed.)
- **Nagao's 12 generators** — Scholten defers them to Nagao [5] and Mestre [4];
  only one candidate point surfaced and it failed the check above.
- **Kloosterman's Kuwata generators** — referred by the paper to Maple worksheets,
  not obtained.

## 4. The proposal record

The full YAML proposal record as returned by the subagent is reproduced in
`candidate_families.json` and in the batch receipt. Its identifier is deliberately
`PROPOSED-NOT-ALLOCATED`: the subagent's write_scope forbids writing to
`ledger/proposals/`, and minting an `IDEA-*` id is a Coordinator act. Key fields:

- **title**: Regenerate Mestre's rank >= 11 Q(T) family in-repo as the
  GOAL-ECQ-002 base, and measure the (rank, naive height) frontier it actually
  reaches.
- **claim**: rank >= 9 over Q(t) certified *here* by specialising at a single good
  T0 and proving the specialised points independent by exact descent plus
  regulator. `>= 11` is Mestre's claim and is what the certification is expected,
  but not required, to reproduce.
- **mechanism**: specialisation `E(Q(T)) -> E_{T0}(Q)` is a group homomorphism, so
  independence of the IMAGES implies independence of the sections. A rank lower
  bound over Q(t) then follows from one finite computation over Q with no appeal
  to Silverman's theorem and no exceptional-set caveat.
- **quantifier order**: EXISTS a 6-tuple and EXISTS T0 such that the twelve points
  span rank >= 9; THEREFORE FOR ALL T the sections span rank >= 9. The certificate
  is existential downstairs and universal upstairs, and it is the homomorphism
  property that reverses it.
- **method ceiling**: cannot reach rank 18 over Q(t), which needs `d >= 3`.
- **nearby-object control**: run the identical pipeline on a 6-tuple in general
  position that is NOT one of Mestre's published tuples. If it also returns rank
  >= 11, the published tuples are not doing the work and the construction is being
  misread.
- **baseline control**: re-certify the existing GOAL-ECQ-001 rank-8 base through
  the same pipeline and confirm it returns 8, not 9. A pipeline that reports 9 on
  a provably-capped-at-8 surface is broken.

## 5. The cheapest check that would falsify the recommendation

**Run the naive height of the minimal model before running anything else.**

Build the Mestre family, specialise at `T0 = 1, 2, 3, 5`, minimalise, print
`(certified rank, naive height)`. It costs seconds and discriminates between two
explanations the campaign currently cannot tell apart:

- **(a) "Generic rank is the lever."** Rank >= 11 at heights in the 60-120 range
  => H-ECQ-d60d07's mechanism is intact: rank bought from the base arrives cheap
  in size, and the r >= 15 cell at height < 118.770 is a real target.
- **(b) "High generic rank is intrinsically large."** Heights above ~150 while
  rank sits at 11-12 => the mechanism is wrong in the way that matters: the height
  cost of a `d >= 2` base swamps the rank it buys, and the honest C1 deliverable
  becomes a measured (rank, height) frontier plus the statement that this lever
  does not reach that cell.

A pre-compute reason to take (b) seriously, recorded as an estimate and **not** a
measurement: calibrating from the pre-registered frontier, the rank-30 curve's
~63-digit coefficients at naive height 442.085 are consistent with
`h ~ log max(|a_4|^3, |a_6|^2)`, so `h < 118.770` needs `|a_4| <~ 1.6 x 10^17`.
Nagao's transcribed quartic already carries coefficients up to `6.5 x 10^18`
*before* passing to Weierstrass form, where `-27I` and `-27J` push them toward
`10^37` and the height toward ~250 — roughly double the target. Against that,
those coefficients carry visible content (`14 017 536 = 2^10 * 3^4 * 13^2`, and
`330 112 972 800 = 14 017 536 x 23 550` exactly), so minimalisation may remove a
lot. **Which way it goes is a one-minute computation and nobody in this program
has run it. Run it first.**

Second-cheapest, falsifying the *recommendation* specifically: assert
`p = g^2 - r` symbolically and print `deg_x r`. If it is 5 for both published
6-tuples, the construction as retrieved does not give an elliptic curve and
MESTRE-1991-QT11 must be withdrawn in favour of unblocking Nagao.

## 6. Honest accounting (docs/inventor-protocol.md section 5)

**Objects considered.** The tracked object in every candidate here is *a section
of an elliptic surface, followed through specialisation* — the projection
`E(Q(t)) -> E_{T0}(Q)`. It passes the lossy-projection test: it discards all
information about the section at every other fibre, keeps only the value at `T0`,
and yet the group law is preserved exactly, so the retained part propagates
deterministically and independence transfers *upward*. That asymmetry — the
projection loses almost everything but reflects independence backwards — is why a
finite computation can certify an infinite statement. Objects considered and set
aside: the Neron-Severi lattice with its Shioda-Tate decomposition (used only for
ceilings here, since computing rho for a K3 is the expensive step these papers
spend their pages on); the Mordell-Weil *lattice* with its height pairing (used as
the independence certificate, not as the tracked object); and the Galois
eigenspace decomposition under `s -> -s` of a quadratic base change (the
INTERNAL-BASECHANGE-K3 entry), which is the same algebraic independence
certificate already implemented in
`experiments/EXP-ECRANK-e1e30e/source/twist_family.py`.

**dominated_by.**
- Research claim: `N. D. Elkies (2006), generic rank >= 18 over Q(t)` per Dujella's
  G(T) table. Also dominating: Kihara 2001 (>= 14) and Nagao 1994 (12 over Q(t), 13
  over Q-bar(t)). The recommended base (>= 11) is dominated on rank by all three. I
  checked every row of the Q(t) frontier I could retrieve — Neron (8,9,10), Mestre
  (11,12), Nagao (13 geometric / 12 rational), Mestre and Kihara (14), Elkies (17,
  18) — and there is no row on which this proposal is not dominated. It is **not**
  dominated on *reproducibility inside this repository*, which is the axis
  GOAL-ECQ-002 C2 actually scores, and that is the entire argument for it.
- Campaign claim (C1, the ICARM cell): `dominated_by: null` is **not** assertable
  and is not asserted — no curve was produced, so the correct entry is
  `n/a (no result claimed)`.

**sota_delta, quantitatively.** Generic rank over Q(t): recommended base >= 11 vs
best known >= 18 -> **-7**. Vs the highest exactly-known Q(t) rank with a peer
proof (Nagao, 12) -> **-1**. Vs this program's current base (GOAL-ECQ-001, rank 8,
`d = 1`) -> **+3**, and `d` moves 1 -> >= 2, so the ceiling moves 8 -> >= 18. On
the ICARM axis: **0** — nothing was computed, no cell moved, and the r >= 15
minimum naive height stands at 118.770 (curve_id 276, Kameron Bettridge),
unchanged from the pre-registered snapshot `118db069...cadc59`.

**Closures enumerated, with mechanisms.** None claims a lane is dead; each names a
*retrieval* obstruction with a mechanism and an unblocking route:

1. *Kihara 2001, rank >= 14 over Q(t)* — closed **for this session only**.
   Mechanism: Project Euclid serves Proc. Japan Acad. as CCITTFax-encoded scans and
   this session had no OCR (`pdftoppm` absent, `Read` refuses PDFs). Unblock: any
   session with poppler + OCR, or an institutional copy.
2. *Elkies rank-18 Q(t) and rank-17 K3 equations* — closed. Mechanism: not printed
   in arXiv:0709.2908, a 14-page extended abstract; the surfaces were distributed
   as data, not displayed equations. Unblock: Elkies' own files / the 2006
   NMBRTHRY postings, or reconstructing the K3 from the Shimura-curve point
   `|t| = 14/13` — a research project, not a retrieval.
3. *Verbatim bulk transcription through WebFetch* — closed. Mechanism: the fetching
   model enforces a quotation limit and refuses section-length reproduction; only
   narrowly targeted question-shaped extraction returns equations, and it is not
   digit-reliable (section 3 proves this concretely). Unblock: `pdftotext` in a
   session with a shell.
4. *Certifying anything computationally in an idea-generator session* — closed by
   tool surface, not by mathematics.

**Open directions for the next session.**

- Unblock Nagao with a real text extractor and re-run the two-coefficient
  consistency check symbolically before trusting anything. Rank 12 over Q(t) with
  its exact value peer-proved is the best base on the table if the digits can be
  had.
- Probe `KLOOSTERMAN-2005-GEOM15`
  (`y^2 = x^3 + 2(t^8+14t^4+1)x + 4t^2(t^8+6t^4+1)`) cheaply: certified rank of
  `E_t(Q)` for `t = 1..20`. Single-digit coefficients, so if its Q(t)-rank were
  above 8 it would be the ideal low-height base. Expected outcome is a small
  Q(t)-rank — still worth ten minutes, because it is the only family in the corpus
  where "tiny coefficients" and "geometric rank 15" coexist.
- Settle whether Kuwata's pi_6 can be arranged over Q so that >= 9 of the <= 11
  possible Q-rational sections are realised (Kloosterman Prop. 2.5 permits it;
  nobody here has tried). Needs the Maple worksheets the paper refers to.
- Pursue `INTERNAL-BASECHANGE-K3`: quadratic base change `t = s^2` of the existing
  rank-8 surface, needing only that the twist by `t` have one non-torsion section.
  Zero retrieval risk, smallest possible coefficients, and eight of the nine
  required sections are already certified in this repo.
- Resolve the ELKIES-2006-QT18 degree discrepancy (K3 by quadratic base change vs
  no-rank-18-K3-over-Q) from the PDF. Either way it fixes the ceiling that bounds
  every ambition above rank 17.

---

**Completion gate check (as returned by the subagent):** every family reports rank
over Q(t) and over Q-bar(t) separately (section 2 and JSON) — yes; every family
reports `d` and `10d-2` with its derivation — yes; every claim is split
verified-here vs cited, with a retrievable citation — yes; a recommended base
family is named (MESTRE-1991-QT11), with the honest caveat that its exact
coefficients were **not** computed in this session and that no family met all
three of "rank > 8 over Q(t) + digit-verified coefficients + sections in hand" —
yes. No hypothesis or goal status was changed; nothing was committed; nothing was
written outside the assigned write scope.
