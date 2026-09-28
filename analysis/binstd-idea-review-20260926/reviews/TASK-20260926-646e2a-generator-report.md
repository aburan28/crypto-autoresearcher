# TASK-20260926-646e2a generator report (seam S3, round 2)

Lane: idea-generator, policy research-deep, seam S3 (Galois-invariant and
algebraic-group factor bases at n = 131, the Couveignes-Lercier successor
question, KN-OPEN-095df5). Written 2026-09-28 after the lane was interrupted.

## Outcome: no proposal filed; all five ids returned unused

The reading list on the card was completed in full (card, BRIEF.md sections
0-4, BRIEF-ROUND2.md, the rendered frontier map, agents/idea-generator.md,
docs/inventor-protocol.md, docs/object-frame-ideation.md, the exemplar
IDEA-20260922-845a77, KN-OPEN-095df5 with both census scripts and
exact_targets.json, KN-LIT-796 and its superseding KN-LIT-0d9d28,
IDEA-20260918-9abf42, KN-FIND-47da4e, IDEA-20260926-b6cc43, the titles and
claims of every IDEA-20260926-*.yaml, analysis/frobenius-orbit-ecc2k130/README.md,
experiments/EXP-CERTBIN-e94b27/impl/README.md, and the corpus greps listed
below).

The generation of the first record (IDEA-20260926-56d3c9) was stopped by the
runtime's safety classifier while the file was being written. The write was
cut off after 23 lines, inside the `claim` block. The runtime instructed the
agent not to produce that content again, and the agent has complied: the file
was not completed, not rewritten, and no other proposal was written.

**Action required by the dispatching session (the agent may not delete
files):** `ledger/proposals/IDEA-20260926-56d3c9.yaml` is a TRUNCATED,
schema-incomplete fragment and must be removed from the branch before any
commit; it is not a filed record and must not be validated, cited or
superseded. The id IDEA-20260926-56d3c9 is returned unused along with the
other four.

Unused ids returned by name: IDEA-20260926-56d3c9, IDEA-20260926-5c26f9,
IDEA-20260926-6f2601, IDEA-20260926-80209d, IDEA-20260926-84e2c0.

## Inventor-protocol section 5 block (honest accounting)

- **Object(s) considered:** the seam's own candidate list as stated on the
  card and in KN-OPEN-095df5 -- commutative algebraic groups over F_2 with a
  rational point of order 131 (abelian varieties of dimension 5 and 6 by exact
  Weil-polynomial census; algebraic tori, in particular the dimension-48
  norm-one torus KN-OPEN-095df5 already names; unipotent and non-commutative
  groups) as sources of Galois-invariant subsets of F_{2^131} with a low-degree
  membership condition. No proposal about any of them was filed.
- **Depth of verified structure:** none claimed by this lane. Nothing beyond
  what KN-OPEN-095df5, IDEA-20260918-9abf42, KN-FIND-47da4e and
  IDEA-20260926-b6cc43 already record is asserted here.
- **dominated_by:** "n/a (no result claimed)".
- **sota_delta:** no attack; no contribution filed; zero on every axis.
- **Enumerated closures:** none. The lane does not close the seam. The
  written Couveignes-Lercier constructions remain excluded at n = 131 over F_2
  exactly as KN-OPEN-095df5 states, and the open problem stays open.
- **Open directions for the next session (pointers only, no new claims):**
  1. The dimension-5 and dimension-6 exact census that KN-OPEN-095df5 names as
     its first cheapest test, using analysis/couveignes-lercier-131/
     exact_targets.py extended past `--max-dim 4` (the Weil bound
     (1 + sqrt 2)^(2g) puts the candidate multiples of 131 at 51 for g = 5 and
     299 for g = 6; the coefficient-box enumeration will need the exact
     Rolle-style pruning that weil_census.py does numerically, since the
     per-target head enumeration of exact_targets.py does not scale to g = 5).
  2. The torus row of KN-OPEN-095df5 (131 | Phi_130(2), dimension phi(130) =
     48), which that entry leaves without a degree bound; a successor lane
     should price its membership condition explicitly rather than by recall.
  3. Reading Couveignes-Lercier directly, which KN-OPEN-095df5 lists as its
     second cheapest test and which has still not been done in this program.
  4. The rich-versus-poor n ladder of IDEA-20260918-9abf42 and the 9e5383
     review's successor seam (primitive versus non-primitive prime at matched
     degree) as the toy control for anything filed here later.

## Novelty greps run (for the next session's reuse)

