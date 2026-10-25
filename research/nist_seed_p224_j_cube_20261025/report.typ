#set page(paper: "a4", margin: 17mm)
#set text(size: 10pt)
#set par(justify: false)
= P-224 cubic j and 3-division splitting
Observation record / 25 October 2026

*Historical selection criterion: unresolved.* This report preserves a specific
lead from a fixed comparison of 21 curves: ten publications and eleven
reconstructed omissions across six streams.

For $y^2=x^3-3x+b$ over $F_p$, $j=6912/(4-b^2)$ modulo $p$.
The published P-224 j-value is a cube in its base field. The three omitted
P-224 j-values are not. The published P-224 3-division polynomial splits into
four linear factors; each omission factors into degrees 1 and 3.

#image("splitting.svg", width: 100%)

*Required counterexample:* published P-256 has a non-cubic j-value, as does
its omitted block 876. Both have the factor pattern 1+3. A universal cube-root
requirement therefore fails this comparison.

The 3-division polynomial, after removing its constant scalar, is
$x^4-6x^2+4b x-3$. Its roots describe nonzero 3-torsion x-coordinates.
This observation does not establish a transfer attack on the prime subgroup.

== Replay and exact identities
The adjacent inputs.json retains all 21 full curve identities, field
characteristics, coefficients, subgroup orders, generators, cofactors,
seeds, timestamps and ordinals. observations.json retains the exact j-values
and polynomial factor degrees. replay.py independently computes j using
Python and native PARI/GP, checks all factor products and p/n primality,
regenerates all seeds, and checks coefficient/identity bindings.

Command: #raw("python3 replay.py --gp gp")

The replay passed all 21 rows and two tampering controls. It does not rerun
SEA, authenticate the original historical program or promote a research claim.

#pagebreak()
= Interpretation boundary and next check

*Observed:* the P-224 publication differs from each of its three omissions
in cubic-residue j and 3-division splitting.

*Exploratory branch hypothesis:* when $p=1$ modulo 4, require a cube root of j.
P-224 is the only such field here. This condition preserves all publications
and rejects these three omissions, leaving eight unexplained. It is not an
independent cross-field prediction.

*Unverified historical mechanism:* a field-dependent point-counting or
validation path could require that root and treat failure as rejection.
No original caller, configuration, fallback or failure handling has been
recovered. The observed pattern alone does not prove such a path existed.

== Falsifiable next investigation
Find a dated implementation and its actual caller. Identify branch admission,
cube-root failure handling, fallback and return status. Replay the declared
path on the complete cohort, including non-cubic published P-256.
A normal fallback would weaken that implementation hypothesis. A matching
P-224 rejection would retain a branch-specific lead but would still leave
the other omissions to explain.

== Custody and limitations
source-provenance.json binds the original exact-input and j/splitting records
by SHA-256. These are reconstructed omissions, not documented rejection logs.
No official experiment or goal status changes. No timing, attack-cost or
weakness claim is made. No canonical isogeny graph changes because this
study proves no new map or subgroup-transport edge.

== Sources
Internal exact-input and arithmetic receipts, retrieved and replayed
25 October 2026, are identified in source-provenance.json.

#link("https://www.anthropic.com/research/ecdsa-curve-origins")[Original seed reconstruction]:
the omission cause is explicitly left unresolved.

#link("https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_finite_field.html")[Sage finite-field curve documentation]:
j and twists do not in general determine base-field isomorphism.

Full details, controls and paths: report.md. This PDF is a derived view of
the adjacent machine-readable record, not historical provenance.
