# Independent technical review — TASK-20260722-210

Role: independent Reviewer  
Input: six BATCH-002 producer artifacts at snapshot commit
`f4425f5ac689eef52e406363ca8d12795fa6e801`  
Scope: literature, symbolic derivation, and defensive protocol review; no
empirical run and no official state transition

## Verdict

The BATCH-002 synthesis is materially sound after four scope qualifications.

1. The current Ogilvie-family reference is Hou–Jiang's corrected table, not
   Ogilvie's published 2–3-bit table. The corrected maximum matched MLWE/LWE
   gap is 0.8 bit.
2. The carry-aware LaMS/isometry derivation is algebraically correct. It
   reduces the proposed orbit statistic to known same-\(A\) coverage and
   weighted rotated-vector scoring. This disposes of the present
   `IDEA-20260722-001` mechanism, not all future structured or p-adic attacks.
3. FIPS 203 does not expose a decryption-failure bit. Conditional oracle-call
   counts, physical leakage, and deterministic implementation bugs are three
   different evidence classes and must remain separate from passive MLWE.
4. `IDEA-20260722-002` and `IDEA-20260722-003` are defensible protocol-security
   studies, not cryptanalytic breakthroughs. The first is cheap and nearly
   protocol-ready; the second needs a numeric acquisition and replication
   budget before execution.

The snapshot itself is valid. Git identifies parent `62151b25...`, exact commit
`f4425f5a...`, the six declared producer paths, and all six receipt hashes. The
receipt's `commit_sha: null` is an intentional self-reference workaround; the
dispatch queue supplies the binding. Uncommitted dispatcher files do not alter
the committed producer paths.

## 1. Corrected attack-cost baseline

### 1.1 The stale table and the actual correction

Ogilvie 2026/279 published:

| Model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 118.8 | 170.2 | 234.8 |
| `CC` | 137.1 | 192.7 | 257.2 |
| `CN` | 132.2 | 186.9 | 252.4 |

Those values are historically real but are not a current baseline. The
independent correction chain is:

* Carrier's code contained `2^100`, which is XOR in Python, rather than
  exponentiation `2**100`.
* The isometric probability path passed `nfft` where the short-vector
  dimension `beta1` was required.
* Hou–Jiang report the corrected Table 1.1 at a success-probability lower
  bound of 0.3.
* TabOg commit `77efa315...`, dated 2026-04-28, is titled “fix bug in
  probability calculation; better R search.” Its refactored weighted integral
  uses `beta1` for the lattice-vector component.
* The correction fork at `7cce6a5...` explicitly documents the
  `nfft`/`beta1` mismatch and retains corrected outputs.

The corrected table is:

| Model | LWE 512/768/1024 | Isometric MLWE 512/768/1024 | Matched gap |
|---|---|---|---|
| `C0` | 121.9 / 173.0 / 237.5 | 121.9 / 173.0 / 237.4 | 0.0 / 0.0 / 0.1 |
| `CC` | 139.3 / 194.7 / 259.6 | 139.1 / 194.7 / 259.0 | 0.2 / 0.0 / 0.6 |
| `CN` | 134.8 / 189.5 / 254.2 | 134.5 / 188.7 / 254.1 | 0.3 / 0.8 / 0.1 |

Thus the producer correctly supersedes every use of 137.1/192.7/257.2 as a
current comparator. Any document still calling those values current, or
claiming a present 2–3-bit ML-KEM structure gain, is stale.

The raw fork outputs do contain the producer's selected decimals, but the same
files contain earlier repeated optimizer results with different values and
fresh polar-code data. No seeds are recorded. The rounded paper table is the
stable claim; ten decimal places are not reproducible accuracy.

### 1.2 Li–Zheng is a screen, not a lower envelope

Li–Zheng 2026/1400 Table 3 supports the reported model-specific minima:

| Model | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| `C0` | 118.09 | 172.36 | 238.12 |
| `CC` | 139.20 | 194.02 | 259.40 |
| `CN` | 134.42 | 189.36 | 253.68 |

