# TASK-20260926-843cf5 -- half A summary (1b16d7, 153a90, e3048d, c2bbe6, 7ab503)

Reviewer lane R3, half A, 2026-09-26. Advisory input to the next `/coordinate`
selection point (DEC-20260924-99ce20 NA-3); decides nothing, edits no record.
Per-idea reviews are the five YAML files beside this note. Every number below
was re-derived this session with self-contained Python arithmetic (no solver,
no experiment) unless marked `unchecked`.

## Summary table

| idea | verdict | agrees with hold? | one-line concrete experiment | successor seam |
| --- | --- | --- | --- | --- |
| IDEA-20260922-1b16d7 (HOLD-K, rank 23) | defective (parity reversed; headline population split dissolves; mechanism itself sound) | agrees, and the revision is larger than the hold implies | Exhaustive m = 2 and m = 3 decomposition census at RC-1 (n = 17, Tr(A) = 0) and the n = 19 cell (Tr(A) = 1) over V = {deg < l}, its two halves {c_0 = 0} / {c_0 = 1}, and a size-matched random subspace; zero-tolerance parity check, aligned/random yield ratio predicted 2 at every m | Parity as a degree-1 certificate inside the descended S_3 system at RC-1 -- is it in the row space, or only in W_4? (owner RQ-CERTBIN-836ce2) |
| IDEA-20260922-153a90 (HOLD-K, T5, rank 24) | sound_with_corrections (closure overreaches its own Sigma; part D conflates leg quotient with rho) | agrees (consolidation and T5) | E/4E class census on Koblitz n = 19 (#E = 4 * 130873): halving-bit histogram, class-sum certificate, yield of class-0-restricted window vs parity-aligned window (predicted 2^{1-m}), relabelled Z/(4l) replica | Non-linear window descriptions with constant E/4E class (KN-OPEN-020 open class; G3) |
| IDEA-20260922-e3048d (HOLD-O, rank 28) | defective (S = Z/4 has a Z/2 quotient; h = 1 null impossible; part B is base size) | agrees | Coset-class census at n = 19 Koblitz and RC-1: V vs C-restricted V_C yield ratio predicted 4^{m-1} (base-size law), parity ratio 2, Z/(4l) replica, h = 2 sibling as the no-Z/4 control | none -- merges into DC-04 (1b16d7/153a90) |
| IDEA-20260922-c2bbe6 (HOLD-Q, rank 31) | dominated (sqrt(2NB) >= 2^66.0 attempts on ECC2K-130 at B = 1 vs rho 2^60.81; plain free-leg is Theta(N)) | agrees; the GTTD route is a new proposal, not a revision | Target-free residual banking at RC-1 (m = 3, about 1.3e5 pairs): collision-rate ratio vs T^2/(2N), attempts-to-B-relations vs sqrt(2NB), Z/(4l) replica, truncated-key adversarial control | GTTD double-large-prime with an oracle cost model: exhibit oracle(V^{m-1} x W)/oracle(V^m) < m sqrt(B'/(2B)) (G1 lane) |
| IDEA-20260922-7ab503 (HOLD-R, rank 32) | defective (Frobenius is an equivariance between conjugate instances, a77711 Lemma A1/A2; no stable V at n = 131, 163; parser point stale) | agrees, with the ord_n(2) column added for FROB routing | Shift test on Koblitz n = 19 with non-stable V = {deg < 10}: shifted certified tuples decompose sigma(R) (predicted always) and never the same R; leg-swap and Z/l scalar-action controls; stable-V positive control at n = 17 | Normal-basis descent of the ORBIT system at a stable-V cell (n = 17 or 23) as HOLD-I's controlled confound (G3; owner FROB/CERTBIN) |

## Which of these five are worth designing next, ranked

1. **1b16d7 (revised) -- the only one with a runnable, cheap, decisive cell.**
   Once the parity table is corrected (aligned half is `{c_0 = Tr(a)}` at every
   m on every odd-n row; the other half at even m only) the record is a true
   per-row relabelling rule plus a census that the existing CERTBIN cells can
   run without a solver. Value: small (<= 1 bit at every m, no floor row
   moves), but it settles a claim three records in DC-04 lean on and seeds the
   one genuinely new question in this half (parity as a linear certificate
   inside the descended system). Rankable only after the revision.
2. **153a90 (as consolidated) -- keep the leg-side explanation, re-scope the
   closure.** Its closure section must go to review-breakthrough (T5) because
   it announces "completely" for a Sigma it does not cover; the E/4E pricing
   derived in its review (second bit non-linear in x, 2^{1-m} by rejection)
   is the answer to its own open number (C) and should be folded into the
   DC-04 revision rather than designed separately.
3. **c2bbe6 -- file as dominated at toy tier; spin the GTTD form out to G1.**
   Nothing to design under BINSTD; the useful residue is the inequality the G1
   lane must beat.
4. **7ab503 -- corrected census cells only; route the live rows to FROB.**
   K-233/K-283/K-409/K-571/sect239k1 host Frobenius-stable subspaces
   (ord_n(2) = 29/94/204/114/119); K-163 and ECC2K-130 do not (162, 130). No
   BINSTD design.
5. **e3048d -- no design; merge the chain certificate into DC-04.**

None of the five changes the ECC2K-130 picture: every one implies no change of
arity `m`, and the largest lever among them (parity alignment) is one bit on
the per-attempt oracle budget at `m = 4` (2^4.4 in KN-FIND-aa2efc's table,
2^6.6 under my standard-balance re-derivation). `m <= 3` stays closed.

## Arithmetic checks performed, by record

Common (all five):
- Matched rho on ECC2K-130: `r = 680564733841876926932320129493409985129`
  (Miller-Rabin prime; `log2 r = 129.000`, bit length 130), `k = 131`:
  `sqrt(pi r/(4k)) = 2^60.8090` -- reproduces KN-FIND-aa2efc. With `k = 262`
  (the 2n form several records use) it is `2^60.309`, 0.5 bit low.
- `#E(F_2^131)` for `y^2 + xy = x^3 + 1` by the Frobenius-trace recurrence
  (`#E(F_2) = 4`, `t = -1`): equals `4 r` exactly.
- Product-law floor re-derivation (standard balance `B^{m+1} = m! N`,
  `N = 2^131`, cost `B^2`, free oracle): m = 2 -> 2^88.00, 3 -> 2^66.79,
  4 -> 2^54.23, 5 -> 2^45.97, 6 -> 2^40.14, 8 -> 2^32.51. KN-FIND-aa2efc's
  table (89.25 / 68.58 / 56.40 / 48.44 / 42.85 / 35.61) is 1.2 to 3.1 bits
  higher on every row; its exact bookkeeping (`relations x targets x oracle
  = m 2^131`) was NOT reproduced and is marked `unchecked`. The qualitative
  verdict (m <= 3 closed even with a free oracle; m = 4 open with a 2^4.4 to
  2^6.6 budget) is reproduced under both.
- `ord_n(2)`: 13 -> 12, 17 -> 8, 19 -> 18, 23 -> 11, 29 -> 28, 31 -> 5,
  37 -> 36, 41 -> 20, 131 -> 130, 163 -> 162, 233 -> 29, 239 -> 119,
  283 -> 94, 409 -> 204, 571 -> 114.
- Koblitz toy orders `y^2 + xy = x^3 + a x^2 + 1`: a = 0: n = 17 -> 4 * 32743
  (not prime), 19 -> 4 * 130873 (prime), 23 -> 4 * 2095853 (prime),
  41 -> 4 * 549756390943 (prime); a = 1: 17 -> 2 * 65587 (prime),
  19 -> 2 * 262543 (prime), 23 -> 2 * 4196903 (prime); n = 163 a = 0 odd part
  composite, a = 1 (K-163) 2 * prime.
- Instrument availability: `numpy` is NOT installed in this container;
  `experiments/EXP-CERTBIN-e94b27/impl/{gf2n,curve}.py` import it at top
  level, so every concrete experiment says `missing: numpy` or lifts the
  scalar arithmetic.

IDEA-20260922-1b16d7:
- Newton bound `Tr(alpha^j) = 0` for `1 <= j < n - s`: computed
  `Tr(t^j)` in `F_2[t]/(t^17+t^3+1)`: 1 at j = 0, 0 for j = 1..16; in
  `F_2[t]/(t^19+t^5+t^2+t+1)`: 1 at j = 0, 0 for j = 1..16, 1 at j = 17,
  0 at j = 18. Consistent (bound sufficient, not necessary).
- `Tr(A)` on the two CERTBIN cells: RC-1 `A = 97044 -> 0` (`Tr(B) = 1`);
  n = 19 `A = 46693 -> 1` (`Tr(B) = 1`). The two cells are the matched
  `Tr(a) = 0 / 1` pair the census needs.
- Halving direction `Tr(x(2P)) = Tr(a)`: 1493/1493 (a = 0) and 1479/1479
  (a = 1) sampled doublings at n = 17.
- Parity table: legs in `{c_0 = 0}` have `pi = Tr(a)`; sum of m legs has
  `pi = m Tr(a) mod 2`; target `pi = 0` => Tr(a) = 1 rows empty at ODD m, not
  even. Legs in `{c_0 = 1}` (n odd) have `pi = 1 + Tr(a)`.
- Brief's Koblitz x-coordinate criterion generalised: `Tr(x) + Tr(a) +
  Tr(1/x) = 0` (b = 1) agrees with the half-trace lift on 3000/3000 x at
  a = 0 and 3000/3000 at a = 1.
- Rows re-read from the audit dump: sect163k1 A = 1 (0x1), B = 1 (0x1),
  cofactor 2; sect239k1 A = 0, cofactor 4; c2pnb208w1 A = 0. Other rows
  `unchecked` (relied on the record and 7ab503's agreeing read).

IDEA-20260922-153a90:
- Block systems of a regular action of `Z/r`, r prime: two. Chain on
  ECC2K-130: `E > 2E > 4E = C` (orders 4l, 2l, l), quotients Z/2, Z/4.
- `10080 = 2^5 * 315`, 315 odd.
- E/4E bit for `P in 2E`: `Tr(y_P + (lambda + 1) x_P)`, lambda a half-trace
  of `x_P + a`; well defined iff `pi(T) = Tr(a) = 0`; not F_2-linear in x.
  Rejection pricing: `2^{1-m}` relative to the parity-aligned window.

IDEA-20260922-e3048d:
- Z/12 subgroup lattice `{1,2,4} x {1,3}` -- splitting confirmed; `Z/4 -> Z/2`
  exists -- the record's "only trivial or all of S" is false.
- x-coordinate coset classes under negation: fractions 1/4 (class 0), 1/4
  (class 2), 1/2 ({1,3}). Yield-conservation pricing: unrestricted vs
  C-restricted legs give `4^{m-1}` more decompositions per C-target at 4x the
  unknowns (base size, not structure).
- h = 1 is impossible for `y^2 + xy = x^3 + a x^2 + b` (the point
  `(0, sqrt b)` always has order 2).

IDEA-20260922-c2bbe6:
- Single large prime: `T = sqrt(2 N B)`; at `N = 2^131`: B = 1 -> 2^66.00,
  2^10 -> 2^71.00, 2^20 -> 2^76.00, 2^30 -> 2^81.00; all above 2^60.81.
  Confirms the ranker's A13 up to sqrt 2.
- Plain free-leg: `T = N` to collect B relations.
- GTTD form (bookkeeping only): attempts `(m-1)! N sqrt(2B/B') / B^{m-1}`
  vs `m! N / B^{m-1}`; gain `m sqrt(B'/(2B))` at fixed arity against an
  oracle-side charge of `B'/B` under leaf-count proportionality.

IDEA-20260922-7ab503:
- Equivariance: `S_{m+1}` has F_2 coefficients for a, b in F_2, so
  `sigma` maps solutions for target R to solutions for `sigma(R)`;
  `sigma R != R` on G since sigma acts as a scalar of order n.
- Stable-subspace dimensions at prime n are subset sums of
  `{1, ord_n(2), ...}`: n = 131 and 163 give {0, 1, n-1, n}; n = 17 gives
  {0, 1, 8, 9, 16, 17}; n = 19 gives {0, 1, 18, 19}.
- `subfield_scan.py` line 17 regex now accepts the `(0x1)` suffix -- the
  parser gap is fixed on the current tree (history not checked).
- RC-1's `A = 97044` is not in F_2, so sigma is not an endomorphism of that
  curve; any Frobenius test needs a Koblitz sibling.

## Files written by this half-lane

- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-1b16d7.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-153a90.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-e3048d.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-c2bbe6.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-7ab503.yaml
- analysis/binstd-idea-review-20260926/reviews/TASK-20260926-843cf5-summary-a.md

No existing record was edited; no run was launched; no ID was minted.
