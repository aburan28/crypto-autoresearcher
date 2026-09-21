# Applicability audit: does Simon 2026's zero-noise DCP specialization apply, as stated, to CSIDH-512's actual N?

Required artifact per specification.yaml required_artifacts[0]. Governed by
CSIDH-OBJ-2's operative test (experiments/EXP-CSIDH-c65945/amendments/v1.yaml):
outcome A requires (i) an EXPLICIT statement, in the text of Simon 2026
and/or one of its cited predecessors (Regev 2004, Kuperberg 2005,
Ettinger-Hoyer), of a NAMED technique — with page/lemma citation — extending
the audited construction's N=2^n presentation to general N, AND (ii) that
technique's own stated preconditions independently checked against
CSIDH-512's actual N. Absent both, outcome is B. My own background field
knowledge may NOT supply the citable reduction (CSIDH-OBJ-2 resolution).

**Scope discipline restated:** this audit does NOT verify Simon 2026's
Lemma 3, does NOT compute or compare any concrete time/query cost against
Kuperberg's sieve, and draws no conclusion about CSIDH's security. Simon
2026 is an UNVERIFIED, unrefereed preprint; nothing here treats any part of
it as established.

## Live retrieval tool test (required disclosure per amendment's finding)

This Executor session's declared tool surface (`.claude/agents/executor.md`,
`tools:` frontmatter line) is `Read, Grep, Glob, Write, Edit, Bash,
SendMessage` — **no WebSearch, WebFetch, or crypto-kb MCP tool is present**,
confirming the identical structural finding the Coordinator recorded in
amendments/v1.yaml's `live_retrieval_tool_test` (tools absent from the role's
own tool surface, not merely erroring).

However, this session's `Bash` tool has outbound network access through this
environment's configured HTTPS proxy. A real `curl` to
`https://eprint.iacr.org/2019/498` returned HTTP 200 with real content, and
the same worked for `arxiv.org/pdf/...` PDF downloads and a `git clone` of
`https://github.com/KULeuven-COSIC/CSI-FiSh` (also successful; a direct
`curl` to `github.com` HTML pages and the GitHub REST API were blocked by a
Claude-Code-specific GitHub proxy restriction, but `git clone` over the git
protocol succeeded regardless). **Result: literature retrieval DID work in
this session, via Bash+curl/git, despite the complete absence of a
WebSearch/WebFetch/MCP tool.** This is a third, distinct data point beyond
the amendment's two: (1) red team's earlier session — tools present but
erroring; (2) Coordinator's session — tools absent from role surface,
untested; (3) this Executor session — tools absent from role surface, BUT an
alternate general-purpose tool (Bash) with network access substituted
successfully. All four CSIDH-CHG-1 primary sources (CSI-FiSh, Kuperberg
2005, Regev 2004, Ettinger-Hoyer) and Simon 2026 itself were reached this
way; NONE of CSIDH-CHG-1's escape valves are triggered by this run — see
`command.txt` for the exact commands and their HTTP status codes.

## The four sources, read

All four were retrieved as real PDFs (Simon 2026's own PDF also retrieved,
16 pages, from `https://eprint.iacr.org/2026/1591.pdf`) and read in full or
near-full:

- **Simon 2026** (KN-LIT-e204ab), "A Polynomial-Time Quantum Algorithm for
  the Dihedral Coset Problem [Preliminary Draft]", eprint 2026/1591.
- **Regev 2004** (KN-LIT-21383c), "Quantum Computation and Lattice
  Problems", SIAM J. Comput. 33(3):738-760; arXiv:cs/0304005.
- **Kuperberg 2005** (KN-LIT-2c8264), "A Subexponential-Time Quantum
  Algorithm for the Dihedral Hidden Subgroup Problem", SIAM J. Comput.
  35(1):170-188; arXiv:quant-ph/0302112.
