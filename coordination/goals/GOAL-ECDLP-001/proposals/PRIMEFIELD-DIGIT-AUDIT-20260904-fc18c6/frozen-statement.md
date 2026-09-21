# Precision-two ordinary-digit representation audit

Frozen by DEC-20260904-4f0f52. This is a non-batch theoretical audit with zero experiments. It concerns the definitions below and no ECDLP algorithm.

Let p > 3 be prime, E/F_p an ordinary elliptic curve in short Weierstrass coordinates y^2=x^3+ax+b with nonzero discriminant, and K=F_p(E). Fix the Serre-Tate canonical lift and the associated elliptic Teichmuller section tau, in compatible short Weierstrass coordinates. Write the x coordinate of tau as the length-two Witt vector (x,x_1). The specified global x_1 is the coordinate function of that section, not an arbitrary interpolation of its F_p values. Cite the source hypotheses needed for this identification. A prime-to-p subgroup may motivate the question but is not the summation domain of the theorem being audited.

For z in Z/p^2 Z let d_1(z) be its ordinary base-p second digit using the unique integer representative in [0,p^2). For a in F_p let u(a) be its representative in {0,...,p-1}; let [a] be its Teichmuller representative modulo p^2. Define c_p(a)=([a]-u(a))/p modulo p and let C_p(X) be its unique polynomial representative of degree less than p. Distinguish d_1, the second Witt coordinate, and a primitive additive character of the whole Witt vector.

Determine, with proofs or exact unresolved obligations:

1. The exact relationship among d_1(z), c_p(a_0), and Witt coordinates (a_0,a_1).
2. The degree and leading coefficient of C_p, the pole divisor of C_p(x), its reduced Artin-Schreier pole order at O, and the conductor of its additive-character sheaf.
3. The same quantities for the specified global representative F_can=x_1+C_p(x). Treat Artin-Schreier equivalence in K separately from equality of values on affine E(F_p).
4. The full-curve additive sum coefficient furnished by the source theorem, its normalization by #E(F_p)-1, and its comparison with the trivial bound. Do not infer subgroup/hybrid sums, bucket statistics, majority advantage, or an algorithmic cost improvement.
5. What changes when a polynomial representative is reduced modulo X^p-X. Determine whether the source's global leading pole survives that change. Minimal conductor across all sample-equivalent functions is not requested and must not be claimed.
6. Why the canonical-lift statement does or does not transfer to b4e6eb's arbitrary good-reduction model. State any unproved transfer explicitly.

Reduced pole order refers to the local pole order of the Artin-Schreier class of f modulo g^p-g, with the definition and coefficient normalization checked against the cited source. Constants and geometrically trivial characters must be handled explicitly. Infinity O is outside the affine-coordinate summation domain; its omission must be charged.

Required controls, all symbolic:

- Precision one recovers the residue x; the standard x-coordinate has its ordinary pole at O and provides a baseline for conventions.
- Compare synthetic Witt vectors (u,0), (u,-C_p(u)), and constant vectors: calculate which of the three observables is constant in each case.
- Compare f=0 and f=g^p-g, including g=x, so a raw pole is not mistaken for a reduced pole.
- Compare zero with (x^p-x)x on affine E(F_p), and compare F_can with its polynomial remainder modulo X^p-X. These are tests of sample equivalence versus global conductor.
- Optional exact source fixture: the ordinary p=5 example in Voloch-Walker Remark 4.3. It is a representation control, not a prime-order or generic-family sample.
- An anomalous curve with group order p has no nonidentity prime-to-p point; it cannot supply the discarded proposal's separating control.

The blind re-deriver receives this statement, source URLs or identical external source bytes, governing contracts, and its own handoff only. It may not read the producer's protocol, report, notes, preparation/admission reasoning, coordinator prior, or outputs. It must report each quantity and control before seeing the producer's answers.

Sources: [Voloch-Walker, Sections 3-4](https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/codes15.pdf); [Blache, Section 3](https://arxiv.org/pdf/math/0202206). These are source material to inspect, not permission to presume applicability.

