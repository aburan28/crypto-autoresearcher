# Exact witness transport: implementation obligations

This note explains the frozen finite experiment. It is not a machine-verified theorem or a performance result.

Let B be the checked point base, closed under negation and Frobenius tau. Let gamma be a signed Frobenius automorphism. If a table stores U+V=C and the actual residual R=Q-P satisfies gamma(R)=C, then

    gamma^-1(U) + gamma^-1(V) + P
      = gamma^-1(U+V) + P
      = gamma^-1(gamma(R)) + P
      = R + P = Q.

All three returned points are in B: P was enumerated from B, and B is invariant under gamma and its inverse. For gamma=epsilon*tau^j, the inverse is epsilon*tau^((19-j) mod19). This explains why the inverse shift and sign are part of the certificate rather than an optional label.

Anchoring the first point of each orbit pair loses no pair-sum orbit. For any original pair, a common signed Frobenius transform sends its first point to the supplied representative of that orbit; the second point remains in its own full orbit. Enumerating all38signed conjugates of the second point therefore covers every transformed sum, including repeated or opposite points. Deduplication may choose a different valid pair witness, but it must retain a real pair and its stored sum.

The normal-x variant uses a coarser key. For a nonzero abscissa on this binary curve, the two rational lifts are negatives. After matching canonical x, the implementation must compare the transformed residual with the stored full sum, choose the correct sign, and only then invert the transform. It must never treat an x match as an already recovered witness. Infinity has a distinct tag; the short-orbit point T=(0,1) is tested in canonicalization controls and remains outside the prime-subgroup query domain.

The experiment checks the concrete implementation rather than assuming this abstract argument applies: all field conversion/Frobenius cases, all subgroup pair-membership points, every recorded canonical witness, all nonzero target-orbit queries, explicit exceptions, and corrupted shifts/signs. An independent checker uses separate arithmetic and replays the returned group identities.

The formalization gap is the concrete codec and normal-conversion correspondence with an additive-group automorphism. An abstract Lean proof of the displayed identity alone would not verify the C++ lookup or its index/sign conventions. That bridge remains a separately recorded future formalization obligation if the implementation merits reuse.
