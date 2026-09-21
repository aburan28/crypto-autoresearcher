# Independent Red-Team Review

Reviewer task `019fafa3-a931-70d0-bab3-8e7e356ca8ab` audited exact commit
`30793d7d676014f8c044073d7b12e679c4ed694f`.

Decision: `REVISE`; preserve only as a reproducible toy functional
observation.

The review matched all manifest hashes, reproduced the verifier receipt
byte-for-byte, obtained the same normalized generator rerun, and found no
subgroup scalar census in the attack-eligible construction, row selection,
solving, or lookup path.

The narrow positive claim is:

> On three generated toy prime-order curves and one seed, four public
> coordinate sets have exact `A+4R` support `0.3403-0.4548`. Retaining all
> supported `A` splits and one canonical `4R` witness per complement produced
> full quotient rank and correctly evaluated every supported held-out target.

The verifier envelope is a scoped negative result. Five adversarial mutations
still returned valid: changing a curve trace, zeroing accounting, removing an
independent target transcript entry, truncating descent coverage, and changing
a random-x source with local digest repair. It validates listed witnesses but
does not attest transcript completeness, source predicates, curve exclusions,
stopping rules, or accounting.

Further limitations:

- descent evaluated supported targets only, not arbitrary targets;
- one canonical `4R` tie-break remains a rank-selection risk;
- memory, bandwidth, and baseline accounting are incomplete;
- three sizes and one seed do not establish asymptotics;
- the exact field policy was `p mod 4 = 3`, with no enforced embedding-degree
  exclusion.

The recommended hardening successor reconstructs all deterministic streams,
factor-base predicates, curve policies, accounting gates, multiple witness
policies, and randomized arbitrary-target descent, with mutation tests for
every success condition.
