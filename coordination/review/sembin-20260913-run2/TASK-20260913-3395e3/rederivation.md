# Blind re-derivation — joint J6-BLIND

- task: `TASK-20260913-3395e3`
- review round: `REVIEW-SEMBIN-20260913-run2`
- role: validator (blind re-deriver). Policy requested: `review-adversarial`.
- review plan: `coordination/review/sembin-20260913-run2/review-plan.yaml` — **not opened**. The statement of the quantity below was transcribed into my task card by the Coordinator; I worked from that transcription and from the frozen Semaev text only.
- `blind_from` respected: **yes**. No path under `experiments/EXP-SEMBIN-354a75/`, no sibling task directory, no `coordination/bus/`, no `ledger/evidence|decisions|corrections|handoffs`, no `coordination/goals/`, no `knowledge/`, no git command, and no repository-wide search was used. The complete list of repository paths opened is in `attestation.yaml` (`sources_read`) and repeated in §7.
- Verdict type: **filed**. A re-derivation files a value; it holds or breaks nothing. I do not know the producer's value and have not tried to infer it.

## 1. The quantity, as received

> Let V be a k-dimensional F_2-subspace of F_{2^n} used as the x-coordinate set of a factor base on E: y^2 + xy = x^3 + B over F_{2^n}. Let L be the number of F_{2^n}-rational points of E whose x-coordinate lies in V. Consider a model in which eq. (11) predicts the mean number of t-element decompositions of a target by charging |V| available x-values, while only L of them carry a rational point.
> DERIVE the exact multiplicative factor by which that substitution misstates the predicted mean, as a closed form in L, |V| and t; then EVALUATE it at t = 2 for k = 10, 11, 12 (so |V| = 1024, 2048, 4096) at n = 20, 22, 24 respectively, with B = 1 and A = 0, computing L yourself.

Curve: y^2 + xy = x^3 + A x^2 + B with A = 0, B = 1.

## 2. Eq. (11) as read from the frozen text

