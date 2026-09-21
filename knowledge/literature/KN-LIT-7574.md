---
id: KN-LIT-7574
type: literature
title: 'Quantum Cryptanalysis on IBM Quantum Hardware: Extending Even-Mansour Period Recovery from N=4 to N=10'
authors: [Kim Taebong, Hong Youngsik, Kim Minsik, Choi Sunyoung, Jang Jaewon, Shin Junghoon, Kim Minseo]
year: 2026
venue: 'arXiv preprint (cs.CR, cs.AI)'
identifiers:
  eprint: null
  doi: null
  arxiv: '2607.18340'
  url: https://arxiv.org/abs/2607.18340
tags: [quantum-cryptanalysis, simon-algorithm, grover, bernstein-vazirani, even-mansour, feistel, real-hardware, nisq, error-mitigation, q2-model, calibration, scope-discipline, adjacent]
confidence: reported
citation_verified: web
added: 2026-07-26
superseded_by: null
---

## Contribution
Reports uncompiled, textbook-faithful quantum cryptanalysis of symmetric-cipher
structures executed on real IBM quantum hardware (`ibm_kingston`, Heron generation).
Simon's algorithm recovers the hidden period of the Even-Mansour cipher up to security
parameter `N = 10`, beyond the largest previously reported real-hardware key recovery
at `N = 4`, plus period recovery for a 3-round Feistel (DES-family) construction at
block sizes 6 and 8. A breadth-first benchmark covers five quantum attacks across four
symmetric design paradigms, validated to a 25-qubit classical-simulation ceiling.

## Key claims (as reported)
- Even-Mansour period recovery via Simon's algorithm on real hardware up to `N = 10`
  (previous real-hardware record: `N = 4`).
- Clean period recovery for 3-round Feistel at block sizes 6 and 8; a 21-qubit block-10
  instance verified in simulation and submitted to hardware.
- Benchmark spans Bernstein-Vazirani (linear structure, single query), Grover (SPN key
  search, quadratic), and Simon (Even-Mansour, CBC-MAC forgery, Feistel).
- The authors are **explicit about scope** and state the negative side themselves:
  these attacks target reduced or structured constructions in the **Q2
  (quantum-query) model**; they "asymptotically follow the birthday bound and
  therefore do not constitute quantum advantage over classical collision-finding";
  they do **not** break full AES/RSA or 16-round DES; and they rely on **error
  mitigation rather than fault-tolerant error correction**.
- The stated contribution is the real-hardware demonstration at record structure size,
  not a cryptanalytic break.

## Relevance to this program
`adjacent` — symmetric-cipher structures, not the ECDLP — and recorded for two
reasons, one substantive and one about reporting standards.

**Substantive:** it is a current, honest ceiling on what real quantum hardware does.
The corpus keeps `KN-TECH-037` (quantum ECDLP resource estimation) and this gather adds
`KN-LIT-7563` (distributed quantum ECDLP resource estimates, 828-1140 *logical* qubits
per node for a 256-bit curve). This paper is the other end of the same ruler: on
present hardware, with error mitigation and no fault tolerance, the demonstrated scale
is a 10-bit structured toy and a 25-qubit simulation ceiling. Holding those two numbers
next to each other is the cheapest available reality check on quantum-threat framing,
and it is exactly the calibration role `KN-TECH-036` and `KN-TECH-049` play for
classical records.

**Reporting standard:** the authors volunteer that their attacks follow the birthday
bound and therefore give no advantage over classical collision search. That is the same
discipline this program's own rules demand — scope every conclusion to the tested
parameters and never let a demonstration at toy scale be read as a crypto-scale claim
(`AGENTS.md`; `docs/claims-and-verification.md`). Useful as an external example of the
standard being met.

Bears on no open problem in the corpus, forecloses nothing on the ECDLP, and supplies
no technique the program can use.

## Not verified here
Full paper not read; all claims relayed from the official arXiv abstract retrieved via
the arXiv API on 2026-07-26 (hence `confidence: reported`). The abstract as retrieved
was **truncated in its final sentence**. Submitted 2026-07-20, primary category cs.CR,
cross-listed cs.AI. A preprint: no DOI, journal reference, or peer review recorded on
arXiv as of this entry.

NOT verified here: the hardware runs, the success rates and fidelities (none appear in
the abstract), the error-mitigation methodology, the priority claim that `N = 4` was
the previous real-hardware record, and the correctness of the circuits. "Genuine",
"uncompiled" and "textbook-faithful" are the authors' characterizations of their own
methodology and were not checked.
