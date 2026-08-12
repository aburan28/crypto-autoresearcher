# Independent extraction transcript

Task: `TASK-20260730-005`  
Source SHA-256: `d4785e2863eebe97eb3a2909e02d669d138b2080c6e96e42c70d8d4fd2e89675`  
Extractor: Poppler `pdftotext -layout`, applied to the archived 25-page PDF.

## Reproduction command

For each locator below:

```text
pdftotext -layout -f <page> -l <page> peikert_2019_725_final.pdf -
```

The transcript preserves the extractor's plain-text conventions: `L̃` is a
base letter plus combining tilde, superscripts are flattened, and the ceiling
brackets in Equation (3.5) appear as `d` and `e`. The normalized mathematical
renderings are therefore checked against surrounding prose and the PDF image,
not silently treated as raw extractor output.

## PDF page 14 — Section 3.3.3, Equation (3.5)

Raw layout extraction:

```text
Concrete constants for QRACM. A close inspection of [Kup11, Section 4.3] shows that the constant
factor in the QRACM bound, and the associated O(1) number of QRACM lookups, are small. The entire
algorithm can be run with 9 lookups and as little as

                     R = Lmax · dmax{(1 + α) log(S 0 /S), log Lmax }e                    (3.5)

bits of reusable QRACM, or with as few as 4 lookups and Lmax · (2(1 + α) log(S 0 /S) + 3 log Lmax ) bits, or
with various intermediate combinations.
```

Normalized check:

\[
R=L_{\max}\left\lceil\max\{(1+\alpha)\log(S_0/S),\log L_{\max}\}\right\rceil .
\]

The BATCH-009 excerpt's constants `9`, \(L_{\max}\), and Equation `(3.5)`
match. Its restored ceiling brackets and subscripts are typography
normalization, not changed mathematical content.

## PDF page 18 — Section 4.1, Figure 1 caption and parameter bullet

Raw layout extraction:

```text
Figure 1: Example complexity estimates for secret-key recovery against CSIDH-log p using the collimation
sieve with arity r = 2, for various bit lengths (rounded to the nearest integer) of the CSIDH parameter p. Each
missing entry is equal to the one above it. Here N is the estimated (or known, in the case of CSIDH-512)
group order; L = S are respectively the desired length and range size of the sieve’s final phase vector;
“QRACM” is the number of bits of quantumly accessible classical memory, which is given by Equation (3.5)
with α = 1/2 for L̃max = 8L indexable cells; “depth” is the depth of the sieve’s recursion tree; Q̃total is the
total number of queries to the quantum oracle to recover all but 56 bits of the secret; T is the total T-gate
complexity of the attack, assuming the complexity of implementing the oracle is not much more than for
evaluating on the “best conceivable” distribution.
```

Raw layout extraction of the bullet:

```text
• We impose a maximum phase-vector length of L̃max = 8L. This reflects the fact that the generated
  phase vectors are sometimes longer than the desired length L, but are almost always within a factor
  of 8, and we can enforce this as a hard bound by doing a partial measurement whenever a phase vector
  happens to be longer. We use Equation (3.5) for the number of bits of QRACM as a function of L̃max .
```

The BATCH-009 Figure 1 and bullet quotations match all material words and
constants: \(\alpha=1/2\), \(\widetilde L_{\max}=8L\), “maximum,” the
factor-of-eight statement, partial-measurement enforcement, and the reference
to Equation (3.5). The BATCH-009 ellipses omit surrounding caption material
without changing the claimed linkage.

## PDF page 20 — Section 4.3, Equation (4.1)

Raw layout extraction:

```text
Fix the collimation arity r = 2. The analysis below shows that the total T-gate complexity of the
collimation sieve (apart from the oracle calls) is essentially

                             36L̃ · (2/(1 − δ))d ,                                  (4.1)

where L̃ is (an upper bound on) the typical phase-vector length, δ is the discard probability, and d is the depth
of the sieve tree.
```

Normalized check:

\[
36\widetilde L\left(\frac{2}{1-\delta}\right)^d .
\]

Raw layout extraction of the derivation:

```text
The estimate from Equation (4.1) is obtained as follows. The full sieve is a traversal of a binary tree
(modulo discards), with one collimation at each non-leaf node, and one or more oracle calls at each leaf node.
Therefore, the T-gate complexity of the sieve itself (apart from the oracle calls) is essentially the number of
non-leaf nodes times the T-gate complexity of collimation. For sieve tree depth d, the number of internal
nodes is about (2/(1 − δ))d when accounting for discards.
    The T-gate complexity of a single collimation step can be bounded as follows. As shown in Section 3.3.3,
for input and output phase vectors having lengths bounded by D, the quantum work is dominated by nine
lookups into a QRACM of D indexable cells. Because [BGB+ 18] implements such a QRACM (for cells of
any uniform size) using classical memory plus just 4D T-gates (and only dlog De ancillary qubits), the claim
follows.
```

The BATCH-009 Equation (4.1), symbol definitions, binary-tree explanation,
and nine-lookups/\(D\)-cell statement match the archived PDF. Its displayed
formula restores the exponent and tilde flattened by extraction.

## Cross-artifact result

`primary_source_excerpts.md` is faithful for the narrow O5 claims checked
above. The source never literally substitutes \(8L\) for
\(\widetilde L\) in Equation (4.1). The defensible linkage is narrower:
Equation (4.1) allows an upper bound on typical length; its derivation uses a
common input/output bound \(D\); and the pinned Figure 1 row enforces
\(\widetilde L_{\max}=8L\). Hence \(D=8L\) is a conservative FC0 cap for that
row, not a source-reported typical-value equality or a full resource estimate.