The source models incorrect-guess scores as normal. It acknowledges the
wrong-tail concern and argues that the normal prediction is conservative for
the selected Carrier regime, but it does not supply an independently validated
tail law under one common revision and success target. The producer is
therefore right to call label-aligned minima provisional rather than a jointly
reproduced lower envelope.

The cost-model firewall is essential. `C0`, `CC`, `CN`, progressive-BKZ gate
counts, memory-routing costs, provable-dual totals, quantum query models, and
physical projections are not common units. Values from different rows cannot
be subtracted, minimized together, or “corrected” by adding a memory penalty
from another attack.

### 1.3 LaMS and the QRS correction collision

LaMS 2026/1326 explicitly derives the Gaussian-width conversion

\[
\sigma_e=\sigma\sqrt{2\pi}.
\]

Its Table 1 gives the following source-defined provable-dual estimates:

| Method | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|---|---:|---:|---:|
| corrected PS24 | 238 | 347 | 478 |
| corrected QX25 | 213 | 313 | 431 |
| LaMS, \(p=2\) | 191 | 282 | 390 |

The 22/31/41-bit LaMS gains are against corrected QX25 only. They are not
`CC` gains over Hou–Jiang, Carrier, or Li–Zheng.

The pinned LaMS source confirms the scaling, hard-codes the corrected PS24
literature table, and searches QX25 and LaMS. Its README requires an external
`lattice-estimator` checkout but does not pin a revision; it retains no saved
optimizer receipt. The publication table is supported, but the package is not
a self-contained one-command reproduction.

The QRS paper compares with Pouly–Shen under the same parameter choices and
reports 9/4/13-bit reductions. Because LaMS subsequently identifies a
consequential error-width substitution in those classical parameters, the
published QRS absolute Kyber tables are stale pending a corrected global
rerun. This does not refute the QRS sampling theorem.

No checked source supplies a reproducible passive full-key recovery at a
standardized ML-KEM parameter set. That is a literature-search boundary, not a
proof that no such algorithm can exist.

## 2. Independent carry-aware LaMS/isometry reconstruction

### 2.1 LaMS layer

Split the flattened relation as

\[
b=A_Gs_G+A_Ds_D+e\pmod q.
\]

At layer \(i\), on the branch where all lower digits are correct, write

\[
s_G=c_i+p^it_i,\qquad
c_i=\sum_{r<i}p^rd_r,\qquad
B_i=p^iA_G.
\]

Then

\[
b_i=b-A_Gc_i=B_it_i+A_Ds_D+e\pmod q. \tag{1}
\]

LaMS defines

\[
\widehat B_i=\frac qp\left\lfloor\frac pqB_i\right\rfloor,\qquad
\Delta_i=B_i-\widehat B_i,
\]

and samples one list

\[
Z\leftarrow D_{L_q^\perp(A_D),qs}.
\]

The unchanged \(A_D\), not equality of all rational lattices, is why the same
literal list can be reused across layers. This matches LaMS equations (6)–(9)
and Algorithms 1–2.

### 2.2 Signed digits require a wrap and carry

Let \(S\) be a signed permutation and let \(x,y\) be canonical residues with

\[
y=[Sx]_q=Sx+q\omega_S(x).
\]

For a negative row, \(\omega=1\) exactly when the selected coefficient is
nonzero. In particular, zero must stay on the \(\omega=0\) branch. Define