`Couveignes|Lercier` (39 files; the only ECDLP-relevant hits are
KN-OPEN-095df5, KN-FIND-47da4e, IDEA-20260922-6cf862, GOAL-FROB-6333a9,
DEC-20260922-e9d35a; the rest are unrelated literature stubs); `torus|tori|
norm-one|Honda-Tate|Weil polynomial|isogeny class|genus 5|Galois-invariant|
GGMP` (250+ files, dominated by unrelated isogeny and lattice records);
`Phi_130|409368176241571|dimension 48` (KN-OPEN-095df5 only, plus an
unrelated lattice record IDEA-20260816-49b818); `autocorrelation|convolution
product|cyclic convolution|mu_131|131st root|131st power|Kummer extension|
cyclotomic subgroup` (106 files; none proposes a factor base on this seam).
The frontier rows positioned against were KR-IC-b0fcda and KR-IC-73db3f. No
web search was run. Every literature reference this lane would have used is
`recalled` or `internal`; any successor record on this seam must carry
`novelty_status: unverified` unless it checks the Couveignes-Lercier text.

## Files written by this lane

- this report;
- `ledger/proposals/IDEA-20260926-56d3c9.yaml` -- TRUNCATED FRAGMENT, to be
  removed by the dispatcher (see above).

No existing record was edited. No run was made. No status changed.

## Second attempt (2026-09-28, seam S3 narrowed to exact censuses and pricings)

Dispatched by the top-level session as the second attempt of the same
handoff, with the scope narrowed to zero-run or near-zero-run exact
computations (no attack designed, no experiment on the challenge curve). The
truncated fragment named above is no longer on disk (glob of
`ledger/proposals/IDEA-20260926-*.yaml` on 2026-09-28 shows no 56d3c9 file);
the dispatcher's removal is taken as done and nothing was written to that id.

### Outcome: three proposals filed, two ids returned unused

| id | class | one line |
| --- | --- | --- |
| IDEA-20260926-5c26f9 | measurement | Exact dimension-5/6 Weil-polynomial census over F_2 for 131 dividing the point count (51 and 299 candidate multiples re-derived from the exact ceilings 6725 and 39201), Rolle-pruned with integer Sturm tests and the last coefficient pinned by congruence, validated against the LMFDB's complete class counts 1645, 14325, 164937 at g = 4, 5, 6 (retrieved); three outcomes defined before any run. |
| IDEA-20260926-6f2601 | control | The torus row priced as a certificate with numbers: 131 divides Phi_k(2) iff k = 130 x 131^j, so every F_2-torus with a rational 131-point has dimension >= 48 (T_130 attains it; Phi_130(2) = (2^65 + 1)/90123 = 131 x 3124947910241, 131 exactly once); Lemma L, that any translation-stable function space on any commutative group gives a Frobenius-stable subspace of F_{2^131}, hence one of 9abf42's four, with the degree-1 torus base exactly the trace-zero hyperplane; the non-stable shape is an orbit union costing >= 17030 F_2-unknowns per slot more than KN-FIND-47da4e's parameterisation. |
| IDEA-20260926-80209d | control | The toy control ladder at n in {17, 23, 31, 41} versus {19, 29, 37}: torus dimensions phi(ord_n(2)) = 4, 10, 4, 8 and 6, 12, 12; the elliptic row empty at every prime n >= 7 over F_2; the abelian-surface row present at n = 19 only (h = x^2 + 3x + 1, 19 points) and absent at 17, 23, 29, 31 by a closed enumeration; threefolds and the genus-2/3 Jacobian columns computed by the existing exact search plus curve enumeration; matched pairs (17, 19) and (31, 37) on the two axes. |

Unused ids returned by name: IDEA-20260926-56d3c9, IDEA-20260926-84e2c0.

### Ranking rationale and first test

Information gain per unit cost ranks 6f2601 first for reading (zero-run,
exact, and it tells the census what a hit can give), 5c26f9 first for running
(hours of single-core Python, either outcome informative), 80209d last (a
fixture, minutes, useful only alongside future experiments). The single test
to run first is 5c26f9's enumerator at g <= 4 unfiltered: if it does not
reproduce 5, 35, 215, 1645 nothing downstream is trusted, and it is the
cheapest valid discriminator between "the exclusion extends" and "the
enumerator has a gap", which is the exact ambiguity KN-OPEN-095df5 discloses.

### Inventor-protocol section 5 block (honest accounting, second attempt)

- **Object(s) considered:** isogeny classes of abelian varieties over F_2 of
  dimension 5 and 6 represented by real Weil polynomials (5c26f9); F_2-tori
  with a rational point of order 131 and the evaluation image of a
  translation-stable function space on a torsor fibre (6f2601); the
  presence/absence vector of small groups at seven toy primes (80209d).
