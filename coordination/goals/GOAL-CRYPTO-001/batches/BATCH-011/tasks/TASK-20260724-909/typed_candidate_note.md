# TASK-20260724-909 typed-candidate note

Verdict: `NO_TYPED_CANDIDATE_FOUND`.

This is a systematic checked-coverage result, not an impossibility theorem,
breakthrough claim, exhaustive-literature claim, or cryptographic evidence. No
curve was run, no key was recovered, and no attack code was written.

## Admission rule

A source had to define, for an ordinary prime-field large-prime-order ECDLP,
all of:

1. factor base;
2. signed relation family;
3. action generators;
4. target map;
5. exact source replay;
6. full adaptive oracle transcript;
7. relation yield and independent rank;
8. fresh scalar-blind descent;
9. preprocessing;
10. memory and traffic;
11. verification; and
12. complete cost against matched Pollard rho.

Unknown fields failed admission. Tuple permutations, bounded isotypic
symmetries, supplied source labels, represented rows, and post-relation solvers
received no mechanism credit.

## What the closest sources actually provide

The closest explicit action is Faugère, Huot, Joux, Renault, and Vitse,
“Symmetrized Summation Polynomials: Using Small Order Torsion Points to Speed
Up Elliptic Curve Index Calculus,” EUROCRYPT 2014,
doi:10.1007/978-3-642-55220-5_3. It types

\[
F=\{P\in E(\mathbb F_{q^n}):\phi(P)\in\mathbf P^1(\mathbb F_q)\},
\quad \tau_T(P)=P+T,\quad
\phi\circ\tau_T=f_T\circ\phi ,
\]

and transforms decomposition tuples subject to
\(\sum_i k_i=0\bmod m\). It therefore supplies a genuine relation-preserving
torsion action and partial source recovery. It is not admissible here:

- its decomposition attack explicitly uses \(n>2\) extension fields and Weil
  restriction;
- \(m\) is small and bounded;
- reducing the factor base by \(m\) lowers decomposition probability by
  \(m^{n-1}\);
- no prime-field fresh scalar-blind descent, complete adaptive transcript,
  independent-rank tail, preprocessing/traffic account, certificate protocol,
  or matched-rho end-to-end cost is given; and
- for a prime-order \(E(\mathbb F_p)\), nontrivial rational small torsion is
  absent.

The strongest growing action is Galbraith, Granger, Merz, and Petit, “On Index
Calculus Algorithms for Subfield Curves,” IACR ePrint 2020/1315. It explicitly
constructs Frobenius-invariant factor bases, orbit representatives, transformed
relations, and conditional independent-rank savings. Its ECDLP is in
\(E(\mathbb F_{q^n})\) for a curve defined over \(\mathbb F_q\). On
\(E(\mathbb F_p)\), the \(p\)-power Frobenius fixes every rational point, so the
action specializes to the identity. The paper also does not claim to beat rho
on practical instances.

Tsakou and Ionica, IACR ePrint 2021/721 / Transactions on Mathematical
Cryptology 1(2), and the GLS/GHS work in IACR ePrint 2021/676 similarly obtain
endomorphism-orbit gains only for extension-field elliptic curves,
hyperelliptic Jacobians, or transferred DLPs. These do not cross the target
scope boundary.

The in-scope prime-field papers do not fill the gap:

- Petit–Kosters–Messeng, PKC 2016,
  doi:10.1007/978-3-662-49387-8_1, types
  \(F=\{(x,y):L(x)=0\}\), Semaev relations, and low-degree-map preprocessing,
  but has no relation action beyond tuple permutation and leaves decisive
  Gröbner, descent, memory, transcript, and matched-rho costs unknown.
- Amadori–Pintore–Sala, doi:10.1016/j.ffa.2018.01.009 / ePrint 2017/609,
  constructs a challenge-dependent dynamic factor base and seeks one Semaev
  dependency; it is a direct-solve variant, not a reusable factor-log action.
- McGuire–Mueller, ePrint 2017/1262, changes the decomposition/solving backend
  but supplies no distinct action.
- Kudo–Yokota–Takahashi–Yasuda,
  doi:10.1007/978-3-030-00434-7_19, is an optimization of the same prime-field
  summation-polynomial family; full chapter text was inaccessible here, so no
  missing interface was assumed.
- Hu, ePrint 2024/1923, proposes a scalar-table/scanning “pseudo-IC” method
  with vanishing hit probability, not a source-faithful relation action.
- Mahalanobis–Mallick, ePrint 2018/134 and
  doi:10.46298/jgcc.2020.12.2.6649, is the already screened
  hyperplane/zero-minor family.

No source supplied a group-circulant, constant-displacement-rank, or other
structured prime-field relation action before rows were represented.

## Reproducible coverage

On 2026-07-24, 25 verbatim Cursor WebSearch queries returned 122 displayed
records, all screened. Four OpenAlex API searches screened 90 first-page
records. Their reported totals were 244, 560, 15, and 4,917 respectively; the
large sets were noisy full-text searches, so only the first 25 ranked records
were screened. Five Crossref queries verified citation metadata. Direct
primary text was retrieved from IACR ePrint/proceedings, HAL, institutional
repositories, arXiv, and Transactions on Mathematical Cryptology.

The search covered prime-field index calculus, summation-polynomial variants,
point decomposition, relation matrices, torsion translations, Frobenius and
effective endomorphisms, non-generic representations, invariant theory,
algebraic geometry, Weil descent, and post-2020 work through 2026-07-24.
Extension-field, subfield/Koblitz, hyperelliptic-Jacobian, supersingular,
anomalous, transfer, and quantum results were recorded separately rather than
treated as prime-field evidence.

Important access limits are: Springer full text for the CANS 2018 Kudo et al.
chapter was unavailable; WebSearch exposed no total-hit counts or stable
provider identity; OpenAlex screening was first-page only for broad searches;
Google Scholar, MathSciNet, and zbMATH were not reproducibly available; forward
citation chaining and non-English searching were not exhaustive.

All exact queries, date bounds, counts, inclusion/exclusion rules, URLs,
retrieval dates, source-level exclusions, and access limits are in
`literature_audit.yaml`.

## Falsification and ranking

The verdict is falsified by one accessible primary source that supplies all
twelve fields for an ordinary \(E(\mathbb F_p)\) large-prime subgroup and lies
outside the prior compact-\(z_R\), hyperplane-signature, SOURCE-LOCATOR,
GGM-family, original-section Newton/BKK, AP/isotypic, and post-relation solver
routes. It is not falsified by a bounded torsion symmetry, extension-field
Frobenius orbit, represented low-rank matrix, toy solve, or untyped source
oracle.

No candidate ranks for experiment. The single first test for any future source
is the zero-compute twelve-field typing gate: quote and type every interface,
specialize its action to \(E(\mathbb F_p)\), and reject on the first absent
field or scope mismatch. This is the cheapest valid discriminator because
scope, action, source replay, and fresh descent are logical prerequisites; no
curve experiment can repair their absence.
