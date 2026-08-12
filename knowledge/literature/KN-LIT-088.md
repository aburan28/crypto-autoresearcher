---
id: KN-LIT-088
type: literature
title: Fermat quotients and the polynomial time discrete log algorithm for anomalous elliptic curves
authors: [Satoh Takakazu, Araki Kiyomichi]
year: 1998
venue: Commentarii Mathematici Universitatis Sancti Pauli, 47(1):81-92
identifiers:
  eprint: null
  doi: null
  url: https://www.lanfanshu.com/paper/61e50034d7071fa839f637c2
tags: [anomalous, trace-one, fermat-quotient, p-adic, additive-transfer, polynomial-time, special-curves, prime-field, ecdlp, hygiene]
confidence: reported
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
The p-adic route to the anomalous-curve attack, developed independently of
Semaev (KN-LIT-087) and Smart (KN-LIT-089) at essentially the same time.
Satoh and Araki use Fermat quotients to construct the homomorphism from the
anomalous curve group to the additive group of F_p, giving a polynomial-time
discrete logarithm algorithm for curves with #E(F_p) = p.

## Key claims (as reported)
- Polynomial-time ECDLP for anomalous elliptic curves over F_p, via a
  Fermat-quotient construction (proven in the source).
- The construction is p-adic in flavour -- it lifts to Q_p and uses the formal
  group / elliptic logarithm -- rather than Semaev's direct isomorphism.

## Relevance to this program
Same boundary as KN-LIT-087, reached by a different technique, and the
difference is what makes it worth a separate entry: the p-adic lift is the
mechanism family that also underlies Xedni-style ideas (KN-LIT-020,
KN-LIT-021) and any proposal to work in a characteristic-zero lift of the
curve. The anomalous case is the one place where such a lift is known to pay,
and the reason it pays is that the trace-one condition makes the formal-group
logarithm globally defined on the relevant subgroup. A proposal that lifts
p-adically and does not explain why it escapes the non-anomalous obstruction is
screened as re-treading this route. See KN-TECH-033.

## Not verified here
Full paper not fetched; the journal is not open access. Authors, title, venue
(Comment. Math. Univ. St. Pauli 47(1):81-92, 1998) and page range were
confirmed against two independent bibliographic records and a third-party
reference list. An errata by the same authors exists (Institutional
Repositories DataBase, doi:10.14992/00009860); its content was not examined,
so the claims above should be treated as `reported` and the errata consulted
before any result depends on the detailed construction. The Fermat-quotient
mechanism description is relayed from secondary sources.
