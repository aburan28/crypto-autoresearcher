---
id: KN-OPEN-9b71bb
type: open_problem
title: >-
  Hard-to-factor composite group order as a partial ECDLP trapdoor -- is there any parameter regime in which knowing the factorization of #E beats what an outsider gets from ECM plus Pohlig-Hellman, or is the construction closed by the ECM bound?
tags: [trapdoor, composite-order, pohlig-hellman, ecm, factoring, partial-trapdoor, expected-negative, ecdlp, open]
confidence: reported
status: open
source_refs: [KN-TECH-6ead00, KN-TECH-906e14, KN-TECH-005, KN-TECH-006]
added: 2026-09-30
superseded_by: null
---

## Statement

Let `E/F_p` have order `N = prod_i q_i` with the `q_i` prime and the
factorization known only to the generator. Pohlig-Hellman reduces the ECDLP
to DLPs in each `q_i`-subgroup, costing `sum_i sqrt(q_i)` with rho, so the
holder pays about `sqrt(max q_i)` while an outsider who cannot factor `N`
pays `sqrt(N)`. With `N = q_1 q_2` and `q_1 ~ q_2 ~ N^{1/2}` the holder's
cost is `N^{1/4}`; with `r` equal factors it is `N^{1/(2r)}`.

**Question.** Is there any `(log N, r)` for which the holder's cost is
feasible while (a) the outsider cannot factor `N` and (b) the outsider's
`sqrt(N)` is infeasible? Equivalently: does the ECM bound close this
construction for every `r`, or is there a corner where it survives?

## The expected-negative argument (recorded so it is not re-derived)

- `N` is public (SEA), so the outsider's task is to factor a number of
  `log N` bits with `r` factors of `log N / r` bits each.
- For `r >= 3` the factors are small relative to `N` and ECM finds a
  factor of `b` bits in about `L_{2^b}(1/2, sqrt 2)` work independent of
  `N`. Published ECM records reach roughly 270-bit factors; to resist, each
  `q_i` must be at least about 250 bits, giving the holder a rho cost of at
  least `2^125` per subgroup, which is not a trapdoor.
- For `r = 2` the outsider's attack is NFS on `N`; resisting it needs
  `log N` above 2000 bits, and the holder's `N^{1/4}` is then `2^500`.
- In every regime, the holder's advantage is a fixed fraction of the exponent
  and never subexponential, so it cannot overcome the size that the
  factoring resistance forces.

## What would overturn it

A subgroup-DLP algorithm that benefits from the *co-factor* structure (for
example, an efficiently computable map that uses the other `q_j`-subgroups
as a factor base), or a family of `N` that resists ECM and NFS at a size
where `N^{1/(2r)}` is still feasible. Neither is known. The composite-
modulus analogue where the secret is the factorization of the *field* rather
than of the *order* is the genuine (factoring-based) trapdoor of
KN-TECH-906e14, and the two should not be confused.

## Why it is filed

The construction is proposed often enough in trapdoor discussions that the
taxonomy (KN-TECH-6ead00) needs a citable record of why it fails. It stays
an *open problem* rather than a finding because the negative argument is a
cost comparison against current factoring records, not a theorem, and the
program's rules do not let an unrun cost estimate be promoted to a finding.
