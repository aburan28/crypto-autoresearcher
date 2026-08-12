---
id: KN-LIT-685
type: literature
title: "Mixture Integral Attacks on Reduced-Round AES with a Known/Secret S-Box"
authors:
  - "Lorenzo Grassi"
  - "Markus Schofnegger"
year: 2019
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2019/772"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2019/772"
tags: [cryptanalysis, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we present new low-data secret-key distinguishers and key-recovery attacks on reduced-round AES. The starting point of our work is “Mixture Differential Cryptanalysis” recently introduced at FSE/ToSC 2019, a way to turn the “multiple-of-8” 5-round AES secret-key distinguisher presented at Eurocrypt 2017 into a simpler and more convenient one (though, on a smaller number of rounds).

## Key claims (as reported)
- By reconsidering this result on a smaller number of rounds, we present as our main contribution a new secret-key distinguisher on 3-round AES with the smallest data complexity in the literature (that does not require adaptive chosen plaintexts/ciphertexts), namely approximately half of the data necessary to set up a 3-round truncated differential distinguisher (which is currently the distinguisher in the literature with the lowest data complexity).
- For a success probability of 95%, our distinguisher requires just 10 chosen plaintexts versus 20 chosen plaintexts necessary to set up the truncated differential attack.
- Besides that, we present new competitive low-data key-recovery attacks on 3- and 4-round AES, both in the case in which the S-box is known and in the case in which it is secret.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2019-772.pdf`
