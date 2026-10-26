# F3 clarification: nonzero coefficients are required modulo r

2026-10-25. Additive correction to the sealed F3 report's conditional
useful-target-coefficient lemma. The original report and receipts are retained.
The isolated local reviewer identified this qualification; see
`reviews/relations_and_bounds/` for its counterexample and coverage record.

The correct statement is: let label pairs (a_i,b_i) be independent uniform
elements of F_r^2, conditioned only on the points R_i=a_iG+b_iQ. Let a
point-only search return an aggregate coefficient vector c in F_r^N that is
nonzero. Conditioned on the point data and this vector, B=sum(c_i b_i) is
uniform in F_r, so Pr(B=0)=1/r. Consequently a nonzero B permits recovery
of the target scalar from A+dB=0, followed by a point verification.

An integer vector that is nonzero over Z may reduce to zero modulo r. The
counterexample c=(r,0,...) is always a subgroup relation but gives B=0 for
every label set. Thus the report's phrase "nonzero relation vector" must be
read as nonzero after reducing and aggregating the coefficients modulo r.
The original wording allowed integer multiplicities without stating that
qualification explicitly.

The implemented three-point search uses small signed coefficients and already
distinguishes zero-information dependencies. Its retained point certificates
and control outcomes are unchanged. The correction narrows the stated lemma;
it supplies no natural relation frequency, solving cost, or ECDLP advantage.
Adaptive label construction or relation selection that reads labels still
falls outside the independent point-only conditional argument.
