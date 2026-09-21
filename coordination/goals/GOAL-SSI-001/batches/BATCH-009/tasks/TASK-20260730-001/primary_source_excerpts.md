# Primary-source excerpts for Equation (4.1) and the \(8L\) bound

Task `TASK-20260730-037` · access date 2026-07-30

## Source identity and verification

- Chris Peikert, “He Gives C-Sieves on the CSIDH,” IACR Cryptology ePrint
  Archive, Report 2019/725; final paper dated February 23, 2020.
- Primary record: <https://eprint.iacr.org/2019/725>
- Primary PDF: <https://eprint.iacr.org/2019/725.pdf>
- Author-hosted PDF cross-check:
  <https://web.eecs.umich.edu/~cpeikert/pubs/csidh-sieve.pdf>
- IACR record history observed on access: last of two revisions, 2020-02-24.
- Verification status: **primary-source text verified by direct PDF text
  extraction; exact mathematical typography normalized below**. Both primary
  URLs exposed matching title, author, paper date, section text, equation
  number, and Figure 1 text. This task does not archive the binary PDF because
  its declared deliverables are exactly four text/YAML artifacts; therefore a
  binary-file hash and PDF page-number mapping are **unverified**. Stable
  locators are section, equation, and figure identifiers.

The extraction flattened superscripts, tildes, and ceiling brackets. The
displayed formulas below restore those glyphs from context but do not change
the words or constants. No numerical security conclusion from the paper is
imported.

## Excerpt A — Equation (4.1) and symbol types

Locator: Section 4.3, “Quantum Complexity of the Sieve,” Equation (4.1).

> “Fix the collimation arity \(r=2\). The analysis below shows that the total
> T-gate complexity of the collimation sieve (apart from the oracle calls) is
> essentially
>
> \[
> 36\widetilde L\cdot\left(\frac{2}{1-\delta}\right)^d, \tag{4.1}
> \]
>
> where \(\widetilde L\) is (an upper bound on) the typical phase-vector
> length, \(\delta\) is the discard probability, and \(d\) is the depth of the
> sieve tree.”

The immediately following derivation states:

> “The full sieve is a traversal of a binary tree (modulo discards), with one
> collimation at each non-leaf node, and one or more oracle calls at each leaf
> node. Therefore, the T-gate complexity of the sieve itself (apart from the
> oracle calls) is essentially the number of non-leaf nodes times the T-gate
> complexity of collimation. For sieve tree depth \(d\), the number of internal
> nodes is about \((2/(1-\delta))^d\) when accounting for discards.”

It then types the per-collimation length bound:

> “As shown in Section 3.3.3, for input and output phase vectors having lengths
> bounded by \(D\), the quantum work is dominated by nine lookups into a QRACM
> of \(D\) indexable cells.”

Verification status: **verified_primary** for the equation, the meanings of
\(\widetilde L,\delta,d\), and the role of a length bound \(D\).

## Excerpt B — Equation (3.5) QRACM dependence

Locator: Section 3.3.3, “Complexity of Binary Collimation,” Equation (3.5).

> “The entire algorithm can be run with 9 lookups and as little as
>
> \[
> R=L_{\max}\cdot
> \left\lceil\max\{(1+\alpha)\log(S_0/S),\log L_{\max}\}\right\rceil
> \tag{3.5}
> \]
>
> bits of reusable QRACM …”

Verification status: **verified_primary** for the nine-lookup row and the fact
that Equation (3.5) is parameterized by \(L_{\max}\). The exact ceiling glyphs
were normalized from the PDF text extraction.

## Excerpt C — Figure 1's \(8L\) row

Locator: Section 4.1, Figure 1 caption.

> “ ‘QRACM’ is the number of bits of quantumly accessible classical memory,
> which is given by Equation (3.5) with \(\alpha=1/2\) for
> \(\widetilde L_{\max}=8L\) indexable cells …”

Locator: Section 4.1, bullet immediately following Figure 1.

> “We impose a maximum phase-vector length of
> \(\widetilde L_{\max}=8L\). This reflects the fact that the generated phase
> vectors are sometimes longer than the desired length \(L\), but are almost
> always within a factor of 8, and we can enforce this as a hard bound by doing
> a partial measurement whenever a phase vector happens to be longer. We use
> Equation (3.5) for the number of bits of QRACM as a function of
> \(\widetilde L_{\max}\).”

Verification status: **verified_primary** for the \(8L\) maximum, its
hard-bound enforcement mechanism, and its use in Equation (3.5).

## O5 implication check

The source does not literally state “substitute \(8L\) for
\(\widetilde L\) in Equation (4.1).” That substitution is an FC0-R2
conservative derivation:

1. Equation (4.1) permits \(\widetilde L\) to be an upper bound on typical
   phase-vector length.
2. The Figure 1 bullet imposes \(8L\) as a hard maximum whenever a generated
   phase vector is longer.
3. The derivation of Equation (4.1) applies a common bound \(D\) to input and
   output phase-vector lengths at each collimation.
4. Therefore, for the same pinned Figure 1 row and the charged traversal,
   setting \(D=\widetilde L_{\max}=8L\) is a conservative symbolic upper bound.

This verifies the type implication needed by O5 without claiming that the
paper used \(8L\) as its typical value in every reported T-gate estimate.
Replacing a typical-length estimate by the hard maximum can only be recorded
as a conservative sensitivity row, not as a source-reported equality.

O5 status in FC0-R2: **adequate_primary_anchor_for_symbolic_cap_rule**.
Limit: this does not instantiate per-invocation lengths or resolve the
stochastic stopping ledger.