Source: `inputs/SEMAEV-2015-310/paper_fulltext.md`, Section 4.3 "Success probability", lines 394–431. Verbatim (extractor line breaks collapsed; the equation number is the paper's):

> We estimate the probability that S_{t+1}(x_1, …, x_t, R_X) = 0, x_1, …, x_t ∈ V, where 2 ≤ t ≤ m, is satisfiable. We adopt the following model. For random z the mapping x_1, …, x_t → S_{t+1}(x_1, …, x_t, z) is a symmetric random mapping from V^t to F_q. Let K be the number of classes of tuples (x_1, …, x_t) under permuting the entries. Then K ≈ |V|^t / t!. The probability of a solution is the probability P(q, m, t, |V|) that the mapping hits 0 ∈ F_q at least once. So
>
> P(q, m, t, |V|) = 1 − (1 − 1/q)^K ≈ 1 − (1 − 1/q)^{|V|^t/t!} ≈ 1 − e^{−|V|^t/(q·t!)}   (11)
>
> If |V|^t/(q·t!) = o(1), then P(q, m, t, |V|) ≈ |V|^t/(q·t!) as in [3, 19].

(lines 396–405 for the model and K; 407–417 for the displayed equation, whose exponent fragments `|V|t`, `t!`, `q t!` are split across lines 409–419 by the PDF extractor; 419–427 for the o(1) form.)

Transcription check. I evaluated 1 − exp(−2^{kt}/(2^n t!)) for the nine (n, m, t, k) rows of Table 1 (lines 639–750) and compared with the printed `P(n,m,t,k)` column: all nine agree to the printed four digits (the paper truncates rather than rounds, e.g. 0.28347 → 0.2834, 0.07996 → 0.0799). Output in Appendix C3. So the formula above is the one the paper's own tables were computed from.

The factor base. Section 4.5, lines 538–546:

> Let f(x) be an irreducible polynomial of degree n over F_2 and α its root in F_{2^n}. Then 1, α, …, α^{n−1} is a basis of F_{2^n} over F_2. Elements of F_{2^n} are represented as polynomials in α of degree at most n − 1. Let V be a set of all polynomials in α of degree < k = ⌈n/m⌉. Obviously, that is a vector space over F_2 of dimension k. Following [3], one can define V as any subspace of F_{2^n} of dimension k. However it seems that using the subspace of low degree polynomials significantly reduces the time and space complexity in comparison with a randomly generated subspace and is therefore preferable.

and the Table 1 footnote, lines 1043–1052: "The line with 6* means a random subspace of dimension 6 in F_{2^17} was used … Otherwise a subspace of all degree < 6 polynomials modulo f(X) was used. We realise the latter is preferable." So the paper's own V is the low-degree subspace **relative to a chosen modulus f**, and it also reports a random-subspace variant. Both are evaluated below.

## 3. Derivation of the closed form

### 3.1 The mean implied by eq. (11)

Eq. (11) is a probability; the *mean* the statement refers to is the quantity that probability is built from. In the model of lines 400–405, K permutation-classes of t-tuples are each mapped to 0 ∈ F_q independently with probability 1/q, so the number of classes hitting 0 is Binomial(K, 1/q), with mean

  μ = K/q,  K ≈ M^t / t!,

where M is the number of x-values charged as available (the paper writes M = |V|). Hence

  μ(M) = M^t / (q · t!).                                         (D1)

(1 − (1 − 1/q)^K is P[≥1 hit]; 1 − e^{−μ} is its Poisson form; μ is the mean. For the three cells below, μ(|V|) = 2^{2k}/(2^n · 2) = 1/2 exactly, since k = n/2 and t = 2.)

### 3.2 The substitution and the factor

The statement's model charges M = |V| available x-values when only L of them are "available" in the sense of carrying a rational point. Everything in (D1) other than M — q, t, t!, the 1/q hit probability, the independence and the permutation symmetry — is untouched by the substitution. Therefore the misstatement is exactly

  Φ(L, |V|, t) := μ(|V|) / μ(L) = (|V|/L)^t.                          (D2)

Equivalently, the correction multiplier that converts eq. (11)'s mean into the L-model mean is its reciprocal,

  μ(L) = (L/|V|)^t · μ(|V|).                                       (D2′)

Properties: q and t! cancel, so Φ depends on neither the field size nor the tuple-symmetry normalisation; t enters **only through the exponent** — Φ is the t-th power of the per-slot ratio |V|/L, because K is a t-fold product over t independently drawn entries from the same pool, and the substitution changes the pool size in every slot identically. At t = 2, Φ = |V|^2/L^2, a rational number, evaluated exactly below.

### 3.3 Assumptions the derivation needs

- **A1 (mean = K/q).** The "predicted mean number of t-element decompositions" is the expected number of permutation-classes mapped to 0, K/q, with K ≈ M^t/t! as eq. (11) writes it; each class hits 0 independently with probability 1/q.
- **A2 (only the pool size changes).** The substitution |V| → L changes only M. In particular the codomain stays F_q of size q = 2^n (the summation polynomial's value set), not E(F_q) of size N = #E(F_{2^n}). If one also moved the codomain to E(F_q), an extra factor N/q would appear; N/q is reported per cell (§4.6) and is **not** folded into Φ.
- **A3 (independence and symmetry).** The t entries are drawn independently from one pool and the map is symmetric under permutation, as in the source model; the t! is common to both sides.
- **A4 (eq. (11)'s own approximation).** K ≈ M^t/t! is used on both sides, so Φ is exact *relative to eq. (11)'s model*. Using exact class counts at t = 2 instead gives C(|V|,2)/C(L,2) (distinct entries) or C(|V|+1,2)/C(L+1,2) (multisets). Both variants are reported; at these sizes they differ from (|V|/L)^2 only in the 5th significant figure.
- **A5 (exact L).** L is computed by exact point counting, not approximated by |V|/2 or |V|.
- **A6 (target).** The target enters eq. (11) only through a random z ∈ F_q standing in for R_X; Φ does not depend on it.

### 3.4 What "L" counts — the statement is internally inconsistent here (finding U1)

The statement's first sentence defines L as the number of rational **points** with x ∈ V. Its second sentence says "only L **of them** carry a rational point", where "them" is the |V| x-values — a count of **x-values**. These are different numbers, related exactly as follows for this curve:

- For x ≠ 0, substituting y = xw turns y^2 + xy = x^3 + B into w^2 + w = x + B/x^2 (A = 0). This has a solution in F_{2^n} iff Tr(x + B/x^2) = 0, and then exactly two: w and w + 1, i.e. y and y + x, which are distinct because x ≠ 0. So a nonzero x carries 0 or 2 rational points.
- For x = 0 (always in a subspace), y^2 = B has the unique solution y = √B (squaring is a bijection in characteristic 2); with B = 1 that is the single point (0, 1), the curve's unique rational 2-torsion point.

Hence, writing L_pts for the point count and L_x for the count of x ∈ V carrying a point,

  L_pts = 2·L_x − 1.

Under the points reading, Φ = (|V|/L_pts)^t ≈ 1 (since L_pts ≈ |V|); under the x-values reading, Φ = (|V|/L_x)^t ≈ 2^t = 4 at t = 2. The statement, as transcribed, does not let me choose between them, so **both are evaluated and reported**. In the tables and in `rederived-values.json`, `L` and `factor` follow the explicit definition (points); `L_alt_xvalues` and `factor_alt_xvalues` follow the "of them" reading. I have not resolved this by reading any forbidden source; it is reported as an underdetermination.

Model note (my own analysis, clearly separate from the asked derivation and asserting nothing about anyone's result): eq. (11)'s |V| is numerically close to L_pts and close to 2·L_x. A decomposition into t rational factor-base points has 2^{t−1} sign patterns per unordered x-tuple (mod global negation), which is where a 2^t-type gap between an x-value model and a point model lives; and eq. (11) counts zeros of S_{t+1} over **all** of V, whose non-rational x-values contribute the "twisted" relations of Lemma 2 (lines 289–300) rather than rational decompositions. Which of these the review plan intends is exactly what the wording leaves open.

## 4. Evaluation

### 4.1 Field construction (all built from scratch, Appendix A)

- Polynomials over F_2 are Python integers, bit i ↔ coefficient of x^i. Elements of F_{2^n} = F_2[α]/(f) are represented in the polynomial basis 1, α, …, α^{n−1}, so "polynomial in α of degree < k" ↔ integer < 2^k.
- Irreducibility: Ben-Or's test (gcd(x^{2^i} − x, f) = 1 for i = 1..⌊n/2⌋), implemented with my own polynomial division and gcd.
- Modulus choice: the **smallest irreducible polynomial of degree n by integer value** (i.e. lexicographically smallest coefficient vector), recorded per cell. The next two smallest were also used, to expose the dependence of the low-degree subspace on f.
- Log/antilog tables over a generator g (g = α = `0x2` turned out to be primitive for all three primary moduli; the table build asserts that g^i, 0 ≤ i < 2^n − 1, enumerates every nonzero element exactly once, which is itself a check of the multiplication). Inversion and squaring for the vectorised passes go through the tables; every scalar re-check uses independent shift-and-reduce multiplication and extended-Euclid inversion.
- Trace: Tr(a) = Σ_{j<n} a^{2^j} by scalar squaring; the vectorised trace uses the linear-functional mask bit i = Tr(α^i) and was checked against the scalar trace on 2000 random elements per field, together with a·a^{−1} = 1, commutativity, associativity, and Tr(a + b) = Tr(a) + Tr(b).

### 4.2 Point counting over x ∈ V

For each x ∈ V \ {0}: c = x + (x^{−1})^2; if Tr(c) = 0, a root w of w^2 + w = c is read from a whole-field table of the map w ↦ w^2 + w (its image was asserted to have exactly 2^{n−1} elements, the trace-zero hyperplane), and **both** points (x, xw), (x, xw + x) are constructed and verified to satisfy y^2 + xy = x^3 + 1 with scalar arithmetic; if Tr(c) = 1, the scalar trace is recomputed independently and asserted to be 1. For x = 0: (0, 1) is verified on the curve and counted once. Then L_x = 1 + #{x ≠ 0 with a point}, L_pts = 2·L_x − 1, and the code asserts this identity.

### 4.3 Verification chain (all in Appendix C)

1. **Small n, three ways.** For n = 6, 8, 10: brute force over all (x, y) ∈ F_{2^n}^2, the trace-criterion count, and the closed-form Koblitz order all agree (#E = 56, 288, 968), and brute force finds exactly one point at x = 0.
2. **Full field at the working sizes.** The trace-criterion count summed over all x ∈ F_{2^n} equals the closed-form order #E(F_{2^n}) = 2^n + 1 − s_n (s_0 = 2, s_1 = −1, s_{j+1} = −s_j − 2 s_{j−1}, from #E(F_2) = 4): 1,047,376 at n = 20; 4,193,912 at n = 22; 16,783,200 at n = 24 — exact matches, for the primary modulus **and** both alternative moduli at every n. This validates modulus, multiplication, inversion, squaring, trace and root table end to end.
3. **Independent brute force over all y (Appendix B).** For the n = 20 and n = 22 low-degree cells, every y ∈ F_{2^n} was tried for every x ∈ V using only field multiplication and squaring — no trace, no root table. Result: n = 20: L_pts = 977, L_x = 489, histogram {1 y: 1 x, 2 y: 488 x, 0 y: 535 x}; n = 22: L_pts = 2051, L_x = 1026, histogram {1: 1, 2: 1025, 0: 1022}. Identical to §4.5. (n = 24 skipped: 4096 × 2^24 evaluations.)

### 4.4 Subspaces used

- **(a) low-degree** — V = {polynomials in α of degree < k} = {0, 1, …, 2^k − 1} in the polynomial basis of the primary modulus (Semaev's choice, lines 540–541). Also evaluated in the polynomial bases of the next two smallest irreducible moduli (a′).
- **(b) random** — k vectors from `random.Random(seed).getrandbits(n)`, redrawn until F_2-rank k, span enumerated (asserted to have 2^k distinct elements). Primary seed 20260913; seeds 1, 2, 3 added to show the spread. Bases are recorded in `rederived-values.json` (`subspace_basis_hex`).

### 4.5 Results

Φ_pts = (|V|/L_pts)^2, Φ_x = (|V|/L_x)^2; reciprocals are the correction multipliers (L/|V|)^2. Exact fractions are in lowest terms; floats are IEEE doubles printed to 15 significant digits.

| n | k | \|V\| | subspace | modulus f | L_pts (= L, explicit def.) | L_x ("of them") | Φ_pts = (\|V\|/L_pts)^2 | (L_pts/\|V\|)^2 | Φ_x = (\|V\|/L_x)^2 | (L_x/\|V\|)^2 | primary |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 10 | 1024 | low-degree | `0x100009` = x^20 + x^3 + 1 | 977 | 489 | 1048576/954529 = 1.09852712699143 | 0.910309791564941 | 1048576/239121 = 4.38512719501842 | 0.228043556213379 | yes |
| 20 | 10 | 1024 | low-degree (alt. f) | `0x10000f` = x^20 + x^3 + x^2 + x + 1 | 1035 | 518 | 1048576/1071225 = 0.978856916147401 | 1.02159976959229 | 262144/67081 = 3.90787257196524 | 0.255893707275391 |  |
| 20 | 10 | 1024 | low-degree (alt. f) | `0x100017` = x^20 + x^4 + x^2 + x + 1 | 1075 | 538 | 1048576/1155625 = 0.907367009194159 | 1.10208988189697 | 262144/72361 = 3.62272494852199 | 0.276035308837891 |  |
| 20 | 10 | 1024 | random seed 20260913 | `0x100009` = x^20 + x^3 + 1 | 1013 | 507 | 1048576/1026169 = 1.02183558458694 | 0.978631019592285 | 1048576/257049 = 4.07928449439601 | 0.24514102935791 | yes |
| 20 | 10 | 1024 | random seed 1 | `0x100009` | 1047 | 524 | 1048576/1096209 = 0.956547519679185 | 1.04542636871338 | 65536/17161 = 3.81889167297943 | 0.261856079101562 |  |
| 20 | 10 | 1024 | random seed 2 | `0x100009` | 991 | 496 | 1048576/982081 = 1.0677082643896 | 0.936585426330566 | 4096/961 = 4.26222684703434 | 0.234619140625 |  |
| 20 | 10 | 1024 | random seed 3 | `0x100009` | 1049 | 525 | 1048576/1100401 = 0.952903532439538 | 1.04942417144775 | 1048576/275625 = 3.80435736961451 | 0.262856483459473 |  |
| 22 | 11 | 2048 | low-degree | `0x400003` = x^22 + x + 1 | 2051 | 1026 | 4194304/4206601 = 0.997076737251762 | 1.00293183326721 | 1048576/263169 = 3.98442065744826 | 0.250977516174316 | yes |
| 22 | 11 | 2048 | low-degree (alt. f) | `0x400027` = x^22 + x^5 + x^2 + x + 1 | 2067 | 1034 | 4194304/4272489 = 0.981700362481916 | 1.01864075660706 | 1048576/267289 = 3.92300468780982 | 0.25490665435791 |  |
| 22 | 11 | 2048 | low-degree (alt. f) | `0x40002b` = x^22 + x^5 + x^3 + x + 1 | 2053 | 1027 | 4194304/4214809 = 0.995135010862888 | 1.00488877296448 | 4194304/1054729 = 3.97666509596304 | 0.251466989517212 |  |
| 22 | 11 | 2048 | random seed 20260913 | `0x400003` = x^22 + x + 1 | 2051 | 1026 | 4194304/4206601 = 0.997076737251762 | 1.00293183326721 | 1048576/263169 = 3.98442065744826 | 0.250977516174316 | yes |
| 22 | 11 | 2048 | random seed 1 | `0x400003` | 2105 | 1053 | 4194304/4431025 = 0.946576469327074 | 1.0564386844635 | 4194304/1108809 = 3.78271099891866 | 0.264360666275024 |  |
| 22 | 11 | 2048 | random seed 2 | `0x400003` | 2035 | 1018 | 4194304/4141225 = 1.01281722195727 | 0.987344980239868 | 1048576/259081 = 4.0472902296965 | 0.247078895568848 |  |
| 22 | 11 | 2048 | random seed 3 | `0x400003` | 2019 | 1010 | 4194304/4076361 = 1.02893340408271 | 0.971880197525024 | 1048576/255025 = 4.11165964121165 | 0.243210792541504 |  |
| 24 | 12 | 4096 | low-degree | `0x100001b` = x^24 + x^4 + x^3 + x + 1 | 4047 | 2024 | 16777216/16378209 = 1.0243620654737 | 0.976217329502106 | 262144/64009 = 4.09542408098861 | 0.244174957275391 | yes |
| 24 | 12 | 4096 | low-degree (alt. f) | `0x100006f` = x^24 + x^6 + x^5 + x^3 + x^2 + x + 1 | 4113 | 2057 | 16777216/16916769 = 0.99175061147906 | 1.00831800699234 | 16777216/4231249 = 3.96507414241043 | 0.252202093601227 |  |
| 24 | 12 | 4096 | low-degree (alt. f) | `0x1000087` = x^24 + x^7 + x^2 + x + 1 | 4135 | 2068 | 16777216/17098225 = 0.981225595054457 | 1.0191336274147 | 1048576/267289 = 3.92300468780982 | 0.25490665435791 |  |
| 24 | 12 | 4096 | random seed 20260913 | `0x100001b` = x^24 + x^4 + x^3 + x + 1 | 3993 | 1997 | 16777216/15944049 = 1.05225567232012 | 0.950339376926422 | 16777216/3988009 = 4.20691528028146 | 0.237703859806061 | yes |
| 24 | 12 | 4096 | random seed 1 | `0x100001b` | 4103 | 2052 | 16777216/16834609 = 0.996590773210117 | 1.00342088937759 | 1048576/263169 = 3.98442065744826 | 0.250977516174316 |  |
| 24 | 12 | 4096 | random seed 2 | `0x100001b` | 4081 | 2041 | 16777216/16654561 = 1.00736464923933 | 0.992689192295074 | 16777216/4165681 = 4.02748458175266 | 0.248293936252594 |  |
| 24 | 12 | 4096 | random seed 3 | `0x100001b` | 4013 | 2007 | 16777216/16104169 = 1.04179333935206 | 0.959883272647858 | 16777216/4028049 = 4.16509729648274 | 0.240090429782867 |  |

The six **primary** cells asked for, in one place:

| n | k | \|V\| | V | f | L_pts | L_x | Φ_pts = (\|V\|/L_pts)^2 | Φ_x = (\|V\|/L_x)^2 |
|---|---|---|---|---|---|---|---|---|
| 20 | 10 | 1024 | low-degree (deg < 10) | x^20 + x^3 + 1 | 977 | 489 | 1048576/954529 = 1.09852712699143 | 1048576/239121 = 4.38512719501842 |
| 22 | 11 | 2048 | low-degree (deg < 11) | x^22 + x + 1 | 2051 | 1026 | 4194304/4206601 = 0.997076737251762 | 1048576/263169 = 3.98442065744826 |
| 24 | 12 | 4096 | low-degree (deg < 12) | x^24 + x^4 + x^3 + x + 1 | 4047 | 2024 | 16777216/16378209 = 1.0243620654737 | 262144/64009 = 4.09542408098861 |
| 20 | 10 | 1024 | random, seed 20260913 | x^20 + x^3 + 1 | 1013 | 507 | 1048576/1026169 = 1.02183558458694 | 1048576/257049 = 4.07928449439601 |
| 22 | 11 | 2048 | random, seed 20260913 | x^22 + x + 1 | 2051 | 1026 | 4194304/4206601 = 0.997076737251762 | 1048576/263169 = 3.98442065744826 |
| 24 | 12 | 4096 | random, seed 20260913 | x^24 + x^4 + x^3 + x + 1 | 3993 | 1997 | 16777216/15944049 = 1.05225567232012 | 16777216/3988009 = 4.20691528028146 |

Note on the n = 22 rows: the low-degree subspace and the seed-20260913 random subspace happen to give the same counts (L_pts = 2051). I checked that they are different subspaces (2046 of the 2048 elements of the random span have degree ≥ 11); the equality is a coincidence of counts, of the kind expected when L_x fluctuates by O(√|V|) around |V|/2.

Means (exact), primary low-degree cells: μ(|V|) = 1/2 at every cell; μ(L_pts) = 954529/2097152 = 0.455154895782471 (n = 20), 4206601/8388608 = 0.501465916633606 (n = 22), 16378209/33554432 = 0.488108664751053 (n = 24); μ(L_x) = 239121/2097152 = 0.114021778106689, 263169/2097152 = 0.125488758087158, 64009/524288 = 0.122087478637695.

Exact-count variants (A4), primary low-degree cells, points reading: C(|V|,2)/C(L,2) = 65472/59597 = 1.09857878752286, 2096128/2102275 = 0.997076024782676, 399360/389861 = 1.02436509422589; C(|V|+1,2)/C(L+1,2) = 524800/477753 = 1.09847557210525, 349696/350721 = 0.997077449026434, 1048832/1023891 = 1.02435903821794. x-values reading: C(|V|,2)/C(L_x,2) = 43648/9943 = 4.3898219853163, 2096128/525825 = 3.98636048114867, 299520/73117 = 4.09644815843101; multisets 104960/23961 = 4.38045156712992, 699392/175617 = 3.98248461139867, 2097664/512325 = 4.09440101498073. All other cells: `rederived-values.json`.

### 4.6 Side values (not folded into Φ)

Curve orders and N/q, should the codomain be taken as E(F_q) instead of F_q (assumption A2): n = 20: N = 1,047,376, N/q = 0.9988555908203125; n = 22: N = 4,193,912, N/q = 0.9999065399169922; n = 24: N = 16,783,200, N/q = 1.000356674194336.

## 5. Internal consistency

Closed form and arithmetic agree: for every cell, the code computes Φ directly as `Fraction(V, L) ** t` from the counted L and independently reports μ(|V|) and μ(L) from (D1); their ratio equals Φ in every cell (it is the same rational number), and the L identity L_pts = 2·L_x − 1 held in all 21 cells. No disagreement to report.

## 6. Underdetermination in the statement (findings)

- **U1 — what L counts (material, factor ≈ 2^t between readings).** Explicit definition: rational points with x ∈ V (L_pts). Second sentence: x-values carrying a point (L_x). L_pts = 2·L_x − 1. Points reading → Φ ≈ 1 (0.997–1.099 across the six primary cells); x-values reading → Φ ≈ 4 (3.98–4.39). Both filed; `L`/`factor` follow the explicit definition, `L_alt_xvalues`/`factor_alt_xvalues` the other.
- **U2 — which V (material, ≈ ±10 % on Φ).** Not fixed. The low-degree V depends on the modulus (n = 20: L_pts = 977 / 1035 / 1075 across the three smallest irreducible f; Φ_pts = 1.099 / 0.979 / 0.907); random V varies with the seed (n = 20: 991–1049). A single "the factor at (n, k)" does not exist without naming f and V; the primary cells are the smallest-irreducible-modulus low-degree V and the seed-20260913 random V.
- **U3 — direction.** "Factor by which the substitution misstates" is filed as predicted/corrected = (|V|/L)^t; the reciprocal (L/|V|)^t is filed alongside.
- **U4 — "exact".** Exact relative to eq. (11)'s K ≈ |V|^t/t!; exact-count variants at t = 2 filed (they move the 5th significant figure).
- **U5 — boundary points.** The point at infinity has no x-coordinate and is excluded; (0, 1) has x = 0 ∈ V and is counted once. Stated so the Coordinator can see the convention rather than infer it.
- The statement does **not** leave the closed form itself underdetermined: given a reading of L, Φ = (|V|/L)^t follows from eq. (11) with no further choice.

## 7. Provenance and reproducibility

- Repository paths opened (complete): `AGENTS.md` (injected as workspace rules), `agents/validator.md`, `templates/research-records.md` (lines 560–703 and a keyword search within that single file), `inputs/SEMAEV-2015-310/paper_fulltext.md` (whole file), and a directory listing of `inputs/SEMAEV-2015-310/`. Nothing else in the repository was opened, listed, or searched. `ledger/hypotheses/` and `knowledge/` were in my read scope but were not opened.
- Scratch work was done in `/tmp/j6blind/` (outside the repository): `rederive.py`, `bruteforce_check.py`, their outputs, and `results.json` from which `rederived-values.json` was generated programmatically. No repository path outside `coordination/review/sembin-20260913-run2/TASK-20260913-3395e3/` was written. No git command was run.
- Environment: Python 3.12.3, numpy 2.4.4, Linux, 4 cores; `rederive.py` ran in 21.7 s, `bruteforce_check.py` in 287 s. Seeds: scalar/vector consistency checks used `random.Random(12345 + n)`; random subspaces used seeds 20260913, 1, 2, 3 as recorded.
- To reproduce: save Appendix A as `rederive.py` and Appendix B as `bruteforce_check.py` in one directory; run `python3 rederive.py results.json` and `python3 bruteforce_check.py`.

---

# Appendices — code that ran and its output

## Appendix A — rederive.py (field arithmetic, irreducibility, point counting, factors)

`/tmp/j6blind/rederive.py` — verbatim.

```python
#!/usr/bin/env python3
"""
Blind re-derivation, joint J6-BLIND, TASK-20260913-3395e3.

Everything here is built from scratch: GF(2)[x] arithmetic on Python ints,
irreducibility test (Ben-Or), field F_{2^n} = F_2[alpha]/(f), generator search,
log/antilog tables (numpy), point counting on E: y^2 + xy = x^3 + A x^2 + B
with A = 0, B = 1, for x in a k-dimensional F_2-subspace V, and evaluation of the
closed-form factor.  No algebra system is used.
"""
import json
import random
import sys
import time
from fractions import Fraction

import numpy as np

A_COEFF = 0  # a2
B_COEFF = 1  # a6

# --------------------------------------------------------------------------
# GF(2)[x] on Python ints: bit i of the int is the coefficient of x^i.
# --------------------------------------------------------------------------


def pdeg(a):
    return a.bit_length() - 1


def pmulmod(a, b, f, n):
    """a*b mod f, f monic of degree n, deg a, deg b < n."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if (a >> n) & 1:
            a ^= f
    return r


def pdivmod(a, b):
    """Polynomial long division over GF(2): returns (q, r) with a = q*b + r."""
    if b == 0:
        raise ZeroDivisionError
    q = 0
    db = pdeg(b)
    while a and pdeg(a) >= db:
        s = pdeg(a) - db
        q ^= 1 << s
        a ^= b << s
    return q, a


def pgcd(a, b):
    while b:
        _, r = pdivmod(a, b)
        a, b = b, r
    return a


def ppowmod(base, e, f, n):
    r = 1
    while e:
        if e & 1:
            r = pmulmod(r, base, f, n)
        base = pmulmod(base, base, f, n)
        e >>= 1
    return r


def is_irreducible(f):
    """Ben-Or test: f (degree n) is irreducible over F_2 iff
    gcd(x^(2^i) - x, f) = 1 for i = 1..floor(n/2)."""
    n = pdeg(f)
    if n < 1:
        return False
    if not (f & 1):
        return False  # divisible by x
    h = 2  # x
    for _ in range(n // 2):
        h = pmulmod(h, h, f, n)  # h = x^(2^i) mod f
        g = pgcd(f, h ^ 2)
        if g != 1:
            return False
    return True


def smallest_irreducibles(n, count):
    out = []
    f = (1 << n) | 1
    while len(out) < count:
        if is_irreducible(f):
            out.append(f)
        f += 2
    return out


def poly_str(f):
    terms = [("x^%d" % i if i > 1 else ("x" if i == 1 else "1"))
             for i in range(pdeg(f), -1, -1) if (f >> i) & 1]
    return " + ".join(terms)


def factor_int(m):
    ps = []
    d = 2
    while d * d <= m:
        while m % d == 0:
            ps.append(d)
            m //= d
        d += 1
    if m > 1:
        ps.append(m)
    return sorted(set(ps))


# --------------------------------------------------------------------------
# The field F_{2^n}
# --------------------------------------------------------------------------


class GF2n:
    def __init__(self, n, f):
        assert pdeg(f) == n and is_irreducible(f)
        self.n = n
        self.f = f
        self.q = 1 << n
        self.order = self.q - 1

    def mul(self, a, b):
        return pmulmod(a, b, self.f, self.n)

    def sqr(self, a):
        return pmulmod(a, a, self.f, self.n)

    def pow(self, a, e):
        return ppowmod(a, e, self.f, self.n)

    def inv(self, a):
        """Extended Euclid in GF(2)[x]."""
        if a == 0:
            raise ZeroDivisionError
        r0, r1 = self.f, a
        s0, s1 = 0, 1
        while r1 != 1:
            qq, rr = pdivmod(r0, r1)
            r0, r1 = r1, rr
            # s0 - qq*s1 over GF(2)[x]
            prod = 0
            t = s1
            e = qq
            while e:
                if e & 1:
                    prod ^= t
                t <<= 1
                e >>= 1
            s0, s1 = s1, s0 ^ prod
        return pdivmod(s1, self.f)[1]

    def trace(self, a):
        t = 0
        c = a
        for _ in range(self.n):
            t ^= c
            c = self.sqr(c)
        assert t in (0, 1), "trace not in F_2 -- arithmetic bug"
        return t

    def find_generator(self):
        primes = factor_int(self.order)
        g = 2
        while True:
            if all(self.pow(g, self.order // p) != 1 for p in primes):
                return g, primes
            g += 1

    # ---- numpy vectorised helpers -------------------------------------

    def mul_const_vec(self, arr, c):
        """arr (uint32 array of field elements) times constant c."""
        tab = [c]
        for _ in range(1, self.n):
            tab.append(self.mul(tab[-1], 2))  # c * alpha^i
        res = np.zeros_like(arr)
        for i in range(self.n):
            bit = ((arr >> np.uint32(i)) & np.uint32(1)).astype(bool)
            res ^= np.where(bit, np.uint32(tab[i]), np.uint32(0))
        return res

    def build_tables(self, g):
        """exp[i] = g^i for 0 <= i < 2^n - 1; log[exp[i]] = i."""
        E = np.array([1], dtype=np.uint32)
        while len(E) < self.order:
            gpow = self.pow(g, len(E))
            E = np.concatenate([E, self.mul_const_vec(E, gpow)])
        E = E[: self.order]
        L = np.full(self.q, -1, dtype=np.int64)
        L[E] = np.arange(self.order, dtype=np.int64)
        assert L[0] == -1, "0 appeared as a power of g -- bug"
        assert np.all(L[1:] >= 0), "g is not a generator or table bug"
        self.exp_tab = E
        self.log_tab = L

    def inv_vec(self, X):
        lg = self.log_tab[X]
        assert np.all(lg >= 0)
        return self.exp_tab[(-lg) % self.order]

    def sqr_vec(self, X):
        out = np.zeros_like(X)
        nz = X != 0
        lg = self.log_tab[X[nz]]
        out[nz] = self.exp_tab[(2 * lg) % self.order]
        return out

    def trace_mask(self):
        m = 0
        for i in range(self.n):
            if self.trace(1 << i):
                m |= 1 << i
        return m

    def trace_vec(self, X):
        v = X & np.uint32(self.trace_mask_cached)
        v ^= v >> np.uint32(16)
        v ^= v >> np.uint32(8)
        v ^= v >> np.uint32(4)
        v ^= v >> np.uint32(2)
        v ^= v >> np.uint32(1)
        return (v & np.uint32(1)).astype(np.uint8)


# --------------------------------------------------------------------------
# Curve helpers
# --------------------------------------------------------------------------


def on_curve(F, x, y):
    lhs = F.sqr(y) ^ F.mul(x, y)
    rhs = F.mul(F.sqr(x), x) ^ F.mul(A_COEFF, F.sqr(x)) ^ B_COEFF
    return lhs == rhs


def koblitz_count(n):
    """#E(F_{2^n}) for y^2 + xy = x^3 + 1 (A=0, B=1), from #E(F_2) = 4:
    Frobenius trace a = -1, s_k = alpha^k + beta^k, s_{k+1} = a s_k - 2 s_{k-1}."""
    a = 2 + 1 - 4
    s_prev, s = 2, a
    if n == 0:
        return None
    for _ in range(n - 1):
        s_prev, s = s, a * s - 2 * s_prev
    return (1 << n) + 1 - s


def brute_force_count(F):
    """Count all affine points by trying every (x, y).  Small n only."""
    cnt = 0
    per_x0 = 0
    for x in range(F.q):
        for y in range(F.q):
            if on_curve(F, x, y):
                cnt += 1
                if x == 0:
                    per_x0 += 1
    return cnt + 1, per_x0  # + point at infinity


def count_points_on_x_set(F, Xset_arr, verify_points=True):
    """Given a numpy uint32 array of x-values (may include 0), count
    F_{2^n}-rational points of E with those x-coordinates, returning
    (L_points, L_xvalues_with_a_point, details)."""
    X = np.asarray(Xset_arr, dtype=np.uint32)
    has_zero = bool(np.any(X == 0))
    Xnz = X[X != 0]
    # For x != 0 substitute y = x*w:  w^2 + w = x + A + B/x^2.
    invX = F.inv_vec(Xnz)
    c = Xnz ^ F.sqr_vec(invX)  # B = 1, A = 0
    if A_COEFF:
        c ^= np.uint32(A_COEFF)
    if B_COEFF != 1:
        raise NotImplementedError
    tr = F.trace_vec(c)
    good = tr == 0
    n_good = int(np.count_nonzero(good))
    L_x = n_good + (1 if has_zero else 0)
    L_pts = 2 * n_good + (1 if has_zero else 0)
    details = {"n_x_nonzero_with_point": n_good,
               "n_x_nonzero_without_point": int(len(Xnz) - n_good),
               "zero_in_set": has_zero}
    if verify_points:
        # Explicitly construct both y for every good x and verify the curve
        # equation with SCALAR arithmetic (independent of the log tables);
        # also verify that x = 0 gives exactly the single point (0, sqrt(B)).
        root_tab = F.root_tab  # w with w^2 + w = c, for c in the image
        xs = Xnz[good]
        cs = c[good]
        ok = 0
        for x, cc in zip(xs.tolist(), cs.tolist()):
            w = int(root_tab[cc])
            assert F.sqr(w) ^ w == cc, "root table bug"
            y1 = F.mul(x, w)
            y2 = y1 ^ x
            assert y1 != y2
            assert on_curve(F, x, y1) and on_curve(F, x, y2), "point not on curve"
            ok += 1
        assert ok == n_good
        # for the bad x, verify with scalar arithmetic that Tr(c) = 1
        xs_bad = Xnz[~good]
        for x in xs_bad.tolist():
            cc = x ^ F.sqr(F.inv(x))
            assert F.trace(cc) == 1, "scalar/vector trace disagree"
        if has_zero:
            # y^2 = B has the unique solution y = sqrt(B); B = 1 -> y = 1.
            assert on_curve(F, 0, 1)
            # squaring is a bijection so no other y: check via log table image
            details["x0_points"] = 1
        details["verified_points_scalar"] = 2 * ok + (1 if has_zero else 0)
    return L_pts, L_x, details


def span_of(basis):
    S = np.array([0], dtype=np.uint32)
    for b in basis:
        S = np.concatenate([S, S ^ np.uint32(b)])
    return S


def rank_gf2(vecs):
    rows = list(vecs)
    rank = 0
    for bit in range(max(v.bit_length() for v in rows) - 1, -1, -1):
        piv = None
        for i in range(rank, len(rows)):
            if (rows[i] >> bit) & 1:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i] >> bit) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def random_subspace_basis(n, k, seed):
    rng = random.Random(seed)
    while True:
        basis = [rng.getrandbits(n) for _ in range(k)]
        if rank_gf2(basis) == k:
            return basis


# --------------------------------------------------------------------------
# The factor
# --------------------------------------------------------------------------


def factors_for(L, Vsize, t, q):
    """eq. (11) mean with |V|:  mu_11 = |V|^t / (q t!)
       same model with L in place of |V|: mu_L = L^t / (q t!)
       overstatement factor  mu_11 / mu_L = (|V|/L)^t
       correction multiplier mu_L / mu_11 = (L/|V|)^t"""
    from math import factorial
    over = Fraction(Vsize, L) ** t
    corr = Fraction(L, Vsize) ** t
    mu11 = Fraction(Vsize ** t, q * factorial(t))
    muL = Fraction(L ** t, q * factorial(t))
    out = {
        "overstatement_factor_(V/L)^t": {"exact": str(over), "float": float(over)},
        "correction_multiplier_(L/V)^t": {"exact": str(corr), "float": float(corr)},
        "mu_eq11_with_V": {"exact": str(mu11), "float": float(mu11)},
        "mu_with_L": {"exact": str(muL), "float": float(muL)},
    }
    if t == 2:
        # exact-count variants (not eq. (11)'s |V|^t/t! approximation)
        sets_ratio = Fraction(Vsize * (Vsize - 1), L * (L - 1))
        multi_ratio = Fraction(Vsize * (Vsize + 1), L * (L + 1))
        out["variant_exact_unordered_pairs_C(V,2)/C(L,2)"] = {
            "exact": str(sets_ratio), "float": float(sets_ratio)}
        out["variant_exact_multisets_C(V+1,2)/C(L+1,2)"] = {
            "exact": str(multi_ratio), "float": float(multi_ratio)}
    return out


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def main():
    t0 = time.time()
    results = {"cells": [], "checks": {}}

    # ---- sanity: brute-force vs trace criterion vs Koblitz count, small n --
    small = {}
    for n in (6, 8, 10):
        f = smallest_irreducibles(n, 1)[0]
        F = GF2n(n, f)
        g, primes = F.find_generator()
        F.build_tables(g)
        F.trace_mask_cached = F.trace_mask()
        W = np.arange(F.q, dtype=np.uint32)
        Q = F.sqr_vec(W) ^ W
        root = np.full(F.q, -1, dtype=np.int64)
        root[Q] = W
        F.root_tab = root
        bf, per_x0 = brute_force_count(F)
        Lp, Lx, det = count_points_on_x_set(F, W, verify_points=True)
        kob = koblitz_count(n)
        small[n] = {"f": hex(f), "brute_force_#E": bf, "trace_criterion_#E": Lp + 1,
                    "koblitz_#E": kob, "points_at_x0_bruteforce": per_x0}
        assert bf == Lp + 1 == kob, small[n]
        assert per_x0 == 1
    results["checks"]["small_n_bruteforce_vs_trace_vs_koblitz"] = small
    print("small-n checks OK:", json.dumps(small), flush=True)

    # ---- the three cells ---------------------------------------------------
    t = 2
    cells_spec = [(20, 10), (22, 11), (24, 12)]
    for n, k in cells_spec:
        q = 1 << n
        Vsize = 1 << k
        irreds = smallest_irreducibles(n, 3)
        f = irreds[0]
        print(f"\n=== n={n} k={k} |V|={Vsize} ===", flush=True)
        print("three smallest irreducible polys:", [hex(p) for p in irreds], flush=True)
        F = GF2n(n, f)
        g, primes = F.find_generator()
        F.build_tables(g)
        F.trace_mask_cached = F.trace_mask()
        # random-sample scalar/vector consistency checks
        rng = random.Random(12345 + n)
        for _ in range(2000):
            a = rng.randrange(1, F.q)
            b = rng.randrange(1, F.q)
            assert F.mul(a, F.inv(a)) == 1
            assert F.mul(a, b) == F.mul(b, a)
            assert F.mul(F.mul(a, b), a) == F.mul(a, F.mul(b, a))
            assert int(F.inv_vec(np.array([a], dtype=np.uint32))[0]) == F.inv(a)
            assert int(F.sqr_vec(np.array([a], dtype=np.uint32))[0]) == F.sqr(a)
            assert int(F.trace_vec(np.array([a], dtype=np.uint32))[0]) == F.trace(a)
            assert F.trace(a ^ b) == F.trace(a) ^ F.trace(b)
        # root table for w^2 + w = c over the whole field
        W = np.arange(F.q, dtype=np.uint32)
        Q = F.sqr_vec(W) ^ W
        root = np.full(F.q, -1, dtype=np.int64)
        root[Q] = W
        F.root_tab = root
        img = int(np.count_nonzero(root >= 0))
        assert img == F.q // 2, "image of w^2+w must be the trace-0 hyperplane"
        # full-field point count vs Koblitz closed form (validates the pipeline)
        Lp_all, Lx_all, det_all = count_points_on_x_set(F, W, verify_points=False)
        N_full = Lp_all + 1
        kob = koblitz_count(n)
        print(f"full-field #E via trace criterion = {N_full}, Koblitz formula = {kob}", flush=True)
        assert N_full == kob
        del W, Q

        cell_common = {
            "n": n, "k": k, "V_size": Vsize, "t": t, "q": q,
            "A": A_COEFF, "B": B_COEFF,
            "modulus_polynomial_hex": hex(f),
            "modulus_polynomial": poly_str(f),
            "generator_used_for_log_tables": g,
            "prime_factors_of_2^n-1": primes,
            "#E(F_2^n)_full": N_full,
            "#E(F_2^n)_koblitz_formula": kob,
        }

        # (a) low-degree subspace: polynomials in alpha of degree < k  (ints < 2^k)
        Vlow = np.arange(Vsize, dtype=np.uint32)
        Lp, Lx, det = count_points_on_x_set(F, Vlow, verify_points=True)
        assert Lp == 2 * Lx - 1
        cell = dict(cell_common)
        cell.update({
            "subspace_kind": "low_degree(deg<k, polynomial basis of modulus)",
            "subspace_basis": [hex(1 << i) for i in range(k)],
            "L_points": Lp, "L_xvalues_with_point": Lx, "details": det,
            "factor_L_points": factors_for(Lp, Vsize, t, q),
            "factor_L_xvalues": factors_for(Lx, Vsize, t, q),
        })
        results["cells"].append(cell)
        print(f"[low-degree f={hex(f)}] L_points={Lp}  L_x={Lx}  "
              f"(V/Lp)^2={float(Fraction(Vsize, Lp) ** 2):.15g}  "
              f"(V/Lx)^2={float(Fraction(Vsize, Lx) ** 2):.15g}", flush=True)

        # (a') low-degree subspace under the next two smallest moduli, to show
        #      dependence of L on the modulus choice
        for f2 in irreds[1:]:
            F2 = GF2n(n, f2)
            g2, _ = F2.find_generator()
            F2.build_tables(g2)
            F2.trace_mask_cached = F2.trace_mask()
            W2 = np.arange(F2.q, dtype=np.uint32)
            Q2 = F2.sqr_vec(W2) ^ W2
            root2 = np.full(F2.q, -1, dtype=np.int64)
            root2[Q2] = W2
            F2.root_tab = root2
            Lp_all2, _, _ = count_points_on_x_set(F2, W2, verify_points=False)
            assert Lp_all2 + 1 == kob
            del W2, Q2
            Lp2, Lx2, det2 = count_points_on_x_set(F2, Vlow, verify_points=True)
            cell2 = dict(cell_common)
            cell2.update({
                "modulus_polynomial_hex": hex(f2),
                "modulus_polynomial": poly_str(f2),
                "generator_used_for_log_tables": g2,
                "subspace_kind": "low_degree(deg<k, polynomial basis of ALTERNATIVE modulus)",
                "subspace_basis": [hex(1 << i) for i in range(k)],
                "L_points": Lp2, "L_xvalues_with_point": Lx2, "details": det2,
                "factor_L_points": factors_for(Lp2, Vsize, t, q),
                "factor_L_xvalues": factors_for(Lx2, Vsize, t, q),
            })
            results["cells"].append(cell2)
            print(f"[low-degree f={hex(f2)}] L_points={Lp2}  L_x={Lx2}  "
                  f"(V/Lp)^2={float(Fraction(Vsize, Lp2) ** 2):.15g}  "
                  f"(V/Lx)^2={float(Fraction(Vsize, Lx2) ** 2):.15g}", flush=True)
            del F2, root2

        # (b) seeded random k-dimensional subspaces (primary seed first)
        for seed in (20260913, 1, 2, 3):
            basis = random_subspace_basis(n, k, seed)
            Vr = span_of(basis)
            assert len(Vr) == Vsize and len(np.unique(Vr)) == Vsize
            Lpr, Lxr, detr = count_points_on_x_set(F, Vr, verify_points=True)
            assert Lpr == 2 * Lxr - 1
            cellr = dict(cell_common)
            cellr.update({
                "subspace_kind": f"random(seed={seed}, python random.Random, getrandbits({n}) x{k}, rank-checked)",
                "subspace_basis": [hex(b) for b in basis],
                "L_points": Lpr, "L_xvalues_with_point": Lxr, "details": detr,
                "factor_L_points": factors_for(Lpr, Vsize, t, q),
                "factor_L_xvalues": factors_for(Lxr, Vsize, t, q),
            })
            results["cells"].append(cellr)
            print(f"[random seed={seed}] L_points={Lpr}  L_x={Lxr}  "
                  f"(V/Lp)^2={float(Fraction(Vsize, Lpr) ** 2):.15g}  "
                  f"(V/Lx)^2={float(Fraction(Vsize, Lxr) ** 2):.15g}", flush=True)
        del F, root

    results["elapsed_seconds"] = time.time() - t0
    with open(sys.argv[1], "w") as fh:
        json.dump(results, fh, indent=1)
    print("\nwrote", sys.argv[1], "elapsed %.1fs" % results["elapsed_seconds"])


if __name__ == "__main__":
    main()
```

## Appendix B — bruteforce_check.py (independent enumeration of every y for every x in V)

`/tmp/j6blind/bruteforce_check.py` — verbatim.

```python
#!/usr/bin/env python3
"""
Independent cross-check for J6-BLIND: for x in V (low-degree subspace), count
y in ALL of F_{2^n} with y^2 + x*y == x^3 + 1, by direct vectorised evaluation
of both sides over the whole field.  Uses no quadratic-solving criterion, no
trace, no root table -- only field multiplication and squaring.
Run for n = 20 (k = 10) and n = 22 (k = 11); n = 24 is skipped for time.
"""
import sys
import time

import numpy as np

sys.path.insert(0, "/tmp/j6blind")
from rederive import GF2n, smallest_irreducibles, poly_str  # noqa: E402


def main():
    for n, k in ((20, 10), (22, 11)):
        t0 = time.time()
        f = smallest_irreducibles(n, 1)[0]
        F = GF2n(n, f)
        g, _ = F.find_generator()
        F.build_tables(g)
        Y = np.arange(F.q, dtype=np.uint32)
        Y2 = F.sqr_vec(Y)  # y^2 for every y (via log tables)
        # cross-check the vectorised squaring against scalar squaring on a sample
        for a in (0, 1, 2, 3, 12345, F.q - 1, F.q // 3):
            assert int(Y2[a]) == F.sqr(a)
        total_points = 0
        x_with_points = 0
        per_x_hist = {}
        for x in range(1 << k):
            rhs = F.mul(F.sqr(x), x) ^ 1  # x^3 + 1, scalar
            lhs = Y2 ^ F.mul_const_vec(Y, x)  # y^2 + x*y for all y
            cnt = int(np.count_nonzero(lhs == np.uint32(rhs)))
            per_x_hist[cnt] = per_x_hist.get(cnt, 0) + 1
            total_points += cnt
            if cnt:
                x_with_points += 1
        print(f"n={n} k={k} f={hex(f)} ({poly_str(f)}): "
              f"L_points={total_points} L_xvalues_with_point={x_with_points} "
              f"histogram(#y per x -> #x)={per_x_hist} elapsed={time.time()-t0:.1f}s",
              flush=True)


if __name__ == "__main__":
    main()
```

## Appendix C1 — output of `python3 rederive.py results.json`

`/tmp/j6blind/output.txt` — verbatim.

```text
small-n checks OK: {"6": {"f": "0x43", "brute_force_#E": 56, "trace_criterion_#E": 56, "koblitz_#E": 56, "points_at_x0_bruteforce": 1}, "8": {"f": "0x11b", "brute_force_#E": 288, "trace_criterion_#E": 288, "koblitz_#E": 288, "points_at_x0_bruteforce": 1}, "10": {"f": "0x409", "brute_force_#E": 968, "trace_criterion_#E": 968, "koblitz_#E": 968, "points_at_x0_bruteforce": 1}}

=== n=20 k=10 |V|=1024 ===
three smallest irreducible polys: ['0x100009', '0x10000f', '0x100017']
full-field #E via trace criterion = 1047376, Koblitz formula = 1047376
[low-degree f=0x100009] L_points=977  L_x=489  (V/Lp)^2=1.09852712699143  (V/Lx)^2=4.38512719501842
[low-degree f=0x10000f] L_points=1035  L_x=518  (V/Lp)^2=0.978856916147401  (V/Lx)^2=3.90787257196524
[low-degree f=0x100017] L_points=1075  L_x=538  (V/Lp)^2=0.907367009194159  (V/Lx)^2=3.62272494852199
[random seed=20260913] L_points=1013  L_x=507  (V/Lp)^2=1.02183558458694  (V/Lx)^2=4.07928449439601
[random seed=1] L_points=1047  L_x=524  (V/Lp)^2=0.956547519679185  (V/Lx)^2=3.81889167297943
[random seed=2] L_points=991  L_x=496  (V/Lp)^2=1.0677082643896  (V/Lx)^2=4.26222684703434
[random seed=3] L_points=1049  L_x=525  (V/Lp)^2=0.952903532439538  (V/Lx)^2=3.80435736961451

=== n=22 k=11 |V|=2048 ===
three smallest irreducible polys: ['0x400003', '0x400027', '0x40002b']
full-field #E via trace criterion = 4193912, Koblitz formula = 4193912
[low-degree f=0x400003] L_points=2051  L_x=1026  (V/Lp)^2=0.997076737251762  (V/Lx)^2=3.98442065744826
[low-degree f=0x400027] L_points=2067  L_x=1034  (V/Lp)^2=0.981700362481916  (V/Lx)^2=3.92300468780982
[low-degree f=0x40002b] L_points=2053  L_x=1027  (V/Lp)^2=0.995135010862888  (V/Lx)^2=3.97666509596304
[random seed=20260913] L_points=2051  L_x=1026  (V/Lp)^2=0.997076737251762  (V/Lx)^2=3.98442065744826
[random seed=1] L_points=2105  L_x=1053  (V/Lp)^2=0.946576469327074  (V/Lx)^2=3.78271099891866
[random seed=2] L_points=2035  L_x=1018  (V/Lp)^2=1.01281722195727  (V/Lx)^2=4.0472902296965
[random seed=3] L_points=2019  L_x=1010  (V/Lp)^2=1.02893340408271  (V/Lx)^2=4.11165964121165

=== n=24 k=12 |V|=4096 ===
three smallest irreducible polys: ['0x100001b', '0x100006f', '0x1000087']
full-field #E via trace criterion = 16783200, Koblitz formula = 16783200
[low-degree f=0x100001b] L_points=4047  L_x=2024  (V/Lp)^2=1.0243620654737  (V/Lx)^2=4.09542408098861
[low-degree f=0x100006f] L_points=4113  L_x=2057  (V/Lp)^2=0.99175061147906  (V/Lx)^2=3.96507414241043
[low-degree f=0x1000087] L_points=4135  L_x=2068  (V/Lp)^2=0.981225595054457  (V/Lx)^2=3.92300468780982
[random seed=20260913] L_points=3993  L_x=1997  (V/Lp)^2=1.05225567232012  (V/Lx)^2=4.20691528028146
[random seed=1] L_points=4103  L_x=2052  (V/Lp)^2=0.996590773210117  (V/Lx)^2=3.98442065744826
[random seed=2] L_points=4081  L_x=2041  (V/Lp)^2=1.00736464923933  (V/Lx)^2=4.02748458175266
[random seed=3] L_points=4013  L_x=2007  (V/Lp)^2=1.04179333935206  (V/Lx)^2=4.16509729648274

wrote /tmp/j6blind/results.json elapsed 21.7s
```

## Appendix C2 — output of `python3 bruteforce_check.py`

`/tmp/j6blind/bruteforce_output.txt` — verbatim.

```text
n=20 k=10 f=0x100009 (x^20 + x^3 + 1): L_points=977 L_xvalues_with_point=489 histogram(#y per x -> #x)={1: 1, 2: 488, 0: 535} elapsed=29.6s
n=22 k=11 f=0x400003 (x^22 + x + 1): L_points=2051 L_xvalues_with_point=1026 histogram(#y per x -> #x)={1: 1, 2: 1025, 0: 1022} elapsed=257.4s
```

## Appendix C3 — eq. (11) transcription check against Table 1, and N/q

`/tmp/j6blind/eq11_table_check.txt` — verbatim.

```text
eq.(11) P = 1 - exp(-|V|^t/(q t!)) vs Table 1 column P(n,m,t,k) as printed in frozen text:
  n=12 m=6 t=6 k=2: lambda=0.00138889  1-exp(-lambda)=0.0014  printed=0.0013
  n=13 m=4 t=4 k=4: lambda=0.333333  1-exp(-lambda)=0.2835  printed=0.2834
  n=13 m=5 t=5 k=3: lambda=0.0333333  1-exp(-lambda)=0.0328  printed=0.0327
  n=14 m=4 t=4 k=4: lambda=0.166667  1-exp(-lambda)=0.1535  printed=0.1535
  n=14 m=5 t=5 k=3: lambda=0.0166667  1-exp(-lambda)=0.0165  printed=0.0165
  n=15 m=4 t=4 k=4: lambda=0.0833333  1-exp(-lambda)=0.0800  printed=0.0799
  n=15 m=5 t=5 k=3: lambda=0.00833333  1-exp(-lambda)=0.0083  printed=0.0082
  n=16 m=4 t=4 k=4: lambda=0.0416667  1-exp(-lambda)=0.0408  printed=0.0408
  n=17 m=3 t=3 k=6: lambda=0.333333  1-exp(-lambda)=0.2835  printed=0.2834

N/q (in case the codomain were E(F_q) rather than F_q):
  n=20: N=1047376 q=1048576 N/q=0.9988555908  (N-q-1)=-1201
  n=22: N=4193912 q=4194304 N/q=0.9999065399  (N-q-1)=-393
  n=24: N=16783200 q=16777216 N/q=1.0003566742  (N-q-1)=5983
```

## Appendix D — make_json.py (generates rederived-values.json from results.json)

`/tmp/j6blind/make_json.py` — verbatim.

```python
#!/usr/bin/env python3
"""Generate rederived-values.json from results.json (no hand transcription)."""
import json
import sys

r = json.load(open('/tmp/j6blind/results.json'))

closed_form = ("Phi(L,|V|,t) = mu_11(|V|)/mu_11(L) = (|V|/L)^t   [overstatement factor of eq. (11)'s "
               "predicted mean when |V| is charged in place of L]; equivalently the correction multiplier "
               "true/predicted = (L/|V|)^t. Here mu_11(M) = M^t/(q*t!) is the mean number of zero-hits "
               "(= t-element decompositions) implied by eq. (11)'s model with M available x-values; q and t! "
               "cancel, and t enters only as the exponent.")

assumptions = [
 "A1. The 'predicted mean number of t-element decompositions' in eq. (11)'s model is the expected number of permutation-classes of t-tuples mapped to 0 by the symmetric random mapping: K/q with K ~ M^t/t! (eq. (11) reads K ~ |V|^t/t!, hit probability 1/q per class, independent classes). The probability 1-(1-1/q)^K in eq. (11) is the probability of >=1 hit; the mean is K/q.",
 "A2. The substitution |V| -> L changes only the size M of the pool from which each of the t entries is drawn; q (the codomain F_q of the summation polynomial), t, t!, and the 1/q hit probability are unchanged. If instead the codomain were taken to be E(F_q) of size N = #E(F_{2^n}), an extra factor N/q would multiply the ratio; N/q is reported per cell but NOT folded into the factor.",
 "A3. The t entries are drawn independently from the same pool and the map is symmetric under permutation, exactly as in eq. (11); the t! class-count symmetry is common to both sides and cancels.",
 "A4. eq. (11)'s own approximation K ~ M^t/t! is used on both sides. With exact class counts at t=2 the ratio becomes C(|V|,2)/C(L,2) (distinct entries) or C(|V|+1,2)/C(L+1,2) (multisets); both are reported per cell and differ from (|V|/L)^2 only in the 5th significant figure at these sizes.",
 "A5. L is evaluated exactly by point counting; no heuristic ~|V|/2 or ~|V| approximation is used for L.",
 "A6. The target R is modelled as in eq. (11): its x-coordinate is a random element z of F_q; the factor does not depend on R.",
]

underdetermined = [
 "U1 (material, ~2^t effect). The statement defines L as the number of F_{2^n}-rational POINTS with x in V, but then says 'only L of them [the |V| x-values] carry a rational point', which is a count of x-VALUES. These differ: every nonzero x in V that carries a point carries exactly two ((x,y) and (x,y+x)), and x=0 (always in V) carries exactly one ((0,sqrt(B)) = (0,1)), so L_points = 2*L_xvalues - 1. Under the points reading the factor is ~1; under the x-values reading it is ~2^t = 4 at t=2. BOTH are evaluated and reported. 'L' and 'factor' in each cell follow the explicit definition (points); 'L_alt_xvalues' and 'factor_alt_xvalues' follow the 'of them' reading.",
 "U2 (material, ~+-10% effect). V is not fixed. The low-degree subspace (Semaev, frozen text lines 538-546: 'Let V be a set of all polynomials in alpha of degree < k') depends on the modulus f defining the polynomial basis; L differs across moduli (e.g. n=20: L_points = 977, 1035, 1075 for the three smallest irreducible f). A random subspace gives yet other values. All evaluated cells are listed; the ones marked primary are the smallest-irreducible-modulus low-degree subspace and the seed-20260913 random subspace.",
 "U3 (labelling). 'The factor by which the substitution misstates the mean' has two directions; 'factor' is predicted/corrected = (|V|/L)^t and 'factor_reciprocal' is corrected/predicted = (L/|V|)^t.",
 "U4 (minor). 'Exact' is relative to eq. (11)'s model, which itself uses K ~ |V|^t/t!; exact-count variants at t=2 are reported (A4).",
 "U5 (minor). Whether the point at infinity or the 2-torsion point (0,1) are 'points whose x-coordinate lies in V': infinity has no x-coordinate and is excluded; (0,1) has x=0 in V and is counted once.",
]

cells_out = []
for c in r['cells']:
    Lp = c['L_points']; Lx = c['L_xvalues_with_point']; V = c['V_size']; t = c['t']; q = c['q']
    kind = c['subspace_kind']
    primary = kind.startswith('low_degree(deg<k, polynomial basis of modulus)') or 'seed=20260913' in kind
    fp = c['factor_L_points']; fx = c['factor_L_xvalues']
    cells_out.append({
        "n": c['n'], "k": c['k'], "V_size": V, "t": t, "q": q,
        "curve": {"A": c['A'], "B": c['B'], "equation": "y^2 + x*y = x^3 + A*x^2 + B"},
        "subspace_kind": kind,
        "primary_cell": primary,
        "modulus_polynomial_hex_or_bits": c['modulus_polynomial_hex'],
        "modulus_polynomial": c['modulus_polynomial'],
        "polynomial_basis_convention": "element sum a_i alpha^i <-> integer sum a_i 2^i; 'degree < k' <-> integer < 2^k",
        "generator_used_for_log_tables": c['generator_used_for_log_tables'],
        "subspace_basis_hex": c['subspace_basis'],
        "L": Lp,
        "L_reading": "number of F_{2^n}-rational points of E with x in V (statement's explicit definition)",
        "L_points": Lp,
        "L_alt_xvalues": Lx,
        "L_alt_reading": "number of x in V carrying at least one rational point ('only L of them carry a rational point' reading); L_points = 2*L_alt_xvalues - 1",
        "x_values_nonzero_with_point": c['details']['n_x_nonzero_with_point'],
        "x_values_nonzero_without_point": c['details']['n_x_nonzero_without_point'],
        "x_equals_zero_points": 1,
        "factor": fp['overstatement_factor_(V/L)^t']['float'],
        "factor_exact": fp['overstatement_factor_(V/L)^t']['exact'],
        "factor_closed_form": "(|V|/L)^t with L = L_points",
        "factor_reciprocal": fp['correction_multiplier_(L/V)^t']['float'],
        "factor_reciprocal_exact": fp['correction_multiplier_(L/V)^t']['exact'],
        "factor_alt_xvalues": fx['overstatement_factor_(V/L)^t']['float'],
        "factor_alt_xvalues_exact": fx['overstatement_factor_(V/L)^t']['exact'],
        "factor_alt_xvalues_closed_form": "(|V|/L_alt_xvalues)^t",
        "factor_alt_xvalues_reciprocal": fx['correction_multiplier_(L/V)^t']['float'],
        "factor_alt_xvalues_reciprocal_exact": fx['correction_multiplier_(L/V)^t']['exact'],
        "mu_eq11_with_V": fp['mu_eq11_with_V'],
        "mu_with_L_points": fp['mu_with_L'],
        "mu_with_L_alt_xvalues": fx['mu_with_L'],
        "variant_exact_pairs_C(V,2)/C(L,2)_points": fp['variant_exact_unordered_pairs_C(V,2)/C(L,2)'],
        "variant_exact_multisets_C(V+1,2)/C(L+1,2)_points": fp['variant_exact_multisets_C(V+1,2)/C(L+1,2)'],
        "variant_exact_pairs_C(V,2)/C(L,2)_xvalues": fx['variant_exact_unordered_pairs_C(V,2)/C(L,2)'],
        "variant_exact_multisets_C(V+1,2)/C(L+1,2)_xvalues": fx['variant_exact_multisets_C(V+1,2)/C(L+1,2)'],
        "N_full_curve_order": c['#E(F_2^n)_full'],
        "N_koblitz_closed_form": c['#E(F_2^n)_koblitz_formula'],
        "N_over_q": c['#E(F_2^n)_full'] / q,
        "verified_points_by_scalar_arithmetic": c['details']['verified_points_scalar'],
    })

out = {
 "task_id": "TASK-20260913-3395e3",
 "joint": "J6-BLIND",
 "review_round_id": "REVIEW-SEMBIN-20260913-run2",
 "role": "validator",
 "blind": True,
 "closed_form": closed_form,
 "closed_form_symbolic": {"overstatement_factor": "(|V|/L)^t", "correction_multiplier": "(L/|V|)^t",
                          "mu_eq11": "M^t/(q*t!) with M = number of charged x-values"},
 "eq11_as_read": ("Frozen text lines 400-419: symmetric random mapping V^t -> F_q; K ~ |V|^t/t! permutation "
                  "classes; P(q,m,t,|V|) = 1-(1-1/q)^K ~ 1-(1-1/q)^{|V|^t/t!} ~ 1-exp(-|V|^t/(q t!))  (11); if "
                  "|V|^t/(q t!) = o(1) then P ~ |V|^t/(q t!). Transcription checked against Table 1's P(n,m,t,k) "
                  "column (all nine rows agree to the printed 4 digits, truncation)."),
 "assumptions": assumptions,
 "underdetermined": underdetermined,
 "curve": {"equation": "y^2 + x*y = x^3 + A*x^2 + B", "A": 0, "B": 1, "E(F_2)_order": 4, "frobenius_trace_over_F_2": -1},
 "environment": {"python": "3.12.3", "numpy": "2.4.4", "algebra_system": "none"},
 "checks": r['checks'],
 "independent_bruteforce_over_all_y": {
   "n=20,k=10,f=0x100009": {"L_points": 977, "L_xvalues_with_point": 489, "histogram_y_per_x": {"1": 1, "2": 488, "0": 535}},
   "n=22,k=11,f=0x400003": {"L_points": 2051, "L_xvalues_with_point": 1026, "histogram_y_per_x": {"1": 1, "2": 1025, "0": 1022}},
   "note": "enumerates every y in F_{2^n} for every x in V using only field mul/sqr; no trace criterion, no root table; n=24 skipped for time"
 },
 "cells": cells_out,
}
p = sys.argv[1]
json.dump(out, open(p, 'w'), indent=1)
print('wrote', p, 'cells:', len(cells_out))
```