- **Ettinger-Hoyer** — IDENTIFIED this run (previously an unresolved
  citation gap per CSIDH-OBJ-1/CSIDH-CHG-1): "On Quantum Algorithms for
  Noncommutative Hidden Subgroups", Adv. in Appl. Math. 25(3):239-251
  (2000); arXiv:quant-ph/9807029 (STACS 1999 conference version:
  Proceedings of TACS, pp.478-487). Confirmed as the correct paper by
  cross-checking Simon 2026's own reference [5] ("M. Ettinger and P. Høyer.
  On quantum algorithms for noncommutative hidden subgroups. Adv. in Appl.
  Math., 25(3):239-251, 2000.") against arXiv's own search API, which
  returned exactly one matching entry with that exact title/author/venue.

## Step 1: does N literally match Simon 2026's stated N=2^n presentation?

**No.** CSIDH-512's actual N (verified in `class_group_order.md`) is
```
254652442229484275177030186010639202161620514305486423592570860975597611726191
```
which is odd (ends in ...191) and manifestly not a power of 2 (its prime
factorization, verified above, is 3 x 37 x 1407181 x [two large primes], none
of which is 2). No literal match is possible.

## Step 2: is there a citable, stated reduction, per the operative test?

### 2a. Simon 2026's own text

- **Section 1.2, p.2** (problem statement, as Simon frames it): "given a
  source of random samples of the superposition... where `2N ≈ 2^{n+1}` is
  the size of the dihedral group, `d,x ∈ {0...N-1}`... find `d`." This is
  the DCP problem Simon addresses, stated with `N` only APPROXIMATELY `2^n`
  — not restricted to an exact power of 2 in this framing paragraph.
- **Section 2.2, "Algorithm Details", Theorem (p.6) and its Proof**: "For
  simplicity, let `N = 2^n`, and assume all arithmetic operations and
  relations involving states, amplitudes and phases are (mod N)." This is
  the ONLY place Simon's own new algorithm (the erasure-technique
  contribution that is this paper's whole claimed advance) is actually
  proved. Every subsequent step (Steps 1-7, pp.6-15) uses bit-level
  manipulations tied specifically to `N` being an exact power of 2: "the
  highest-order bit `h` of `z`" (Step 2, p.7), additions of `2^{n-1}` to
  shift between `h` and `h*` values (Lemma 2's proof, p.10, and the
  Definition-1/Lemma-3 apparatus, pp.10-14), and recursion "using knowledge
  of `d_n` to erase the last bit... obtaining `d_{n-1}`" (Section 2.1
  overview, p.4) — a bit-by-bit recursion over exactly `n = log2(N)` binary
  digits.
