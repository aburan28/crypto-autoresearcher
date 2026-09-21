# Admission can destroy the intended affine structure

Internal artifact observation from RUN-KIC-c2b1b7, snapshot afad85a6dae42178feac397b25d7d7c99870fcf5. This is a post-run structural diagnostic and proposed successor, not an additional benchmark or a causal performance claim.

The two polynomial-coordinate seed flats were (a,b,c)=(23,7,121) and(42,17,34). Their eight j=0 abscissae are [23,110,16,105] and[42,8,59,25]. Only23 and105 survive the rational odd-subgroup admission. The canonical valid selector set in basis_manifest.json is exactly {(t,j,u,v)=(0,j,s,s):0<=j<7,s in{0,1}}. Root checked set equality against every stored selector. Thus the admitted domain can be written x=Frobenius^j(23 XOR126*s). The advertised two affine2-flats have collapsed to a single affine line before Frobenius closure.

This does not invalidate the frozen test: its circuit exactly represented that admitted set, and its correctness controls passed. It does mean that retained affine dimension and density should be measured before a larger-field co-design claim. It is not established that this collapse caused the observed timing or propagation outcome; no simplified-selector ablation has run.

A stronger proposed N19 construction keeps a complete affine2-flat: seek four admissible abscissae from four distinct full Frobenius orbits with x1 XOR x2 XOR x3 XOR x4=0. They then form a+span_F2{b,c} with all four seed values retained. Closing under Frobenius yields four signed point orbits, matching the152-point/four-column prior boundary without extra per-seed admission holes.

The existing frozen37-orbit pool is a useful bounded search space. Pair-XOR joins on its37*19=703abscissae can find four-orbit rectangles, excluding repeated orbit IDs and recording a canonical witness. Exact three-point group coverage must then be measured or replayed for those candidates; it cannot be inferred from the affine condition, clause counts, or the prior unconstrained winner. Select geometry/coverage before inspecting fresh SAT timing targets. Compare a compact affine encoding, a propagation-strong exact-domain encoding and the same-base cold MITM; all discovery/construction/encoding/verification costs and any use of prior per-curve advice must be explicit.

No rectangle search, N19 experiment, simplified-selector solve or broader claim is approved or performed by this note. The responsible next owner is the Coordinator after the independent N7 evidence review.
