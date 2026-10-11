# Degree norm: primary formula and Hom application

Task TASK-20261007-efaa15; verified_by: producer /root/ssi_j45_producer. Provenance: retrieved for sources; internal for the Hom adaptation and bound.

Helmut Hasse, *Zur Theorie der abstrakten elliptischen Funktionenkörper III. Die Struktur des Meromorphismenrings. Die Riemannsche Vermutung*, J. reine angew. Math.175 (1936), pp.193–208. Primary original journal scan retrieved https://download.uni-mainz.de/mathematik/Algebraische%20Geometrie/Lehre/WS23.Padische.Hasse.III.pdf at 2026-10-07T06:26:44.644Z; SHA256 `2e2de9b6697b9e8c5ff4b1cc1e3ad7e68b01bc2722789ceefba840588b25d24b`. Inspected by OCR and actual scan: printed pp.193–195 (PDF pp.1–3), especially §1 “Die Normenadditionsformel”, equation(1), p.193. Hasse's domain is a genus-one function field over an algebraically closed constant field of characteristic0 or prime p; N is the function-field extension degree. Hasse's term “normiert” is historical terminology and must not be confused with this packet's differential normalization.

[Retrieved statement] The norm satisfies N(mu+nu)+N(mu-nu)=2N(mu)+2N(nu). Primary equation and opening proof inspected; full proof audit is not claimed.

Supplement: J.S.Milne, *Elliptic Curves*, second edition, author web PDF https://www.jmilne.org/math/Books/EC2.pdf, title page says 2021 (site may list2020), SHA256 `646c0c4f193cdaa35f32c7d60fbd46a75e2f5187db4301810e8613726e3ebbee`, retrieved 2026-10-07T06:23:46.553Z. Source type: authoritative monograph, not original research. Inspected II§6: equation(18) and Theorem6.1, printed69–70 (PDF73–74), dual-additivity discussion printed74 (PDF78), Lemma6.12 printed75 (PDF79). This explicitly binds nonnegative degree, degree multiplicativity, and the endomorphism parallelogram law.

[Derived Hom transfer] f,g:E->C must be group homomorphisms on the SAME source and target, with deg(0)=0. If one is nonzero, E,C are isogenous; choose a fixed nonzero isogeny u:C->E (a dual of a nonzero f suffices). Apply the End(E) formula to uf,ug. Multiplicativity gives deg(u)deg(f+g)+deg(u)deg(f-g)=2deg(u)(deg f+deg g); cancel deg(u)>0. Nonnegative degree yields deg(f±g)<=2deg f+2deg g<=4D. This includes an inseparable difference; geometric kernel size<=separable degree<=total degree. No assumption that f-g is separable is needed. The latter kernel fact is supplemented by Sutherland2025 Theorem5.8, lecture5 pp.3–4.

If a nonzero h=f-g kills a point of order M, it kills its M-element cyclic subgroup, so M<=deg(h). With M=N>4D, h=0 follows. With P=O, M=1. With lower-order P the applicable condition is M>4D; M<=4D is loss of this proof, not a collision witness.

Verification: primary formula and authoritative supplement inspected; displayed Hom adaptation derived. Original-primary binding is available; independent proof review remains pending. Zero scientific/implementation/formalizer/experiment runs.
