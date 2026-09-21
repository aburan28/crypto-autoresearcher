---
id: KN-LIT-7baf07
type: literature
title: "Quasipolynomial Cryptanalysis of the McEliece Cryptosystem (or: PIR Meets McEliece)"
authors:
  - "Ashrujit Ghoshal"
  - "Yuval Ishai"
  - "Aayush Jain"
  - "Nuozhou Sun"
authors_note: >-
  Affiliations AS RELAYED by the acquisition described in
  citation_verified_note, not independently checked: Ghoshal (IIT Madras),
  Ishai (Technion, AWS), Jain (Carnegie Mellon University), Sun (Carnegie
  Mellon University).
year: 2026
venue: null
identifiers:
  eprint: "iacr:2026/1630"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1630"
tags: [code-based, mceliece, classic-mceliece, goppa, structural-attack, distinguish-then-recover, quasipolynomial, pir, locally-decodable-codes, heuristic]
confidence: reported
citation_verified: web
citation_verified_note: |-
  THE ABSTRACT QUOTED IN THIS ENTRY IS A TOOL RELAY, NOT A TRANSCRIPTION, AND
  IS MATERIALLY WEAKER PROVENANCE THAN THIS CORPUS'S OWN BEST STANDARD.

  How it was obtained: the orchestrating session ran its WebFetch tool against
  the landing page https://eprint.iacr.org/2026/1630 on 2026-08-10. WebFetch
  renders a page and answers a prompt over it USING A SMALL SUMMARIZING MODEL.
  The abstract text under "Key claims (as reported)" below is therefore that
  model's output about the page, not a byte-exact transcription this program
  can re-verify. It is NOT the standard KN-LIT-c41d8b holds itself to
  (`transcription_of_full_text_at_recorded_sha256`, with the source
  independently re-acquired byte-identically at that hash by a second task).
  A reader who needs the primary object must fetch it and read it; a reader
  who needs the abstract verbatim must re-acquire the landing page, because
  this entry cannot supply it.

  FULL TEXT WAS NOT OBTAINED. Exactly three attempts were made, and these are
  their exact outcomes as reported by the session that made them:

    1. `curl -sSL -o mce2026-1630.pdf https://eprint.iacr.org/2026/1630.pdf`
       -> Cloudflare "Just a moment..." interstitial, 5402 bytes, text/html,
       no PDF bytes.
    2. `curl -sSL -A "Mozilla/5.0" ... https://eprint.iacr.org/2026/1630.pdf`
       -> HTTP 403, 5423 bytes, text/html.
       (The `...` is present in the relayed command as received; it marks
       arguments the relay did not spell out. It is not an omission made by
       this entry, and this entry does not reconstruct what it stood for.)
    3. WebFetch against https://eprint.iacr.org/2026/1630.pdf
       -> "The server returned HTTP 403 Forbidden."

  NO PDF BYTES WERE EVER RECEIVED, SO NO sha256 OF THE FULL TEXT EXISTS AND
  NONE IS RECORDED HERE. Under AGENTS.md core rule 5 that stays missing and is
  reported as missing. This reproduces, on a different report, the same
  path-scoped eprint PDF blocker GOAL-MCE-001 already records for
  iacr:2026/1232 (KN-LIT-7c4620); it is a recorded retrieval outcome and is
  never evidence about the mathematics (AGENTS.md rule 5).

  What IS verified: that a report numbered 2026/1630 with this title and these
  four authors exists on the IACR ePrint Archive, received 2026-08-07 and
  posted 2026-08-10, as rendered by the landing page. Nothing else.
added: "2026-08-10"
superseded_by: null
---

## Contribution

A claimed **classical quasipolynomial-time distinguisher for Goppa--McEliece
in the asymptotic "Classic McEliece" regime**, extended heuristically to a
ciphertext-decryption (message-recovery) attack at the same
`n^O(log n)` cost. The paper's stated origin is a *failed* attempt to build
doubly efficient private information retrieval from algebraic locally
decodable codes.

If it holds, this is a result on the assumption GOAL-MCE-001's own research
question calls the one that has produced every break in the McEliece family:
`RQ-MCE-e65b3c` scope assumption (2), "a scrambled binary Goppa
generator/parity-check matrix is indistinguishable from a random one." That is
why this entry exists on the day the report was surfaced, and it is the whole
of the claim this entry makes: **that a third party claims this.** This
program has not read the paper, has checked nothing in it, and asserts nothing
about whether it is correct.

