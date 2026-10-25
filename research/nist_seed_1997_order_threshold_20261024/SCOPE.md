# Scope and inference rule

Date: 2026-10-24 UTC. This is a **post-observation**, source-motivated audit, not a preregistered discovery experiment. The first diagnostic already showed that the P-224 omitted orders exceed the published order before this file was written.

Question: Can one field-fixed lower subgroup-order threshold `r_min`, the free parameter in §F.2.2 and §F.3.2 of the 17 November 1997 ANSI X9.62 draft, accept every published prime-field sample and reject every earlier named full-prime-order omission in that same field?

Inputs: the eleven exact omitted `p,n,seed,ordinal` rows in `research/nist_seed_skipped_curves_20261016/assessed.json`; the ten published prime-field `p,n,seed,ordinal` rows in `research/nist_seed_selection_20261016/targets.json`; the prior independent prime-order point certificates in `research/nist_seed_selection_20261016/raw/full_prime_order_certificates.jsonl`; and the 21-label matrix in `research/nist_seed_selection_deep_20261016/selection_matrix.json`. Compare the four fields with named omissions: 192, 224, 239 and 256 bits, eight published and eleven omitted rows. P-384 and P-521 have no named omissions and cannot falsify a within-field threshold.

Predicate: a prime full-order candidate passes exactly when `n >= r_min`. For a field, every published row passes only if `r_min <= min(published n)`. An omitted row with `n >= min(published n)` therefore passes under **every** threshold that admits all published rows. Count such unavoidable omissions. A complete separator exists iff `max(omitted n) < min(published n)` for that field. No optimization, significance test, or historical attempt-count inference is permitted.

Controls: check every archived certificate's exact `p,n` against the named row; require its primality and order certificate flags; require the four field sizes and expected 8/11 counts; verify the boundary threshold `r_min = min(published n)` directly. A separate verifier redoes the integer inequalities from source rows without importing the analysis module.

Interpretation: a counterexample rejects this **field-fixed threshold as a complete selection rule**, conditional on the program visiting those positions. It does not exclude a threshold that changes during a run, a combined rule, a software failure, an unpublished policy, or a hidden weakness. The draft's advised `r_min <= p+1-2 sqrt(p)` is a stronger restriction already covered by the prior acceptance report.
