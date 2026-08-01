---
id: KN-LIT-7594
type: literature
title: "Discovering cryptographic weaknesses with Claude"
authors:
  - "Anthropic Frontier Red Team"
year: 2026
venue: 'Anthropic research blog, 2026-07-28'
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: https://www.anthropic.com/research/discovering-cryptographic-weaknesses
tags: [llm-cryptanalysis, autonomous-research, agentic-harness, hawk, aes, lea, serpent, salsa20, poseidon, sha-1, cryptanalysisbench, responsible-disclosure, verification-bottleneck, methodology, program-level]
confidence: reported
citation_verified: web
added: "2026-07-28"
superseded_by: null
---

## Contribution
The program-level account tying together two cryptanalytic results found with Claude
Mythos Preview — the HAWK key-recovery reduction ([[KN-LIT-7592]]) and the 7-round AES
Möbius bridge ([[KN-LIT-7593]]) — plus a set of preliminary follow-on attacks, cost and
autonomy figures for the discovery process, and the authors' account of what changes when
a model rather than a human produces the result.

## Key claims (as reported)
**The two headline results.**
- HAWK: a third-round NIST additional-signatures candidate that "survived two rounds of
  expert human review over a period of two years"; the attack was found in about **60
  hours** of work and effectively halves key strength. Expected full key-recovery cost
  against HAWK-256 drops from `2^64` to `2^38`. Explicitly a **faster exponential-time**
  attack, not polynomial; specific to HAWK, and stated not to affect other NIST PQC
  candidates or lattice-based cryptography generally.
- AES: an improved attack on 7 of 10 rounds under chosen plaintext, `2^105` data,
  "200-800×" faster than prior best.
- Each result cost **roughly $100,000 in API cost**. Neither affects any production
  system; no software must change.

**Autonomy and the discovery loop.** HAWK was found semi-autonomously — a multi-worker
agentic harness with Python and Sage, an operator with a theoretical-CS background who was
not a lattice expert, and human input "limited to project management." The key idea came
from **a pair of workers disagreeing**: the first "prematurely rejected the idea as
infeasible," the second found a way to exploit it, and they converged by exchanging
messages. AES was found essentially fully autonomously: over three days Claude produced
several hundred million tokens (one billion output tokens in total for the refined
attack) under **three substantive prompts**, all of which pushed against the model's own
premature closure. The blog publishes the operator's verbatim prompts.

**The failure mode that had to be prompted around.** Claude initially "would not engage
with the problem, because it claimed that it was impossible to improve cryptanalysis of
AES," writing things like "AES-128 r5/r6 is just genuinely hard" and "there's nothing
easy to find; this is the most-studied block cipher in existence." The single operator
message that unblocked it was an observation about model behaviour — "the models tend to
think it is impossible to solve so they don't try they [sic] need a good amount of
prompting" — in response to which **Claude rewrote its own agent harness** to search for
genuinely novel ideas. The remaining two prompts also pushed against retreat: refusing a
proposed target switch to an easier cipher, and "we are not looking for low hanging fruit."

**Follow-on results (preliminary, not yet published in full).**
- **LEA** (ISO/IEC 29192-2:2019, 24 rounds): best published 13-round cryptanalysis needs
  `2^98` plaintext pairs and `2^86` work; Mythos found a practical 13-round key recovery
  in under `2^30` plaintexts running in under an hour on a desktop. Runs end-to-end, so
  confidence is high; exact bounds and the extension to 14 rounds are still open.
- **Serpent-128**: a practical full key recovery on 6 of 32 rounds, extending published
  work needing `> 2^70` pairs and `2^90` decryptions.
- Smaller (`< 10×`) improvements against **Salsa20**, **Poseidon**, and **SHA-1**.