\[
c_i'=(Sc_i+q\omega)\bmod p^i,\qquad
\kappa_i=\frac{Sc_i+q\omega-c_i'}{p^i}.
\]

Direct substitution gives

\[
t_i'=St_i+\kappa_i,\qquad
d_i'=(Sd_i+\kappa_i)\bmod p. \tag{2}
\]

Therefore negation is not digitwise in canonical base \(p\). The missing state
in a naive rotation is precisely the public wrap/carry history.

Assume an orbit-stable guessed block with
\(JA_G=A_GS_G\). The transformed layer target is

\[
\begin{aligned}
b_i'&=Jb-A_Gc_i'\\
    &=Jb_i+B_i\kappa_i\pmod q. \tag{3}
\end{aligned}
\]

It is a valid correctly updated LaMS layer, but it is not simply \(Jb_i\).
An incorrect lower digit changes every later prefix, carry, target, and
candidate label; orbit averaging does not repair that branch.

### 2.3 Modulus-switching cocycle

For canonical \(x\ne0\), the scalar switch map satisfies

\[
\mathcal R_p(q-x)=q-\frac qp-\mathcal R_p(x),\qquad
\Delta_p(q-x)=\frac qp-\Delta_p(x), \tag{4}
\]

with a separate zero branch. Consequently, even when \(JB_i=B_iS_G\),
entrywise switching need not commute with signs. Define

\[
C_i=J\widehat B_i-\widehat B_iS_G
   =\Delta_iS_G-J\Delta_i\pmod q.
\]

For \(a'=(S_Ga+\kappa_i)\bmod p\), using that
\(p\widehat B_i\) is a multiple of \(q\) gives

\[
x_i'(a')=Jx_i(a)+\Delta_i\kappa_i+C_ia\pmod q. \tag{5}
\]

The pair \((\kappa_i,C_i)\) is a known label/rounding cocycle. It obstructs a
naive “same candidate, same score” average but does not expose a secret
invariant.

### 2.4 Exact score reduction and partition boundary

Let

\[
\alpha_i(z)=\sum_{v\in\mathbb Z_q^g}
\exp\!\left(-\frac{2\pi i}{q}\langle\Delta_i v,z\rangle\right).
\]

For any public/candidate shift \(u\),

\[
G_{Z,i}(Jb-u)=
\Re\frac1N\sum_{z\in Z}
\alpha_i(z)e^{-2\pi i\langle u,z\rangle/q}
e^{2\pi i\langle b,J^Tz\rangle/q}. \tag{6}
\]

Equation (6) is exact. A target-orbit LaMS score is an original-target score
using equal-norm rotated vectors \(J^Tz\) and known attached weights. Carries
and switching alter those weights and candidate labels; they do not create
fresh samples.

Two partition conventions must remain distinct:

* With a fixed \(G,D\), the literal \(A_D\) and list \(Z\) remain valid, but
  different orbit elements cover different signed/permuted original
  coordinates.
* If candidates are aligned to one original coordinate set, the partition
  rotates. The pool must rotate into the associated dual lattice unless
  \(G,D\) are orbit-stable, for example unions of complete polynomial blocks.

This is the weighted adjoint form of Wu–Xu's rotated-vector mechanism and the
same-\(A\) coverage/preprocessing reuse of Ogilvie and Hou–Jiang. Since every
orbit target is an invertible deterministic transform of \(b\),

\[
I(s;b,\{J_jb\}_j\mid A)=I(s;b\mid A).
\]

The producer's narrow negative conclusion is supported: the current
LaMS-isometry proposal adds no structural information and derives no
unmatched two-bit cost path. The stronger statement “all p-adic or structured
MLWE research is closed” would be false. In particular, LaMS's
independent-uniform matrix/rank assumptions have not been proved for the
block-negacyclic matrix and fixed sample supply of one FIPS 203 key.

## 3. FIPS 203 and the oracle boundary

FIPS 203 Table 1 gives honest decapsulation-failure rates
\(2^{-138.8}\), \(2^{-164.8}\), and \(2^{-174.8}\) for the three parameter
sets. Algorithm 18:

1. decrypts the ciphertext;
2. derives the re-encryption coins;
3. computes \(\bar K=J(z\|c)\);
4. re-encrypts and compares the complete ciphertext;
5. substitutes \(\bar K\) on mismatch; and
6. returns a 256-bit value.

An honest failure probability is therefore not an exported failure bit.
FIPS 203's ideal interface supplies neither a PC bit, a DF bit, an inequality,
nor soft leakage. Such a channel must be instantiated by protocol
confirmation, logic error, timing, cache behavior, power/EM leakage, or a
fault.

The producer's three-way separation is the correct security interpretation:

| Class | Evidence meaning |
|---|---|
| Passive core MLWE | public-key/public-data algorithm only |
| Conditional oracle algorithm | query complexity assuming a stated oracle |
| Implementation attack | measured or deterministic construction of that oracle on named code/hardware |

For example, 2,950 calls for ML-KEM-768 is supported only for the stipulated
95%-accurate one-bit oracle. The physical GoFetch follow-up separately charges
calibration, Prime+Probe measurements, platform access, burst errors, and
retries. Its 73/100 criterion is Hamming distance at most four, not universal
exact-key success.

The two comparison CVEs are unusually clean defensive controls:

* CVE-2026-10097: wolfSSL AVX2 ML-KEM-1024 compared 1,536 of 1,568 bytes.
  NVD/CNA reports about 350 chosen ciphertexts and about 98% PoC success when
  the caller can distinguish valid-path and rejection secrets. PR 10430 fixes
  the final block.
* CVE-2026-6330: wolfSSL ARM64 NEON compared only half the input. PR 10192
  repairs the reduction and adds a tamper/FO-rejection test. No end-to-end
  recovery count is reported, so the AVX2 metric must not be transferred.

Both are violations of Algorithm 18 on named backends, not weaknesses in
passive MLWE or every FIPS-conforming implementation.

Final ML-KEM also differs from round-three Kyber in the FO derivation,
pre-hashing of encapsulation randomness, fixed 256-bit shared-secret length,
input checks, and key-generation domain separation. Oracle and
implementation claims require final-FIPS reproduction even when the
underlying ring arithmetic transfers.

## 4. Defensive candidate review and ranking

### Rank 1 — IDEA-20260722-002

The cross-backend negative-ciphertext matrix survives as a defensive
conformance regression. Its information gain per cost is high because it has
deterministic vulnerable controls, patched controls, exact FIPS semantics, and
no physical acquisition campaign.

Before design approval, the protocol should:

* pin exact vulnerable and patched commits and all build flags;
* attest that AVX2 or NEON code actually ran rather than silently dispatching
  to scalar;
* use architecture-appropriate runners;
* hold the decapsulation key fixed across backend comparisons;
* mutate every byte and SIMD lane of an equal-length ciphertext;
* compare exact shared-secret bytes against an independently checked scalar
  Algorithm-18 oracle; and
* test malformed lengths separately from equal-length implicit rejection.

Passing proves functional rejection conformance only. It says nothing about
timing, power, EM, cache, fault resistance, or general release security.

### Rank 2 — IDEA-20260722-003

The end-to-end soft-oracle budget survives as a defensive protocol-security
question. Soft-PC, SPRT, adaptive-LDPC, and masked-Keccak work supports the
premise that hard accuracy alone discards confidence, dependence,
executions-per-query, calibration, and profiling cost.

It is not yet bounded enough to execute. A frozen protocol must distinguish PC
from DF semantics, match each trace classifier to a compatible recovery
backend, and set maximum devices, keys, profiling traces, attack traces,
retries, wall time, and post-processing. The factor-two median claim also
needs a predeclared power calculation and confidence interval; three
configurations alone do not define replication.

The cheapest pre-gate is offline: on one frozen trace corpus, compare hard,
calibrated-soft, and time-ordered burst-aware replay on held-out keys. Advance
to physical key recovery only if calibration and rank prediction discriminate
the models. This remains implementation-specific defensive measurement, not
evidence that passive MLWE is easier.

No passive algorithmic proposal survives this batch. The optional
\(n\le16\) carry/cocycle check is useful transcription assurance but has low
research information and cannot validate standardized costs.

## 5. Source and reproducibility conclusion

The most material primary checks covered FIPS 203; Ogilvie and Hou–Jiang;
LaMS equations, algorithms, theorems, correction, and estimator; Wu–Xu
rotated vectors; Li–Zheng's table and tail assumption; the QRS comparison;
adaptive-LDPC; soft-PC and SPRT; masked Keccak; both wolfSSL CVEs; and PRs
10430/10192. The detailed statuses and URLs are recorded in
`review_report.yaml`.

The evidence supports a corrected and carefully separated research map. It
does not support a passive ML-KEM break, a cross-model security scalar,
universal implementation vulnerability, or closure of future structured
cryptanalysis.