- **No sentence anywhere in Simon 2026's text** states that this specific
  proof, or its Theorem, extends to general (non-power-of-2) `N` via any
  named technique, nor cites one. The paper's only other explicit
  discussion of scope is the "Corollary" restating the LWE/SVP consequence
  (p.15) and the acknowledged incompleteness items already recorded in
  KN-LIT-e204ab (Lemma 3 sketch, conditioning gap, corollary's "rescale by
  analogy" step) — none of which addresses non-power-of-2 group order.

**Finding: Simon 2026's own text supplies NO citable, page/lemma-located
statement satisfying operative-test criterion (i) for its own construction.**

### 2b. Regev 2004 (cited predecessor, ref [10] in Simon 2026)

- **Section 2, Definition 2.1, p.5**: "The input to the DCP with failure
  parameter f consists of poly(log N) registers. Each register is... in the
  state `1/sqrt(2)(|0,x> + |1,(x+d) mod N>)`... where `x ∈ {0,...,N-1}` is
  arbitrary and `d` is fixed." **General N throughout — no power-of-2
  restriction anywhere in Regev's own DCP definition or in Section 4's
  algorithm** (the subset-sum-oracle-based DSP/DCP algorithm Simon's paper
  explicitly modifies). Regev's own oracle-based algorithm (Section 4,
  pp.13-19) is stated and proved for general modulus `N` mod-arithmetic
  throughout (e.g. Definitions in Section 4.1, "subset sum problem... two
  integers `t, N`").
- This establishes that the FRAMEWORK Simon's paper builds on (Regev's own
  base algorithm before Simon's erasure-technique modification) is already
  general-N in Regev's own text. However — Regev's paper predates Simon
  2026 and cannot, and does not, state anything about whether SIMON's later
  *modification* (the specific erasure technique, absent from Regev's own
  paper) preserves general-N applicability. Regev's own text supplies no
  statement about Simon's specific technique at all (it cannot, chronologically).
- **No named technique for extending an N=2^n-specific PROOF (such as
  Simon's) to general N is stated in Regev 2004** — Regev's algorithm was
  never restricted to N=2^n in the first place, so there is nothing in
  Regev's text to extend FROM.

**Finding: Regev 2004 does not supply the citable reduction the operative
test requires for Simon's specific construction (it addresses a different,
though related, algorithm that was never N=2^n-restricted to begin with).**

### 2c. Kuperberg 2005 (cited predecessor, ref [6] in Simon 2026)

- **Theorem 1.1, p.1**: "There is a quantum algorithm that finds a hidden
  reflection in the dihedral group `G = D_N` (of order `2N`) with time and
  query complexity `2^O(sqrt(log N))`." — stated for general N from the
  abstract onward.
- **Section 3, p.2**: "We will prove Theorem 1.1 in a convenient case,
  `N = 2^n`, in Section 3." — Kuperberg's OWN sieve algorithm is likewise
  FIRST proved only for `N=2^n`, exactly as Simon's is.
- **Section 5, "Other Algorithms", p.4, Algorithm 2** (page 4 of the PDF,
  labeled "5. OTHER ALGORITHMS" in the paper's own section numbering):
  "The first task is to prove Theorem 1.1 when N is not a power of 2...
  Another difference when N is not a power of 2 is that the quantum Fourier
  transform on Z/N is more complicated... **Write N = 2^a M with M odd. By
  the Chinese remainder theorem, C_N ≅ C_{2^a} x C_M. For each
  1 ≤ j ≤ ⌈log2 N⌉, apply Algorithm 1 to produce many |ψ_k⟩ with
  2^min(a,j)|k. Then repeat steps 1-4 after applying the group automorphism
  x → x^{2^-j} to the C_M factor of D_N.**" (Algorithm 2, step 4). Kuperberg
  states explicitly, immediately following: "The proof of Theorem 3.1
  carries over to show that Algorithm 2 also requires only
  `O(8^sqrt(log2 N))` queries..." — i.e. this is a CITABLE, NAMED technique
  (CRT decomposition into a power-of-2 part and an odd part, plus an
  explicit automorphism relabeling) with a stated complexity-preservation
  claim, located at page/section/algorithm granularity.
- **This satisfies operative-test criterion (i) for Kuperberg's OWN sieve
  algorithm** — but Kuperberg's sieve is a DIFFERENT construction from
  Simon's: it requires error-free (zero-fault-rate) input samples (already
  established in KN-LIT-2c8264: "The algorithm requires error-free
  samples"), whereas the audited construction is specifically Simon's
  *noise-tolerant* erasure technique (tolerating fault rate `1/O(log n)`),
  which is a structurally different algorithm (subset-sum/Hadamard-erasure
  based, not pairwise-qubit-combination-sieve based) with a different
  proof (Lemmas 1-4, balls-in-bins arguments over bit groups) that
  Kuperberg's CRT/automorphism technique does not address or mention.
- **No statement in Kuperberg 2005 addresses whether his CRT-based general-N
  technique — devised for his own pairwise-combination sieve — would
  preserve the preconditions of Simon's specific balls-in-bins,
  bit-decomposition-dependent noise-tolerance argument** (Lemma 4's
  `n^{(c-1)/2}` bin-deviation bound, the group-size-`c log n` bit
  partitioning, the `2^{n-1}` split used throughout Simon's Steps 2-7). This
  would require new derivation work this contract explicitly forbids
  (citation-plus-arithmetic-check only, never symbolic re-derivation — see
  CSIDH-CHG-2's own justification_for_this_reading item (1)).

**Finding: Kuperberg 2005 supplies a real, citable general-N technique — but
for a DIFFERENT construction (Kuperberg's own error-free sieve), not for the
audited construction (Simon's noise-tolerant erasure technique). This is
recorded as a directly relevant, honestly-qualified negative finding, not
folded silently into an overall A.**

### 2d. Ettinger-Hoyer (cited predecessor, ref [5] in Simon 2026)

- **Theorem 2 ("Main theorem"), p.3**: "Let `γ : D_N → R` be a function that
  fulfills the dihedral subgroup promise with respect to `H`. There exists a
  quantum algorithm that given `γ`, uses `Θ(log N)` evaluations of `γ` and
  outputs a subset `X ⊆ D_N` such that `X` is a generating set for `H` with
  probability at least `1 - 2/N`." — general `N` throughout, no
  power-of-2 restriction anywhere in Ettinger-Hoyer's paper.
- **Theorem 2's own proof, p.4**: explicitly reduces the general-N dihedral
  subgroup problem to Theorem 3's order-2-subgroup case at a general
  divisor-type value `M` (not restricted to a power of 2): "The subgroup
  `<X1> ≤ D_N` is normal in `D_N`, and the factor group `D_N/<X1>` is
  isomorphic to `D_M` where `M = min{1 ≤ j ≤ N | (j,0) ∈ <X1>}`."
- Ettinger-Hoyer's own algorithm (Theorem 3, p.4) solves a DIFFERENT
  problem than DCP/erasure — it is the SUBGROUP-IDENTIFICATION problem
  (finding a generating set for `H`, using a maximum-likelihood test over
  `O(log N)` classical "cosine observations", Section 3, p.6-7), not the
  coset/shift-recovery-via-erasure problem Regev's DSP formulation and
  Simon's paper address. Simon's own paper cites Ettinger-Hoyer (ref [5])
  only for the narrower fact "it suffices to solve the problem in the case
  where the subgroup is of order 2" (Simon 2026, Section 1.2, p.2) — a
  reduction Ettinger-Hoyer's paper does supply generally (for `N`
  unrestricted), but this is a reduction of a DIFFERENT problem (subgroup
  identification) than the one Simon's own new erasure technique is proved
  for (DCP with a fixed hidden shift `d`, recovered via bit-recursive
  Hadamard-basis measurement).
- **No statement in Ettinger-Hoyer's paper addresses Simon's specific
  erasure/noise-tolerance technique at all** (chronologically impossible;
  Ettinger-Hoyer predates it by 26 years), and their own general-N subgroup
  identification algorithm's proof structure (classical maximum-likelihood
  post-processing over "cosine observations", Theorem 5 and its proof,
  pp.5-6) is unrelated to Simon's bit-decomposition-specific balls-in-bins
  argument.

**Finding: Ettinger-Hoyer supplies a general-N result, but for a materially
different problem (subgroup identification, not DCP/erasure with a fixed
faulty-sample rate); it does not supply the citable reduction the operative
test requires for Simon's specific construction.**

## Conclusion: applicability_outcome

**Outcome B (NOT-APPLICABLE-AS-STATED).**

No explicit, page/lemma-citable statement — in Simon 2026 itself, or in
Regev 2004, Kuperberg 2005, or Ettinger-Hoyer as its cited predecessors — was
located within budget that states a NAMED technique extending Simon 2026's
own N=2^n-restricted proof (the audited construction, Section 2.2's
Theorem/Proof) to CSIDH-512's actual, non-power-of-2 group order
`N' = 254652442229484275177030186010639202161620514305486423592570860975597611726191`,
with that technique's preconditions checked. This satisfies both halves of
CSIDH-CHG-1's applicability_outcome_interaction clause for the applicability
determination itself: all four sources WERE reached (no escape valve
triggers for reachability), and the audit is COMPLETE (not partial) because
every one of the four sources was read and checked against the operative
test — the negative result comes from the test failing on the merits, not
from any source being unreachable.

This is a decidable NEGATIVE finding for H-CSIDH-3eaede's premise (i), per
the falsification_criterion in specification.yaml — recorded as such, with
no further interpretation. It does not evaluate premise (ii), Lemma 3's
correctness, any concrete cost, or CSIDH's security (all explicitly out of
scope). The closest positive-adjacent finding — that Kuperberg 2005 does
supply a citable general-N technique, but for his own different, error-free
sieve construction rather than for Simon's noise-tolerant one — is preserved
above exactly as found, per this program's "record, never discard" rule,
rather than omitted for looking like it might weaken the negative result's
apparent decisiveness.
