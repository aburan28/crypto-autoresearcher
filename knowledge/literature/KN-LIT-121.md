---
id: KN-LIT-121
type: literature
title: 'Creating Cryptographic Challenges Using Multi-Party Computation: The LWE Challenge'
authors: [Buchmann Johannes, Buscher Niklas, Gopfert Florian, Katzenbeisser Stefan, Kramer Juliane, Micciancio Daniele, Siim Sander, van Vredendaal Christine, Walter Michael]
year: 2016
venue: AsiaPKC@AsiaCCS 2016, ACM, pages 11-20 (ePrint 2017/606)
identifiers:
  eprint: iacr:2017/606
  doi: 10.1145/2898420.2898422
  url: https://eprint.iacr.org/2017/606
tags: [lwe-challenge, darmstadt, mpc, benchmark, records, practical-hardness, calibration, verifiability, lattice]
confidence: reported
citation_verified: read
added: 2026-07-24
superseded_by: null
---

## Contribution
Solves a structural problem with cryptographic challenges: for problems like LWE
it was not known how to create a challenge without knowing its solution, which
excludes the organisers from competing and requires trusting them. The paper
uses secure multi-party computation to generate LWE instances such that no
participating party learns the secret, and makes the generation independently
auditable.

## Key claims (as reported)
- An MPC-based method to create challenges without excluding anyone from
  participating, demonstrated by building the LWE Challenge.
- The verification design: parties commit to all randomness in advance, fixed
  randomness makes the protocol transcript deterministic in content and message
  order, so replaying it through a simulator detects any deviation from honest
  behaviour. Two protocols are specified -- `create_challenge`, run by the
  generating parties, and `check_challenge`, runnable by anyone.
- Parameters were chosen to provide an appropriate hardness range while staying
  as close as possible to instances used to instantiate real encryption schemes.
- Stated purpose: determine the practical hardness of LWE, compare the best
  known solvers, and motivate further work.

## Relevance to this program
Beyond calibration, this is a direct precedent for a problem the program has
already confronted: how does an artifact become trustworthy to someone who was
not present when it was produced? The answer here -- commit to randomness in
advance, make the transcript deterministic, publish an independently runnable
checker -- is structurally the same answer as the program's own frozen protocols
plus certificate re-verification (`docs/claims-and-verification.md`). It is
worth recording as external corroboration that the program's artifact policy is
the standard solution rather than local overhead.

The challenge instances themselves are the reference point for what LWE
parameters have actually been solved; KN-LIT-106 reports solving previously
unsolved instances including `(n, alpha) = (75, 0.005)`.

## Not verified here
The ePrint abstract and the PDF's protocol description were fetched and read.
The MPC protocol was not analysed for soundness, the parameter selection was not
checked, and the current state of the challenge table was not frozen by this
entry.
