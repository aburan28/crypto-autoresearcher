#set page(paper: "a4", margin: 18mm)
#set text(font: "DejaVu Sans", size: 10pt)
#text(size: 20pt, weight: "bold")[Grouped indicators: a structural regularity lead]

#text(fill: rgb("#855200"), weight: "bold")[Derived; independent review pending; no scientific trials]

Represent every pair of coordinate bits by three mutually exclusive Boolean indicators. The all-zero indicator vector represents digit zero. Each original assignment has exactly one representation, and the coordinate remains affine in the new variables.

#image("next-leads.svg", width: 100%)

For two coordinates of even width s, the original S3 bit system has leading-form regularity s plus the ceiling of (s+2)/2 under the assumptions in the separate two-summand proof. The grouped system has 3s variables and 6s local quadratics, plus the substituted quartic. Its regularity is at most s+1: a monomial of degree s+1 repeats one of the s groups, so its within-group quadratic factor lies in the top ideal.

The inverse maps are explicit. For bits b0,b1, take u1=b0(1-b1), u2=(1-b0)b1, and u3=b0 b1. Conversely b0=u1+u3 and b1=u2+u3. Thus the result concerns an equivalent projected problem, with a changed variable count and degree filtration.

#link("https://arxiv.org/html/2304.13485")[Salizzoni, Proposition 3.10], bounds the mutant-style solving degree by the maximum of regularity plus one and the maximum input degree. Here that gives s+2. This is an upper bound for the specified multiplication-closed-space convention. It does not prove a strict reduction in the actual solving degree of the original problem, or predict a particular software implementation's behavior.

The local top quotient has Hilbert series (1+3T) to the power s and total dimension 4 to the power s. The encoding retains all coordinate assignments. Lower degree therefore comes with wider graded components; runtime, memory and certificate costs remain unresolved. Fixed two-bit groups avoid the exponential membership-table construction of the other lead.

The full derivation, general group-width formula, proposed SAT interface, and separate unreviewed three-summand extension are in `next-leads.md`. Indicator encodings are established CSP tools; novelty has not been established. This page is outside the frozen two-summand membership proof and inherits no verdict from its review.