## Key claims (as reported)

Quoted from the relayed abstract. Read `citation_verified_note` first: this is
a summarizing model's rendering of the landing page, not a transcription.

> The McEliece code-based cryptosystem, utilizing binary Goppa codes, is the
> earliest public-key encryption scheme that is still considered post-quantum
> secure. We present a simple, classical quasipolynomial-time distinguisher for
> Goppa--McEliece in the asymptotic 'Classic McEliece' regime: for code length
> n, extension degree m=Theta(log n), Goppa degree t=Theta(n/log n), and
> public-code dimension k=Theta(n), the algorithm runs in time n^O(log n) and
> distinguishes the McEliece public key from the uniform distribution over
> F_2^{k x n} with advantage 1-o(1). The distinguisher is not merely
> asymptotic: it applies to all Classic McEliece parameter sets considered in
> the NIST process and yields improved (though not yet practical) concrete
> attack estimates. Our distinguishing attack originated from a failed attempt
> to construct doubly efficient private information retrieval (PIR) protocols
> from algebraic locally decodable codes, and can be intuitively explained from
> the PIR perspective. We extend this provable algorithm to a heuristic
> n^O(log n)-time ciphertext-decryption attack that recovers the message from a
> noisy codeword.

Itemised, with the paper's own modal words preserved:

- A distinguisher, described by the abstract as **provable** ("this provable
  algorithm"), running in time `n^O(log n)`, with advantage `1-o(1)`, against
  the uniform distribution on `F_2^{k x n}`.
- Its regime, as stated: `m = Theta(log n)`, `t = Theta(n/log n)`,
  `k = Theta(n)`.
- A claim of applicability to **all Classic McEliece parameter sets considered
  in the NIST process**, with "improved (though not yet practical) concrete
  attack estimates". **"Not yet practical" is the authors' own phrase and is
  load-bearing** — see "What this entry does NOT establish".
- A **heuristic** extension to ciphertext decryption / message recovery from a
  noisy codeword, also `n^O(log n)`.
- A stated origin in a failed doubly-efficient-PIR-from-algebraic-LDC
  construction.

No complexity figure beyond the abstract's own `n^O(log n)` appears anywhere in
this entry. No theorem number, page number, heuristic number, constant, or
concrete estimate is recorded, because none was obtained.

## Claim class

**`distinguish-then-recover`** (`knowledge/TAG-CLAIM-CLASS-v2.md` section 1,
rule R-CC-2).

- The **distinguisher** is the first result: telling a McEliece public key from
  uniform over `F_2^{k x n}` in time `n^O(log n)` with advantage `1-o(1)`. The
  abstract calls this one provable.
- The **recovery** is the second result: a ciphertext-decryption attack that
  recovers **the message** from a noisy codeword, at the same `n^O(log n)`.
- **The condition under which the escalation holds, as R-CC-2 requires it be
  named:** the abstract states the extension is **heuristic**, while the
  distinguisher is provable. That word is the entire stated condition, and the
  underlying assumptions are **not recorded here because they were not
  obtained** — they are in a full text this program does not have. A future
  reader must not treat the recovery half as carrying the distinguisher's
  stated provability.

**The recovery is of a MESSAGE, not of a KEY. The paper does not claim key
recovery.** `docs/claims-and-verification.md` and `RQ-MCE-e65b3c`'s standing
constraint ("Distinguisher is not break") forbid promoting either result to
the other, and message recovery from a chosen ciphertext is a third thing
again — it is not key recovery and no deliverable of this program may report it
as one.

**A vocabulary gap, recorded rather than papered over (AGENTS.md rule 8).**
`knowledge/TAG-CLAIM-CLASS.md` and `TAG-CLAIM-CLASS-v2.md` define exactly three
claim-class tokens — `distinguisher`, `key-recovery`, `distinguish-then-recover`
— and **there is no `message-recovery` token in that vocabulary.** So no tag on
this entry can, by itself, convey that the recovery half is message recovery
rather than key recovery: `distinguish-then-recover`'s table row says only
"an escalation of it to recovery". `key-recovery` would be affirmatively false
here, and `distinguisher` alone is excluded by the vocabulary's own definition
("claims **no** key or message recovery"), which this paper's second result
contradicts. `distinguish-then-recover` is therefore the only admissible token,
and this section carries the message-vs-key distinction that the token cannot.
**This entry does not invent a fourth token.** Extending the vocabulary is a
new file under a new task id that cites the existing two (R-CC-6 discipline);
it is not something a literature entry may do on its own.

R-CC-1 (mutual exclusion of `distinguisher` and `key-recovery`) is satisfied
by construction: this entry's `tags` carries neither token. Per R-CC-4 and
`TAG-CLAIM-CLASS-v2.md` section 2, `distinguish-then-recover` is a distinct
string and can never match either.

**The basis of this classification is a relayed abstract and nothing more.**
Nobody in this program has read this paper.

**Falsification condition, stated so it can be checked rather than assumed**
(the `KN-LIT-3c9f21` form): if a read of the full text shows the paper claims
key recovery in any regime, or shows that the recovery half is not an
escalation of the distinguisher, or shows the distinguisher is not
unconditional, then this classification is wrong and **this entry must itself
be superseded under a new id**. It is never re-tagged in place (R-CC-6).

## Position relative to what this program already filed

This is the substantive part, and it is written to be checkable. Each claim
below is marked **[RELAYED]** (the paper's own claim, at the provenance in
`citation_verified_note`), **[FILED]** (what a named corpus record already
says), or **[THIS PROGRAM'S READING]** (an inference made here, by this
Coordinator, from the two).

### Against the filed distinguisher line — KN-LIT-13a01d, superseded on tags by KN-LIT-3c9f21

**[FILED]** `KN-LIT-3c9f21` (superseding `KN-LIT-13a01d` on claim-class tags
only) records Faugère--Gauthier--Otmani--Perret--Tillich as *"A distinguisher
for high rate McEliece cryptosystems"*: high-rate Goppa/alternant public keys
are distinguishable from random, no key recovery, **"Confined to high rate."**
Both entries state the rate threshold itself is NOT recorded anywhere in this
corpus, and that neither entry was written from a read of the paper.

**[RELAYED]** The regime here is `m = Theta(log n)`, `t = Theta(n/log n)`,
`k = Theta(n)`.

**[THIS PROGRAM'S READING]** These are different regimes, and that is the
reason the filed line does not already cover this claim. Arithmetic on the
relayed asymptotics: `n - k` is the redundancy, `m*t = Theta(log n) *
Theta(n/log n) = Theta(n)`, and `k = Theta(n)` is stated directly. A redundancy
of `Theta(n)` means `n - k >= c*n` for some constant `c > 0`, so the rate
`k/n <= 1 - c` is **bounded away from 1**. The filed distinguisher line is
confined to *high* rate, i.e. rate approaching 1 / redundancy small relative to
`n`. A constant-rate-bounded-away-from-1 regime is therefore not the regime
`KN-LIT-13a01d`/`KN-LIT-3c9f21` addresses, and a reader may not treat the
filed line as already covering, anticipating, or subsuming this claim.

**Three limits on that reading, stated because they are real:**

1. It is arithmetic on Theta-notation in a relayed abstract. It fixes no
   constant, and this program has never transcribed the filed line's actual
   rate threshold — `KN-LIT-3c9f21` says so explicitly ("this entry supplies no
   number to compare against them"). So this is a statement that the two
   regimes are *qualitatively different*, not a measured distance.
2. **[RELAYED]** the abstract also asserts applicability "to all Classic
   McEliece parameter sets considered in the NIST process", which are concrete
   finite parameter sets, not an asymptotic family. How a `Theta`-scaling
   regime is meant to bind specific parameter sets is exactly the kind of
   question that cannot be answered from an abstract, and this entry does not
   answer it.
3. Classic McEliece's actual transcribed parameters live in `KN-LIT-84b674`
   (the cryptosystem specification, at a recorded sha256); this entry performs
   no arithmetic against them and states no distance.

### Against the filed key-recovery line — KN-LIT-4c8135, superseded by KN-LIT-c41d8b

**[FILED]** `KN-LIT-c41d8b` (superseding `KN-LIT-4c8135`) records
Bardet--Mora--Tillich as polynomial-time key recovery for **generic/random
alternant** codes at high rate with `q ∈ {2,3}`, and records verbatim from the
full text at sha256 `ebbd94ac…` that *"Interestingly our attack does not work
at all when the alternant code has the additional structure of being a Goppa
code."*

**This exclusion may not be invoked bare.** `RQ-MCE-f8fca0` (the completing
supersession, in force for every deliverable of GOAL-MCE-001) requires that any
deliverable citing it also carry the source's own qualification, quoted rather
than summarised:

> However, unlike the case of the filtration where right now this part of the
> attack does not work at all, it seems that here even if the Gröbner basis
> computation consists of more steps, solving the whole system should still be
> polynomial.  *(Q-3, PDF page 32)*

> The discussion below does not represent a proof that computing a filtration
> is impossible for Goppa codes, but rather an intuition about what hampers
> it.  *(Q-4, PDF page 15, section 3.2)*

> Therefore it is tempting to conjecture that Goppa codes, at least in the
> regime where they are distinguishable from random codes (which applies in
> particular to the CFS scheme [CFS01]) should eventually be attacked in
> polynomial by some variation the attack that has been given here.
> *(Q-2, PDF page 32)*

The exclusion is thus phase-scoped (to the filtration step), present-tense
("right now"), explicitly not a proof, and conjectured by its own authors to
fall.

**[THIS PROGRAM'S READING]** The 2024 result's stated boundary — a *generic
alternant* result that does not reach Goppa codes — is not a boundary the
present claim inherits, because the present claim is **[RELAYED]** stated for
Goppa--McEliece directly. Nothing here confirms the present claim; the point is
narrower and purely negative: **no filed record of this corpus rules it out**,
and in particular `KN-LIT-c41d8b`'s Goppa exclusion is a statement by different
authors about *their own* attack's filtration step at one moment in time, and
transfers to nothing else. `KN-LIT-c41d8b` says exactly this in its own "What
this correction does NOT establish" section, and this entry does not stretch
it.

### Against the 2026 heuristic subexponential line — KN-LIT-7c4620

**[FILED]** `KN-LIT-7c4620` (Briaud--Lemoine--Randriambololona--Tillich,
`iacr:2026/1232`) is a **heuristic subexponential key-recovery** claim on
McEliece, citation-verified only, full text never obtained — the same
Cloudflare-class blocker recorded again here. It is GOAL-MCE-001's declared
primary target and remains unread.

**[THIS PROGRAM'S READING]** These are two distinct unread 2026 claims that
this program cannot presently relate to one another at all. They differ in the
class of result **[RELAYED/FILED]** (a provable distinguisher plus a heuristic
*message*-recovery attack, versus a heuristic *key*-recovery attack), in the
stated complexity form (`n^O(log n)` versus subexponential), and in author
group. **Whether either bears on the other is unknown and must not be guessed
at.** Anything more than that requires reading at least one of the two.

### Net effect on the corpus, stated without inflation

Nothing filed becomes wrong. The filed distinguisher line stays a high-rate
result; the filed alternant key-recovery line stays generic-alternant with a
qualified, conjectured-to-fall Goppa exclusion; `KN-LIT-7c4620` stays unread.
What changes is that **the corpus now holds a third-party claim in the regime
GOAL-MCE-001 actually targets, and no filed record covers that regime.**

## The lens this program did not cross

**[RELAYED]** The paper states its origin as a *failed* attempt to construct
doubly efficient PIR from algebraic locally decodable codes, and that its
distinguishing attack "can be intuitively explained from the PIR perspective."

**Checkable process facts about this corpus, established by greps run for this
entry over `knowledge/` on 2026-08-10:**

- A PIR/LDC cluster exists. A case-insensitive search for
  `private information retrieval|\bPIR\b` over `knowledge/literature/` returns
  **31 entries, 62 occurrences** — among them `KN-LIT-5300` (*On Basing Private
  Information Retrieval on NP-Hardness*), `KN-LIT-1886` (*SPIDER: Two Server
  Functionality for the Cost of Zero*, single-server PIR with client
  preprocessing and stored hints), and `KN-LIT-5918` (*Private Searching On
  Streaming Data*, framed by its own entry as a generalisation of PIR). A
  search for `locally decodable` returns six entries, including `KN-LIT-6034`
  (*Public-Key Locally-Decodable Codes*).
- A McEliece cluster exists. A case-insensitive search for
  `mceliece|goppa|alternant` over the same directory returns **180 entries**.
- **The two file sets do not intersect.** No entry in `knowledge/literature/`
  mentions both. Outside `knowledge/literature/`, the phrase "private
  information retrieval" appears only in the generated corpus manifests
  (`knowledge/sources.json`, `knowledge/SOURCES.md`) — in no technique,
  finding, or open-problem entry at all.

**What that is an instance of.** `docs/inventor-protocol.md` section 8, audit 2
(`KN-TECH-080`, "Observation-collision test") is the mandatory cheap audit that
asks, of a named observable, whether two structurally distinct objects share
it — the systematic form of looking for the same object under two lenses. This
program filed both clusters and ran no such search across them. Two clusters,
zero co-mentions, and a third party reports arriving at a McEliece distinguisher
by pushing on a PIR/LDC construction until it failed.

**Recorded as a process fact, and bounded as one.** This is not a claim that
running a cross-cluster audit would have produced this result; it very probably
would not have, cheap audits are falsification aids and not generators
(`KN-TECH-080`, "Epistemic status"), and this program has read neither the
paper nor most of either cluster. Nor is it a claim of misconduct or of
negligence: nothing in the goal's charter directed a PIR sweep. It is simply
the true and checkable statement that a link a third party found productive is
one this corpus does not contain, and that the protocol which would have looked
for such links was not run across these two clusters. The forward-looking form
of it belongs in a decision record, not here.

## What this entry does NOT establish

- **It says nothing about Classic McEliece's security in either direction.**
  Not that it is broken, not that it is safe. It relays a third-party claim
  whose *citation only* is verified.
- **A quasipolynomial distinguisher is not a practical break.** `n^O(log n)` is
  superpolynomial, and the abstract's own concrete estimates are, in the
  authors' words, **"not yet practical"**. No record of this program may report
  this as a practical break of any deployed or standardized parameter set.
- **A distinguisher is not a key recovery, and a message recovery is not a key
  recovery.** See "Claim class".
- **It moves no hypothesis and files no evidence.** `GOAL-MCE-001`'s
  `active_hypothesis_ids` stays empty and `RQ-MCE-e65b3c`'s TOY claim-tier
  ceiling is untouched by this entry.
- **It does not assert the paper is correct, and it does not assert the paper
  is wrong.** No claim in it has been checked by anyone here.

**Does not bear on the ECDLP.**

## Not verified here

- **The full text was not read, was not obtained, and no sha256 of it exists.**
  See `citation_verified_note` for the three exact fetch attempts and outcomes.
- The abstract itself is a **tool relay through a summarizing model**, not a
  transcription. It is weaker provenance than `KN-LIT-c41d8b`'s
  transcription-at-recorded-sha256 standard, and this entry is not a
  substitute for the abstract's actual bytes.
- No complexity figure, concrete estimate, heuristic, proof, theorem number,
  page number or benchmark has been reproduced, checked, or even seen by this
  program.
- The claimed applicability "to all Classic McEliece parameter sets considered
  in the NIST process" is **relayed and unchecked**, including which parameter
  sets that phrase covers. `GOAL-MCE-001`'s `scheme_context` separately records
  that the ISO set list contains no `mceliece348864` variant; whether that
  interacts with the paper's claim is unknown here.
- The authors' affiliations are relayed, not checked.
- Nothing about the PIR/LDC origin story has been verified beyond its presence
  in the relayed abstract.

## Provenance

- Surfaced by the user on 2026-08-10; acquisition performed by the
  orchestrating session as described in `citation_verified_note`.
- Filed by `TASK-20260810-025f09`'s parent decision `DEC-20260810-4eae48`
  (GOAL-MCE-001), which also carries `CORR-20260810-c487ff`, the correction to
  this goal's scoping premise that this entry's existence triggers.
- Corpus comparisons in "Position relative to what this program already filed"
  read `KN-LIT-13a01d`, `KN-LIT-3c9f21`, `KN-LIT-4c8135`, `KN-LIT-c41d8b`,
  `KN-LIT-7c4620`, `KN-LIT-84b674`, `RQ-MCE-e65b3c`, `RQ-MCE-f8fca0` and
  `GOAL-MCE-001/goal.yaml` directly in the worktree.
- Claim-class vocabulary: `knowledge/TAG-CLAIM-CLASS.md` section 1 and
  `knowledge/TAG-CLAIM-CLASS-v2.md` sections 1-2 (R-CC-1 through R-CC-6).
