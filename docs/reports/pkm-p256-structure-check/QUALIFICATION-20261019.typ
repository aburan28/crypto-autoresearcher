#set page(paper: "a4", margin: 1.8cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")

= Qualification (2026-10-19) of the P-256 coset report

*Additive.* This note qualifies `report.typ` / `report.pdf` of the same directory. The historical report, its PDF and its diagram are unchanged; where they differ from this note, this note governs. Origin: content review of PR \#2424 (finding \[P2\]). Labels as in the report: *derived*, *computed*, *recalled*.

== What was overstated

The report's lemma is stated with the hypothesis that $|K|$ is coprime to $n$, and is correct as stated. Its *application* dropped that hypothesis: the report concludes that "whatever isogeny degree is used" a factor base made of an isogeny-kernel coset has at most one $F_p$-rational point, and (Section 1.4 and the diagram) that kernel-coset factor bases cannot sit inside $E_P (F_p)$; Section 1.6 item 2 rules out "any construction that needs a rational coset". Those sentences are too strong.

== Corrected statement (derived)

Let $\#E(F_p) = n$ be prime and $K subset E(overline(F)_p)$ a finite subgroup. Then $K inter E(F_p)$ is a subgroup of a group of prime order, so it is either ${O}$ or all of $E(F_p)$.

- *Case $n divides.not |K|$* (equivalently $gcd(|K|, n) = 1$, which excludes $K inter E(F_p) = E(F_p)$): $K inter E(F_p) = {O}$ and every coset $R + K$ contains at most one $F_p$-rational point. This is the report's lemma. It covers the proposed 2-power chain ($|K| = 2^L$, and $n$ is odd for P-256), every $l$-power kernel with $l != n$, and every $K$ of order coprime to $n$.
- *Case $E(F_p) subset.eq K$* (this requires $n | |K|$): $K inter E(F_p) = E(F_p)$, so for every $R in E(F_p)$ the coset $R + K$ contains all $n$ rational points. Example: $K = E(F_p)$, the Frobenius-stable subgroup of order $n$; the separable quotient isogeny $E -> E slash K$ is defined over $F_p$ and has all $n$ rational points in its kernel. The lemma does not exclude such cosets. They supply no useful decomposition (the "factor base" would be the whole group, and the quotient sends every rational point to $O$), but that is a separate observation, not a consequence of the lemma.

#figure(image("diagram_qualified.svg", width: 80%), caption: [Corrected scope of the coset lemma. The original diagram's last clause ("kernel-coset factor bases cannot sit inside $E_P (F_p)$") applies to the left case only.])

== What is and is not affected

- *Unchanged:* Result 1 (no isogeny between the supersingular auxiliary curve and the ordinary $E_P$), every computed fact in `output.json`, and the conclusion for the proposal under test: the 2-power kernel on the auxiliary curve is outside $E_P$ altogether, and a 2-power kernel on $E_P$ falls in the coprime case.
- *Narrowed:* the claim that no kernel-coset factor base can live inside $E_P (F_p)$ holds for kernels of order coprime to $n$, not for every kernel. The rule in Section 1.6 item 2 reads: reject a construction that needs a rational coset of a subgroup $K$ with $n divides.not |K|$ before any experiment.
- *Not claimed:* anything about kernels with $n | |K|$ beyond the two observations above, or about P-256 security.

Mutable summaries updated in the same change: the "Derived" bullet of `problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md`.
