# EXP-FROB-ec08b5 — the Frobenius-stable factor-base design space

Run `RUN-FROB-627924`. Every number below is an exact finite count; nothing is sampled or estimated.

## Preregistered predictions

| id | prediction | verdict |
| --- | --- | --- |
| P1 | four independent lattice methods agree | HELD |
| P2 | totient and Burnside censuses agree | HELD |
| P3 | stable V gives a pi-stable factor base; both controls fail | HELD |
| P4 | orbit count equals f + (|F_V| - f)/n exactly | HELD |
| P5 | net loss at n = 131, 163; net win available at n = 127 | HELD |

## Verification

- self-test fixtures: 10/10 pass
- lattice cells cross-checked by 4 methods: 12, of which 10 also by exhaustive subspace enumeration
- stable subspaces compared across two independent orbit-census derivations: 200, mismatches: 0
- curve cells measured: 14, factor-base points enumerated: 6844, largest factor base: 4005

## Curve panel — measured Frobenius orbits on real factor bases

| q | n | dim V | j-index | \|F_V\| | fixed | orbits | predicted | exact | reduction | non-stable V control | null-curve control |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 5 | 4 | 0 | 21 | 1 | 5 | 5 | yes | 4.2000 | fails as required | fails as required |
| 2 | 7 | 3 | 0 | 1 | 1 | 1 | 1 | yes | 1.0000 | fails as required | fails as required |
| 2 | 7 | 4 | 0 | 3 | 3 | 3 | 3 | yes | 1.0000 | fails as required | fails as required |
| 2 | 7 | 6 | 0 | 57 | 1 | 9 | 9 | yes | 6.3333 | fails as required | fails as required |
| 3 | 5 | 4 | 0 | 52 | 2 | 12 | 12 | yes | 4.3333 | fails as required | fails as required |
| 3 | 5 | 4 | 1 | 60 | 0 | 12 | 12 | yes | 5.0000 | fails as required | fails as required |
| 5 | 3 | 2 | 0 | 37 | 1 | 13 | 13 | yes | 2.8462 | fails as required | fails as required |
| 5 | 3 | 2 | 1 | 23 | 2 | 9 | 9 | yes | 2.5556 | fails as required | fails as required |
| 2 | 11 | 10 | 0 | 1057 | 1 | 97 | 97 | yes | 10.8969 | fails as required | fails as required |
| 3 | 7 | 6 | 0 | 786 | 2 | 114 | 114 | yes | 6.8947 | fails as required | fails as required |
| 3 | 7 | 6 | 1 | 700 | 0 | 100 | 100 | yes | 7.0000 | fails as required | fails as required |
| 4 | 3 | 2 | 0 | 15 | 3 | 7 | 7 | yes | 2.1429 | fails as required | fails as required |
| 4 | 3 | 2 | 1 | 27 | 3 | 11 | 11 | yes | 2.4545 | fails as required | fails as required |
| 2 | 13 | 12 | 0 | 4005 | 1 | 309 | 309 | yes | 12.9612 | fails as required | fails as required |

## Target degrees — is the orbit trick available, and is it a net win?

`d` is ord_n(q); `s` the number of irreducible factors of Phi_n over F_q; `d_faith` the smallest stable dimension on which Frobenius acts non-trivially. `l*` = ceil(n/m) is the unconstrained Gaudry dimension, `l'` the smallest attainable faithful one at least that large. Margin is log2(mean orbit size) - (l' - l*)*log2(q): positive means the orbit quotient outweighs the factor-base inflation.

| q | n | d | s | #stable | d_faith | m=2 | m=3 | m=4 | m=5 | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 113 | 28 | 4 | 32 | 28 | win +6.8b | loss -11.2b | win +6.8b | win +1.8b | SECG-adjacent binary degree |
| 2 | 127 | 7 | 18 | 524288 | 7 | win +7.0b | win +7.0b | win +4.0b | win +5.0b | Mersenne-prime extension degree |
| 2 | 131 | 130 | 1 | 4 | 130 | loss -57.0b | loss -79.0b | loss -90.0b | loss -96.0b | ECC2K-130 challenge degree |
| 2 | 163 | 162 | 1 | 4 | 162 | loss -72.7b | loss -99.7b | loss -113.7b | loss -121.7b | NIST K-163 / B-163 |
| 2 | 233 | 29 | 8 | 512 | 29 | win +7.9b | loss -1.1b | win +7.9b | loss -3.1b | NIST K-233 / B-233 |
| 2 | 239 | 119 | 2 | 8 | 119 | win +7.9b | loss -31.1b | loss -51.1b | loss -63.1b | SECG sect239 family |
| 2 | 283 | 94 | 3 | 16 | 94 | loss -37.9b | win +8.1b | loss -14.9b | loss -28.9b | NIST K-283 / B-283 |
| 2 | 409 | 204 | 2 | 8 | 204 | win +8.7b | loss -58.3b | loss -92.3b | loss -113.3b | NIST K-409 / B-409 |
| 2 | 571 | 114 | 5 | 64 | 114 | loss -46.8b | loss -27.8b | loss -75.8b | win +9.2b | NIST K-571 / B-571 |
| 2 | 41 | 20 | 2 | 8 | 20 | win +5.4b | loss -0.6b | loss -3.6b | loss -5.6b | GOAL-FROB-6333a9 primary cell |
| 2 | 43 | 14 | 3 | 16 | 14 | loss -0.6b | win +5.4b | win +2.4b | win +0.4b | GOAL-FROB-6333a9 decisive cell |
| 2 | 7 | 3 | 2 | 8 | 3 | win +2.0b | win +2.0b | win +1.0b | win +1.0b | toy |
| 2 | 11 | 10 | 1 | 4 | 10 | loss -0.6b | loss -2.6b | loss -3.6b | loss -3.6b | toy |
| 3 | 41 | 8 | 5 | 64 | 8 | win +0.6b | win +2.2b | loss -2.6b | win +5.3b | odd-characteristic comparison |
| 4 | 41 | 10 | 4 | 32 | 10 | win +5.4b | loss -6.6b | win +5.4b | win +3.4b | q = 4 comparison at the same n |
| 8 | 41 | 20 | 2 | 8 | 20 | win +5.4b | loss -12.6b | loss -21.6b | loss -27.6b | q = 8 comparison at the same n |

## Scope

- Scoped to the Gaudry/Diem factor-base family `F_V = {P : x(P) in V}` with V an F_q-subspace. Other factor-base shapes are not covered.
- Clauses about orbit length are for n an odd prime with gcd(q, n) = 1. The lattice itself is verified also at p | n, where T^n - 1 is not squarefree.
- Structural availability is not practical feasibility: a cell marked `win` at large m says nothing about whether the Semaev system at that m can be solved.
- No discrete logarithm is solved and no deployed curve is an instance.
