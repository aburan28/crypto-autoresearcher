---
id: KN-LIT-090
type: literature
title: The GHS Attack in odd Characteristic
authors: [Diem Claus]
year: 2003
venue: Journal of the Ramanujan Mathematical Society, 18(1):1-32
identifiers:
  eprint: null
  doi: null
  url: http://www.math.uni-leipzig.de/~diem/preprints/english.html
tags: [ghs, weil-descent, odd-characteristic, kummer-theory, conorm-norm, cover-attack, extension-field, prime-field, applicability, ecdlp]
confidence: reported
citation_verified: web
added: 2026-07-24
superseded_by: null
---

## Contribution
Generalizes the GHS Weil-descent attack (KN-LIT-007), originally formulated
for characteristic two, to hyperelliptic curves over finite fields of
arbitrary -- in particular odd -- characteristic. Where the characteristic-two
construction uses Artin-Schreier extensions, Diem uses Kummer theory, and
analyses when the kernel of the conorm-norm homomorphism is small enough that
the discrete logarithm actually survives the transfer to the Jacobian of the
descended curve.

## Key claims (as reported)
- A general treatment of GHS-style descent valid in arbitrary characteristic,
  with the odd-characteristic and odd-extension-degree cases worked out.
- The attack's effectiveness is governed by the genus of the descended curve
  against the extension degree: the descent is only useful when the genus stays
  small enough for index calculus in the Jacobian to beat rho on the original
  curve.
- Conditions are given under which the conorm-norm homomorphism has trivial or
  small kernel, i.e. under which the DLP is preserved by the transfer.

## Relevance to this program
This is the entry that answers "does Weil descent threaten E(F_p)?" precisely,
and the answer is structural: GHS-type descent needs a nontrivial field
extension F_{q^n}/F_q to descend along. A prime field F_p has no such
subfield structure, so the construction has nothing to act on -- the attack
family is inapplicable to the program's declared target class by hypothesis,
not by a cost margin. KN-LIT-007 states the binary-composite case and notes
prime fields are out of scope; this entry supplies the odd-characteristic
generalization and makes clear that "odd characteristic" means odd-degree
*extensions*, not prime fields. Any proposal invoking descent over F_p must
therefore first manufacture an extension structure, and that construction is
where the cost hides.

## Not verified here
Paper not fetched; the journal is not open access and the author's PDF was not
retrieved. Author, title, venue (J. Ramanujan Math. Soc. 18(1):1-32, 2003)
were confirmed against the author's own publication list at Universität
Leipzig and against two independent citing papers. The technical claims above
are relayed from those citing papers' descriptions of Diem's treatment
(Kummer theory, conorm-norm kernel, genus bounds), not from the source text,
hence confidence: reported. The prime-field inapplicability argument in
"Relevance" is this program's reading of the construction's prerequisites, not
a quotation from Diem.
