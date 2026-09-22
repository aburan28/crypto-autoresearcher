# Prospective cofactor projection for an implicit affine factor base

This is an unapproved design note, not a run, a claim of novelty, a validated group-kernel theorem, or a timing result. It does not change EXP-KIC-424885. Root computed the exact integer identities below while the approved N7 implementation was being prepared.

The independently reviewed earlier N53 K0 fixture has subgroup order r=21,044,858,204,113 and cofactor428. Internal source: `research/cold_arm_composition_ic_20260921/artifacts/RUN-KIC-a15078/conformance/attempt1/n53/ic_candidate/stdout.jsonl`, its `point_defined_factor_base` record. Directly filtering a small affine coordinate domain for membership in this subgroup can discard many points. A different possible construction is to map rational seed points into the subgroup while retaining their simple seed-coordinate description as the decomposition variables.

Let t be a formal element satisfying t^2+t+2=0, the K0 Frobenius characteristic relation. Exact arithmetic in Z[t]/(t^2+t+2) gives

```
t^53 - 1 = 5,928,473 + 68,476,319 t
psi       = 1 - t - t^6 + t^8 = -15 + 7 t
eta       = 1,935,145 - 2,496,832 t
t^53 - 1 = psi * eta
Norm(psi) = 428
Norm(eta) = 21,044,858,204,113
gcd(Norm(psi), Norm(eta)) = 1
```

Here Norm(a+b t)=a^2-a b+2b^2. The product norm is9,007,199,311,360,364, equal to428r. These are verified integer-ring identities only. Their use as an elliptic-curve subgroup projection still requires a declared group-theoretic certificate, including the characteristic relation, separability, rational kernel and image-size obligations; do not silently treat the integer calculation as that review.

The candidate point map is

```
Psi(P) = P - Frobenius(P) - Frobenius^6(P) + Frobenius^8(P).
```

If its image on this exact rational curve group is certified to be the desired prime subgroup, one can propose B=Psi(C), where C is a rational-point set defined by simple affine seed coordinates. Decomposition would search for P_i in C satisfying Psi(P_1+...+P_m)=Q and output Psi(P_i), with full image membership, duplicate handling and group replay. This moves the subgroup condition into an explicit map; it does not make the map or its SAT constraints free. It also uses the endomorphism on the sum once, rather than assuming independent images supply unrelated constraints.

The four-term Frobenius expression suggests a compact arithmetic circuit, but this has not been implemented or measured here. A useful test must charge raw-domain construction, rational lifts, Frobenius maps, group additions, exceptional branches, image collisions, SAT encoding and decoding, and the relation/rank consequences. It must compare the image construction with the existing cofactor-cleared point-defined base and direct decomposition on exactly the same image set. Raw and projected cardinalities and effective orbit columns must all be reported.

Small fixed seed dimension is only an instrumentation choice. Two affine2-flats supply at most8n abscissae and16n signed points before filtering/collisions; increasing field size without increasing seed dimension cannot be assumed to preserve useful coverage. Any larger-field contract must state the seed-dimension schedule and quantify coverage alongside solving cost.

The first proof obligation could be formalized as the displayed polynomial identity in the quadratic quotient ring. The group-kernel/image obligation is separate and cannot be replaced by that easier identity. A bounded implementation control could check point-map identities and kernel/image behavior on compatible exhaustive small curves, followed by explicitly known synthetic points at the exact N53 parameters; such a protocol has not been approved or run.

The general use of Frobenius-invariant factor bases is prior art, not a novelty claim: Galbraith, Granger, Merz and Petit, *On Index Calculus Algorithms for Subfield Curves*, https://eprint.iacr.org/2020/1315.pdf (retrieved and opened by root). Novelty of this particular base/solver composition is unverified. The current N7 SAT experiment must finish its own fixed controls, measurements and independent review before this lead is ranked for execution.