**The verification bottleneck — the paper's central methodological claim.** Mythos took
one week to discover the AES attack; **two researchers needed nearly a month to gain
confidence it was correct.** "The vast majority of our time over the past few months has
been in verifying the correctness of Claude's results." The authors predict human
researchers will become bottlenecked on validating machine-produced results for technical
validity, novelty, and utility, as has already happened in vulnerability triage. The
HAWK and LEA attacks were far easier to trust **because they run end-to-end**; the AES
attack cannot be run and is the expensive one.

**Process.** Responsible disclosure was followed: the HAWK attack was shared with the
HAWK authors in June 2026 and coordinated with the public NIST mailing list; advance
copies went to US government and industry partners. CryptanalysisBench was built with
academics at ETH Zurich, Tel Aviv University, and the University of Haifa.

## Relevance to this program
This is a description of a harness doing what this harness is built to do, run by the
group that built the model this harness runs on. It is recorded as **methodological
literature, not as a result** — nothing in it bears on the ECDLP.

Four points bear directly on how this program operates, and one contradicts a comfortable
assumption:

1. **The default failure mode is premature closure, not overclaiming.** This program's
   entire rule set — `AGENTS.md` rules 3–6, the claim tiers, the Red Team role — is
   tuned against *overclaiming*. The AES discovery was blocked in the opposite direction:
   the model repeatedly refused to try, on the correct-sounding grounds that the target was
   well studied. That is precisely the reasoning shape this program's own novelty
   discipline rewards. **A saturation finding ("the space has been mined") is a hypothesis
   about the search, not a theorem about the problem**, and it should be recorded as
   `unverified` unless it comes with a closure argument. This is the sharpest available
   caution against this program's own saturation reports (see [[KN-LIT-7595]] for what a
   *real* closure argument looks like).
2. **Verification, not discovery, is the scarce resource.** A 1:4 discovery-to-validation
   time ratio, with the ratio driven by whether the result runs end-to-end. This is a
   direct argument for the program's existing preference for results that carry an
   independently re-verifiable **solution certificate** (`docs/claims-and-verification.md`)
   and for weighting cheap-to-falsify hypotheses upward in prioritization.
3. **Multi-agent disagreement was load-bearing.** The HAWK idea survived because a second
   worker did not accept the first worker's rejection. A single agent would have closed
   the lane. This program's `red-team` and `validator` roles are adversarial *after* a
   result exists; there is no mechanism for a second opinion on a *rejected* idea.
4. **Costs are stated.** ~60 hours and ~$100k per result, ~10^9 output tokens for one
   attack. Useful as an order-of-magnitude prior when the Coordinator prices a batch.

**CryptanalysisBench is already in the corpus** as `KN-LIT-7588` (arXiv:2607.18538),
ingested in the 2026-07-27 gather before this post connected it to these results; the
caution recorded there — that symmetric-domain benchmark results do **not** transfer to
ECDLP — stands unchanged and applies to this entry too.

## Not verified here
Blog post retrieved from the official URL above on 2026-07-28 and read in full;
`confidence: reported`. All technical claims are relayed from the post and from the two
linked papers ([[KN-LIT-7592]], [[KN-LIT-7593]]); none has been independently checked by
this program.

NOT verified here: every complexity figure above, including the HAWK `2^64 → 2^38`
HAWK-256 figure and the "200-800×" AES speedup (note that the AES paper itself states a
runtime range, `2^89.3`–`2^91.4` against a `2^99` baseline, whose width depends on
accounting choices — the blog's single "200-800×" range is that spread restated, not an
independent measurement); the LEA, Serpent-128, Salsa20, Poseidon, and SHA-1 follow-ons,
**none of which has a published paper as of this entry** and which are described by the
authors themselves as preliminary; the cost and token figures; the autonomy account and
the claim that the published prompts are the complete set of substantive human input; and
the disclosure timeline. The claim that reviewing NIST specifications with AI "will be a
powerful tool" is a forward-looking statement by the authors, not a result. This is a
blog post by the discovering party — not peer-reviewed and not a primary technical
source; where it and the papers differ, the papers govern.
