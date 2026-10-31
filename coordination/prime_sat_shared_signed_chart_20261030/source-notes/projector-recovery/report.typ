#set page(paper: "a4", margin: (x: 16mm, y: 15mm), numbering: "1")
#set text(size: 10pt)
#set par(leading: 0.55em)
= Interval factor recovery from idempotents
*Preliminary derivation — unreviewed, unimplemented, zero trials.*

The selected shared-chart construction already asks for quotient idempotents witnessing interval membership. Those witnesses can also supply x-support and multiplicities through small linear algebra, without a separate generic factorization of the quotient polynomial.

#image("diagram.svg", width: 100%)

== Exact input and output
Let U be monic of degree k at least one over a prime field, and let Q be the quotient by U. For an s-bit interval of length strictly less than p, shifted by t, suppose the supplied quotient elements satisfy:
#raw("e_j² = e_j;   n^k = 0;   n = X − t − Σ 2^j e_j.", block: true)
The interval may wrap modulo p; k need not be less than p. The claimed output is distinct coordinates and positive integer multiplicities whose linear-factor product is U. The elliptic-curve application additionally keeps p greater than three and k at most five.

== Algorithm and splitting invariant
Use the k-dimensional power basis. Form multiplication matrices M for X and E_j for each e_j. They commute and every E_j is a projector. Start with the whole space. At bit j split each current subspace V into bases for the images of E_j V and (I−E_j)V, keeping only nonzero images and appending the corresponding bit.

Each split is a direct sum: the projector is identity on one image and zero on the other. Commutation preserves invariance under M and the remaining projectors. The dimensions always sum to k, so at most k nonzero spaces survive at any depth; the algorithm does not enumerate all interval labels.

On a final space with bitword b, define x_b as t plus its binary label modulo p. Multiplication by n restricts to M−x_b I and is nilpotent. The characteristic polynomial of that block is therefore the corresponding linear factor raised to its integer dimension. Multiplication by X on Q is the companion matrix of U, so the product of all block factors is exactly U. Interval injectivity distinguishes different bitwords, including across a wrap.

#pagebreak()
= Cost, uniqueness and remaining obligations

== Witness-assisted cost and independent check
Conservative classical arithmetic builds one multiplication matrix in O(k³) field operations. At each bit, current dimensions sum to k, so multiplying and eliminating all image bases also costs O(k³). Checking the idempotent and nilpotence equations fits the same total bound:
#raw("O((s+1)k³) field operations, including field inversions.", block: true)
Streaming projectors needs O(k²) workspace beyond O(sk) input field elements and at most k bit labels. Modular arithmetic bit costs remain separately chargeable. This is a derived bound, not a measurement.

An independent factor checker verifies canonical labels, distinct coordinates, positive integer multiplicities summing to k, then multiplies the linear factors and compares with U. This costs O(k²) field operations and does not trust reported matrix ranks. Original chart-witness checks remain required.

== Existence and uniqueness
If U splits into interval-root powers, the Chinese remainder decomposition provides local factors. Set each e_j to the coordinate label's bit on each factor. The idempotent equations hold and n is nilpotent of index at most k.

Conversely, an idempotent in each local factor is exactly zero or one. The nilpotence equation fixes the residue coordinate, and interval injectivity fixes all its bits. Hence the interval idempotents are unique for fixed U, t and s. This does not imply uniqueness of the signed chart function.

A characteristic-five hand example is U = (X−1)⁵, interval {0,1}, and e_0 = 1. The image of its projector has integer dimension five, although its field trace is zero. Recovery retains multiplicity five. This example was not executed and asserts no elliptic-curve instance. For degree zero use empty support; for a zero-bit interval the nilpotence equation gives the single coordinate t.

== Scope of the construction
The input includes already supplied interval witnesses. Their search cost and partial-assignment pruning are unresolved. Signed zeros of h = A+B y still require local orders, exactly one target-point subtraction, common A/B roots, inverse pairs, two-torsion and all lower-pole/identity charts. Balanced pairs can still require square-root work. The factor extractor's bound does not cover those tasks.

The predecessor coset/Graeffe domain and the new interval domain stay distinct. No-wrap moment substitutions are optional and are not needed for this recovery argument. Independent proof review and implementation are the next checks; scientific acceptance remains false.

== Sources
Stacks Project Example 10.35.24 (tag 00GG): standard idempotent matrices and the positive-characteristic trace pitfall. Section 10.53 (tag 00J4): finite algebras and local factors. Retrieved 30 October 2026. These sources support the background, not novelty or independent validation of this application. The detailed proof and source bindings are in proof.md and report-inputs.json.