- **Depth of verified structure:** derivation only, none machine-checked.
  Exact re-derivations in the records: the ceilings 2 a_g - 1 (6725, 39201)
  and multiple counts (51, 299); Phi_130(2) by the Moebius product with the
  2^65 + 1 cross-check and its 131-adic valuation 1; the achievable surface
  point counts {1..16, 19, 20, 25}; the seven torus orders; Lemma L's
  three-line proof from the torsor relation and 9abf42 part C. Retrieved this
  session: LMFDB class counts 1645 (g = 4), 14325 (g = 5), 164937 (g = 6) and
  the completeness statement at dimension <= 6 over GF(2); consequently
  census.json's numerical count 1624 at g = 4 is 21 short, so the numerical
  enumerator's gap grows with g (4 at g = 3, 21 at g = 4), which is recorded
  in 5c26f9 as the reason the exact pruning is mandatory.
- **dominated_by:** "n/a (no result claimed)" on all three; each is a
  certificate or fixture and competes with nothing on time, memory or queries.
  For 6f2601 the only surviving torus-derived set (an orbit union of an
  ordinary subspace) is already parameterised at zero extra cost by
  KN-FIND-47da4e, and the torus description is dominated by it on unknowns
  (17030 versus 131 per slot) at equal set.
- **sota_delta:** no attack; zero on time and memory. On data/queries: the
  first exact census past dimension 4 with a completeness control; the first
  exact statement routing every translation-stable Couveignes-Lercier base on
  any commutative group into the four-subspace count at n = 131; the first
  tabulation of group existence beside stable-subspace richness at toy primes.
- **Enumerated closures (with mechanism):** one, conditional on Lemma L's
  hypothesis matching Couveignes-Lercier's setting as GGMP relays it. At
  n = 131 over F_2 the torus row is closed for every translation-stable
  filtration (mechanism: ev_b(W) is a Frobenius-stable F_2-subspace, 9abf42
  leaves four, and the degree-1 image is exactly the trace-zero hyperplane
  with 2^130 elements, so there is no size control) and reduces, for
  non-stable filtrations, to the Frobenius orbit union of an ordinary subspace
  (mechanism: the Frobenius closure of ev_b(W) is the union of sigma^j
  ev_b(W)), an object the corpus already measures without any group. Forward
  guidance: the only shapes left on the seam are (i) orbit unions of
  subspaces, whose cost KN-FIND-47da4e measures cost-neutral at m = 2, toy
  tier, unverified, and (ii) section-ratio bases on abelian varieties, whose
  existence at dimension <= 6 is what 5c26f9 decides. The abelian-variety row
  is NOT closed by this lane; 5c26f9 says so and predicts no direction.
- **Open directions for the next session:** (1) run 5c26f9 and 80209d as one
  zero-run analysis artifact; (2) validator check of Lemma L against its toy
  instance at n = 17 (6f2601 minimal test); (3) read Couveignes-Lercier
  (still not done; the scope obligation in 6f2601 depends on it); (4) on a
  5c26f9 hit, the Jacobian-or-not step and then the section-ratio shape's
  degree, which is where GGMP table 3's 280x row becomes the relevant
  baseline.

### Novelty greps and retrievals (second attempt)

`genus 5|genus 6|dimension 5|dimension 6|Phi_130|cyclotomic torus|norm-one
torus|torus-based|T_130|translation-stable|orbit union of a subspace|
evaluation image` over ledger/, knowledge/, analysis/ (54 files; no filed
proposal on the seam; hits are KN-OPEN-095df5, the briefs, one review, MLKEM
evidence and lattice records). `primitive root|ord_n(2)|rich versus poor` in
ledger/proposals (22 files; nearest IDEA-20260918-9abf42, IDEA-20260915-8fe0ef,
IDEA-20260926-9c5694). The first attempt's greps were reused as recorded
above. Frontier rows read: KR-IC-b0fcda, KR-IC-73db3f, and for positioning
KR-IC-a4dd54, KR-IC-49c882, KR-IC-5ea2f8, KR-IC-f5c584, KR-IC-1fcdbc. Web:
three LMFDB search pages (q = 2, g = 4, 5, 6) fetched for class counts only;
the point-count column was not read reliably and is not relied on. All three
records carry `novelty_status: unverified`.

### Files written by this lane (second attempt)

- `ledger/proposals/IDEA-20260926-5c26f9.yaml`
- `ledger/proposals/IDEA-20260926-6f2601.yaml`
- `ledger/proposals/IDEA-20260926-80209d.yaml`
- this report (appended; the first attempt's text above is unchanged)

No existing record was edited. No run was made. No status changed. No file
outside the declared write scope was written.
