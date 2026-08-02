---
id: KN-LIT-7670
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
tags: [hawk, lattice-isomorphism-problem, module-lip, nrd-pip, principal-ideal-problem, quaternion, lenstra-silverberg, subfield-attack, heuristic, key-recovery, unverified-heuristic, pqc, cryptanalysis]
confidence: reported
citation_verified: web
added: "2026-08-01"
superseded_by: KN-LIT-7674
---

> **Superseded 2026-08-02 by [[KN-LIT-7674]].** This entry records the paper's
> 30/06 update as "truncated mid-sentence in the retrieved record" and therefore
> stops before the authors' actual retraction. **The source was never truncated** —
> the ePrint abstract is 2031 characters, complete, unchanged since before this
> entry was written. The truncation was an artifact of a 1600-character display cap
> in this program's own extraction script, recorded as a property of the source.
> The missing text states that "the main algorithm appears to run in
> **super-polynomial time**", names the cause (fractional ideals omitted from a
> count of ideals of norm `q'` in `O_F`), and adds that **Heuristics 1-3 have been
> independently experimentally verified**. Cite KN-LIT-7674. Body left unedited per
> the immutability rule; see `ledger/corrections/CORR-20260802-008.yaml`.

## Contribution
A **classical algorithm claimed to recover the HAWK secret key in probabilistic
polynomial time, assuming four number-theoretic heuristics.**

HAWK is a signature scheme built on the **lattice isomorphism problem (LIP)**. The
algorithm's pivot is the **Eurocrypt 2025 reduction from the rank-2 module-LIP instances
underlying HAWK to nrd-PIP** — the same reduction [[KN-LIT-7647]] relayed as the reason
quaternion-order PIP had drawn attention.

The method: conjugate the HAWK public Gram matrix `G` by a random lower-triangular
unimodular `U` with **short** entries, forming `G' := U*GU`, then test whether the
`O`-nrd-PIP instance attached to `G'` is **unusually easy**. For a non-negligible
proportion of such `G'`, the **Lenstra–Silverberg algorithm** solves the corresponding
`O`-nrd-PIP instance via a **subfield approach**. Resampling `U` until such an instance
appears — re-randomising the nrd-PIP instance while holding the module-LIP instance
fixed — then yields a valid HAWK private key.

## Key claims (as reported) — and the authors' own retraction

The authors are explicit about the claim's status, and this entry preserves that
exactly:

- **"At the time of writing, we do not claim that HAWK is broken, as we have not yet
  verified these heuristics experimentally."** They add that the heuristics seem very
  plausible and that they hope to verify with an implementation.
- **Update (30/06)**: following discussions with Daniel Apon and Markku-Juhani
  Saarinen, the authors **acknowledge that Heuristic 4 is insufficient to conclude that
  the main algorithm runs in** [the retrieved abstract is truncated here — the sentence
  is cut mid-clause, and this entry does not complete it].

So the record is: **a claimed polynomial-time key-recovery algorithm, resting on four
heuristics, one of which the authors have publicly conceded is not sufficient for the
stated running-time conclusion.** That is not a break, and this entry does not treat it
as one.

## Relevance to this program
**This is the sweep's most consequential entry for the thread opened on 2026-08-01**, and
it changes the state of [[KN-OPEN-024]].

That open problem asked whether the rank-1 (quaternion-order) PIP inherits the
tractability [[KN-LIT-7641]] showed for `M_g(O)`, `g ≥ 2`, and flagged the Eurocrypt 2025
module-LIP → nrd-PIP reduction as the cheapest thing to verify because it would decide
whether quaternion-order PIP sits upstream of HAWK. **This paper is that reduction being
used as an attack**, by an overlapping author set — Nelson and Mendelsohn also wrote
[[KN-LIT-7647]] (SoliloQuat, which *assumes* SG-PIP in quaternion orders is hard), and
Cong Ling also wrote [[KN-LIT-7648]] (the DEFI LIP break). The same small group is
simultaneously proposing schemes on this assumption and attacking it.

Three things follow, none of them a security conclusion:

1. **`KN-OPEN-024`'s question 2 is live, not academic.** The nrd-PIP route from a
   deployed lattice signature is real enough that a concrete algorithm has been written
   against it.
2. **The `unusually easy instance` structure is the reusable idea.** Rather than solving
   the hard instance, re-randomise until a *tractable* instance of the same underlying
   problem appears, then solve that. This is a search over instance representations, and
   it is the kind of move `docs/inventor-protocol.md` asks generators to look for.
   Whether an ECDLP analogue exists is not asserted here.
3. **The retraction is the model behaviour.** An author group that publishes a
   heuristic-dependent break, then publicly narrows the claim when a heuristic is
   challenged, is doing exactly what `AGENTS.md` rule 4 and the claim tiers require.
   Cite this entry as an example of the norm, alongside [[KN-LIT-7669]]'s explicit "does
   not break Dilithium."

**No assessment of HAWK's security is made here, in either direction.** Note also
[[KN-LIT-7648]] reports HAWK *unaffected* by its own definite/indefinite LIP techniques
— a different attack route, also unverified by this program.

**Does not bear on the ECDLP.**

## Not verified here
Full paper not read. Claims relayed from the ePrint abstract page for report 2026/1318,
retrieved 2026-08-01 (hence `confidence: reported`); **the abstract is truncated mid-
sentence in the retrieved record, inside the 30/06 update about Heuristic 4.** Citation
checked against the ePrint record: title, four authors, report number, year 2026.

NOT verified here: the algorithm; any of the four heuristics; the proportion of `G'` for
which the nrd-PIP instance is easy; the applicability of Lenstra–Silverberg or the
subfield approach; the polynomial-time claim; and the exact content and scope of the
30/06 acknowledgement, **which this entry deliberately leaves incomplete rather than
guess at**. Anyone relying on this thread must read the current version of 2026/1318
directly — a heuristic-dependent claim with a live public correction is exactly the case
where an abstract-level record is insufficient.
