# NIST Koblitz signed-Frobenius rho audit

Status: **derived consistency audit of archived certificates and random-map model; no rho timing or solve.**

| curve | ord(lambda) | signed orbit | gain vs negation (bits) | transitions factor | conditional endpoint ceiling |
|:--|--:|--:|--:|--:|--:|
| K-163 | 163 | 326 | 3.674364 | 12.767145x | 7.8326% |
| K-233 | 233 | 466 | 3.932093 | 15.264338x | 6.5512% |
| K-283 | 283 | 566 | 4.072329 | 16.822604x | 5.9444% |
| K-409 | 409 | 818 | 4.337979 | 20.223748x | 4.9447% |
| K-571 | 571 | 1142 | 4.578673 | 23.895606x | 4.1849% |

The gain column compares with the same curve's negation-only rho. The additional half bit in the
plain-rho comparison is not a second Koblitz advantage. Conditional on an endpoint having only
negation as a usable quotient, the floor ceiling is its maximum cost per transition
relative to one fully charged source signed-tau transition, needed
to offset the lost orbit quotient before setup and transfer costs.
