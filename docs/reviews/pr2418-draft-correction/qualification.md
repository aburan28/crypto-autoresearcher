# Review qualification for the unapproved RC-2 drafts

This review applies to the six draft and pilot paths at commit `cb425b67ec65d14a9e6eec007937750ffdcdda68`, with original hashes in `review-bindings.json`. The two unfrozen proposals remain `review_required` and `execution_authorized: false`. The published pilot scripts and logs, original study inputs and archived results are preserved. This correction authorizes no experiment and does not adopt the proposed support decision.

For `N = 353`, `B = 13`, and `lambda = 222`, the quadratic `lambda^2 - lambda + 5` vanishes modulo N and lambda has multiplicative order 22, exceeding B. The first B powers are distinct labels but occupy only eleven classes modulo sign: both 1 and -1, and both 222 and -222, occur. The attached finite arithmetic fixture records every label. Thus order greater than B is insufficient for the distinct-class convention used by the frozen `random_labels`. A matched protocol must check B distinct nonzero sign classes directly. The pilot logs do not retain per-member labels, so this counterexample does not assert that a particular historical pilot member was affected.

Randomizing signs is an abstract model. It does not reproduce a curve chart's canonical sign choices without a verified mapping. Likewise a CM-versus-generic comparison must use the same eligible moduli, or explicitly limit its inference to separately sampled populations. The unapproved draft now requires the matched choice to be frozen before approval. The other-norm contrasts need a stated common-population or separately matched design.

The small exploratory pilot does not determine C24 variance or an asymptotic variance law. The proposed sample counts and power calculations remain planning assumptions. A finite mean-coverage interval does not prove full distributional exchangeability. The proposed support text now names that narrower observable; its original independence and archival prerequisites remain unresolved.

Conservation bounds coverage by `min(1, mu)` and the ratio to a positive baseline by `min(1, mu)/c0` at each instance. A uniform constant ratio over growing N additionally requires a uniform positive lower bound on baseline coverage. These drafts establish no asymptotic cost or exponent conclusion. The prospective clustering explanation remains untested.

Validation is limited to parsing the two proposals and recomputing the finite arithmetic counterexample and preservation hashes. No pilot, solver or campaign command was executed for this review.
