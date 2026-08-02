---
id: KN-LIT-7674
type: literature
title: "Cryptanalysis of HAWK: a Guessing Game"
authors:
  - "Ben Nelson"
  - "Joshua Limbrey"
  - "Cong Ling"
  - "Andrew Mendelsohn"
year: 2026
venue: "IACR Cryptology ePrint Archive, Report 2026/1318"
identifiers:
  eprint: "iacr:2026/1318"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1318"
tags: [hawk, lattice-isomorphism-problem, module-lip, nrd-pip, principal-ideal-problem, quaternion, lenstra-silverberg, subfield-attack, heuristic, retracted-claim, super-polynomial, key-recovery, pqc, cryptanalysis, lattice]
confidence: reported
citation_verified: read
added: "2026-08-02"
supersedes: KN-LIT-7670
superseded_by: null
---

> **Correction entry.** This supersedes [[KN-LIT-7670]], which records the paper's
> 30/06 update as "truncated mid-sentence in the retrieved record" and therefore
> leaves the authors' retraction incomplete. **The abstract was never truncated.**
> The ePrint page is 18133 bytes and the abstract is 2031 characters, complete,
> and unchanged since before that entry was written (OAI datestamp `2026-07-05`).
> The truncation was introduced by a **1600-character display cap in this
> program's own extraction script**, and was then recorded as a property of the
> source. See `ledger/corrections/CORR-20260802-004.yaml`.
>
> The omitted text is decision-critical: it contains the authors' withdrawal of
> the polynomial-time claim. It is transcribed in full below.

## Contribution
A classical algorithm for HAWK secret-key recovery, routed through the Eurocrypt 2025
reduction from HAWK's rank-2 **module-LIP** instances to **nrd-PIP**. The public Gram
matrix `G` is conjugated by a random lower-triangular unimodular `U` with short
entries to form `G' := U*GU`; for a claimed non-negligible proportion of such `G'`
the attached `O`-nrd-PIP instance is "unusually easy" and yields to the
**Lenstra–Silverberg** algorithm via a subfield approach. Resampling `U` until such
an instance appears — re-randomising the nrd-PIP instance while holding the
module-LIP instance fixed — then recovers a valid HAWK private key.

## The 30/06 update — verbatim and complete

> "Update (30/06): Following discussions with Daniel Apon and Markku-Juhani
> Saarinen, we acknowledge that Heuristic 4 is insufficient to conclude that the
> main algorithm runs in polynomial time, **and in fact the main algorithm appears
> to run in super-polynomial time.** This mistake originates from the count of
> ideals of norm $q'$ in $\mathcal{O}_F$: one must include fractional ideals in
> this count, of which there are many. **We note as an aside that Heuristics 1-3
> have been independently experimentally verified.** We would also like to thank
> the HAWK team and Alice Pellet-Mary for their responses to our work."

And, from the body of the abstract, the authors' own prior statement of status:

> "At the time of writing, we do not claim that HAWK is broken, as we have not yet
> verified these heuristics experimentally. On the other hand, these heuristics seem
> to be very plausible, and we hope to be able to verify this in the future with an
> implementation of our algorithm."

## What this changes

[[KN-LIT-7670]] recorded this as "a claimed polynomial-time key-recovery algorithm,
resting on four heuristics, one of which the authors have publicly conceded is not
sufficient for the stated running-time conclusion." **That understates the
retraction in one direction and overstates the damage in another.**

The accurate reading, on the complete text:

1. **The polynomial-time claim is withdrawn, not merely weakened.** The authors say
   the algorithm "appears to run in **super-polynomial time**." This is not "a gap in
   a proof of polynomiality" — it is the authors' own assessment that the algorithm
   is not polynomial. **There is no live claim of a polynomial-time HAWK break from
   this paper.**
2. **The cause is named and arithmetic, not vague.** The count of ideals of norm `q'`
   in `O_F` omitted **fractional** ideals, "of which there are many." That is a
   specific, checkable error, which is why it was found by discussion rather than by
   experiment.
3. **Heuristics 1–3 have been independently experimentally verified.** This is the
   part [[KN-LIT-7670]] misses entirely, and it cuts the *other* way: three of the
   four heuristics are in better standing than that entry implies. Only Heuristic 4
   — the one governing the instance density — failed.

So the paper's contribution stands as **a real reduction pathway with a corrected,
super-polynomial cost**, not as a break and not as a discredited construction.

## Relevance to this program

Directly governs `GOAL-HAWK-001`, whose objective is framed around "the reported
classical **polynomial-time** smLIP key-recovery attack on HAWK." For **this** paper
that framing is now void by the authors' own statement. The goal's target must be
re-scoped onto the disclosed attack [[KN-LIT-7592]] (Straznickas–Weis), which is
unconditional and whose cost claim `2^{(n/2+1)+o(n)}` is exponential-but-halved
rather than polynomial — a different result of a different kind.

`KN-OPEN-027` was written against the incomplete record and its question (Q1: "do the
heuristics hold?") is now partly answered: **Heuristics 1–3 verified independently;
Heuristic 4 failed, and its failure is the reason the algorithm is super-polynomial.**
That entry needs a superseding revision; this one does not attempt it.

**A methodological point worth keeping.** The retraction came "following discussions
with Daniel Apon and Markku-Juhani Saarinen" — third-party scrutiny of a posted
preprint, resolved in under two weeks, with the authors naming the arithmetic cause
in public. That is the external analogue of the review discipline `AGENTS.md`
imposes here, and it worked.

**Does not bear on the ECDLP.**

## Not verified here
Abstract and update read in full from the ePrint record for 2026/1318, retrieved
2026-08-02 (18133 bytes; abstract 2031 chars). `citation_verified: read` is set for
**the abstract and update text only** — the PDF remains Cloudflare-gated and the
**body of the paper has not been read**. `confidence` stays `reported`.

NOT verified here: the algorithm; Heuristics 1–4 or the independent verification of
1–3; the "unusually easy" instance density; the applicability of Lenstra–Silverberg;
the fractional-ideal miscount or the super-polynomial assessment that follows from
it; and the Eurocrypt 2025 module-LIP → nrd-PIP reduction, which is relayed and is
not an entry in this corpus. **No assessment of HAWK's security is made in either
direction.**
